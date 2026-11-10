# Full reproduction of the table and finite catalogs

This route generates the input universes again. It may require a large allocation of compute and storage. The quick verifier never starts it. Commands below run from the repository root in Bash; replace the executable paths and fresh output paths before use.

## Campaign names and software

Campaign names are words, not coefficient fields. Homology coefficients are written `Z`, `F_2` and `F_3` below.

| Name used here | Historical record name | Universe and purpose |
|---|---|---|
| table12 | F2_12 | All connected order-12 graphs; full table row |
| table13 | F2_13 | All connected order-13 graphs; full table row |
| table14 | F4 | All connected K4-free order-14 graphs; full table row |
| seeds14 | F3 | K4-free, biconnected order-14 graphs, minimum degree at least 4 and maximum degree at most 12; stuck seeds |

The historical filenames under `data/census/` retain these old identifiers for traceability. The initial letter F in an identifier says nothing about homology coefficients.

Requirements are Python 3.11+, GCC with C11 support and nauty `geng`. K4-free generation requires support for `-k`. Isomorphism comparisons below also use nauty `labelg`. The partition driver requires Unix file locking. Its C classifier accepts graph orders 1–16. Counting-mode input records must be valid graph6, have one common order and end in a newline. Use the current classifier for a new run; [small-order provenance](small-order-provenance.md) explains the historical implementations of rows 3–11.

The recorded table12/table13/seeds14/table14 runs used classifier v2.2 and driver v2.4. Their source hashes are:

- `v2/src/atascadas_v2.c`: `bd18224f907971e298a3997fad156628ed0f4aca0737beec3e7c900599782e8a`
- `v2/pipeline/campana_v2.py`: `d417c200bb4a9e7d8274899332f44a7a9890003310f1bc6d8b7d5b640cd362a3`

### Fix the executable identities before a run

Choose the binaries that will actually be used. Record their version responses and SHA-256 values before initializing any run, and keep those values unchanged throughout it. A new build can have different bytes from a historical executable. That is compatible with reproducing the union of a graph universe; it does not establish identical residue assignments. Residue-by-residue historical comparisons require the same generator bytes, options and modulus, including the generator's splitting options.

```bash
set -euo pipefail
REPO=$(pwd)
GENG=/absolute/path/to/geng
LABELG=/absolute/path/to/labelg
"$GENG" --version
"$LABELG" --version
sha256sum "$GENG" "$LABELG"
# Copy the observed version token and hashes into these fixed values:
GENG_VERSION=replace_with_observed_token
GENG_SHA256=replace_with_sha256_of_the_binary_selected_above
LABELG_SHA256=replace_with_sha256_of_the_binary_selected_above
printf '%s  %s\n' "$GENG_SHA256" "$GENG" "$LABELG_SHA256" "$LABELG" | sha256sum -c -
```

Historical identity records are included, without distributing executables:

| Executable recorded | Version token | SHA-256 |
|---|---|---|
| Unrestricted generator |2.7000|`4c7d127ad7ee2f531c431bdc536f0753df84d4f5b04beb6f4aa81f696d707ddb`|
| K4-free generator, historically named geng28 |2.9301|`179508d908b1f399fde36cb0e702960150eaa8b48ba0788bc8627cbdf33ae2cb`|
| Canonical labeller |2.7000|`f6a1ded5fcabc96a075090dd9992da1c7115862fc1d6cdcfb99c1643106b8f33`|
| Generator in separate small-order checks |2.8090|`7d3e7c585e52445c1e3ab4d1d19abcaf8b45fbb351ea15663e7e2307370846f5`|

Sources: `finite/provenance/generator_probe_2026-10-17.json` and `nauty289_identity.json`. These are identities of preserved or probed executables, not authentication of every earlier invocation.

## Generate each table row

Set `N`, `MOD`, `WORKERS` and `GENERATOR_FLAGS` for the desired row:

| Row | Flags | Executable choice of MOD/WORKERS | Historical partition information |
|---|---|---|---|
|3–10|`-c`|1 / 1|Separate local checks used unsplit streams|
|11|`-c`|4 / 4|The exact-state local recount used residues 0/4 through 3/4|
|12|`-c`|4000 / 896|table12 used 4000 residues and 896 workers|
|13|`-c`|200000 / 896|table13 used 200000 residues and 896 workers|
|14|`-c -k`|2000000 / 896|table14 used 2000000 residues and 896 workers|

