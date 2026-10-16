"""Independent check (Ripser, no Smith normal form): Betti numbers of the clique complex with Z/2 and Z/3
coefficients for every graph6 line of a file.  The clique complex is the Vietoris-Rips complex of the
graph metric at scale 1 (edges at distance 1, non-edges at 2); bars alive at scale 1 = homology.
A graph with H~1(Z) = Z/3 must give b1 = b2 = 1 over Z/3 and 0 over Z/2; a contractible one gives 0.
Usage: python tools/ripser_z3_check.py file.g6   (requires: pip install ripser networkx)"""
