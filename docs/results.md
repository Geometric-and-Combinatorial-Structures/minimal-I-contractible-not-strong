# Results, notation and proofs

The [article](../paper/main.pdf) establishes the counterexamples and the cardinality table. The [supplement](../supplement/main.pdf) develops the finite constructions extending those results. This guide relates their mathematical statements to the data in the repository.

## Graph classes

All graphs are finite and simple. The clique complex of $G$ consists of its cliques. Homology of a graph refers to that complex; acyclicity means vanishing reduced homology in every degree, with coefficients specified.

Write $N_G(v)$ for the induced open neighbourhood and $N_G(u,v)$ for the induced common neighbourhood. The class $\mathfrak I_S$ contains $K_1$, excludes the empty graph and, for a graph $G$ of order at least two, is defined recursively by

$$G\in\mathfrak I_S\quad\Longleftrightarrow\quad
\bigl(N_G(v),G-v\in\mathfrak I_S\text{ for some }v\bigr)
\ \text{or}\ \bigl(N_G(u,v),G-uv\in\mathfrak I_S\text{ for some }uv\in E(G)\bigr).$$

The I-contractible class $\mathfrak I$ is the least class containing $K_1$ and closed under vertex and edge additions and deletions whose tested neighbourhood lies in $\mathfrak I$. An operation is **admissible** here when its tested neighbourhood lies in $\mathfrak I_S$. Write $\mathfrak I_{SV}$ for the strong class defined by the same recursion with vertex deletions only.

A cone has a vertex adjacent to all other vertices. Cones form $(-1)$-Dis. For $k\geq0$, a vertex is $k$-dismantlable when its open neighbourhood belongs to $(k-1)$-Dis; a graph belongs to $k$-Dis if successive such deletions reduce it to one vertex. The empty graph belongs to none of these classes.

These families satisfy

$$(-1)\text{-Dis}\subseteq0\text{-Dis}\subseteq1\text{-Dis}\subseteq\cdots\subseteq\mathfrak I_{SV}\subseteq\mathfrak I_S\subseteq\mathfrak I.$$

