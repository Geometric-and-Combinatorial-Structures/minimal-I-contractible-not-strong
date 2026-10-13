#SBATCH --account=p011
#SBATCH --qos=qos011
#SBATCH --partition=cpu
#SBATCH --time=7-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

# ============================================================================
# envoltorio_n14_tabla.sh — Búsqueda exhaustiva de gráficas Z2-acíclicas
# atascadas — TABLA fila 14 restringida a K4-LIBRES conexas (sin vértices ni aristas I_S-contraíbles) con n=14 vértices, YUCA.
# Lanza un job array interno de 7 nodos x 64 CPU y reparte 2000000 rebanadas
# res/mod de geng. Resultados persistentes en /lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla.
# Generador: geng -k -c 14 -q r/2000000     Filtro: atascadas --modo tabla
# Reanudable: las rebanadas ya listas (registradas en listas_t*.txt) se omiten.
# ============================================================================
set +e; set -uo pipefail
N=14; MOD=2000000; NT=7; GOPTS="-k -c"; MODE=tabla
BASE=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla
GENG=/lustre/proyectos/p029/busqueda_minimal/bin/geng28
WORK=$PWD
mkdir -p $BASE/out $BASE/logs
cp -f /lustre/proyectos/p029/busqueda_minimal/src/atascadas.c $BASE/
cd $BASE
gcc -O3 -march=native -std=c11 -o atascadas atascadas.c || { echo "fallo compilación"; exit 1; }
echo "inicio $(date)  nodo $(hostname)  N=$N MOD=$MOD NT=$NT GOPTS=$GOPTS MODE=$MODE" | tee -a $BASE/bitacora.txt
for t in $(seq 0 $((NT-1))); do touch $BASE/listas_t$t.txt $BASE/enc_t$t.txt; done

cat > $BASE/tarea.sh <<EOT
#!/bin/bash
#SBATCH --account=p011
#SBATCH --qos=qos011
#SBATCH --partition=cpu
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=32G
#SBATCH --job-name=atasc_n14
#SBATCH --output=$BASE/logs/tarea_%A_%a.out
cd $BASE
t=\$SLURM_ARRAY_TASK_ID; export t
echo "tarea \$t inicio \$(date) en \$(hostname)"
# la tarea t procesa las rebanadas r = t, t+NT, t+2NT, ... con 64 procesos en paralelo
seq \$t $NT $((MOD-1)) | xargs -P 64 -I{} bash -c '
  r={}; d=out/\$((r/1000)); mkdir -p \$d; f=\$d/\$r
  grep -qx "\$r" listas_t\$t.txt && exit 0
  $GENG $GOPTS $N -q \$r/$MOD | ./atascadas --modo $MODE > \$f.res 2> \$f.log || exit 1
  ( flock 9; cat \$f.res >> enc_t\$t.txt; echo \$r >> listas_t\$t.txt ) 9> lock_t\$t
'
echo "tarea \$t fin \$(date)"
EOT

# sbatch interno: quitar variables heredadas de SLURM
JID=$(env -u SLURM_JOB_ID -u SLURM_JOBID -u SLURM_CPUS_PER_TASK -u SLURM_MEM_PER_NODE -u SLURM_NTASKS -u SLURM_NNODES -u SLURM_JOB_NODELIST -u SLURM_NODELIST -u SLURM_TASKS_PER_NODE -u SLURM_JOB_CPUS_PER_NODE -u SLURM_CPUS_ON_NODE -u SLURM_SUBMIT_DIR -u SLURM_JOB_PARTITION -u SLURM_JOB_ACCOUNT -u SLURM_JOB_QOS -u SLURM_EXPORT_ENV -u SBATCH_EXPORT \
      sbatch --parsable --export=NONE --array=0-$((NT-1)) $BASE/tarea.sh)
echo "array interno: $JID" | tee -a $BASE/bitacora.txt
T0=$(date +%s)
# vigilancia: progreso y encontradas acumuladas cada 60 s
while squeue -h -j "$JID" 2>/dev/null | grep -q . ; do
  DONE=$(cat $BASE/listas_t*.txt | wc -l)
  cat $BASE/enc_t*.txt > $BASE/encontradas_n14_acum.txt
  FOUND=$(wc -l < $BASE/encontradas_n14_acum.txt)
  echo "$(date +%F_%T) transcurrido=$(( $(date +%s)-T0 ))s rebanadas_listas=$DONE/$MOD encontradas=$FOUND" > $BASE/progreso.txt
  sleep 60
done
echo "array terminado $(date)" | tee -a $BASE/bitacora.txt
sacct -j $JID --format=JobID,State,Elapsed,MaxRSS,ExitCode -P > $BASE/logs/sacct_$JID.txt 2>/dev/null || true
# recolección
cat $BASE/enc_t*.txt > $BASE/encontradas_n14.txt
find $BASE/out -name '*.log' -print0 | xargs -0 cat | awk -F'[ =]' '{for(i=1;i<=NF;i++) if($i ~ /^(total|pasa_cono|pasa_chi|pasa_vecindades|pasa_aristas|encontradas|conexas|chi1|aciclicas|I|I_indecisas|I_S|I_SV|3-Dis|2-Dis|1-Dis|0-Dis|-1-Dis)$/) s[$i]+=$(i+1)} END{for(k in s) printf "%s=%d\n", k, s[k]}' | sort > $BASE/resumen_n14.txt
DONE=$(cat $BASE/listas_t*.txt | wc -l)
echo "rebanadas_listas=$DONE/$MOD" >> $BASE/resumen_n14.txt
echo "faltantes:" >> $BASE/resumen_n14.txt
comm -23 <(seq 0 $((MOD-1)) | sort) <(cat $BASE/listas_t*.txt | sort) | sort -n >> $BASE/resumen_n14.txt
cp $BASE/resumen_n14.txt $BASE/encontradas_n14.txt $BASE/bitacora.txt $WORK/ 2>/dev/null || true
cp $BASE/atascadas.c $WORK/atascadas_usado.c; cp $BASE/tarea.sh $WORK/tarea_usada.sh
echo "fin $(date)" | tee -a $BASE/bitacora.txt
cat $BASE/resumen_n14.txt | head -40
ls -lh $WORK || true
