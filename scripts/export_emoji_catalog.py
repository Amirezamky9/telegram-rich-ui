#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"assets/emoji-catalog"
FIELDS=["custom_emoji_id","name","fallback","description","category","style_family","animated","needs_repainting","packs","aliases","keywords","tags","status","selectable","sources"]
def main():
    data=json.loads((DIR/"catalog.json").read_text(encoding="utf-8"))
    out=DIR/"catalog.csv"
    with out.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader()
        for r in data["records"]:
            row=dict(r)
            for f in ("packs","aliases","keywords","tags","sources"): row[f]="|".join(str(v) for v in (r.get(f) or []))
            w.writerow({f:row.get(f) for f in FIELDS})
    print(f"wrote {len(data['records'])} rows to {out}")
if __name__=="__main__": main()
