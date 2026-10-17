#!/bin/bash
#SBATCH --account=p029
#SBATCH --qos=qos029
#SBATCH --partition=cpu
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=32G
#SBATCH --job-name=n14_medio_p029b
# Frente INTERMEDIO m029b de la tabla fila 14 K4-libre (geng28 -k -c 14 r/2000000), autorizado por el autor el 17-oct-2026.
# Mismo esquema que frente_medio_n14_p029_asc.sh (m029, COMPLETED 0:0 el 16-oct-2026): escribe en out_m/, candado lock_m_t*,
# encontradas enc_m_t*, lista propia listas_m_m029b.txt, y sólo AÑADE a listas_t$t.txt (t = r mod 7) las rebanadas que
# termina con éxito (pipefail). No toca los trabajos en marcha ni sus archivos de salida.
# Usa el MISMO binario ./atascadas del directorio (nodos amdcpu, como los frentes principales). Antes de registrar nada:
#  (1) exige el SHA-256 de ese binario; (2) recalcula en este nodo las rebanadas de control 1998006 y 1998007 (en el
#      directorio del trabajo, no en el experimento) y exige .log y .res byte a byte iguales a out/1998/<r>.{log,res}.
# Rango acotado r = 290000 -> 172000 (descendente), para terminar junto con los demás frentes sin duplicar rebanadas
# pesadas antiguas que siguen en curso.
set -u
B=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla
GENG=/lustre/proyectos/p029/busqueda_minimal/bin/geng28
ID=m029b; START=290000; STEP=-1; END=172000
ATAS_SHA=c6a7c7cb96924ae202af56b96d8051d1999ca05781964dbe53e372d441b53b17
H=$(hostname)
sha256sum $B/atascadas | cut -d' ' -f1 > atascadas.sha256
if [ "$(cat atascadas.sha256)" != "$ATAS_SHA" ]; then
  echo "frente $ID $(date) $H: SHA de atascadas distinto, no se hace nada" >> $B/bitacora_medio.txt; exit 1
fi
for r in 1998006 1998007; do
  $GENG -k -c 14 -q $r/2000000 | $B/atascadas --modo tabla > control_$r.res 2> control_$r.log
  if ! cmp -s control_$r.log $B/out/1998/$r.log || ! cmp -s control_$r.res $B/out/1998/$r.res; then
    echo "frente $ID $(date) $H: CONTROL $r NO coincide, no se hace nada" >> $B/bitacora_medio.txt; exit 1
  fi
done
cd $B
echo "frente intermedio $ID inicio $(date) nodo $H START=$START STEP=$STEP END=$END cpus=$SLURM_CPUS_PER_TASK job=$SLURM_JOB_ID; atascadas $ATAS_SHA; controles 1998006/1998007 idénticos" >> bitacora_medio.txt
export GENG ID
seq $START $STEP $END | xargs -P $SLURM_CPUS_PER_TASK -I{} bash -c '
  set -o pipefail; r={}; t=$((r%7))
  grep -qx "$r" listas_t$t.txt && exit 0
  d=out_m/$((r/1000)); mkdir -p $d; f=$d/$r
  $GENG -k -c 14 -q $r/2000000 | ./atascadas --modo tabla > $f.res 2> $f.log || { echo "$r" >> fallidas_$ID.txt; exit 0; }
  ( flock 9; cat $f.res >> enc_m_t$t.txt; echo $r >> listas_m_$ID.txt; echo $r >> listas_t$t.txt ) 9> lock_m_t$t
'
echo "frente intermedio $ID fin $(date)" >> bitacora_medio.txt
