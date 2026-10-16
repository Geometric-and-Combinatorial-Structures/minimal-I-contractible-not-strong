# Cambios de la versión 4 del manuscrito (16-oct-2026)

*Small non-strong I-contractible graphs and odd torsion in flag complexes* (J. F. Espinoza, M. E. Frías-Armenta,
R. G. Hernández-Amador, H. A. Hernández-Hernández).

Base: ZIP de la versión 3, `manuscrito_v3_overleaf.zip` (SHA-256 `bd0ea276f10e02a92a85bc5dc4fbc7a3f1efbdf54a71c7860398a7a7bb00d6ce`).
Cambian 14 archivos (13 de texto y `figures/fig07.pdf`) y se añaden 2 (`tables/strictly2dis12.tex` y este archivo); el detalle de las fuentes está en `DIFF_v4_vs_v3.patch`.
`main.bbl`, `refs.bib`, `appendix_data/` y las figuras distintas de `fig07.pdf` no cambian.

Compilación: tectonic 0.17 (motor XeTeX), 33 páginas. **La compilación con pdfLaTeX (la de Overleaf) no se evaluó**: la
instalación TeX del entorno local no tiene formato `pdflatex.fmt` ni paquetes LaTeX.

## A. Hallazgos de la ronda 2 de la auditoría externa

| hallazgo | lugar (v3) | cambio en v4 |
|---|---|---|
| H-26 (R2-MATH-01) | `sections/D_cluster.tex:25` | La igualdad con OEIS A001349 se presenta como control de consistencia. Se enuncian las premisas que el registro no certifica: partición por residuos, flujo de cada rebanada sin repeticiones y contenido en su clase, contadores íntegros, un solo resultado por residuo. También el argumento: 0 ≤ n_r ≤ N_r y Σ n_r = Σ N_r implican n_r = N_r. Sin esas premisas, omisiones y duplicaciones podrían compensarse. La recomputación prevista las comprueba rebanada por rebanada. |
| H-26 | `sections/05_table.tex:3` | Antes: "enumerates all … connected graphs". Ahora: la fila se calculó en 200 000 rebanadas y sus contadores suman el valor de A001349, como control de consistencia con remisión al Apéndice D. Las filas 12 y 13 quedan "reported as computed", con la reserva de integridad de las corridas. |
| H-26 | `sections/05_table.tex:17` (Obs. 5.1(ii)) | La cota "un grafo de 𝔍_VS que no es 2-desmantelable tiene al menos 14 vértices" queda condicionada a que las filas 12 y 13 estén completas. Se explica que las columnas 𝔍_VS y k-Dis no dependen del memo y que la cota depende sólo de la integridad de las corridas. |
| H-26 | `sections/07_consequences.tex:67` | Lo mismo en la Pregunta 7.7: "at most 24; if the reported rows of orders 12 and 13 are complete, it is at least 14". |
| H-26 (ítem 3) | `sections/01_intro.tex:29` (E) | "complete rows" → "rows … with every column filled". Son "reported as computed", con la reserva de integridad y las recomputaciones previstas. |
| H-27 (R2-MATH-02) | `make_tables.py` | Versión corregida (sin la fila 13 provisional duplicada). Ahora también genera `tables/strictly2dis12.tex` desde `data/strictly_2dis_12.tsv` y escribe `^` como `\textasciicircum{}` (sección D.1). Las tres tablas se regeneran desde los datos del repositorio. Respecto a v3: Tabla 2 idéntica byte a byte; la Tabla 4 cambia sólo en sus 9 filas con `^`; la Tabla 5 coincide con la del repositorio salvo el escape de `^`. |
| H-28 (R2-MATH-03) | `sections/05_table.tex:5-10`, `main.tex` | La Tabla 2 pasa a una página apaisada (`pdflscape`, sin `sidewaystable`), dentro de `adjustbox` (sólo reduce). Causa medida: dentro de `sidewaystable`, `\textwidth` = `\textheight` = 650.43 pt y el bloque girado quedaba desplazado unos 150 pt hacia el borde. La tabla se coloca al final de §5. Resultado: la leyenda completa visible en la página 12 (`/Rotate 90`), 0 palabras fuera de su página en las 33 páginas, y desaparece el aviso "Annotation out of page boundary". |

