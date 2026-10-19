"""Synthetic fixtures only: no real 2026 candidates, polls or vote outcomes."""
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.ingestion.prospective import preserve
from src.statistics.cofre_a import DataError, aggregate, logit
from src.statistics import freeze_2t as flow
from src.statistics.freeze_1t import PREREG, PREREG_HASH, sha
from src.validation.prospective import Audit, CUTOFF, DEADLINE, ELECTION, families, packet, reject_outcomes

ROOT = Path(__file__).resolve().parents[1]


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ('src', 'tests', 'docs', 'methodology', 'sources', '.github'):
            shutil.copytree(ROOT / folder, self.root / folder, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('PROMPT.md', 'AGENTS.md', 'requirements.txt', '.gitignore'):
            shutil.copy(ROOT / name, self.root / name)
        (self.root / 'data/canonical').mkdir(parents=True)
        (self.root / 'data/derived').mkdir()
        for path in (ROOT / 'data/canonical').glob('*.json'):
            shutil.copy(path, self.root / 'data/canonical' / path.name)
        shutil.copy(ROOT / 'data/derived/cofre-a-1t-2026.json', self.root / 'data/derived')
        source = self.root / 'data/raw/synthetic-evidence.txt'
        source.parent.mkdir(parents=True)
        source.write_text('SYNTHETIC TEST EVIDENCE; NOT A REAL POLL OR COVERAGE CERTIFICATE')
        self.ref = dict(path=source.relative_to(self.root).as_posix(), sha256=sha(source),
                        url='https://www.tse.jus.br/synthetic-test-only', retrieved_at='2026-10-25T12:00:00-03:00',
                        location='synthetic fixture')
        self.mapping = families(Audit(self.root))
        self.polls = [self.poll(i) for i in range(3)]
        self.inventory = dict(year=2026, turn=2, status='AUDITED', complete=True, sources=[self.ref], rows=[
            dict({k: p[k] for k in ('poll_id', 'registration', 'institute', 'fieldwork_start', 'fieldwork_end', 'office', 'scope', 'exit_poll', 'mode', 'sample_size', 'institute_legal_id', 'published_at')},
                 sources=[self.ref]) for p in self.polls])
        self.write('data/canonical/prospective-2t-inventory.json', self.inventory)
        self.p = dict(year=2026, turn=2, official_candidates=dict(names=['A', 'B'],
                      tse_ids={'A': 'synthetic-a', 'B': 'synthetic-b'}, status='CLASSIFICADOS_2T', sources=[self.ref]),
                      target=dict(name='A', party='PL', endorser='Jair Bolsonaro', sources=[self.ref]),
                      polls=self.polls, coverage=dict(complete=True, reviewer='SYNTHETIC TEST', method='fixture',
                      sources=[self.ref], as_of='2026-10-25T12:00:00-03:00', no_2026_outcomes_used=True,
                      inventory_sha256=sha(self.root / 'data/canonical/prospective-2t-inventory.json'),
                      inventory_poll_ids=[p['poll_id'] for p in self.polls], not_published=[]))
        self.write('data/canonical/packet-2t.json', self.p)

    def write(self, path, obj):
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(flow.serialized(obj))

    def poll(self, i, **changes):
        p = dict(poll_id=f'synthetic-{i}', registration=f'BR-{i+1:05d}/2026', institute=f'Unmapped-{i}',
                 institute_legal_id=f'SYNTHETIC-{i}', year=2026, turn=2, office='Presidente', scope='Brasil',
                 mode='SYNTHETIC', exit_poll=False, sample_size=1000,
                 fieldwork_start='2026-10-22', fieldwork_end='2026-10-24',
                 published_at='2026-10-25T11:00:00-03:00', sources=[self.ref],
                 scenarios=[dict(scenario_id='s', stimulated=True, candidates=['A', 'B'], valid={'A': .52, 'B': .48},
                                 original_values={'A': 52, 'B': 48}, original_denominator='valid percent', sources=[self.ref])])
        p.update(changes)
        return p

    def load(self):
        self.write('data/canonical/packet-2t.json', self.p)
        return packet(Audit(self.root), 'data/canonical/packet-2t.json',
                      'data/canonical/prospective-2t-inventory.json', self.mapping)

    def complete_prospective(self):
        self.write(flow.STATUS, dict(year=2026, turn=2, collection_complete=True,
                   packet='data/canonical/packet-2t.json', inventory='data/canonical/prospective-2t-inventory.json',
                   late_discovery=[]))
        self.write('sources/institutes/families-2t-review.json', dict(complete=True, reviewer='SYNTHETIC',
                   table_sha256=sha(self.root / 'sources/institutes/families-2t.yaml'), families={}))

    def complete_history(self):
        """Exercise existing raw normalization/aggregation on synthetic 2022, both turns."""
        columns = 'ANO_ELEICAO;NR_TURNO;SG_UE;CD_CARGO;SQ_CANDIDATO;NM_URNA_CANDIDATO;QT_VOTOS_NOMINAIS;CD_MUNICIPIO;NR_ZONA;ST_VOTO_EM_TRANSITO;DS_DETALHE_SITUACAO_CAND'
        lines = [columns]
        for turn in (1, 2):
            lines += [f'2022;{turn};BR;1;1;Jair Bolsonaro;60;1;1;N;DEFERIDO',
                      f'2022;{turn};BR;1;2;Lula;40;1;1;N;DEFERIDO']
        raw = ('\n'.join(lines)+'\n').encode('latin1')
        raw_path = self.root / 'data/raw/synthetic-2022.csv.gz'
        raw_path.write_bytes(gzip.compress(raw, mtime=0))
        self.write('data/raw/synthetic-2022.manifest.json', dict(year=2022, path='data/raw/synthetic-2022.csv.gz',
                   sha256=sha(raw_path), member_sha256=hashlib.sha256(raw).hexdigest()))
        for turn, end in [(1, '2022-09-30'), (2, '2022-10-28')]:
            p = copy.deepcopy(self.p)
            p['year'], p['turn'] = 2022, turn
            p['official_candidates'] = dict(names=['Jair Bolsonaro', 'Lula'], tse_ids={'Jair Bolsonaro': '1', 'Lula': '2'}, sources=[self.ref])
            for row in p['polls']:
                row.update(year=2022, turn=turn, fieldwork_start=end, fieldwork_end=end,
                           published_at=end+'T12:00:00-03:00', registration=row['registration'].replace('2026', '2022'))
                row['scenarios'][0].update(candidates=['Jair Bolsonaro', 'Lula'],
                                          valid={'Jair Bolsonaro': .7 if turn == 1 else .5, 'Lula': .3 if turn == 1 else .5})
            self.write(f'data/canonical/synthetic-2022-{turn}.json', p)
        ledger = json.loads((self.root / flow.LEDGER).read_text())
        ledger[2].update(collection_complete=True, packets={'1': 'data/canonical/synthetic-2022-1.json',
                         '2': 'data/canonical/synthetic-2022-2.json'}, coverage_evidence=[self.ref],
                         tse_manifest='data/raw/synthetic-2022.manifest.json')
        self.write(flow.LEDGER, ledger)


class EligibilityTests(Fixture):
    def test_ready_packet_uses_two_candidates_and_unmapped_families(self):
        result, _ = self.load()
        self.assertEqual(result['P'], {'A': .52, 'B': .48})
        self.assertEqual(result['adv'], 'B')
        self.assertTrue(all('UNMAPPED_FAMILY' in p['flags'] for p in result['selected']))

    def test_inclusive_fieldwork_and_publication_boundaries(self):
        for end, eligible in [('2026-10-10', False), ('2026-10-11', True), ('2026-10-24', True), ('2026-10-25', False)]:
            for published, within in [('2026-10-25T12:00:00-03:00', True), ('2026-10-25T15:00:01+00:00', False)]:
                polls = [self.poll(i, fieldwork_start=end, fieldwork_end=end, published_at=published) for i in range(3)]
                result = aggregate(polls, ['A', 'B'], ELECTION, CUTOFF, 2, {})
                self.assertEqual(result['P'] is not None, eligible and within)

    def test_extra_candidate_spontaneous_and_wrong_pair_rejected(self):
        for candidates, stimulated in [(['A', 'B', 'C'], True), (['A', 'B'], False), (['A', 'C'], True)]:
            p = self.polls[0]['scenarios'][0]
            p.update(candidates=candidates, stimulated=stimulated)
            result, _ = self.load()
            self.assertEqual(result['status'], 'NÃO_ESTIMÁVEL')
            self.assertIsNone(result['P'])
            self.assertEqual(result['excluded'][0]['reason'], 'NOT_PUBLISHED')

    def test_exact_pair_scenario_tie_fails(self):
        self.polls[0]['scenarios'].append(copy.deepcopy(self.polls[0]['scenarios'][0]))
        with self.assertRaises(DataError): self.load()

    def test_duplicate_registration_does_not_multiply_families(self):
        self.polls[1]['registration'] = self.polls[0]['registration']
        self.inventory['rows'][1]['registration'] = self.polls[0]['registration']
        self.write('data/canonical/prospective-2t-inventory.json', self.inventory)
        self.p['coverage']['inventory_sha256'] = sha(self.root / 'data/canonical/prospective-2t-inventory.json')
        with self.assertRaisesRegex(DataError, 'same registration'): self.load()

    def test_family_selection_tiebreakers_and_one_wave(self):
        polls = [self.poll(0, institute='Ipec'), self.poll(1, institute='IBOPE'), self.poll(2)]
        polls[0]['sample_size'] = 2000
        result = aggregate(polls, ['A', 'B'], ELECTION, CUTOFF, 2, self.mapping)
        self.assertEqual(len(result['families']), 2)
        self.assertIn('synthetic-0', result['poll_ids'])
        polls[0]['sample_size'] = 1000
        result = aggregate(polls, ['A', 'B'], ELECTION, CUTOFF, 2, self.mapping)
        self.assertIn('synthetic-0', result['poll_ids'])
        polls[0]['fieldwork_end'] = '2026-10-23'
        result = aggregate(polls, ['A', 'B'], ELECTION, CUTOFF, 2, self.mapping)
        self.assertIn('synthetic-1', result['poll_ids'])

    def test_missing_target_or_qualification_fails(self):
        for section, key, bad in [('target', 'name', 'C'), ('target', 'party', 'OTHER'),
                                  ('official_candidates', 'status', 'HYPOTHETICAL')]:
            with self.subTest(key=key):
                old = self.p[section][key]; self.p[section][key] = bad
                with self.assertRaises(DataError): self.load()
                self.p[section][key] = old

    def test_missing_transcription_source_fails(self):
        self.polls[0]['scenarios'][0]['sources'] = []
        with self.assertRaises(DataError): self.load()

    def test_inventory_mismatch_or_unaccounted_poll_fails(self):
        self.p['coverage']['inventory_poll_ids'].append('omitted')
        with self.assertRaises(DataError): self.load()

    def test_future_or_naive_or_early_coverage_fails(self):
        for value in ['2026-10-25T11:59:59-03:00', '2026-10-25T12:00:00', '2026-10-25T17:00:00-03:00']:
            self.p['coverage']['as_of'] = value
            with self.assertRaises(DataError): self.load()

    def test_outcome_guard_is_recursive(self):
        for key in ('R', 'results', 'outcomes', 'votes', 'official_results'):
            with self.assertRaises(DataError): reject_outcomes({'nested': [{'nested': {key: 1}}]})

    def test_source_tampering_and_escape_fail(self):
        (self.root / self.ref['path']).write_text('changed')
        with self.assertRaises(DataError): self.load()
        with self.assertRaises(DataError): Audit(self.root).track('../escape')


class FlowTests(Fixture):
    def test_initial_state_nulls_and_1t_preservation(self):
        before = {name: sha(self.root / name) for name in flow.PROTECTED}
        result = flow.build(self.root)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['calibration']['E_hist_size'], 0)
        self.assertEqual(len(result['calibration']['excluded_years']), 3)
        for key in ('e_ref_2T', 'q90', 'sigma_hat'):
            self.assertIsNone(result['calibration'][key])
        self.assertIsNone(result['output_2T']['P'])
        self.assertEqual(before, {name: sha(self.root / name) for name in flow.PROTECTED})
        self.assertEqual(flow.serialized(result), flow.serialized(flow.build(self.root)))

    def test_original_prereg_preserved(self):
        self.assertEqual(sha(self.root / PREREG), PREREG_HASH)
        (self.root / PREREG).write_text('tampered')
        with self.assertRaises(DataError): flow.build(self.root)

    def test_complete_history_and_prospective_reuse_estimator(self):
        self.complete_history(); self.complete_prospective()
        r = flow.build(self.root)
        c = r['calibration']
        self.assertEqual(r['status'], 'READY_FOR_FREEZE')
        self.assertEqual(c['included_years'], [2022])
        self.assertEqual(c['E_hist_size'], 4)
        self.assertAlmostEqual(c['e_ref_2T'], logit(.6) - logit(.5))
        self.assertLess(c['e_ref_1T'], 0)
        self.assertGreater(c['e_ref_2T'], 0)
        self.assertIsNotNone(r['output_2T']['intervals'])
        self.assertIn('data/raw/synthetic-2022.csv.gz', r['artifact_sha256'])
        self.assertIn(self.ref['path'], r['inputs']['raw_sha256'])

    def test_incomplete_year_excludes_both_turns(self):
        self.complete_history()
        ledger = json.loads((self.root / flow.LEDGER).read_text())
        ledger[2]['collection_complete'] = False
        self.write(flow.LEDGER, ledger)
        self.assertEqual(flow.build(self.root)['calibration']['E_hist_size'], 0)

    def test_claimed_complete_year_missing_second_packet_fails(self):
        self.complete_history()
        ledger = json.loads((self.root / flow.LEDGER).read_text()); del ledger[2]['packets']['2']
        self.write(flow.LEDGER, ledger)
        with self.assertRaises(KeyError): flow.build(self.root)

    def test_family_review_missing_blocks_without_fabrication(self):
        self.complete_history(); self.complete_prospective()
        self.write('sources/institutes/families-2t-review.json', dict(complete=False))
        r = flow.build(self.root)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertTrue(any('FAMILY_' in b for b in r['blockers']))

    def test_family_review_hash_and_alias_conflicts_fail(self):
        self.complete_history(); self.complete_prospective()
        review = json.loads((self.root / 'sources/institutes/families-2t-review.json').read_text())
        review['table_sha256'] = '0' * 64
        self.write('sources/institutes/families-2t-review.json', review)
        with self.assertRaises(DataError): flow.build(self.root)
        path = self.root / 'sources/institutes/families-2t.yaml'
        path.write_text(path.read_text() + '\n  conflict:\n    aliases: [ipec]\n    basis: synthetic\n')
        with self.assertRaises(DataError): families(Audit(self.root))

    def test_known_family_needs_raw_review(self):
        from src.validation.prospective import family_review
        self.complete_prospective()
        with self.assertRaises(DataError): family_review(Audit(self.root), self.mapping, {'Ipec'})

    def test_nonpositive_second_reference_is_vazia(self):
        self.complete_history()
        p = json.loads((self.root / 'data/canonical/synthetic-2022-2.json').read_text())
        for row in p['polls']:
            row['scenarios'][0]['valid'] = {'Jair Bolsonaro': .7, 'Lula': .3}
        self.write('data/canonical/synthetic-2022-2.json', p)
        self.assertEqual(flow.build(self.root)['calibration']['q2_status'], 'VAZIA')

    def test_late_discovery_cannot_reenter_inputs(self):
        self.complete_prospective()
        s = json.loads((self.root / flow.STATUS).read_text())
        s['late_discovery'] = [dict(poll_id='synthetic-0')]
        self.write(flow.STATUS, s)
        with self.assertRaises(DataError): flow.build(self.root)

    def test_artifact_tampering_fails(self):
        r = flow.build(self.root)
        self.write(flow.OUTPUT, r)
        (self.root / flow.MANIFEST).write_text(flow.markdown(r))
        flow.verify_artifacts(self.root, r)
        (self.root / flow.OUTPUT).write_text('{}')
        with self.assertRaises(DataError): flow.verify_artifacts(self.root, r)

    def test_time_gate_exact_boundaries_and_future_attestation(self):
        r = dict(coverage_as_of=CUTOFF.isoformat())
        for moment in ['2026-10-25T11:59:59-03:00', '2026-10-25T17:00:00-03:00', '2026-10-26T00:00:00-03:00']:
            with self.assertRaises(DataError): flow.time_gate(r, datetime.fromisoformat(moment))
        flow.time_gate(r, CUTOFF)
        flow.time_gate(r, datetime.fromisoformat('2026-10-25T16:59:59-03:00'))
        r['coverage_as_of'] = '2026-10-25T13:00:00-03:00'
        with self.assertRaises(DataError): flow.time_gate(r, CUTOFF)

    def test_blocked_freeze_creates_no_tag(self):
        r = flow.build(self.root); self.write(flow.OUTPUT, r)
        (self.root / flow.MANIFEST).write_text(flow.markdown(r))
        with patch.object(flow, 'git') as git:
            with self.assertRaisesRegex(DataError, 'BLOCKED'): flow.freeze(self.root)
            git.assert_not_called()


