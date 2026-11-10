"""Exact finite-list isomorphism checks, with safe invariant bucketing."""
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'finite/certificates'))
from finite_checks import decode, isomorphic as _equal_order_isomorphic


def isomorphic(A, B):
    # The retained finite backtracker assumes equal orders. Enforce its domain
    # before calling it, including when the first graph is empty.
    return len(A) == len(B) and _equal_order_isomorphic(A, B)


def invariant(A):
    # Degree and number of incident triangles are preserved by isomorphism.
    return len(A), tuple(sorted((row.bit_count(), sum(bool(A[u] >> v & 1)
        for u, v in combinations((w for w in range(len(A)) if row >> w & 1), 2)))
        for row in A))


def pairwise_nonisomorphic(graphs):
    buckets = defaultdict(list)
    comparisons = 0
    for graph in graphs:
        A = decode(graph)
        group = buckets[invariant(A)]
        for old, B in group:
            comparisons += 1
            assert not isomorphic(A, B), ('isomorphic duplicate', old, graph)
        group.append((graph, A))
    return {'classes': len(graphs), 'invariant_buckets': len(buckets),
            'exact_pair_comparisons': comparisons, 'isomorphic_duplicates': 0}


def unique_inclusions(source, target):
    buckets = defaultdict(list)
    for graph in target:
        A = decode(graph)
        buckets[invariant(A)].append((graph, A))
    matches = []
    for graph in source:
        A = decode(graph)
        found = [other for other, B in buckets[invariant(A)] if isomorphic(A, B)]
        assert len(found) == 1, ('expected one isomorphic target', graph, found)
        matches.append({'source': graph, 'target': found[0]})
    assert len({r['target'] for r in matches}) == len(matches)
    return matches
