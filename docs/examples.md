# Working with the witnesses

The exporter uses exactly the vertex labels in the article and finite certificates. It does not relabel a graph canonically. All outputs go to standard output, so a command can be inspected before being redirected to a file.

```bash
python3 generate.py --graph G13
python3 generate.py --graph G14a --format json
python3 generate.py --graph G14a --extension --format edges
```

The default format is `graph6`; `json` supplies vertices, edges, order, size and the encoding; `edges` is a two-column TSV with header `u` and `v`. Only the five listed witnesses are accepted. `--extension` adds the certifying edge to one of the four contractible examples; it is not defined for `G13`.

| Identifier | Order | Edges | Integral H1 | Certifying edge |
|---|---:|---:|---|---|
| `G13` | 13 | 40 | Z/3 | — |
| `G14a` | 14 | 44 | 0 | {0,1} |
| `G14b` | 14 | 45 | 0 | {0,3} |
| `G14c` | 14 | 45 | 0 | {2,3} |
| `D15` | 15 | 46 | 0 | {9,12} |

Each graph in the table is non-strong. Each of the four displayed certifying additions produces a strong graph, and its common neighbourhood is strong. The article gives complete reductions for the three order-14 extensions. The earlier 15-vertex example is compared with its published labelling in the supplement.

## A small calculation in Python

From the repository root:

```python
import json, subprocess, sys
sys.path.insert(0, 'finite/certificates')
from finite_checks import decode, h1, strong

g = json.loads(subprocess.check_output(
    [sys.executable, 'generate.py', '--graph', 'G13', '--format', 'json'], text=True))
assert h1(decode(g['graph6'])) == (0, (3,))
```

The pair returned by `h1` is `(free_rank, torsion_invariant_factors)`. The calculation uses a spanning forest to present integral first homology by triangle relations. The supplement proves this presentation. A first-homology calculation alone says nothing about higher homology; the article's disc presentation and the complete finite checks provide the additional information used for these examples.

## From a picture to an exact graph

[`tools/figures/witness_data.json`](../tools/figures/witness_data.json) separates the graph's edges from drawing coordinates. The figure generator checks the actual emitted edge sets. Vertex labels are mathematical labels in the author's Palatino/Pazo graph style. Coordinates carry no combinatorial meaning.

[`finite/certificates/disc_hypotheses.json`](../finite/certificates/disc_hypotheses.json) contains the five disc presentations. [`finite/certificates/check_disc_hypotheses.py`](../finite/certificates/check_disc_hypotheses.py) reconstructs them from graph encodings, checks the links and boundary identifications, and computes the attaching degrees. The [notebook](../notebooks/reproduce.ipynb), copied for interactive use with `python3 tools/copy_notebook.py`, joins these examples to the two homology columns in the table.
