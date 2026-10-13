# `atascadas.c`

Single-file C program (C99, no dependencies) that reads graphs in graph6 format from standard input, one per line
(typically piped from `geng`), and runs in one of the following modes (`--modo <mode>`).  The vocabulary in the
source is Spanish: *atascada* = stuck, *acíclica* = ℤ/2-acyclic, *vecindad* = neighbourhood, *pegado* = edge addition,
*borrado* = deletion, *cerradura* = closure, *traza* = trace, *rebanada* = slice.

| mode | purpose |
|---|---|
| `atascadas` (default) | Prints the graphs that are ℤ/2-acyclic and **stuck**: every open neighbourhood N(v) is non-acyclic and every common neighbourhood N(u,v) of an edge is empty or non-acyclic. Implements the filter cascade cone → Euler characteristic → neighbourhoods → edges → ℤ/2 homology. This is the mode run on the cluster. |
| `casi` | Prints `g6 u` for ℤ/2-acyclic graphs with exactly one vertex u whose neighbourhood is acyclic and all edges stuck ("almost-stuck" pieces, the building blocks of a stuck graph with a cut vertex). Used to prove 2-connectivity of minimal counterexamples. |
| `tabla` | Counts, for the input stream: connected graphs, χ = 1, ℤ/2-acyclic, 𝔍 (I-contractible: 𝔍_S or certified by ≤ 3 I₄ additions; undecided acyclic graphs are counted separately as `I_indecisas`), 𝔍_S, 𝔍_VS, 3-, 2-, 1-, 0- and (−1)-dismantlable. Output goes to standard error as a single line `n=… conexas=… …`. |
| `verificar` | Detailed report for each input graph: χ, connectivity, ℤ/2 Betti numbers, every N(v) and N(u,v) with its status, counts of deletable vertices/edges, membership in 0-Dis, 𝔍_VS, 𝔍_S, and whether the graph is stuck. |
| `cerradura` | Enumerates all supergraphs obtained by repeatedly adding edges uv with N(u,v) ∈ 𝔍_S (the I₄-closure), reporting the 𝔍_S status of each (labelled graphs; isomorphism reduction is done afterwards with `nauty`'s `labelg`/`shortg`). |
| `traza` | Prints an explicit deletion sequence (vertices with N(v) ∈ 𝔍_S, edges with N(u,v) ∈ 𝔍_S) down to K₁ for graphs in 𝔍_S. |
| `icert [--prof d]` | Searches breadth-first for ≤ d additions of I₄ edges leading to a graph in 𝔍_S; this certifies I-contractibility. |

Exact deciders: 𝔍_S by memoised backtracking over the deletion tree; 𝔍_VS and k-Dis by dynamic programming over
vertex subsets (bitmasks). ℤ/2 homology by Gaussian elimination over GF(2) on the clique complex.

Compile with `gcc -O3 -march=native -o atascadas atascadas.c -lm`.

Conventions (as in Dochtermann–Espinoza–Frías-Armenta–Hernández 2023): open neighbourhoods; the empty graph is
**not** in 𝔍_S; "acyclic" means vanishing reduced ℤ/2 homology of the clique complex in all degrees (so acyclic graphs
are connected).

The header comment of the file contains the reduction lemmas (in Spanish) that justify the `geng` restrictions
`-C -d4 -D(n-2)` used on the cluster; the paper states and proves them in English.

`yuca/as_run/` keeps the exact versions compiled for each cluster run (SHA-256 recorded in `yuca/README.md`); the
version here is a superset (additional modes `cerradura`, `traza`, `icert` and extra table columns).
