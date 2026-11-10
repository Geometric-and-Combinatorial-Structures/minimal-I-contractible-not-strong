#!/usr/bin/env python3
"""Emit exact TikZ figures from the frozen witness data, at final printed size.

Only Python's standard library is required. The graph data, coordinate maps and
triangle gluing are separate from the drawing. No source delivery is modified.
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import hashlib
import json
import math
import re
import argparse

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).with_name('witness_data.json')
OUT = ROOT / 'build' / 'generated-paper' / 'figures'
REPORT = ROOT / 'build' / 'verification' / 'witnesses'


def canonical_edge(e):
    return tuple(sorted(e))


def triangles(n, edges):
    eset = set(map(canonical_edge, edges))
    return [t for t in combinations(range(n), 3)
            if all(e in eset for e in combinations(t, 2))]


def unfold(n, edges):
    tris = triangles(n, edges)
    incident = defaultdict(list)
    for i, tri in enumerate(tris):
        for e in combinations(tri, 2):
            incident[e].append(i)
    parent = {}

    def find(c):
        while parent.setdefault(c, c) != c:
            parent[c] = parent[parent[c]]
            c = parent[c]
        return c

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, tri in enumerate(tris):
        for v in tri:
            find((i, v))
    for e, faces in incident.items():
        if len(faces) == 2:
            for v in e:
                union((faces[0], v), (faces[1], v))
    roots = sorted({find(c) for c in parent}, key=lambda x: (x[1], x[0]))
    idx = {c: i for i, c in enumerate(roots)}
    label = {idx[c]: c[1] for c in roots}
    lifted = [tuple(idx[find((i, v))] for v in t) for i, t in enumerate(tris)]
    counts = Counter(canonical_edge(e) for t in lifted for e in combinations(t, 2))
    return label, lifted, counts


def distance_to_segment(p, a, b):
    d = [b[i] - a[i] for i in range(2)]
    t = max(0., min(1., sum((p[i] - a[i]) * d[i] for i in range(2)) /
                    sum(x * x for x in d)))
    return math.dist(p, [a[i] + t * d[i] for i in range(2)])


def emit(name, vertices, edges, labels, positions, scale, highlight=(),
         added=(), node_options=None, face_triangles=()):
    pos = {v: [scale * float(x) for x in positions[str(v)]] for v in vertices}
    edges = sorted(map(canonical_edge, edges))
    assert len(edges) == len(set(edges))
    high, extra = set(map(canonical_edge, highlight)), set(map(canonical_edge, added))
    nodes = node_options or {}
    lines = [r'\begin{tikzpicture}[x=1cm,y=1cm]',
             r'\definecolor{witnessred}{RGB}{181,55,36}',
             r'\definecolor{witnessblue}{RGB}{32,89,140}']
    for v in vertices:
        lines.append(r'\coordinate (v%d) at (%.9f,%.9f);' % (v, *pos[v]))
    for tri in face_triangles:
        lines.append(r'\fill[blue!3] ' + ' -- '.join('(v%d)' % v for v in tri) + ' -- cycle;')
    for a, b in edges:
        style = 'draw=black!52,line width=.38pt'
        if (a, b) in high:
            style = 'draw=witnessred,line width=.8pt'
        if (a, b) in extra:
            style = 'draw=witnessblue,line width=1pt,dashed'
        lines.append(r'\draw[%s] (v%d) -- (v%d);' % (style, a, b))
    # All complete, opaque nodes are drawn after all edges.
    for v in vertices:
        style = 'jfef vertex' + (',' + nodes[v] if v in nodes else '')
        lines.append(r'\node[%s] at (v%d) {$%s$};' % (style, v, labels[v]))
    lines += [r'\end{tikzpicture}', '']
    tex = '\n'.join(lines)
    (OUT / (name + '.tex')).write_text(tex)
    # Parse the emitted edge statements independently of their count.
    emitted = [tuple(map(int, m)) for m in re.findall(
        r'\\draw\[[^\n]+\] \(v(\d+)\) -- \(v(\d+)\);', tex)]
    assert emitted == edges
    emitted_nodes = re.findall(r'\\node\[[^\n]+\] at \(v(\d+)\) \{\$([^$]+)\$\};', tex)
    assert [(int(v), s) for v, s in emitted_nodes] == [(v, str(labels[v])) for v in vertices]
    mind = min(math.dist(pos[a], pos[b]) for a, b in combinations(vertices, 2))
    clearance = min(distance_to_segment(pos[v], pos[a], pos[b])
                    for a, b in edges for v in vertices if v not in (a, b))
    assert mind > .68, (name, mind)
    assert clearance > .34, (name, clearance)
    return {'panel': name, 'vertices': len(vertices), 'edges': len(edges),
            'edge_set_exact': True, 'all_labels_math_mode': True,
            'font_size_pt': 8, 'minimum_node_diameter_mm': 5.8,
            'minimum_centre_distance_cm': mind,
            'minimum_nonincident_edge_centre_distance_cm': clearance,
            'coordinate_width_cm': max(p[0] for p in pos.values()) - min(p[0] for p in pos.values()),
            'coordinate_height_cm': max(p[1] for p in pos.values()) - min(p[1] for p in pos.values()),
            'sha256': hashlib.sha256(tex.encode()).hexdigest()}


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=OUT)
    parser.add_argument('--check', action='store_true', help='compare generated files with the frozen article')
    args = parser.parse_args()
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from output_paths import generated_output
    try:
        args.output_dir = generated_output(args.output_dir)
    except ValueError as error:
        parser.error(str(error))
    OUT = args.output_dir.resolve()
    if OUT == ROOT/'paper' or OUT.is_relative_to(ROOT/'paper'):
        parser.error('Generate outside the frozen article; use --check to compare')
    data = json.loads(DATA.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    g13 = data['graphs']['G13']
    ga = data['graphs']['Ga']
    label, lifted, counts = unfold(g13['n'], g13['edges'])
    boundary = [e for e, k in counts.items() if k == 1]
    boundary_vertices = set(v for e in boundary for v in e)
    reports = [emit('G13_disc', sorted(label), counts, label,
                    data['positions']['G13_disc'], 3.4, highlight=boundary,
                    node_options={v: 'draw=witnessred,line width=.7pt' for v in boundary_vertices},
                    face_triangles=lifted)]
    reports.append(emit('G13_graph', list(range(13)), g13['edges'],
                        {v: v for v in range(13)}, data['positions']['G13_graph'], 1.6,
                        highlight=[(8, 10), (10, 9), (9, 11), (11, 8)],
                        node_options={v: 'draw=witnessred,line width=.7pt' for v in (8, 9, 10, 11)}))
    reports.append(emit('Ga_extension', list(range(14)), ga['edges'] + [[0, 1]],
                        {v: v for v in range(14)}, data['positions']['G14a'], 2.3,
                        highlight=[(8, 12), (12, 5), (5, 10), (10, 13)], added=[(0, 1)],
                        node_options={**{v: 'fill=orange!12' for v in (8, 12, 5, 10, 13)},
                                      **{v: 'draw=witnessblue,line width=.8pt' for v in (0, 1)}}))
    (REPORT / 'figure_data_checks.json').write_text(json.dumps(reports, indent=2) + '\n')
    if args.check:
        for name in ['G13_disc.tex', 'G13_graph.tex', 'Ga_extension.tex']:
            if (OUT/name).read_bytes() != (ROOT/'paper/figures'/name).read_bytes():
                parser.exit(1, 'Generated figure differs from the frozen article: ' + name + '\n')
    print(json.dumps(reports, indent=2))


if __name__ == '__main__':
    main()
