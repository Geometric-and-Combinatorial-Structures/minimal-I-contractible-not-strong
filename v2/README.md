# Version 2 of the classifier and of the cluster pipeline (current release: v2.3)

Remediation of the external audit of commit `4a059b5` (verdict "not certified", 15–16 Oct 2026; 21 findings).
Nothing in `src/` or in the historical result directories was changed: those are the records of what ran. Under `yuca/as_run/` the only change is the provenance correction H-05 (commit `892e41b`): the task script that the p011 front of the n = 14 search actually ran (array 2079156, SHA-256 `b95a125b…`) was added as `tarea_n14_p011.sh`, and the file previously stored under that name, which is the `tarea.sh` of the failed attempt 2079068, is kept byte for byte (SHA-256 `50477550…`) as `tarea_n14_p029_intento_fallido_2079068.sh`. No as-run file was edited.
Version 2 is for **new** computations: the exact recomputations of rows 12–14 and the rerun of the order-14 search.

**Version 2.1** (16 Oct 2026) answers round 2 of the external audit (verdict "not certified", 16 Oct 2026): findings
H-18 (extended), H-22, H-23, H-24, H-25 and H-29, and the pinning requests of Q9; see the section on v2.1 below. The
algorithms did not change.

**Version 2.2** (17 Oct 2026) answers round 3 of the external audit (verdict "not certified", 17 Oct 2026): the
partial closures H-22, H-23, H-24 and H-29, the new finding H-35 and request S4, closed by class and not only for the
auditor's examples; see the section on v2.2 below. The algorithms did not change.

**Version 2.3** (17 Oct 2026) answers round 4 of the external audit (verdict "not certified"; H-23, H-24, H-31 and
H-35 closed): the residues of H-22 and H-29, closed by class in the driver. The classifier is unchanged (its source,
binary and version string are those of v2.2). The conda-forge origin of `geng28` (request S4) is now shown by bytes in
`../yuca/geng28_provenance.md`. No version 2.x has been used for a production run. The rerun of the order-14 search
(F3) waits for the auditor's review of v2.3, for the end of the historical producers and for the author's decision.

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
| `tests/test_regressions_r3.py` | v2.2: the round-3 counterexamples extended to their classes (init, receipt, reference, aggregate, classifier, harness); `--driver`, `--source`, `--bin` run it against older files |
| `tests/test_regressions_r4.py` | v2.3: the round-4 counterexamples extended to their classes (labelg, transaction, worker), with systematic fault injection; `--driver` runs it against an older driver |
| `tests/provenance.py` | v2.1: SHA-256 and `--version` of every binary, source and tool, recorded in each result file (v2.2: argv paths normalized, H-35) |
| `tests/results/*.json`, `sanitizer.txt` | results of the **v2** runs of 16 Oct 2026, kept as they ran |
| `tests/results/v2.1/` | results of the **v2.1** runs of 16 Oct 2026, kept as they ran |
| `tests/results/v2.2/` | results of the **v2.2** runs of 17 Oct 2026, kept as they ran |
| `tests/results/v2.3/` | results of the **v2.3** runs reported below |

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

## Version 2.3: round 4 of the external audit

