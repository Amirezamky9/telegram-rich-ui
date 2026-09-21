#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re
from pathlib import Path
from search_emoji import score_record
from emoji_registry import eligible
from export_emoji_catalog import csv_row, FIELDS

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"assets/emoji-catalog"
ID_RE=re.compile(r"^\d{10,}$")
TG_EMOJI_RE=re.compile(r'<tg-emoji\s+emoji-id="(\d+)">([^<]+)</tg-emoji>')

def load(name): return json.loads((DIR/name).read_text(encoding="utf-8"))

def main():
    errors=[]
    cat=load("catalog.json"); cur=load("curated-ui.json"); reg=load("regional-packs.json"); src=load("sources.json")
    records=cat.get("records",[])
    by_id={}
    source_ids={s["id"] for s in src.get("sources",[])}
    for i,r in enumerate(records):
        cid=r.get("custom_emoji_id")
        if not isinstance(cid,str) or not ID_RE.fullmatch(cid or ""):
            errors.append(f"invalid id at records[{i}]: {cid!r}"); continue
        if cid in by_id: errors.append(f"duplicate custom_emoji_id {cid}")
        by_id[cid]=r
        if not r.get("sources") or not set(r.get("sources",[])) <= source_ids:
            errors.append(f"{cid}: missing/unknown source reference")
        if not r.get("provenance"):
            errors.append(f"{cid}: missing provenance")
        for observation in r.get("provenance", []):
            if observation.get("source_id") not in r.get("sources", []) or not observation.get("locator"):
                errors.append(f"{cid}: unresolved provenance observation")
        if r.get("selectable") and not any(o.get("fallback") == r.get("fallback") for o in r.get("provenance", [])):
            errors.append(f"{cid}: fallback has no matching provenance")
        verification = r.get("verification", {})
        if verification.get("status") not in {"source_mapped", "pending", "bot_api_verified", "not_returned"}:
            errors.append(f"{cid}: invalid verification state")
        if r.get("selectable") and verification.get("status") not in {"source_mapped", "bot_api_verified"}:
            errors.append(f"{cid}: selectable but verification pending")
        if verification.get("status") == "bot_api_verified":
            if not verification.get("checked_at") or verification.get("method") not in {"getStickerSet", "getCustomEmojiStickers"}:
                errors.append(f"{cid}: missing official verification evidence")
        if r.get("selectable") and not eligible(r): errors.append(f"{cid}: unsafe selectable record")
        if r.get("selectable") and r.get("fallback") in {"%", "₽", "…", "⋮", "#"}:
            errors.append(f"{cid}: text symbol cannot be used as fallback")
        if r.get("selectable") and not r.get("fallback"): errors.append(f"selectable record missing fallback: {cid}")
        if r.get("status")=="ready" and not r.get("selectable"): errors.append(f"ready record not selectable: {cid}")
        if r.get("selectable") and r.get("status")!="ready": errors.append(f"selectable record not ready: {cid}")
        for field in ("packs","aliases","keywords","tags","sources"):
            v=r.get(field)
            if not isinstance(v,list): errors.append(f"{cid}: {field} must be a list")
            elif len(v)!=len(set(v)): errors.append(f"{cid}: {field} has duplicates")

    ready=[r for r in records if r.get("selectable")]
    ready_count=len(ready)
    if cat.get("record_count")!=len(records): errors.append("record_count mismatch")
    if cat.get("selectable_count")!=ready_count: errors.append("selectable_count mismatch")
    if cat.get("needs_enrichment_count")!=len(records)-ready_count: errors.append("needs_enrichment_count mismatch")
    if cat.get("dedupe_key")!="custom_emoji_id": errors.append("dedupe_key must be custom_emoji_id")

    for set_name,spec in cur.get("sets",{}).items():
        ids=spec.get("ids",[])
        if len(ids)!=len(set(ids)): errors.append(f"curated {set_name} has duplicate IDs")
        for cid in ids:
            r=by_id.get(cid)
            if not r: errors.append(f"curated {set_name} missing {cid}")
            elif not r.get("selectable"): errors.append(f"curated {set_name} uses non-selectable {cid}")
            elif any(not r.get(field) for field in ("ui_category", "label_fa", "description", "usage_notes", "curation")):
                errors.append(f"curated {set_name} missing semantic metadata for {cid}")
        declared=spec.get("style_family")
        if declared and any(by_id[c].get("style_family")!=declared for c in ids if c in by_id):
            errors.append(f"curated {set_name} style mismatch")

    regional=[]
    for pack in reg.get("packs", []):
        ids = pack.get("raw_ids", [])
        if len(ids) != len(set(ids)): errors.append(f"duplicate IDs within regional pack {pack['short_name']}")
        regional.extend(ids)
        for cid in ids:
            if cid not in by_id: errors.append(f"regional ID missing from catalog: {cid}")
    # This is discovery inventory, not a count of pending records. Enrichment must not invalidate it.

    source_ids=[s.get("id") for s in src.get("sources",[])]
    if len(source_ids)!=len(set(source_ids)): errors.append("duplicate source IDs")

    with (DIR/"catalog.csv").open(encoding="utf-8",newline="") as fh:
        csv_rows=list(csv.DictReader(fh))
    if csv_rows and list(csv_rows[0]) != FIELDS: errors.append("catalog.csv columns differ from export contract")
    for row in csv_rows:
        record = by_id.get(row.get("custom_emoji_id"))
        if record and row != csv_row(record): errors.append(f"catalog.csv stale content: {row['custom_emoji_id']}")
    csv_ids=[r["custom_emoji_id"] for r in csv_rows]
    if len(csv_rows)!=len(records): errors.append("catalog.csv row count mismatch")
    if len(csv_ids)!=len(set(csv_ids)): errors.append("catalog.csv duplicate IDs")
    if set(csv_ids)!=set(by_id): errors.append("catalog.csv IDs differ from catalog.json")

    # Lock literal emoji IDs used by bundled UI templates to the canonical registry.
    for template in sorted((ROOT/"assets/templates").glob("*.html")):
        text=template.read_text(encoding="utf-8")
        for cid,fallback in TG_EMOJI_RE.findall(text):
            record=by_id.get(cid)
            if record is None:
                errors.append(f"{template.name}: unknown custom emoji ID {cid}")
                continue
            if not record.get("selectable"):
                errors.append(f"{template.name}: non-selectable custom emoji ID {cid}")
            if record.get("fallback")!=fallback:
                errors.append(
                    f"{template.name}: fallback mismatch for {cid}; template={fallback!r}, registry={record.get('fallback')!r}"
                )

    search_cases={
        "support":"5884510167986343350",
        "shop":"5983399041197675256",
        "settings":"5341715473882955310",
        "ai":"5931415565955503486",
        "یلدا":"5305336095863485125",
    }
    for query,expected in search_cases.items():
        ranked=sorted(((score_record(r,query),r) for r in ready),key=lambda x:(-x[0],x[1].get("name") or ""))
        ranked=[x for x in ranked if x[0]>0]
        got=ranked[0][1].get("custom_emoji_id") if ranked else None
        if got!=expected: errors.append(f"search regression for {query!r}: expected {expected}, got {got}")
    top_ai={r.get("name") for s,r in sorted(((score_record(r,"ai"),r) for r in ready),key=lambda x:-x[0])[:10]}
    if "airpods" in top_ai or "train" in top_ai: errors.append("short query 'ai' matched substring noise")

    fa_ready=[r for r in ready if "persian_ui" in (r.get("tags") or [])]
    if len(fa_ready)<5: errors.append("expected at least 5 Persian/Iranian ready palette entries")

    if errors:
        print("EMOJI CATALOG VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f"EMOJI CATALOG OK: {len(records)} unique IDs, {ready_count} selectable, {len(records)-ready_count} pending enrichment")
    print(f"CSV rows: {len(csv_rows)}; curated sets: {len(cur.get('sets',{}))}; regional raw IDs: {len(regional)}")
    print("Bundled template custom-emoji IDs/fallbacks: OK")
    return 0

if __name__=="__main__": raise SystemExit(main())
