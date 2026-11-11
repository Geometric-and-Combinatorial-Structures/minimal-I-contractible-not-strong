# How the results are verified

The results combine three kinds of evidence. **Mathematical arguments** establish the algorithms and deductions. **Finite checks** reconstruct the supplied graphs, reductions and homology calculations. **Enumeration records** give the counts and complete partitions of the larger graph universes. The command `python3 reproduce.py` runs the finite checks and compares the recorded numerical sources; [full enumeration](full-reproduction.md) regenerates the graph universes.

The large enumerations and their recomputations use versions of the project's classifier; they are not independent implementations. The finite verifier uses separate recurrences and homology calculations. These provide checks on the supplied objects, not an independent recount of every graph in the large universes. The repository contains selected aggregate records and all the finite exceptional graphs; the complete historical per-residue archives are outside this selection.

## Counterexamples and finite constructions

| Result | Mathematical argument | Finite calculation |
|---|---|---|
| The order-13 torsion examples | Disc attachment of degree three and the universal coefficient theorem | Disc hypotheses, exact integral first homology and identification of the three variants |
| `G14a`, `G14b`, `G14c` lie in $\mathfrak I\setminus\mathfrak I_S$ | One-edge extensions and obstruction to every first strong deletion | All neighbourhoods and every step of the reduction sequences |
| Eight K4-free order-14 classes, minimum 44 edges | Reduction to a stuck seed and exhaustive pruned closure | Three K4-free closure sets of sizes 4, 3 and 1, identified with the eight enumeration positives |
| The 2,271-class closure union | Closure algorithm and homology preservation under additions | Every stored path, non-strong status, integral first homology and pairwise nonisomorphism; full 51-seed regeneration |
| The 51 natural unfoldings | Triangle gluing and local surface criterion | Every corner identification, component, vertex link and boundary word |
| The 20 strictly 2-dismantlable graphs | Table difference and nested-family inclusions | Membership, nonmembership, pairwise nonisomorphism and automorphism orders |

The [certificate index](../finite/certificates/README.md) and [catalog dictionary](../finite/data/README.md) identify the data and individual checks. The three I-contractible seed closures are reconstructed by the finite route. [Regeneration of all 51 closures](../verification/closures51/README.md) uses the enumeration classifier and nauty to compare the complete 2,271-class set. Of these classes, 277 occur in the table's 633 K4-free acyclic non-strong exceptions, leaving 356 outside the closure union.

## The cardinality table

All rows count connected isomorphism classes. Orders 3–13 include all connected graphs; **every column at order 14 is K4-free**. The statement numbers below refer to the [article](../paper/main.pdf); the accompanying labels locate them in its [LaTeX sources](../paper/).

| Rows or assertion | Retained evidence | What the finite route checks |
|---|---|---|
| Table 1 (`tab:card`), orders 3–9 | `finite/provenance/small_order_counts.json`: comparison of two implementations on 273,191 graphs | Source identities, recorded counts and table transcription; the individual comparison rows are not distributed |
| Table 1 (`tab:card`), order 10 | `separate_order10_census.txt` and command log in `finite/provenance/` | Counts and successful-exit records; source attribution and the conditional code-path argument are detailed in [small-order provenance](small-order-provenance.md) |
| Table 1 (`tab:card`), order 11 | `exact_n11_summary.json` and four residue records; retained instrumented complete-state source | The four sums, successful exits, source correspondence and counts |
| Table 1 (`tab:card`), orders 12–14 | `data/census/F2_12_aggregate.json`, `F2_13_aggregate.json`, `F4_aggregate.json` | Aggregate coverage fields, all raw counters and all mathematical table entries |
| Theorem 5.1 (`thm:classification13`) | Lower-order rows, three order-13 residuals and the explicit examples | Isomorphism with the three variants, nonzero integral homology, and their vertex and edge neighbourhoods |
| Theorem 5.2 (`thm:classification14`), 51 seeds | `F3_aggregate.json`, `F3_stuck.g6` and the seed catalog | All 51 graphs, the 48 torsion cases and three positive certificates; agreement with the stuck subset of the 633 table14 exceptions |
| Proposition 5.3 (`prop:table-integral`) | All three order-13 and 625 order-14 residuals, their homology records and eight positive classes | Exact integral first homology, pairwise nonisomorphism and correspondence of the seed and residual sets |

The seeds are generated with the degree and connectivity restrictions justified by the article's reduction lemmas. The proof also uses the absence of almost-stuck graphs in the [643 connected K4-free classes of orders 2–7](../data/local_K4/README.md). Their generator record supplies enumeration coverage; their finite checker tests every graph, including the case with no admissible vertex. The full order-14 table uses only connectedness and K4-freeness, without the additional seed filters.

### The integral column

The 628 residual graphs are connected and K4-free, have Euler characteristic one, and have exact integral first homology $\mathbb Z/3$. Their clique complexes have dimension at most two. Second homology is free, and Euler characteristic forces its rank to vanish; hence all other reduced integral homology is zero.

The classification partitions every $\mathbb F_2$-acyclic non-strong graph in the stated universes into a graph with a positive I-contractibility certificate or one of these torsion cases. Together with

$$\mathfrak I_S\subseteq\mathfrak I\subseteq\mathcal A_{\mathbb Z}\subseteq\mathcal A_{\mathbb F_2},$$

this determines the I and integral-acyclicity columns. A failed bounded search remains unresolved until a certificate or obstruction is supplied. The exhaustive partitions come from the enumeration and the article's reduction arguments; the finite route recalculates the recorded exceptional graphs.

### Minimum orders and consistency relations

Corollary 5.4 (`cor:minimality`) combines the explicit examples with the unrestricted classification through order 13. It gives global minimum orders 13 and 14, including the admissible-edge deletion property. The eight classes and the minimum 44 edges remain restricted to K4-free order-14 graphs.

The minimum of 14 vertices for a contractible, non-collapsible flag complex uses the same lower-order classification. Contractibility implies I-contractibility by Dochtermann–Matsushita; through order 13 the graph is strong; strong I-contractibility implies collapsibility by Espinoza–Frías-Armenta–Hernández-Hernández. The clique complex of `G14a` attains the bound: every edge lies in at least two triangles and every vertex lies in a triangle, so there is no free face (article, Proposition 3.5). The [bibliography guide](bibliography.md) gives the references.

Nested-family inclusions determine the 2-Dis and 3-Dis entries through order 11 from the equal 1-Dis and $\mathfrak I_{SV}$ counts. In the K4-free universe these four families coincide by the tree-neighbourhood criterion. The cone column follows from the bijection obtained by adjoining a universal vertex. The [small-order note](small-order-provenance.md) explains these consistency relations and the source dependence of the Euler-characteristic column.

## Checks of the programs and distributed files

The optional [recurrence comparison](../verification/current_recurrences/README.md) evaluates the C classifier and direct recurrences on all 1,100 labelled graphs of orders 0–5 and their 33,867 induced states. It includes every first deletion, empty and singleton graphs, disconnected states and empty neighbourhoods. The large-order distinctions between the classes are checked by their separate example certificates.

`reproduce.py` also checks document identity, import records, local links, generated mathematical tables, witness exports and notebook cells. Mutation tests deliberately alter disc degrees, membership flags and input bytes. The file inventories detect changes to the distributed inputs; the mathematical verifiers reconstruct and test the objects those inputs represent.

The [reproduction guide](reproduction.md) gives the required commands. Historical computations and executable identities are indexed in [`finite/provenance/`](../finite/provenance/README.md).
