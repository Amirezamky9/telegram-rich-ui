#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, urllib.request
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

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pack", help="Sticker-set short name or t.me/addemoji/... URL")
    ap.add_argument("--category", default="imported")
    ap.add_argument("--write", action="store_true")
    args=ap.parse_args()
    token=os.environ.get("BOT_TOKEN")
    if not token: raise SystemExit("BOT_TOKEN is required")
    name=args.pack.rstrip("/").split("/")[-1]
    if not re.fullmatch(r"[A-Za-z0-9_]+",name): raise SystemExit("Invalid pack short name")
    ss=call(token,"getStickerSet",{"name":name})
    if ss.get("sticker_type")!="custom_emoji": raise SystemExit(f"{name} is not a custom_emoji sticker set")
    data=json.loads(CAT.read_text(encoding="utf-8"))
    by={r["custom_emoji_id"]:r for r in data["records"]}
    added=merged=0
    for st in ss.get("stickers",[]):
        cid=st.get("custom_emoji_id")
        if not cid: continue
        if cid in by:
            r=by[cid]; merged+=1
        else:
            r={"custom_emoji_id":cid,"name":f"{name.lower()}_{cid[-8:]}","fallback":None,
               "description":f"Custom emoji imported from {name}","category":args.category,
               "style_family":name,"animated":None,"needs_repainting":None,"packs":[],
               "aliases":[],"keywords":[],"tags":["imported"],"sources":["telegram-bot-api"],
               "status":"needs_enrichment","selectable":False}
            data["records"].append(r); by[cid]=r; added+=1
        if st.get("emoji"): r["fallback"]=st["emoji"]
        if name not in r["packs"]: r["packs"].append(name)
        r["needs_repainting"]=bool(st.get("needs_repainting",False))
        if r.get("fallback"): r["status"]="ready"; r["selectable"]=True
    data["records"].sort(key=lambda r:int(r["custom_emoji_id"]))
    data["record_count"]=len(data["records"])
    data["selectable_count"]=sum(bool(r.get("selectable")) for r in data["records"])
    data["needs_enrichment_count"]=data["record_count"]-data["selectable_count"]
    if args.write: CAT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"pack={name} added={added} merged={merged} total={data['record_count']} write={args.write}")

if __name__=="__main__": main()
