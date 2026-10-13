# Revisión narrativa de la secuencia de figuras (paper-narrative)

Fecha: 2026-10-13. Herramienta: skill `paper-narrative` (`derive_paper_brief` + `narrative_review_task`, revisor "handling editor" sobre las nueve figuras principales como imágenes; modelo de razonamiento del host). Abstract evaluado: el del encargo (Teoremas A–D, refutación de las Conjeturas 14 y 15 de DEFH23). Las salidas estructuradas completas están en `narrative_review_round1.json` y `narrative_review_round2.json`; aquí se resume lo que importa y se documenta la decisión tomada.

## Brief derivado (resumen)
- **Pitch:** la contractibilidad de un complejo flag no implica que se pueda desmontar vértice a vértice / arista a arista (𝔍_S): los contraejemplos mínimos viven en 14 vértices, y la obstrucción mínima a "Z₂-acíclico ⇒ 𝔍_S" es un complejo flag de 13 vértices que es el espacio de Moore M(ℤ/3,1).
- **Activo más llamativo:** el disco cuyo borde da tres vueltas al 4-ciclo (G₁₃).

## Ronda 1 — veredicto: `weak`
Hallazgos del revisor y decisión:

| # | Hallazgo | Decisión |
|---|---|---|
| 1 | Fig. 1 mezclaba gancho + mecanismo + objeto; el dibujo de la gráfica (40 aristas) iba primero y enterraba la idea "borde que da 3 vueltas = ℤ/3". | **Aceptado.** Fig. 1 reordenada: (a) disco desplegado con el borde (10 9 11 8)³, (b) esquema del espacio de Moore, (c) la gráfica G₁₃ (degradada a "el objeto, para el registro"). |
| 2 | Falta el "tejido conectivo" entre el Teorema A (torsión, a³) y el Teorema B (contráctil, a·a·a⁻¹). | **Aceptado.** Nuevo panel (c) en la Fig. 2: los dos patrones de identificación lado a lado (a·a·a → H₁ = ℤ/3: G₁₃ y 45 de las 48 atascadas de torsión; a·a·a⁻¹ → contráctil: Dunce Hat y G14a/b/c). |
| 3 | Mover la Fig. 2 (no hay Dunce Hat flag de 13) al suplemento. | **Rechazado.** Es la Proposición de §6.1 y, con el panel (c) nuevo, es la bisagra A→B. Se mantiene en §6.1. |
| 4 | Fusionar la Fig. 9 (flujo de cómputo) como inset de la Fig. 7. | **Rechazado.** El artículo tiene una sección de métodos (§4) donde la Fig. 9 es la figura de referencia del Algoritmo 7; el mosaico de la Fig. 7 ya está al límite de densidad. |
| 5 | Mover la Fig. 8 (lema de 2-conexidad) al suplemento. | **Rechazado.** Es la figura del Lema 3.2 (Teorema C) en §3; en una revista de matemáticas la justificación del generador `-C -d4 -D(n−2)` es parte del cuerpo. |
| 6 | Comprimir la Fig. 6 (19 paneles) a antes/después + tira de conteo de vértices. | **Rechazado** (restricción del equipo: el certificado debe ser verificable a mano por los árbitros). En su lugar se añadió un encabezado de una línea (ver ronda 2). |
| 7 | Nueva figura "conjetura vs. contraejemplo". | **Pospuesto:** se cubre con la Tabla 2 y el enunciado de los Teoremas B y D; no se añade figura. |

## Ronda 2 — veredicto: `yes` (would_send_for_review)
Con las restricciones del manuscrito explícitas (Fig. 1 en la introducción; Fig. 8 en §3; Fig. 9 en §4; Fig. 2 en §6.1; Figs. 3–5 y 7 en §6.2; Fig. 6 en §7), el revisor enviaría el deck a arbitraje. Arco devuelto: **gancho** Fig. 1 → **mecanismo** Figs. 8, 9, 2 → **evidencia** Figs. 3, 4, 5, 7 → **aplicación** Fig. 6. `kill_list` vacía. Peticiones menores y decisión:

| # | Petición | Decisión |
|---|---|---|
| a | Tira comparativa del trío (longitud del ciclo 5 / 4+espolón / 6; aristas 44/45/45) al frente de la Fig. 3. | **Aceptado en forma ligera:** se añadió a los tres recuadros verdes de la Fig. 7 la etiqueta "G14x: a = k-cycle", y el panel (c) de la Fig. 2 ya nombra al trío; no se añade panel a la Fig. 3 (habría duplicado los paneles (a) de las Figs. 3–5). |
| b | En la Fig. 7, marcar qué atascadas de torsión "provienen de G₁₃ por pegados I₄". | **Rechazado por incorrecto:** las 51 atascadas de 14 vértices no son cerraduras de nada (una cerradura I₄ añade aristas en 1 triángulo y deja de ser atascada); todas provienen de la búsqueda exhaustiva en 14. La relación con G₁₃ es de patrón (a³), ya indicada en la Fig. 2c. |
| c | Encabezado en la Fig. 6 que diga explícitamente que la homología no cambia y sólo cambia la 𝔍_S-contractibilidad. | **Aceptado:** línea añadida en Figs. 6, 6b y 6c. |

## Orden final de las figuras
fig01 (introducción, gancho) · fig08 (§3) · fig09 (§4) · fig02 (§6.1) · fig03–fig05, fig07 (§6.2) · fig06 (§7, Teorema D) · fig06b, fig06c (apéndice C). La numeración de archivos fig01–fig09 se conserva como la pidió el equipo; el manuscrito las citará en el orden anterior, por lo que al componer el LaTeX conviene renumerar: Fig. 1 = fig01, Fig. 2 = fig08, Fig. 3 = fig09, Fig. 4 = fig02, Figs. 5–7 = fig03–fig05, Fig. 8 = fig07, Fig. 9 = fig06.

## Verificación de las figuras
- Cada figura pasó el chequeo geométrico §9.1 de `figure-style` (0 solapes de texto; `verify_log.txt`). Los "textos fuera de la caja" que reporta el log para fig01 y fig07 son textos bajo los ejes que `bbox_inches='tight'` incluye en el archivo guardado (verificado visualmente en los PNG).
- Inspección perceptual de todos los PNG a 300 dpi (sin aristas que atraviesen vértices: la disposición de vértices se eligió maximizando la holgura arista–vértice; colores: rojo = ciclo de identificación / elemento borrado, ámbar = vecindad, azul = arista I₄ pegada, púrpura = cliques falsas; sin pares rojo/verde opuestos).
- Las palabras de frontera dibujadas se recalcularon con una reimplementación del despliegue (`discos.py`) y coinciden con las registradas en `estructura.md` y `atascadas14_final.txt` (G13a, G14a, G14b, G14c, Dunce Hat); las 18/19/18 etapas de los certificados se re-ejecutaron sobre la gráfica al dibujarlas (asserts en `make_figures.py`).
- Dos datos corregidos respecto del encargo: (i) el g6 del Dunce Hat se generó en orden de inserción, así que la etiqueta i de g6 corresponde a la etiqueta (1,4,13,12,11,3,14,15,10,5,2,6,7,8,9)[i] de la Fig. 2A, y con ese mapeo el ciclo de identificación es 1–2–3–4–1 como dice el encargo; (ii) la gráfica del intercambio 10↔11 con las etiquetas que dan las cliques falsas 1–4–11 y 2–5–10 es `L?qa``{wtlzM~o`, isomorfa a `LtDzQNKmpKXT`V` (misma forma canónica `labelg`).
