"""Audit the input contract; no assertion here can replace source review."""
from __future__ import annotations

from datetime import date, datetime
import json
from pathlib import Path
from urllib.parse import urlparse
import unicodedata

import yaml

from src.statistics.cofre_a import DataError, aggregate
from src.statistics.freeze_1t import evidence, resolve, sha

ELECTION = date(2026, 10, 25)
CUTOFF = datetime.fromisoformat('2026-10-25T12:00:00-03:00')
DEADLINE = datetime.fromisoformat('2026-10-25T17:00:00-03:00')
FAMILIES = 'sources/institutes/families-2t.yaml'
FAMILY_REVIEW = 'sources/institutes/families-2t-review.json'
FORBIDDEN = {'r', 'results', 'outcomes', 'official_results', 'votes',
             'valid_votes_total', 'e_logit', 'winner', 'vote_count'}


def timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise DataError('timezone required')
    return parsed


def reject_outcomes(value) -> None:
    if isinstance(value, dict):
        if any(str(key).casefold() in FORBIDDEN for key in value):
            raise DataError('prospective inputs cannot contain 2026 outcomes')
        for item in value.values():
            reject_outcomes(item)
    elif isinstance(value, list):
        for item in value:
            reject_outcomes(item)


class Audit:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.hashes: dict[str, str] = {}

    def track(self, name: str) -> Path:
        path = resolve(self.root, name)
        current = self.root
        for part in Path(name).parts:
            current = current / part
            if current.is_symlink():
                raise DataError('symlink evidence is not an immutable repository file')
        if not path.is_file():
            raise DataError('evidence must be a repository file')
        self.hashes[name] = sha(path)
        return path

    def read(self, name: str):
        return json.loads(self.track(name).read_text(encoding='utf-8'))

    def sources(self, refs: list[dict], *, latest: datetime | None = None) -> None:
        evidence(self.root, refs)
        for ref in refs:
            self.track(ref['path'])
            if urlparse(ref['url']).scheme not in ('https', 'http'):
                raise DataError('original source URL required')
            if latest is not None and timestamp(ref['retrieved_at']) > latest:
                raise DataError('source retrieved after coverage attestation')


def families(audit: Audit) -> dict[str, str]:
    table = yaml.safe_load(audit.track(FAMILIES).read_text())
    mapping, normalized = {}, {}
    for family, row in table['families'].items():
        if not isinstance(family, str) or not family.strip() or not row.get('basis') or not row.get('aliases'):
            raise DataError('invalid family definition')
        for alias in row['aliases']:
            if not isinstance(alias, str) or not alias.strip() or alias != alias.strip() or alias in mapping:
                raise DataError('empty/duplicate family alias')
            key = unicodedata.normalize('NFKC', alias).casefold()
            if key in normalized and normalized[key] != family:
                raise DataError('conflicting family aliases')
            normalized[key] = family
            mapping[alias] = family
    return mapping


def family_review(audit: Audit, mapping: dict, used: set[str]) -> None:
    review = audit.read(FAMILY_REVIEW)
    if review.get('complete') is not True or not review.get('reviewer'):
        raise DataError('institutional family provenance review incomplete')
    if review.get('table_sha256') != sha(audit.track(FAMILIES)):
        raise DataError('family review refers to a different table')
    for family in {mapping[name] for name in used if name in mapping}:
        row = review['families'].get(family, {})
        if not row.get('basis') or not row.get('legal_identities'):
            raise DataError('family identity/continuity review absent')
        audit.sources(row.get('sources', []))
    # Unknown institutions remain independent with UNMAPPED_FAMILY (§4.4), never
    # excluded for not appearing in the table. Legal identity is retained per poll.


