# Finite checks and file coverage

The [verification map](../docs/verification-scope.md) relates each mathematical assertion to its proof, finite calculation and enumeration records. The [certificate](certificates/README.md), [catalog](data/README.md) and [provenance](provenance/README.md) guides identify the corresponding files and fields.

`integrity_manifest.json` covers the files in `data/`, `certificates/` and `provenance/`, together with the TSV panel and reduction dictionaries in `figures/`. Its digest is recorded in `integrity_manifest.sha256`. The repository-wide `SHA256SUMS.txt` additionally covers the table aggregates, document sources and other distributed inputs.

The inventory check compares bytes with the selected snapshot. The mathematical checks reconstruct graphs, complexes, reductions and homology groups. Coverage of the large graph universes is recorded by their enumeration aggregates and is regenerated through the [full route](../docs/full-reproduction.md).
