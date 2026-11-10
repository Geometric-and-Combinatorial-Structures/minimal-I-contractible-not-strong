# Computational tools

Start with root `generate.py` for named examples and `reproduce.py` for finite verification. The mathematical algorithms and proofs are in the article and supplement.

| Tools | Purpose |
|---|---|
| `check_cardinalities.py`, `generate_cardinalities.py` | Compare all numerical sources and generate the article's table |
| `check_secondary_results.py`, `build_supplement_tables.py` | Verify auxiliary catalog scope and generate the supplement's tables |
| `reproduce_closures.py` | Regenerate all 51 finite seed closures with the current C core |
| `integrity.py`, `check_repository.py` | Check bytes, article identity, migration records and links |
| `build_paper.py`, `check_document_logs.py` | Compile temporary source copies and inspect TeX logs |
| `generate_local_K4_catalogue.py`, `check_local_K4_catalogue.py` | Generate and check the bounded 643-graph reduction set |
| `figures/` | Exact labelled data, TikZ generators and NetworkX/SymPy witness verification |
| `homology/` | Integer and field homology for the complete residual-adjudication route |
| `campaign_controls/` | Validate partitioned-run records, coverage and aggregation |

`clique_homology.py`, `strong_contractible.py`, `kdismantlable.py`, `dunce_hat.py` and `ripser_z3_check.py` are retained project utilities. They expose earlier exploratory interfaces and may require optional scientific-Python packages. They are not the entry points used to certify the present finite delivery; those checks are listed by `reproduce.py`. Historical filenames ending in a review-round identifier retain their source identity and do not denote a mathematical parameter.

The verifier in `finite/` uses its own exact recurrences, Smith reduction and isomorphism backtracking. The current census core is `v2/src/atascadas_v2.c`. This separation gives finite cross-checks; it is not a second full census.
