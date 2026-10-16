# `atascadas_memo_exacto.c` — audit variant of the I_S decision

`src/atascadas.c` (and the as-run copy `yuca/as_run/atascadas_n14_tabla.c`) memoises the exact strong-I-contractibility
search `is_rec` in an open-addressing table keyed **only by a 63-bit hash** of the state (vertex set m and the rows A[i]&m).
A hash collision between two different states would return the memoised answer of the other state.

`atascadas_memo_exacto.c` is generated from the as-run source by a mechanical patch: it stores the **full key** next to the hash,
accepts a hit only if the full key matches, and prints at the end
`AUDIT memo: consultas=… aciertos=… colisiones_reales=… esperanza_falsos_aciertos_hash63=…`
(real collisions = equal hash but different key, i.e. the cases in which the original would have returned a wrong memo value;
the last number is Σ occupancy/2^63 over all lookups, the expected number of false hits of the original for that workload).
Everything else is byte-identical to the as-run source.

Exposure: in `--modo tabla` the memoised `is_rec` is only reached for Z/2-acyclic graphs that are not in I_SV (all other
columns use exact subset-indexed memo tables), e.g. 12 graphs for n = 11 and about 1.5·10^7 for n = 13.
Local check (16 Oct 2026): the variant reproduces the rows n = 7…11 exactly; for n = 11: 820 lookups, 0 real collisions,
expected false hits 3.6·10^-15.
