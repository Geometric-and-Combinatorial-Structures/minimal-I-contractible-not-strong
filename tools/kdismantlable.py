#!/usr/bin/env python3
"""Exact k-dismantlability test (Fieux–Jouve; Dochtermann et al. 2023, Def. 10), pure Python.

A vertex v is (-1)-dismantlable if N(v) is the whole rest of the graph (G is a cone with apex v);
0-dismantlable if N(v) is a cone; k-dismantlable (k >= 1) if N(v) is (k-1)-dismantlable.
G is k-dismantlable (k-Dis) if it can be reduced to K_1 by deleting k-dismantlable vertices.

Usage: python3 kdismantlable.py file.g6 [--k 3] [--trace]   prints, per graph, the smallest k in {-1,0,1,2,3} with G in k-Dis (or '>3');
       --trace adds an explicit k-dismantling sequence (vertex labels of the graph6 string).
"""
import sys
from functools import lru_cache
sys.setrecursionlimit(10000)

def parse_g6(s):
    s = s.strip()
    if s.startswith('>>graph6<<'): s = s[10:]
    data = [ord(c) - 63 for c in s]
    n = data[0]; data = data[1:]
    bits = []
    for d in data: bits.extend([(d >> k) & 1 for k in range(5, -1, -1)])
    adj = [0] * n; i = 0
    for v in range(1, n):
        for u in range(v):
            if bits[i]: adj[u] |= 1 << v; adj[v] |= 1 << u
            i += 1
    return n, tuple(adj)

def make(adj):
    def nb(v, m): return adj[v] & m
    def is_cone(m):
        if m & (m - 1) == 0: return True
        t = m
        while t:
            v = (t & -t).bit_length() - 1; t &= t - 1
            if nb(v, m) == m ^ (1 << v): return True
        return False
    @lru_cache(maxsize=None)
    def kdis(m, k):
        if m == 0: return False
        if m & (m - 1) == 0: return True
        if k == -1: return is_cone(m)
        t = m
        while t:
            v = (t & -t).bit_length() - 1; t &= t - 1
            link = nb(v, m)
            if link and kdis(link, k - 1) and kdis(m ^ (1 << v), k): return True
        return False
    def trace(m, k):
        """A k-dismantling sequence of G[m] (list of (vertex, link-as-tuple)), or None."""
        if m == 0: return None
        if m & (m - 1) == 0: return []
        t = m
        while t:
            v = (t & -t).bit_length() - 1; t &= t - 1
            link = nb(v, m)
            if link and kdis(link, k - 1) and kdis(m ^ (1 << v), k):
                rest = trace(m ^ (1 << v), k)
                return [(v, tuple(i for i in range(len(adj)) if link >> i & 1))] + rest
        return None
    kdis.trace = trace
    return kdis

def main(argv):
    kmax = 3
    if '--k' in argv: kmax = int(argv[argv.index('--k') + 1])
    files = [a for a in argv if not a.startswith('--') and not a.isdigit()]
    f = open(files[0]) if files else sys.stdin
    for line in f:
        if not line.strip() or line.startswith('#'): continue
        s = line.split()[-1] if ' ' in line.strip() else line.strip()
        n, adj = parse_g6(s); kdis = make(adj); full = (1 << n) - 1
        best = next((k for k in range(-1, kmax + 1) if kdis(full, k)), None)
        print(f'{s}  n={n} m={sum(bin(a).count("1") for a in adj)//2}  smallest k with G in k-Dis: {best if best is not None else ">%d" % kmax}')
        if '--trace' in argv and best is not None and best >= 0:
            for i, (v, link) in enumerate(kdis.trace(full, best), 1):
                print(f'  {i:2d}. delete vertex {v}  (link {{{",".join(map(str, link))}}} is {best-1}-dismantlable)')

if __name__ == '__main__':
    main(sys.argv[1:])
