# Counterexamples and enumeration for contractible and dismantlable graphs

This repository contains the graphs, mathematical supplement and computations accompanying *Counterexamples and enumeration for contractible and dismantlable graphs* by Jesús F. Espinoza, Martín Eduardo Frías-Armenta, Rosalía G. Hernández-Amador and Héctor A. Hernández-Hernández.

The article constructs graphs on 13 and 14 vertices that refute the minimum orders proposed in Conjectures 14 and 15 of [Dochtermann, Espinoza, Frías-Armenta and Hernández (2023)](https://doi.org/10.1016/j.disc.2023.113516). It also gives a cardinality table for contractible and dismantlable graph families, with algorithms and proofs of correctness and exhaustiveness.

- [Article](paper/main.pdf) · [LaTeX sources](paper/) · [Citation information](ARTICLE.md)
- [Mathematical supplement](supplement/main.pdf) · [Results and notation](docs/results.md)
- [Examples](docs/examples.md) · [Reproduction guide](docs/reproduction.md)

## The examples

A graph is **I-contractible** if it can be transformed into one vertex by vertex and edge additions and deletions whose tested neighbourhoods are themselves I-contractible. **Strong I-contractibility** requires a reduction by deletions alone, with the same condition imposed recursively on the neighbourhoods used. Write $\mathfrak I$ and $\mathfrak I_S$ for these classes. We call members of $\mathfrak I_S$ **strong**, and an operation **admissible** when its tested neighbourhood is strong. Homology of a graph means homology of its clique complex, whose simplices are the cliques. A graph lies in $\mathfrak I$ exactly when its clique complex is contractible; a graph in $\mathfrak I_S$ has a collapsible clique complex. [Results and notation](docs/results.md) gives the definitions and references.

The graph $G_{13}$ has vanishing reduced homology over $\mathbb F_2$ and first integral homology $\mathbb Z/3$. Thus it is acyclic over $\mathbb F_2$ but is not I-contractible. Adding $\{4,7\}$, and then $\{5,6\}$, gives two variants with the same homology.

The graph $G_{14}^a$, with 14 vertices and 44 edges, belongs to $\mathfrak I\setminus\mathfrak I_S$. Adding the edge $\{0,1\}$ gives a strong I-contractible graph. The endpoints have a strong common neighbourhood, so deleting this edge is admissible and recovers $G_{14}^a$.

Conjecture 14 proposed minimum order 15 both for $\mathbb F_2$-acyclic non-strong graphs and for members of $\mathfrak I\setminus\mathfrak I_S$. Conjecture 15 proposed minimum order 15 for a strong graph with an admissible edge whose deletion leaves the strong class. The three constructions above refute these proposed bounds, respectively.

The [examples guide](docs/examples.md) gives the labelled graphs, their certificates and the variants of $G_{13}$. To export the 14-vertex example and its extension, run from the repository root:

```bash
python3 generate.py --graph G14a --format json
python3 generate.py --graph G14a --extension --format json
```

## The cardinality table

The [table](data/cardinalities.csv) counts connected graphs up to isomorphism. Rows **3–13 include all connected graphs**; **every column of row 14 is restricted to K4-free graphs**. Separate columns record acyclicity over $\mathbb Z$ and over $\mathbb F_2$.

The classification gives minimum orders 13 for $\mathbb F_2$-acyclic graphs outside $\mathfrak I_S$ and 14 for graphs in $\mathfrak I\setminus\mathfrak I_S$. There are exactly eight K4-free graphs of order 14 in the latter class, with minimum 44 edges. Integral acyclicity and I-contractibility coincide within the universes of the table. [Results and notation](docs/results.md) explains these deductions and the auxiliary finite catalogs.

## Reproduce the calculations

With Python 3.11 or later on a POSIX system, run:

```bash
python3 reproduce.py
```

This command uses the Python standard library. It reconstructs the finite examples and certificates, checks homology and reductions, and compares the table with its recorded sources. It writes a report in a new directory under `results/`. The [reproduction guide](docs/reproduction.md) explains the outputs and provides an interactive notebook.

The finite checks use the supplied graphs and records. To generate the complete graph universes and recalculate the table, follow the [full enumeration guide](docs/full-reproduction.md). That route has substantially larger computing requirements. The [verification map](docs/verification-scope.md) identifies the mathematical arguments, finite checks and enumeration records supporting each result.

## Data and algorithms

| Material | Location |
|---|---|
| Cardinalities, with universes and coefficient columns | [`data/cardinalities.csv`](data/cardinalities.csv) |
| Disc constructions, neighbourhoods and reduction sequences | [`finite/certificates/`](finite/certificates/) |
| Seed graphs, the eight K4-free examples and auxiliary catalogs | [`finite/data/`](finite/data/) |
| Enumeration totals and graphs requiring a separate homology calculation | [`data/`](data/) |
| Enumeration and classification programs | [`v2/`](v2/) |
| Figure data and generators | [`tools/figures/`](tools/figures/) |

See [citation information](ARTICLE.md) when using the results, code or data. Original code is under the [MIT License](LICENSE); the article, supplement, original mathematical notes, data and figures are under [CC BY 4.0](LICENSE-DATA). Third-party material retains its attribution and licence.
