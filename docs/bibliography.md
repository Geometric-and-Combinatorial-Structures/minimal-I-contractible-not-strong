# Bibliography and mathematical dependencies

The article's bibliography is in [`paper/refs.bib`](../paper/refs.bib), and the supplement's is in [`supplement/refs.bib`](../supplement/refs.bib). The following references provide the principal background results.

| Reference | Use in this work |
|---|---|
| A. Dochtermann, J. F. Espinoza, M. E. Frías-Armenta and H. A. Hernández, “Minimal graphs for contractible and dismantlable properties”, *Discrete Mathematics* 346 (2023), 113516. [DOI](https://doi.org/10.1016/j.disc.2023.113516) | Conjectures 14–15, the hierarchy of graph families and the 15-vertex example |
| J. F. Espinoza, M. E. Frías-Armenta and H. A. Hernández-Hernández, “Collapsibility and homological properties of I-contractible transformations”, *Boletín de la Sociedad Matemática Mexicana* 28 (2022), 42. [DOI](https://doi.org/10.1007/s40590-022-00434-7) | Strong I-contractibility and collapsibility |
| A. Dochtermann and T. Matsushita, “Simple homotopy of flag simplicial complexes and contractible contractions of graphs”, *Topology and its Applications* 367 (2025), 109326. [DOI](https://doi.org/10.1016/j.topol.2025.109326) | Contractible graph transformations and simple homotopy; the equivalence between I-contractibility and contractibility of the clique complex |
| M. Adamaszek, “Small flag complexes with torsion”, *Canadian Mathematical Bulletin* 57 (2014), 225–230. [DOI](https://doi.org/10.4153/CMB-2013-032-9) | Classification of small flag complexes with torsion in first homology |

The reference to Corollary 1.5 of Dochtermann–Matsushita uses the numbering in the [author version](https://arxiv.org/abs/2312.10976v2). Graph generation and canonical labelling use nauty; see McKay and Piperno, “Practical graph isomorphism, II”, *Journal of Symbolic Computation* 60 (2014), 94–112 ([DOI](https://doi.org/10.1016/j.jsc.2013.09.003)).

The repository includes four graph encodings attributed to Adamaszek and recalculates their first integral homology as $\mathbb Z/2$. The supplement identifies `D15` with the earlier example by a vertex bijection and equality of all 32 triangles. The [data dictionary](../finite/data/README.md#earlier-examples) gives the corresponding files and attribution.
