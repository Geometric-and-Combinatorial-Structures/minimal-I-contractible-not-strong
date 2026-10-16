#!/bin/bash
#SBATCH --account=p011
#SBATCH --qos=qos011
#SBATCH --partition=cpu
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=27
#SBATCH --mem=32G
#SBATCH --job-name=n14_medio_p011
# frente_medio_n14_K4libre_tabla — frente INTERMEDIO de la tabla fila 14 K4-libre (geng28 -k -c 14 r/2000000).
# Usa sólo los 51 CPU que quedan libres bajo el tope GrpTRES cpu=500 de la cuenta (los frentes principales
# ocupan 7×64+1 = 449).  No toca los trabajos en curso ni su directorio out/: escribe en out_m/, con candado
# propio (lock_m_t*) y lista de encontradas propia (enc_m_t*).  Lo único compartido es el registro
# listas_t$t.txt (t = r mod 7), al que sólo AÑADE las rebanadas que termina, para que los frentes principales
# las salten (mismo mecanismo que ya usan los frentes p029/p011).  listas_m_m011.txt dice qué rebanadas
# tienen su .log en out_m/ (la recolección final debe sumar out/ y out_m/, una vez por rebanada).
set -u
B=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla
GENG=/lustre/proyectos/p029/busqueda_minimal/bin/geng28
ID=m011; START=639999; STEP=-1; END=0
cd $B
echo "frente intermedio $ID inicio $(date) nodo $(hostname) START=$START STEP=$STEP END=$END cpus=$SLURM_CPUS_PER_TASK job=$SLURM_JOB_ID" >> bitacora_medio.txt
export GENG ID
seq $START $STEP $END | xargs -P $SLURM_CPUS_PER_TASK -I{} bash -c '
  set -o pipefail; r={}; t=$((r%7))
  grep -qx "$r" listas_t$t.txt && exit 0
  d=out_m/$((r/1000)); mkdir -p $d; f=$d/$r
  $GENG -k -c 14 -q $r/2000000 | ./atascadas --modo tabla > $f.res 2> $f.log || { echo "$r" >> fallidas_$ID.txt; exit 0; }
  ( flock 9; cat $f.res >> enc_m_t$t.txt; echo $r >> listas_m_$ID.txt; echo $r >> listas_t$t.txt ) 9> lock_m_t$t
'
echo "frente intermedio $ID fin $(date)" >> bitacora_medio.txt
