# Finite evidence coverage

The operational coverage matrix is [verification-scope.md](../docs/verification-scope.md). `data/README.md`, `certificates/README.md` and `provenance/README.md` give the field-level descriptions. Scripts, metadata and selected normalized source records are all included in the finite byte manifest; the separately maintained table aggregates are covered by the repository-wide manifest.

No field is described as mathematically verified merely because its digest agrees. The executable quick check reconstructs the finite mathematical objects. Per-residue coverage of large historical runs is stated from their retained aggregate records, not replayed in the quick check.
