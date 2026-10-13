# Data files

All graphs are given in graph6 format (one per line; lines starting with `#` are comments; tab-separated
extra columns where indicated).  Vertex labels referred to in other files are the 0-based labels of the graph6 string.

| file | content |
|---|---|
| `acyclic_not_strong_13.g6` | The 3 ℤ/2-acyclic graphs on 13 vertices that are not strong I-contractible (exhaustive). First line: the unique stuck one, G13. All have H₁(ℤ) = ℤ/3. |
| `stuck_14_K4free.g6` / `.tsv` | The 51 stuck ℤ/2-acyclic K₄-free graphs on 14 vertices (exhaustive within the K₄-free class). The `.tsv` adds edges, triangles, integer H₁, I-contractibility with the certifying I₄ edge, |Aut|, size of the unfolded disc and its boundary word. |
| `minimal_I_not_strong_14.g6` | The three minimal members of 𝔍 ∖ 𝔍_S (G14a, G14b, G14c) and the strong I-contractible graphs G + e that certify I-contractibility. |
| `I_not_strong_14_closure.tsv` | The 29 graphs in 𝔍 ∖ 𝔍_S on 14 vertices lying in the I₄-closure of the 51 stuck graphs (8 of them K₄-free). |
| `acyclic_not_strong_14_closure.tsv` | The 2,271 ℤ/2-acyclic non-𝔍_S graphs on 14 vertices in that closure (29 contractible, 2,242 with H₁ = ℤ/3). |
| `dunce_hat_15.g6` | Flag dunce hat of DEFH 2023 Fig. 2A and the Fig. 2B graph. |
| `table_cardinalities_raw.txt` | Rows n = 3 … of the extended cardinality table as printed by `atascadas --modo tabla` (local runs for n ≤ 11; cluster logs in `yuca/logs/` for n = 12, 13). |
| `table_cardinalities.csv` | The same table in CSV with English column names. |
