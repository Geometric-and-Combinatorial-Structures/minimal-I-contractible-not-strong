#!/usr/bin/env bash
# Builds the binaries used by tests/: v2, v2 with a 6-bit hash, v2 with sanitizers, v1, and v1 with a 6-bit hash.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
CF="-O3 -march=native -std=c11"
gcc $CF -Wall -Wextra -Wpedantic -Werror -o build/atascadas_v2 src/atascadas_v2.c
gcc $CF -Wall -Wextra -Wpedantic -Werror -DHASH_WEAK_BITS=6 -o build/atascadas_v2_weak src/atascadas_v2.c
gcc -O1 -g -std=c11 -Wall -Wextra -Wpedantic -Werror -fsanitize=address,undefined -fno-omit-frame-pointer \
    -o build/atascadas_v2_san src/atascadas_v2.c
gcc $CF -o build/atascadas_v1 ../src/atascadas.c
sed 's/return h|1;/return (h \& 0x3full)|1;/' ../src/atascadas.c > build/atascadas_v1_weak.c
grep -q '0x3full' build/atascadas_v1_weak.c
gcc $CF -o build/atascadas_v1_weak build/atascadas_v1_weak.c
ls -la build