## B. Precisiones de la revisión del manuscrito (ronda 2, `results/manuscript_review.md`)

1. **Ítem 6, script p011.**
   - `01_intro.tex:35`: "the script actually used has been recovered and verified" → identificación por corroboración forense a partir de registros del sistema de archivos y bitácoras, no copia autenticada del script enviado.
   - `D_cluster.tex:27-32`: la misma formulación.
2. **§4.6 y §8.**
   - `04_algorithms.tex:105` y `08_data.tex:5`: "31 checks" y "row 11 … not repeated" se sustituyen por el estado actual. `verify.sh` pasa sus 39 comprobaciones; el script no cambia desde el 13-oct (7b00ebd) y el registro de la ronda 1 (`AUDIT_OUT/logs/verify.stdout`) da `passed=39 failed=0`.
   - Se añade el resultado de la auditoría externa de 4a059b5: filas 3–9 gráfica por gráfica con código independiente, fila 10 completa con el C archivado, y fila 11 completa (1 006 700 565 gráficas) con la variante de memo de estado completo. Todas coinciden. Las filas 12 y 13 no se reenumeraron.
3. **Figura 9** (`figures/fig07.pdf`, la del mosaico).
   - La leyenda dentro de la figura se regeneró con `figures/make_figures.py --only fig07`.
   - "exhaustive" → "all such graphs under H14".
   - "(identification cycle a)" → descripción por casos, verificada para las 51 gráficas:
     - discos: el ciclo *a* (5- y 6-ciclo en G14a/G14c; 4-ciclo y espolón en G14b; 4/5/6-ciclo en 25/18/2 de torsión);
     - anillos *: un 4-ciclo y una arista disjunta en 4 triángulos;
     - anillo y disco **: dos 4-ciclos disjuntos.
   - Mismo tamaño de página que en v3 (499.812 × 724.26 pt), sin solapes y con los mismos 2 textos fuera del recuadro que ya tenía v3.
   - El pie de figura (`06_examples.tex:127`) lleva la misma información y la reserva H14.
4. **Avisos de hyperref**: 39 → 0, con `\texorpdfstring` en 7 títulos (`04_algorithms` ×2, `06_examples` ×2, `07_consequences` ×2, `B_tables`).
5. **Cita de Fieux–Jouve [Proposition 8]: verificada, sin cambio.**
   - En el PDF de arXiv v2 (depósito HAL, SHA-256 `163090f7…`, p. 5) es "Proposition 8: ∀n ≥ 2, Q_n ∈ D_{n−1} ∖ D_{n−2}", y Q_n tiene 2n + 2ⁿ vértices, es decir, 24 para n = 4.
   - La introducción editorial en ScienceDirect también la cita como Proposition 8.
   - La "Proposición 9" de la ronda 2 proviene del HTML de arXiv, que numera de otra manera.

## C. Propuestas aprobadas por el autor

- **P1.** El Apéndice B pasa a llamarse "Graph lists", con dos subsecciones:
  - **B.1**: las 51 gráficas (Tabla 4).
  - **B.2**: las 20 gráficas de orden 12 en 2-Dis ∖ 1-Dis (Tabla 5), con la reserva H12 y la del Apéndice D.

  La Tabla 5 se verificó de forma independiente:
  - las 20 filas coinciden con el TSV y con la tabla;
  - invariantes recalculados con networkx y |Aut| por enumeración de automorfismos;
  - las 20 son distintas y no isomorfas entre sí;
  - el clasificador v2.1 en modo `2dis_no_1dis` devuelve las 20, y `tools/kdismantlable.py` da k mínimo = 2 para las 20.

  Corrida de extracción (`yuca/logs/n12_2dis_no_1dis_resumen.txt`): total 164 059 830 476 (igual a la fila 12), 4000/4000 rebanadas, 0 faltantes, 20 encontradas.
- **P4.** La Obs. 5.1(ii) ya no contiene rutas `\path`: remite a la Tabla 5 y a §8.

## D. Errores adicionales encontrados en esta revisión (no señalados en la ronda 2)

