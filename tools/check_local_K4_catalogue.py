#!/usr/bin/env python3
"""Check all stored small K4-free graphs and the almost-stuck exclusion.

No generator is needed. The check validates the finite list and its local
properties; exhaustive coverage remains a claim of the recorded generation.
"""
from collections import defaultdict
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'finite/certificates'))
sys.path.insert(0, str(ROOT / 'tools'))
from finite_checks import decode, encode, cliques, components, tree, induced, h1
from finite_isomorphism import pairwise_nonisomorphic


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data/local_K4')
    args = parser.parse_args()
    path = args.data_dir / 'connected_n2_7.g6'
    raw = path.read_bytes()
    metadata = json.loads((path.parent / 'generation.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == metadata['catalogue_sha256']
    lines = raw.decode().splitlines()
    assert len(lines) == len(set(lines)) == metadata['classes'] == 643
    byorder = defaultdict(list)
    for line in lines:
        A = decode(line)
        assert encode(A) == line
        assert 2 <= len(A) <= 7 and components(A) == 1 and not cliques(A, 4)
        byorder[len(A)].append(line)
    reference = json.loads((ROOT / 'finite/provenance/local_K4_small_checks.json').read_text())
    old = {r['order']: r for r in reference['runs']}
    reports = []
    for n, expected in {2: 1, 3: 2, 4: 5, 5: 17, 6: 82, 7: 536}.items():
        assert len(byorder[n]) == expected
        iso = pairwise_nonisomorphic(byorder[n])
        candidates, found = [], []
        for graph in byorder[n]:
            A = decode(graph)
            if any((A[u] & A[v]).bit_count() == 1 for u, v in cliques(A, 2)):
                continue
            admissible = [v for v, row in enumerate(A) if tree(induced(A, row))]
            if len(admissible) > 1:
                continue
            candidates.append({'graph6': graph, 'admissible_vertices': admissible})
            if n - len(cliques(A, 2)) + len(cliques(A, 3)) != 1:
                continue
            free, torsion = h1(A)
            # K4-free + connected + chi=1: beta2(F2)=beta1(F2).
            # UCT gives beta1(F2)=free rank + number of even torsion factors.
            if free == 0 and all(d % 2 for d in torsion):
                found.append({'graph6': graph, 'admissible_vertices': admissible})
        assert len(candidates) == old[n]['local_candidates'] and not found
        stream = ('\n'.join(byorder[n]) + '\n').encode()
        recorded, = [r for r in metadata['runs'] if r['order'] == n]
        assert recorded['exit'] == 0 and recorded['connected_K4_free_graphs'] == expected
        assert recorded['options'] == ['-kc', str(n)]
        assert hashlib.sha256(stream).hexdigest() == recorded['stream_sha256']
        reports.append({'order': n, 'classes': expected, 'isomorphism': iso,
                        'zero_admissible_vertex_candidates': sum(not r['admissible_vertices'] for r in candidates),
                        'one_admissible_vertex_candidates': sum(len(r['admissible_vertices']) == 1 for r in candidates),
                        'almost_stuck': found})
    print(json.dumps({'PASS': True, 'classes_checked': 643,
        'definition': 'F2-acyclic; no admissible edge; zero or one admissible vertex',
        'local_criterion': 'vertex link a nonempty tree; edge common neighbourhood a singleton',
        'catalogue_sha256': hashlib.sha256(raw).hexdigest(), 'orders': reports,
        'coverage': 'finite list checked; exhaustive coverage uses the recorded generator',
        'generator_executed': False}, indent=2))


if not __debug__:
    raise RuntimeError('Run without -O: assertions are required.')
if __name__ == '__main__':
    main()
