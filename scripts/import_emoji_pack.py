#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re
from pathlib import Path
from emoji_registry import apply_sticker, call, index_records, recount, unique, ID_RE

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT/'assets/emoji-catalog/catalog.json'
SOURCES = ROOT/'assets/emoji-catalog/sources.json'

def pack_name(value):
    value = value.strip().rstrip('/')
    match = re.fullmatch(r'https?://t\.me/addemoji/([A-Za-z0-9_]+)', value)
    if match: return match.group(1)
    if re.fullmatch(r'[A-Za-z0-9_]+', value): return value
    raise ValueError('Invalid custom emoji pack name/URL')

def merge_pack(data, sticker_set, name, category='imported', style_family=None, tags=(), source='telegram-bot-api'):
    if sticker_set.get('sticker_type') != 'custom_emoji':
        raise ValueError('Not a custom_emoji sticker set')
    by = index_records(data['records'])
    added = merged = 0
    seen = set()
    for sticker in sticker_set.get('stickers', []):
        cid = sticker.get('custom_emoji_id')
        if not isinstance(cid, str) or not ID_RE.fullmatch(cid):
            raise ValueError('Invalid custom emoji ID in sticker set')
        if cid in seen: continue
        seen.add(cid)
        if cid not in by:
            record = {'custom_emoji_id': cid, 'name': f'{name.lower()}_{cid}',
                      'description': f'Imported from {name}; semantic description needs review.',
                      'category': category, 'style_family': style_family or name,
                      'aliases': [], 'keywords': [], 'tags': ['imported'], 'sources': [], 'packs': []}
            by[cid] = record; data['records'].append(record); added += 1
        else:
            record = by[cid]; merged += 1
        record['tags'] = unique([*record.get('tags', []), *tags])
        apply_sticker(record, sticker, 'getStickerSet', name, source)
    recount(data)
    return added, merged

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pack', help='Sticker-set short name or t.me/addemoji/... URL')
    ap.add_argument('--category', default='imported')
    ap.add_argument('--style-family')
    ap.add_argument('--tag', action='append', default=[])
    ap.add_argument('--source-id', default='telegram-bot-api', help='Existing ID in sources.json')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    token = os.environ.get('BOT_TOKEN')
    if not token: ap.error('BOT_TOKEN is required')
    sources = json.loads(SOURCES.read_text(encoding='utf-8'))
    if args.source_id not in {s['id'] for s in sources['sources']}:
        ap.error('--source-id must already be registered in sources.json')
    try:
        name = pack_name(args.pack)
        data = json.loads(CAT.read_text(encoding='utf-8'))
        index_records(data['records'])
        sticker_set = call(token, 'getStickerSet', {'name': name})
        added, merged = merge_pack(data, sticker_set, name, args.category, args.style_family, args.tag, args.source_id)
        if args.write:
            CAT.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    except (ValueError, RuntimeError) as exc:
        ap.exit(1, str(exc)+'\n')
    print(json.dumps({'pack': name, 'added': added, 'merged': merged, 'total': data['record_count'], 'write': args.write}))
if __name__ == '__main__': main()
