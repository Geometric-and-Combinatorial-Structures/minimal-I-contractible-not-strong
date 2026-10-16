# Version 2 of the classifier and of the cluster pipeline (current release: v2.1)

Remediation of the external audit of commit `4a059b5` (verdict "not certified", 15–16 Oct 2026; 21 findings).
Nothing in `src/` or in the historical result directories was changed: those are the records of what ran. Under `yuca/as_run/` the only change is the provenance correction H-05 (commit `892e41b`): the task script that the p011 front of the n = 14 search actually ran (array 2079156, SHA-256 `b95a125b…`) was added as `tarea_n14_p011.sh`, and the file previously stored under that name, which is the `tarea.sh` of the failed attempt 2079068, is kept byte for byte (SHA-256 `50477550…`) as `tarea_n14_p029_intento_fallido_2079068.sh`. No as-run file was edited.
Version 2 is for **new** computations: the exact recomputations of rows 12–14 and the rerun of the order-14 search.

**Version 2.1** (16 Oct 2026) answers round 2 of the external audit (verdict "not certified", 16 Oct 2026): findings
H-18 (extended), H-22, H-23, H-24, H-25 and H-29, and the pinning requests of Q9; see the section on v2.1 below. The
algorithms did not change. Neither v2 nor v2.1 has been used for a production run. The rerun of the order-14 search
(F3) waits for the auditor's review of v2.1, for the end of the historical producers and for the author's decision.

## Contents

| path | what it is |
|---|---|
| `src/atascadas_v2.c` | classifier, same algorithms as `src/atascadas.c` (v1) |
| `pipeline/campana_v2.py` | campaign driver (standard library only): `init`, `worker`, `status`, `aggregate` |
| `tests/test_equivalence.py` | v1 versus v2 (tables, search modes, special graphs, hash-independence) |
| `tests/test_robustness.py` | graph6 input validation and exit codes |
| `tests/test_pipeline.py` | fault injection into the pipeline |
| `tests/test_regressions_r2.py` | v2.1: the round-2 adversarial cases (classifier, slice, receipt, campaign, references, aggregate, init) |
| `tests/run_sanitizers.sh` | v2.1: AddressSanitizer + UBSan battery with two positive controls |
| `tests/provenance.py` | v2.1: SHA-256 and `--version` of every binary, source and tool, recorded in each result file |
| `tests/results/*.json`, `sanitizer.txt` | results of the **v2** runs of 16 Oct 2026, kept as they ran |
| `tests/results/v2.1/` | results of the **v2.1** runs reported below |

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

## Version 2.1: round 2 of the external audit