| finding | defect in v2.2 | fix in v2.3 | regression cases (`test_regressions_r4.py`) |
|---|---|---|---|
| H-22 | `labelg` was hashed at one moment and run from the given path at another; replacing it in between (the auditor put a constant canonizer there at its first use) made `aggregate` accept G14a against K14; a changed hash was recorded without invalidating anything | `labelg` is copied, from the bytes that are hashed, to a private read-only file of the attempt (`aggregate_attempts/<id>.tools/`); that copy is checked by SHA-256 before and after every run and any difference fails the attempt; `labelg` must pass a self-test (P4 and a relabelled P4 coincide, P4 and the star K1,3 differ) and return graph6 strings of the right order; every reference (CSV, graph6, `labelg`) is hashed again at the end and a change fails the attempt. The same rule for the workers: the pinned `geng` and classifier are checked before and after every slice, and nothing is published on a difference | labelg: 12; worker: 4 |
| H-29 | the final write of the attempt record came after `aggregate.json` had been published with `ok=true`, outside the block that reverts success: its failure left `ok=true` with an attempt in state `started` (exit 1) | every write of `aggregate`, the first record of the attempt included, is inside its transaction; the attempt record becomes terminal, with the SHA-256 of the aggregate, before `aggregate.json` is published; the summary is printed before as well; publishing `aggregate.json` is the last operation | transaction: 7 (the auditor's fault; one write failure, a persistent failure and a crash at each of the 15 write operations of a successful `aggregate`; stdout on a full device) |

So `aggregate.json` with `ok=true` always belongs to an attempt whose record is terminal (`ok`) and names its SHA-256,
and a failing attempt never leaves `ok=true`.  A consumer should still require exit 0 and the attempt it launched.
Limits stated by the auditor: a modification restored to the same bytes between two checks, or a change of the
bytes of a running process, is not detected.

Documentation changes made with v2.3 (not code changes): `../yuca/geng28_provenance.md` and
`../yuca/provenance_geng28/` show that `geng28` is byte-identical to `bin/geng` of the conda-forge package
nauty-2.9.3-hb03c661_0 (linux-64), from the channel's index to the bytes on YUCA, and record how the file reached
YUCA; `README.md` and `yuca/README.md` cite it.

## Version 2.2: round 3 of the external audit

| finding | defect in v2.1 | fix in v2.2 | regression cases (`test_regressions_r3.py`) |
|---|---|---|---|
| H-22 | `csv.DictReader` kept the last of two equal column names, so a CSV whose first `connected` column said 999 passed; `--expect` without a value compared nothing and exited 0; the key `-1-Dis` could not be given | the CSV header must name each column once and every row must have as many fields as the header; unreadable or non-UTF-8 references are refused; `--expect` takes one `KEY=VALUE` per occurrence (`--expect=-1-Dis=V` for that key); repeated keys and malformed values are refused; an empty graph6 reference and `--labelg` without `--reference-g6` are refused; the path and SHA-256 of every reference (CSV, graph6, labelg) are recorded in `aggregate.json` and in the attempt record | reference: 23 |
| H-23 | an unclosed quote in `--geng-args` or `--cflags`, or a `geng --help` that fails, was found after the root existed; a failure after `config.sha256` was written left a root that workers accepted | `--geng-args` and `--cflags` are parsed (shlex) and `geng --help` must exit 0 with output before the `mkdir`; the last step of `init` writes `INIT_COMPLETE.json` with the config hash; `worker`, `status` and `aggregate` refuse a root with `INIT_FAILED.txt`, without the marker, or with a marker for another config | init: 11 (two late failures injected: at the chmod of `config.sha256` and at the marker) |
| H-24 | receipts accepted NaN or Infinity seconds, times in any format or order, booleans for integers, extra keys and repeated JSON keys | receipts are read by a strict JSON reader (no NaN or Infinity, no repeated keys) and written with `allow_nan=False`; a receipt has exactly the schema keys (SLURM ids included); integers of exact type (a boolean is not an integer); finite non-negative seconds; UTC times in the driver's own format, ordered (tolerance 5 s) and inside the life of the campaign (tolerance 300 s); summaries compared in canonical form; a resumed slice is validated by the same rules | receipt: 49 (the auditor's five patches; 241 wrong values over the 26 keys; every missing key; extra keys; both sides of each clock tolerance; NaN, Infinity, a repeated key and `true` for 1 in the files) |
| H-29 | an attempt that failed before archiving (busy worker lock, refused reference) left the earlier `aggregate.json` with `ok=true` in place; `status` crashed on a receipt containing `null` or `[]` | `aggregate` takes `aggregate.lock`, records the attempt in `aggregate_attempts/<id>.json` and archives earlier outputs first; then it checks the references, takes the worker locks and sums; any failure writes `aggregate.json` with `ok=false`, `status=failed` and the reason; a successful `aggregate.json` names its `attempt_id`; `status` counts anything that is not a readable receipt object as unreadable | aggregate: 9 |
| S4 | the early exits of the classifier (usage errors, lack of memory) did not check their streams | `finish_streams` (flush and error check, exit 6) on every early exit, `--version` and lack of memory included | classifier: 6 |
| H-35 | the test harness recorded a new absolute `--out` path verbatim, so `check_portable` refused the result after the run | absolute paths that do not exist yet and `--option=PATH` are recorded like existing paths (relative to the repository, or file name only) | harness: 6 |

A usage error of `aggregate` (for example `--expect` without a value) stops in the argument parser with exit 2,
before any attempt starts; it touches no output and records no attempt.

Documentation changes made with v2.2 (not code changes):
- H-31: the comment headers of `data/acyclic_not_strong_13.g6`, `data/strictly_2dis_12.g6`,
  `data/stuck_14_K4free.tsv` and `data/minimal_I_not_strong_14.g6` state the reservations of `data/README.md`; the
  data lines are byte-identical. The recorded output of `verification/check_table_B1_fig07.py` was regenerated: same
  body, new SHA-256 of the TSV.
- Provenance: `geng28` on YUCA is the conda-forge binary of nauty 2.9.3, not nauty 2.8 (`yuca/README.md`,
  `README.md`, `verification/VERIFICACION_INDEPENDIENTE.md`). The manuscript keeps the wrong statement until its
  next version.

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
6 write error on stdout or stderr (takes priority; since v2.2 also on the early exits: usage errors, `--version` and
lack of memory).  A stream that received no output cannot produce a 6.

Data correction made with v2.1 (not a code change): in `data/table_cardinalities.csv` the I-undecided entry of row 13
is now the raw counter of the run, 3 (`yuca/logs/n13_tabla_resumen.txt`); see `data/README.md`.

## Test results of v2.3 (17 Oct 2026, local machine, gcc 14.2, nauty 2.9.3; `results/v2.3/`)

