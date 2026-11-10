# Current classifier versus mathematical recurrences

This optional check compares the actual functions in `v2/src/atascadas_v2.c` with separate, direct implementations of the mathematical recurrences. It covers every labelled graph of order 0 through 5 and every induced vertex mask: **1,100 graphs and 33,867 states**.

Requirements: Python 3.11 or newer, its standard library, and GCC or Clang on a POSIX system. No graph generator, Python package, network access or external project directory is needed.

From the repository root:

```bash
python3 verification/current_recurrences/implementation_correspondence.py
```

The script locates all inputs relative to its own location, so it also works when invoked from another working directory. It compiles the C harness locally and writes the binary, raw observations and JSON report under `build/current_recurrences/`. Generated files are excluded by the repository's `.gitignore`. A successful run prints `"status": "PASS"`, with 1,100 graphs, 33,867 states and zero mismatches, and exits with code zero. Compilation, execution or comparison failures exit nonzero. Python's `-O` option is refused because the checker requires assertions.

To select a compiler or a different output directory:

```bash
python3 verification/current_recurrences/implementation_correspondence.py \
  --cc gcc --output-dir build/current_recurrences
```

The harness includes the current C source by a relative path and renames only its executable entry point. The classification functions themselves are unmodified. The same harness can be compiled separately from the repository root:

```bash
mkdir -p build/current_recurrences
cc -O2 -std=c11 -Wall -Wextra -Wpedantic -Werror \
  verification/current_recurrences/implementation_correspondence.c \
  -o build/current_recurrences/implementation_correspondence.bin
```

Running that binary emits the C observations only. The Python command performs the independent comparison and records input and output digests.

The checks cover strong contractibility, strong vertex contractibility, cones, dismantling levels 0–3, F2-acyclicity with and without preliminary filters, Euler characteristic, connectedness, and all successful first vertex and edge deletions. The comparison recurrences do not use homology, connectedness or greedy dismantling as shortcuts. Empty masks, singleton masks, disconnected subgraphs and empty neighbourhoods are included. Order zero is tested through the original internal functions; the classifier's graph6 input interface intentionally rejects an order-zero record.

This is a bounded regression check. It does not repeat the large censuses or prove the executable correct in every order. The separate recurrences were written after inspecting the C source and manuscript; they are not a preregistered clean-room implementation. Small graphs do not exhibit the large-order separations between the recursive classes; those examples have their own finite certificates.
