# Finite certificates

`check_certificates.py` checks every field of the following three records:

- `link_checks.json`: all 70 vertex links of G13, G14a, G14b, G14c and D15, including vertex and edge counts, first Betti numbers and all edge-link size sets. These links are triangle-free, so the first Betti number is edges minus vertices plus connected components.
- `G13_successors.json`: all IS-admissible missing edges in each of the three representative states, their common neighbourhoods, and the isomorphism relating the two first additions. The field is named `IS_admissible`.
- `certificate_replay.json`: four exact one-edge extensions and every subsequent deletion, its current neighbourhood, its edge list, its strong reduction certificate, its tree flag, the consecutive step numbers and the final singleton. Vertex labels are retained throughout. The three displayed traces are also compared field by field with `../figures/trace_steps.tsv`.

`check_disc_hypotheses.py` reconstructs and compares every field of `disc_hypotheses.json`. It checks the five unfolded complexes, incidence conditions, connectedness, every vertex link, boundary cycles, injectivity off the boundary and attaching degree. It reads by default; `--write` is an explicit regeneration mode.

`finite_checks.py` supplies exact strong recursion, exact k-dismantlability recursion, adjacency-preserving automorphism counting, and integer Smith reduction used by the finite table checks. It constructs the integer H1 presentation by contracting a spanning forest, with one generator per non-tree edge and one relation per triangle. No precomputed homology group is used as an input to that calculation.

`test_certificate_integrity.py` exercises the distinct byte-integrity layer. It uses the system temporary directory (or `TMPDIR`) and never writes into the supplied evidence tree. Its output lists the exact number of substitutions tried in every file. The fixed digest manifest covers all bytes; a hash agreement is not a proof of a mathematical claim, nor authentication of a historical run.
