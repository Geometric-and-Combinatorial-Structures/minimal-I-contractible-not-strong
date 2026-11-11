# Enumeration records and provenance

These records identify the enumerations supporting the cardinality table and the restricted seed searches. The [verification map](../../docs/verification-scope.md) relates their totals to the mathematical statements. This index describes the selected files, their normalisation and the recorded computing resources.

## Normalisation of the selected records

The complete source archive is retained in the authors' project records. Copies prepared for distribution replace local and cluster paths by neutral `<deposit>/` and `<cluster>/` prefixes, omit user and node identities, and translate field names and diagnostic labels into English. Command arrays are normalised descriptions of the recorded commands, not verbatim shell commands; executable names and mode labels in them are descriptive. Counts, graph6 strings, return codes, version tokens and timing values are unchanged. `SELECTION_SOURCES.json` has one entry per selected source file (23 entries). `original_sha256` identifies the original record, `sha256` the selected copy, and `private_record` its opaque source identifier. Referenced binary and source-archive digests use distinct `referenced_executable_sha256` and `referenced_source_archive_sha256` fields. Some timing and counter records are also retained verbatim in earlier Git commits. The complete source archive is not included; original-file hashes identify source bytes and do not authenticate execution.

## Small-order counts

- `small_order_counts.json` records class-count comparisons at orders 3–9. It is an aggregate comparison, not an included comparison graph by graph.
- `separate_order10_census.txt` and `separate_order10_commands.jsonl` record a complete order-10 recount with the project classifier.
- `exact_n11_summary.json` records the complete-state order-11 recount. The four files `exact_n11_r0.stderr.txt` through `exact_n11_r3.stderr.txt` contain the per-residue counters and memo diagnostics.
- `almost_stuck_n11_runs.json` records four separate order-11 almost-stuck checks; `almost_stuck_n11_r0.stderr.txt` through `almost_stuck_n11_r3.stderr.txt` preserve their counters. `final_local_checks.json` gives the aggregate comparisons. Both sets of four residues total 1,006,700,565 graphs.
- `project_almost_stuck_orders3-11.txt` is the original almost-stuck record: one stream through order 10, eight contributions at order 11. It is a different run from the four-residue check.
- `nauty_build.json` retains the configure and make output for nauty 2.8.9 and adds the source-archive and preserved-executable digests. `nauty289_identity.json` gives the observed version token 2.8090 and the same digests. The build used GCC with `-O4 -mpopcnt -march=native`. The digests were computed from preserved files on 18 October 2026; they were not part of the historical build log. A rebuild with machine-specific compiler flags need not reproduce the executable bytes.

The original local environment identified nauty 2.9.3, but that does not identify the bytes used in every small-order invocation. The separately documented checks use the preserved nauty 2.8.9 build. The counts of connected graphs and cones are compared with OEIS A001349 (connected graphs) and A000088 (cones of order n via all graphs of order n - 1); the 63 entries shared with Dochtermann et al. (2023) are compared with its published table.

[Small-order provenance](../../docs/small-order-provenance.md) maps these rows to their actual production sources. The historical orders 3–9 check compared two implementations graph by graph, although only its summary is selected here. The equality of acyclic and I_SV counters avoids the old hash-only strong branch in the complete streams through order 10. The complete order-11 recount instead used the variant that compares full state keys.

The historical mode called `casi` required exactly one vertex passing its acyclic-link test; its unrestricted order-10/11 records are not the mathematical exclusion of almost-stuck pieces used in the article. That proof requires zero or one admissible vertex and is checked on the 643 supplied connected K4-free graphs of orders 2–7 by `tools/check_local_K4_catalogue.py`. The historical restricted order-13 search and its timing likewise do not replace the full order-13 table evidence.

## Original scheduling and accounting

The original arrays assigned residue r to task r mod 7, with 64 concurrent processes per task. Two groups of tasks traversed the larger partitions in opposite directions. The original order-14 seed-search records contain 2,000,692 entries for 2,000,000 residues, with 692 repeated residues. The complete order-13 census has 483 repeated residues. Counts were summed once per residue. Only one copy of each repeated output survives, because the groups shared output paths; the later recomputations establish agreement without asserting equality of overwritten copies.