| finding | defect in v2 | fix in v2.1 | regression cases |
|---|---|---|---|
| H-18 (extended) | NUL bytes accepted; a last line without newline counted as a valid record, so a truncated stream could pass; an empty `--prof` was read as 0 | every line must end in a newline and contain no NUL; a line of 4096 bytes or more (newline included) is invalid; all of these are invalid records (exit 3); `--prof` must be a non-empty string of decimal digits (otherwise usage error, exit 1) | classifier: 9 |
| H-25 | write errors ignored: output to a full device ended with exit 0 | `fflush`/`ferror` on stdout and stderr at the end, also for `--version`: exit 6, which takes priority over every other code | classifier: 2 |
| H-24 | permissive summary parser: repeated or contradictory keys, trailing text, negative values, memo hits above lookups, foreign worker metadata | exact key set without repetitions; non-negative integers; pinned summary version; `memo_aciertos` ≤ `memo_consultas` (hash collisions are counted per probe and may exceed lookups); at most one `>A` generator header, which must name the order and the class r/mod, and exactly one `>Z` line; receipts must carry worker id, host, UTC times and seconds, and the worker must own the residue (r mod workers = worker id) | slice: 32, receipt: 16 |
| H-23 | two concurrent inits on one directory both succeeded with different configs; the driver was not pinned; a promised path guard was not implemented | all checks that do not need the disk run first; the root is created with an exclusive `mkdir`; protected directories (`/lustre/proyectos/p029/busqueda_minimal` by default, `--protect`, `CAMPANA_PROTECT`); geng, source and driver are copied read-only into `bin/` and pinned by SHA-256 in `config.json`, itself pinned by `config.sha256` (both created exclusively, mode 0444); a worker refuses an edited config or a driver other than the pinned one; geng is pinned by the **exact** version token printed by `geng --version` and by its SHA-256 (both options required), its full `--version` output is stored in the config and its full `--help` output in `bin/geng_help.txt`; a failure after the `mkdir` leaves `INIT_FAILED.txt` and no config | init: 11 |
| H-29 | a failed aggregation could leave an earlier `aggregate.json` with `ok=true`; `status` counted receipts by existence; test wrappers did not quote the geng path | `aggregate` takes every worker lock (it refuses while a producer runs) and moves earlier outputs to `aggregate_history/` before writing; `status` counts readable and unreadable receipts and states that it is not a certificate; `shlex.quote` | aggregate: 3 |
| H-22 | the aggregator accepted a CSV reference without the requested row or columns (exit 0, `ok=true`, nothing compared); duplicate rows and `--expect` could silently override conflicts | the reference must have exactly one row for the order, with all 12 columns integers; conflicts are fatal; `--expect` keys are unique and their values non-negative integers; a requested comparison that compares nothing is an error. Also (pipeline audit, round 2): `--reference-g6` compared labelled strings; with `--labelg` it now compares canonical forms | reference: 9 |
| Q9 | `-march=native` in the build | portable flags in `build.sh` and in the driver's default `--cflags` | classifier: 1 |

The other 4 classifier cases are controls (valid input, a header-only line, a read error, the version string).

The geng version token is compared as printed because nauty prints NAUTYVERSIONID/10000 and `nauty.h` defines
NAUTYVERSIONID as 10000·version + HAVE_TLS: release 2.8.9 prints `2.8090`, release 2.9.3 prints `2.9300` or `2.9301`.
No conversion to a dotted release name is attempted (an earlier draft of v2.1 did so and misread 2.9301).

Exit codes of `atascadas_v2`: 0 correct; 1 usage; 2 internal capacity exceeded; 3 invalid records; 4 internal
inconsistency, violated invariant or read error; 5 disconnected input (`tabla`) or mixed orders (counting modes);
6 write error on stdout or stderr (takes priority).

Data correction made with v2.1 (not a code change): in `data/table_cardinalities.csv` the I-undecided entry of row 13
is now the raw counter of the run, 3 (`yuca/logs/n13_tabla_resumen.txt`); see `data/README.md`.

## Test results of v2.1 (16 Oct 2026, local machine, gcc 14.2, nauty 2.9.3; `results/v2.1/`)

Every result file records the SHA-256 of the binaries, sources and tools it exercised (key `provenance`). The v2.1
binaries were built from `src/atascadas_v2.c` with SHA-256 `826fec148cb76f4184aedb0e…`; the sensitivity run uses
the older binary named below on purpose.

- **Equivalence** (`equivalence.json`): 49/49 pass, 449 s; the same T1–T6 checks as for v2 (below), now between v1 and v2.1.
- **Robustness** (`robustness.json`): 25/25 pass.
- **Pipeline** (`pipeline.json`): 12/12 pass.
- **Round-2 regressions** (`regressions_r2.json`): 89/89 pass (classifier 16, slice 32, receipt 16, campaign 2,
  reference 9, aggregate 3, init 11).
- **Sensitivity** (`regressions_r2_sensitivity_f6ab7e4.json`): the classifier cases run against the v2 binary of
  commit `f6ab7e4` (its source is byte-identical to `git show f6ab7e4:v2/src/atascadas_v2.c`) fail in 10 of 16 cases:
  NUL without final newline (3 inputs), a valid line or a header line without final newline, write errors on stdout
  and stderr, empty or blank `--prof`, and the version string. This exit status 1 is the expected outcome.
