#!/bin/bash
#SBATCH --account=p029
#SBATCH --qos=qos029
#SBATCH --partition=cpu
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=32G
#SBATCH --job-name=atasc_n14
#SBATCH --output=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla/logs/tarea_%A_%a.out
cd /lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla
t=$SLURM_ARRAY_TASK_ID; export t
echo "tarea $t inicio $(date) en $(hostname)"
# la tarea t procesa las rebanadas r = t, t+NT, t+2NT, ... con 64 procesos en paralelo
seq $t 7 1999999 | xargs -P 64 -I{} bash -c '
  r={}; d=out/$((r/1000)); mkdir -p $d; f=$d/$r
  grep -qx "$r" listas_t$t.txt && exit 0
  /lustre/proyectos/p029/busqueda_minimal/bin/geng28 -k -c 14 -q $r/2000000 | ./atascadas --modo tabla > $f.res 2> $f.log || exit 1
  ( flock 9; cat $f.res >> enc_t$t.txt; echo $r >> listas_t$t.txt ) 9> lock_t$t
'
echo "tarea $t fin $(date)"
