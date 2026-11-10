# Finite mathematical evidence

Run `../verify.sh` from the repository root, or the individual scripts described in `data/README.md` and `certificates/README.md`. Every graph6 encoding uses zero-based vertices. Geometric drawings may relabel those vertices; the paper supplies the correspondence.

The five designated graphs are G13, G14a, G14b, G14c and D15. G13 has integer H1=Z/3 and is F2-acyclic. G14a is the 14-vertex, 44-edge I-contractible non-strong witness developed in the manuscript. G14b and G14c account for the other contractible stuck seeds. D15 is the 15-vertex published comparison example.

The 51-row, eight-row and 20-row catalogs, all 2,271 pruned-closure classes and the three complete finite closure records are included. Their exhaustiveness statements have different scopes: see `../docs/secondary-results.md`. The evidence files are not a new exhaustive enumeration of all graphs.

`check_integrity.py` verifies the byte inventory in `integrity_manifest.json`; the manifest digest is in `integrity_manifest.sha256`. A mathematical verifier and an integrity verifier answer different questions. [Coverage](VERIFICATION_COVERAGE.md) identifies the distinction.
