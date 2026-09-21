"""Offline behavioral regressions: no bot token or network needed."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from emoji_registry import apply_sticker, call, eligible, index_records
from enrich_custom_emoji import enrich
from import_emoji_pack import merge_pack, pack_name
from search_emoji import norm
from export_emoji_catalog import csv_row, FIELDS
import validate_emoji_catalog as validator

CAT = json.loads((ROOT/'assets/emoji-catalog/catalog.json').read_text())

def sticker(cid, emoji='✅', **extra):
    return {'custom_emoji_id': cid, 'type': 'custom_emoji', 'emoji': emoji, **extra}

class RegistryTests(unittest.TestCase):
    def test_pending_never_emits_ui_output(self):
        for fmt in ('id', 'html', 'button-json'):
            p = subprocess.run([sys.executable, str(ROOT/'scripts/search_emoji.py'),
                                '--include-unverified', '--format', fmt], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(p.stdout, '')

    def test_exact_id_and_persian_search(self):
        self.assertEqual(norm('كِيف پول'), norm('کیف پول'))
        self.assertEqual(norm('به‌روزرسانی'), norm('به روزرسانی'))
        for query in ('5884510167986343350', 'پشتیبانی'):
            p = subprocess.run([sys.executable, str(ROOT/'scripts/search_emoji.py'), query,
                                '--limit', '1', '--format', 'json'], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(p.stdout)[0]['custom_emoji_id'], '5884510167986343350')

    def test_merge_preserves_editorial_and_provenance(self):
        record = copy.deepcopy(next(r for r in CAT['records'] if r['name']=='support'))
        before = copy.deepcopy(record)
        data = {'records': [record]}
        st = sticker(record['custom_emoji_id'], '💬', is_video=True)
        pack = {'sticker_type': 'custom_emoji', 'stickers': [st, st]}
        self.assertEqual(merge_pack(data, pack, 'Example', tags=['test']), (0,1))
        merge_pack(data, pack, 'Example', tags=['test'])
        self.assertEqual(len(data['records']), 1)
        for key in ('description','aliases','usage_notes','label_fa','category'):
            self.assertEqual(record[key], before[key])
        self.assertTrue(all(o in record['provenance'] for o in before['provenance']))
        self.assertEqual(len(record['provenance']), len(before['provenance'])+1)
        self.assertTrue(record['is_video'])
        self.assertEqual(record['verification']['status'], 'bot_api_verified')

    def test_authoritative_fallback_changes_preserve_source(self):
        record = copy.deepcopy(CAT['records'][0]); previous=copy.deepcopy(record['provenance'])
        apply_sticker(record, sticker(record['custom_emoji_id'], '✅'), 'getCustomEmojiStickers')
        self.assertEqual(record['fallback'], '✅')
        self.assertTrue(all(o in record['provenance'] for o in previous))
        apply_sticker(record, sticker(record['custom_emoji_id'], None), 'getCustomEmojiStickers')
        self.assertFalse(eligible(record))
        self.assertIsNone(record['fallback'])

    def test_batches_missing_and_unexpected_ids(self):
        data = {'records': copy.deepcopy(CAT['records'][:201])}; sizes=[]
        def fake(token, method, payload):
            sizes.append(len(payload['custom_emoji_ids']))
            return []
        report=enrich(data, 'unused', True, fake)
        self.assertEqual(sizes, [200,1])
        self.assertEqual(report['not_returned'], 201)
        self.assertTrue(all(not eligible(r) for r in data['records']))
        with self.assertRaises(ValueError):
            enrich(data, 'unused', True, lambda *args: [sticker('1234567890')])

    def test_regional_enrichment_remains_valid(self):
        data = copy.deepcopy(CAT)
        regional = next(r for r in data['records'] if r['category']=='regional_iran')
        apply_sticker(regional, sticker(regional['custom_emoji_id'], '🇮🇷'), 'getCustomEmojiStickers')
        from emoji_registry import recount
        recount(data)
        import csv
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)
            for path in (ROOT/'assets/emoji-catalog').glob('*.json'):
                (dest/path.name).write_text(path.read_text())
            (dest/'catalog.json').write_text(json.dumps(data))
            with (dest/'catalog.csv').open('w', newline='') as f:
                w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(csv_row(r) for r in data['records'])
            with patch.object(validator,'DIR',dest), patch('builtins.print'):
                self.assertEqual(validator.main(),0)
                sources=json.loads((dest/'sources.json').read_text());sources['sources']=[]
                (dest/'sources.json').write_text(json.dumps(sources))
                self.assertEqual(validator.main(),1)

    def test_csv_detects_stale_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)
            for path in (ROOT/'assets/emoji-catalog').glob('*'):
                if path.suffix in ('.json','.csv'): (dest/path.name).write_bytes(path.read_bytes())
            data=copy.deepcopy(CAT);data['records'][0]['description']='Changed without exporting'
            (dest/'catalog.json').write_text(json.dumps(data))
            with patch.object(validator,'DIR',dest),patch('builtins.print'):
                self.assertEqual(validator.main(),1)

    def test_reject_invalid_pack_and_duplicate_input(self):
        with self.assertRaises(ValueError): pack_name('https://t.me/addstickers/Example')
        with self.assertRaises(ValueError): index_records([CAT['records'][0]]*2)
        with self.assertRaises(ValueError): merge_pack({'records':[]},{'sticker_type':'regular'},'Example')
        data={'records':[]}
        merge_pack(data, {'sticker_type':'custom_emoji','stickers':[sticker('1234567890')]}, 'Example')
        self.assertEqual(data['record_count'],1)
        self.assertEqual(data['records'][0]['sources'],['telegram-bot-api'])

    def test_error_does_not_expose_token(self):
        from urllib.error import URLError
        with patch('urllib.request.urlopen',side_effect=URLError('https://api.telegram.org/botSECRET/method')):
            with self.assertRaises(RuntimeError) as ctx: call('SECRET','getStickerSet',{})
        self.assertNotIn('SECRET',str(ctx.exception))
        self.assertIsNone(ctx.exception.__cause__)

if __name__ == '__main__': unittest.main()
