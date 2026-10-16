#!/bin/bash
# Number of connected K4-free graphs on n vertices (geng -k -c -u), used to extrapolate the size of the n=14
# K4-free table.  Results (14 Oct 2026): n=8: 5606, 9: 95915, 10: 2784072, 11: 135885572, 12: 10977061102.
for n in 8 9 10 11; do echo -n "$n "; geng -k -c -u $n 2>&1 | grep -o '[0-9]* graphs'; done
seq 0 63 | xargs -P 8 -I{} sh -c 'geng -k -c -u 12 {}/64 2>&1 | grep -o "[0-9]* graphs"' | awk '{s+=$1} END{print "12", s, "graphs"}'
