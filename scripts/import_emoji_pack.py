#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, urllib.error, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"assets/emoji-catalog/catalog.json"

def call(token, method, payload):
    req=urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type":"application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r: body=json.load(r)
    except urllib.error.HTTPError as exc:
        detail=exc.read().decode("utf-8",errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {detail}") from exc
    if not body.get("ok"): raise RuntimeError(body)
    return body["result"]

def unique(xs): return list(dict.fromkeys(x for x in xs if x))

def pack_name(value):
    value=value.strip().rstrip("/")
    m=re.fullmatch(r"https?://t\.me/addemoji/([A-Za-z0-9_]+)",value)
    if m: return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_]+",value): return value
    raise SystemExit("Invalid custom emoji pack name/URL")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pack",help="Sticker-set short name or t.me/addemoji/... URL")
    ap.add_argument("--category",default="imported")
    ap.add_argument("--style-family")
    ap.add_argument("--tag",action="append",default=[])
    ap.add_argument("--source-id")
    ap.add_argument("--write",action="store_true")
    args=ap.parse_args()
    token=os.environ.get("BOT_TOKEN")
    if not token: raise SystemExit("BOT_TOKEN is required")
    name=pack_name(args.pack)
    ss=call(token,"getStickerSet",{"name":name})
    if ss.get("sticker_type")!="custom_emoji":
        raise SystemExit(f"{name} is not a custom_emoji sticker set")

    data=json.loads(CAT.read_text(encoding="utf-8"))
    by={r["custom_emoji_id"]:r for r in data["records"]}
    source=args.source_id or f"telegram-pack:{name}"
    added=merged=0
    for st in ss.get("stickers",[]):
        cid=st.get("custom_emoji_id")
        if not cid: continue
        fallback=st.get("emoji")
        if cid in by:
            r=by[cid]; merged+=1
        else:
            r={"custom_emoji_id":cid,"name":f"{name.lower()}_{cid[-8:]}","fallback":fallback,
               "description":f"Custom emoji from {name}","category":args.category,
               "style_family":args.style_family or name,"animated":bool(st.get("is_animated")),
               "needs_repainting":bool(st.get("needs_repainting")),"packs":[name],
               "aliases":[],"keywords":unique([fallback,name]),"tags":unique(["imported",*args.tag]),
               "sources":[source],"status":"ready" if fallback else "needs_enrichment","selectable":bool(fallback)}
            data["records"].append(r); by[cid]=r; added+=1
            continue
        if not r.get("fallback") and fallback: r["fallback"]=fallback
        r["packs"]=unique([*(r.get("packs") or []),name])
        r["sources"]=unique([*(r.get("sources") or []),source])
        r["tags"]=unique([*(r.get("tags") or []),*args.tag])
        r["keywords"]=unique([*(r.get("keywords") or []),fallback,name])
        if r.get("animated") is None: r["animated"]=bool(st.get("is_animated"))
        if r.get("needs_repainting") is None: r["needs_repainting"]=bool(st.get("needs_repainting"))
        if r.get("fallback"): r["status"]="ready"; r["selectable"]=True

    data["records"].sort(key=lambda r:int(r["custom_emoji_id"]))
    data["record_count"]=len(data["records"])
    data["selectable_count"]=sum(bool(r.get("selectable")) for r in data["records"])
    data["needs_enrichment_count"]=data["record_count"]-data["selectable_count"]
    if args.write:
        CAT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"pack":name,"title":ss.get("title"),"added":added,"merged":merged,
                      "total":data["record_count"],"write":args.write},ensure_ascii=False))
if __name__=="__main__": main()
