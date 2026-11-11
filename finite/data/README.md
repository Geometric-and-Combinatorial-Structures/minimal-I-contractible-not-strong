# Catalogs and data fields

The catalogs describe the finite constructions in the [supplement](../../supplement/main.pdf). TSV files have one header row. Graph6 strings determine vertex labels, starting at zero. A boundary word is cyclic: its final vertex is followed by its first. [Results and notation](../../docs/results.md) defines the graph families; [finite closures](../../docs/secondary-results.md) explains their construction and scope.

## The 51 stuck graphs and their unfoldings

[`stuck_14_K4free.tsv`](stuck_14_K4free.tsv) lists the 51 stuck K4-free graphs of order 14.

| Field | Meaning |
|---|---|
| `H1_Z` | Integral first homology; `trivial` denotes zero |
| `I_certificate_edge` | `yes ({u,v})` gives a missing edge whose addition certifies I-contractibility; `no` records the torsion cases |
| `unfolded_vertices`, `boundary_edges` | Counts for the entire natural unfolding |
| `unfolding` | Types of its connected components |
| `boundary_component_lengths` | All boundary lengths in increasing order |
| `boundary_words` | Cyclic words in the same order, with ties ordered lexicographically |
| `automorphism_order` | Order of the graph's automorphism group |

The natural unfolding glues triangle edges of incidence two, preserving endpoint labels. [`unfolding_components.json`](unfolding_components.json) records every component, its Euler characteristic, boundary words and vertex-link checks. Boundary links are paths and interior links are cycles. A displayed boundary word may be cyclically rotated or reversed without changing the boundary component.

## Admissible-edge closures

The pruned closure expands non-strong graphs by admissible edge additions and records their first-strong boundary. Strong states are recorded without further expansion.

| File | Contents |
|---|---|
| [`closure_G14a.tsv`](closure_G14a.tsv) | The 16 non-strong classes and 32 first-strong boundary classes from `G14a`; `added_edges` is measured from the seed |
| [`small_closure_certificates.json`](small_closure_certificates.json) | The complete three positive-seed closures, with non-strong/boundary sizes 16/32, 10/16 and 5/8 |
| [`K4_free_I_not_strong_14.tsv`](K4_free_I_not_strong_14.tsv) | All eight K4-free order-14 graphs in $\mathfrak I\setminus\mathfrak I_S$, with seeds, paths and certifying edges |
| [`acyclic_not_strong_14_closure.tsv`](acyclic_not_strong_14_closure.tsv) | The 2,271 non-strong classes generated from all 51 seeds |
| [`I_not_strong_14_closure.tsv`](I_not_strong_14_closure.tsv) | The 29 I-contractible classes in that union |

Each addition path is ordered and uses its seed's labelling. `H1_torsion` is a JSON list of invariant factors; the empty list means no torsion. Membership in $\mathfrak I$ follows from the seed certificate and admissible additions. For each of the eight K4-free graphs and its displayed edge, the common neighbourhood and the extended graph are strong, while the original graph is non-strong.

The three positive-seed closures overlap up to isomorphism, giving 29 non-strong classes in their union. The larger 2,271-class union is the specified closure catalog; its relation to the complete order-14 table is explained in [finite closures](../../docs/secondary-results.md#the-union-from-all-51-seeds).

## Strictly 2-dismantlable graphs

[`strictly_2dis_12.tsv`](strictly_2dis_12.tsv) lists the 20 order-12 graphs in $2$-Dis outside $1$-Dis. `K4_count` counts four-vertex cliques; `clique_number` is the maximum clique order; the degree columns give minimum and maximum degree; `automorphism_order` is the group order.

## Earlier examples

[`D15_label_correspondence.tsv`](D15_label_correspondence.tsv) and [`D15_published_triangles.json`](D15_published_triangles.json) give the vertex bijection and triangle set for Figure 2A of [Dochtermann et al. (2023)](https://doi.org/10.1016/j.disc.2023.113516). Edge {9,12} in the repository labelling corresponds to {5,7} there. The finite checker compares all 32 triangles after relabelling.

[`adamaszek_11_graphs.g6`](adamaszek_11_graphs.g6) contains the first four encodings appended to the source of arXiv:1208.3892v1: the eleven-vertex torsion graphs in Adamaszek's Theorem 1.1. [`adamaszek_11_homology.json`](adamaszek_11_homology.json) records attribution and homology. Each calculation has free rank zero and one torsion factor 2, giving first integral homology $\mathbb Z/2$.

## Run individual checks

From the repository root:

```bash
python3 -P finite/data/check_unfoldings.py
python3 -P finite/data/check_small_closures.py
python3 -P finite/data/check_tables.py
python3 -P finite/data/check_adamaszek.py
```

These commands use the Python standard library and are included in `reproduce.py`. They reconstruct the unfoldings and the three small closures, calculate the graph and automorphism invariants, check the 2,271 first-homology groups and seed classification, and compare the path and subset records. `check_tables.py` also compares the tabular panel dictionaries. For an intentional regeneration, `check_small_closures.py --write` replaces its certificate record; update the finite inventory in that working copy afterward.

## Restricted-search records

[`restricted_K4_records/`](restricted_K4_records/) contains the counters and survivor streams of the restricted searches at orders 5–12. The eight order-12 residues concatenate in numerical order. `restricted_K4_filter.c` tests tree vertex neighbourhoods, singleton edge neighbourhoods and Euler characteristic one on K4-free input. `check_local_K4_records.py` compares the retained counts and streams and calculates the survivors' homology.

The optional command below regenerates connected K4-free graphs of orders 2–8 and tests almost-stuckness, including zero admissible vertices:

```bash
python3 -P finite/data/check_local_K4_small.py --geng /path/to/geng
```

It requires a nauty `geng` supporting `-k`. Per-order stream hashes and counts are compared with [`local_K4_small_checks.json`](../provenance/local_K4_small_checks.json), which also records checks of the three order-13 examples. Add `--require-digest` to require the recorded generator bytes. The article's reduction uses only orders 2–7; the default reproduction route checks that supplied [643-graph list](../../data/local_K4/README.md) without a generator.
