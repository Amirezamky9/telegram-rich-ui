#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from search_emoji import score_record
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"assets/emoji-catalog/catalog.json"
CUR=ROOT/"assets/emoji-catalog/curated-ui.json"
REG=ROOT/"assets/emoji-catalog/regional-packs.json"

def main():
    errors=[]
    cat=json.loads(CAT.read_text(encoding="utf-8"))
    cur=json.loads(CUR.read_text(encoding="utf-8"))
    reg=json.loads(REG.read_text(encoding="utf-8"))
    records=cat.get("records",[])
    ids=[r.get("custom_emoji_id") for r in records]
    if len(ids)!=len(set(ids)): errors.append("duplicate custom_emoji_id values found")
    by_id={r["custom_emoji_id"]:r for r in records if isinstance(r.get("custom_emoji_id"),str)}
    for r in records:
        cid=r.get("custom_emoji_id")
        if not isinstance(cid,str) or not re.fullmatch(r"\d{10,}",cid or ""): errors.append(f"invalid id: {cid!r}")
        if r.get("selectable") and not r.get("fallback"): errors.append(f"selectable record missing fallback: {cid}")
        if r.get("status")=="ready" and not r.get("selectable"): errors.append(f"ready record not selectable: {cid}")
        if r.get("selectable") and r.get("status")!="ready": errors.append(f"selectable record not ready: {cid}")
    for set_name,spec in cur.get("sets",{}).items():
        for cid in spec.get("ids",[]):
            r=by_id.get(cid)
            if not r: errors.append(f"curated {set_name} references missing id {cid}")
            elif not r.get("selectable"): errors.append(f"curated {set_name} references non-selectable id {cid}")
    iran=set()
    for p in reg.get("packs",[]):
        for cid in p.get("raw_ids",[]): 
            if cid in iran: errors.append(f"duplicate regional raw id {cid}")
            iran.add(cid)
            if cid not in by_id: errors.append(f"regional id missing from catalog {cid}")
    # Semantic search regression checks: prevent broad substring/synonym pollution.
    ready=[r for r in records if r.get("selectable")]
    search_cases={
        "support":"5884510167986343350",
        "shop":"5983399041197675256",
        "settings":"5341715473882955310",
        "ai":"5931415565955503486",
        "یلدا":"5305336095863485125",
    }
    for query,expected in search_cases.items():
        ranked=sorted(((score_record(r,query),r) for r in ready), key=lambda x:(-x[0], x[1].get("name") or ""))
        ranked=[item for item in ranked if item[0]>0]
        if not ranked or ranked[0][1].get("custom_emoji_id")!=expected:
            got=ranked[0][1].get("custom_emoji_id") if ranked else None
            errors.append(f"search regression for {query!r}: expected top {expected}, got {got}")
    bad_ai={r.get("name") for s,r in sorted(((score_record(r,"ai"),r) for r in ready),key=lambda x:-x[0])[:10]}
    if "airpods" in bad_ai or "train" in bad_ai:
        errors.append("search regression: short query 'ai' matched substring noise")

    expected_selectable=sum(bool(r.get("selectable")) for r in records)
    if cat.get("record_count")!=len(records): errors.append("record_count mismatch")
    if cat.get("selectable_count")!=expected_selectable: errors.append("selectable_count mismatch")
    if errors:
        print("EMOJI CATALOG VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print(f'EMOJI CATALOG OK: {len(records)} unique IDs, {expected_selectable} selectable, {len(records)-expected_selectable} pending enrichment')
    return 0

if __name__=="__main__": raise SystemExit(main())
