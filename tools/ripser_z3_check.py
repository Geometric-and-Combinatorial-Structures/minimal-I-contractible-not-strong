"""Independent check (Ripser, no Smith normal form): Betti numbers of the clique complex with Z/2 and Z/3
coefficients for every graph6 line of a file.  The clique complex is the Vietoris-Rips complex of the
graph metric at scale 1 (edges at distance 1, non-edges at 2); bars alive at scale 1 = homology.
A graph with H~1(Z) = Z/3 must give b1 = b2 = 1 over Z/3 and 0 over Z/2; a contractible one gives 0.
Usage: python tools/ripser_z3_check.py file.g6 [--each]   (requires: pip install ripser networkx)"""
import sys, collections
import numpy as np, networkx as nx
from ripser import ripser

def betti(G, p):
    n = G.number_of_nodes()
    D = np.full((n, n), 2.0); np.fill_diagonal(D, 0.0)
    for u, v in G.edges(): D[u, v] = D[v, u] = 1.0
    dg = ripser(D, distance_matrix=True, maxdim=2, coeff=p, thresh=1.0)['dgms']
    return tuple(int(np.sum(np.isinf(d[:, 1]))) for d in dg)   # (b0, b1, b2) of the clique complex

def main(path, each=False):
    res = collections.Counter()
    for line in open(path):
        g6 = line.strip()
        if not g6 or g6.startswith('#'): continue
        G = nx.from_graph6_bytes(g6.encode())
        k = (betti(G, 2), betti(G, 3))
        res[k] += 1
        if each: print(g6, 'Z2', k[0], 'Z3', k[1])
    for (b2, b3), v in sorted(res.items()):
        print(f"{v} graph(s): Betti over Z/2 (b0,b1,b2) = {b2}   over Z/3 = {b3}")

if __name__ == '__main__':
    main(sys.argv[1], '--each' in sys.argv)
