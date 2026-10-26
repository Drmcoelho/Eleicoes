"""Verify this audit bundle and preservation of every pre-existing Git blob.

Default: inspect HEAD in a real clone. --tree-json accepts a separately retrieved
GitHub recursive tree JSON (or response envelope) for a connector-only checkout.
Hashes ensure integrity, not pre-deadline publication or semantic source fidelity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tree_entries(document):
    payload = document.get('response', document)
    require(payload.get('truncated') is False, 'Truncated tree evidence')
    return {x['path']: (x['mode'], x['type'], x['sha']) for x in payload['tree'] if x['type'] == 'blob'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree-json', type=Path)
    args = parser.parse_args()
    manifest = json.loads((HERE / 'integrity.json').read_text())
    for item in manifest['files']:
        path = (ROOT / item['path']).resolve()
        require(path.is_relative_to(ROOT), 'Path outside repository')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'],
                f"Audit evidence changed: {item['path']}")
    before = tree_entries(json.loads((HERE / 'evidence/tree.json').read_text()))
    if args.tree_json:
        after = tree_entries(json.loads(args.tree_json.read_text()))
    else:
        raw = subprocess.check_output(['git', 'ls-tree', '-rz', 'HEAD'], cwd=ROOT).decode()
        after = {}
        for row in raw.split('\0'):
            if row:
                meta, name = row.split('\t', 1)
                mode, kind, sha = meta.split()
                after[name] = (mode, kind, sha)
    for name, entry in before.items():
        require(after.get(name) == entry, f'Pre-existing blob changed or removed: {name}')
    refs = json.loads((HERE / 'evidence/refs.json').read_text())['response']
    require(not any(x['ref'].startswith('refs/tags/') for x in refs), 'Snapshot contains a tag')
    for filename in ('output_initial.json', 'output_current.json'):
        d = json.loads((HERE / 'evidence' / filename).read_text())
        d = d.get('response', d)
        require(d['status'] == 'BLOCKED' and d['calibration']['E_hist_size'] == 0,
                'Audited preparation is no longer the recorded BLOCKED object')
        require(d['output_2T']['P'] is None, 'Unexpected forecast')
    print(f"OK: {len(manifest['files'])} hashes; {len(before)} original blobs preserved; recorded BLOCKED/no-tag evidence consistent")


if __name__ == '__main__':
    main()