- **Sanitizers** (`sanitizer.txt`, produced by `tests/run_sanitizers.sh`): both positive controls report; in the other
  17 runs (`tabla` on all connected graphs n = 9; `atascadas`, `casi` and `2dis_no_1dis` on n = 8; `verificar` on K16;
  `verificar`, `icert` and `traza` on the 56 special graphs; `cerradura` on G14a; five malformed inputs, an invalid `--prof` and two runs writing
  to a full device) there is no report and every exit code is the documented one. Leak detection off (ptrace); `verify_asan_link_order=0`.

## Test results of v2 (16 Oct 2026, local machine, gcc 14.2, nauty 2.9.3; `results/`)

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

- Not evaluated: exclusion between nodes or accounts through `flock` on Lustre. Only local exclusion was verified; a
  preflight on YUCA must precede a two-account campaign.
- Receipts are not authenticated: a receipt rewritten coherently (streams, counts and hashes together) is accepted;
  the regression suite documents this. The defences are the re-validation of every receipt from its stored streams
  and the archived hashes.
- The pipeline has not run at scale on YUCA. Its first production uses are planned after the current n = 14 table:
  - complete-state recomputation of rows 12 and 13;
  - the rerun of the order-14 stuck search;
  - the exact recomputation of the K₄-free order-14 row.
- The external auditor's own driver for the exact recomputations (test Y-R01) uses the exact-key variant `verification/atascadas_memo_exacto.c`, not v2. The two implementations are independent of each other.

## Build and run

```bash
./build.sh                      # build/atascadas_v2 and the binaries used by the tests (portable flags)
geng -c 9 | build/atascadas_v2 --modo tabla > found.txt 2> summary.txt; echo $?

# campaign (example: order 12 table, 4000 slices, 448 single-core workers)
G=/path/to/geng
"$G" --version                  # e.g. "Nauty&Traces version 2.9301 (32 bits)": the token is 2.9301
python3 pipeline/campana_v2.py init --root /scratch/run_n12 --n 12 --mod 4000 --workers 448 --mode tabla \
        --geng "$G" --geng-args=-c --source src/atascadas_v2.c \
        --expect-geng-version 2.9301 --expect-geng-sha256 "$(sha256sum "$G" | cut -d' ' -f1)"
python3 /scratch/run_n12/bin/campana_v2.py worker --config /scratch/run_n12/config.json --worker-id $SLURM_ARRAY_TASK_ID
python3 /scratch/run_n12/bin/campana_v2.py aggregate --config /scratch/run_n12/config.json \
        --reference-csv ../data/table_cardinalities.csv
```

The workers and the aggregation run the driver copy pinned in `bin/`; another copy is refused unless it is
byte-identical. In production the expected SHA-256 of geng is written out, not computed from the file being pinned.

Tests (from `v2/`, after `./build.sh`):

```bash
python3 tests/test_equivalence.py                  # about 8 min with 8 processes
python3 tests/test_robustness.py
python3 tests/test_pipeline.py --work /tmp/pt
python3 tests/test_regressions_r2.py --work /tmp/reg
python3 tests/test_regressions_r2.py --work /tmp/sens --sections classifier --bin OLD_BINARY \
        --out tests/results/v2.1/regressions_r2_sensitivity_f6ab7e4.json      # expected to fail (exit 1)
tests/run_sanitizers.sh
```

The equivalence test needs the four binaries in `build/`:
- `atascadas_v1` and `atascadas_v2`, built from the two sources;
- `atascadas_v2_weak`, built with `-DHASH_WEAK_BITS=6`;
- `atascadas_v1_weak`, built from v1 with its hash masked to 6 bits.
