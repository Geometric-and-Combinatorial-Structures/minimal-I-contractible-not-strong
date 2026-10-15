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
| n = 14 K₄-free, full table | `envoltorio_n14_K4libre_tabla_p029.sh`, `…_p011.sh`, `frente_medio_n14_p029_asc.sh`, `frente_medio_n14_p011_desc.sh` | `geng28 -k -c 14 r/2000000` | 2,000,000 | 2084887 (p029), 2085018 (p011), 2085231 + 2085232 (middle fronts, 51 CPU each; 2085232 stopped 14 Oct 22:51 to free cores for another p011 user and replaced by 2085623 + 2085624, 24 CPU each on GPU-partition nodes without GPUs, `frente_medio_n14_p011_gpu_{a,b}.sh`) | ≈1000 | in progress (started 13 Oct 18:52 MST; p011 front added 22:20 MST; two middle fronts from r = 640,000 added 14 Oct 16:16 MST, writing to `out_m/`) |

`geng28` is `geng` from nauty 2.8.x compiled in the project directory (the cluster's nauty 2.7r4 `geng` does not
support `-k`).

## Hardware and software (recorded on node amdcpu-hpc-01, 2026-10-13)

CPU partition: 24 nodes, each with two AMD EPYC 9354 32-core processors (64 cores, 1 thread/core) and 1,031,112 MB of RAM; Rocky Linux 9.6, kernel 5.14; SLURM 24.11.1; gcc 11.5.0; nauty 2.7r4 (`geng`) and nauty 2.8 (`geng28`, built in the project directory). Full `lscpu`, `scontrol`, `sinfo`, `sacct` and `sacctmgr` dumps are archived in the project's Dropbox folder (`10_yuca_raw/sistema/`).

## `logs/`

* `casi_n03-11.txt`: output of `geng -c n | atascadas --modo casi` for n = 3,…,11 (0 almost-stuck graphs; basis of the 2-connectivity lemma up to 22 vertices). Run locally (n = 11: about 4 min on 8 cores).
* `n14_bitacora_failed_geng27_array2079068.txt`: log of the first, discarded n = 14 submission (array 2079068, geng 2.7r4 without `-k`: total = 0).
* `n12_*`, `n13_*`, `n14_*`: the `bitacora` (wrapper log), `resumen` (totals of the filter cascade: `total`, `pasa_cono`,
  `pasa_chi`, `pasa_vecindades`, `pasa_aristas`, `encontradas`), `encontradas` (graphs found, labelled, before isomorphism
  reduction), `sacct` accounting output.
* `n14_listas_distintas.txt.gz`: the 2,000,000 distinct slice numbers processed (coverage proof); `n14_faltantes_n14.txt`
  is empty (0 missing slices); `n14_duplicadas.txt` lists the 692 slices processed by both fronts (identical outputs);
  `n14_pordir_n14.txt` counts result files per output directory; `n14_cobertura_n14.txt` is the coverage summary.

## `as_run/` — sources and task scripts exactly as executed

| file | SHA-256 |
|---|---|
| `atascadas_n12.c` | `0c3a1a71c132fd697fe0ae0198f2796743bf2386614525cb5052734169d4bc23` |
| `atascadas_n13.c` | `0c3a1a71c132fd697fe0ae0198f2796743bf2386614525cb5052734169d4bc23` |
| `atascadas_n14.c` | `d97e8bf58ce368b855eb182b241aaaebf571639fed4be55db42805ae6ae0e199` |
| `tarea_n12.sh` | `6f575822b9f9eb208ee9bd0c7a6e28e2065f96e0936450b889bf27eb638349f8` |
| `tarea_n13.sh` | `953ec4d1f0e898c2c878a0098f77c80032b57a1bee6300b0fe9a5b69f23e937f` |
| `tarea_n14_p011.sh` | `50477550293c8442ee6368b360dbeade20144fe8f20be54f32571d263018b320` |
| `tarea_n14_p029.sh` | `41fb94bc2d444c225bc0117214b452319e3f131933862e5d899cf5b92bbcfe84` |
