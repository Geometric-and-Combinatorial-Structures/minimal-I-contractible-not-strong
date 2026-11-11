# Connected K4-free graphs of orders 2–7

[`connected_n2_7.g6`](connected_n2_7.g6) contains all 643 connected K4-free isomorphism classes at orders 2–7, with respective counts 1, 2, 5, 17, 82 and 536. They are used in the article's cut-vertex reduction.

In a K4-free graph, a vertex deletion is admissible precisely when its open neighbourhood is a nonempty tree; an edge deletion is admissible precisely when the endpoints have one common neighbour. An **almost-stuck** graph is $\mathbb F_2$-acyclic, has no admissible edge and has at most one admissible vertex. None of these 643 graphs is almost stuck.

The list was generated with nauty `geng -kc n` and concatenated in increasing order. [`generation.json`](generation.json) records the generator identity, counts, successful exits and stream hashes. Exhaustiveness uses the graph-generation method; the finite checker verifies every supplied graph, the local criterion and pairwise nonisomorphism.

From the repository root, check the supplied list with:

```bash
python3 -P tools/check_local_K4_catalogue.py
```

This uses the Python standard library and repository modules. To regenerate the same bounded universe with a nauty `geng` supporting `-k`, choose a new output directory and run:

```bash
python3 tools/generate_local_K4_catalogue.py --geng /path/to/geng \
  --output-dir build/local_K4
python3 -P tools/check_local_K4_catalogue.py --data-dir build/local_K4
```

This generation covers only orders 2–7. The complete table universes are described in [full enumeration](../../docs/full-reproduction.md).
