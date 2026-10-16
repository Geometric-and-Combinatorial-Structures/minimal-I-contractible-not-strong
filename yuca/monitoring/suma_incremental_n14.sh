#!/bin/bash
# Progress count used during the n=14 K4-free table run (run on the YUCA login node, < 10 min).
# Sums 'conexas=' over the non-empty .log files of the directories given as arguments (out/ or out_m/),
# 8 directories in parallel.  A directory with 1000 non-empty logs is complete and never changes (a .log
# stays empty until its slice finishes), so successive counts only re-read the incomplete directories.
# Usage: suma_incremental_n14.sh out|out_m DIR1 DIR2 ...   -> lines "dir nlogs sum"
B=/lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla; D=$1; shift
cd $B/$D && for x in "$@"; do [ -d $x ] && echo $x; done | nice xargs -P 8 -I{} sh -c 'find {} -name "*.log" -size +0 -print0 | xargs -0 cat | awk -v d={} "{for(i=1;i<=NF;i++) if(\$i ~ /^conexas=/){split(\$i,a,\"=\");s+=a[2];n++}} END{printf \"%s %d %.0f\\n\", d, n, s}"'
