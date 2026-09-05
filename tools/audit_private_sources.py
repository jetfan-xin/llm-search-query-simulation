#!/usr/bin/env python3
"""Read-only fingerprint/aggregate checks against an uncommitted source map.

No model inference, network access, participant-row output or file writes.
"""

import argparse
import hashlib
import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dataset_summary(path):
    data = json.loads(path.read_text())
    queries = []
    by_task = {}
    sessions = rationales = feedback = serps = clicks = 0
    for user in data:
        for task_id, task in user['task'].items():
            sessions += 1
            events = task['content'].values() if 'content' in task else task.values()
            for event in events:
                queries.append(event.get('query', ''))
                by_task[task_id] = by_task.get(task_id, 0) + 1
                # Same explicit missing-report marker used by the historical checker.
                rationale = event.get('thought', '')
                response = event.get('satisfaction_thought', '')
                rationales += bool(rationale) and '\u88ab\u8bd5\u6ca1\u8bf4' not in rationale
                feedback += bool(response) and '\u88ab\u8bd5\u6ca1\u8bf4' not in response
                serps += len(event.get('SERP', []))
                clicks += sum(result.get('click_or_not') == 1 for result in event.get('SERP', []))
    return {'users': len(data), 'sessions': sessions, 'query_records': len(queries),
            'distinct_literal_queries': len(set(queries)), 'queries_by_task': by_task,
            'rationales_under_legacy_completeness_rule': rationales,
            'feedback_under_legacy_completeness_rule': feedback,
            'serp_entries': serps, 'clicked_entries': clicks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-map', type=Path, required=True)
    args = parser.parse_args()
    source_map = args.source_map.resolve()
    require(not source_map.is_relative_to(ROOT), 'Keep the private source map outside the repository')
    paths = {sid: Path(path) for sid, path in json.loads(source_map.read_text())['sources'].items()}
    manifest = json.loads((ROOT / 'evidence-manifest.json').read_text())
    for entry in manifest['sources']:
        sid = entry['id']
        require(sid in paths and paths[sid].is_file(), 'Missing private evidence source: ' + sid)
        digest = hashlib.sha256()
        with paths[sid].open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(chunk)
        require(digest.hexdigest() == entry['sha256'], 'Different source version: ' + sid)
    print(f"PASS: {len(manifest['sources'])} original evidence fingerprints match.")

    summaries = json.loads((ROOT / 'results/data-audit.json').read_text())['records']
    for expected in summaries:
        sid = expected['source_id']
        observed = dataset_summary(paths[sid])
        require(observed == {key: value for key, value in expected.items() if key != 'source_id'},
                'Data aggregate mismatch: ' + sid)
    print('PASS: four data/output versions, sample counts and annotation counts match.')

    runs = json.loads((ROOT / 'results/saved-score-audit.json').read_text())['runs']
    score_count = 0
    for run in runs:
        for name, expected in run['metrics'].items():
            source_id = expected['source_id']
            data = json.loads(paths[source_id].read_text())
            if name == 'jaccard':
                values = [value for key, scores in data.items() if key != 'average' for value in scores]
                observed = statistics.mean(statistics.mean(data[str(i)]) for i in range(1, 11))
                require(abs(observed - data['average']['0']) < 1e-10,
                        'Stored Jaccard mean disagrees with its score arrays: ' + source_id)
            else:
                values = data if isinstance(data, list) else [value for scores in data.values() for value in scores]
                observed = statistics.mean(values)
            require(len(values) == expected['n'] and abs(observed - expected['value']) < 1e-10,
                    'Saved-score aggregate mismatch: ' + source_id)
            score_count += 1
    print(f'PASS: {score_count} saved-score aggregates across {len(runs)} condition records match.')
    print('No participant records printed, files changed, models loaded or network calls made.')


if __name__ == '__main__':
    main()
