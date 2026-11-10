#!/usr/bin/env python3
"""Read-only checks of retained residue, timing and digest records."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import csv, hashlib, json
BASE = Path(__file__).resolve().parent

def fields(line):
    return {k: int(v) for k,v in (word.split('=',1) for word in line.split())}
def counters(path):
    return fields(path.read_text().splitlines()[0])
def main():
    exact = json.loads((BASE/'exact_n11_summary.json').read_text())
    sums = Counter()
    for residue in range(4):
        row = counters(BASE/f'exact_n11_r{residue}.stderr.txt')
        assert row.pop('n') == 11
        sums.update(row)
        run = exact['runs'][residue]
        assert run['res'] == residue and run['mod'] == 4
        assert run['exit_geng'] == run['exit_classifier'] == 0
    assert dict(sums) == exact['sum']
    almost_runs = json.loads((BASE/'almost_stuck_n11_runs.json').read_text())
    almost = Counter()
    for residue in range(4):
        row = counters(BASE/f'almost_stuck_n11_r{residue}.stderr.txt')
        assert row.pop('n') == 11
        almost.update(row)
        assert almost_runs[residue]['exit'] == [0,0]
        assert almost_runs[residue]['geng'][-1] == f'{residue}/4'
    original = [fields(line) for line in (BASE/'project_almost_stuck_orders3-11.txt').read_text().splitlines() if line.startswith('n=11 total=')]
    assert len(original) == 8
    original_sum = Counter()
    for row in original:
        row.pop('n'); original_sum.update(row)
    assert original_sum == almost
    assert almost['total'] == sums['connected'] == 1006700565
    assert almost['found'] == 0
    accounting = list(csv.DictReader((BASE/'search_accounting_rows.tsv').open(),delimiter='\t'))
    intervals = list(csv.DictReader((BASE/'search_task_intervals.tsv').open(),delimiter='\t'))
    assert len(accounting) == len(intervals) == 21
    for full, short in zip(accounting,intervals):
        for key in ('job_id','state','submit','start','end','elapsed'): assert full[key] == short[key]
        assert full['exit_code'] == '0:0' and full['state'] == 'COMPLETED'
    times = json.loads((BASE/'search_elapsed_comparison.json').read_text())['results']
    assert set(times) == {'13', '14'}
    for order, result in times.items():
        rows = [r for r in accounting if r['job_id'].split('_')[0] in result['jobs']]
        first = min(r['start'] for r in rows); last = max(r['end'] for r in rows)
        assert first == result['start'] and last == result['end']
        assert int((datetime.fromisoformat(last)-datetime.fromisoformat(first)).total_seconds()) == result['seconds']
    entries = json.loads((BASE/'SELECTION_SOURCES.json').read_text())
    assert len(entries) == len({e['file'] for e in entries})
    for entry in entries:
        assert len(entry['original_sha256']) == 64 and len(entry['sha256']) == 64
        assert entry['private_record'] and entry['transformation']
        assert Path(entry['file']).name == entry['file']
        assert hashlib.sha256((BASE/entry['file']).read_bytes()).hexdigest() == entry['sha256'], entry['file']
    identity = json.loads((BASE/'nauty289_identity.json').read_text())
    for entry in entries:
        if 'referenced_executable_sha256' in entry:
            assert entry['referenced_executable_sha256'] in json.dumps(identity)
        if 'referenced_source_archive_sha256' in entry:
            assert entry['referenced_source_archive_sha256'] in json.dumps(identity)
    elapsed = {
        'order13_original_restricted_search': times['13']['seconds'],
        'order14_original_K4_free_restricted_search': times['14']['seconds'],
    }
    print(json.dumps({'exact_residues':4,'almost_stuck_check_residues':4,'original_almost_stuck_contributions':8,'connected_total':sums['connected'],'almost_stuck_found':almost['found'],'accounting_rows':21,
        'historical_restricted_search_elapsed_seconds':elapsed,
        'elapsed_scope':'Last recorded task end minus first task start, UTC-7; original restricted searches, not full table13/table14 runs; excludes aggregation and homological adjudication.',
        'selected_digest_entries':len(entries),'all_checks_passed':True},indent=2))
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__ == '__main__': main()
