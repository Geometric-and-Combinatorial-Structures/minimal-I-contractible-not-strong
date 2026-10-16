#!/bin/bash
# Local sample (8 cores) of 32 random intermediate slices of geng -k -c 14 r/2000000, used on 14 Oct 2026 to
# estimate the total work of the n=14 K4-free table.  Output: "r count seconds" (TIMEOUT = more than 1500 s).
python -c "
import random; random.seed(14)
print('\n'.join(str(r) for r in sorted(random.sample(range(24000,1280000),32))))" > muestra_r.txt
cat muestra_r.txt | xargs -P 8 -I{} sh -c 's=$(date +%s); o=$(timeout 1500 geng -k -c -u 14 {}/2000000 2>&1 | grep -o "[0-9]* graphs" | awk "{print \$1}"); echo "{} ${o:-TIMEOUT} $(( $(date +%s)-s ))"' | sort -n
