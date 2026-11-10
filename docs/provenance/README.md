# Provenance and migration

The previous default-branch commit is `c66e0399bc864e4e0147aa14d01ac9fb24db5028`. Its complete Git history is preserved. `migration-inventory.tsv` accounts for every file in that tree by old Git blob, disposition and current destination. Historical figures, scheduler records and obsolete notes remain available in history; they are not active reproduction instructions.

The prepared manuscript selection was imported from the ZIP identified in root `PROVENANCE.json`. `selection-migration.json` accounts for every file from that selection. The old selection map and manifest are preserved as `manuscript-r01-selection.json` and `manuscript-r01-sha256.txt`; their hashes refer to the prior snapshot. They do not assert that later edited documentation still has those bytes. The current full inventory is root `SHA256SUMS.txt`.

`article-r01.json` fixes the 20 packaged source inputs and the complete reviewed PDF. The repository checker compares these hashes on every finite run. The article delivery itself remains unchanged; the new mathematical material is in the separate supplement.

The baseline is a historical research repository, so its older commits include material removed from the current reader-facing tree. The migration preserves history rather than rewriting it. No change of repository visibility is part of this update.

## Retained historical evidence

`finite/provenance/` holds selected normalized source identities, small-order comparisons and completion records. `finite/data/restricted_K4_records/` preserves the earlier restricted-search survivor lists and counters used to interpret reduction checks. `finite/figures/` contains tabular panel/trace dictionaries used by finite verifiers, not obsolete drawings. `src/atascadas.c` and `verification/historical_small_orders/` serve historical source comparisons; new runs use `v2/src/atascadas_v2.c`.

The homology scripts under `tools/homology/archive/` are historical comparison material. Their filenames do not certify independence of a full census. The active residual-adjudication route and its two homology methods are described in `docs/full-reproduction.md`. The small benchmark graph streams under `data/` are compared with their canonical certificate catalogs by `tools/check_secondary_results.py`.

Mathematical claims, finite reconstructions and historical execution evidence are distinguished in `docs/verification-scope.md`. The source selection does not contain all per-residue production archives or authenticate historical execution.
