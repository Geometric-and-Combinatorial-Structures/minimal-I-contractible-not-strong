# Historical small-order production sources

These sources identify the retained table evidence; they are not the recommended production program for new runs.

- `atascadas_classify.c` is `src/atascadas.c` with one per-graph output statement added. It was compared with `cleanroom.cpp` on every connected graph of orders 3–9.
- `cleanroom.cpp` is the separate historical C++ implementation used in that comparison.
- `exact_n11_capture.c` is `verification/atascadas_memo_exacto.c` with one output statement listing the acyclic graphs outside I_SV. It produced the four complete-state order-11 streams.
- `SOURCE_IDENTITY.json` binds these bytes and the original local orchestration scripts to their SHA-256 values. Local paths in those orchestration scripts are why they are not redistributed; the sources and selected result records are retained here.
- `check_source_identity.py` verifies these digests, the instrumentation-only differences and the counter equalities used in the source-path argument. It starts no graph generator and runs no census.

The scope and code-path justification for orders 3–11 are in [small-order-provenance.md](../../docs/small-order-provenance.md). New reproductions should use `v2/src/atascadas_v2.c` through the documented current driver.