`search_accounting_rows.tsv` contains the 21 selected accounting rows, with personal identity fields normalised. `search_task_intervals.tsv` retains their timing fields and original line numbers; `search_elapsed_comparison.json` computes last task End minus first task Start. The elapsed times are 7 h 10 min 11 s at order 13 and 35 h 2 min 48 s at order 14, in Hermosillo time (UTC-7). The first spans 11 October 2026, 01:40:45–08:50:56; the second spans 11 October, 11:23:46, to 12 October, 22:26:34. The order-13 wrapper log is preserved separately. These are task spans, excluding wrapper startup and shutdown, and are not CPU times. Up to 448 and 896 cores were allocated. The recorded environment was GCC 11.5.0, Rocky Linux 9.6 and SLURM 24.11.1, on systems with two 32-core AMD EPYC 9354 processors.

The original restricted order-13 filter processed 21,011,415,992,470 graphs, with 3,335,926,431,910 after the cone stage, 480,204,455,162 after the Euler stage, 15,693,920,490 after the vertex-neighbourhood stage, and 218,516 after the edge-neighbourhood stage; the homology test retained one graph. The corresponding order-14 figures are 64,856,470,381,820; 48,303,369,131,820; 1,462,235,073,536; 108,022,349,478; 13,536,597; and 51. The complete order-13 census provides a separate route to the same single seed and its three-class closure.

## Executable identities

`generator_probe_2026-10-17.json` gives version responses, help output and digests for the fixed unrestricted generator (nauty 2.7r4, token 2.7000), the K4-free generator (nauty 2.9.3, token 2.9301) and the canonical labeller (nauty 2.7r4, token 2.7000). The K4-free executable was historically named geng28; its bytes match `bin/geng` in the linux-64 conda-forge build `hb03c661_0`. The script for descending residues was identified from its file times and starting residues; the scheduler did not preserve an authenticated submitted script. Preserved source and executable identities are recorded separately and do not authenticate an earlier invocation.

## Contract for complete recomputations

Each run fixed generator bytes and options, residue modulus, classifier source and executable, and driver version. A residue was accepted only when both programs exited successfully, the generator count equalled the classifier input count, the output schema and invariants were valid, and the recorded identities matched the fixed configuration. Each receipt bound its residue to output hashes, software identities, job and attempt. Aggregation required exactly one accepted contribution per residue, with no missing residue, and a successful current invocation with a terminal record identifying the aggregate hash. Earlier outputs and repeated attempts were retained separately.

For the full table recomputations (table12, table13 and table14; historical identifiers F2_12, F2_13 and F4), the twelve raw counters and two output sets were compared residue by residue: certified graphs in I outside I_S, and $\mathbb F_2$-acyclic graphs outside I_S left undecided by the bounded certificate search. The latter were resolved by the stated homological classification. Raw lists, their canonical forms and the justified final classifications remain distinct. In order 14, the positive set equals the eight graphs in `../data/K4_free_I_not_strong_14.tsv`; the I count exceeds the I_S count by eight, and the cone count is 20,797,002.

The filtered stuck-seed recomputation (seeds14, historical F3) instead compared its final 51-class set up to isomorphism and its aggregate counters; it did not compare historical outputs residue by residue and did not run homological adjudication. Its aggregate, dated 29 October 2026, records all 2,000,000 residues, 64,856,470,381,820 input graphs and 51 classes, with no reported problems. The current finite seed checks and the full table14 census provide separate supporting checks; [full-reproduction.md](../../docs/full-reproduction.md) gives the exact scopes and campaign-name map.

## Read-only checks and complete file index

From this directory, run `python3 -P check_records.py` to compare the four order-11 exact residues, the four almost-stuck residues, the eight original contributions, the 21 accounting rows and their intervals, aggregate elapsed times, and every selected digest in `SELECTION_SOURCES.json`. Run `python3 -P ../check_integrity.py` for byte coverage of all metadata fields, including this index and the source manifest. The finite checker does not authenticate historical jobs or original private records. SLURM JobID values are retained as technical identifiers.

The files listed above include every selected source record. In addition, `order13_elapsed.txt` gives the original elapsed-time output, and `order13_wrapper_log.txt` preserves the normalised order-13 wrapper transcript; their origin and hashes are recorded separately. `SELECTION_SOURCES.json` is the provenance map and `check_records.py` its checker. The [coverage guide](../VERIFICATION_COVERAGE.md) distinguishes the mathematical checks, comparisons of numerical records and file-integrity checks.

## Local K4-free reduction evidence

`local_K4_small_checks.json` records an enumeration of all connected K4-free graphs of orders 2–8, the exact almost-stuck test (at most one admissible vertex, no admissible edge, and $\mathbb F_2$-acyclicity), and clique and H1 checks for the three order-13 examples. It identifies the nauty 2.8.9 binary and output streams. Its reproduction command is documented in `../data/README.md`.

