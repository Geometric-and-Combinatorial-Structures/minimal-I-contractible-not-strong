# Connected K4-free graphs of orders 2–7

`connected_n2_7.g6` contains one representative of each class produced by nauty `geng -kc n`, concatenated in increasing order. The class counts are 1, 2, 5, 17, 82 and 536, for a total of 643. `generation.json` records the fresh small generation, generator digest, return codes, per-order stream digests and the combined catalogue digest. The streams agree with the retained historical small-order check.

The mandatory quick route runs `tools/check_local_K4_catalogue.py`. It verifies the universe, counts, absence of isomorphic duplicates and the almost-stuck criterion on every listed graph. In the K4-free universe a vertex is admissible precisely when its open neighbourhood is a nonempty tree, and an edge is admissible precisely when its common neighbourhood has one vertex. The check includes **zero or one admissible vertex**, not just exactly one. None of these graphs is almost stuck. Finite membership checks and a stored list alone do not prove exhaustive coverage; coverage relies on the stated generator and its mathematical generation method.

From the repository root, no generator is needed to check the supplied list:

```bash
python3 -P tools/check_local_K4_catalogue.py
```

To repeat only this bounded generation with an installed nauty `geng` supporting `-k`, and check the newly generated copy:

```bash
python3 tools/generate_local_K4_catalogue.py --geng /path/to/geng \
  --output-dir build/local_K4
python3 -P tools/check_local_K4_catalogue.py --data-dir build/local_K4
```

The verifier uses the Python standard library and repository modules only. It does not invoke a generator or access the network. The generation script does not run any census above order seven.
