# Reproducing the finite evidence

Run commands from the repository root. A POSIX system and Python 3.11 or later, without `-O` or `-OO`, are required; the deposited routes are tested on Linux. The default route uses only the Python standard library and performs no network or scheduler operations.

```bash
python3 reproduce.py
```

The output directory is new on every invocation. To choose its name:

```bash
python3 reproduce.py --output results/my-check
```

An existing output directory is refused. `report.txt` gives a short result; `report.json` records the route, Python version, source-manifest digest, required checks, exit codes and elapsed times. Separate output files retain the individual checker results. The input manifest is checked before and after execution.

## Required checks

The finite driver runs eleven checks: the finite byte inventory; five disc presentations; witness links and strong reductions; all 51 natural unfoldings; the three small pruned closures and stored admissible paths; the auxiliary catalog invariants and integral first homology; the four attributed Adamaszek encodings; retained small K4-free records; lower-order provenance consistency; the supplied 643-graph reduction set; and all 144 table entries with the complete finite residual adjudication.

The top-level command additionally verifies the unchanged article and migration inventory, then runs secondary catalog comparisons, historical source identities, both generated mathematical tables, witness-export tests, semantic certificate-mutation tests, 46,913 specified byte substitutions and file-appending tests and all code cells of the example notebook. These stages are required, and no missing dependency is silently skipped. The report records elapsed time for each stage. The top-level subprocess limit is configurable with `--timeout` (seconds, greater than zero and at most 100,000). The eleven-stage finite driver applies that limit to each of its stages and receives twelve times the limit overall; the other required stages each receive one limit. The interface tests inherit it for their subprocesses. An expired check fails rather than certifying a partial result. On POSIX systems the driver terminates the timed-out process group and retains its captured output. The working checkout must be writable for generated test and notebook outputs.

The source inventory excludes root Git metadata, root `build/`, `results/` and `.venv/`, the legacy generated directories `v2/build/` and `v2/tests/results/`, Python bytecode and notebook checkpoints, `.DS_Store`, LaTeX intermediates within the two document directories, the legacy local binary `src/atascadas`, and root `quick-verification.json`. A directory named `build` or `results` inside the data is still checked as an input. New command outputs inside the repository are restricted to subdirectories of root `results/` or `build/`. The inventory includes the distributed source, data, notes and PDFs. To verify the inventory alone:

```bash
python3 tools/integrity.py
```

Maintainers can deliberately regenerate it with `python3 tools/integrity.py --write` after reviewing changes. Hashes detect changes relative to a selected version; they do not authenticate an execution or establish mathematical correctness.

## Current C implementation

```bash
python3 reproduce.py --extended --cc gcc --output results/extended
```

This route adds the actual C functions in `v2/src/atascadas_v2.c` to the finite checks. It compares them with direct recurrences on all 1,100 labelled graphs of orders 0–5, including all induced masks and all possible first vertex and edge deletions. The evidence covers 33,867 masked states. It includes empty graphs, singleton graphs and empty neighbourhoods. The harness does not modify the classifier source. This is a bounded implementation check, not a proof of arbitrary machine code or an independent large census.

Continuous integration runs this route on Python 3.11 and 3.13. Compiler outputs and reports remain under `results/`. The larger historical regression suite is described in [`v2/README.md`](../v2/README.md).

## Examples, figures and documents

`generate.py` exports witnesses without external dependencies. The [examples guide](examples.md) gives the formats and label conventions. For an interactive walkthrough, make a writable copy first with `python3 tools/copy_notebook.py`, then open `results/notebook/reproduce.ipynb` in Jupyter. Jupyter is needed only for the interface. Its autosaved output belongs in that copy; the distributed notebook remains an inventoried input. The distributed notebook's plain-Python cells also run without saving with:

```bash
python3 tests/run_notebook.py
```

The manuscript already contains the checked TikZ sources. [`tools/figures/README.md`](../tools/figures/README.md) documents regeneration and the additional NetworkX/SymPy verification route. Build the article and supplement as described in [`ARTICLE.md`](../ARTICLE.md).

`./verify.sh` remains a compatibility entry point for the eleven finite checks alone. It prints a JSON report to standard output and does not run the new interface or notebook tests.

## Large computations and historical evidence

The [full route](full-reproduction.md) specifies graph generation, classification, integral homology adjudication and aggregation. It is deliberately separate from the commands above because its universes are large. It records the requirements for a valid run, including complete residue coverage and real successful exits.

The quick route rechecks the deposited finite exceptions and the arithmetic connection to retained aggregate records. It does not generate every graph counted by those records. Full per-residue production archives remain in the authors' project archive; this repository contains a selected reproducible core. A full independent recount using a different classifier remains deferred. See the [assertion-to-evidence map](verification-scope.md).

## Regenerating the complete finite closure catalog

The 51-seed closure can be regenerated locally without a graph-universe census:

```bash
python3 tools/reproduce_closures.py --cc gcc --labelg /path/to/labelg --output results/closures51
```

This route requires nauty `labelg` and the C11 compiler. It compares the complete non-strong class set with the 2,271-row catalog and records successful process exits and unchanged input hashes. The recorded local run and its precise scope are described in [`verification/closures51/`](../verification/closures51/). The default route checks its finite data and independently regenerates the three smaller positive-seed closures.

## Git history and source archives

Every route checks the distributed snapshot. When Git and the baseline commit are available, it also compares the complete migration inventory with that historical tree. Source ZIPs and shallow clones lack that optional historical object comparison; both `report.txt` and `report.json` state this explicitly. For a shallow clone, `git fetch --unshallow` makes the historical comparison available. Continuous integration fetches the complete history and passes `--require-git-baseline`, so its historical comparison is mandatory. A source archive omits that option.
