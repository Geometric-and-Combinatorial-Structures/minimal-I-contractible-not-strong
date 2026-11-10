# Data routes and encodings

`cardinalities.csv` is the mathematical table: its universe column distinguishes unrestricted connected rows 3–13 from the K4-free connected row 14, and the two acyclicity columns specify coefficients.

`table_cardinalities.csv` and `table_row14_K4free.csv` are retained historical table views used for source comparison and regression tests. `raw_classifier_reference.csv` contains the twelve fields consumed by the current recording driver; it does not have the derived integral column. `tools/check_cardinalities.py` compares these views with `cardinalities.csv`.

The canonical TSV catalogs are under `finite/data/`; duplicate copies formerly placed here have been removed. `stuck_14_K4free.g6` and `strictly_2dis_12.g6` are graph6 input streams for full reproduction and regression tests. The latter contains 20 data records and no comment lines. `acyclic_not_strong_13.g6` and `dunce_hat_15.g6` retain labelled regression examples. Their class sets are compared with the certificate catalogs by the secondary checker.

`census/` retains selected normalized historical aggregate records, all residual graphs, homology adjudications and the finite positive set. Campaign names beginning with F are historical identifiers, not coefficient fields. The local `local_K4/` directory contains the 643 small graphs used in a reduction lemma.

The old `minimal_I_not_strong_14.g6` export had an ambiguous scope in its name; use `finite/data/K4_free_I_not_strong_14.tsv` for the eight classes. The unused historical 84-graph structure file and duplicate TSVs are retained in Git history, with their disposition recorded in `docs/provenance/migration-inventory.tsv`.
