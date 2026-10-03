"""Lossless acquisition and deterministic normalization of historical TSE data.

Only 2014/2018/2022 endpoints are allowed. No generic outcome URL argument.
Archives stay outside Git; the original BR CSV member is preserved losslessly
in gzip, with both member and archive hashes. Never overwrite raw artifacts.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import urllib.request
import zipfile

YEARS = (2014, 2018, 2022)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def preserve_archive(year: int, archive: Path, root: Path) -> Path:
    if year not in YEARS:
        raise ValueError('only preregistered historical outcomes may be ingested')
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.upper().endswith(f'_{year}_BR.CSV')]
        if len(names) != 1:
            raise ValueError('exactly one original national BR member required')
        member = names[0]
        raw = z.read(member)
    member_hash = hashlib.sha256(raw).hexdigest()
    path = root / f'data/raw/tse/{year}-{member_hash[:12]}.csv.gz'
    manifest = path.with_suffix('.manifest.json')
    if path.exists() or manifest.exists():
        if not path.exists() or not manifest.exists() or gzip.decompress(path.read_bytes()) != raw:
            raise ValueError('raw collision or incomplete previous acquisition')
        return manifest
    path.parent.mkdir(parents=True, exist_ok=True)
    compressed = gzip.compress(raw, mtime=0)
    path.write_bytes(compressed)
    metadata = {'year': year, 'source_type': 'DADO_OFICIAL',
                'url': f'https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{year}.zip',
                'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'archive_sha256': digest(archive), 'archive_bytes': archive.stat().st_size,
                'member': member, 'member_sha256': member_hash,
                'path': path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(compressed).hexdigest(),
                'storage': 'gzip lossless; mtime=0; original member bytes unchanged'}
    manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    return manifest


def acquire(year: int, root: Path) -> Path:
    if year not in YEARS:
        raise ValueError('2026 outcomes forbidden in this acquisition path')
    url = f'https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{year}.zip'
    with tempfile.TemporaryDirectory() as directory:
        archive = Path(directory) / f'{year}.zip'
        with urllib.request.urlopen(url, timeout=60) as response, archive.open('wb') as target:
            while chunk := response.read(1024 * 1024):
                target.write(chunk)
        return preserve_archive(year, archive, root)


def normalize(manifest: Path, root: Path) -> dict:
    m = json.loads(manifest.read_text())
    if m['year'] not in YEARS:
        raise ValueError('historical years only')
    path = root / m['path']
    if digest(path) != m['sha256']:
        raise ValueError('raw hash mismatch')
    raw = gzip.decompress(path.read_bytes())
    if hashlib.sha256(raw).hexdigest() != m['member_sha256']:
        raise ValueError('member hash mismatch')
    reader = csv.DictReader(io.StringIO(raw.decode('latin1')), delimiter=';')
    required = {'ANO_ELEICAO', 'NR_TURNO', 'SG_UE', 'CD_CARGO', 'SQ_CANDIDATO',
                'NM_URNA_CANDIDATO', 'QT_VOTOS_NOMINAIS', 'CD_MUNICIPIO', 'NR_ZONA', 'ST_VOTO_EM_TRANSITO'}
    if not required <= set(reader.fieldnames or []):
        raise ValueError('TSE schema mismatch')
    counts, names, seen = defaultdict(int), {}, set()
    vote_column = 'QT_VOTOS_NOMINAIS_VALIDOS' if 'QT_VOTOS_NOMINAIS_VALIDOS' in reader.fieldnames else 'QT_VOTOS_NOMINAIS'
    for row in reader:
        if int(row['ANO_ELEICAO']) != m['year'] or row['SG_UE'] != 'BR' or row['CD_CARGO'] != '1':
            raise ValueError('mixed year/office/jurisdiction in national member')
        turn = int(row['NR_TURNO'])
        key = (turn, row['SQ_CANDIDATO'])
        row_key = key + (row['CD_MUNICIPIO'], row['NR_ZONA'], row['ST_VOTO_EM_TRANSITO'])
        if turn not in (1, 2) or row_key in seen:
            raise ValueError('duplicate municipal-zone candidate key or invalid turn')
        seen.add(row_key)
        votes = int(row[vote_column])
        if votes < 0:
            raise ValueError('negative nominal votes')
        if vote_column == 'QT_VOTOS_NOMINAIS' and row.get('DS_DETALHE_SITUACAO_CAND') != 'DEFERIDO':
            raise ValueError('legacy valid vote classification requires review')
        names[key] = row['NM_URNA_CANDIDATO']
        counts[key] += votes
    totals = {t: sum(n for (turn, _), n in counts.items() if turn == t) for t in (1, 2)}
    if any(v <= 0 for v in totals.values()):
        raise ValueError('both historical turns required')
    rows = [{'turn': t, 'candidate_id': c, 'name_original': names[t, c], 'votes': n,
             'valid_votes_total': totals[t], 'R': n / totals[t], 'source_type': 'DADO_OFICIAL',
             'source_manifest': manifest.relative_to(root).as_posix(), 'vote_column': vote_column}
            for (t, c), n in sorted(counts.items())]
    return {'year': m['year'], 'rows': rows, 'transformation': 'tse_br_nominal_validos_v1',
            'geography': 'Brazil including overseas (ZZ), no duplicated BRASIL/UF files'}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--year', type=int, choices=YEARS, required=True)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    manifest = preserve_archive(args.year, args.archive, args.root) if args.archive else acquire(args.year, args.root)
    normalized = normalize(manifest, args.root)
    output = args.root / f'data/canonical/tse-results-{args.year}.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
