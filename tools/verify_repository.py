#!/usr/bin/env python3
"""Validate public artifacts without importing historical modules or using data."""

import ast
import csv
import hashlib
import json
import re
import warnings
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((ROOT / 'source-manifest.json').read_text())
    sources = manifest['files']
    expected = {entry['path'] for entry in sources}
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / 'legacy').glob('*.py')}
    require(expected == actual, 'Historical source file list differs from manifest')
    for entry in sources:
        raw = (ROOT / entry['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == entry['published_sha256'],
                'Published source fingerprint differs: ' + entry['path'])

    python_files = list(ROOT.rglob('*.py'))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', SyntaxWarning)
        for path in python_files:
            ast.parse(path.read_text())
    for path in (ROOT / 'legacy').glob('prompt*.py'):
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                if node.targets[0].id.startswith('guidance'):
                    require(ast.literal_eval(node.value) == '', 'Embedded example must stay withheld')

    evidence = json.loads((ROOT / 'evidence-manifest.json').read_text())
    evidence_ids = {item['id'] for item in evidence['sources']}
    require(len(evidence_ids) == len(evidence['sources']), 'Duplicate evidence ID')
    for item in evidence['sources']:
        require(re.fullmatch('[0-9a-f]{64}', item['sha256']), 'Invalid evidence fingerprint')
        require(item['redistributed'] is False, 'Private source artifact marked for publication')

    public_artifacts = json.loads((ROOT / 'public-artifact-manifest.json').read_text())
    artifact_ids = {item['id'] for item in public_artifacts['artifacts']}
    require(len(artifact_ids) == len(public_artifacts['artifacts']), 'Duplicate public artifact ID')
    expected_artifacts = {item['path'] for item in public_artifacts['artifacts']}
    actual_artifacts = {
        str(path.relative_to(ROOT)) for path in (ROOT / 'assets').rglob('*') if path.is_file()
    }
    require(expected_artifacts == actual_artifacts, 'Public artifact file list differs from manifest')
    for item in public_artifacts['artifacts']:
        path = ROOT / item['path']
        require(path.is_file(), 'Missing public artifact: ' + item['path'])
        raw = path.read_bytes()
        require(re.fullmatch('[0-9a-f]{64}', item['sha256']), 'Invalid public artifact fingerprint')
        require(item['redistributed'] is True, 'Public artifact not marked for redistribution')
        require(item['byte_for_byte_archive_copy'] is True,
                'Public figure must remain an unmodified archive copy')
        require(len(raw) == item['bytes'], 'Public artifact size differs: ' + item['path'])
        require(hashlib.sha256(raw).hexdigest() == item['sha256'],
                'Public artifact fingerprint differs: ' + item['path'])

    audit = json.loads((ROOT / 'results/data-audit.json').read_text())
    require([row['query_records'] for row in audit['records']] == [737, 713, 713, 737],
            'Keep historical input/output versions distinct')
    for row in audit['records']:
        require(row['source_id'] in evidence_ids, 'Unknown data evidence ID')
        require(sum(row['queries_by_task'].values()) == row['query_records'], 'Query totals disagree')

    saved = json.loads((ROOT / 'results/saved-score-audit.json').read_text())
    for run in saved['runs']:
        for metric in run['metrics'].values():
            require(metric['source_id'] in evidence_ids, 'Unknown score source')
            require(0 <= metric['value'] <= 1 and metric['n'] > 0, 'Invalid aggregate score')
    standard = next(run for run in saved['runs'] if run['variant'] == 'standard')
    require(all(metric['n'] == 713 for metric in standard['metrics'].values()),
            'Standard saved evaluation uses 713 query scores')
    with (ROOT / 'results/thesis-table-4.csv').open(newline='') as handle:
        table = list(csv.DictReader(handle))
    require(len(table) == 14, 'Expected fourteen thesis conditions')
    for key in ('jaccard', 'bleu', 'bertscore'):
        require(round(standard['metrics'][key]['value'], 3) == float(table[2][key]),
                'Standard saved score and thesis transcription disagree')

    links = 0
    for path in ROOT.rglob('*.md'):
        content = path.read_text()
        require(not re.search(r'[\u4e00-\u9fff]', content), 'Explanatory documents must be English')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            require(resolved.is_relative_to(ROOT) and resolved.exists(), 'Broken local link: ' + target)
            links += 1

    prohibited = {'.pdf', '.docx', '.xlsx', '.sqlite3', '.db', '.zip', '.rar', '.m4a', '.srt', '.ipynb'}
    secret = re.compile(rb'sk-[A-Za-z0-9_-]{16,}|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----')
    private_path = re.compile(rb'/(?:Users|Volumes|home)/[A-Za-z0-9_.-]+')
    for path in ROOT.rglob('*'):
        if not path.is_file() or '.git' in path.parts:
            continue
        require(path.suffix not in prohibited, 'Unexpected private/binary artifact: ' + path.name)
        require('private-source-index' not in path.name, 'Private path index must stay outside repository')
        raw = path.read_bytes()
        require(not secret.search(raw), 'Credential-like content detected in ' + path.name)
        require(not private_path.search(raw),
                'Private local path detected in ' + path.name)
    require(json.loads((ROOT / 'examples/synthetic_session.json').read_text())['synthetic'] is True,
            'Example must remain labelled synthetic')
    print(f'PASS: {len(sources)} historical source files, {len(python_files)} Python syntax checks, '
          f'{len(evidence_ids)} private evidence sources, {len(artifact_ids)} public figure artifacts, '
          f'14 thesis conditions, {links} local links.')
    print('Publication consistency and hygiene checks only; not a live model run or complete security audit.')


if __name__ == '__main__':
    main()
