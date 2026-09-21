#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"assets/emoji-catalog/catalog.json"

def norm(value: object) -> str:
    return re.sub(r"[_\-]+"," ",str(value or "").casefold()).strip()

def fields(r):
    exact=set()
    weighted=[]
    for key,weight in (("name",8),("fallback",10),("category",6),("style_family",5)):
        v=r.get(key)
        if v:
            n=norm(v); exact.add(n); weighted.append((n,weight))
    for key,weight in (("aliases",9),("keywords",7),("tags",6),("packs",4),("sources",1)):
        for v in r.get(key) or []:
            n=norm(v); exact.add(n); weighted.append((n,weight))
    desc=norm(r.get("description"))
    if desc: weighted.append((desc,2))
    return exact,weighted

def score_record(r, query: str) -> int:
    q=norm(query)
    if not q: return 1
    qtokens=[t for t in q.split() if t]
    exact,weighted=fields(r)
    if q in exact: return 100
    score=0
    for value,weight in weighted:
        tokens=set(value.split())
        if q in tokens: score=max(score,60+weight)
        if len(q)>2 and value.startswith(q+" "): score=max(score,35+weight)
        if len(q)>3 and any(tok.startswith(q) for tok in tokens): score=max(score,20+weight)
        if len(qtokens)>1 and all(any(qt==tok or (len(qt)>3 and tok.startswith(qt)) for tok in tokens) for qt in qtokens):
            score=max(score,45+weight)
    return score

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
    ranked=[]
    for r in data["records"]:
        if not args.include_unverified and not r.get("selectable"): continue
        if args.category and r.get("category")!=args.category: continue
        if args.style and r.get("style_family")!=args.style: continue
        if args.tag and args.tag not in (r.get("tags") or []): continue
        s=score_record(r,args.query)
        if s>0: ranked.append((s,r))
    ranked.sort(key=lambda x:(-x[0], x[1].get("style_family") or "", x[1].get("name") or "", int(x[1]["custom_emoji_id"])))
    rows=[r for _,r in ranked[:max(args.limit,0)]]
    if args.format=="json":
        print(json.dumps(rows,ensure_ascii=False,indent=2)); return
    if args.format=="html":
        for r in rows:
            if r.get("fallback"):
                print(f'<tg-emoji emoji-id="{r["custom_emoji_id"]}">{r["fallback"]}</tg-emoji>  # {r["name"]}')
        return
    print("ID\tFALLBACK\tNAME\tCATEGORY\tSTYLE")
    for r in rows:
        print(f'{r["custom_emoji_id"]}\t{r.get("fallback") or "-"}\t{r.get("name") or "-"}\t{r.get("category") or "-"}\t{r.get("style_family") or "-"}')

if __name__=="__main__": main()
