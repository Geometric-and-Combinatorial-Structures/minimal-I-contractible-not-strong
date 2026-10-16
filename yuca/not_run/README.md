Scripts submitted during the n=14 K4-free table run that never processed any slice (kept for the record):
- `frente_medio_n14_p011_desc_27.sh`: relaunch of the p011 middle front with 27 CPUs (SLURM 2085550), queued (Priority) and cancelled before starting, 14 Oct 2026.
- `frente_medio_n14_p011_desc_gpu.sh`: same front on GPU-partition nodes with 48 CPUs (SLURM 2085622), queued (Resources) and cancelled before starting; replaced by `../frente_medio_n14_p011_gpu_{a,b}.sh` (2×24 CPUs). A 51-CPU variant was rejected by sbatch (GPU nodes have 48 CPUs; job 2085618, never assigned).
