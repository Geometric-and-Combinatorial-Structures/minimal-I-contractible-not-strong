# Manuscript sources

Version 3 (16 Oct 2026) of *Small non-strong I-contractible graphs and odd torsion in flag complexes* (J. F. Espinoza, M. E. Frías-Armenta, R. G. Hernández-Amador, H. A. Hernández-Hernández). Apart from `make_tables.py` (see below), these files are byte-identical to the Overleaf project `manuscrito_v3_overleaf.zip` (SHA-256 `bd0ea276…`). `main.pdf` is the reference build (Tectonic/XeTeX, 32 pp.).

`main.tex` (elsarticle, preprint) with `sections/`, `tables/` (generated from `../data/` by `make_tables.py`, run from `paper/`), `figures/` (PDF; sources in `../figures/`), `appendix_data/` (`traces.txt`; `tarea_n14_p011_correct.sh`, the task script run by the p011 front of the n = 14 search, identical to `../yuca/as_run/tarea_n14_p011.sh`), `refs.bib` and `elsarticle-num.bst`. Compile with `./build.sh` or `tectonic main.tex`; on Overleaf use pdfLaTeX (`COMPILAR_EN_OVERLEAF.md`). `CAMBIOS_v3.md` lists the changes from the authors' Overleaf version and four proposals that were not applied (P1–P4).

`make_tables.py` reproduces `tables/table_cardinalities.tex` and `tables/stuck51.tex` byte for byte. The copy in the Overleaf ZIP still wrote a fixed "computation in progress" line for n = 13, which duplicated the complete row 13 read from `../data/table_cardinalities.csv`. That line was removed here, and the script no longer writes a final newline after the table, as in the sources. The manuscript is unaffected, because the table in the ZIP is the correct one.

`tables/strictly2dis12.tex` is the table of the 20 graphs on 12 vertices that are 2-dismantlable but not 1-dismantlable (appendix of v2.1). It is not included in v3 (proposal P1, pending).

Versions: v1 (2026-10-13, 38 pp.) → internal adversarial review (`REVISION_LOG_round1-2.md`, `NUMERIC_CHECK.md`: 2 rounds, 45 findings, 42 numerical checks; both files refer to the v1/v2 text) → v2 (2026-10-13, 41 pp.) → v3 (2026-10-16, 32 pp.; the authors' Overleaf version with the corrections listed in `CAMBIOS_v3.md`).
