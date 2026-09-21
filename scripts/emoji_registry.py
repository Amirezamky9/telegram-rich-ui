"""Shared registry operations. Source mapping is not live Telegram verification."""
from __future__ import annotations
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone

INVALID_FALLBACKS = {"%", "₽", "…", "⋮", "#"}
ID_RE = re.compile(r"[1-9][0-9]{9,19}\Z")

def unique(values):
    return list(dict.fromkeys(v for v in values if v))

def eligible(record):
    return (record.get('selectable') is True and record.get('status') == 'ready'
            and isinstance(record.get('fallback'), str) and bool(record['fallback'].strip())
            and record['fallback'] not in INVALID_FALLBACKS
            and isinstance(record.get('custom_emoji_id'), str)
            and bool(ID_RE.fullmatch(record['custom_emoji_id'])))

def index_records(records):
    by = {}
    for record in records:
        cid = record.get('custom_emoji_id')
        if not isinstance(cid, str) or not ID_RE.fullmatch(cid):
            raise ValueError('Invalid custom emoji ID; IDs must remain decimal strings')
        if cid in by:
            raise ValueError(f'Duplicate catalog ID {cid}; reconcile provenance before importing')
        by[cid] = record
    return by

def recount(data):
    data['records'].sort(key=lambda r: int(r['custom_emoji_id']))
    data['record_count'] = len(data['records'])
    data['selectable_count'] = sum(eligible(r) for r in data['records'])
    data['needs_enrichment_count'] = data['record_count'] - data['selectable_count']

def call(token, method, payload):
    request = urllib.request.Request(
        f'https://api.telegram.org/bot{token}/{method}',
        data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response)
    except urllib.error.HTTPError as exc:
        # URLs and Telegram descriptions can contain token/request data; never echo them.
        raise RuntimeError(f'Telegram HTTP {exc.code}; request failed, no changes written') from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        raise RuntimeError('Telegram transport/JSON failure; no changes written') from None
    if not isinstance(body, dict) or body.get('ok') is not True or 'result' not in body:
        raise RuntimeError('Telegram rejected the request; no changes written')
    return body['result']

def apply_sticker(record, sticker, method, pack=None, source='telegram-bot-api'):
    """Merge one official observation while preserving editorial and prior source metadata."""
    cid = record['custom_emoji_id']
    if sticker.get('custom_emoji_id') != cid or sticker.get('type') != 'custom_emoji':
        raise ValueError('Unexpected sticker identity/type')
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    fallback = sticker.get('emoji')
    fallback = fallback if isinstance(fallback, str) and fallback.strip() else None
    observation = {'source_id': source, 'locator': f'{method}:{cid}', 'fallback': fallback}
    pack = sticker.get('set_name') or pack
    if pack:
        observation['pack'] = pack
    record.setdefault('provenance', [])
    if observation not in record['provenance']:
        record['provenance'].append(observation)
    record['sources'] = unique([*record.get('sources', []), source])
    record['packs'] = unique([*record.get('packs', []), pack])
    record['keywords'] = unique([*record.get('keywords', []), fallback, pack])
    if fallback in INVALID_FALLBACKS:
        fallback = None
    record['fallback'] = fallback  # authoritative response supersedes stale source mapping
    record['animated'] = bool(sticker.get('is_animated'))
    record['is_video'] = bool(sticker.get('is_video'))
    record['needs_repainting'] = bool(sticker.get('needs_repainting'))
    record['selectable'] = bool(fallback)
    record['status'] = 'ready' if fallback else 'needs_enrichment'
    record['verification'] = {'status': 'bot_api_verified' if fallback else 'pending',
                              'checked_at': now, 'method': method}
    return record

def mark_missing(record):
    record['selectable'] = False
    record['status'] = 'needs_enrichment'
    record['verification'] = {'status': 'not_returned',
                              'checked_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                              'method': 'getCustomEmojiStickers'}
