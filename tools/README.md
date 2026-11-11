# Calculation and verification tools

The main interfaces are [`generate.py`](../generate.py), which exports named graphs, and [`reproduce.py`](../reproduce.py), which checks the finite examples and table records. The [reproduction guide](../docs/reproduction.md) introduces their mathematical inputs and outputs. The tools below support particular parts of those calculations.

| Tools | Purpose |
|---|---|
| `check_cardinalities.py`, `generate_cardinalities.py` | Compare the table with its numerical sources and format its two LaTeX panels |
| `check_secondary_results.py`, `build_supplement_tables.py` | Check the auxiliary catalogs and format their tables |
| `reproduce_closures.py` | Regenerate the closures of all 51 seeds |
| `generate_local_K4_catalogue.py`, `check_local_K4_catalogue.py` | Generate and check the 643-graph set used in the cut-vertex reduction |
| [`figures/`](figures/) | Generate the witness drawings and check their edges, homology and reductions |
| [`homology/`](homology/) | Classify the unresolved graphs from a complete enumeration by integer and field homology |
| `build_paper.py`, `check_document_logs.py` | Compile the article and supplement and inspect the TeX logs |
| `integrity.py`, `check_repository.py` | Check the file inventory, article identity, provenance maps and links |
| [`campaign_controls/`](campaign_controls/) | Check partition coverage and aggregation records |

`clique_homology.py`, `strong_contractible.py`, `kdismantlable.py`, `dunce_hat.py` and `ripser_z3_check.py` are earlier project utilities with separate interfaces and optional scientific-Python dependencies. The checks used by the main reproduction command are listed in the [verification map](../docs/verification-scope.md).
