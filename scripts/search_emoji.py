#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, unicodedata
from html import escape
from emoji_registry import eligible
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"assets/emoji-catalog/catalog.json"
CURATED=ROOT/"assets/emoji-catalog/curated-ui.json"

def norm(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold().translate(str.maketrans("يك", "یک"))
    text = "".join(c for c in text if not ("\u064b" <= c <= "\u065f") and c != "\u0640")
    return " ".join(re.sub(r"[_\-\u200c]+", " ", text).split())

def score_record(r, query: str) -> int:
    q=norm(query)
    if not q: return 1
    qtokens=[t for t in q.split() if t]
    score=0
    fields=[
        (r.get("custom_emoji_id"),150),(r.get("label_fa"),120),(r.get("ui_category"),95),(r.get("name"),120),(r.get("fallback"),120),(r.get("category"),95),(r.get("style_family"),80),
    ]
    fields += [(v,105) for v in (r.get("aliases") or [])]
    fields += [(v,90) for v in (r.get("keywords") or [])]
    fields += [(v,70) for v in (r.get("tags") or [])]
    fields += [(v,45) for v in (r.get("packs") or [])]
    fields += [(r.get("description"),20)]
    for raw,weight in fields:
        if not raw: continue
        value=norm(raw); tokens=set(value.split())
        if value==q: score=max(score,weight)
        elif q in tokens: score=max(score,weight-10)
        elif len(q)>3 and any(tok.startswith(q) for tok in tokens): score=max(score,weight-25)
        elif len(qtokens)>1 and all(any(qt==tok or (len(qt)>3 and tok.startswith(qt)) for tok in tokens) for qt in qtokens):
            score=max(score,weight-20)
    if "curated_ui" in (r.get("tags") or []) and score>0: score+=5
    return score

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("query", nargs="*", help="English/Persian semantic search terms")
    ap.add_argument("--category")
    ap.add_argument("--ui-category", help="Curated semantic category, e.g. commerce or navigation")
    ap.add_argument("--verified-only", action="store_true", help="Require an official Bot API metadata observation")
    ap.add_argument("--style")
    ap.add_argument("--tag", action="append", default=[])
    ap.add_argument("--pack")
    ap.add_argument("--curated", help="curated set name from curated-ui.json")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--include-unverified", action="store_true", help="Inspect pending inventory in table/json only")
    ap.add_argument("--format", choices=("table","json","html","id","button-json"), default="table")
    args=ap.parse_args()
    if args.include_unverified and args.format not in ("table", "json"):
        ap.error("--include-unverified is inspection-only; use table or json")

    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    records=data["records"]
    by_id={r["custom_emoji_id"]:r for r in records}

    curated_order=None
    if args.curated:
        cur=json.loads(CURATED.read_text(encoding="utf-8"))
        spec=cur.get("sets",{}).get(args.curated)
        if spec is None:
            raise SystemExit("Unknown curated set: "+args.curated+". Available: "+", ".join(sorted(cur.get("sets",{}))))
        curated_order=spec.get("ids",[])
        records=[by_id[cid] for cid in curated_order if cid in by_id]

    query=" ".join(args.query).strip()
    ranked=[]
    for idx,r in enumerate(records):
        if not args.include_unverified and not eligible(r): continue
        if args.verified_only and r.get("verification", {}).get("status") != "bot_api_verified": continue
        if args.ui_category and norm(r.get("ui_category")) != norm(args.ui_category): continue
        if args.category and norm(r.get("category"))!=norm(args.category): continue
        if args.style and norm(r.get("style_family"))!=norm(args.style): continue
        if any(norm(tag) not in {norm(v) for v in (r.get("tags") or [])} for tag in args.tag): continue
        if args.pack and norm(args.pack) not in {norm(v) for v in (r.get("packs") or [])}: continue
        s=score_record(r,query)
        if s>0: ranked.append((s,idx,r))

    if args.curated and not query:
        ranked.sort(key=lambda x:x[1])
    else:
        ranked.sort(key=lambda x:(-x[0], x[2].get("style_family") or "", x[2].get("name") or "", int(x[2]["custom_emoji_id"])))
    rows=[r for _,_,r in ranked[:max(args.limit,0)]]

    if args.format=="json":
        print(json.dumps(rows,ensure_ascii=False,indent=2)); return
    if args.format=="html":
        for r in rows:
            if r.get("fallback"):
                print(f'<tg-emoji emoji-id="{r["custom_emoji_id"]}">{escape(r["fallback"])}</tg-emoji>')
        return
    if args.format=="id":
        for r in rows: print(r["custom_emoji_id"])
        return
    if args.format=="button-json":
        for r in rows:
            print(json.dumps({"icon_custom_emoji_id":r["custom_emoji_id"]},ensure_ascii=False))
        return
    print("ID\tFALLBACK\tNAME\tCATEGORY\tSTYLE\tVERIFICATION\tDESCRIPTION\tPACKS")
    for r in rows:
        print(f'{r["custom_emoji_id"]}\t{r.get("fallback") or "-"}\t{r.get("name") or "-"}\t{r.get("category") or "-"}\t{r.get("style_family") or "-"}\t{r.get("verification", {}).get("status", "unknown")}\t{r.get("description", "")}\t{",".join(r.get("packs") or [])}')

if __name__=="__main__": main()
