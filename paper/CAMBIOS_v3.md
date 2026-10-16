# Manuscrito v3 (16-oct-2026): cambios respecto al ZIP de Overleaf

**Base.** `_Articulo__Conjetura_Dunce_Hat (1).zip` (SHA-256 `d5f0d346ec97270a299fd7e342042d463ee4c0a6c5d56a25ed19313805326056`), confirmado por el autor como la última versión (con Rosalía G. Hernández-Amador como coautora). La copia de Dropbox y la adjunta en la conversación son idénticas byte a byte.

**Criterio.** Corregir lo que es falso, obsoleto o internamente incoherente y conservar el enfoque prudente del texto base. Las restauraciones de contenido se proponen al final y **no** se aplicaron. El diff completo está en `DIFF_v3_vs_ZIP_original.patch`.

## Cambios aplicados

| # | Archivo | Cambio | Motivo / evidencia |
|---|---|---|---|
| 1 | `sections/01_intro.tex` | Enunciados **textuales** de las Conjeturas 14 y 15 (versión editorial) y nota al pie sobre el preprint | PDF editorial *Discrete Math.* 346 (2023) 113516, pp. 8–9 ("trivial ℤ₂-homology"); reformuladas en p. 13, la 14 sin su segunda oración. El preprint arXiv:2109.06729v2 (26-jun-2022) dice "trivial homology" con la convención H_n(G) := H_n(G;ℤ); con esa lectura la conjetura también es falsa y el mínimo es 14, no 13. Atiende el hallazgo H-07 (remedio: citar por versión y separar los mínimos ℤ₂ = 13 y ℤ = 14). |
| 2 | `refs.bib` | Referencia nueva `DEFH2022arXiv` | Necesaria para la nota del punto 1. |
| 3 | `sections/01_intro.tex` (E) | "Filas 12 y 13 completas" y calificación de sus entradas I_S | El texto decía que la fila 13 seguía "computation in progress", pero la Tabla 2 ya la contiene. |
| 4 | `main.tex` (resumen) | "cardinalities through order 13" | Antes decía 12, también incoherente con la tabla. |
| 5 | `01_intro.tex`, `08_data.tex` | Commit `83d5ffe` → `4a059b5` | `83d5ffe` es "manuscript draft v1" (13-oct). No contiene la fila 13 (c74ce1d), la segunda corrida n = 12 (8dcd5bf), las 20 gráficas 2-Dis∖1-Dis (7b00ebd), la verificación independiente con Wolfram (019cde7) ni las herramientas de auditoría. `4a059b5` es el commit examinado por la auditoría externa y contiene todo lo que el texto describe. |
| 6 | `01_intro.tex` | El script p011 "ha sido recuperado y verificado" | Prueba Y-F01 de la auditoría (16-oct): fechas de nacimiento, modificación y cambio del archivo = segundo del envío del array 2079156; los logs imprimen los `r0` descendentes. |
| 7 | `sections/05_table.tex` | Fila 12: dos corridas, la segunda con todas las columnas. Fila 13: enumeración completa (A001349) que confirma el Teorema A por otra vía. Pie de tabla: "rows 12 and 13 are new" | El texto decía que la corrida n = 12 dejó sin calcular 3-, 2-, 1- y (−1)-Dis, pero la tabla muestra esas celdas, que provienen de la segunda corrida (array 2084878). |
| 8 | `05_table.tex`, Observación 5.1 | (i) ℤ₂- y ℤ-aciclicidad coinciden para n ≤ 12 bajo H12. (ii) 𝔍_VS = 2-Dis = 3-Dis para n ≤ 13, de donde el mínimo de 𝔍_VS∖2-Dis es ≥ 14 (antes ≥ 13, condicionado a un conteo no publicado de 2025). 2-Dis − 1-Dis = 20 (n = 12) y 35,757 (n = 13), con la lista de las 20 en el repositorio; estas columnas no dependen del memo con hash. (iii) 𝔍_S − 𝔍_VS = 14,948,703 en n = 13. (iv) Brecha de χ = 1 en n = 13 = 4,240,933,193,936 y control (−1)-Dis = A000088 | Todas las cifras se verificaron por programa contra `data/table_cardinalities.csv` y contra OEIS A001349 y A000088. |
| 9 | `sections/07_consequences.tex` | Cota inferior de la pregunta 𝔍_VS∖2-Dis: 14 | Se elimina "column alignment of the 2025 table remains to be checked visually": ahora la cota sale de nuestra propia tabla. |
| 10 | `sections/D_cluster.tex` | Contabilidad de las corridas de tabla (n = 12: 2084878; n = 13: 2084597/2084636, 200,000 rebanadas, 483 duplicadas; la suma de conexas es A001349, así que no falta ni está truncada ninguna rebanada). Evidencia forense del script p011. El trabajo pendiente se describe como las dos recomputaciones previstas | Registros de `yuca/README.md` y `yuca/logs/`; prueba Y-F01. |
| 11 | `build.sh`, `COMPILAR_EN_OVERLEAF.md` | `build.sh` produce `main.pdf` (antes `-jobname=main_v2`); descripción de la v3 | Coherencia con las instrucciones. |

**No se tocaron:** enunciados de teoremas, pruebas, las hipótesis H12/Hcasi/H13/H14, figuras, Tabla 2 (salvo su pie) ni los Apéndices A–C.

## Verificación de compilación

- Compilado con Tectonic 0.17.0 (motor XeTeX): 32 páginas, igual que el PDF original; 0 referencias o citas indefinidas; 0 cajas sobrellenas; BibTeX sin avisos. El aviso "Annotation out of page boundary" también aparece al compilar el ZIP original.
- Overleaf usa pdfLaTeX, así que los cortes de línea pueden variar ligeramente. `main_v3_referencia.pdf` sirve sólo como referencia.
- Instrucciones: **New Project → Upload Project →** `manuscrito_v3_overleaf.zip`; compilador pdfLaTeX; documento principal `main.tex`.

## Propuestas para decidir (no aplicadas)

1. **P1.** Restaurar la tabla de las 20 gráficas 2-dismantelables no 1-dismantelables de 12 vértices, con sus propiedades. Estaba en la v2.1 del repositorio (apéndice `strict2dis`). Es un resultado nuevo, exacto (no depende del memo) y verificado de forma independiente con `tools/kdismantlable.py`.
2. **P2.** Al terminar las recomputaciones exactas de n = 12 y n = 13 y la búsqueda v2 de n = 14: convertir H12/H13/H14 en hechos verificados (o retirarlos), actualizar el Apéndice D y citar un tag o release final del repositorio en lugar de un commit.
3. **P3.** Fila 14 (K₄-libre): incluirla sólo si la corrida exacta (opción a) termina antes del envío; si no, enviar el artículo sin esa fila y agregarla en la revisión.
4. **P4.** Evitar cortes dentro de rutas largas (`\path`) en la Observación 5.1(ii).

## Pendientes fuera del manuscrito

- Repositorio (rama `v2-auditoria`): renombrar `yuca/as_run/tarea_n14_p011.sh`, que es el script del intento fallido 2079068, y añadir el script p011 real (SHA-256 `b95a125b…`).
- `yuca/README.md` dice "identical outputs" para los 692 duplicados de la búsqueda n = 14; esa afirmación no está respaldada y debe retirarse, como ya hace el Apéndice D.
