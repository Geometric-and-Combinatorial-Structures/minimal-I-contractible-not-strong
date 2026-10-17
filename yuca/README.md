# Cluster runs (YUCA, ACARUS – Universidad de Sonora)

All runs follow the same pattern: a 1-core *wrapper* job (`envoltorio_*.sh`) compiles the program, writes the
array-task script and submits `sbatch --export=NONE --array=0-6` of 64-core tasks (SLURM partition `cpu`).  Task `t`
processes the `res/mod` slices r ≡ t (mod 7) of the `geng` enumeration with 64 parallel processes (`xargs -P 64`),
appending the found graphs and the slice number to per-task registries (`enc_t*.txt`, `listas_t*.txt`) under a file
lock, so a run can be resumed.  For the n = 14 full table two extra *middle* fronts (51 CPU each, the head-room left under the
GrpTRES cpu=500 limit of each account) start at r = 640,000 and move up/down; they only append finished slices to the shared
registries and keep their logs in `out_m/` (list in `listas_m_*.txt`), so the final collection sums `out/` and `out_m/`, once per slice.  For n = 14 a second front ran on account p011 with slices in descending order
(`envoltorio_n14_K4libre_p011.sh`); both fronts shared the registries.

| run | wrapper | geng command | slices | SLURM arrays | cores | wall |
|---|---|---|---|---|---|---|
| n = 12, full table | `envoltorio_n12_tabla.sh` | `geng -c 12 r/4000` | 4,000 | 2079049 / 2079051 | 448 | 8 min |
| n = 13, stuck graphs | `envoltorio_n13_atascadas.sh` | `geng -C -d4 -D11 13 r/200000` | 200,000 | 2079058 / 2079059 | 448 | 7 h 10 min |
| n = 14 K₄-free, stuck graphs | `envoltorio_n14_K4libre.sh`, `…_p011.sh` | `geng28 -k -C -d4 -D12 14 r/2000000` | 2,000,000 | 2079102 (p029), 2079156 (p011) | 896 | ≈ 33 h |
| n = 13, full table | `envoltorio_n13_tabla.sh`, `…_p011.sh` | `geng -c 13 r/200000` | 200,000 | 2084597 (p029), 2084636 (p011) | 896 | 21 h (12 Oct 21:04 – 13 Oct 17:59 MST); 483 slices processed twice, 0 missing; logs `n13_tabla_*` |
| n = 12, full table v2 (all columns) | `envoltorio_n12_tabla_v2.sh` | `geng -c 12 r/4000` | 4,000 | 2084878 | 448 | 8 min; logs `n12_tabla_v2_*` (counters re-summed with the full key list) |
| n = 12, 2-Dis ∖ 1-Dis extraction | `d21_n12_48cpu.sh` (single 48-core task) | `geng -c 12 r/4000` | 4,000 | 2084929 | 48 | 47 min; 20 graphs (`data/strictly_2dis_12.*`) |
| n = 14 K₄-free, full table | `envoltorio_n14_K4libre_tabla_p029.sh`, `…_p011.sh`, `frente_medio_n14_p029_asc.sh`, `frente_medio_n14_p011_desc.sh` | `geng28 -k -c 14 r/2000000` | 2,000,000 | 2084887 (p029), 2085018 (p011), 2085231 + 2085232 (middle fronts, 51 CPU each; 2085232 stopped 14 Oct 22:51 to free cores for another p011 user and replaced by 2085623 + 2085624, 24 CPU each on GPU-partition nodes without GPUs, `frente_medio_n14_p011_gpu_{a,b}.sh`; 2085231 finished 16 Oct 08:56 MST; 2089945, middle front m029b, 48 CPU, r = 290,000 → 172,000, `frente_medio_n14_p029_m029b.sh`, added 17 Oct 00:04 MST) | ≈1000 | in progress (started 13 Oct 18:52 MST; p011 front added 22:20 MST; two middle fronts from r = 640,000 added 14 Oct 16:16 MST, writing to `out_m/`; every middle front records its slices in its own `listas_m_<id>.txt`) |

`geng28` is the `geng` binary of the conda-forge package nauty 2.9.3, copied into the project directory: its strings
name the build tree `/usr/local/src/conda/nauty-2.9.3`, `geng28 --version` prints the token `2.9301`, and its SHA-256
is `179508d908b1f399fde36cb0e702960150eaa8b48ba0788bc8627cbdf33ae2cb` (probe P0 of round 3 of the external audit,
17 Oct 2026).  It is byte-identical to `bin/geng` of the conda-forge package nauty-2.9.3-hb03c661_0 (linux-64,
package SHA-256 `63228fa3f782c80c4730d5e42ec6d39c89d2940835325d52fe79b92da890ed2e`): the chain from the channel's
index to these bytes, and the record of how the file reached YUCA on 11 Oct 2026, are in `geng28_provenance.md`.
The name is historical.  Earlier versions of this README, the comment in line 19 of
`envoltorio_n14_K4libre.sh` (kept byte-identical to the script that ran) and the answer to round 2 of the audit
called it nauty 2.8; that was wrong.  The cluster's nauty 2.7r4 `geng` does not support `-k`.

## Hardware and software (recorded on node amdcpu-hpc-01, 2026-10-13)

CPU partition: 24 nodes, each with two AMD EPYC 9354 32-core processors (64 cores, 1 thread/core) and 1,031,112 MB of RAM; Rocky Linux 9.6, kernel 5.14; SLURM 24.11.1; gcc 11.5.0; nauty 2.7r4 (`geng`) and nauty 2.9.3 (`geng28`, the conda-forge binary copied into the project directory; see above). Full `lscpu`, `scontrol`, `sinfo`, `sacct` and `sacctmgr` dumps are archived in the project's Dropbox folder (`10_yuca_raw/sistema/`).