def packet(audit: Audit, path: str, inventory_path: str, mapping: dict) -> tuple[dict, dict]:
    p, inventory = audit.read(path), audit.read(inventory_path)
    reject_outcomes(p)
    reject_outcomes(inventory)
    if (p['year'], p['turn']) != (2026, 2) or (inventory['year'], inventory['turn']) != (2026, 2):
        raise DataError('2T packet/inventory year/turn mismatch')
    if inventory.get('complete') is not True or inventory.get('status') != 'AUDITED':
        raise DataError('inventory has not been audited; empty preparation is not coverage')
    cov = p['coverage']
    if cov.get('complete') is not True or not cov.get('reviewer') or not cov.get('method'):
        raise DataError('coverage attestation missing')
    as_of = timestamp(cov['as_of'])
    if not CUTOFF <= as_of < DEADLINE:
        raise DataError('coverage must close after publication cutoff and before deadline')
    if cov.get('inventory_sha256') != audit.hashes[inventory_path]:
        raise DataError('inventory hash mismatch')
    if cov.get('no_2026_outcomes_used') is not True:
        raise DataError('prospective non-contamination attestation missing')
    audit.sources(cov['sources'], latest=as_of)
    audit.sources(inventory['sources'], latest=as_of)
    official = p['official_candidates']
    names = official['names']
    ids = official['tse_ids']
    if len(names) != 2 or len(set(names)) != 2 or set(ids) != set(names) or len(set(ids.values())) != 2 or not all(ids.values()):
        raise DataError('exactly two officially qualified candidates with distinct TSE IDs required')
    if official.get('status') != 'CLASSIFICADOS_2T':
        raise DataError('official qualification evidence required, not a hypothetical matchup')
    audit.sources(official['sources'], latest=as_of)
    if not any((urlparse(ref['url']).hostname or '').endswith('.tse.jus.br')
               or urlparse(ref['url']).hostname == 'tse.jus.br' for ref in official['sources']):
        raise DataError('official two-candidate qualification requires a TSE source')
    target = p['target']
    if target['party'] != 'PL' or target['endorser'] != 'Jair Bolsonaro' or target['name'] not in names:
        raise DataError('target missing/unverified or absent from runoff; human review required')
    audit.sources(target['sources'], latest=as_of)
    rows = inventory['rows']
    row_ids = [row['poll_id'] for row in rows]
    if len(row_ids) != len(set(row_ids)):
        raise DataError('duplicate inventory poll_id')
    if set(row_ids) != set(cov['inventory_poll_ids']) or len(row_ids) != len(cov['inventory_poll_ids']):
        raise DataError('coverage is not reconciled to independently sourced inventory')
    indexed = {row['poll_id']: row for row in rows}
    accounted = [row['poll_id'] for row in p['polls'] + cov['not_published']]
    if len(accounted) != len(set(accounted)) or set(accounted) != set(row_ids):
        raise DataError('unaccounted/duplicate inventory poll')
    for row in rows:
        audit.sources(row['sources'], latest=as_of)
    registrations, legal_families = set(), {}
    for poll in p['polls']:
        row = indexed[poll['poll_id']]
        for key in ('registration', 'institute', 'fieldwork_start', 'fieldwork_end',
                    'office', 'scope', 'exit_poll', 'mode', 'sample_size', 'institute_legal_id', 'published_at'):
            if poll[key] != row[key]:
                raise DataError('poll disagrees with audited registration inventory: ' + key)
        if poll['registration'] in registrations:
            raise DataError('same registration cannot count as multiple waves/families')
        registrations.add(poll['registration'])
        if not poll.get('mode') or not poll.get('institute_legal_id'):
            raise DataError('mode and institutional legal identity required')
        if poll.get('institution_family', mapping.get(poll['institute'], 'unmapped:' + poll['institute'])) != mapping.get(poll['institute'], 'unmapped:' + poll['institute']):
            raise DataError('poll family conflicts with registered table')
        family = mapping.get(poll['institute'], 'unmapped:' + poll['institute'])
        legal = poll['institute_legal_id']
        if legal in legal_families and legal_families[legal] != family:
            raise DataError('same legal institute split across independent families; review aliases')
        legal_families[legal] = family
        publication = timestamp(poll['published_at'])
        if publication.date() < date.fromisoformat(poll['fieldwork_end']) or publication > as_of:
            raise DataError('publication before end of fieldwork or after audit')
        audit.sources(poll['sources'], latest=as_of)
        for scenario in poll['scenarios']:
            if not scenario.get('original_values') or not scenario.get('original_denominator'):
                raise DataError('original values/denominator required')
            audit.sources(scenario['sources'], latest=as_of)
    for missing in cov['not_published']:
        if missing['reason'] not in ('NOT_FOUND', 'NOT_PUBLISHED') or not missing.get('detail'):
            raise DataError('unexplained inventory exclusion')
        audit.sources(missing['sources'], latest=as_of)
    result = aggregate(p['polls'], names, ELECTION, CUTOFF, 2, mapping)
    result['inventory_exclusions'] = cov['not_published']
    result.update(c_star=target['name'], adv=next(n for n in names if n != target['name']), intervals=None)
    return result, p
