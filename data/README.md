# Data files

All graphs are given in graph6 format (one per line; lines starting with `#` are comments; tab-separated
extra columns where indicated).  Vertex labels referred to in other files are the 0-based labels of the graph6 string.

| file | content |
|---|---|
| `acyclic_not_strong_13.g6` | The 3 ℤ/2-acyclic graphs on 13 vertices that are not strong I-contractible found by the recorded search and table run; that there are no others is subject to the computational hypotheses H12, Hcasi and H13 of the paper (those runs used the hash-keyed memo of `src/atascadas.c`, audit finding H-01, and are being recomputed with an exact key). First line: the only stuck one, G13. All have H₁(ℤ) = ℤ/3. |
| `stuck_14_K4free.g6` / `.tsv` | The 51 stuck ℤ/2-acyclic K₄-free graphs on 14 vertices (the complete output of the recorded search over the K₄-free class; that there are no others is subject to the hypotheses H12, Hcasi and H14 of the paper and to the pending re-run of the search with pipeline v2). The `.tsv` adds edges, triangles, integer H₁, I-contractibility with the certifying I₄ edge, |Aut|, size of the unfolded disc and its boundary word. |
| `minimal_I_not_strong_14.g6` | The three stuck K₄-free members of 𝔍 ∖ 𝔍_S on 14 vertices, G14a, G14b, G14c (14 is the minimum order of 𝔍 ∖ 𝔍_S subject to H12, Hcasi and H13) and the strong I-contractible graphs G + e that certify I-contractibility. |
| `I_not_strong_14_closure.tsv` | The 29 graphs in 𝔍 ∖ 𝔍_S on 14 vertices lying in the I₄-closure of the 51 stuck graphs (8 of them K₄-free), computed as the pruned closure: graphs in 𝔍_S are not expanded, which loses no graph outside 𝔍_S because I₄ additions preserve 𝔍_S. This finite computation is certified; that every K₄-free graph of 𝔍 ∖ 𝔍_S on 14 vertices is among them depends on the completeness of `stuck_14_K4free.g6`. |
| `acyclic_not_strong_14_closure.tsv` | The 2,271 ℤ/2-acyclic non-𝔍_S graphs on 14 vertices in that closure (29 contractible, 2,242 with H₁ = ℤ/3). |
| `closure_G14a.tsv` | The I₄-closure of G14a as computed by `atascadas --modo cerradura` (graphs outside 𝔍_S are expanded; graphs in 𝔍_S are recorded but not expanded): 48 pairwise non-isomorphic graphs, 16 outside 𝔍_S and 32 in 𝔍_S; the latter are the 32 examples for Theorem D (Conjecture 15). |
| `strictly_2dis_12.g6` / `.tsv` | The 20 connected graphs on 12 vertices that are 2-dismantlable but not 1-dismantlable (the complete output of the `2dis_no_1dis` run over all connected 12-vertex graphs; that there are no others is subject to the integrity of the n = 12 runs, which the external audit has not yet certified; none on ≤ 11 vertices, verified independently by the audit); `.tsv` adds edges, triangles, K₄ count, clique number, min/max degree, \|Aut\|. 2-dismantling sequences in `certificates/strictly_2dis_12_traces.txt`. Identical to the list of the authors' 2025 computation. |
| `dunce_hat_15.g6` | Flag dunce hat of DEFH 2023 Fig. 2A and the Fig. 2B graph. |
| `table_cardinalities_raw.txt` | Rows n = 3 … of the extended cardinality table as printed by `atascadas --modo tabla` (local runs for n ≤ 11; cluster logs in `yuca/logs/` for n = 12, 13). |
| `table_cardinalities.csv` | The same raw counts in CSV with English column names. The header explains the 3 graphs of order 13 counted as I-undecided (raw counter, kept as printed). |