The first two pairs are explicit settings for a new current-driver reproduction, not a claim that the historical small-order runs used that driver. `MOD=1, WORKERS=1` is accepted by the driver. For any row one may choose another positive modulus and `1 <= WORKERS <= MOD`; every residue must still be covered exactly once. The one-worker examples are convenient executable specifications, not speed estimates.

```bash
RUN=/absolute/path/to/new-table14-run
N=14
MOD=2000000
WORKERS=896
GENERATOR_FLAGS='-c -k'
python3 -P "$REPO/v2/pipeline/campana_v2.py" init \
  --root "$RUN" --n "$N" --mod "$MOD" --workers "$WORKERS" \
  --mode tabla --geng "$GENG" --geng-args="$GENERATOR_FLAGS" \
  --source "$REPO/v2/src/atascadas_v2.c" \
  --expect-geng-version "$GENG_VERSION" --expect-geng-sha256 "$GENG_SHA256"
for ((worker=0; worker<WORKERS; worker++)); do
  python3 -P "$RUN/bin/campana_v2.py" worker \
    --config "$RUN/config.json" --worker-id "$worker"
done
python3 -P "$RUN/bin/campana_v2.py" aggregate \
  --config "$RUN/config.json" \
  --reference-csv "$REPO/data/raw_classifier_reference.csv"
```

The run directory must not exist, and its parent must exist. Use the pinned driver copied to `RUN/bin/`. Parallel scheduling can replace the sequential loop, but all worker exits must be checked before aggregation. No scheduler is required by the classifier. The aggregator validates every receipt, complete residue coverage, identities, counts and output hashes. The current invocation must exit zero and create a terminal successful attempt bound to its aggregate hash; files from an earlier success do not certify a later failed invocation. See `v2/README.md`.

Repeat for each row with the settings above. The reference CSV contains all twelve raw fields in the exact vocabulary accepted by the driver. The row14 reference always means K4-free, even though this legacy raw-counter schema has no universe column. The mathematical CSV `data/cardinalities.csv` explicitly names the universe and both coefficient columns.

## Required adjudication of every residual

The raw `I` counter counts positive certificates. Failed bounded searches remain in `ACICLICA_NO_IS_INDECISA.g6`; they are not negative decisions. After successful table aggregation, this homology stage is **required whenever residuals are present, for both the exact I count and the integral column of the complete route**. It is not part of the quick route, which checks the supplied finite residual lists with its separate standard-library implementation.

```bash
python3 -P "$REPO/tools/homology/adjudicate_inventory_r2.py" \
  --campaign "$RUN" \
  --independent "$REPO/tools/homology/independent_homology_r2.py" \
  --out "${RUN}-homology"
```

This stage requires NumPy and Ripser. The output directory must be new and outside the input run. Require the real exit zero, `summary.json` with `PASS: true`, processed count equal to the raw residual count and unchanged input hashes. The method checks integer homology in every dimension and compatibility with computations over `F_2` and `F_3`, without changing raw counters. An empty residual list needs no homological decisions; recording an empty successful adjudication is also supported.

The historical table has no residual below order 13, three at order 13 and 625 in table14. Each has H1=Z/3 and no other reduced integral homology. A new unresolved residual prevents final classification. A timeout or failed certificate search is not a negative proof. For a completed **table14** run, compare its positive set with the eight classes and check the stored admissible paths and one-edge certificates:

```bash
POSITIVE_CHECK="${RUN}-positive-check"
mkdir "$POSITIVE_CHECK"
test "$(wc -l < "$RUN/I_NO_IS.g6")" -eq 8
"$LABELG" -q "$RUN/I_NO_IS.g6" | LC_ALL=C sort -u \
  > "$POSITIVE_CHECK/new.canonical.g6"
awk -F '\t' 'NR>1 {print $1}' "$REPO/finite/data/K4_free_I_not_strong_14.tsv" \
  > "$POSITIVE_CHECK/reference.g6"
"$LABELG" -q "$POSITIVE_CHECK/reference.g6" | LC_ALL=C sort -u \
  > "$POSITIVE_CHECK/reference.canonical.g6"
cmp "$POSITIVE_CHECK/new.canonical.g6" "$POSITIVE_CHECK/reference.canonical.g6"
python3 -P "$REPO/finite/data/check_small_closures.py" \
  > "$POSITIVE_CHECK/certificate-check.json"
printf '%s  %s\n' "$LABELG_SHA256" "$LABELG" | sha256sum -c -
```

