#!/usr/bin/env python3
"""Integer and Z/2 homology of the clique (flag) complex of a graph given in graph6.

Usage:  python3 clique_homology.py  [file.g6 | -]      (one graph6 string per line, '#' comments ignored)
        python3 clique_homology.py --g6 'M?b@bFHNEk@~|k}U?'

For each graph it prints: n, m, #triangles, #K4, reduced Betti numbers over Z/2,
and the integer reduced homology groups (free rank + torsion coefficients) of the
clique complex in every dimension.  Pure Python (no dependencies); the Smith normal
form is computed exactly over the integers, so odd torsion (e.g. Z/3) is detected.
"""
import sys, itertools

def parse_g6(s):
    s = s.strip()
    if s.startswith('>>graph6<<'): s = s[10:]
    data = [ord(c) - 63 for c in s]
    if data[0] == 63:
        n = (data[1] << 12) | (data[2] << 6) | data[3]; data = data[4:]
    else:
        n = data[0]; data = data[1:]
    bits = []
    for d in data:
        bits.extend([(d >> k) & 1 for k in range(5, -1, -1)])
    adj = [set() for _ in range(n)]
    i = 0
    for v in range(1, n):
        for u in range(v):
            if bits[i]: adj[u].add(v); adj[v].add(u)
            i += 1
    return n, adj

def cliques(n, adj, kmax=None):
    """All cliques, grouped by size (list of lists of tuples)."""
    out = {1: [(v,) for v in range(n)]}
    k = 1
    while True:
        nxt = []
        for c in out[k]:
            cand = set(range(c[-1] + 1, n))
            for v in c: cand &= adj[v]
            for v in sorted(cand): nxt.append(c + (v,))
        if not nxt: break
        k += 1; out[k] = nxt
        if kmax and k >= kmax: break
    return out

def boundary(C, k, index):
    """Boundary matrix from k-simplices (size k+1) to (k-1)-simplices, as dict rows."""
    rows = []
    for c in C.get(k + 1, []):
        row = {}
        for i in range(len(c)):
            face = c[:i] + c[i + 1:]
            row[index[face]] = (-1) ** i
        rows.append(row)
    return rows  # rows indexed by k-simplices, columns by (k-1)-simplices

def smith_diagonal(rows, ncols):
    """Nonzero diagonal entries of the Smith normal form of a sparse integer matrix."""
    # Dense elimination over Z (matrices here are small: < 200 x 200).
    M = [[0] * ncols for _ in rows]
    for i, r in enumerate(rows):
        for j, v in r.items(): M[i][j] = v
    nr = len(M); diag = []
    r = 0; c = 0
    while r < nr and c < ncols:
        # find pivot with smallest |value| in submatrix
        piv = None
        for i in range(r, nr):
            for j in range(c, ncols):
                if M[i][j] and (piv is None or abs(M[i][j]) < abs(M[piv[0]][piv[1]])):
                    piv = (i, j)
                    if abs(M[i][j]) == 1: break
            if piv and abs(M[piv[0]][piv[1]]) == 1: break
        if piv is None: break
        i, j = piv
        M[r], M[i] = M[i], M[r]
        for row in M: row[c], row[j] = row[j], row[c]
        while True:
            p = M[r][c]; done = True
            for i in range(r + 1, nr):
                if M[i][c]:
                    q = M[i][c] // p
                    if q:
                        Mi, Mr = M[i], M[r]
                        for j in range(c, ncols):
                            if Mr[j]: Mi[j] -= q * Mr[j]
                    if M[i][c]:
                        M[r], M[i] = M[i], M[r]; done = False; break
            if not done: continue
            for j in range(c + 1, ncols):
                if M[r][j]:
                    q = M[r][j] // p
                    if q:
                        for i in range(r, nr):
                            if M[i][c]: M[i][j] -= q * M[i][c]
                    if M[r][j]:
                        for row in M: row[c], row[j] = row[j], row[c]
                        done = False; break
            if done: break
        diag.append(abs(M[r][c])); r += 1; c += 1
    # fix divisibility chain (only matters for presenting torsion coefficients)
    from math import gcd
    changed = True
    while changed:
        changed = False
        for a in range(len(diag)):
            for b in range(a + 1, len(diag)):
                if diag[a] and diag[b] % diag[a]:
                    g = gcd(diag[a], diag[b]); l = diag[a] * diag[b] // g
                    diag[a], diag[b] = g, l; changed = True
    return diag

def homology(n, adj):
    C = cliques(n, adj)
    dims = max(C)  # largest clique size
    index = {k: {c: i for i, c in enumerate(C[k])} for k in C}
    # reduced: augment with the empty simplex in dimension -1
    res = {}
    diags = {}
    for k in range(0, dims):          # boundary d_k : C_k -> C_{k-1}, k = dim
        if k == 0:
            diags[0] = [1] if n > 0 else []     # augmentation map to Z
        else:
            diags[k] = smith_diagonal(boundary(C, k, index[k]), len(C[k]))
    for k in range(0, dims):
        ck = len(C[k + 1])
        rank_dk = len(diags[k])
        rank_dk1 = len(diags.get(k + 1, []))
        free = ck - rank_dk - rank_dk1
        tors = [d for d in diags.get(k + 1, []) if d > 1]
        res[k] = (free, tors)
    return C, res

def betti_mod2(C, res):
    out = []
    for k, (free, tors) in sorted(res.items()):
        b = free + sum(1 for t in tors if t % 2 == 0)
        # torsion in H_{k-1} with even coefficient also contributes to H_k(Z/2)
        if k - 1 in res: b += sum(1 for t in res[k - 1][1] if t % 2 == 0)
        out.append(b)
    return out

def fmt(res):
    parts = []
    for k, (free, tors) in sorted(res.items()):
        s = ' + '.join(['Z'] * free + [f'Z/{t}' for t in tors]) or '0'
        parts.append(f'H~{k}={s}')
    return '  '.join(parts)

def main(argv):
    lines = []
    if len(argv) >= 2 and argv[0] == '--g6': lines = [argv[1]]
    else:
        f = sys.stdin if not argv or argv[0] == '-' else open(argv[0])
        lines = [l.split()[0] for l in f if l.strip() and not l.startswith('#')]
    for s in lines:
        n, adj = parse_g6(s)
        C, res = homology(n, adj)
        m = len(C.get(2, [])); t = len(C.get(3, [])); k4 = len(C.get(4, []))
        acyclic = all(f == 0 and not tors for f, tors in res.values())
        print(f'{s}  n={n} m={m} tri={t} K4={k4}  Z2-betti={betti_mod2(C,res)}  {fmt(res)}  '
              f'{"Z-acyclic" if acyclic else "NOT Z-acyclic"}')

if __name__ == '__main__':
    main(sys.argv[1:])
