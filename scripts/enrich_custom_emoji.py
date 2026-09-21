#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from emoji_registry import apply_sticker, call, eligible, index_records, mark_missing, recount

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT/'assets/emoji-catalog/catalog.json'

def chunks(items, size):
    for start in range(0, len(items), size): yield items[start:start+size]

def enrich(data, token, all_records=False, caller=call):
    by = index_records(data['records'])
    targets = [cid for cid, r in by.items() if all_records or not eligible(r)]
    updated = missing = 0
    for batch in chunks(targets, 200):
        result = caller(token, 'getCustomEmojiStickers', {'custom_emoji_ids': batch})
        if not isinstance(result, list): raise ValueError('Unexpected Telegram response')
        seen = set()
        for sticker in result:
            cid = sticker.get('custom_emoji_id')
            if cid not in batch or cid in seen:
                raise ValueError('Unexpected or duplicate Telegram response ID')
            seen.add(cid)
            apply_sticker(by[cid], sticker, 'getCustomEmojiStickers')
            updated += 1
        for cid in set(batch)-seen:
            mark_missing(by[cid]); missing += 1
    recount(data)
    return {'queried': len(targets), 'updated': updated, 'not_returned': missing}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true', help='Re-query source-mapped/ready IDs too')
    ap.add_argument('--write', action='store_true', help='Write catalog.json; default is dry run')
    args = ap.parse_args()
    token = os.environ.get('BOT_TOKEN')
    if not token: ap.error('BOT_TOKEN is required')
    try:
        data = json.loads(CAT.read_text(encoding='utf-8'))
        report = enrich(data, token, args.all)
        if args.write:
            CAT.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    except (ValueError, RuntimeError) as exc:
        ap.exit(1, str(exc)+'\n')
    print(json.dumps({**report, 'selectable': data['selectable_count'], 'write': args.write}))
if __name__ == '__main__': main()
