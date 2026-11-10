# Exact classifier and enumeration pipeline

`src/atascadas_v2.c` is classifier v2.2, with complete-state memoisation. Its keys contain the current vertex mask and all restricted adjacency rows. `pipeline/campana_v2.py` is recording driver v2.4. These are the sources used in the recorded complete recomputations; their bytes and hashes are preserved.

For the finite reader-facing checks, use `python3 reproduce.py --extended` from the repository root. The [full reproduction guide](../docs/full-reproduction.md) is the single maintained specification for generation, partitioning, residual adjudication and aggregation. It uses `data/raw_classifier_reference.csv` for the twelve raw counters and `data/cardinalities.csv` for the mathematical table, including the derived integral column.

## Build and a small example

From the repository root, with a C11 compiler and nauty `geng` on PATH:

```bash
cd v2
./build.sh
geng -c 5 | build/atascadas_v2 --modo tabla
```

Use Bash with `set -euo pipefail` when retaining a pipeline result. The example enumerates only the 21 connected graphs of order five. `build.sh` also creates the legacy and deliberately weakened-hash executables used by the regression suite. The executable option is `--modo`; the recording driver's option is `--mode`.

## Aggregate certificate contract

An invocation certifies its recorded result only when all four conditions hold:

1. Its real exit status is zero.
2. `aggregate.json` names the attempt created by that invocation.
3. The corresponding `aggregate_attempts/<attempt>.json` is terminal, with status `ok`.
4. Its `aggregate_sha256` equals the hash of the aggregate bytes being read.

An earlier success can remain after a failed invocation; coherent files alone
therefore do not satisfy this contract. Receipts and preserved hashes do not
authenticate historical execution. The fault model concerns process and file
operations; the directory is not fsync'ed after a rename, so durability across
operating-system crashes or power loss is not established. Worker exclusion
also depends on the filesystem's locking behaviour.

## Regression suite

Run from `v2/` after building. These commands write fresh working directories and result records. The equivalence test additionally needs nauty tools; the larger suite is separate from the default finite route.

```bash
python3 tests/test_robustness.py
python3 tests/test_pipeline.py --work build/pipeline-test
python3 tests/test_regressions_r2.py --work build/regressions-r2
python3 tests/test_regressions_r3.py --work build/regressions-r3
python3 tests/test_regressions_r4.py --work build/regressions-r4
python3 tests/test_regressions_r5.py --work build/regressions-r5
python3 tests/test_equivalence.py
tests/run_sanitizers.sh
```

Consult each command's `--help` before a targeted rerun. Sensitivity tests against deliberately old binaries or drivers require those historical artifacts and are not default reproduction commands. Historical comparisons and their limits are described in [small-order provenance](../docs/small-order-provenance.md) and [`finite/provenance/README.md`](../finite/provenance/README.md).