The canonical comparison transfers the checked certificates from the reference labellings to the newly generated isomorphism classes. Requiring eight input records and equality with eight distinct reference classes also excludes duplicate isomorphism classes. These commands concern the positive exceptions of table14; rows with no positive exceptions do not run this eight-class comparison. The integral column equals the raw positive I count only after the exhaustive residual partition is resolved; it is a derived column, not an independent integral census.

## Reproduce the 51 stuck seeds: seeds14

`-C` means biconnected; `-k` means K4-free. The reduction lemmas justify the degree and connectivity restrictions for the stuck-seed search. **Do not use these filters for the full table14 row.** The graph6 reference below exists and has 51 entries; its TSV dictionary is under `finite/data/`.

```bash
SEED_RUN=/absolute/path/to/new-seeds14-run
SEED_MOD=2000000
SEED_WORKERS=896
python3 -P "$REPO/v2/pipeline/campana_v2.py" init \
  --root "$SEED_RUN" --n 14 --mod "$SEED_MOD" --workers "$SEED_WORKERS" \
  --mode atascadas --geng "$GENG" --geng-args='-k -C -d4 -D12' \
  --source "$REPO/v2/src/atascadas_v2.c" \
  --expect-geng-version "$GENG_VERSION" --expect-geng-sha256 "$GENG_SHA256"
for ((worker=0; worker<SEED_WORKERS; worker++)); do
  python3 -P "$SEED_RUN/bin/campana_v2.py" worker \
    --config "$SEED_RUN/config.json" --worker-id "$worker"
done
python3 -P "$SEED_RUN/bin/campana_v2.py" aggregate \
  --config "$SEED_RUN/config.json" --expect encontradas=51 \
  --reference-g6 "$REPO/data/stuck_14_K4free.g6" \
  --labelg "$LABELG" --expect-labelg-sha256 "$LABELG_SHA256"
```

The aggregator freezes a copy of `labelg` and verifies its hash before and after canonicalization. Success proves equality of the generated and reference sets up to isomorphism under the documented execution contract. It does not replace the table14 calculation.

The retained seeds14 result is complete, rather than an outstanding launch: its aggregate records all 2,000,000 residues, 64,856,470,381,820 generated graphs, 51 output classes, `ok: true` and no problems. The selected aggregate is `data/census/F3_aggregate.json`, with attempt identifier `20261029T224045.532685Z-16b1e100`.

That run compared the final 51-class set up to isomorphism and its aggregate counters with the earlier search; it did **not** compare old and new outputs residue by residue. It also did not include the later homology stage. The present finite checks verify the 48 torsion seeds and three positive certificates separately. Complete historical receipts and scheduler records remain in the authors' project archive and are not authenticated by this compact selection.

## Catalog of 20 and finite pruned closures

The options differ because the Python driver uses `--mode`, while the C executable uses `--modo`. Build the current C executable in a fresh working directory:

```bash
CATALOG_RUN=/absolute/path/to/new-catalog-run
mkdir "$CATALOG_RUN"
gcc -O3 -std=c11 -Wall -Wextra -Wpedantic -Werror \
  -o "$CATALOG_RUN/classifier" "$REPO/v2/src/atascadas_v2.c"
CATALOG_MOD=4000
mkdir "$CATALOG_RUN/parts"
for ((residue=0; residue<CATALOG_MOD; residue++)); do
  "$GENG" -c 12 "$residue/$CATALOG_MOD" \
    2> "$CATALOG_RUN/parts/$residue.geng.stderr" | \
    "$CATALOG_RUN/classifier" --modo 2dis_no_1dis \
      > "$CATALOG_RUN/parts/$residue.raw" \
      2> "$CATALOG_RUN/parts/$residue.classifier.stderr"
  awk '$1=="2DIS_NO_1DIS" {print $2}' "$CATALOG_RUN/parts/$residue.raw" \
    > "$CATALOG_RUN/parts/$residue.g6"
done
cat "$CATALOG_RUN/parts/"*.g6 > "$CATALOG_RUN/strict12.g6"
test "$(wc -l < "$CATALOG_RUN/strict12.g6")" -eq 20
"$LABELG" -q "$CATALOG_RUN/strict12.g6" | LC_ALL=C sort -u > "$CATALOG_RUN/strict12.canonical.g6"
awk 'NF && $0 !~ /^#/ {print}' "$REPO/data/strictly_2dis_12.g6" > "$CATALOG_RUN/strict12.reference-input.g6"
"$LABELG" -q "$CATALOG_RUN/strict12.reference-input.g6" | LC_ALL=C sort -u > "$CATALOG_RUN/strict12.reference.g6"
cmp "$CATALOG_RUN/strict12.canonical.g6" "$CATALOG_RUN/strict12.reference.g6"
```

