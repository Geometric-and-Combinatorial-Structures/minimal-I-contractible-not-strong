# Historical classifier `atascadas.c`

Retained solely as a regression comparison implementation. Use `../v2/src/atascadas_v2.c` for new enumeration. The v1 memoization defect below is part of the reason for retaining regression tests; this program is not the production classifier of the present table.

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
| `cerradura` | Enumerates the pruned I₄-closure: starting from the input graph it repeatedly adds edges uv with N(u,v) ∈ 𝔍_S and expands only graphs outside 𝔍_S (a graph in 𝔍_S is reported but not expanded, since further additions stay in 𝔍_S), reporting the 𝔍_S status of each (labelled graphs; isomorphism reduction is done afterwards with `nauty`'s `labelg`/`shortg`). |
| `traza` | Prints an explicit deletion sequence (vertices with N(v) ∈ 𝔍_S, edges with N(u,v) ∈ 𝔍_S) down to K₁ for graphs in 𝔍_S. |
| `icert [--prof d]` | Searches breadth-first for ≤ d additions of I₄ edges leading to a graph in 𝔍_S; this certifies I-contractibility. |

Deciders: 𝔍_VS and k-Dis by exact dynamic programming over vertex subsets (bitmasks); 𝔍_S by backtracking over the
deletion tree with a memo that, in this historical version, identifies a subproblem by a 63-bit hash only (finding H-01
of the external audit: a collision could in principle return a wrong answer; none has been observed).
`v2/src/atascadas_v2.c` stores and compares the full key, and the later complete recomputations used that version.  ℤ/2 homology by Gaussian elimination over GF(2) on the clique complex.

Compile with `gcc -O3 -o atascadas atascadas.c -lm` (add `-march=native` only if every node that runs the binary has the same CPU).

Conventions (as in Dochtermann–Espinoza–Frías-Armenta–Hernández 2023): open neighbourhoods; the empty graph is
**not** in 𝔍_S; "acyclic" means vanishing reduced ℤ/2 homology of the clique complex in all degrees (so acyclic graphs
are connected).

The header comment of the file contains the reduction lemmas (in Spanish) that justify the `geng` restrictions
`-C -d4 -D(n-2)` used on the cluster; the paper states and proves them in English.

The original archived `yuca/as_run/` tree is not redistributed in this selection. Selected provenance records are in `../finite/provenance/`.
