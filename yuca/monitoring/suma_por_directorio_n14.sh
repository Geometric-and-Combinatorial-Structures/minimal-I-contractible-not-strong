#!/bin/bash
#SBATCH --account=p029
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --job-name=suma_n14
cd /lustre/proyectos/p029/busqueda_minimal/n14_K4libre_tabla/out
date
ls | sort -n | xargs -P 8 -I{} sh -c 'find {} -name "*.log" -size +0 -print0 | xargs -0 cat | awk -v d={} "{for(i=1;i<=NF;i++) if(\$i ~ /^conexas=/){split(\$i,a,\"=\");s+=a[2];n++}} END{printf \"%s %d %.0f\\n\", d, n, s}"' | sort -n > $OLDPWD/suma_por_dir.txt
date
awk '{n+=$2; s+=$3} END{printf "logs %d suma %.6e\n", n, s}' $OLDPWD/suma_por_dir.txt
