#!/bin/bash
#SBATCH --account=p011
#SBATCH --qos=qos011
#SBATCH --partition=cpu
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=32G
#SBATCH --job-name=tabla_n14_p011
#SBATCH --output=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla/logs/tarea_p011_%A_%a.out
cd /lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla
t=$SLURM_ARRAY_TASK_ID; export t
r0=$(( 2000000 - 1 - ( (2000000 - 1 - t) % 7 ) ))
echo "tarea p011 $t inicio $(date) en $(hostname); r0=$r0"
seq $r0 -7 0 | xargs -P 64 -I{} bash -c '
  set -o pipefail; r={}; d=out/$((r/1000)); mkdir -p $d; f=$d/$r
  grep -qx "$r" listas_t$t.txt && exit 0
  /lustre/proyectos/p029/busqueda_minimal/bin/geng28 -k -c 14 -q $r/2000000 | ./atascadas --modo tabla > $f.res 2> $f.log || exit 1
  ( flock 9; cat $f.res >> enc_t$t.txt; echo $r >> listas_t$t.txt ) 9> lock_p011_t$t
'
echo "tarea p011 $t fin $(date)"
