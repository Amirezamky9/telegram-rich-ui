#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re
from pathlib import Path
from search_emoji import score_record

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
    for i,r in enumerate(records):
        cid=r.get("custom_emoji_id")
        if not isinstance(cid,str) or not ID_RE.fullmatch(cid or ""):
            errors.append(f"invalid id at records[{i}]: {cid!r}"); continue
        if cid in by_id: errors.append(f"duplicate custom_emoji_id {cid}")
        by_id[cid]=r
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
        declared=spec.get("style_family")
        if declared and any(by_id[c].get("style_family")!=declared for c in ids if c in by_id):
            errors.append(f"curated {set_name} style mismatch")

    regional=[]
    for p in reg.get("packs",[]):
        regional.extend(p.get("raw_ids",[]) or [])
    if len(regional)!=len(set(regional)): errors.append("duplicate regional raw IDs")
    for cid in regional:
        if cid not in by_id: errors.append(f"regional ID missing from catalog: {cid}")
    iran_pending=[r for r in records if r.get("category")=="regional_iran" and not r.get("selectable")]
    iran_pack=next((p for p in reg.get("packs",[]) if p.get("short_name")=="iranNewz"),None)
    if iran_pack and len(iran_pack.get("raw_ids",[]))!=len(iran_pending): errors.append("iranNewz inventory/pending mismatch")

    source_ids=[s.get("id") for s in src.get("sources",[])]
    if len(source_ids)!=len(set(source_ids)): errors.append("duplicate source IDs")

    with (DIR/"catalog.csv").open(encoding="utf-8",newline="") as fh:
        csv_rows=list(csv.DictReader(fh))
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
