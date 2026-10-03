"""PREREG-0001, unchanged. Offline estimator; never acquires outcomes.

Inputs are fractions (not percentages). An unresolved scenario tie or a
missing candidate is an error, not permission to impute zero. Quantiles use
linear interpolation (Hyndman–Fan type 7); sample SD uses ddof=1.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
import math
import re
import statistics
from typing import Any


class DataError(ValueError):
    """Invalid or ambiguous evidence; stop instead of repairing silently."""


def logit(p: float) -> float:
    if not math.isfinite(p) or not 0 < p < 1:
        raise DataError("logit requires a finite share strictly between 0 and 1")
    return math.log(p / (1 - p))


def expit(x: float) -> float:
    return 1 / (1 + math.exp(-x)) if x >= 0 else math.exp(x) / (1 + math.exp(x))


def shares(values: dict[str, float], *, composition: bool = False) -> None:
    if not values or any(isinstance(v, bool) or not isinstance(v, (int, float))
                         or not math.isfinite(v) or not 0 <= v <= 1
                         for v in values.values()):
        raise DataError("missing, non-finite or out-of-range shares")
    if composition and abs(sum(values.values()) - 1) > 0.015:
        raise DataError("published valid shares do not sum to 1 within rounding tolerance")


def scenario(poll: dict[str, Any], official: list[str], turn: int) -> dict[str, Any] | None:
    eligible = [s for s in poll['scenarios'] if s['stimulated'] is True
                and (turn == 1 or set(s['candidates']) == set(official))]
    if not eligible:
        return None
    score = lambda s: (len(set(s['candidates']) & set(official)), len(s['candidates']))
    best = max(map(score, eligible))
    winners = [s for s in eligible if score(s) == best]
    if best[0] == 0:
        return None
    if len(winners) != 1:
        raise DataError("scenario tie unresolved by prereg §4.2")
    return winners[0]


def convert(s: dict[str, Any], official: list[str]) -> tuple[dict[str, float] | None, list[str], str]:
    candidates = s['candidates']
    if len(candidates) != len(set(candidates)):
        raise DataError("duplicate scenario candidates")
    kept = [c for c in candidates if c in official]
    flags = ['SCENARIO_TRIMMED'] if len(kept) != len(candidates) else []
    if set(kept) != set(official):
        raise DataError("official candidate absent from selected scenario; no zero imputation")
    published, totals = s.get('valid'), s.get('total')
    converted = None
    if totals is not None:
        shares(totals)
        if set(totals) != set(candidates) or sum(totals.values()) > 1.015:
            raise DataError("total candidate vector invalid")
        denominator = sum(totals[c] for c in kept)
        if denominator <= 0:
            raise DataError("zero valid denominator")
        converted = {c: totals[c] / denominator for c in kept}
    if published is not None:
        shares(published, composition=True)
        if set(published) != set(candidates):
            raise DataError("published vector incomplete")
        p = {c: published[c] for c in kept}
        shares(p, composition=True)
        if converted and any(abs(p[c] - converted[c]) > 0.005 + 1e-12 for c in kept):
            flags.append('DENOMINATOR_MISMATCH')
        return p, flags, 'DADO_OBSERVADO'
    return converted, flags, 'totais_to_validos_v1' if converted else 'NOT_PUBLISHED'


def registration_key(registration: str) -> int:
    match = re.fullmatch(r'BR-(\d+)/(\d{4})', registration)
    if not match:
        raise DataError("invalid national PesqEle registration")
    return int(match[1])


def aggregate(polls: list[dict[str, Any]], official: list[str], election: date,
              cutoff: datetime, turn: int, families: dict[str, str]) -> dict[str, Any]:
    if cutoff.tzinfo is None or len(official) != len(set(official)) or not official:
        raise DataError("timezone or official candidacy list invalid")
    if turn not in (1, 2) or (turn == 2 and len(official) != 2):
        raise DataError("invalid turn")
    seen, eligible, excluded = set(), [], []
    for p in polls:
        pid = p['poll_id']
        if pid in seen:
            raise DataError("duplicate poll_id")
        seen.add(pid)
        if p['year'] != election.year or p['turn'] != turn:
            raise DataError("mixed election/turn inputs")
        if not isinstance(p['exit_poll'], bool) or not isinstance(p['institute'], str) or not p['institute'].strip():
            raise DataError("exit_poll must be boolean and institute must be identified")
        if any(not isinstance(s['stimulated'], bool) for s in p['scenarios']):
            raise DataError("stimulated must be boolean")
        start, end = date.fromisoformat(p['fieldwork_start']), date.fromisoformat(p['fieldwork_end'])
        publication = datetime.fromisoformat(p['published_at'])
        if publication.tzinfo is None or not start <= end <= election:
            raise DataError("invalid fieldwork/publication dates")
        reason = None
        if p['office'] != 'Presidente' or p['scope'] != 'Brasil' or p['exit_poll']:
            reason = 'NOT_APPLICABLE'
        elif not p.get('registration'):
            reason = 'NOT_FOUND'
        elif not election - timedelta(days=14) <= end <= election - timedelta(days=1) or publication > cutoff:
            reason = 'OUTSIDE_CUTOFF'
        else:
            registration_key(p['registration'])
            if int(p['registration'].split('/')[-1]) != election.year:
                raise DataError("registration year mismatch")
            s = scenario(p, official, turn)
            if s is None:
                reason = 'NOT_PUBLISHED'
            else:
                values, flags, transform = convert(s, official)
                if values is None:
                    reason = 'NOT_PUBLISHED'
                else:
                    if not isinstance(p['sample_size'], int) or isinstance(p['sample_size'], bool) or p['sample_size'] <= 0:
                        raise DataError("invalid sample size")
                    family = families.get(p['institute'], 'unmapped:' + p['institute'])
                    if p['institute'] not in families:
                        flags.append('UNMAPPED_FAMILY')
                    eligible.append(dict(p, p=values, flags=flags, transformation=transform,
                                         family=family, selected_scenario=s['scenario_id']))
        if reason:
            excluded.append({'poll_id': pid, 'reason': reason})
    selected = {}
    for p in eligible:
        key = lambda r: (-date.fromisoformat(r['fieldwork_end']).toordinal(),
                         -r['sample_size'], registration_key(r['registration']))
        old = selected.get(p['family'])
        if old is not None and key(p) == key(old):
            raise DataError("duplicate registration or unresolved family tie")
        if old is None or key(p) < key(old):
            selected[p['family']] = p
    selected_rows = [selected[f] for f in sorted(selected)]
    base = {'families': sorted(selected), 'poll_ids': [p['poll_id'] for p in selected_rows],
            'selected': selected_rows, 'excluded': excluded,
            'superseded_poll_ids': sorted(p['poll_id'] for p in eligible if p not in selected_rows)}
    if len(selected) < 3:
        return dict(base, status='NÃO_ESTIMÁVEL', P=None)
    return dict(base, status='ESTIMÁVEL', P={c: statistics.mean(p['p'][c] for p in selected_rows) for c in official})


def quantile90(errors: list[float]) -> float:
    if not errors or any(not math.isfinite(e) for e in errors):
        raise DataError("empty/non-finite error set")
    values = sorted(abs(e) for e in errors)
    index = .9 * (len(values) - 1)
    low = math.floor(index)
    return values[low] + (index - low) * (values[math.ceil(index)] - values[low])


def calibrate(years: list[dict[str, Any]]) -> dict[str, Any]:
    """Include an entire historical year only when collection covers both turns."""
    errors, included, excluded, reference = [], [], [], None
    if sorted(y['year'] for y in years) != [2014, 2018, 2022]:
        raise DataError("historical ledger must account for exactly 2014/2018/2022")
    for y in years:
        if y.get('collection_complete') is not True:
            excluded.append({'year': y['year'], 'reason': 'UNRECOVERABLE', 'detail': y['reason']})
            continue
        if set(y['turns']) != {'1', '2'} or not y.get('coverage_evidence'):
            raise DataError("claimed complete year without both turns and coverage evidence")
        included.append(y['year'])
        for t, payload in y['turns'].items():
            agg, results = payload['aggregate'], payload['R']
            shares(results, composition=True)
            if agg['status'] == 'NÃO_ESTIMÁVEL':
                continue
            if set(results) != set(agg['P']):
                raise DataError("result/poll candidate mismatch")
            for c, p in agg['P'].items():
                if p >= .05:
                    error = logit(results[c]) - logit(p)
                    errors.append({'year': y['year'], 'turn': int(t), 'candidate': c, 'e_logit': error})
                    if y['year'] == 2022 and t == '1' and c == 'Jair Bolsonaro':
                        reference = error
    e = [row['e_logit'] for row in errors]
    ready = len(e) >= 2 and reference is not None
    return {'status': 'READY' if ready else 'BLOCKED', 'included_years': included,
            'excluded_years': excluded, 'E_hist': errors, 'E_hist_size': len(e),
            'e_ref_1T': reference, 'q90': quantile90(e) if e else None,
            'sigma_hat': statistics.stdev(e) if len(e) >= 2 else None,
            'q2_status': 'UNAVAILABLE' if reference is None else ('VAZIA' if reference <= 0 else 'PENDING_OUTCOME'),
            'quantile_method': 'Hyndman-Fan type 7 (linear)', 'sd_ddof': 1}


def intervals(p: dict[str, float], calibration: dict[str, Any]) -> dict[str, Any]:
    if calibration['status'] != 'READY':
        raise DataError("calibration unavailable; no synthetic uncertainty")
    out = {}
    for c, value in p.items():
        if value < .05:
            out[c] = {'status': 'NOT_APPLICABLE'}
        else:
            center = logit(value)
            q, sd = calibration['q90'], calibration['sigma_hat']
            out[c] = {'empirical_90': [expit(center-q), expit(center+q)],
                      'parametric_comparison': [expit(center-1.645*sd), expit(center+1.645*sd)]}
    return out
