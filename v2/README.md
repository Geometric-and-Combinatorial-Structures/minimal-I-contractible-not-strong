# Version 2 of the classifier and of the cluster pipeline

Remediation of the external audit of commit `4a059b5` (verdict "not certified", 15–16 Oct 2026; 21 findings).
Nothing in `src/` or in the historical result directories was changed: those are the records of what ran. Under `yuca/as_run/` the only change is the provenance correction H-05 (commit `892e41b`): the task script that the p011 front of the n = 14 search actually ran (array 2079156, SHA-256 `b95a125b…`) was added as `tarea_n14_p011.sh`, and the file previously stored under that name, which is the `tarea.sh` of the failed attempt 2079068, is kept byte for byte (SHA-256 `50477550…`) as `tarea_n14_p029_intento_fallido_2079068.sh`. No as-run file was edited.
Version 2 is for **new** computations: the exact recomputations of rows 12–14 and the rerun of the order-14 search.

## Contents

| path | what it is |
|---|---|
| `src/atascadas_v2.c` | classifier, same algorithms as `src/atascadas.c` (v1) |
| `pipeline/campana_v2.py` | campaign driver (standard library only): `init`, `worker`, `status`, `aggregate` |
| `tests/test_equivalence.py` | v1 versus v2 (tables, search modes, special graphs, hash-independence) |
| `tests/test_robustness.py` | graph6 input validation and exit codes |
| `tests/test_pipeline.py` | fault injection into the pipeline |
| `tests/results/*.json`, `sanitizer.txt` | results of the runs reported below |

## Findings and fixes

| finding | defect in v1 | fix in v2 | test |
|---|---|---|---|
| H-01 | `is_rec` memo and the "seen" sets of `icert`/`cerradura` identify a state by a 63-bit hash only | the full key (vertex mask and rows `A[i]&m`) is stored and compared on every hit; the hash only locates the slot. Lookups, hits and hash collisions are reported | T6: v2 built with a **6-bit** hash gives byte-identical output to normal v2 while absorbing 364,775,904 hash collisions (all connected graphs, n ≤ 7) |
| H-02 | a failing producer could be registered as a success | the pipeline records both exit codes, requires the generator's `>Z N graphs generated` count to equal the classifier's count, and publishes a slice only after every check passes | P4–P7: producer exit 42, `>E` line, missing `>Z`, truncated stream → no receipt, worker exits ≠ 0, aggregate refuses |
| H-03 | two fronts shared per-slice paths with different locks | static partition of residues among worker ids; an exclusive lock per worker id; atomic publication (unique temporary name, fsync, rename) | P3: a duplicate worker id is refused |
| H-04 | the collector accepted inconsistent data | per-slice and global invariants, re-validation of every receipt from its stored streams, exact coverage, cross-slice duplicate checks, reference comparisons | P11: edited counts, forged record, missing receipt, wrong shard → aggregate fails |
| H-18 | inline graph6 header dropped; invalid records skipped with exit 0 | strict parser (order 1..16, characters 63..126, exact length, zero padding); header prefix consumed; any invalid record → exit 3 | 25 robustness cases |
| H-19 | `MAXF` = 8192 < C(16,8) = 12870 | `MAXF` = 2^14; 64-bit unsigned counters per process | K16 in `tabla` and `verificar` |
| H-20 | `atascada=1` printed for non-acyclic graphs (C4) | `verificar`: `atascada` requires n ≥ 2, Z/2-acyclicity and no vertex or edge neighbourhood in I_S (exact decision); `sin_movimientos` reported separately. `tools/strong_contractible.py --stuck` corrected the same way | C4 → `sin_movimientos=1 atascada=0`; the 51 stuck graphs → `stuck=yes` |
| H-21 | 17 `-Wmisleading-indentation` warnings | one statement per line | compiles with `-Wall -Wextra -Wpedantic -Werror` |
| H-06 | definitions written as a degenerate downward closure | header comment and Python docstring state the existential / gluing definitions | review |

