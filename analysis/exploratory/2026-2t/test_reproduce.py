"""Regression checks for the isolated official-result normalization."""
import copy
import unittest
from pathlib import Path

import reproduce as r


class OfficialSnapshotTests(unittest.TestCase):
    def setUp(self):
        sources = r.read_json((r.HERE / 'sources.json').read_bytes())['sources']
        self.source = next(s for s in sources if s['name'] == 'tse-result-2t')
        self.data = r.read_json((r.ROOT / self.source['path']).read_bytes())

    def test_snapshot_reproduces_exactly(self):
        self.assertEqual(r.serialized(r.build()), (r.HERE / 'official-outcome.json').read_text())

    def test_wrong_scope_round_simulation_and_partial_rejected(self):
        for key, value in [('t', '1'), ('ele', '6257'), ('tpabr', 'uf'), ('f', 's'), ('tf', 'n'), ('and', 'p')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                r.normalize(dict(self.data, **{key: value}), self.source)

    def test_total_mismatch_rejected(self):
        d = copy.deepcopy(self.data)
        d['v']['tv'] = str(int(d['v']['tv']) + 1)
        with self.assertRaises(ValueError):
            r.normalize(d, self.source)

    def test_duplicate_candidate_identity_rejected(self):
        d = copy.deepcopy(self.data)
        candidates = [c for a in d['carg'][0]['agr'] for p in a['par'] for c in p['cand']]
        candidates[1]['sqcand'] = candidates[0]['sqcand']
        with self.assertRaises(ValueError):
            r.normalize(d, self.source)

    def test_changed_vote_destination_rejected(self):
        d = copy.deepcopy(self.data)
        d['carg'][0]['agr'][0]['par'][0]['cand'][0]['dvt'] = 'Anulado sub judice'
        with self.assertRaises(ValueError):
            r.normalize(d, self.source)

    def test_duplicate_keys_and_nonfinite_rejected(self):
        for raw in [b'{"t":"1","t":"2"}', b'{"v":NaN}', b'{"v":Infinity}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                r.read_json(raw)

    def test_never_promotes_outcome_to_forecast(self):
        result = r.build()
        self.assertFalse(result['prospective_forecast'])
        for key in ('P', 'intervals', 'e_ref_2T', 'q90', 'sigma_hat'):
            self.assertIsNone(result[key])
        self.assertEqual(result['Q2'], 'NOT_EVALUABLE_NO_VALID_FREEZE')


if __name__ == '__main__':
    unittest.main()
