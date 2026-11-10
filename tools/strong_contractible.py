#!/usr/bin/env python3
"""Exact decision procedure for strong I-contractibility (class J_S) of a graph, with an
explicit deletion trace, and detection of "stuck" graphs.

Definitions (Dochtermann, Espinoza, Frias-Armenta, Hernandez, Discrete Math. 346 (2023), Defs. 4-5):
  J_S is the class generated from K_1 by gluing a vertex along a neighbourhood in J_S and by gluing
  an edge uv whose common neighbourhood N(u) cap N(v) is in J_S.  Equivalently (this is what is
  computed): G is in J_S iff G = K_1, or G has a vertex v with N(v) in J_S and G - v in J_S, or G has
  an edge uv with N(u) cap N(v) in J_S and G - uv in J_S.  The empty graph is NOT in J_S.
  Membership does NOT mean that every such deletion stays in J_S: the order of deletions matters.
  G is in J_S iff G can be reduced to K_1 by SOME sequence of such vertex and edge deletions.

This is an exact (exhaustive, memoised) search over all deletion sequences; it depends on
nothing but the Python standard library, so it is an independent check of src/atascadas.c.

Usage:
  python3 strong_contractible.py file.g6            # one graph6 per line
  python3 strong_contractible.py --g6 'M?b@bFHNEk@~|k}U?' [--add 0 1] [--trace]
     --add u v   : add the edge uv before testing (vertex labels as in the graph6 string)
     --trace     : print an explicit deletion sequence down to K_1 (when the graph is in J_S)
     --stuck     : also report whether the graph is "stuck" in the sense of the paper: at least two
                   vertices, Z/2-acyclic clique complex, no vertex with N(v) in J_S and no edge
                   with N(u,v) in J_S.  "no_moves" reports the last two conditions alone.
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

def no_moves(V, E):
    """True if no vertex has N(v) in J_S and no edge has N(u,v) in J_S (no strong deletion)."""
    for v in V:
        Nv = nbrs(V, E, v)
        if Nv and in_JS(*induced(V, E, Nv)) is not None: return False
    for (u, v) in E:
        Nuv = nbrs(V, E, u) & nbrs(V, E, v)
        if Nuv and in_JS(*induced(V, E, Nuv)) is not None: return False
    return True

def z2_acyclic(V, E):
    """Reduced Z/2-homology of the clique complex vanishes (requires a non-empty graph)."""
    if not V: return False
    adj = {v: set() for v in V}
    for (a, b) in E:
        adj[a].add(b); adj[b].add(a)
    faces = []                       # all cliques, as sorted tuples
    def extend(cur, cand):
        for v in sorted(cand):
            new = cur + (v,)
            faces.append(new)
            extend(new, {u for u in cand if u > v and u in adj[v]})
    extend((), set(V))
    by_dim = {}
    for f in faces:
        by_dim.setdefault(len(f) - 1, []).append(f)
    index = {d: {f: i for i, f in enumerate(fs)} for d, fs in by_dim.items()}
    def rank_boundary(d):            # rank over Z/2 of d_d : C_d -> C_{d-1}
        basis = {}                   # leading bit -> reduced vector (Python int as bit set)
        for f in by_dim.get(d, []):
            vec = 0
            for i in range(len(f)):
                vec ^= 1 << index[d - 1][f[:i] + f[i + 1:]]
            while vec:
                lead = vec.bit_length() - 1
                if lead not in basis:
                    basis[lead] = vec
                    break
                vec ^= basis[lead]
        return len(basis)
    top = max(by_dim)
    rk = {d: rank_boundary(d) for d in range(1, top + 1)}
    rk[top + 1] = 0
    if len(by_dim[0]) - rk.get(1, 0) != 1:
        return False                 # reduced b_0 != 0
    return all(len(by_dim[d]) - rk[d] - rk[d + 1] == 0 for d in range(1, top + 1))

def is_stuck(V, E):
    """Stuck in the sense of the paper: |V| >= 2, Z/2-acyclic, and no strong deletion available."""
    return len(V) >= 2 and z2_acyclic(V, E) and no_moves(V, E)

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
        if stuck:
            out += '  stuck=' + ('yes' if is_stuck(V, E) else 'no')
            out += '  no_moves=' + ('yes' if no_moves(V, E) else 'no')
        print(out)
        if trace and t is not None:
            for k, (kind, x) in enumerate(t, 1):
                print(f'  {k:2d}. delete ' + (f'vertex {x}' if kind == 'v' else f'edge {x[0]}-{x[1]}'))
            print(f'  -> K_1 after {len(t)} deletions')

if __name__ == '__main__':
    main(sys.argv[1:])