class GitFreezeTests(Fixture):
    def setUp(self):
        super().setUp()
        self.complete_history(); self.complete_prospective()
        subprocess.run(['git', 'init', '-q'], cwd=self.root, check=True)
        self.g('config', 'user.name', 'Synthetic Test')
        self.g('config', 'user.email', 'synthetic@example.org')
        self.commit('baseline')
        self.base = self.g('rev-parse', 'HEAD')
        self.base_patch = patch.object(flow, 'BASE', self.base)
        self.base_patch.start(); self.addCleanup(self.base_patch.stop)
        self.clock_patch = patch.object(flow, 'datetime')
        self.clock = self.clock_patch.start(); self.addCleanup(self.clock_patch.stop)
        self.clock.now.return_value = datetime.fromisoformat('2026-10-25T13:00:00-03:00')
        self.prepare()
        self.commit('synthetic final input seal')

    def g(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True).strip()

    def commit(self, message):
        import os
        self.g('add', '.')
        environment = dict(os.environ, GIT_AUTHOR_DATE='2026-10-25T12:30:00-03:00',
                           GIT_COMMITTER_DATE='2026-10-25T12:30:00-03:00')
        subprocess.run(['git', 'commit', '-qm', message], cwd=self.root, env=environment, check=True)

    def prepare(self):
        r = flow.build(self.root)
        self.write(flow.OUTPUT, r)
        (self.root / flow.MANIFEST).write_text(flow.markdown(r))

    def test_clean_committed_input_set_passes_without_creating_tag(self):
        r, head = flow.check(self.root)
        self.assertEqual(r['status'], 'READY_FOR_FREEZE')
        self.assertEqual(head, self.g('rev-parse', 'HEAD'))
        self.assertFalse(self.g('tag', '--list', flow.TAG))

    def test_untracked_file_blocks(self):
        (self.root / 'untracked').write_text('pending')
        with self.assertRaisesRegex(DataError, 'clean'): flow.check(self.root)

    def test_committed_change_to_1t_cannot_be_hidden_by_regeneration(self):
        (self.root / 'data/derived/cofre-a-1t-2026.json').write_text('{}')
        self.prepare(); self.commit('synthetic tampering')
        with self.assertRaisesRegex(DataError, 'protected'): flow.check(self.root)

    def test_existing_reference_is_never_moved(self):
        self.g('tag', flow.TAG, self.base)
        with self.assertRaisesRegex(DataError, 'already exists'): flow.freeze(self.root)
        self.assertEqual(self.g('rev-parse', flow.TAG), self.base)

    def test_deadline_rechecked_after_test_suite(self):
        original = subprocess.run
        def run(args, **kwargs):
            if args[:3] == [sys.executable, '-m', 'unittest']:
                self.clock.now.return_value = DEADLINE
                return subprocess.CompletedProcess(args, 0)
            return original(args, **kwargs)
        with patch.object(flow.subprocess, 'run', side_effect=run):
            with self.assertRaisesRegex(DataError, 'outside freeze'): flow.freeze(self.root)
        self.assertFalse(self.g('tag', '--list', flow.TAG))

    def test_successful_freeze_creates_annotated_exact_head_reference(self):
        original = subprocess.run
        def run(args, **kwargs):
            if args[:3] == [sys.executable, '-m', 'unittest']:
                return subprocess.CompletedProcess(args, 0)
            return original(args, **kwargs)
        head = self.g('rev-parse', 'HEAD')
        with patch.object(flow.subprocess, 'run', side_effect=run): flow.freeze(self.root)
        self.assertEqual(self.g('cat-file', '-t', flow.TAG), 'tag')
        self.assertEqual(self.g('rev-parse', flow.TAG + '^{}'), head)
        self.assertIn('manifest_sha256', self.g('cat-file', '-p', flow.TAG))

    def test_pre_tag_ready_commit_seals_inputs(self):
        r = flow.build(self.root)
        changed = copy.deepcopy(r)
        changed['inputs']['poll_ids'].append('late-poll')
        with self.assertRaisesRegex(DataError, 'seal cannot be revised'):
            flow.committed_seal(self.root, changed)

    def test_assume_unchanged_cannot_hide_uncommitted_bytes(self):
        name = 'docs/cofre-a-freeze-2t.md'
        self.g('update-index', '--assume-unchanged', name)
        path = self.root / name
        path.write_text(path.read_text() + '\nHidden edit\n')
        r = flow.build(self.root)
        # Attacker also updates derived files and hides those changes from status.
        for output in (flow.OUTPUT, flow.MANIFEST):
            self.g('update-index', '--assume-unchanged', output)
        self.write(flow.OUTPUT, r)
        (self.root / flow.MANIFEST).write_text(flow.markdown(r))
        self.assertEqual(self.g('status', '--porcelain'), '')
        with self.assertRaisesRegex(DataError, 'working bytes differ'):
            flow.check(self.root)

    def test_failed_tests_never_create_reference(self):
        original = subprocess.run
        def run(args, **kwargs):
            if args[:3] == [sys.executable, '-m', 'unittest']:
                raise subprocess.CalledProcessError(1, args)
            return original(args, **kwargs)
        with patch.object(flow.subprocess, 'run', side_effect=run):
            with self.assertRaises(subprocess.CalledProcessError): flow.freeze(self.root)
        self.assertFalse(self.g('tag', '--list', flow.TAG))


