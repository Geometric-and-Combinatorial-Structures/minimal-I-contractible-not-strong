#!/usr/bin/env python3
"""Recompute integral H1 for the four published eleven-vertex torsion graphs."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'certificates'))
from finite_checks import decode, h1, cliques, isomorphic

def main():
    strings = (ROOT / 'data/adamaszek_11_graphs.g6').read_text().splitlines()
    record = json.loads((ROOT / 'data/adamaszek_11_homology.json').read_text())
    assert len(strings) == len(record['graphs']) == 4
    graphs = []
    actual = []
    for i, text in enumerate(strings, 1):
        graph = decode(text)
        assert len(graph) == 11
        assert all(not isomorphic(graph, other) for other in graphs)
        graphs.append(graph)
        free, torsion = h1(graph)
        assert (free, torsion) == (0, (2,))
        actual.append({'graph': i, 'graph6': text, 'vertices': 11,
                       'edges': len(cliques(graph, 2)),
                       'triangles': len(cliques(graph, 3)),
                       'H1_free_rank': free, 'H1_torsion': list(torsion)})
    assert actual == record['graphs']
    print(json.dumps({'graphs_checked': 4, 'pairwise_nonisomorphic': True,
                      'H1': 'Z/2 for each graph; free rank zero',
                      'method': 'Integral cycle lattice and Smith normal form'}, indent=2))

if not __debug__:
    raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__ == '__main__':
    main()
