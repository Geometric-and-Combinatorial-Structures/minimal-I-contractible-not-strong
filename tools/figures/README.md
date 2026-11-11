# Witness figures and tables

`witness_data.json` records the labelled edges, reduction sequences and vertex coordinates for the article's figures. The generators keep the combinatorial data separate from the drawing coordinates and check every emitted edge set.

From this directory, run:

```bash
python3 make_witness_figures.py --check
python3 make_witness_tables.py --check
python3 verify_witnesses.py
```

The first two commands use the Python standard library. They generate three figure sources and four tables under `build/generated-paper/` at the repository root and compare them with the article's sources. The verifier requires NetworkX and SymPy, with versions specified in `requirements.txt`. It computes integral first homology from a spanning-tree cycle basis, replays the reductions and reconstructs the disc by successive triangle attachments. Reports go under `build/verification/witnesses/`.

The disc presentation of $G_{13}$, the graph $G_{13}$ and $G_{14}^a+\{0,1\}$ panels have 48, 40 and 45 edges, respectively. In the last panel the added edge is dashed; $G_{14}^a$ itself has 44 edges.

The TikZ panels use mathematical labels in Palatino/Pazo, at 8 pt, and a minimum node diameter of 5.8 mm. Compile them at their specified size. The local `jfef-mis-grafos` styles are loaded by the article preamble. The [figure workflow](../../.github/workflows/reproduce.yml) checks the generated sources and witness certificates.