The `set -euo pipefail` at the start is required throughout these pipelines. Keep their logs and require all exits zero. The reference file contains exactly 20 graph6 records and no comments; the filtering step also accepts older commented exports. The order-12 pass examines 164,059,830,476 connected graphs; the example divides that universe into 4,000 residues. Its sequential loop specifies complete coverage, not an efficient production schedule: the residue jobs may be scheduled in parallel, but every residue must finish successfully before concatenation. An unsplit stream is not recommended. This stage is not part of the quick route. The difference of the two table columns supplies a separate arithmetic consistency check that the catalog has 20 classes.

For all 51 seeds, generate the pruned closure and canonicalize only the non-strong states:

```bash
"$CATALOG_RUN/classifier" --modo cerradura < "$REPO/data/stuck_14_K4free.g6" \
  > "$CATALOG_RUN/closures.raw" 2> "$CATALOG_RUN/closures.stderr"
awk '$1=="NO_I_S" {print $2}' "$CATALOG_RUN/closures.raw" > "$CATALOG_RUN/closures.g6"
"$LABELG" -q "$CATALOG_RUN/closures.g6" | LC_ALL=C sort -u > "$CATALOG_RUN/closures.canonical.g6"
awk -F '\t' 'NR>1 {print $1}' "$REPO/finite/data/acyclic_not_strong_14_closure.tsv" > "$CATALOG_RUN/closures.reference.g6"
"$LABELG" -q "$CATALOG_RUN/closures.reference.g6" | LC_ALL=C sort -u > "$CATALOG_RUN/closures.reference.canonical.g6"
cmp "$CATALOG_RUN/closures.canonical.g6" "$CATALOG_RUN/closures.reference.canonical.g6"
printf '%s  %s\n' "$GENG_SHA256" "$GENG" "$LABELG_SHA256" "$LABELG" | sha256sum -c -
```

A capacity error or `CERRADURA_TRUNCADA` is a failed computation; the executable exits nonzero and the pipeline must stop. The expected union has 2,271 non-strong classes. Strong boundary states are reported but not expanded. For the three contractible seeds, the standard-library command `python3 -P "$REPO/finite/data/check_small_closures.py"` reconstructs their closures with its own exact isomorphism backtracking, compares every stored state and checks the eight K4-free classes. This read-only command is already required by the quick route. Adding `--write` regenerates the certificate JSON; use it only in a disposable copy because the finite byte manifest would then need refreshing.

## Small K4-free reduction check, formatting and retained records

`data/local_K4/connected_n2_7.g6` is the 643-graph finite input for the small-piece step. The quick route checks its local criterion and pairwise nonisomorphism without `geng`. To regenerate only that bounded universe in a separate directory, use:

```bash
python3 -P "$REPO/tools/generate_local_K4_catalogue.py" \
  --geng "$GENG" --output-dir "$REPO/build/local_K4"
python3 -P "$REPO/tools/check_local_K4_catalogue.py" \
  --data-dir "$REPO/build/local_K4"
```

The generator's identity and stream hashes are recorded. The stored 643 objects alone do not prove the generator's exhaustiveness. No graph above order seven is generated by this command.

`python3 -P "$REPO/tools/generate_cardinalities.py" --csv "$REPO/data/cardinalities.csv" --output /absolute/path/to/cardinalities.tex` formats the two LaTeX panels. Add `--check` to compare existing output. This performs no enumeration.

Complete historical per-residue archives are not included in this compact selection. `data/census/` supplies selected aggregates, all residuals and their adjudications, and the finite positive set; `finite/provenance/` supplies selected lower-order comparisons. [The assertion-to-evidence map](verification-scope.md) states the status of each use. A full independent recount with another classification core remains deferred.
