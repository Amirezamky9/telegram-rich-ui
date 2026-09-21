#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"assets/emoji-catalog/catalog.json"

def call(token, method, payload):
    req=urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json"},
        method="POST")
    with urllib.request.urlopen(req,timeout=30) as r: body=json.load(r)
    if not body.get("ok"): raise RuntimeError(body)
    return body["result"]

def chunks(xs,n):
    for i in range(0,len(xs),n): yield xs[i:i+n]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="Re-query ready IDs too")
    ap.add_argument("--write", action="store_true", help="Write catalog.json; otherwise print summary")
    args=ap.parse_args()
    token=os.environ.get("BOT_TOKEN")
    if not token: raise SystemExit("BOT_TOKEN is required")
    data=json.loads(CAT.read_text(encoding="utf-8"))
    records=data["records"]
    targets=[r["custom_emoji_id"] for r in records if args.all or not r.get("selectable")]
    by={r["custom_emoji_id"]:r for r in records}
    updated=0
    for batch in chunks(targets,200):
        for st in call(token,"getCustomEmojiStickers",{"custom_emoji_ids":batch}):
            cid=st.get("custom_emoji_id")
            if not cid or cid not in by: continue
            r=by[cid]
            if st.get("emoji"): r["fallback"]=st["emoji"]
            if st.get("set_name") and st["set_name"] not in r["packs"]: r["packs"].append(st["set_name"])
            r["needs_repainting"]=bool(st.get("needs_repainting",False))
            if r.get("fallback"):
                r["status"]="ready"; r["selectable"]=True
            updated+=1
    data["selectable_count"]=sum(bool(r.get("selectable")) for r in records)
    data["needs_enrichment_count"]=len(records)-data["selectable_count"]
    if args.write:
        CAT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"queried={len(targets)} updated={updated} selectable={data['selectable_count']} write={args.write}")

if __name__=="__main__": main()
