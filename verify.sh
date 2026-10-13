#!/usr/bin/env bash
# verify.sh — reproduces, from scratch, every finite certificate behind the paper's main results.
#
#   Level 0 (no dependencies beyond python3 >= 3.8):  integer homology + exact J_S decisions
#   Level 1 (gcc):                                    cross-check with the C program used on the cluster
#   Level 2 (geng from nauty, optional):              re-derive the cardinality table for n <= 9
#                                                     (pass  --full-table  to go up to n = 11; ~1 h on 8 cores)
#
# Exit status 0 means every check passed.
set -euo pipefail
cd "$(dirname "$0")"
PASS=0; FAIL=0
check () { if [ "$2" = "$3" ]; then echo "  [ok]   $1 = $2"; PASS=$((PASS+1)); else echo "  [FAIL] $1: got '$2', expected '$3'"; FAIL=$((FAIL+1)); fi; }

echo "== Level 0: Python tools =="
H=tools/clique_homology.py; S=tools/strong_contractible.py
# 13 vertices: the three Z/2-acyclic non-J_S graphs all have H_1 = Z/3 (hence are not I-contractible)
check "n=13: graphs with H~1 = Z/3"   "$(python3 $H data/acyclic_not_strong_13.g6 | grep -c 'H~1=Z/3  H~2=0')" 3
check "n=13: Z/2-acyclic"             "$(python3 $H data/acyclic_not_strong_13.g6 | grep -c 'Z2-betti=\[0, 0, 0\]')" 3
check "n=13: not in J_S"              "$(python3 $S data/acyclic_not_strong_13.g6 | grep -c 'NOT in J_S')" 3
check "n=13: stuck"                   "$(python3 $S data/acyclic_not_strong_13.g6 --stuck | grep -c 'stuck=yes')" 1
# 14 vertices: the 51 stuck K4-free graphs
check "n=14: 51 graphs listed"        "$(grep -vc '^#' data/stuck_14_K4free.g6)" 51
check "n=14: Z/2-acyclic"             "$(python3 $H data/stuck_14_K4free.g6 | grep -c 'Z2-betti=\[0, 0, 0\]')" 51
check "n=14: K4-free"                 "$(python3 $H data/stuck_14_K4free.g6 | grep -c 'K4=0')" 51
check "n=14: H~1 = Z/3"               "$(python3 $H data/stuck_14_K4free.g6 | grep -c 'H~1=Z/3')" 48

check "n=14: integer-acyclic (strict)" "$(python3 $H data/stuck_14_K4free.g6 | grep -vc 'NOT Z-acyclic')" 3
check "n=14: not in J_S"              "$(python3 $S data/stuck_14_K4free.g6 | grep -c 'NOT in J_S')" 51
check "n=14: stuck"                   "$(python3 $S data/stuck_14_K4free.g6 --stuck | grep -c 'stuck=yes')" 51
# the three minimal examples become strong I-contractible after adding one I4-edge
check "G14a + {0,1} in J_S"           "$(python3 $S --g6 'M?b@bFHNEk@~|k}U?' --add 0 1 | grep -c '  in J_S')" 1
check "G14b + {0,3} in J_S"           "$(python3 $S --g6 'M?B@thku?~Lylk}[?' --add 0 3 | grep -c '  in J_S')" 1
check "G14c + {2,3} in J_S"           "$(python3 $S --g6 'M?r@d`ifbiFfo}~o?' --add 2 3 | grep -c '  in J_S')" 1
check "N(0,1) in G14a is a path (in J_S)"  "$(python3 - <<'PY'
import sys; sys.path.insert(0,'tools'); import strong_contractible as sc
V,E=sc.parse_g6('M?b@bFHNEk@~|k}U?'); N=sc.nbrs(V,E,0)&sc.nbrs(V,E,1)
print(sorted(N), sc.in_JS(*sc.induced(V,E,N)) is not None)
PY
)" "[5, 8, 10, 12, 13] True"
# dunce hat (Dochtermann et al. 2023, Fig. 2)
check "dunce hat: stuck, not in J_S"  "$(python3 $S --g6 'N|thHsL`sHoI`RPOwLG' --stuck | grep -c 'NOT in J_S  stuck=yes')" 1
check "dunce hat + Fig.2B edge in J_S" "$(python3 $S --g6 'N|thHsL`sHoI`RPOwLG' --add 9 12 | grep -c '  in J_S')" 1
check "dunce hat: integer-acyclic"    "$(python3 $H --g6 'N|thHsL`sHoI`RPOwLG' | grep -vc 'NOT Z-acyclic')" 1

echo "== Level 1: C program (gcc) =="
if command -v gcc >/dev/null; then
  gcc -O2 -o /tmp/atascadas_verify src/atascadas.c -lm
  R=$(grep -v '^#' data/stuck_14_K4free.g6 | /tmp/atascadas_verify --modo verificar)
  check "C: 51 graphs Z/2-acyclic"     "$(echo "$R" | grep -c '^chi=1 conexa=1 aciclica=1')" 51
  check "C: 51 graphs not I_S"         "$(echo "$R" | grep -c 'I_S=0 ')" 51
  check "C: 51 graphs stuck"           "$(echo "$R" | grep -c '(atascada=1)')" 51
  check "C: 51 graphs re-found by --modo atascadas" "$(grep -v '^#' data/stuck_14_K4free.g6 | /tmp/atascadas_verify --modo atascadas | wc -l)" 51
  check "C: G14a+{0,1} is I_S"         "$(echo 'M_b@bFHNEk@~|k}U?' | /tmp/atascadas_verify --modo verificar | grep -c 'I_S=1 ')" 1
  check "C: G14a I-contractible (icert)" "$(echo 'M?b@bFHNEk@~|k}U?' | /tmp/atascadas_verify --modo icert --prof 1 | grep -c 'I-CONTRAIBLE')" 1
else echo "  gcc not found — skipped"; fi

echo "== Level 2: cardinality table (geng) =="
if command -v geng >/dev/null; then
  NMAX=9; [ "${1:-}" = "--full-table" ] && NMAX=11
  for n in $(seq 3 $NMAX); do grep -q "^n=$n " data/table_cardinalities_raw.txt || { echo "  (row n=$n not yet in data file)"; continue; }
    got=$(geng -cq $n | /tmp/atascadas_verify --modo tabla 2>&1)
    exp=$(grep "^n=$n " data/table_cardinalities_raw.txt)
    check "table row n=$n" "$got" "$exp"
  done
else echo "  geng not found — skipped (install nauty to re-derive the table)"; fi

echo; echo "passed=$PASS failed=$FAIL"; [ $FAIL -eq 0 ]
