# Sources and repository history

`migration-inventory.tsv` accounts for every file in the historical tree at commit `c66e0399bc864e4e0147aa14d01ac9fb24db5028`, recording its Git blob, disposition and current destination. Earlier figures, scheduling records and notes remain in Git history.

Root `PROVENANCE.json` identifies the source archive imported into this repository. `selection-migration.json` accounts for its files. `manuscript-r01-selection.json` and `manuscript-r01-sha256.txt` preserve the source selection map and inventory; root `SHA256SUMS.txt` covers the current tree. A file marked as updated or superseded retains its original identity in the corresponding migration record.

`article-r01.json` identifies the 20 article source inputs and the PDF in `paper/`. The repository checker compares those files with the recorded identities. The supplement has its own sources under `supplement/`.

## Enumeration and finite verification

| Records | Contents |
|---|---|
| [`finite/provenance/`](../../finite/provenance/) | Selected source identities, small-order comparisons and completion records |
| [`data/census/`](../../data/census/) | Enumeration aggregates, residual graphs and homology adjudications |
| [`finite/data/restricted_K4_records/`](../../finite/data/restricted_K4_records/) | Restricted-search counters and survivor lists used in local reduction checks |
| [`verification/historical_small_orders/`](../../verification/historical_small_orders/) | Historical source variants and their comparison |
| [`verification/closures51/`](../../verification/closures51/) | A recorded regeneration of all 51 finite seed closures |

[`finite/figures/`](../../finite/figures/) contains panel and reduction dictionaries used by the verifiers. Historical homology comparison scripts are under [`tools/homology/archive/`](../../tools/homology/archive/); the active route is described in [full reproduction](../full-reproduction.md).

The [verification map](../verification-scope.md) relates these records to the mathematical statements and distinguishes the checks that can be repeated from the retained execution evidence.
