#!/usr/bin/env python3
"""Exact decision procedure for strong I-contractibility (class J_S) of a graph, with an
explicit deletion trace, and detection of "stuck" graphs.

Definitions (Dochtermann, Espinoza, Frias-Armenta, Hernandez, Discrete Math. 346 (2023)):
  * K_1 is in J_S.  The empty graph is NOT in J_S.
  * If G is in J_S and v is a vertex with N(v) in J_S, then G - v is in J_S  (and conversely
    G in J_S can be certified by deleting such a v when G - v is in J_S).
  * If G is in J_S and uv is an edge with N(u) cap N(v) in J_S, then G - uv is in J_S.
  G is in J_S iff G can be reduced to K_1 by a sequence of such vertex and edge deletions.

This is an exact (exhaustive, memoised) search over all deletion sequences; it depends on
nothing but the Python standard library, so it is an independent check of src/atascadas.c.

Usage:
  python3 strong_contractible.py file.g6            # one graph6 per line
  python3 strong_contractible.py --g6 'M?b@bFHNEk@~|k}U?' [--add 0 1] [--trace]
     --add u v   : add the edge uv before testing (vertex labels as in the graph6 string)
     --trace     : print an explicit deletion sequence down to K_1 (when the graph is in J_S)
     --stuck     : also report whether the graph is "stuck" (no vertex with N(v) in J_S and
                   no edge with non-empty N(u,v) in J_S)
"""
import sys
from functools import lru_cache
sys.setrecursionlimit(10000)

def parse_g6(s):
    s = s.strip()
    if s.startswith('>>graph6<<'): s = s[10:]
    data = [ord(c) - 63 for c in s]
    if data[0] == 63:
        n = (data[1] << 12) | (data[2] << 6) | data[3]; data = data[4:]
    else:
        n = data[0]; data = data[1:]
    bits = []
    for d in data: bits.extend([(d >> k) & 1 for k in range(5, -1, -1)])
    edges = set(); i = 0
    for v in range(1, n):
        for u in range(v):
            if bits[i]: edges.add((u, v))
            i += 1
    return frozenset(range(n)), frozenset(edges)

def nbrs(V, E, v):
    return frozenset(u for (a, b) in E for u in ((b,) if a == v else (a,) if b == v else ()))

def induced(V, E, S):
    return S, frozenset(e for e in E if e[0] in S and e[1] in S)

@lru_cache(maxsize=None)
def in_JS(V, E):
    """Exact membership in J_S.  Returns a deletion trace (tuple) or None."""
    if len(V) == 0: return None
    if len(V) == 1: return ()
    # vertices first (shrinks the graph fastest), then edges
    for v in sorted(V):
        Nv = nbrs(V, E, v)
        if not Nv: continue
        if in_JS(*induced(V, E, Nv)) is not None:
            rest = in_JS(*induced(V, E, V - {v}))
            if rest is not None: return (('v', v),) + rest
    for (u, v) in sorted(E):
        Nuv = nbrs(V, E, u) & nbrs(V, E, v)
        if not Nuv: continue
        if in_JS(*induced(V, E, Nuv)) is not None:
            rest = in_JS(V, E - {(u, v)})
            if rest is not None: return (('e', (u, v)),) + rest
    return None

def is_stuck(V, E):
    for v in V:
        Nv = nbrs(V, E, v)
        if Nv and in_JS(*induced(V, E, Nv)) is not None: return False
    for (u, v) in E:
        Nuv = nbrs(V, E, u) & nbrs(V, E, v)
        if Nuv and in_JS(*induced(V, E, Nuv)) is not None: return False
    return True

def main(argv):
    add = None; trace = '--trace' in argv; stuck = '--stuck' in argv
    if '--add' in argv:
        i = argv.index('--add'); add = (int(argv[i + 1]), int(argv[i + 2]))
    if '--g6' in argv:
        lines = [argv[argv.index('--g6') + 1]]
    else:
        files = [a for a in argv if not a.startswith('--') and not a.lstrip('-').isdigit()]
        f = open(files[0]) if files else sys.stdin
        lines = [l.split()[0] for l in f if l.strip() and not l.startswith('#')]
    for s in lines:
        V, E = parse_g6(s)
        label = s
        if add:
            u, v = sorted(add); E = E | {(u, v)}; label += f' +{{{u},{v}}}'
        t = in_JS(V, E)
        out = f'{label}  n={len(V)} m={len(E)}  ' + ('in J_S' if t is not None else 'NOT in J_S')
        if stuck: out += '  stuck=' + ('yes' if is_stuck(V, E) else 'no')
        print(out)
        if trace and t is not None:
            for k, (kind, x) in enumerate(t, 1):
                print(f'  {k:2d}. delete ' + (f'vertex {x}' if kind == 'v' else f'edge {x[0]}-{x[1]}'))
            print(f'  -> K_1 after {len(t)} deletions')

if __name__ == '__main__':
    main(sys.argv[1:])
