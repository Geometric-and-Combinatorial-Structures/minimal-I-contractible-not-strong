# Counterexamples and enumeration for contractible graphs

Can every I-contractible graph be reduced to a point by strong contractible deletions? The accompanying article answers this question negatively and separates integral acyclicity from acyclicity over the field with two elements. It refutes Conjectures 14 and 15 of [Dochtermann, Espinoza, Frías-Armenta and Hernández (2023)](https://doi.org/10.1016/j.disc.2023.113516) and establishes a table of cardinalities by exact graph algorithms.

This repository contains the examples, algorithms, data and proofs that support the article, together with a mathematical supplement on finite closures and auxiliary catalogs.

- [Read the article](paper/main.pdf) · [LaTeX sources](paper/) · [Article and citation information](ARTICLE.md)
- [Read the mathematical supplement](supplement/main.pdf) · [Supplement sources](supplement/main.tex)
- [Explore examples](docs/examples.md) · [Notebook guide](docs/reproduction.md) · [Understand the results](docs/results.md)

## One edge makes the difference

The graph $G_{14}^a$ has 14 vertices and 44 edges. It belongs to $\mathfrak I$ but not to $\mathfrak I_S$. Adding the edge $\{0,1\}$ gives a strong I-contractible graph. The reverse deletion is admissible and leaves the strong class: this is the counterexample to Conjecture 15.

Export the pair, preserving the labels in the article:

```bash
python3 generate.py --graph G14a --format json
python3 generate.py --graph G14a --extension --format json
```

The 13-vertex witness `G13` instead has first integral homology $\mathbb Z/3$ and vanishing reduced homology over $\mathbb F_2$. Its disc construction explains the torsion. The [examples guide](docs/examples.md) connects each construction to its certificate and proof.

## Reproduce the finite results

Clone the repository, enter its directory, and run:

```bash
python3 reproduce.py
```

On a POSIX system (tested on Linux), Python 3.11 or later and its standard library are sufficient. The command creates a new directory under `results/` containing `report.txt`, `report.json` and the check outputs. It checks the witnesses, reduction traces, finite closures, unfoldings, homology, table-source correspondence, notebook and input hashes. A failed or incomplete required check returns a nonzero exit code.

To include a comparison of the current C classifier with direct mathematical recurrences on every labelled graph of order at most five:

```bash
python3 reproduce.py --extended --cc gcc
```

This additional check requires a C11 compiler. Neither command repeats the large census. [Reproduction](docs/reproduction.md) describes both routes, their requirements and expected outputs. [Full reproduction](docs/full-reproduction.md) gives the generation, classification and aggregation procedure for the table, with its substantially larger resource requirements.

## What is counted

All entries count connected graphs up to isomorphism. Rows **3–13 are unrestricted**. **Every column of row 14 counts only K4-free graphs**. The table separates acyclicity over $\mathbb Z$ from acyclicity over $\mathbb F_2$.

| Result | Scope |
|---|---|
| Minimum order for $\mathbb F_2$-acyclic graphs outside $\mathfrak I_S$: 13 | All connected graphs |
| Minimum order for $\mathfrak I\setminus\mathfrak I_S$: 14 | All graphs |
| Eight classes in $\mathfrak I\setminus\mathfrak I_S$, with minimum 44 edges | K4-free graphs of order 14 |
| Equality of integral acyclicity and I-contractibility | Only the classified universes above |
| 2,271 non-strong classes from the 51 stuck seeds | The stated admissible-edge closures |

The complete large enumerations are represented by selected historical aggregate records and their finite exceptional sets. The finite verifiers use code separate from the census classifier; they do not constitute an independent recount of its entire input universes. [Verification scope](docs/verification-scope.md) connects each assertion to its evidence and states the limits of the retained production records.

## Find the material

| Location | Contents |
|---|---|
| [`data/cardinalities.csv`](data/cardinalities.csv) | Table with universes and coefficient columns |
| [`finite/certificates/`](finite/certificates/) | Witnesses, disc presentations, links and reductions |
| [`finite/data/`](finite/data/) | The 51 seeds, eight K4-free positive exceptions, 20 strictly 2-dismantlable graphs, and closure catalogs |
| [`data/census/`](data/census/) | Selected aggregates, all residuals and their homology adjudications |
| [`v2/`](v2/) | Current complete-state classifier and partition driver |
| [`verification/`](verification/) | Bounded implementation checks and historical source comparisons |
| [`tools/figures/`](tools/figures/) | Exact witness data, TikZ generators and drawing verification |
| [`docs/provenance/`](docs/provenance/) | Selection and migration records |

[Review and verification](docs/review.md) records the adversarial review scope and local validation.

The paper is a complete draft for author review. It has no assigned arXiv identifier or publication DOI. The [citation file](CITATION.cff) records the authors and manuscript title. Original code is under the [MIT License](LICENSE); original mathematical notes, data and figures are under [CC BY 4.0](LICENSE-DATA). Third-party works retain their own licenses and attribution.
