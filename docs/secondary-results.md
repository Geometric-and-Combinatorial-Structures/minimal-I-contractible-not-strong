# Secondary finite results

## Naming and scope

Repository identifiers use plain text: `G13` denotes the manuscript's G_13, and `G14a`, `G14b`, `G14c` denote G_14^a, G_14^b, G_14^c, respectively. The three order-13 variants are G_13 and its two successive admissible-edge additions, as constructed in the manuscript and reconstructed by `tools/check_cardinalities.py`.

The catalogs below preserve auxiliary finite results and the data needed to inspect them. Their automorphism orders are recorded invariants, not a new analysis of symmetries or an additional premise for the classification of eight K4-free classes. 

## Pruned admissible-edge closures

For a graph G, explore every missing edge whose common neighborhood belongs to I_S. Identify isomorphic results and stop expanding a state when it first belongs to I_S. Each branch terminates because an edge is added at every step. Exact tests of I_S and graph isomorphism make this a finite exhaustive procedure on the stated search space.

The pruning is valid for the purpose of enumerating non-strong descendants: if H is in I_S and an edge is admissibly added, the resulting graph is in I_S by the defining gluing rule. Induction shows that no later admissible addition leaves I_S. The stopping boundary therefore omits no non-strong descendant, but it is not the full set of strong descendants.

The closures of G14a, G14b and G14c have respectively 16/32, 10/16 and 5/8 non-strong/first-strong classes. Their non-strong union has 29 isomorphism classes, of which eight are K4-free. Each retains a seed and an ordered admissible-addition path. The certificates of the seeds show that all 29 belong to I. The 32 first-strong classes for G14a give examples with an admissible edge deletion leaving I_S. They are not asserted to exhaust all such examples.

The other 21 classes in this 29-class union contain a K4. Their collapsibility is not examined here; that question is reserved for separate work. Their inclusion as finite data makes no assertion about a complete unrestricted order-14 classification.

The 51 stuck K4-free order-14 seeds have a union of 2,271 non-strong classes in their pruned closures. The three I-contractible seeds generate the 29 classes above. The other 48 seeds have H1=Z/3; admissible additions preserve integral homology, so their descendants cannot belong to I. Exact Smith computations check H1 for every catalog entry. Overlaps are removed up to isomorphism. These 2,271 graphs do not exhaust all F2-acyclic non-strong order-14 graphs: only 277 of the 633 K4-free exceptions occur in the closure union, and the 29 I graphs do not assert an unrestricted order-14 classification.

## Other finite catalogs

`finite/data/strictly_2dis_12.tsv` has the 20 isomorphism classes in 2-Dis outside 1-Dis at order 12. The finite checker verifies their membership and automorphism orders; the full table supplies the completeness and minimality statements. 

`finite/data/D15_label_correspondence.tsv` relates D15 to Figure 2A of Dochtermann et al. (2023). The checker compares all 32 published triangles after relabeling, as well as the graph's local obstruction and its one-edge extension certificate. This is a comparison with the earlier example, not a claim of a new 15-vertex minimum.

The four Adamaszek order-11 encodings are attributed in `finite/data/adamaszek_11_homology.json`. Their finite H1 check returns Z/2. It does not reproduce that paper's classification or convert a general odd-torsion problem into the F2-acyclic problem studied here.
