#!/usr/bin/env bash
# AddressSanitizer + UBSan battery for atascadas_v2 (v2.1).  Usage: tests/run_sanitizers.sh [OUT]
# Default OUT: tests/results/v2.1/sanitizer.txt.  Needs build/atascadas_v2_san (./build.sh), gcc, geng and python3.
# Each line records the label (with the documented exit code expected), the exit code obtained, the number of
# sanitizer reports in stderr and the last line of stderr.  Two positive controls (a heap overflow and a signed
# overflow, compiled with the same sanitizers) must report; if they do not, the configuration is not detecting errors
# and the rest of the log proves nothing.
# Environment notes: detect_leaks=0 because LeakSanitizer cannot run under ptrace; verify_asan_link_order=0 because
# some sandboxes preload a library (LD_PRELOAD), which is kept loaded rather than removed.
set -u
cd "$(dirname "$0")/.."
OUT=${1:-tests/results/v2.1/sanitizer.txt}
mkdir -p "$(dirname "$OUT")"
S=build/atascadas_v2_san
[ -x "$S" ] || { echo "missing $S: run ./build.sh" >&2; exit 1; }
export ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:verify_asan_link_order=0
export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
printf '#include <stdlib.h>\nint main(int c, char **v){ (void)v; int *a = malloc(4*sizeof(int)); a[c+3] = 1; int r = a[1]; free(a); return r; }\n' > "$W/ovf.c"
printf '#include <limits.h>\nint main(int c, char **v){ (void)v; int x = INT_MAX - 1 + c; x = x + c; return x == 0; }\n' > "$W/ub.c"
gcc -O0 -g -fsanitize=address,undefined "$W/ovf.c" -o "$W/ovf"
gcc -O0 -g -fsanitize=address,undefined "$W/ub.c" -o "$W/ub"
RUNS=0
run() {
  local label=$1; shift
  RUNS=$((RUNS + 1))
  local s e rc rep
  s=$(date +%s.%N); { ( "$@" > "$W/out" 2> "$W/err" ); } 2> /dev/null; rc=$?; e=$(date +%s.%N)
  rep=$(grep -c -E "ERROR: AddressSanitizer|runtime error" "$W/err")
  local msg
  msg=$(grep -m1 -E "ERROR: AddressSanitizer|runtime error" "$W/err" || grep -v '^ *$' "$W/err" | tail -1)
  msg=$(printf '%s' "$msg" | sed -e "s|$W|<tmp>|g" -e "s|$PWD|.|g" -e "s|$HOME|~|g" | cut -c1-110)
  printf '%-50s exit=%-3s sanitizer_reports=%s %6.1f s | %s\n' "$label" "$rc" "$rep" "$(echo "$e - $s" | bc)" "$msg"
}
{
  echo "# v2.1 under AddressSanitizer + UBSan: gcc -O1 -g -std=c11 -fsanitize=address,undefined -fno-omit-frame-pointer ($(gcc --version | head -1))"
  echo "# ASAN_OPTIONS=$ASAN_OPTIONS  UBSAN_OPTIONS=$UBSAN_OPTIONS"
  echo "# expected exit codes as documented in src/atascadas_v2.c: 0 ok, 1 usage, 2 capacity, 3 invalid records, 4 internal inconsistency, 6 write error"
  echo "# $(date -u '+%Y-%m-%d %H:%M UTC'); src/atascadas_v2.c SHA-256 $(sha256sum src/atascadas_v2.c | cut -d' ' -f1)"
  echo "# $S SHA-256 $(sha256sum $S | cut -d' ' -f1); reports: $($S --version)"
  run "POSITIVE CONTROL heap overflow (must report)" "$W/ovf"
  run "POSITIVE CONTROL signed overflow (must report)" "$W/ub"
  geng -cq 9 > "$W/n9.g6"; run "tabla, all 261080 connected n=9 (exit 0)" sh -c "$S --modo tabla < $W/n9.g6"
  geng -cq 8 > "$W/n8.g6"
  for m in atascadas casi 2dis_no_1dis; do run "$m, all 11117 connected n=8 (exit 0)" sh -c "$S --modo $m < $W/n8.g6"; done
  run "verificar K16 (exit 0)" sh -c "printf 'O~~~~~~~~~~~~~~~~~~~~\n' | $S --modo verificar"
  cat ../data/acyclic_not_strong_13.g6 ../data/stuck_14_K4free.g6 ../data/dunce_hat_15.g6 | grep -v '^#' | awk 'NF{print $1}' > "$W/special.g6"
  echo "# special graphs: $(wc -l < "$W/special.g6") (data/acyclic_not_strong_13.g6, stuck_14_K4free.g6, dunce_hat_15.g6)"
  for m in verificar icert traza; do run "$m, special graphs (exit 0)" sh -c "$S --modo $m < $W/special.g6"; done
  run "cerradura G14a (exit 0)" sh -c "printf 'M?b@bFHNEk@~|k}U?\n' | $S --modo cerradura"
  printf 'Bw\0' > "$W/a1"; run "adversarial: NUL, no final newline (exit 3)" sh -c "$S --modo tabla < $W/a1"
  printf 'Bw\0bad\nBw\n' > "$W/a2"; run "adversarial: NUL inside a line (exit 3)" sh -c "$S --modo tabla < $W/a2"
  printf 'Bw' > "$W/a3"; run "adversarial: unterminated last line (exit 3)" sh -c "$S --modo tabla < $W/a3"
  printf '>>graph6<<Bw' > "$W/a4"; run "adversarial: unterminated header line (exit 3)" sh -c "$S --modo tabla < $W/a4"
  python3 -c "print('B'+'w'*5000)" > "$W/a5"; run "adversarial: 5001-byte line (exit 3)" sh -c "$S --modo tabla < $W/a5"
  printf 'Bw\n' > "$W/a6"; run "adversarial: --prof 12x (usage, exit 1)" sh -c "$S --modo tabla --prof 12x < $W/a6"
  run "stdout to /dev/full, verificar (exit 6)" sh -c "$S --modo verificar < $W/a6 > /dev/full"
  run "stdout to /dev/full, --version (exit 6)" sh -c "$S --version > /dev/full"
  echo "# runs: $RUNS"
} > "$OUT" 2>&1
if grep -q -F -e "$PWD" -e "$HOME" "$OUT"; then echo "SANITIZERS: the log would record a local path; refusing" >&2; exit 1; fi
cat "$OUT"
# verdict: both controls report; every other line has no sanitizer report and the exit code named in its label
python3 - "$OUT" <<'EOF'
import re, sys
bad, n, runs = [], 0, None
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    if line.startswith("# runs: "):
        runs = int(line.split()[2])
        continue
    m = re.search(r"exit=(\d+)\s+sanitizer_reports=(\d+)", line)
    if not m:
        continue
    n += 1
    rc, rep = int(m.group(1)), int(m.group(2))
    if line.startswith("POSITIVE CONTROL"):
        if rep == 0:
            bad.append("control did not report: " + line.split("exit=")[0].strip())
        continue
    want = re.search(r"exit (\d+)\)", line.split("exit=")[0])
    if rep != 0:
        bad.append("sanitizer report: " + line.split("exit=")[0].strip())
    if want is None or int(want.group(1)) != rc:
        bad.append(f"exit {rc}, label expects {want.group(1) if want else '?'}: " + line.split("exit=")[0].strip())
if runs is None or n != runs or n == 0:
    bad.append(f"{n} result lines for {runs} runs")
print(f"SANITIZERS: {n} of {runs} runs checked;", "PASS (controls detected; no reports; every exit code as labelled)"
      if not bad else "FAILED")
for b in bad:
    print("  " + b)
sys.exit(0 if not bad else 1)
EOF
