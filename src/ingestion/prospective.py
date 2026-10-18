"""Preserve explicitly supplied evidence, without interpreting or fetching outcomes.

Capture original bytes first; normalization/review is a separate operation. Repeated
imports are idempotent. A changed source creates a new SHA-addressed raw version.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from src.statistics.cofre_a import DataError

KINDS = ('registration', 'publication', 'official_candidates', 'endorsement',
         'family', 'coverage')


def preserve(root: Path, source: Path, url: str, kind: str, location: str) -> dict:
    if kind not in KINDS or urlparse(url).scheme not in ('http', 'https') or not location.strip():
        raise DataError('evidence kind, original URL and precise location required')
    raw = source.read_bytes()
    if not raw:
        raise DataError('empty source is not evidence')
    digest = hashlib.sha256(raw).hexdigest()
    directory = root / 'data/raw/prospective-2t'
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / digest
    # Source metadata is also addressed by content: the same bytes can legitimately
    # have several original URLs/locations. Never silently replace an acquisition.
    identity = json.dumps([digest, url, kind, location], ensure_ascii=False).encode()
    manifest = directory / (hashlib.sha256(identity).hexdigest() + '.manifest.json')
    if manifest.exists():
        record = json.loads(manifest.read_text())
        if not target.exists() or target.read_bytes() != raw:
            raise DataError('raw acquisition collision or incomplete previous acquisition')
        return record
    if target.exists():
        if target.read_bytes() != raw:
            raise DataError('raw hash collision')
    else:
        with target.open('xb') as stream:
            stream.write(raw)
    record = dict(path=target.relative_to(root).as_posix(), sha256=digest,
                  url=url, retrieved_at=datetime.now(timezone.utc).isoformat(),
                  location=location, kind=kind, status='UNREVIEWED', bytes=len(raw))
    with manifest.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--file', type=Path, required=True)
    parser.add_argument('--url', required=True)
    parser.add_argument('--kind', choices=KINDS, required=True)
    parser.add_argument('--location', required=True)
    args = parser.parse_args()
    print(json.dumps(preserve(args.root.resolve(), args.file, args.url, args.kind,
                              args.location), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