class DocumentValidationTests(Fixture):
    def test_duplicate_json_keys_are_rejected(self):
        path = self.root / flow.STATUS
        path.write_text('{"collection_complete": false, "collection_complete": true}')
        with self.assertRaisesRegex(DataError, 'duplicate'): Audit(self.root).read(flow.STATUS)

    def test_nonfinite_json_numbers_are_rejected(self):
        from src.validation.prospective import strict_json
        for value in ('NaN', 'Infinity', '-Infinity', '1e999'):
            with self.subTest(value=value):
                with self.assertRaises(DataError): strict_json('{"value":' + value + '}')

    def test_duplicate_yaml_family_definition_is_rejected(self):
        path = self.root / 'sources/institutes/families-2t.yaml'
        path.write_text(path.read_text() + '\n  ibope_ipec:\n    aliases: [SomethingElse]\n    basis: synthetic\n')
        with self.assertRaisesRegex(DataError, 'duplicate'): families(Audit(self.root))

    def test_absolute_or_noncanonical_evidence_paths_are_rejected(self):
        for name in (str(self.root / self.ref['path']), 'data/../data/raw/synthetic-evidence.txt', './data/raw/synthetic-evidence.txt'):
            with self.assertRaises(DataError): Audit(self.root).track(name)

    def test_family_evidence_after_deadline_is_rejected(self):
        ref = dict(self.ref, retrieved_at=DEADLINE.isoformat())
        with self.assertRaisesRegex(DataError, 'deadline'): Audit(self.root).sources([ref])

    def test_any_source_in_future_blocks_freeze_clock_gate(self):
        with self.assertRaisesRegex(DataError, 'future'):
            flow.time_gate(dict(coverage_as_of=CUTOFF.isoformat(), latest_source_at='2026-10-25T14:00:00-03:00'),
                           datetime.fromisoformat('2026-10-25T13:00:00-03:00'))

    def test_publication_calendar_is_brasilia_even_when_timestamp_is_utc(self):
        for poll, row in zip(self.polls, self.inventory['rows']):
            poll['published_at'] = row['published_at'] = '2026-10-24T01:00:00+00:00'
        self.write('data/canonical/prospective-2t-inventory.json', self.inventory)
        self.p['coverage']['inventory_sha256'] = sha(self.root / 'data/canonical/prospective-2t-inventory.json')
        with self.assertRaisesRegex(DataError, 'before end'): self.load()


class AcquisitionTests(unittest.TestCase):
    def test_immutable_idempotent_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); original = root / 'input'; original.write_bytes(b'original bytes')
            a = preserve(root, original, 'https://example.org/source', 'publication', 'p1')
            self.assertEqual(a, preserve(root, original, 'https://example.org/source', 'publication', 'p1'))
            original.write_bytes(b'new source version')
            b = preserve(root, original, 'https://example.org/source', 'publication', 'p1')
            self.assertNotEqual(a['path'], b['path'])
            self.assertEqual((root / a['path']).read_bytes(), b'original bytes')
            with self.assertRaises(DataError): preserve(root, original, 'https://example.org/source', 'outcome', 'p1')


if __name__ == '__main__':
    unittest.main()
