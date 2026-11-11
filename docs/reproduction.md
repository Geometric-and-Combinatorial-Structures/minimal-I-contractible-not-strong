# Reproduce the finite calculations

This route reconstructs the examples and the finite catalogs and checks their relation to the cardinality table. It uses the graphs and enumeration records supplied in the repository. Generating every graph in a table row is a separate, larger calculation described in [full enumeration](full-reproduction.md).

## Run the checks

Clone or download the repository and open a terminal in its root directory. With Python 3.11 or later on a POSIX system, run:

```bash
python3 reproduce.py
```

The route uses the Python standard library and is tested on Linux. Run Python without `-O` or `-OO`, since the checks use assertions. The checkout must be writable for the generated reports and notebook outputs.

The command creates a new directory under `results/` and reports its location. To choose a name:

```bash
python3 reproduce.py --output results/my-check
```

Use a new directory for each invocation. Open `report.txt` for the overall result and the outcome of each check. `report.json` additionally records the commands, return codes, elapsed times and input identities. Individual outputs are retained alongside these reports. A failed or incomplete required check gives a nonzero exit code.

## What is calculated

| Mathematical object | Calculation |
|---|---|
| Five designated examples | Disc presentations, neighbourhood obstructions and complete reduction sequences |
| The 51 stuck K4-free graphs | Graph invariants, integral first homology and all natural unfoldings |
| Closures of the three I-contractible seeds | All admissible additions up to the first strong graph, with isomorphism identification |
| The 2,271-class closure union | Stored addition paths, first homology, pairwise nonisomorphism and the 29/2,242 partition |
| The 20 strictly 2-dismantlable graphs | Membership, nonmembership and automorphism orders |
| Small K4-free reduction set | All 643 supplied connected graphs of orders 2–7 and the almost-stuck criterion |
| Cardinality table | All 144 entries against their sources; the three order-13 and 625 order-14 torsion cases; the eight positive order-14 classes |

The route also checks the four attributed Adamaszek examples, correspondence with historical records, generated tables, witness exports and the notebook. Input inventories check that the tested files are the distributed ones; tests with deliberately altered certificates check that the verifiers reject such alterations. The [verification map](verification-scope.md) relates these calculations to the proofs and enumeration records.

The three positive-seed closures are regenerated in this route. To regenerate the **full 51-seed closure**, install a C11 compiler and nauty `labelg`, then run:

```bash
python3 tools/reproduce_closures.py --cc gcc --labelg /path/to/labelg --output results/closures51
```

This command compares the generated non-strong class set with the 2,271-row catalog. The [closure guide](../verification/closures51/README.md) describes the output and the recorded comparison.

## Interactive examples

Create a working copy of the notebook:

```bash
python3 tools/copy_notebook.py
```

Open `results/notebook/reproduce.ipynb` in Jupyter. It computes the first homology of `G13`, compares `G14a` with its one-edge extension and examines the two coefficient columns of the table. Jupyter is needed for this interactive interface; the cells themselves use only the standard library. They also run from the terminal with:

```bash
python3 tests/run_notebook.py
```

Keep interactive outputs in the working copy, since the distributed notebook is part of the input inventory. The [examples guide](examples.md) describes the graph exporter and the mathematical meaning of its outputs.

## Compare the two implementations

To include a comparison of the C classifier with direct mathematical recurrences, run:

```bash
python3 reproduce.py --extended --cc gcc --output results/extended
```

This needs a C11 compiler. It compares all 1,100 labelled graphs of orders 0–5 and their 33,867 induced states, including empty graphs, singletons, empty neighbourhoods and every possible first deletion. This tests the implementations on that finite domain; the algorithmic proofs and the large enumeration records have the separate roles described in the [verification map](verification-scope.md).

## Figures and documents

The [figure guide](../tools/figures/README.md) describes how to regenerate the TikZ drawings and check their exact edge sets. Its additional witness verifier uses NetworkX and SymPy. The [document guide](../ARTICLE.md#build-the-documents) gives commands to build the article and supplement from their LaTeX sources.

## Run options and input records

The default time limit is applied separately to the required checks. `--timeout SECONDS` accepts a positive value at most 100,000; an expired check fails and retains its captured output. Details of the stage limits and output locations are in [maintainer guidance](../CONTRIBUTING.md#checks-and-output-directories).

Every route compares the distributed files with their recorded hashes. With a complete Git history it also checks the import records against the historical baseline. Source archives and shallow clones omit that historical-object comparison and identify the omission in the report. To require it, use `--require-git-baseline`; for a shallow clone, first run `git fetch --unshallow`. GitHub Actions fetches the complete history and requires this comparison.

The compatibility entry point `./verify.sh` runs the eleven checks in `finite/` and prints their JSON report. `reproduce.py` additionally runs the repository, interface and notebook checks described above.
