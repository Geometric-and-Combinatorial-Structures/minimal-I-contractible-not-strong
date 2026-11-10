# Results and their proofs

The [article](../paper/main.pdf) contains the counterexamples, the mathematical classification algorithms and the cardinality table. The [supplement](../supplement/main.pdf) develops the auxiliary finite constructions. The table below is a guide to those arguments and to the corresponding data.

| Statement | Mathematical treatment | Rechecked finite evidence |
|---|---|---|
| G13 is F2-acyclic with integral H1 = Z/3 | Article: disc presentation and degree-three attachment | Five disc hypotheses; exact integral homology |
| G14a, G14b, G14c belong to I outside the strong class | Article: local obstructions, admissible additions and reductions | All links and reduction traces |
| One admissible edge deletion can leave the strong class | Article: the extension of G14a | Extension certificate and exact strong tests |
| The table has separate F2 and integral columns | Article: algorithms, coverage and residual partition | 144 source comparisons, three order-13 and 625 order-14 torsion residuals, eight positive order-14 classes |
| Three finite closures have non-strong/first-strong counts 16/32, 10/16 and 5/8 | Supplement: closure theorem | Entire three-seed closures regenerated with exact isomorphism tests |
| The non-strong union from the 51 seeds has 2,271 classes, 29 in I | Supplement: specified seed-generated catalog | Stored paths and integer H1; all 51 closures regenerated with the current C core |
| The 51 natural unfoldings consist of 48 discs, two annuli and one disc plus annulus | Supplement: gluing construction and surface recognition | Every corner class, vertex link and boundary component reconstructed |
| Exactly 20 strictly 2-dismantlable graphs occur at order 12 | Article's table and supplement's catalog argument | Membership, nonmembership, pairwise non-isomorphism checks and invariants |
| D15 agrees with the previously published example | Supplement: label correspondence | All 32 triangles and the certifying edge compared |

## Reading the finite closure counts

A closure here allows successive additions of missing edges with strong common neighbourhood. Expansion stops at the first strong state on a path. Isomorphic states are identified. Once a state is strong, further admissible edge additions remain strong, so this stopping rule loses no non-strong descendants.

The union from the three contractible seeds has 29 non-strong classes, eight of them K4-free. The other 21 contain a K4; their simplicial collapsibility is not classified here. The 48 torsion seeds contribute the remaining 2,242 classes in the larger 2,271-class union. These are specified finite closures, not an unrestricted enumeration of all order-14 graphs.

The 32 boundary classes for G14a each supply an admissible edge deletion that exits the strong class. The boundary records all first strong states in that pruned closure, not every strong graph reachable by longer additions.

## Scope of computation

Rows 3–13 of the table count all connected isomorphism classes. Every column of row 14 is K4-free. The global minimum order 14 follows from the unrestricted smaller rows and the explicit witness. The eight classes and the 44-edge minimum use the restricted row. Equality of integral acyclicity and I-contractibility is justified only in those classified universes.

The exact finite verification is separate from the historical census. It checks the supplied exceptional graphs and the source correspondence of the counts. The [verification map](verification-scope.md) and [full reproduction procedure](full-reproduction.md) give the evidence and limits behind each use. The [secondary-results note](secondary-results.md) records the selection of auxiliary material and excluded lines of research.
