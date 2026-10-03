"""Synthetic fixtures only; no election outcome 2026 is used."""
import copy
from datetime import date, datetime, timezone
import math
import unittest

from src.statistics.cofre_a import (DataError, aggregate, calibrate, convert,
                                   expit, intervals, logit, quantile90, scenario)

D = date(2022, 10, 2)
CUTOFF = datetime(2022, 10, 2, 15, tzinfo=timezone.utc)
OFFICIAL = ['Jair Bolsonaro', 'Other']


def poll(index=1, institute=None, end='2022-10-01', sample=1000, valid=None):
    return {'poll_id': f'p{index}', 'registration': f'BR-{index:05d}/2022',
            'year': 2022, 'turn': 1, 'institute': institute or f'i{index}',
            'office': 'Presidente', 'scope': 'Brasil', 'exit_poll': False,
            'fieldwork_start': min('2022-09-18', end), 'fieldwork_end': end,
            'published_at': '2022-10-01T20:00:00-03:00', 'sample_size': sample,
            'mode': 'synthetic', 'scenarios': [{'scenario_id': 's1', 'stimulated': True,
            'candidates': OFFICIAL, 'valid': valid or dict(zip(OFFICIAL, [.4, .6]))}]}


def agg(rows, families=None):
    return aggregate(rows, OFFICIAL, D, CUTOFF, 1, families or {})


def ledger(complete=False):
    return [{'year': y, 'collection_complete': complete, 'reason': 'missing poll inventory',
             'coverage_evidence': ['synthetic-fixture-only'],
             'turns': {str(t): {'aggregate': {'status': 'ESTIMÁVEL', 'P': dict(zip(OFFICIAL, [.4, .6]))},
                              'R': dict(zip(OFFICIAL, [.45, .55]))} for t in (1, 2)}}
            for y in (2014, 2018, 2022)]


