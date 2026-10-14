#SBATCH --account=p011
#SBATCH --qos=qos011
#SBATCH --partition=cpu
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

# ============================================================================
# envoltorio_n14_K4libre_tabla_p011.sh — Segundo frente (cuenta p011, autorizada por
# el usuario el 2026-10-11 sólo para este proyecto; uso confirmado el 2026-10-14
# porque p029 está saturado) para la tabla fila 14 K4-libre (geng28 -k -c 14). Procesa las rebanadas en
# ORDEN INVERSO (r descendente) y comparte listas_t*.txt / enc_t*.txt con el
# array de p029 (2084887), que es quien hace la recolección final.
# ============================================================================
set +e; set -uo pipefail
N=14; MOD=2000000; NT=7; GOPTS="-k -c"; MODE=tabla
BASE=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla
GENG=/lustre/proyectos/p029/busqueda_minimal/bin/geng28
cd $BASE
echo "inicio frente p011 $(date) nodo $(hostname)" | tee -a $BASE/bitacora.txt

cat > $BASE/tarea_p011.sh <<EOT
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
#SBATCH --output=$BASE/logs/tarea_p011_%A_%a.out
cd $BASE
t=\$SLURM_ARRAY_TASK_ID; export t
r0=\$(( MOD_PLACEHOLDER - 1 - ( (MOD_PLACEHOLDER - 1 - t) % $NT ) ))
echo "tarea p011 \$t inicio \$(date) en \$(hostname); r0=\$r0"
seq \$r0 -$NT 0 | xargs -P 64 -I{} bash -c '
  set -o pipefail; r={}; d=out/\$((r/1000)); mkdir -p \$d; f=\$d/\$r
  grep -qx "\$r" listas_t\$t.txt && exit 0
  $GENG $GOPTS $N -q \$r/$MOD | ./atascadas --modo $MODE > \$f.res 2> \$f.log || exit 1
  ( flock 9; cat \$f.res >> enc_t\$t.txt; echo \$r >> listas_t\$t.txt ) 9> lock_p011_t\$t
'
echo "tarea p011 \$t fin \$(date)"
EOT
sed -i "s/MOD_PLACEHOLDER/$MOD/g" $BASE/tarea_p011.sh

JID=$(env -u SLURM_JOB_ID -u SLURM_JOBID -u SLURM_CPUS_PER_TASK -u SLURM_MEM_PER_NODE -u SLURM_NTASKS -u SLURM_NNODES -u SLURM_JOB_NODELIST -u SLURM_NODELIST -u SLURM_TASKS_PER_NODE -u SLURM_JOB_CPUS_PER_NODE -u SLURM_CPUS_ON_NODE -u SLURM_SUBMIT_DIR -u SLURM_JOB_PARTITION -u SLURM_JOB_ACCOUNT -u SLURM_JOB_QOS -u SLURM_EXPORT_ENV -u SBATCH_EXPORT \
      sbatch --parsable --export=NONE --array=0-$((NT-1)) $BASE/tarea_p011.sh)
echo "array interno p011: $JID" | tee -a $BASE/bitacora.txt
while squeue -h -j "$JID" 2>/dev/null | grep -q . ; do sleep 120; done
echo "array p011 terminado $(date)" | tee -a $BASE/bitacora.txt
sacct -j $JID --format=JobID,State,Elapsed,MaxRSS,ExitCode -P > $BASE/logs/sacct_p011_$JID.txt 2>/dev/null || true
cp $BASE/logs/sacct_p011_$JID.txt $BASE/tarea_p011.sh ./ 2>/dev/null || true
echo "rebanadas_listas=$(cat $BASE/listas_t*.txt | wc -l)/$MOD" | tee resumen_p011.txt