The classifier is the v2.2 one (source `bd18224f907971e2…`, `build/atascadas_v2` `0c8a6e11f6faf47a…`); the driver
`pipeline/campana_v2.py` has SHA-256 `9202cece2c9957ab…`.  Every result file records its provenance.

- **Equivalence** (`equivalence.json`): 49/49 pass, 430 s.
- **Robustness** (`robustness.json`): 25/25 pass.
- **Pipeline** (`pipeline.json`): 12/12 pass.
- **Round-2 regressions** (`regressions_r2.json`): 89/89 pass.
- **Round-3 regressions** (`regressions_r3.json`): 104/104 pass.
- **Round-4 regressions** (`regressions_r4.json`): 25/25 pass (init 2, labelg 12, transaction 7, worker 4). The
  transaction group injects one write failure, a persistent failure and a crash at each of the 15 write operations of
  a successful `aggregate` (45 runs).
- **Sensitivity** (`regressions_r4_sensitivity_v2.2.json`): the same suite run against the v2.2 driver
  (`git show c605d78:v2/pipeline/campana_v2.py`) fails in 18 of 25 cases: init 1 of 2, labelg 9 of 12, transaction
  6 of 7, worker 2 of 4. The 7 cases that pass are controls (a normal init, the fixture, the real `labelg` accepting
  a relabelled G14a and refusing K14, the count of write operations, and the two recoveries after restoring the
  executables). This exit status 1 is the expected outcome.
- **Sanitizers** (`sanitizer.txt`): 19 of 19 runs checked; both positive controls report; no report in the other 17.
- **`verify.sh`** (repository root): 39/39.

## Test results of v2.2 (17 Oct 2026, local machine, gcc 14.2, nauty 2.9.3; `results/v2.2/`)

Every result file records the SHA-256 of the binaries, sources and tools it exercised (key `provenance`). The v2.2
binaries were built from `src/atascadas_v2.c` with SHA-256 `bd18224f907971e2…` (`build/atascadas_v2`:
`0c8a6e11f6faf47a…`); the driver `pipeline/campana_v2.py` has SHA-256 `f01fdb5ed609d356…`.

- **Equivalence** (`equivalence.json`): 49/49 pass, 403 s; the same T1–T6 checks, now between v1 and v2.2.
- **Robustness** (`robustness.json`): 25/25 pass.
- **Pipeline** (`pipeline.json`): 12/12 pass.
- **Round-2 regressions** (`regressions_r2.json`): 89/89 pass. The fixture receipt of the receipt cases now has the
  keys and UTC format of a v2.2 receipt (strict schema); the cases are unchanged.
- **Round-3 regressions** (`regressions_r3.json`): 104/104 pass (init 11, receipt 49, reference 23, aggregate 9,
  classifier 6, harness 6).
- **Sensitivity** (`regressions_r3_sensitivity_v2.1.json`): the same suite run against the v2.1 driver, source and
  binary (`git show da46581:v2/pipeline/campana_v2.py` and `…/src/atascadas_v2.c`, built with the flags of
  `build.sh`) fails in 68 of 104 cases: init 10 of 11, receipt 31 of 49, reference 15 of 23, aggregate 7 of 9,
  classifier 5 of 6, harness 0 of 6. The harness group exercises `tests/provenance.py`, the same file in both runs;
  the v2.1 harness, checked separately, keeps the local path in both H-35 probes. The cases that pass against v2.1
  are behaviours v2.1 already had (checks of streams, hashes, commands and identity; uneven CSV rows; exit 6 of
  `--version`). This exit status 1 is the expected outcome.
- **Sanitizers** (`sanitizer.txt`): 19 of 19 runs checked; both positive controls report; no report in the other 17
  runs; every exit code is the documented one.
- **`verify.sh`** (repository root): 39/39.

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

- Not evaluated: exclusion between nodes or accounts through `flock` on Lustre. Only local exclusion was verified; the
  preflight P1 requested in round 3 must pass on YUCA before a two-account campaign.
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
python3 tests/test_regressions_r3.py --work /tmp/reg3
python3 tests/test_regressions_r3.py --work /tmp/sens3 --driver OLD_DRIVER --source OLD_SOURCE --bin OLD_BINARY \
        --out tests/results/v2.2/regressions_r3_sensitivity_v2.1.json        # expected to fail (exit 1)
python3 tests/test_regressions_r4.py --work /tmp/reg4
python3 tests/test_regressions_r4.py --work /tmp/sens4 --driver OLD_DRIVER \
        --out tests/results/v2.3/regressions_r4_sensitivity_v2.2.json        # expected to fail (exit 1)
tests/run_sanitizers.sh
```

The equivalence test needs the four binaries in `build/`:
- `atascadas_v1` and `atascadas_v2`, built from the two sources;
- `atascadas_v2_weak`, built with `-DHASH_WEAK_BITS=6`;
- `atascadas_v1_weak`, built from v1 with its hash masked to 6 bits.
