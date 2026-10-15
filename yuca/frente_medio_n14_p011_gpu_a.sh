#!/bin/bash
#SBATCH --account=p011
#SBATCH --qos=qos011
#SBATCH --partition=gpu
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=32G
#SBATCH --job-name=n14_medio_p011_gpu_a
# Frente INTERMEDIO p011 de la tabla fila 14 K4-libre, en la partición gpu usando SÓLO núcleos de CPU (sin --gres).
# Igual que frente_medio_n14_p011_desc.sh (escribe en out_m/, candado lock_m_t*, encontradas enc_m_t*, sólo AÑADE
# rebanadas terminadas a listas_t$t.txt), con dos salvaguardas extra porque los nodos GPU pueden tener otra CPU:
#  (1) compila su propia copia de atascadas desde el MISMO atascadas.c en el nodo donde corre;
#  (2) antes de registrar nada recalcula dos rebanadas de control y exige que su .log sea byte a byte idéntico al
#      que ya obtuvieron los frentes principales; si no coincide, termina sin tocar ningún registro.
set -u
B=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla
GENG=/lustre/proyectos/p029/busqueda_minimal/bin/geng28
ID=m011a; START=639999; STEP=-2; END=0
cd $B
H=$(hostname); mkdir -p gpu_bin; ATAS=$B/gpu_bin/atascadas_${H}_$SLURM_JOB_ID
gcc -O3 -march=native -std=c11 -o $ATAS.tmp atascadas.c && mv $ATAS.tmp $ATAS || { echo "frente $ID gpu $(date) $H: FALLO compilación, no se hace nada" >> bitacora_medio.txt; exit 1; }
for r in 1998006 1998007; do
  $GENG -k -c 14 -q $r/2000000 | $ATAS --modo tabla > gpu_bin/control_${SLURM_JOB_ID}_$r.res 2> gpu_bin/control_${SLURM_JOB_ID}_$r.log
  if ! cmp -s gpu_bin/control_${SLURM_JOB_ID}_$r.log out/1998/$r.log; then echo "frente $ID gpu $(date) $H: CONTROL $r NO coincide, no se hace nada" >> bitacora_medio.txt; exit 1; fi
done
echo "frente intermedio $ID (gpu) inicio $(date) nodo $H START=$START STEP=$STEP END=$END cpus=$SLURM_CPUS_PER_TASK job=$SLURM_JOB_ID; controles 1998006/1998007 idénticos" >> bitacora_medio.txt
export GENG ID ATAS
seq $START $STEP $END | xargs -P $SLURM_CPUS_PER_TASK -I{} bash -c '
  set -o pipefail; r={}; t=$((r%7))
  grep -qx "$r" listas_t$t.txt && exit 0
  d=out_m/$((r/1000)); mkdir -p $d; f=$d/$r
  $GENG -k -c 14 -q $r/2000000 | $ATAS --modo tabla > $f.res 2> $f.log || { echo "$r" >> fallidas_$ID.txt; exit 0; }
  ( flock 9; cat $f.res >> enc_m_t$t.txt; echo $r >> listas_m_$ID.txt; echo $r >> listas_t$t.txt ) 9> lock_m_t$t
'
echo "frente intermedio $ID (gpu) fin $(date)" >> bitacora_medio.txt