Additional checks in v2: connected input required in `tabla` (exit 5 otherwise); one order per counting run; table
invariants checked at the end (exit 4 if violated); `icert` queue overflow counted (`icert_truncados`) and never
treated as a certificate.

## Test results (16 Oct 2026, local machine, gcc 14.2, nauty 2.9.3)

- **Equivalence** (`results/equivalence.json`, all pass, 7 min 28 s):
  - T1 `tabla`: all connected graphs n = 1…10 give the same 13 summary fields and the same output lines in v1 and v2, and equal `data/table_cardinalities.csv`.
  - T2 `atascadas` (n = 5…10), T3 `casi` (n = 3…9), T4 `2dis_no_1dis` (n ≤ 9, plus the 20 graphs of order 12): identical in v1 and v2.
  - T5 special graphs (G13 ×3, G14a/b/c and their one-edge extensions, D15 and D15+{9,12}, the 51 stuck graphs):
    - I_S decisions match the paper;
    - `icert` outcomes are identical in v1, v2 and weak-hash v2 (3 + 48 without certificate);
    - closures of G14a/b/c and D15 are identical.
  - T6 `verificar`: all connected graphs n ≤ 8, v1 and v2 agree; the weak-hash runs cover n ≤ 7. With a 6-bit hash, v1 misclassified no graph at n ≤ 7, so the H-01 defect remains a possibility that was not observed, not a demonstrated error.
- **Robustness** (`results/robustness.json`): 25/25 pass. The same inputs show the v1 behaviours described in H-18 and H-19, for example `conexas=0` with exit 0 for an inline header, three "graphs" counted from one 5000-character line, and exit 2 on K16.
- **Pipeline** (`results/pipeline.json`): 12/12 pass, including a normal campaign that reproduces the published row n = 8 and a stuck-search campaign that reproduces the n = 9 totals.
- **Sanitizers** (`results/sanitizer.txt`): AddressSanitizer and UBSan, no report in `tabla` n ≤ 8, `verificar` n ≤ 6, `icert`/`cerradura`/`traza` on the special graphs, `atascadas` n = 9 and K16. Leak detection was off: LeakSanitizer cannot run under the ptrace of the local sandbox.

## Not yet done

- The pipeline has not run at scale on YUCA. Its first production uses are planned after the current n = 14 table:
  - complete-state recomputation of rows 12 and 13;
  - the rerun of the order-14 stuck search;
  - the exact recomputation of the K₄-free order-14 row.
- The external auditor's own driver for the exact recomputations (test Y-R01) uses the exact-key variant `verification/atascadas_memo_exacto.c`, not v2. The two implementations are independent of each other.

## Build and run

```bash
gcc -O3 -std=c11 -Wall -Wextra -Wpedantic -Werror -o atascadas_v2 src/atascadas_v2.c
geng -c 9 | ./atascadas_v2 --modo tabla > found.txt 2> summary.txt; echo $?

# campaign (example: order 12 table, 4000 slices, 448 single-core workers)
python3 pipeline/campana_v2.py init --root /scratch/run_n12 --n 12 --mod 4000 --workers 448 --mode tabla \
        --geng /path/to/geng --geng-args=-c --source src/atascadas_v2.c --expect-geng-version 2.7
python3 pipeline/campana_v2.py worker --config /scratch/run_n12/config.json --worker-id $SLURM_ARRAY_TASK_ID
python3 pipeline/campana_v2.py aggregate --config /scratch/run_n12/config.json --reference-csv ../data/table_cardinalities.csv
```

Tests: `python3 tests/test_robustness.py`, `python3 tests/test_pipeline.py` and `python3 tests/test_equivalence.py`.
The equivalence test needs the four binaries in `build/`:
- `atascadas_v1` and `atascadas_v2`, built from the two sources;
- `atascadas_v2_weak`, built with `-DHASH_WEAK_BITS=6`;
- `atascadas_v1_weak`, built from v1 with its hash masked to 6 bits.
