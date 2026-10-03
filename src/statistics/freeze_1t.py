"""Build an auditable PRE_FREEZE report. Fail closed; never creates a Git tag.

Run offline: python -m src.statistics.freeze_1t --root .
--check verifies committed outputs rather than silently regenerating them.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

import yaml

from src.ingestion.tse import normalize
from src.statistics.cofre_a import DataError, aggregate, calibrate, intervals

PREREG = 'methodology/preregistration/0001-cofre-A-2026.md'
PREREG_COMMIT = 'c377991a9dd645ec77df903179b0b44f4b54bfc7'
PREREG_HASH = 'b5757670a716af3f297808d5ef33c47f242bcbfa09918085ff138924a88aade1'
MANIFEST = 'methodology/preregistration/0001-freeze-manifest.md'
OUTPUT = 'data/derived/cofre-a-1t-2026.json'
CUTOFF = datetime.fromisoformat('2026-10-04T12:00:00-03:00')
DEADLINE = datetime.fromisoformat('2026-10-04T17:00:00-03:00')
HISTORICAL_DATES = {2014: ('2014-10-05', '2014-10-26'),
                    2018: ('2018-10-07', '2018-10-28'),
                    2022: ('2022-10-02', '2022-10-30')}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(root: Path, name: str) -> Path:
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise DataError('source path escapes repository')
    return path


def evidence(root: Path, references: list[dict]) -> None:
    if not references:
        raise DataError('missing raw provenance')
    for ref in references:
        path = resolve(root, ref['path'])
        if not ref['path'].startswith('data/raw/') or sha(path) != ref['sha256']:
            raise DataError('raw provenance/hash mismatch')
        if not ref.get('url') or not ref.get('retrieved_at') or not ref.get('location'):
            raise DataError('source URL, retrieval timestamp and location required')
        if datetime.fromisoformat(ref['retrieved_at']).tzinfo is None:
            raise DataError('retrieval timestamp needs timezone')


def family_map(root: Path) -> dict[str, str]:
    table = yaml.safe_load((root / 'sources/institutes/families.yaml').read_text())
    mapping = {}
    for family, row in table['families'].items():
        for alias in row['aliases']:
            if alias in mapping:
                raise DataError('duplicate family alias')
            mapping[alias] = family
    return mapping


def load_packet(root: Path, path: str, year: int, turn: int, families: dict) -> tuple[dict, dict]:
    packet = json.loads(resolve(root, path).read_text())
    if packet['year'] != year or packet['turn'] != turn:
        raise DataError('packet year/turn mismatch')
    if year == 2026 and any(k in packet for k in ('R', 'results', 'outcomes', 'official_results')):
        raise DataError('2026 packet may contain inputs only, no outcome')
    evidence(root, packet['official_candidates']['sources'])
    candidates = packet['official_candidates']['names']
    polls = packet['polls']
    for poll in polls:
        evidence(root, poll['sources'])
        if not poll.get('mode'):
            raise DataError('poll mode missing')
        for scenario in poll['scenarios']:
            if not scenario.get('original_values') or not scenario.get('original_denominator'):
                raise DataError('original poll values/denominator required')
    coverage = packet['coverage']
    evidence(root, coverage['sources'])
    if coverage.get('complete') is not True or not coverage.get('reviewer') or not coverage.get('method'):
        raise DataError('complete inventory attestation with method/reviewer required')
    if len(coverage['inventory_poll_ids']) != len(set(coverage['inventory_poll_ids'])):
        raise DataError('duplicate inventory poll_id')
    accounted = [p['poll_id'] for p in polls] + [p['poll_id'] for p in coverage['not_published']]
    if len(accounted) != len(set(accounted)) or set(accounted) != set(coverage['inventory_poll_ids']):
        raise DataError('unaccounted/duplicate poll in coverage inventory')
    for missing in coverage['not_published']:
        if missing['reason'] not in ('NOT_FOUND', 'NOT_PUBLISHED') or not missing.get('detail'):
            raise DataError('invalid typed inventory exclusion')
        evidence(root, missing['sources'])
    election = date(2026, 10, 4) if year == 2026 else date.fromisoformat(HISTORICAL_DATES[year][turn-1])
    cutoff = CUTOFF if year == 2026 else datetime.fromisoformat(election.isoformat() + 'T12:00:00-03:00')
    result = aggregate(polls, candidates, election, cutoff, turn, families)
    result['inventory_exclusions'] = coverage['not_published']
    return result, packet


def historical(root: Path, ledger: list[dict], families: dict) -> dict:
    rows = []
    for entry in ledger:
        row = dict(entry)
        if entry['collection_complete'] is True:
            row['turns'] = {}
            for turn in (1, 2):
                aggregated, packet = load_packet(root, entry['packets'][str(turn)], entry['year'], turn, families)
                official = normalize(resolve(root, entry['tse_manifest']), root)
                aliases = packet['official_candidates']['tse_ids']
                if set(aliases) != set(packet['official_candidates']['names']):
                    raise DataError('official candidate alias map incomplete')
                observed = {r['candidate_id']: r for r in official['rows'] if r['turn'] == turn}
                if set(aliases.values()) != set(observed):
                    raise DataError('official TSE candidates incomplete')
                for name, candidate_id in aliases.items():
                    if name.casefold() != observed[candidate_id]['name_original'].casefold():
                        raise DataError('candidate alias requires explicit reviewed normalization')
                row['turns'][str(turn)] = {'aggregate': aggregated,
                                         'R': {name: observed[cid]['R'] for name, cid in aliases.items()}}
        rows.append(row)
    return calibrate(rows)


def build(root: Path) -> dict:
    if sha(root / PREREG) != PREREG_HASH:
        raise DataError('original prereg modified; cannot freeze')
    families = family_map(root)
    ledger = json.loads((root / 'data/canonical/historical-coverage.json').read_text())
    calibration = historical(root, ledger, families)
    # Verify every acquired historical raw file even when excluded from calibration.
    for manifest in sorted((root / 'data/raw/tse').glob('*.manifest.json')):
        normalized = normalize(manifest, root)
        canonical = root / f"data/canonical/tse-results-{normalized['year']}.json"
        if json.loads(canonical.read_text()) != normalized:
            raise DataError('canonical TSE results differ from reproducible raw normalization')
    from src.ingestion.pesqele import normalize as normalize_inventory
    for manifest in sorted((root / 'data/raw/pesqele').glob('*.manifest.json')):
        inventory = normalize_inventory(manifest, root)
        canonical = root / f"data/canonical/pesqele-inventory-{inventory['year']}.json"
        if json.loads(canonical.read_text()) != inventory:
            raise DataError('PesqEle inventory differs from reproducible raw normalization')
    prospective = json.loads((root / 'data/canonical/prospective-1t-status.json').read_text())
    blockers = []
    if calibration['status'] != 'READY':
        blockers.append('No complete historical calibration with numeric reference, q90 and sample SD')
    output = {'status': 'INPUTS_INCOMPLETE', 'P': None, 'intervals': None,
              'families': [], 'poll_ids': [], 'excluded': [], 'c_star': None, 'adv': None}
    if prospective.get('collection_complete') is True:
        aggregated, packet = load_packet(root, prospective['packet'], 2026, 1, families)
        # Provenance for the PL candidacy and public Bolsonaro endorsement is separate.
        target = packet['target']
        evidence(root, target['sources'])
        if target['party'] != 'PL' or target['endorser'] != 'Jair Bolsonaro' or target['name'] not in packet['official_candidates']['names']:
            raise DataError('target does not satisfy prereg §4.3')
        output = dict(aggregated, c_star=target['name'], adv=None, intervals=None)
        late_ids = {p['poll_id'] for p in prospective.get('late_discovery', [])}
        if late_ids & {p['poll_id'] for p in packet['polls']}:
            raise DataError('late-discovered poll cannot enter frozen input set')
        if aggregated['P'] is not None:
            others = {c: p for c, p in aggregated['P'].items() if c != target['name']}
            winners = [c for c, p in others.items() if p == max(others.values())]
            if len(winners) != 1:
                raise DataError('adversary tie not resolved by prereg')
            output['adv'] = winners[0]
            if calibration['status'] == 'READY':
                output['intervals'] = intervals(aggregated['P'], calibration)
    else:
        blockers.append(prospective['reason'])
    # Even NÃO_ESTIMÁVEL still needs complete manifest of eligible/excluded inputs.
    hashes = {}
    for folder in ('src', 'tests', 'sources', 'data/raw', 'data/canonical', 'methodology/model_specifications', 'docs', '.github'):
        for path in sorted((root / folder).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                hashes[path.relative_to(root).as_posix()] = sha(path)
    for name in ('PROMPT.md', 'AGENTS.md', PREREG, 'requirements.txt', '.gitignore'):
        hashes[name] = sha(root / name)
    return {'status': 'READY_FOR_FREEZE' if not blockers else 'BLOCKED',
            'prereg_commit': PREREG_COMMIT, 'prereg_sha256': PREREG_HASH,
            'classification': 'CONFIRMATORY_PROSPECTIVE preparation; historical calibration CONFIRMATORY_RETROSPECTIVE',
            'publication_cutoff': CUTOFF.isoformat(), 'freeze_deadline': DEADLINE.isoformat(),
            'calibration': calibration, 'output_1T': output, 'blockers': blockers,
            'artifact_sha256': hashes, 'late_discovery': prospective.get('late_discovery', []),
            'outcomes_2026_consulted': False}


def markdown(result: dict) -> str:
    c = result['calibration']
    fields = [('ê_ref(1T)', c['e_ref_1T']), ('q90', c['q90']), ('σ̂', c['sigma_hat']), ('|E_hist|', c['E_hist_size'])]
    display = lambda value: 'INDISPONÍVEL (null; não imputado)' if value is None else str(value)
    return ('# PREREG-0001 — Manifesto de preparação do freeze 1T\n\n'
            f"**Status: {result['status']} — nenhuma tag criada por este programa.**\n\n"
            'Este manifesto documenta o estado disponível; BLOCKED não é freeze nem previsão congelada.\n\n'
            f"Prereg original: `{PREREG_COMMIT}`; SHA-256 `{PREREG_HASH}`. Texto preservado integralmente.\n\n"
            '| Parâmetro | Valor |\n|---|---|\n' + ''.join(f'| {name} | {display(value)} |\n' for name, value in fields) + '\n'
            f"Anos incluídos: {c['included_years']}. Q2: {c['q2_status']} (indisponibilidade não equivale a VAZIA).\n\n"
            + ''.join(f"- {y['year']}: **{y['reason']}** — {y['detail']}\n" for y in c['excluded_years']) + '\n'
            f"c*: {display(result['output_1T']['c_star'])}; adv: {display(result['output_1T']['adv'])}.\n\n"
            f"Saída 1T: {result['output_1T']['status']}. P e intervalos constam em `{OUTPUT}`; nenhum número fictício.\n\n"
            '## Bloqueios\n\n' + (''.join(f'- {b}\n' for b in result['blockers']) or '- Nenhum bloqueio de dados detectado; conferir testes e prazo antes da tag.\n') + '\n'
            '## Integridade e reprodução\n\n'
            f"Hashes de PROMPT, AGENTS, código, testes, model spec, fontes, raw e canonical: `{OUTPUT}`.\n\n"
            'Quantil: interpolação linear tipo 7; σ̂: desvio-padrão amostral, ddof=1. Sem clipping de logit. '
            'Sensibilidades reservadas ao pós-urna; grau A não reivindicado.\n\n'
            'Cutoff: 04/10/2026 12:00 BRT. Manifesto de inputs e tag antes de 04/10/2026 17:00 BRT, '
            'sem acesso à totalização. Descoberta posterior ao manifesto entra somente em late_discovery.\n\n'
            'Execute `python -m unittest discover -s tests -v` e `python -m src.statistics.freeze_1t --check`. '
            'A verificação retorna erro enquanto houver bloqueios. Nenhum desfecho de 2026 foi adquirido.\n')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = build(args.root)
    serialized = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n'
    report = markdown(result)
    if args.check:
        if (args.root / OUTPUT).read_text() != serialized or (args.root / MANIFEST).read_text() != report:
            raise SystemExit('FAIL: stale or altered freeze artifacts')
        if result['status'] != 'READY_FOR_FREEZE':
            raise SystemExit('BLOCKED: ' + '; '.join(result['blockers']))
        if datetime.now(timezone.utc) >= DEADLINE:
            raise SystemExit('FAIL: prospective freeze deadline elapsed')
        if subprocess.run(['git', 'diff', '--quiet'], cwd=args.root).returncode:
            raise SystemExit('FAIL: uncommitted tracked changes')
        if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=args.root).returncode:
            raise SystemExit('FAIL: staged changes not committed')
        if subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=args.root).strip():
            raise SystemExit('FAIL: untracked files')
        print('READY: artifacts reproduced; create tag on this exact tested commit, never move it')
    else:
        (args.root / OUTPUT).parent.mkdir(parents=True, exist_ok=True)
        (args.root / OUTPUT).write_text(serialized)
        (args.root / MANIFEST).write_text(report)
        print(result['status'])


if __name__ == '__main__':
    main()
