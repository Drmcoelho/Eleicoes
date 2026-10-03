"""Historical registration inventory, not an eligibility certificate or poll result."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta
import hashlib
import io
import json
from pathlib import Path
import re
from collections import defaultdict
import urllib.request
import zipfile

from src.statistics.freeze_1t import HISTORICAL_DATES


def parse_date(value: str) -> str:
    for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError('unknown PesqEle date format')


def normalize(manifest: Path, root: Path) -> dict:
    metadata = json.loads(manifest.read_text())
    year = metadata['year']
    if year not in HISTORICAL_DATES:
        raise ValueError('historical inventory only')
    archive = root / metadata['path']
    if hashlib.sha256(archive.read_bytes()).hexdigest() != metadata['sha256']:
        raise ValueError('PesqEle raw hash mismatch')
    rows, source_rows = [], defaultdict(list)
    with zipfile.ZipFile(archive) as z:
        member = f'pesquisa_eleitoral_{year}_BR.csv'
        reader = csv.DictReader(io.StringIO(z.read(member).decode('latin1')), delimiter=';')
        for row_number, r in enumerate(reader, 2):
            if int(r['AA_ELEICAO']) != year or r['SG_UE'] != 'BR':
                raise ValueError('unexpected registration election/jurisdiction')
            reg = r['NR_PROTOCOLO_REGISTRO']
            if not re.fullmatch(r'BR\d{5}' + str(year), reg):
                raise ValueError('unexpected registration format')
            # Older exports can repeat a registration for multiple contractors.
            # Preserve all source records; never count them as independent polls.
            source_rows[reg].append(row_number)
            cargo = r.get('DS_CARGO', r.get('DS_CARGOS'))
            if 'Presidente' not in cargo:
                continue
            start, end = parse_date(r['DT_INICIO_PESQUISA']), parse_date(r['DT_FIM_PESQUISA'])
            if start > end:
                raise ValueError('fieldwork dates inverted')
            windows = []
            for turn, d in enumerate(HISTORICAL_DATES[year], 1):
                election = datetime.fromisoformat(d).date()
                if election-timedelta(days=14) <= datetime.fromisoformat(end).date() <= election-timedelta(days=1):
                    windows.append(turn)
            if windows:
                rows.append({'poll_id': reg, 'registration': f'BR-{reg[2:7]}/{year}',
                             'source_record_id': f'{reg}:row{row_number}',
                             'year': year, 'candidate_turn_windows': windows,
                             'institute_legal_original': r['NM_EMPRESA'],
                             'institute_trade_original': r['NM_EMPRESA_FANTASIA'],
                             'cnpj_original': r['NR_CNPJ_EMPRESA'],
                             'fieldwork_start': start, 'fieldwork_end': end,
                             'sample_original': r.get('QT_ENTREVISTADO', r.get('QT_ENTREVISTADOS')),
                             'announced_publication_original': r.get('DT_DIVULGACAO'),
                             'scope_original': r['DS_DADO_MUNICIPIO'],
                             'source_manifest': manifest.relative_to(root).as_posix(),
                             'source_location': f'{member}: CSV row {row_number}',
                             'national_scope': 'NOT_VERIFIED', 'published_result': 'NOT_VERIFIED',
                             'scenario': 'NOT_VERIFIED', 'eligible': None})
    duplicates = {reg: indices for reg, indices in source_rows.items() if len(indices) > 1}
    for row in rows:
        row['flags'] = ['DUPLICATE_SOURCE_REGISTRATION_REVIEW_REQUIRED'] if row['poll_id'] in duplicates else []
    return {'year': year, 'status': 'REGISTRATION_INVENTORY_ONLY',
            'national_scope_is_not_implied_by_BR_registration': True,
            'duplicate_source_registrations': duplicates,
            'rows': sorted(rows, key=lambda row: row['poll_id'])}


def acquire(year: int, root: Path) -> Path:
    if year not in HISTORICAL_DATES:
        raise ValueError('historical inventory only')
    url = f'https://cdn.tse.jus.br/estatistica/sead/odsele/pesquisa_eleitoral/pesquisa_eleitoral_{year}.zip'
    raw = urllib.request.urlopen(url, timeout=60).read()
    digest = hashlib.sha256(raw).hexdigest()
    target = root / f'data/raw/pesqele/{year}-{digest[:12]}.zip'
    manifest = target.with_suffix('.manifest.json')
    if target.exists() or manifest.exists():
        if not target.exists() or not manifest.exists() or target.read_bytes() != raw:
            raise ValueError('raw acquisition collision/incomplete manifest')
        return manifest
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    manifest.write_text(json.dumps({'year': year, 'path': target.relative_to(root).as_posix(),
                       'sha256': digest, 'url': url, 'retrieved_at': datetime.now().astimezone().isoformat(),
                       'source_type': 'DADO_OFICIAL', 'purpose': 'registration inventory; not published poll result'}, indent=2)+'\n')
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--year', type=int, choices=HISTORICAL_DATES, required=True)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    manifest = args.manifest or acquire(args.year, args.root)
    packet = normalize(manifest, args.root)
    output = args.root / f'data/canonical/pesqele-inventory-{args.year}.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
