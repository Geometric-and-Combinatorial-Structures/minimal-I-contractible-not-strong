#!/bin/bash
#SBATCH --account=p029
#SBATCH --qos=qos029
#SBATCH --partition=cpu
#SBATCH --time=1-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=24G
# Extraction of the connected 12-vertex graphs that are 2-dismantlable but not 1-dismantlable
# (geng -c 12, 4000 res/mod slices, atascadas --modo 2dis_no_1dis), single 48-core task (fits the free part of the p029 QOS).
set +e; set -uo pipefail
BASE=/lustre/proyectos/p029/busqueda_minimal/n12_2dis_no_1dis_48
GENG=/lustre/proyectos/p029/Librerias/nauty27r4/geng
WORK=$PWD
mkdir -p $BASE/out
cp -f $WORK/atascadas.c $BASE/atascadas.c
cd $BASE
gcc -O3 -march=native -std=c11 -o atascadas atascadas.c -lm || { echo "compile failed"; exit 1; }
touch listas.txt enc.txt
echo "inicio $(date) nodo $(hostname) cpus=$SLURM_CPUS_PER_TASK" | tee -a bitacora.txt
export GENG
seq 0 3999 | xargs -P 48 -I{} bash -c '
  set -o pipefail; r={}; d=out/$((r/100)); mkdir -p $d; f=$d/$r
  grep -qx "$r" listas.txt && exit 0
  $GENG -c 12 -q $r/4000 | ./atascadas --modo 2dis_no_1dis > $f.res 2> $f.log || exit 1
  ( flock 9; cat $f.res >> enc.txt; echo $r >> listas.txt ) 9> lock
'
echo "fin $(date)" | tee -a bitacora.txt
sort -u enc.txt > encontradas_2dis_no_1dis_n12.txt
find out -name '*.log' -print0 | xargs -0 cat | awk -F'[ =]' '{for(i=1;i<=NF;i++) if($i=="total") t+=$(i+1)} END{print "total="t}' > resumen.txt
echo "rebanadas_listas=$(sort -u listas.txt | wc -l)/4000" >> resumen.txt
echo "faltantes=$(comm -23 <(seq 0 3999 | sort) <(sort -u listas.txt) | wc -l)" >> resumen.txt
echo "encontradas=$(wc -l < encontradas_2dis_no_1dis_n12.txt)" >> resumen.txt
cp encontradas_2dis_no_1dis_n12.txt resumen.txt bitacora.txt $WORK/
cat resumen.txt; cat encontradas_2dis_no_1dis_n12.txt
