#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"assets/emoji-catalog"
FIELDS=["custom_emoji_id","name","fallback","description","category","style_family","animated","needs_repainting","packs","aliases","keywords","tags","status","selectable","sources","ui_category","label_fa","description_fa","usage_notes","is_video","verification","provenance","curation"]
def csv_row(record):
    row = {}
    for field in FIELDS:
        value = record.get(field)
        if isinstance(value, list) and field != "provenance": value = "|".join(str(v) for v in value)
        elif isinstance(value, (dict, list)): value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        row[field] = "" if value is None else str(value)
    return row

def main():
    data=json.loads((DIR/"catalog.json").read_text(encoding="utf-8"))
    out=DIR/"catalog.csv"
    with out.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS,lineterminator="\n"); w.writeheader()
        for r in data["records"]:
            w.writerow(csv_row(r))
    print(f"wrote {len(data['records'])} rows to {out}")
if __name__=="__main__": main()