class CofreATests(unittest.TestCase):
    def test_floor_no_number(self):
        for n in (0, 1, 2):
            self.assertIsNone(agg([poll(i) for i in range(1, n+1)])['P'])

    def test_equal_weight_not_sample_weight(self):
        rows = [poll(1, sample=100, valid=dict(zip(OFFICIAL, [.2, .8]))), poll(2), poll(3, sample=10000)]
        self.assertAlmostEqual(agg(rows)['P'][OFFICIAL[0]], 1/3)

    def test_family_successor_collapsed(self):
        rows = [poll(1, 'IBOPE'), poll(2, 'Ipec'), poll(3, 'Datafolha')]
        r = agg(rows, {'IBOPE': 'same', 'Ipec': 'same', 'Datafolha': 'df'})
        self.assertEqual(len(r['families']), 2)
        self.assertIsNone(r['P'])

    def test_recency_then_sample_then_registration(self):
        rows = [poll(1, 'same', end='2022-09-30', sample=9999),
                poll(4, 'same', sample=100), poll(3, 'same', sample=200), poll(2, 'same', sample=200)]
        self.assertEqual(agg(rows)['poll_ids'], ['p2'])

    def test_window_end_inclusive(self):
        rows = [poll(1, end='2022-09-18'), poll(2, end='2022-09-17'), poll(3, end='2022-10-02')]
        self.assertEqual(agg(rows)['poll_ids'], ['p1'])

    def test_publication_cutoff(self):
        p = poll(); p['published_at'] = '2022-10-02T12:00:01-03:00'
        self.assertEqual(agg([p])['poll_ids'], [])

    def test_duplicate_id(self):
        with self.assertRaises(DataError): agg([poll(), poll()])

    def test_bad_dates(self):
        p = poll(); p['fieldwork_start'] = '2022-10-02'
        with self.assertRaises(DataError): agg([p])

    def test_unknown_family_flag(self):
        self.assertIn('UNMAPPED_FAMILY', agg([poll()])['selected'][0]['flags'])

    def test_scenario_max_intersection_before_size(self):
        p = poll(); p['scenarios'].append({'scenario_id': 'wrong', 'stimulated': True,
                                         'candidates': ['Other', 'Extra', 'Extra2']})
        self.assertEqual(scenario(p, OFFICIAL, 1)['scenario_id'], 's1')

    def test_scenario_unresolved_tie_stops(self):
        p = poll(); p['scenarios'].append(copy.deepcopy(p['scenarios'][0]))
        with self.assertRaises(DataError): scenario(p, OFFICIAL, 1)

    def test_trim_and_total_conversion(self):
        s = {'candidates': OFFICIAL + ['Undeferred'], 'total': dict(zip(OFFICIAL + ['Undeferred'], [.3, .5, .1]))}
        values, flags, transformation = convert(s, OFFICIAL)
        self.assertAlmostEqual(values[OFFICIAL[0]], .375)
        self.assertEqual(flags, ['SCENARIO_TRIMMED'])
        self.assertEqual(transformation, 'totais_to_validos_v1')

    def test_published_precedence_mismatch(self):
        s = {'candidates': OFFICIAL, 'valid': dict(zip(OFFICIAL, [.4, .6])), 'total': dict(zip(OFFICIAL, [.3, .5]))}
        values, flags, _ = convert(s, OFFICIAL)
        self.assertEqual(values[OFFICIAL[0]], .4)
        self.assertIn('DENOMINATOR_MISMATCH', flags)

    def test_missing_not_zero(self):
        self.assertIsNone(convert({'candidates': OFFICIAL}, OFFICIAL)[0])
        with self.assertRaises(DataError): convert({'candidates': ['Other'], 'valid': {'Other': 1}}, OFFICIAL)

    def test_invalid_shares(self):
        for v in (float('nan'), float('inf'), -1, 2, None, True):
            with self.assertRaises(DataError): convert({'candidates': OFFICIAL, 'valid': dict(zip(OFFICIAL, [v, .6]))}, OFFICIAL)

    def test_noncompositional_vector(self):
        with self.assertRaises(DataError): convert({'candidates': OFFICIAL, 'valid': dict(zip(OFFICIAL, [.4, .2]))}, OFFICIAL)

    def test_incomplete_year_excluded_as_whole(self):
        years = ledger(True); years[0]['collection_complete'] = False
        r = calibrate(years)
        self.assertEqual(r['included_years'], [2018, 2022])
        self.assertEqual(r['E_hist_size'], 8)
        self.assertEqual(r['excluded_years'][0]['reason'], 'UNRECOVERABLE')

    def test_all_years_missing_blocks(self):
        r = calibrate(ledger())
        for field in ('e_ref_1T', 'q90', 'sigma_hat'): self.assertIsNone(r[field])
        self.assertEqual(r['E_hist_size'], 0)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertEqual(r['q2_status'], 'UNAVAILABLE')

    def test_missing_second_turn_not_complete(self):
        years = ledger(True); del years[0]['turns']['2']
        with self.assertRaises(DataError): calibrate(years)

    def test_missing_year_not_silent(self):
        with self.assertRaises(DataError): calibrate(ledger()[:2])

    def test_reference_direction_and_sample_sd(self):
        r = calibrate(ledger(True))
        self.assertAlmostEqual(r['e_ref_1T'], logit(.45)-logit(.4))
        self.assertGreater(r['sigma_hat'], 0)
        self.assertEqual(r['q2_status'], 'PENDING_OUTCOME')

    def test_empty_hypothesis_not_unavailable(self):
        years = ledger(True)
        years[2]['turns']['1']['R'] = dict(zip(OFFICIAL, [.35, .65]))
        self.assertEqual(calibrate(years)['q2_status'], 'VAZIA')

    def test_q90_known_type7(self):
        self.assertAlmostEqual(quantile90([1, -2, 3, -4]), 3.7)

    def test_logit_no_clipping(self):
        for p in (0, 1, float('nan')):
            with self.assertRaises(DataError): logit(p)
        self.assertAlmostEqual(expit(logit(.45)), .45)

    def test_intervals(self):
        r = intervals({'large': .4, 'small': .01}, calibrate(ledger(True)))
        self.assertEqual(r['small']['status'], 'NOT_APPLICABLE')
        self.assertLess(r['large']['empirical_90'][0], .4)
        self.assertGreater(r['large']['empirical_90'][1], .4)


if __name__ == '__main__': unittest.main()
