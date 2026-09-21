#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"assets/emoji-catalog/catalog.json"

def haystack(r):
    parts=[r.get("name"),r.get("fallback"),r.get("description"),r.get("category"),r.get("style_family")]
    for k in ("packs","aliases","keywords","tags","sources"): parts.extend(r.get(k) or [])
    return " ".join(str(x) for x in parts if x).casefold()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--category")
    ap.add_argument("--style")
    ap.add_argument("--tag")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--include-unverified", action="store_true")
    ap.add_argument("--format", choices=("table","json","html"), default="table")
    args=ap.parse_args()
    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    q=args.query.casefold().strip()
    rows=[]
    for r in data["records"]:
        if not args.include_unverified and not r.get("selectable"): continue
        if q and q not in haystack(r): continue
        if args.category and r.get("category")!=args.category: continue
        if args.style and r.get("style_family")!=args.style: continue
        if args.tag and args.tag not in (r.get("tags") or []): continue
        rows.append(r)
    rows=rows[:max(args.limit,0)]
    if args.format=="json":
        print(json.dumps(rows,ensure_ascii=False,indent=2)); return
    if args.format=="html":
        for r in rows:
            if not r.get("fallback"): continue
            print(f'<tg-emoji emoji-id="{r["custom_emoji_id"]}">{r["fallback"]}</tg-emoji>  # {r["name"]}')
        return
    print("ID\tFALLBACK\tNAME\tCATEGORY\tSTYLE")
    for r in rows:
        print(f'{r["custom_emoji_id"]}\t{r.get("fallback") or "-"}\t{r.get("name") or "-"}\t{r.get("category") or "-"}\t{r.get("style_family") or "-"}')

if __name__=="__main__": main()
