# Provenance of the table rows of orders 3–11

The retained small-order results were not all produced by one program. This note identifies the runs supporting those rows and explains where the historical hash-only memoization is relevant. The finite route checks the retained records; the full route generates the graph universes again.

| Rows | Recorded generator and classifier | Retained evidence |
|---|---|---|
|3–9|nauty `geng` 2.8.9; the project classifier with per-graph output instrumentation, compared with a separate C++ implementation|`finite/provenance/small_order_counts.json`: 273,191 connected graphs, zero per-graph discrepancies|
|10|Reconstructed attribution: nauty `geng` 2.8.9, `-cq 10`; `src/atascadas.c`, table mode|`finite/provenance/separate_order10_census.txt`: 11,716,571 graphs; `separate_order10_commands.jsonl` records generator and classifier exits|
|11|nauty `geng` 2.8.9, `-cq 11 r/4` for all four residues; the complete-state memo variant with output instrumentation|`finite/provenance/exact_n11_summary.json`: 1,006,700,565 graphs; all four generator/classifier pairs exited zero|

The generator identity is recorded in `finite/provenance/nauty289_identity.json`. Selected records use normalized path placeholders; they do not point to a public deposit. Historical orchestration scripts were read to establish this mapping. Their digests, and the retained production source digests, are in `verification/historical_small_orders/SOURCE_IDENTITY.json`.

For order 10, the attribution of the generator version and of `src/atascadas.c` was reconstructed by local reading of those historical scripts and source records. The selected command log records a classifier invocation and successful exits, but contains no source or executable identity. The orchestration scripts themselves are not included. A reader of this selection therefore has the recorded result and the relevant source, but no independently authenticated source-to-executable binding for that invocation. The argument below is a code-path analysis under this stated attribution, not authentication of the historical run.

## Orders 3–10: scope of the hash-only branch argument

The historical `src/atascadas.c` stores only a hash in its strong-membership memo. No injectivity guarantee for that hash at these orders is supplied.

For the table runs of orders at most ten, the relevant code is:

```c
int ac = ch && acyclic_full(A,FULL);
int d0 = dismantle0(A,FULL);
int sv = d0 || (ac && isv_graph(A));
int si = sv || (ac && is_graph(A));
```

Here `ac`, `d0` and `sv` are intended to test acyclicity over $\mathbb F_2$, 0-dismantlability and $\mathfrak I_{SV}$, respectively. The first three tests do not use the hash-only strong-membership memo. The $\mathfrak I_{SV}$ recursion deletes only vertices of one fixed graph, so its exact vertex-subset key determines its state. Assume that the preliminary Euler-characteristic, homology and dismantlability tests compute their stated predicates correctly. Then 0-dismantlability implies acyclicity, and the code gives `sv` as a subset of `ac` on this input universe.

For every retained row of orders 3–10, the `acyclic` and `I_SV` counters agree. Under the preceding assumptions, no graph in those streams satisfied `ac && !sv`; C short-circuit evaluation therefore avoids `is_graph(A)` in the table branch. No bounded I-certificate search is needed either. This isolates the hash-only memoization issue. It does not independently certify the preliminary predicates, the source-to-executable attribution or the order-10 row, and it makes no assertion about other modes of the historical program.

The orders 3–9 comparison supplies a second implementation on all 273,191 graphs: `cleanroom.cpp` implements its recursive membership using full graph strings as memo keys. The historical driver compared its output with the instrumented project program graph by graph, including the homology and dismantlability fields. It also required acyclicity and strong membership to agree for every graph before inferring the I count. This independence applies to these small orders only.

For order 10 the retained row reports 2,343,148 acyclic graphs and the same number of I_SV graphs. Its coverage is supported by the recorded full generator stream and successful exits, subject to the source-attribution limit above. No independent classification is supplied for that row.

## Order 11: complete-state memoization

The order-11 run used `verification/atascadas_memo_exacto.c`, with one additional output statement listing the acyclic graphs outside $\mathfrak I_{SV}$. The exact instrumented source is retained as `verification/historical_small_orders/exact_n11_capture.c`. Its source comparison verifies that no classification logic changed.

This version stores the active vertex mask and the restricted adjacency rows, and compares the complete key by `memcmp`. The hash selects a bucket; it does not decide state identity. The four residue streams contain twelve acyclic graphs outside $\mathfrak I_{SV}$, all strong. The retained sum is 166,978,401 acyclic and strong graphs, with 166,978,389 in $\mathfrak I_{SV}$ and zero unresolved I cases.

`finite/provenance/final_local_checks.json` records 818 memo queries, 334 hits and zero detected hash collisions across the four runs. The guarantee needed here comes from comparing full keys, not from the observed absence of collisions or from the heuristic collision estimates also retained in that record. Other historical modes still contain hash-only deduplication; they are not used to establish this table row. The zero acyclic/non-strong remainder also means that the bounded extension search is not used for its I count.

## Corroboration from inclusions and its limits

The 63 entries shared with Table 1 of Dochtermann–Espinoza–Frías-Armenta–Hernández (2023) agree with the current table: connected graphs, F_2-acyclic graphs, I, I_S, I_SV, 1-Dis and 0-Dis, for orders 3–11. In those rows the published 1-Dis and I_SV counts coincide. The inclusions

`1-Dis ⊆ 2-Dis ⊆ 3-Dis ⊆ I_SV`

therefore force the intermediate 2-Dis and 3-Dis entries. This corroborates those entries without using the historical k-dismantlability code, conditional on the endpoint counts; it is not another computation of those endpoints.

In the K4-free universe the equality is structural: an I_SV vertex link is a nonempty tree, hence 0-dismantlable. An I_SV vertex-deletion sequence is consequently a 1-Dis sequence, and the reverse inclusion always holds. Thus all four families in the displayed chain coincide in that universe, including row 14. This supplies an additional consistency check of their reported equality without reclassifying that row.

No independent full enumeration of the Euler-characteristic-one column is supplied for orders 10–14. Those entries retain their dependence on the producer's clique enumeration and Euler-characteristic calculation. The separate implementation at orders 3–9 and the present finite checks have their stated, smaller scopes; they do not validate that entire column in the larger universes.

## Checks of the retained records

The finite route compares the retained small-order counts with the cardinality table. The source identity check verifies the retained source bytes and the two instrumentation-only transformations:

```bash
python3 -P verification/historical_small_orders/check_source_identity.py
```

It does not execute these historical classifiers. For a new full reproduction use the complete-state current classifier and the commands in [full-reproduction.md](full-reproduction.md). The current C recurrences have also been compared with separate direct recurrences on all 1,100 labelled graphs of orders 0–5 and their 33,867 induced masks; this bounded test is not a new order-11 census.