`local_K4_restricted_records.json` describes the separate restricted enumeration at orders 5–12 and identifies its preserved source archive by SHA-256. The corresponding counters, survivor streams and C filter are in `../data/`. The current check sums the eight order-12 counters (914,568,002 inputs), compares their concatenated streams, and recomputes the local criteria and $\mathbb F_2$ homology of every survivor (zero acyclic survivors). It does not rerun the large generator streams or authenticate their earlier execution.

## Large-enumeration wall times and allocated core-hours

The following wall-clock intervals come from retained completion records. All timestamps are in UTC-7. A submission command is the invocation of the submission script, not the scheduler's later SubmitTime. Array endpoints exclude aggregation and homological adjudication unless explicitly included. The cited completion reports and original logs are retained in the project archive, which is not distributed here; relative paths beginning `yuca/` identify records within that archive. Some of those logs are also available in the [retained Git history](https://github.com/Geometric-and-Combinatorial-Structures/minimal-I-contractible-not-strong/tree/c66e0399bc864e4e0147aa14d01ac9fb24db5028/yuca/logs). Both order-14 seed searches impose biconnectivity and $4\leq\delta\leq\Delta\leq12$.

| Calculation | Recorded interval | Start and end | Endpoint types / source |
|---|---|---|---|
| Original complete order-12 census, run 1 (classifier v1) | 8 min 0 s | 2026-10-11 01:32:05 to 01:40:05 | Wrapper start to array end; original archived record `yuca/logs/n12_bitacora.txt` |
| Original complete order-12 census, run 2 (classifier v1) | 8 min 0 s | 2026-10-13 18:52:34 to 19:00:34 | Wrapper start to array end; original archived record `yuca/logs/n12_tabla_v2_bitacora.txt` |
| Original complete order-13 census (classifier v1) | 20 h 54 min 53 s | 2026-10-12 21:04:33 to 2026-10-13 17:59:26 | Wrapper start to last array end; original archived record `yuca/logs/n13_tabla_bitacora.txt` |
| Original restricted order 13 | 7 h 10 min 11 s | 2026-10-11 01:40:45 to 08:50:56 | First task start to last task end; `search_task_intervals.tsv` |
| Original K4-free order-14 seed search | 35 h 2 min 48 s | 2026-10-11 11:23:46 to 2026-10-12 22:26:34 | First task start to last task end; `search_task_intervals.tsv` |
| Complete order-12 census recomputation | 5 min 35 s | 2026-10-21 21:56:56 to 22:02:31 | First array start to last array end; completion report of 22 October 2026, section 3 |
| Complete order-13 census recomputation | 23 h 16 min 28 s | 2026-10-26 18:21:52 to 2026-10-27 17:38:20 | First array start to end of homological adjudication; completion report of 27 October 2026, section 2 |
| K4-free order-14 seed recomputation (seeds14) | 45 h 21 min 52 s | 2026-10-27 19:02:22 to 2026-10-29 16:24:14 | Submission command to end of aggregation; completion report of 29 October 2026, section 2 |
| Complete K4-free order-14 recomputation | 8 d 0 h 33 min 51 s | 2026-10-29 17:10:45 to 2026-11-06 17:44:36 | First submission command to end of homological adjudication, including resumption of 51 tasks that reached the seven-day limit; completion report of 6 November 2026, section 2 |

No wall-time interval is stated here for the original complete K4-free order-14 census: the selected records do not establish that interval. The complete recomputation in the last row is a different run.

The scheduler records allocated core time as `CPUTimeRAW = Elapsed * AllocCPUS`. Summing the selected task rows (without double-counting job steps) gives:

| Original restricted search | Tasks | Allocated core-seconds | Allocated core-hours (one decimal) |
|---|---:|---:|---:|
| Order 13 | 7 | 11,398,272 | 3,166.2 |
| K4-free order 14 | 14 | 101,046,464 | 28,068.5 |

These totals agree with the sum of elapsed seconds times `allocated_cpus` in `search_accounting_rows.tsv`. They are recorded allocations, not measured CPU use: the retained scheduler `TotalCPU` fields are zero, so measured CPU time was not recorded. The completion reports for the recomputations above contain no allocated core-hour totals; none is estimated from maximum core counts and wall spans. The complete per-residue production archive is not included in this selection. The selected aggregates and finite adjudications are in `../../data/census/`.