1. **Cadenas graph6 con `^`.**
   - El generador escribía `\^{}` (acento circunflejo), que se copia del PDF como U+02C6: una cadena copiada de la tabla no era la gráfica.
   - En v3, ninguna de las 9 cadenas con `^` de la Tabla 4 se copiaba bien. La tabla de las 20 del repositorio tenía el mismo defecto en sus 20 filas.
   - En v4, 51/51 y 20/20 cadenas se extraen literalmente de las páginas de las tablas. No hay ningún U+02C6 ni U+02DC en el texto del PDF.
2. **Opciones de línea de órdenes en `\texttt`.** `--` se fundía en un solo carácter y se copiaba "-trace", "-full-table", "-modo". Se corrigió en 4 lugares con `-{}-` (`06_examples`, `C_certificates`, `08_data`, `D_cluster`).
3. **§8 y Apéndice D desactualizados respecto del repositorio.**
   - Decían que `yuca/as_run/tarea_n14_p011.sh` es el script equivocado y que "was not altered". Era cierto en 4a059b5, pero no desde 892e41b.
   - Desde entonces ese nombre contiene el script identificado (`b95a125b…`), y el equivocado (`50477550…`) se conserva sin cambios como `tarea_n14_p029_intento_fallido_2079068.sh`.
   - El texto ahora cita los dos commits.
4. **§8 citaba un "audit supplement"** con las comprobaciones de Wolfram que no está en el repositorio. Ahora remite a `verification/indep.py`, `verification/wolfram_codigo_y_salidas.json` y `paper/NUMERIC_CHECK.md`, que sí existen.
5. **Apéndice D**: tras "not the recovery of an authenticated copy" seguía "the recovered file". Ahora dice "this file".

## E. Comprobaciones del PDF v4

- **Compilación**: 33 páginas; 0 referencias o citas indefinidas; 0 cajas sobrellenas; 0 avisos de hyperref; 0 "Annotation out of page"; 0 palabras fuera de su página (la página 12, girada, se evaluó en su propio marco).
- **Avisos restantes**: cajas `underfull` (cosméticas) y bytes UTF-8 de `algorithm2e.sty`.
- **Revisión visual de las 33 páginas**: sin recortes ni solapes. La Tabla 5 queda dentro del Apéndice B gracias a `\FloatBarrier`.
- **`verification/check_table_B1_fig07.py`**: PASS sobre la Tabla 4 y la Fig. 9 nuevas, y también sobre la Tabla 4 de v3. El script acepta ahora `\textasciicircum{}`.
- **Texto**: los pasajes modificados se releyeron sobre el texto extraído del PDF, sin "??".

## F. NO EVALUADO

- Compilación con pdfLaTeX (Overleaf) y su aspecto visual, en particular las páginas 12 (Tabla 2), 20 (Fig. 9) y 25–27 (Tablas 4 y 5).
- Las figuras distintas de la Fig. 9 no se regeneraron. `figures/make_figures.py` necesita cuatro archivos de entrada que no están en el repositorio. La Fig. 9 se regeneró con `atascadas14_final.txt` de Dropbox (SHA-256 `2634c0a1…`, las mismas 51 cadenas que `data/stuck_14_K4free.g6`).
- No hay nuevas enumeraciones: las filas 12 y 13 siguen como se registraron.

## G. Cambios correspondientes en el repositorio (rama `v2.1`)

- `figures/make_figures.py`: nueva leyenda de la Fig. 7/9, opción `--only` y título actual.
- `figures/fig07.{pdf,png,svg}` regenerados.
- `figures/captions.md`: reservas H12/Hcasi/H13/H14 y título actual.
- `figures/make_deck.py` (nuevo) y `figures/deck_all_figures.pdf` regenerado: 11 páginas, reproducible.
- `paper/make_tables.py` y `paper/tables/{stuck51,strictly2dis12}.tex`.
- `verification/check_table_B1_fig07.py`.
- `paper/REVISION_LOG_round1-2.md`: se eliminó una nota de proceso interna.

## H. Decisiones del autor pendientes

1. Cómo identificar la auditoría externa en el artículo. Ahora dice "an external audit", sin nombrar al auditor.
2. `LICENSE` (MIT) nombra a 3 titulares, mientras que el manuscrito y `CITATION.cff` tienen 4 autores.
3. La historia de `main` contiene esa nota de proceso interna, eliminada en `v2.1`. Antes de hacer público el repositorio, conviene publicar sólo el árbol (archivo con DOI) o reescribir esa historia.
