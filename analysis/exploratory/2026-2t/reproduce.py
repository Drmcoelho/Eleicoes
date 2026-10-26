"""Reproduce one acquired official 2T snapshot; never produce a forecast.

Standard library only. No network, clock substitution, Git writes or old Cofre A
imports. Every input is addressed by a source manifest and verified SHA-256.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"Non-finite JSON number: {value}")


def read_json(raw: bytes):
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid_constant)


def integer(value: str) -> int:
    require(isinstance(value, str) and value.isascii() and value.isdigit(),
            f"Expected a non-negative integer string: {value!r}")
    return int(value)


def normalize(d: dict, source: dict) -> dict:
    require(all(d[k] == v for k, v in {
        'ele': '6258', 't': '2', 'f': 'o', 'sup': 'n',
        'tpabr': 'br', 'cdabr': 'br', 'tf': 's', 'and': 'f', 'dv': 's',
    }.items()), 'Wrong election, round, scope, simulation or incomplete snapshot')
    require(len(d['carg']) == 1 and d['carg'][0]['cd'] == '1', 'Not the presidential cargo')
    require(integer(d['s']['st']) == integer(d['s']['ts']) and integer(d['s']['snt']) == 0,
            'Not all sections totalized')
    v = {k: integer(d['v'][k]) for k in ('tv', 'vvc', 'vv', 'vnom', 'van', 'vansj', 'vb', 'tvn', 'vn', 'vnt', 'vscv')}
    require(v['vv'] > 0 and v['vv'] == v['vnom'], 'Invalid nominal denominator')
    require(v['vvc'] == v['vv'] + v['van'] + v['vansj'], 'Votable votes do not reconcile')
    require(v['tvn'] == v['vn'] + v['vnt'], 'Null votes do not reconcile')
    require(v['tv'] == v['vvc'] + v['vb'] + v['tvn'] + v['vscv'], 'Total votes do not reconcile')
    require(integer(d['e']['c']) == v['tv'], 'Attendance and total votes differ')
    require(integer(d['e']['c']) + integer(d['e']['a']) == integer(d['e']['esi']),
            'Attendance and absence do not reconcile with installed-section electorate')
    # This v1 handles the observed two-valid-candidate snapshot only. Any future
    # judicial destination change needs explicit review, never silent reallocation.
    candidates = []
    for ai, group in enumerate(d['carg'][0]['agr']):
        for pi, party in enumerate(group['par']):
            for ci, c in enumerate(party['cand']):
                require(c['dvt'] == 'Válido', 'Candidate vote destination requires review')
                votes = integer(c['vap'])
                published = Decimal(c['pvapn'].replace(',', '.'))
                require(published.is_finite(), 'Non-finite published percentage')
                # EA20 pvapn uses vvc, not necessarily vv. Use vv for R below.
                require(abs(Decimal(votes) * 100 / Decimal(v['vvc']) - published) <= Decimal('0.000000001'),
                        'Published candidate percentage does not reconcile')
                candidates.append({
                    'tse_id': c['sqcand'], 'ballot_number': c['n'], 'name': c['nm'],
                    'ballot_name': c['nmu'], 'party': party['sg'], 'votes': votes,
                    'vote_destination': c['dvt'], 'official_status': c['st'],
                    'source_pointer': f'/carg/0/agr/{ai}/par/{pi}/cand/{ci}',
                    'published_percent_votable': c['pvapn'],
                    'R_valid_votes_fraction': {'numerator': votes, 'denominator': v['vv']},
                    'R_valid_votes': float(Decimal(votes) / Decimal(v['vv'])),
                })
    require(len(candidates) == 2 and len({c['tse_id'] for c in candidates}) == 2,
            'Two distinct official candidates required')
    require(len({c['ballot_number'] for c in candidates}) == 2, 'Duplicate ballot number')
    require(sum(c['votes'] for c in candidates) == v['vv'], 'Candidate votes do not sum to valid votes')
    return {
        'classification': 'EXPLORATORY_POST_ELECTION',
        'data_class': 'DADO_OFICIAL; R_valid_votes is TRANSFORMAÇÃO',
        'prospective_forecast': False, 'prospective_evaluation': 'NOT_EVALUABLE_NO_VALID_FREEZE',
        'year': 2026, 'turn': 2, 'office': 'Presidente', 'scope': 'Brasil incluindo exterior',
        'denominator': 'v.vv (votos válidos)',
        'source_path': source['path'], 'source_sha256': source['sha256'],
        'source_url': source['acquisition']['source_url'],
        'retrieved_at': source['acquisition']['retrieved_at'],
        'source_generation': {k: d[k] for k in ('dg', 'hg', 'idg', 'dt', 'ht', 'tf', 'and')},
        'sections': {k: d['s'][k] for k in ('ts', 'st', 'snt', 'pstn')},
        'votes': v, 'candidates': sorted(candidates, key=lambda c: c['ballot_number']),
        'P': None, 'intervals': None, 'e_ref_2T': None, 'q90': None, 'sigma_hat': None,
        'Q1': 'NOT_EVALUABLE_NO_VALID_FREEZE', 'Q2': 'NOT_EVALUABLE_NO_VALID_FREEZE',
        'transformation': 'official_6258_valid_votes_v1: integer vap / integer v.vv',
        'limitations': [
            'Versioned snapshot, not a claim that the source can never be revised.',
            'No independent reconciliation with section-level BUs has been performed.',
            'No poll aggregation or candidate-versus-bloc classification is made.',
            '2026 outcomes are already known; subsequent analysis is exploratory.',
        ],
    }


def build() -> dict:
    manifest = read_json((HERE / 'sources.json').read_bytes())
    for source in manifest['sources']:
        path = (ROOT / source['path']).resolve()
        require(path.is_relative_to(HERE / 'raw'), 'Source outside the isolated raw directory')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'], 'Source hash mismatch')
    sources = [s for s in manifest['sources'] if s['name'] == 'tse-result-2t']
    require(len(sources) == 1, 'Exactly one versioned result source required')
    source = sources[0]
    return normalize(read_json((ROOT / source['path']).read_bytes()), source)


def serialized(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare without rewriting')
    args = parser.parse_args()
    text = serialized(build())
    if args.check:
        require((HERE / 'official-outcome.json').read_text() == text, 'Stale normalized snapshot')
        print('OK: hashes, official snapshot scope, reconciliation and deterministic reproduction')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
