#!/bin/bash
# Checks to be applied to the graphs reported by the n=14 K4-free table (enc_t*.txt, enc_m_t*.txt):
#  (1) I_NO_IS lines vs the 8 K4-free graphs of data/I_not_strong_14_closure.tsv (canonical forms, labelg);
#  (2) ACICLICA_NO_IS_INDECISA lines: exact integer homology (tools/clique_homology.py) and an independent
#      Ripser check over Z/2 and Z/3 (tools/ripser_z3_check.py).  Usage: verificar_encontradas_n14.sh enc.txt
# Status (2026-10-16): written on 2026-10-15 and not yet run in this form; it will be run, and its output archived,
# on the complete lists when the n=14 row is collected.
# enc.txt: one "TYPE graph6" per line.
E=$1
awk '$1=="I_NO_IS"{print $2}' $E | sort -u > /tmp/f.g6
awk -F'\t' '!/^#/ && $3==0 {print $1}' data/I_not_strong_14_closure.tsv > /tmp/k.g6
labelg -q /tmp/f.g6 | sort -u > /tmp/fc; labelg -q /tmp/k.g6 | sort > /tmp/kc
echo "I_NO_IS: $(wc -l < /tmp/fc) found, $(comm -12 /tmp/fc /tmp/kc | wc -l) equal to known, $(comm -23 /tmp/fc /tmp/kc | wc -l) new"
awk '$1=="ACICLICA_NO_IS_INDECISA"{print $2}' $E | sort -u > /tmp/i.g6; echo "undecided: $(wc -l < /tmp/i.g6)"
python tools/clique_homology.py /tmp/i.g6 | grep -o 'H~1=[^ ]*\|H~2=[^ ]*' | sort | uniq -c
python tools/ripser_z3_check.py /tmp/i.g6
