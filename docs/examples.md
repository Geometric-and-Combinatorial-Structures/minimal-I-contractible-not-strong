# The graphs and their certificates

The examples distinguish acyclicity over $\mathbb F_2$, integral acyclicity and strong I-contractibility. Homology below is homology of the clique complex. The identifiers in the first column are the names accepted by `generate.py`; their vertex labels agree with the article and the certificate files.

| Identifier | Vertices | Edges | Integral first homology | Edge giving a strong extension |
|---|---:|---:|---|---|
| `G13` | 13 | 40 | $\mathbb Z/3$ | — |
| `G14a` | 14 | 44 | $0$ | {0,1} |
| `G14b` | 14 | 45 | $0$ | {0,3} |
| `G14c` | 14 | 45 | $0$ | {2,3} |
| `D15` | 15 | 46 | $0$ | {9,12} |

All five graphs are non-strong. For each of the last four, the displayed edge has a strong common neighbourhood, and adding it produces a strong graph. Reversing the addition proves I-contractibility of the original graph. The article gives the reductions for the order-14 examples; the supplement relates `D15` to the example in [Dochtermann et al. (2023)](https://doi.org/10.1016/j.disc.2023.113516).

`G13` has a different role: its clique complex is obtained from a disc by a boundary attachment of degree three. It is acyclic over $\mathbb F_2$ but has nonzero integral first homology, so it is not I-contractible. Its two variants are obtained by adding $\lbrace 4,7\rbrace$ and then $\lbrace 5,6\rbrace$. The admissible additions and their common neighbourhoods are recorded in [`G13_successors.json`](../finite/certificates/G13_successors.json).

## Export a labelled graph

Run from the repository root:

```bash
python3 generate.py --graph G13
python3 generate.py --graph G14a --format json
python3 generate.py --graph G14a --extension --format edges
```

The default format is `graph6`, a compact encoding of a labelled simple graph. `json` includes its vertices, edges, order, size and encoding. `edges` gives one edge per line, with columns `u` and `v`. Output is written to standard output; labels are preserved. `--extension` adds the edge in the table and is available for `G14a`, `G14b`, `G14c` and `D15`.

## Calculate the first homology

The finite verifier presents integral first homology using one generator for each edge outside a spanning forest and one relation for each triangle. The supplement proves this presentation. For example, from the repository root:

```python
import json, subprocess, sys
sys.path.insert(0, 'finite/certificates')
from finite_checks import decode, h1

g = json.loads(subprocess.check_output(
    [sys.executable, 'generate.py', '--graph', 'G13', '--format', 'json'], text=True))
assert h1(decode(g['graph6'])) == (0, (3,))
```

The result is `(free_rank, torsion_invariant_factors)`, so `(0, (3,))` represents $\mathbb Z/3$. The disc construction in the article supplies the remaining homology groups and the proof of acyclicity over $\mathbb F_2$.

## Read the certificates

- [`disc_hypotheses.json`](../finite/certificates/disc_hypotheses.json) records five disc presentations. Its checker reconstructs the triangles, links and boundary identifications and determines the attaching degrees.
- [`link_checks.json`](../finite/certificates/link_checks.json) records the neighbourhood obstructions to a first strong deletion.
- [`certificate_replay.json`](../finite/certificates/certificate_replay.json) records the extensions and every step of their reductions, with neighbourhoods evaluated before the corresponding deletion.
- [`witness_data.json`](../tools/figures/witness_data.json) gives the edge sets and, separately, coordinates for the figures. The generators check that the drawn edge sets agree with the graph data.

The [notebook walkthrough](reproduction.md#interactive-examples) performs the first-homology calculation, compares `G14a` with its extension and reads the two acyclicity columns.
