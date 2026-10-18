"""PREREG-0001 second-round preparation. No 1T output is regenerated.

Preparation is reproducible and may remain BLOCKED. --check additionally checks
real time and Git state. --freeze rechecks after tests and creates a local,
annotated, never-replaced reference; publication is a separate Git push.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from src.statistics.cofre_a import DataError, intervals
from src.statistics.freeze_1t import PREREG, PREREG_HASH, PREREG_COMMIT, historical, sha
from src.validation.prospective import (Audit, CUTOFF, DEADLINE, ELECTION, FAMILIES,
                                        FAMILY_REVIEW, families, family_review, packet, timestamp)

BASE = 'd92008b5bae107c0c380209931c31f07a911cba4'
STATUS = 'data/canonical/prospective-2t-status.json'
LEDGER = 'data/canonical/historical-coverage-2t.json'
OUTPUT = 'data/derived/cofre-a-2t-2026.json'
MANIFEST = 'methodology/preregistration/0001-freeze-manifest-2t.md'
TAG = 'pre-election-freeze-2026-2t'
PROTECTED = ('PROMPT.md', 'AGENTS.md', PREREG, 'src/statistics/cofre_a.py',
             'src/statistics/freeze_1t.py', 'sources/institutes/families.yaml',
             'data/canonical/historical-coverage.json', 'data/canonical/prospective-1t-status.json',
             'data/derived/cofre-a-1t-2026.json', 'methodology/preregistration/0001-freeze-manifest.md',
             'methodology/model_specifications/cofre-a-1t-v1.md', 'docs/cofre-a-freeze.md')


def serialized(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n'


def historical_2t(audit: Audit, mapping: dict) -> tuple[dict, set[str]]:
    ledger = audit.read(LEDGER)
    used = set()
    for entry in ledger:
        if not isinstance(entry.get('collection_complete'), bool):
            raise DataError('historical completeness must be an explicit boolean')
        if not entry['collection_complete']:
            if not entry.get('reason'):
                raise DataError('incomplete historical year needs an exclusion reason')
            continue
        # The prior loader reproduces both turns from raw TSE. Register every
        # dependency here as well; hashing only the packet would omit its evidence.
        audit.sources(entry['coverage_evidence'])
        manifest = audit.read(entry['tse_manifest'])
        audit.track(manifest['path'])
        for turn in ('1', '2'):
            p = audit.read(entry['packets'][turn])
            audit.sources(p['official_candidates']['sources'])
            audit.sources(p['coverage']['sources'])
            for row in p['polls']:
                used.add(row['institute'])
                audit.sources(row['sources'])
                for scenario in row['scenarios']:
                    audit.sources(scenario['sources'])
            for row in p['coverage']['not_published']:
                audit.sources(row['sources'])
    c = historical(audit.root, ledger, mapping)
    refs = [r['e_logit'] for r in c['E_hist']
            if r['year'] == 2022 and r['turn'] == 2 and r['candidate'] == 'Jair Bolsonaro']
    if len(refs) > 1:
        raise DataError('ambiguous second-round historical reference')
    ref = refs[0] if refs else None
    # Same E_hist, q90, sample SD and formula; only the Q2 reference is turn-specific.
    c['e_ref_2T'] = ref
    c['status'] = 'READY' if c['E_hist_size'] >= 2 and ref is not None else 'BLOCKED'
    c['q2_status'] = 'UNAVAILABLE' if ref is None else ('VAZIA' if ref <= 0 else 'PENDING_OUTCOME')
    return c, used


def build(root: Path) -> dict:
    audit = Audit(root)
    if sha(audit.track(PREREG)) != PREREG_HASH:
        raise DataError('original prereg modified; cannot prepare/freeze')
    mapping = families(audit)
    calibration, used = historical_2t(audit, mapping)
    status = audit.read(STATUS)
    if status.get('year') != 2026 or status.get('turn') != 2 or not isinstance(status.get('collection_complete'), bool):
        raise DataError('invalid second-round collection status')
    if status.get('inventory'):
        from src.validation.prospective import reject_outcomes
        reject_outcomes(audit.read(status['inventory']))
    blockers = []
    if calibration['status'] != 'READY':
        blockers.append('HISTORICAL_CALIBRATION_INCOMPLETE: numeric ê_ref(2T), q90 and sample SD required')
    output = dict(status='INPUTS_INCOMPLETE', P=None, intervals=None, families=[],
                  poll_ids=[], excluded=[], c_star=None, adv=None)
    inputs = dict(packet=None, inventory=None, inventory_poll_ids=[], poll_ids=[], raw_sha256={})
    coverage_as_of = None
    if status['collection_complete']:
        output, p = packet(audit, status['packet'], status['inventory'], mapping)
        coverage_as_of = p['coverage']['as_of']
        used.update(row['institute'] for row in p['polls'])
        inputs.update(packet=status['packet'], inventory=status['inventory'],
                      inventory_poll_ids=sorted(p['coverage']['inventory_poll_ids']),
                      poll_ids=sorted(row['poll_id'] for row in p['polls']))
        if output['P'] is not None and calibration['status'] == 'READY':
            output['intervals'] = intervals(output['P'], calibration)
    else:
        blockers.append('PROSPECTIVE_COLLECTION_INCOMPLETE: ' + status['reason'])
    review = audit.read(FAMILY_REVIEW)
    if review.get('complete') is not True:
        blockers.append('FAMILY_PROVENANCE_INCOMPLETE: legal identities and continuity await source review')
    else:
        family_review(audit, mapping, used)
    late = status.get('late_discovery', [])
    late_ids = [row['poll_id'] for row in late]
    if len(late_ids) != len(set(late_ids)) or set(late_ids) & set(inputs['inventory_poll_ids']):
        raise DataError('late discovery duplicates or contaminates sealed inventory')
    for row in late:
        if not row.get('reason') or not row.get('discovered_at'):
            raise DataError('late discovery requires reason and timestamp')
        timestamp(row['discovered_at'])
        audit.sources(row['sources'])
    # Dependency closure: excluded historical raw files are not model inputs.
    # Their acquisition manifests remain on the original branch and are tested
    # there. Never imply they were re-audited or consumed by this second-round run.
    for directory in ('src', 'tests'):
        for path in sorted((audit.root / directory).rglob('*.py')):
            audit.track(path.relative_to(audit.root).as_posix())
    for name in (*PROTECTED, 'requirements.txt', '.gitignore', '.github/workflows/cofre-a.yml',
                 'docs/cofre-a-freeze-2t.md', 'methodology/model_specifications/cofre-a-2t-v1.md'):
        audit.track(name)
    inputs['raw_sha256'] = {k: v for k, v in sorted(audit.hashes.items()) if k.startswith('data/raw/')}
    return dict(status='BLOCKED' if blockers else 'READY_FOR_FREEZE', turn=2,
                stage='PREPARATION_NOT_FROZEN', prereg_commit=PREREG_COMMIT, prereg_sha256=PREREG_HASH,
                baseline_1t_commit=BASE, intended_reference=TAG,
                classification='CONFIRMATORY_PROSPECTIVE preparation; historical calibration CONFIRMATORY_RETROSPECTIVE',
                election_date=ELECTION.isoformat(), fieldwork_window=['2026-10-11', '2026-10-24'],
                publication_cutoff=CUTOFF.isoformat(), freeze_deadline=DEADLINE.isoformat(),
                coverage_as_of=coverage_as_of, calibration=calibration, output_2T=output,
                blockers=blockers, inputs=inputs, artifact_sha256=dict(sorted(audit.hashes.items())),
                late_discovery=late,
                outcome_policy='2026 outcomes are forbidden; source-content fidelity requires human audit',
                limitation='No calibrated forecast or completed coverage is asserted by a BLOCKED preparation')


def markdown(r: dict) -> str:
    c = r['calibration']
    value = lambda x: 'INDISPONÍVEL (null; não imputado)' if x is None else str(x)
    lines = ['# PREREG-0001 — Manifesto de preparação do 2T', '',
             f"**{r['status']} — preparação; não é um congelamento.**", '',
             f'Prereg original: `{PREREG_COMMIT}`; SHA-256 `{PREREG_HASH}`.',
             f'Base preservada do 1T: `{BASE}`. Este documento pertence a um commit separado.', '',
             '| Parâmetro | Valor |', '|---|---|']
    for label, key in [('ê_ref(2T)', 'e_ref_2T'), ('q90', 'q90'), ('σ̂', 'sigma_hat'), ('|E_hist|', 'E_hist_size')]:
        lines.append(f'| {label} | {value(c[key])} |')
    lines += ['', f"Anos incluídos: {c['included_years']}. Q2: {c['q2_status']}.", '']
    lines += [f"- {row['year']}: {row['reason']} — {row['detail']}" for row in c['excluded_years']]
    lines += ['', f"Saída: {r['output_2T']['status']}; c*: {value(r['output_2T']['c_star'])}; adv: {value(r['output_2T']['adv'])}.",
              f'P, intervalos, famílias, poll_ids, exclusões e hashes: `{OUTPUT}`.', '',
              '## Bloqueios', '']
    lines += ['- ' + b for b in r['blockers']] or ['- Nenhum bloqueio de dados; ainda verificar prazo, testes e commit limpo.']
    lines += ['', 'Campo: 11–24/10/2026. Publicação: até 25/10/2026 12:00 BRT, inclusive.',
              'Fechamento de cobertura após esse cutoff; manifesto/commit/tag estritamente antes de 17:00 BRT.',
              f'Referência exclusiva do 2T: `{TAG}`; a tag de 1T nunca é criada retroativamente nem movida.', '',
              'Amostra histórica dos dois turnos; anos incompletos inteiros excluídos. Quantil tipo 7, SD ddof=1.',
              'NÃO_ESTIMÁVEL exige coleta completa e menos de três famílias; não significa dados ausentes.',
              'Sensibilidades somente após a urna. Grau A não é reivindicado. Evidência de cobertura exige auditoria humana.', '',
              'Reprodução: `python -m src.statistics.freeze_2t --verify-artifacts`.',
              'Autorização local: `python -m src.statistics.freeze_2t --check` (falha enquanto BLOCKED).', '']
    return '\n'.join(lines)


def verify_artifacts(root: Path, result: dict) -> None:
    if (root / OUTPUT).read_text() != serialized(result) or (root / MANIFEST).read_text() != markdown(result):
        raise DataError('stale or altered 2T artifacts')


def time_gate(result: dict, now: datetime) -> None:
    if now.tzinfo is None:
        raise DataError('real clock requires timezone')
    if not CUTOFF <= now < DEADLINE:
        raise DataError('outside freeze interval: publication cutoff <= now < 17:00 BRT deadline')
    if not result['coverage_as_of'] or timestamp(result['coverage_as_of']) > now:
        raise DataError('coverage attestation is missing or in the future')


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def check(root: Path) -> tuple[dict, str]:
    result = build(root)
    verify_artifacts(root, result)
    if result['status'] != 'READY_FOR_FREEZE':
        raise DataError('BLOCKED: ' + '; '.join(result['blockers']))
    time_gate(result, datetime.now(timezone.utc))
    if git(root, 'status', '--porcelain', '--untracked-files=all'):
        raise DataError('freeze requires a clean, fully committed working tree')
    head = git(root, 'rev-parse', 'HEAD')
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, head], cwd=root, check=True)
    if git(root, 'diff', '--name-only', BASE, head, '--', *PROTECTED):
        raise DataError('protected 1T/prereg artifacts changed since baseline')
    # A preparation committed earlier is not a final input seal. Its final commit
    # must itself be after the publication cutoff and before the prereg deadline.
    for name in (MANIFEST, OUTPUT):
        committed = timestamp(git(root, 'log', '-1', '--format=%cI', '--', name))
        if not CUTOFF <= committed < DEADLINE:
            raise DataError('final 2T manifest/output commit outside permitted interval')
    for name in result['artifact_sha256']:
        subprocess.run(['git', 'ls-files', '--error-unmatch', '--', name], cwd=root,
                       check=True, stdout=subprocess.DEVNULL)
    return result, head


def freeze(root: Path) -> None:
    _, head = check(root)
    if git(root, 'tag', '--list', TAG):
        raise DataError('immutable 2T reference already exists; never overwrite')
    # A freeze never trusts a manually asserted tests_passed flag.
    subprocess.run(['python', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=root, check=True)
    result, checked_head = check(root)
    if head != checked_head:
        raise DataError('HEAD changed during tests')
    note = serialized(dict(status='FROZEN_2T', commit=head, sealed_at=datetime.now(timezone.utc).isoformat(),
                           manifest_sha256=sha(root / MANIFEST), output_sha256=sha(root / OUTPUT),
                           prereg_sha256=PREREG_HASH, inputs=result['inputs']))
    # No force option and no implicit network publication. Check the clock again
    # immediately before the only reference-creation operation.
    time_gate(result, datetime.now(timezone.utc))
    subprocess.run(['git', 'tag', '-a', TAG, head, '-m', note], cwd=root, check=True)
    print(f'Created local annotated {TAG} at {head}; never replace it')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--verify-artifacts', action='store_true')
    group.add_argument('--check', action='store_true')
    group.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.freeze:
            freeze(root)
        elif args.check:
            check(root)
            print('READY: structural checks passed; --freeze reruns tests and deadline checks')
        else:
            result = build(root)
            if args.verify_artifacts:
                verify_artifacts(root, result)
            else:
                # Do not regenerate a sealed set even if late discoveries exist.
                if (root / '.git').exists() and git(root, 'tag', '--list', TAG):
                    raise DataError('2T reference exists; sealed artifacts cannot be regenerated')
                (root / OUTPUT).parent.mkdir(parents=True, exist_ok=True)
                (root / OUTPUT).write_text(serialized(result), encoding='utf-8')
                (root / MANIFEST).write_text(markdown(result), encoding='utf-8')
            print(result['status'])
    except (DataError, KeyError, OSError, ValueError, TypeError, subprocess.CalledProcessError) as exc:
        raise SystemExit('BLOCKED: ' + str(exc)) from exc


if __name__ == '__main__':
    main()
