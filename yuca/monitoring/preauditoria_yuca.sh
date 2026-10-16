#!/bin/bash
#SBATCH --account=p011
#SBATCH --qos=qos011
#SBATCH --partition=gpu
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=3
#SBATCH --mem=12G
#SBATCH --job-name=preauditoria_n14
# PREAUDITORÍA (sólo lectura sobre el experimento): todo se escribe en el directorio de trabajo de este job.
set +e; set -u
B=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla
GENG=/lustre/proyectos/p029/busqueda_minimal/bin/geng28
W=$PWD; mkdir -p $W/ev $W/rec
echo "inicio $(date) nodo $(hostname) job $SLURM_JOB_ID" > $W/preauditoria_bitacora.txt
# 1) binarios propios, compilados en este nodo desde copias de las fuentes
cp $B/atascadas.c $W/atascadas_asrun.c
sha256sum $W/atascadas_asrun.c $W/atascadas_exacta.c $GENG > $W/ev/sha256_fuentes_y_geng.txt
gcc -O3 -march=native -std=c11 -o $W/atas_o $W/atascadas_asrun.c && gcc -O3 -march=native -std=c11 -o $W/atas_e $W/atascadas_exacta.c || { echo "FALLO compilación" >> $W/preauditoria_bitacora.txt; exit 1; }
# 2) muestra reproducible de rebanadas registradas (semilla fija), por tipo de frente
cat $B/listas_t*.txt | sort -n -u > $W/registradas.txt
sort -n -u $B/listas_m_m029.txt $B/listas_m_m011.txt > $W/medio_cpu.txt
sort -n -u $B/listas_m_m011a.txt $B/listas_m_m011b.txt > $W/medio_gpu.txt
comm -23 $W/registradas.txt <(sort -n -u $W/medio_cpu.txt $W/medio_gpu.txt) > $W/principal.txt
pick () { # $1 lista, $2 directorio (out|out_m), $3 cuántas, $4 semilla, $5 etiqueta
  shuf --random-source=<(yes $4) $1 | while read r; do f=$B/$2/$((r/1000))/$r.log; [ -s $f ] || continue
    c=$(grep -o 'conexas=[0-9]*' $f | cut -d= -f2); [ -n "$c" ] || continue
    if [ $c -ge 100000 ] && [ $c -le 15000000 ]; then echo "$r $2 $5"; fi; done | head -$3; }
{ pick $W/principal.txt out 30 101 principal; pick $W/medio_cpu.txt out_m 10 202 medio_cpu; pick $W/medio_gpu.txt out_m 10 303 medio_gpu; } > $W/muestra.txt
echo "muestra: $(wc -l < $W/muestra.txt) rebanadas" >> $W/preauditoria_bitacora.txt
# 3) recálculo: original (byte a byte), variante exacta (log idéntico + estadísticas memo), conteo geng -u
export B GENG W
cat $W/muestra.txt | xargs -P 3 -L 1 bash -c '
  r=$0; D=$1; tipo=$2; o=$B/$D/$((r/1000))/$r
  $GENG -k -c 14 -q $r/2000000 | $W/atas_o --modo tabla > $W/rec/$r.res 2> $W/rec/$r.log
  $GENG -k -c 14 -q $r/2000000 | $W/atas_e --modo tabla > $W/rec/$r.eres 2> $W/rec/$r.elog
  u=$($GENG -k -c -u 14 $r/2000000 2>&1 | grep -o "[0-9]* graphs" | cut -d" " -f1)
  c=$(grep -o "conexas=[0-9]*" $o.log | cut -d= -f2)
  lo=$(cmp -s $W/rec/$r.log $o.log && echo IGUAL || echo DIFIERE)
  ro=$(cmp -s <(sort $W/rec/$r.res) <(sort $o.res) && echo IGUAL || echo DIFIERE)
  le=$(cmp -s <(head -1 $W/rec/$r.elog) $o.log && echo IGUAL || echo DIFIERE)
  st=$(grep AUDIT $W/rec/$r.elog | cut -d" " -f3-)
  echo "$r $tipo conexas_log=$c conteo_geng_u=$u log_original=$lo res_original=$ro log_exacta=$le $st"
' > $W/preauditoria_resultados.txt
# 4) instantánea de evidencias (copias de archivos pequeños; nada se modifica en $B)
cp $B/bitacora.txt $B/bitacora_medio.txt $B/progreso.txt $B/tarea.sh $B/tarea_p011.sh $W/ev/ 2>/dev/null
cp $B/listas_m_*.txt $W/ev/; cat $B/enc_t*.txt > $W/ev/enc_principales.txt; cat $B/enc_m_t*.txt > $W/ev/enc_intermedios.txt
grep -h ERROR $B/enc_t*.txt $B/enc_m_t*.txt > $W/ev/enc_errores.txt; echo "lineas ERROR: $(wc -l < $W/ev/enc_errores.txt)" >> $W/preauditoria_bitacora.txt
for t in 0 1 2 3 4 5 6; do echo "t$t lineas=$(wc -l < $B/listas_t$t.txt) unicas=$(sort -u $B/listas_t$t.txt | wc -l) residuo_incorrecto=$(awk -v t=$t '$1%7!=t' $B/listas_t$t.txt | wc -l) fuera_de_rango=$(awk '$1<0||$1>1999999' $B/listas_t$t.txt | wc -l)"; done > $W/ev/registros_por_residuo.txt
gzip -c $W/registradas.txt > $W/ev/rebanadas_registradas_unicas.txt.gz
ls $B/logs | head -50 > $W/ev/logs_tareas_lista.txt; for f in $B/logs/*.out; do echo "== $(basename $f)"; head -3 $f; tail -3 $f; grep -i -E 'error|killed|oom|segmentation|fallo' $f | head -5; done > $W/ev/logs_tareas_extracto.txt 2>&1
ls $B/gpu_bin > $W/ev/gpu_bin_lista.txt; cat $B/gpu_bin/control_*.log > $W/ev/gpu_bin_controles.txt 2>/dev/null; sha256sum $B/gpu_bin/atascadas_* $B/atascadas > $W/ev/sha256_binarios_en_uso.txt 2>/dev/null
cat $B/fallidas_* > $W/ev/fallidas.txt 2>/dev/null; echo "fallidas: $(cat $W/ev/fallidas.txt 2>/dev/null | wc -l)" >> $W/preauditoria_bitacora.txt
sacct -X -n -P -j 2084886,2084887,2085017,2085018,2085231,2085232,2085550,2085618,2085622,2085623,2085624 -o JobID,JobName%30,Account,Partition,AllocCPUS,State,ExitCode,Submit,Start,End,NodeList > $W/ev/sacct_n14_tabla.txt
sacct -n -P -j 2084887,2085018,2085231,2085623,2085624 -o JobID,State,ExitCode,MaxRSS,ReqMem > $W/ev/sacct_n14_tabla_pasos.txt
squeue -u $USER -o '%i %a %P %T %C %M %N' > $W/ev/squeue_instantanea.txt; date > $W/ev/fecha_instantanea.txt
tar czf $W/evidencia_yuca_n14_$(date +%Y%m%d_%H%M).tar.gz -C $W ev preauditoria_resultados.txt preauditoria_bitacora.txt muestra.txt
echo "fin $(date)" >> $W/preauditoria_bitacora.txt
