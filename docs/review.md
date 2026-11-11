# Validation records

The mathematical proofs, finite calculations and complete enumerations have distinct roles, described in the [verification map](verification-scope.md). The [reproduction guide](reproduction.md) gives the commands for the finite calculations; [GitHub Actions](https://github.com/Geometric-and-Combinatorial-Structures/minimal-I-contractible-not-strong/actions/workflows/reproduce.yml) runs them on Python 3.11 and 3.13 and checks the document builds and figure generation.

The retained validation records include:

- [Source comparisons for the small-order enumerations](../verification/historical_small_orders/README.md).
- [Comparison of the C classifier with direct mathematical recurrences](../verification/current_recurrences/README.md).
- [Regeneration of all 51 finite closures](../verification/closures51/README.md), giving the deposited 2,271-class set.
- [Adversarial-review inputs](../verification/review/snapshots.json), identifying the files or diffs supplied in six completed reviews of the repository preparation.

Those review records identify the versions examined. Their assessments were considered alongside direct inspection and executable checks.

The classifier and partition-driver [regression suite](../v2/README.md#regression-suite) covers equivalence, incomplete or malformed input, failed processes and aggregation. The finite route also tests deliberately altered certificates and input files. Reports retain the individual outcomes so that a reader can distinguish a completed check from a missing or failed one.
