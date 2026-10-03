import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.ingestion.tse import normalize, preserve_archive
from src.statistics.cofre_a import DataError
from src.statistics.freeze_1t import PREREG, PREREG_HASH, build, evidence, family_map, sha

ROOT = Path(__file__).resolve().parents[1]


class FreezeTests(unittest.TestCase):
    def test_prereg_original_hash(self):
        self.assertEqual(sha(ROOT / PREREG), PREREG_HASH)

    def test_aliases_and_unmapped_policy(self):
        mapping = family_map(ROOT)
        self.assertEqual(mapping['IBOPE'], mapping['Ipec'])
        self.assertNotIn('Invented institute', mapping)

    def test_no_2026_outcome_ingestion(self):
        with self.assertRaises(ValueError): preserve_archive(2026, Path('not-read'), ROOT)

    def test_lossless_raw_and_historical_regressions(self):
        expected = {2014: {'DILMA': (43267668, 54501118)},
                    2018: {'JAIR BOLSONARO': (49277010, 57797847)},
                    2022: {'LULA': (57259504, 60345999), 'JAIR BOLSONARO': (51072345, 58206354)}}
        for manifest in sorted((ROOT / 'data/raw/tse').glob('*.manifest.json')):
            result = normalize(manifest, ROOT)
            self.assertEqual(result, json.loads((ROOT / f"data/canonical/tse-results-{result['year']}.json").read_text()))
            for candidate, votes in expected[result['year']].items():
                for t in (1, 2):
                    row = next(r for r in result['rows'] if r['name_original'] == candidate and r['turn'] == t)
                    self.assertEqual(row['votes'], votes[t-1])
            for t in (1, 2):
                self.assertAlmostEqual(sum(r['R'] for r in result['rows'] if r['turn'] == t), 1)

    def test_bad_raw_hash_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'raw.gz').write_bytes(gzip.compress(b'wrong'))
            manifest = root / 'manifest.json'
            manifest.write_text(json.dumps({'year': 2014, 'path': 'raw.gz', 'sha256': '0'*64}))
            with self.assertRaises(ValueError): normalize(manifest, root)

    def test_provenance_is_required(self):
        with self.assertRaises(DataError): evidence(ROOT, [])
        with self.assertRaises(DataError): evidence(ROOT, [{'path': '../escape', 'sha256': '0'*64}])

    def test_prereg_tampering_blocks_before_reading_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); p = root / PREREG; p.parent.mkdir(parents=True)
            p.write_text('altered prereg')
            with self.assertRaises(DataError): build(root)

    def test_incomplete_state_has_no_fake_forecast(self):
        r = build(ROOT)
        ledger = json.loads((ROOT / 'data/canonical/historical-coverage.json').read_text())
        if not any(y['collection_complete'] for y in ledger):
            self.assertEqual(r['status'], 'BLOCKED')
            self.assertEqual(r['calibration']['included_years'], [])
            self.assertEqual(r['calibration']['E_hist_size'], 0)
            self.assertIsNone(r['calibration']['e_ref_1T'])
        prospective = json.loads((ROOT / 'data/canonical/prospective-1t-status.json').read_text())
        if not prospective['collection_complete']:
            self.assertIsNone(r['output_1T']['P'])
            self.assertEqual(r['output_1T']['status'], 'INPUTS_INCOMPLETE')

    def test_registration_inventory_raw_and_duplicates(self):
        from src.ingestion.pesqele import normalize as normalize_inventory
        for manifest in (ROOT / 'data/raw/pesqele').glob('*.manifest.json'):
            d = normalize_inventory(manifest, ROOT)
            expected = json.loads((ROOT / f"data/canonical/pesqele-inventory-{d['year']}.json").read_text())
            self.assertEqual(d, expected)
            self.assertEqual(len(d['rows']), len({r['source_record_id'] for r in d['rows']}))
            self.assertTrue(all(r['eligible'] is None for r in d['rows']))


if __name__ == '__main__': unittest.main()
