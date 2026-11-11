# Historical classifier

`atascadas.c` records an earlier implementation of the graph recursions and is retained for source comparisons and regression tests. For enumeration, use the [current classifier](../v2/README.md) and the [full reproduction guide](../docs/full-reproduction.md).

The historical program reads one graph6 record per line and selects an operation with `--modo`. Its source uses Spanish names: *atascada* means stuck, *vecindad* means neighbourhood and *cerradura* means closure. Write $\mathfrak I$, $\mathfrak I_S$ and $\mathfrak I_{SV}$ for the contractible, strong and strong vertex classes, respectively. Acyclicity here is over $\mathbb F_2$.

| Mode | Calculation |
|---|---|
| `atascadas` | Selects acyclic graphs for which every open neighbourhood is non-acyclic and every edge's common neighbourhood is empty or non-acyclic |
| `casi` | Selects acyclic graphs with exactly one vertex having an acyclic neighbourhood, and no edge having a nonempty acyclic common neighbourhood |
| `tabla` | Counts connected graphs, Euler characteristic one, acyclicity, the contractible and strong classes, and dismantling levels $-1$ through $3$ |
| `verificar` | Reports connectivity, Euler characteristic, Betti numbers, neighbourhood tests and membership tests |
| `cerradura` | Adds edges whose common neighbourhood is strong, expanding each non-strong result and recording the first strong results |
| `traza` | Prints a strong deletion sequence to $K_1$ |
| `icert --prof d` | Searches for at most `d` admissible edge additions leading to a strong graph |

In table mode, the `I` counter includes strong graphs and graphs certified by at most three such edge additions. Failed certificate searches are counted separately as `I_indecisas`. The historical `casi` test differs from the **at most one** admissible vertex condition needed for almost-stuck pieces; the [local K4-free check](../data/local_K4/README.md) implements that condition.

## Implementation and historical scope

Vertex-only recursions use exact vertex-subset keys. The strong-membership recursion in this version identifies subproblems by a 63-bit hash alone, which can conflate distinct states. The current version compares the complete active graph. [Small-order provenance](../docs/small-order-provenance.md) explains which historical table rows use each implementation and the conditional argument for avoiding the hash-only branch through order ten.

The historical source can be compiled from this directory with:

```bash
gcc -O3 -o atascadas atascadas.c -lm
```

The source requires C99 and the standard C library. Selected execution records are in [`finite/provenance/`](../finite/provenance/).
