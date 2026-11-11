# Finite closures and auxiliary catalogs

The [supplement](../supplement/main.pdf) proves the constructions described here. Notation for the graph families is recalled in [results and notation](results.md). The identifiers `G14a`, `G14b` and `G14c` denote the three I-contractible stuck K4-free graphs of order 14.

## Admissible-edge closures

Starting from a graph outside $\mathfrak I_S$, add each missing edge whose common neighbourhood belongs to $\mathfrak I_S$. Identify isomorphic graphs and continue from the non-strong results. Record a strong result on the **first-strong boundary** and stop expanding it. This is the pruned edge-addition closure.

The procedure terminates because each addition increases the edge count on a fixed vertex set. Its pruning rule follows from the definition of $\mathfrak I_S$: adding an admissible edge to a strong graph leaves a strong graph, since deleting that edge recovers the original one. Thus every path ending outside $\mathfrak I_S$ stays outside that class at every intermediate step. Exploring every admissible edge, with exact membership and isomorphism tests, finds all non-strong descendants and their first-strong boundary.

| Seed | Non-strong classes | First-strong boundary | K4-free non-strong classes |
|---|---:|---:|---:|
| `G14a` | 16 | 32 | 4 |
| `G14b` | 10 | 16 | 3 |
| `G14c` | 5 | 8 | 1 |

The non-strong sets overlap up to isomorphism, so their union has 29 classes. All belong to $\mathfrak I$: the seeds have I-contractibility certificates and admissible additions preserve membership. Eight are K4-free and 21 contain a K4. Each of the 32 boundary classes for `G14a` has an admissible edge deletion leaving the strong class. The boundary counts first entries into the strong class along these paths.

[`small_closure_certificates.json`](../finite/data/small_closure_certificates.json) gives the complete three closures. Each graph in [`K4_free_I_not_strong_14.tsv`](../finite/data/K4_free_I_not_strong_14.tsv) has a seed, an ordered addition path and a certifying edge. The finite reproduction route reconstructs these closures.

## The union from all 51 seeds

The 51 stuck K4-free graphs of order 14 generate **2,271 non-strong isomorphism classes**. The three I-contractible seeds contribute the 29 classes above. The other 48 seeds have first integral homology $\mathbb Z/3$; admissible additions preserve homology, so their 2,242 distinct descendants lie outside $\mathfrak I$.

The union contains 277 K4-free classes: eight in $\mathfrak I$ and 269 with first homology $\mathbb Z/3$. These lie among the 633 K4-free acyclic non-strong graphs of order 14 in the table. The remaining 356 are outside this seed-generated union. Accordingly, the catalog classifies the specified closures; it is not an enumeration of all acyclic non-strong graphs of order 14.

The full union and its I-contractible subset are in [`acyclic_not_strong_14_closure.tsv`](../finite/data/acyclic_not_strong_14_closure.tsv) and [`I_not_strong_14_closure.tsv`](../finite/data/I_not_strong_14_closure.tsv). Each row records a seed, an admissible path and first-homology invariants. [Closure regeneration](../verification/closures51/README.md) gives the command that reconstructs the complete union.

## Natural unfoldings

Take a separate triangle for each triangle of a seed's clique complex. Glue pairs of triangle edges precisely when the original edge belongs to two triangles, preserving endpoint labels. The result is the **natural unfolding**. The supplement proves how to recover its components, vertex links and boundary words from this gluing.

The 51 unfoldings consist of 48 discs, two annuli, and one disc together with an annulus. The three I-contractible seeds have disc unfoldings; the other 45 discs acquire torsion after their boundary identifications. [`unfolding_components.json`](../finite/data/unfolding_components.json) records the components and their local surface checks.

## Strictly 2-dismantlable graphs

[`strictly_2dis_12.tsv`](../finite/data/strictly_2dis_12.tsv) lists the 20 isomorphism classes in $2$-Dis outside $1$-Dis at order 12. Exact recursive tests verify membership and nonmembership for each graph. Given the table, the difference of the corresponding columns proves completeness, and their equality at smaller orders gives minimality. Degree bounds, clique counts and automorphism-group orders are included as catalog invariants.

## Earlier examples

[`D15_label_correspondence.tsv`](../finite/data/D15_label_correspondence.tsv) identifies `D15` with the graph in Figure 2A of [Dochtermann et al. (2023)](https://doi.org/10.1016/j.disc.2023.113516). The comparison uses all 32 triangles after relabelling, together with the certifying edge. The supplement gives its disc presentation and strong reduction after that edge is added.

Four eleven-vertex examples from Adamaszek's torsion classification are retained in [`adamaszek_11_graphs.g6`](../finite/data/adamaszek_11_graphs.g6), with [attribution and first-homology data](../finite/data/adamaszek_11_homology.json). Their first integral homology is $\mathbb Z/2$. The finite check concerns these four examples; the classification theorem is taken from the cited work.