A graph is I-contractible exactly when its clique complex is contractible ([Dochtermann–Matsushita, Corollary 1.5](https://arxiv.org/abs/2312.10976v2)). Strong I-contractibility implies simplicial collapsibility ([Espinoza–Frías-Armenta–Hernández-Hernández, Theorem 1](https://doi.org/10.1007/s40590-022-00434-7)). Consequently,

$$\mathfrak I_S\subseteq\mathfrak I\subseteq\mathcal A_{\mathbb Z}\subseteq\mathcal A_{\mathbb F_2},$$

where $\mathcal A_R$ denotes the graphs acyclic over $R$.

A **stuck graph** has at least two vertices, is $\mathbb F_2$-acyclic and admits no admissible vertex or edge deletion. Starting from a non-strong graph, add every admissible missing edge and identify isomorphic results. Stop expanding a graph when it becomes strong. The resulting **pruned closure** consists of its non-strong descendants and their **first-strong boundary**.

## Counterexamples and minimum orders

The graph `G13` and its two variants, obtained by adding $\{4,7\}$ and then $\{5,6\}$, have first integral homology $\mathbb Z/3$ and vanishing reduced homology over $\mathbb F_2$. They are the only $\mathbb F_2$-acyclic graphs outside $\mathfrak I_S$ through order 13. Their nonzero integral homology excludes them from $\mathfrak I$.

The graphs `G14a`, `G14b` and `G14c` belong to $\mathfrak I\setminus\mathfrak I_S$. Each has an admissible one-edge extension in $\mathfrak I_S$. The [examples guide](examples.md) describes their certificates. These constructions refute the two assertions of Conjecture 14 and the minimum proposed in Conjecture 15 of [Dochtermann et al. (2023)](https://doi.org/10.1016/j.disc.2023.113516).

| Minimum | Order | Basis of the result |
|---|---:|---|
| $\mathbb F_2$-acyclic graph outside $\mathfrak I_S$ | 13 | The three torsion graphs and the lower-order classification |
| Graph in $\mathfrak I\setminus\mathfrak I_S$ | 14 | The explicit example and the classification through order 13 |
| Integrally acyclic graph outside $\mathfrak I_S$ | 14 | `G14a`, the lower-order classification and the torsion of the three order-13 exceptions |
| Strong graph with an admissible edge deletion leaving the strong class | 14 | The extension of `G14a` and the preceding lower bound |
| Contractible, non-collapsible flag complex | 14 vertices | The clique complex of `G14a` has no free face; the lower-order classification gives minimality |

Every edge of the clique complex of `G14a` lies in at least two triangles, and every vertex lies in a triangle. There is therefore no free face with which to start a collapse (article, Proposition 3.5).

All these minima are global. The eight isomorphism classes and minimum of 44 edges describe the narrower class of **K4-free order-14 graphs** in $\mathfrak I\setminus\mathfrak I_S$.

## The table and its coefficient columns

[`cardinalities.csv`](../data/cardinalities.csv) counts connected graphs up to isomorphism. Rows 3–13 are unrestricted; every column of row 14 is K4-free. The article proves the recursive membership tests, enumeration up to isomorphism and the reduction lemmas used in the classification.

The CSV has twelve count columns in addition to order and universe:

| Column | Family counted |
|---|---|
| `connected` | All graphs in the row's connected universe |
| `chi1` | Graphs whose clique complex has Euler characteristic one |
| `acyclic_F2`, `acyclic_Z` | Acyclic graphs over $\mathbb F_2$ and $\mathbb Z$, respectively |
| `I`, `I_S`, `I_SV` | The three contractible classes defined above |
| `3_Dis`, `2_Dis`, `1_Dis`, `0_Dis` | The corresponding dismantling levels |
| `cones` | $(-1)$-Dis |

Deleting a universal vertex identifies cones of order $n$ up to isomorphism with arbitrary graphs of order $n-1$. In the K4-free row, those graphs must be triangle-free.

Within each classified universe, the $\mathbb F_2$-acyclic graphs outside $\mathfrak I_S$ split into a set $P$ with positive I-contractibility certificates and a residual set $R$ whose members all have first integral homology $\mathbb Z/3$. Thus

$$\mathcal A_{\mathbb F_2}=\mathfrak I_S\sqcup P\sqcup R,\qquad
\mathcal A_{\mathbb Z}=\mathfrak I=\mathfrak I_S\sqcup P.$$

The second equality follows because the members of $\mathfrak I$ have contractible clique complexes, while the graphs in $R$ have nonzero integral homology. The difference between the two acyclicity columns is therefore $|R|$: three at order 13 and 625 in row 14. These residuals have no other reduced integral homology. The [verification map](verification-scope.md) identifies the finite calculations and enumeration records establishing the partition.

The classification of the eight K4-free order-14 graphs proceeds through the stuck seeds. The reduction lemmas restrict those seeds to biconnected graphs with $4\leq\delta\leq\Delta\leq12$. Their enumeration gives 51 classes; exactly three, `G14a`, `G14b` and `G14c`, are I-contractible. Every K4-free graph of order 14 in $\mathfrak I\setminus\mathfrak I_S$ reduces by admissible edge deletions to one of these three. Their K4-free non-strong admissible-edge closures contain respectively four, three and one classes. These three sets are pairwise disjoint up to isomorphism, giving the eight graphs.

## Complementary finite constructions

There are 51 stuck K4-free graphs of order 14. The supplement studies their pruned closures and proves the stopping rule and exhaustiveness of the procedure on its stated search space.

| Construction | Result | Mathematical treatment and data |
|---|---|---|
| Closures of `G14a`, `G14b`, `G14c` | Non-strong/first-strong counts 16/32, 10/16 and 5/8; non-strong union of size 29 | Supplement: closure algorithm; [closure catalogs](secondary-results.md) |
| Non-strong closures of all 51 seeds | 2,271 classes: 29 in $\mathfrak I$, 2,242 with first homology $\mathbb Z/3$ | Supplement: catalog proof; [data dictionaries](../finite/data/README.md) |
| Natural unfoldings of the 51 seeds | 48 discs, two annuli, one disc together with an annulus | Supplement: triangle gluing and surface recognition |
| Strictly 2-dismantlable graphs (in $2$-Dis outside $1$-Dis) of order 12 | Exactly 20 classes | Table and supplement: catalog argument |
| Earlier 15-vertex example `D15` | Label correspondence, disc presentation and one-edge certificate | Supplement: comparison with the earlier construction |

The 2,271 classes form the specified seed-generated union. Its 277 K4-free members lie among the 633 K4-free acyclic non-strong graphs in the table; the remaining 356 are outside these closures. The classification of the eight K4-free graphs in $\mathfrak I\setminus\mathfrak I_S$ uses the three positive-seed closures and the article's reduction theorem.

To calculate these finite objects, start with [reproduction](reproduction.md). To generate all graphs counted by a table row, use [full enumeration](full-reproduction.md).
