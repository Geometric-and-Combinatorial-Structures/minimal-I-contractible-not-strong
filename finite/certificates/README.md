# Certificates for the examples

The records in this directory specify the constructions and reductions used to prove the properties of `G13`, `G14a`, `G14b`, `G14c` and `D15`. The [examples guide](../../docs/examples.md) identifies these graphs and their role in the conjectures. Vertex labels are preserved throughout each reduction.

| Record | Mathematical content |
|---|---|
| [`disc_hypotheses.json`](disc_hypotheses.json) | Five disc presentations, their boundary identifications and attaching degrees |
| [`link_checks.json`](link_checks.json) | All 70 vertex neighbourhoods and the edge-neighbourhood size sets |
| [`G13_successors.json`](G13_successors.json) | Every admissible missing edge in the three order-13 states, the common neighbourhoods and the isomorphism relating the first additions |
| [`certificate_replay.json`](certificate_replay.json) | Four one-edge extensions and each subsequent deletion, with its current neighbourhood and reduction certificate |

The vertex neighbourhoods in `link_checks.json` are triangle-free, so their first Betti numbers are edges minus vertices plus connected components. In the reduction record, every neighbourhood is evaluated before its deletion; the final state is a singleton. The displayed traces are also compared with `../figures/trace_steps.tsv`.

## Check the constructions

From the repository root:

```bash
python3 -P finite/certificates/check_certificates.py
python3 -P finite/certificates/check_disc_hypotheses.py
```

The first command checks all fields of the neighbourhood, successor and reduction records. The second reconstructs triangles, connected components, vertex links and boundary cycles, checks injectivity away from the boundary and computes the attaching degree. Both run in the standard finite reproduction route.

`finite_checks.py` supplies the recursive strong and k-dismantlability tests, automorphism counting and the integer first-homology calculation. The latter uses a spanning forest, with one generator per non-tree edge and one relation per triangle; its proof is in the supplement.

## Regeneration and input checks

`check_disc_hypotheses.py --write` regenerates the disc record. Use a separate working copy and update the finite inventory after an intentional change. `test_certificate_integrity.py` tests specified byte substitutions and file appending in a temporary directory, reporting the number tried for each file. The [coverage note](../VERIFICATION_COVERAGE.md) distinguishes those input checks from the mathematical calculations.
