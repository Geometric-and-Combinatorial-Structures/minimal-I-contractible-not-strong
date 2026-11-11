# Article and mathematical supplement

**Jesús F. Espinoza, Martín Eduardo Frías-Armenta, Rosalía G. Hernández-Amador and Héctor A. Hernández-Hernández.** *Counterexamples and enumeration for contractible and dismantlable graphs*.

[Read the article](paper/main.pdf) · [LaTeX sources](paper/) · [Citation metadata](CITATION.cff)

The article develops the 13- and 14-vertex counterexamples, the algorithms for the cardinality table and the proofs of the resulting minimum orders. [Results and notation](docs/results.md) provides a guide to the mathematical statements and their scope.

The [supplement, *Finite closures and graph certificates*](supplement/main.pdf), develops four complementary constructions: admissible-edge closures, natural unfoldings of the 51 stuck K4-free graphs of order 14, a catalog of 20 strictly 2-dismantlable graphs, and the relation with the earlier 15-vertex example. It also proves the integral first-homology presentation used in the finite checks. Its [LaTeX source](supplement/main.tex) and [catalog data](finite/data/) are included.

## Build the documents

From the repository root, with `latexmk` and a TeX installation containing `amsart`, Palatino, Euler and TikZ:

```bash
python3 tools/build_paper.py --output build/paper
python3 tools/build_paper.py --source supplement --output build/supplement
```

Choose a new output directory for each build. The commands compile temporary copies and write the PDF, logs and a source-hash record there. They use the included `main.bbl` files. To regenerate the bibliography in the temporary copy, add `--refresh-bibliography`.

The [bibliography guide](docs/bibliography.md) identifies the principal references and the results used from them. The source records for the documents are described in [provenance](docs/provenance/README.md).
