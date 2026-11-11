# Finite graphs, constructions and certificates

This directory contains the five designated examples (`G13`, `G14a`, `G14b`, `G14c`, `D15`), their certificates and the finite catalogs developed in the [article](../paper/main.pdf) and [supplement](../supplement/main.pdf). Graph6 encodings use vertex labels starting at zero; the displayed reductions and figures use the corresponding labels.

| Material | Guide |
|---|---|
| Disc presentations, neighbourhood obstructions and reductions | [Certificates](certificates/README.md) |
| The 51 seeds, eight K4-free examples, 20 strictly 2-dismantlable graphs and closure catalogs | [Catalog data](data/README.md) |
| Enumeration totals, source identities and execution records | [Provenance](provenance/README.md) |

For the finite reproduction route, run `python3 reproduce.py` from the repository root. The compatibility command `./verify.sh`, also run from the root, invokes the eleven checks within this directory. Individual commands are given in the guides above.

The [verification map](../docs/verification-scope.md) explains how these finite calculations combine with the mathematical proofs and exhaustive enumerations. [Coverage](VERIFICATION_COVERAGE.md) identifies the file inventories used by the checks.
