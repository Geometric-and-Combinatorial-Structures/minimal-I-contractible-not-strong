#!/usr/bin/env python3
"""Generate the finite incidence tables printed in the mathematical appendix."""
from pathlib import Path
import json
import argparse
from make_witness_figures import ROOT, DATA, unfold

OUT = ROOT / 'build' / 'generated-paper' / 'tables'


def math_list(values):
    return '$' + (','.join(map(str, values)) if values else r'\varnothing') + '$'


def operation(s):
    element = s['element']
    if s['kind'] == 'vertex':
        return '$v(%d)$' % element
    return '$e(%d,%d)$' % tuple(element)


def path_notation(s):
    verts, edges = s['link_vertices'], s['link_edges']
    if len(verts) == 1:
        return '$%d$' % verts[0]
    adj = {v: set() for v in verts}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    if max(map(len, adj.values())) <= 2:
        current = min(v for v in verts if len(adj[v]) == 1)
        order, prev = [], None
        while True:
            order.append(current)
            nxt = adj[current] - {prev}
            if not nxt:
                break
            prev, current = current, next(iter(nxt))
        assert len(order) == len(verts)
        return '$' + r'\text{--}'.join(map(str, order)) + '$'
    # The unique non-path neighbourhood in the variants.
    assert set(map(tuple, edges)) == {(1, 8), (1, 11), (8, 10), (8, 12)}
    return r'$11\text{--}1\text{--}8\text{--}10,\ 8\text{--}12$'


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=OUT)
    parser.add_argument('--check', action='store_true', help='compare generated tables with the frozen article')
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
    data = json.loads(DATA.read_text()); OUT.mkdir(parents=True, exist_ok=True)
    rows = [r'\begin{tabular}{@{}rllll@{}}', r'\toprule',
            r'$i$ & $\Gt$ & $\Ga$ & $\Gb$ & $\Gc$ \\', r'\midrule']
    for i in range(14):
        row = [str(i)]
        for name in ['G13', 'Ga', 'Gb', 'Gc']:
            g = data['graphs'][name]
            row.append('---' if i >= g['n'] else math_list(sorted(b for a, b in g['edges'] if a == i)))
        rows.append(' & '.join(row) + r' \\')
    rows += [r'\bottomrule', r'\end{tabular}']
    (OUT / 'witness_adjacency.tex').write_text('\n'.join(rows) + '\n')
    rga, rgb, rgc = data['reductions']
    rows = [r'\begin{tabular}{@{}rll@{}}', r'\toprule',
            r'Step & Delete & Current neighbourhood \\', r'\midrule']
    for s in rga['steps']:
        rows.append('%d & %s & %s' % (s['step'], operation(s), path_notation(s)) + r' \\')
    rows += [r'\bottomrule', r'\end{tabular}']
    (OUT / 'Ga_reduction.tex').write_text('\n'.join(rows) + '\n')
    rows = [r'\begin{tabular}{@{}rllll@{}}', r'\toprule',
            r'& \multicolumn{2}{c}{$\Gb+\{0,3\}$} & \multicolumn{2}{c}{$\Gc+\{2,3\}$} \\',
            r'Step & Delete & Current neighbourhood & Delete & Current neighbourhood \\', r'\midrule']
    for i in range(19):
        row = [str(i + 1)]
        for reduction in (rgb, rgc):
            if i < len(reduction['steps']):
                s = reduction['steps'][i]; row += [operation(s), path_notation(s)]
            else:
                row += ['---', '---']
        rows.append(' & '.join(row) + r' \\')
    rows += [r'\bottomrule', r'\end{tabular}']
    (OUT / 'variant_reductions.tex').write_text('\n'.join(rows) + '\n')
    g = data['graphs']['G13']; labels, tris, counts = unfold(g['n'], g['edges'])
    badj = {}
    for (a, b), k in counts.items():
        if k == 1:
            badj.setdefault(a, set()).add(b); badj.setdefault(b, set()).add(a)
    start = max(badj, key=lambda x: data['positions']['G13_disc'][str(x)][1])
    cycle, prev = [start], None
    while True:
        nxt = min(badj[cycle[-1]] - {prev})
        if nxt == start:
            break
        prev = cycle[-1]; cycle.append(nxt)
    if [labels[x] for x in cycle[:4]] != [10, 9, 11, 8]:
        cycle = [cycle[0]] + cycle[:0:-1]
    assert [labels[x] for x in cycle] == [10, 9, 11, 8] * 3
    names = {v: ('b_{%d}' % cycle.index(v) if v in cycle else str(labels[v])) for v in labels}
    rows = [r'\begin{tabular}{@{}rlrlrlrl@{}}', r'\toprule',
            r'$j$ & $T_j$ & $j$ & $T_j$ & $j$ & $T_j$ & $j$ & $T_j$ \\', r'\midrule']
    for row in range(7):
        entries = []
        for col in range(4):
            j = row + col * 7
            entries += [str(j+1), '$\\{'+','.join(names[v] for v in tris[j])+r'\}$']
        rows.append(' & '.join(entries) + r' \\')
    rows += [r'\bottomrule', r'\end{tabular}']
    (OUT / 'G13_disc_triangles.tex').write_text('\n'.join(rows) + '\n')
    if args.check:
        for name in ['witness_adjacency.tex', 'Ga_reduction.tex', 'variant_reductions.tex', 'G13_disc_triangles.tex']:
            if (OUT/name).read_bytes() != (ROOT/'paper/tables'/name).read_bytes():
                parser.exit(1, 'Generated table differs from the frozen article: ' + name + '\n')


if __name__ == '__main__':
    main()