## `logs/`

* `casi_n03-11.txt`: output of `geng -c n | atascadas --modo casi` for n = 3,…,11 (0 almost-stuck graphs; basis of the 2-connectivity lemma up to 22 vertices). Run locally (n = 11: about 4 min on 8 cores).
* `n14_bitacora_failed_geng27_array2079068.txt`: log of the first, discarded n = 14 submission (array 2079068, geng 2.7r4 without `-k`: total = 0).
* `n12_*`, `n13_*`, `n14_*`: the `bitacora` (wrapper log), `resumen` (totals of the filter cascade: `total`, `pasa_cono`,
  `pasa_chi`, `pasa_vecindades`, `pasa_aristas`, `encontradas`), `encontradas` (graphs found, labelled, before isomorphism
  reduction), `sacct` accounting output.
* `n14_listas_distintas.txt.gz`: the 2,000,000 distinct slice numbers processed (coverage proof); `n14_faltantes_n14.txt`
  is empty (0 missing slices); `n14_duplicadas.txt` lists the 692 slices processed by both fronts (both fronts wrote to the same per-slice
  paths with different lock files, so the archive keeps one copy per slice and identity of the two outputs is NOT
  established; external audit finding H-03);
  `n14_pordir_n14.txt` counts result files per output directory; `n14_cobertura_n14.txt` is the coverage summary.

## `as_run/` — sources and task scripts exactly as executed

| file | SHA-256 |
|---|---|
| `atascadas_n12.c` | `0c3a1a71c132fd697fe0ae0198f2796743bf2386614525cb5052734169d4bc23` |
| `atascadas_n13.c` | `0c3a1a71c132fd697fe0ae0198f2796743bf2386614525cb5052734169d4bc23` |
| `atascadas_n14.c` | `d97e8bf58ce368b855eb182b241aaaebf571639fed4be55db42805ae6ae0e199` |
| `tarea_n12.sh` | `6f575822b9f9eb208ee9bd0c7a6e28e2065f96e0936450b889bf27eb638349f8` |
| `tarea_n13.sh` | `953ec4d1f0e898c2c878a0098f77c80032b57a1bee6300b0fe9a5b69f23e937f` |
| `tarea_n14_p011.sh` | `b95a125b466b47e921269baa43028983ea00081563ae3d4a126fc86452381ba9` |
| `tarea_n14_p029.sh` | `41fb94bc2d444c225bc0117214b452319e3f131933862e5d899cf5b92bbcfe84` |
| `tarea_n14_p029_intento_fallido_2079068.sh` | `50477550293c8442ee6368b360dbeade20144fe8f20be54f32571d263018b320` |

**Correction (16 Oct 2026, external audit finding H-05, test Y-F01).** Until commit `4a059b5` the file named
`tarea_n14_p011.sh` was in fact the task of the first, discarded n = 14 attempt (array 2079068: account p029, ascending
slices, geng 2.7r4 without `-k`, no `pipefail`), copied from `n14_K4libre_fallido_1791743024/tarea.sh`. It is now kept
as `tarea_n14_p029_intento_fallido_2079068.sh`. The task actually run by the p011 front (array 2079156: account p011,
geng28, descending slices) is `tarea_n14_p011.sh` above. SLURM accounting on YUCA does not keep submitted batch
scripts (`sacct --batch-script` returns `NONE`), so the identification rests on the file-system records: the file's
birth, modification and change times all equal the submission time of 2079156 (2026-10-11 15:40:09 MST); the task logs
print the descending starting residues it computes (r0 = 1999998, 1999999, 1999993, …); and nothing in the valid run
directory predates 2026-10-11 11:23:44, while the failed attempt keeps its own directory.

### As-run copies, monitoring and verification (n = 14 K₄-free table)
- `as_run/atascadas_n14_tabla.c` is the exact source compiled for the n = 14 table (SHA-256 0676f313…); it differs from `src/atascadas.c` only by the later mode `--modo 2dis_no_1dis` (the `tabla` code path is identical). `as_run/tarea_n14_tabla_p029.sh` and `as_run/tarea_n14_tabla_p011.sh` are the array tasks generated by the two wrappers.
- `monitoring/`: progress counts (`suma_incremental_n14.sh`, `suma_por_directorio_n14.sh`), the 32-slice sample used to estimate the total work (`muestreo_rebanadas_n14.sh`, results in `logs/n14_tabla_muestreo_32_rebanadas.txt`), the counts of connected K₄-free graphs for n ≤ 12 (`conteo_k4libres_conexas.sh`) and the script that checks the reported graphs (`verificar_encontradas_n14.sh`; written on 15 Oct 2026 and not yet run in this form: it will be run on the complete lists when the row is collected).
- `not_run/`: scripts that were submitted but never processed a slice.
- Known defects found by the external audit (kept unchanged as records of what ran):
  `monitoring/preauditoria_yuca.sh` (job 2089558) applies `comm` to numerically sorted lists (finding H-15), so the
  stratum labels of its 50-slice sample may be wrong; the independent sample of the audit (test Y-F02, seed 20261016,
  job 2089574, integer set differences) passed 50/50 and supersedes it.  `monitoring/recolectar_n14_tabla.py` accepts
  inconsistent per-slice data (finding H-04) and must not be used to certify the n = 14 row; the final collection uses
  the auditor's per-slice inventory (test Y-F03).  Version 2 of the classifier and of the pipeline is in `../v2/`.
