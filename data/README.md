# Table data and graph encodings

[`cardinalities.csv`](cardinalities.csv) is the mathematical table. Its universe column distinguishes all connected graphs at orders 3–13 from connected K4-free graphs at order 14. Separate columns give acyclicity over $\mathbb F_2$ and over $\mathbb Z$.

| Files | Contents and use |
|---|---|
| `table_cardinalities.csv`, `table_row14_K4free.csv` | Recorded table views used for comparison |
| `raw_classifier_reference.csv` | Twelve raw counters read by the enumeration driver; the integral column is derived separately |
| `stuck_14_K4free.g6` | The 51 stuck K4-free order-14 seeds |
| `strictly_2dis_12.g6` | The 20 strictly 2-dismantlable order-12 graphs |
| `acyclic_not_strong_13.g6`, `dunce_hat_15.g6` | Labelled examples used in regression comparisons |
| [`census/`](census/) | Selected enumeration totals, all residual graphs and their homology calculations, and the positive order-14 set |
| [`local_K4/`](local_K4/) | The 643 small graphs used in the cut-vertex reduction |

Graph6 files encode finite simple graphs with labels starting at zero. The TSV [catalogs](../finite/data/README.md) supply additional invariants and certificates. The eight K4-free graphs of order 14 in $\mathfrak I\setminus\mathfrak I_S$ are listed in [`K4_free_I_not_strong_14.tsv`](../finite/data/K4_free_I_not_strong_14.tsv).

`tools/check_cardinalities.py` compares the numerical sources with the mathematical table. `tools/check_secondary_results.py` compares the labelled example streams with the certificate catalogs up to isomorphism. Historical filenames beginning with `F` identify computations; their naming convention is explained in the [enumeration guide](../docs/full-reproduction.md#enumerations-and-record-names).
