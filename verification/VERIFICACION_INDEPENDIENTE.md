# Verificación independiente de homología entera y certificados (Fase 1, 2026-10-13)

Todas las comprobaciones de este documento se hicieron con **`indep.py`**, un módulo escrito desde cero para esta verificación (parser graph6 propio, cliques por extensión recursiva, matrices frontera enteras, forma normal de Smith por eliminación entera exacta sobre `int` de Python, homología Z₂ por rango sobre GF(2) con máscaras de bits, criterios cono/0-desmantelable, y un decisor exacto de 𝔍_S por backtracking con memo y poda "𝔍_S ⇒ Z₂-acíclica"). No reutiliza ninguna función de `atascadas.c` ni del `homZ` del proyecto. Segunda vía para la SNF: `sympy.matrices.normalforms.smith_normal_form`; tercera vía (gráficas clave): Wolfram Language (`SmithDecomposition`) vía el conector MCP.

**Resultado global: ninguna discrepancia con los resultados previos del proyecto.** La única observación que corrige el plan de trabajo es la cota de 2-conexidad del Lema 2 (§3: n ≤ 22, no 21), y un matiz estructural sobre las 48 atascadas de torsión (§4).

Entorno: conda `grafos` (python 3.11, networkx, numpy, sympy, nauty 2.8 `geng`/`labelg`, gcc). Compilación: `gcc -O3 -march=native -std=c11 -o atascadas atascadas.c` (sin avisos).

## 1. Homología entera H_*(Δ(G); ℤ) (archivo `homologia_Z_independiente.csv`)

Controles de la SNF propia: `[[2,4,4],[-6,6,12],[10,-4,-16]] → [2,6,12]`; 200 matrices enteras aleatorias (hasta 6×6, entradas en [−5,5]) coinciden con sympy; C₅ → H₁=ℤ; K₄ → trivial; Petersen → H₁=ℤ⁶.

| grupo | nº gráficas | H_*(ℤ) obtenida (SNF propia) | coincide con sympy | coincide con resultado previo |
|---|---|---|---|---|
| 4 etiquetadas = 3 clases de isomorfismo (labelg) de `cand13_cerradura.txt` | 4 | H0=Z H1=Z/3 H2=0: 4 | 4/4 | sí (4/4) |
| 51 atascadas (`atascadas14_lista.g6`) | 51 | H0=Z H1=Z/3 H2=0: 48; H0=Z H1=0 H2=0: 3 | 51/51 | sí (51/51) |
| 29 de `I_no_IS_14.txt` | 29 | H0=Z H1=0 H2=0: 8; H0=Z H1=0 H2=0 H3=0: 21 | 29/29 | sí (29/29) |
| muestra aleatoria de 30 de las 2242 de torsión de `noIS14_todas.txt` (semilla 20261013) | 30 | H0=Z H1=Z/3 H2=0 H3=0: 26; H0=Z H1=Z/3 H2=0: 4 | 30/30 | sí (30/30) |
| Dunce Hat Fig. 2A y Fig. 2B (`dunce.g6`) | 2 | H0=Z H1=0 H2=0: 1; H0=Z H1=0 H2=0 H3=0: 1 | 2/2 | sí (2/2) |

Detalle de la coincidencia con lo previo: las 3 clases de 13 tienen H₁=ℤ/3 (previo: ℤ/3); de las 51 atascadas, las 3 marcadas "I-contraíble SÍ" (G14a/b/c) tienen homología trivial y las 48 marcadas ℤ/3 tienen H₁=ℤ/3; las 29 contráctiles tienen homología trivial (8 sin K₄; 21 con K₄ y H₃=0); las 30 de la muestra de torsión tienen H₁=ℤ/3 como indica su columna `H1(Z) torsión [3]`; el Dunce Hat y Dunce Hat+{5,7} son acíclicos sobre ℤ. Las 116 son Z₂-acíclicas.

### Wolfram (WolframLanguageEvaluator; cliques por subconjuntos, matrices frontera construidas en WL, `SmithDecomposition`)

| gráfica | g6 | salida de Wolfram |
|---|---|---|
| G13a | `L?qa``{wttym~o` | `{"n" -> 13, "aristas" -> 40, "triangulos" -> 28, "K4" -> 0, "d1.d2 cero" -> True, "b0" -> 1, "b1" -> 0, "b2" -> 0, "torsion H0" -> {}, "torsion H1" -> {3}, "SNF d2" -> {{1, 27}, {3, 1}}}` |
| G13b | `L?qa`p{wttym~o` | `{"n" -> 13, "aristas" -> 41, "triangulos" -> 29, "K4" -> 0, "d1.d2 cero" -> True, "b0" -> 1, "b1" -> 0, "b2" -> 0, "torsion H0" -> {}, "torsion H1" -> {3}, "SNF d2" -> {{1, 28}, {3, 1}}}` |
| G13c | `L?qahp{wttym~o` | `{"n" -> 13, "aristas" -> 42, "triangulos" -> 30, "K4" -> 0, "d1.d2 cero" -> True, "b0" -> 1, "b1" -> 0, "b2" -> 0, "torsion H0" -> {}, "torsion H1" -> {3}, "SNF d2" -> {{1, 29}, {3, 1}}}` |
| G14a | `M?b@bFHNEk@~|k}U?` | `{"n" -> 14, "aristas" -> 44, "triangulos" -> 31, "K4" -> 0, "d1.d2 cero" -> True, "b0" -> 1, "b1" -> 0, "b2" -> 0, "torsion H0" -> {}, "torsion H1" -> {}, "SNF d2" -> {{1, 31}}}` |
| G14b | `M?B@thku?~Lylk}[?` | `{"n" -> 14, "aristas" -> 45, "triangulos" -> 32, "K4" -> 0, "d1.d2 cero" -> True, "b0" -> 1, "b1" -> 0, "b2" -> 0, "torsion H0" -> {}, "torsion H1" -> {}, "SNF d2" -> {{1, 32}}}` |
| G14c | `M?r@d`ifbiFfo}~o?` | `{"n" -> 14, "aristas" -> 45, "triangulos" -> 32, "K4" -> 0, "d1.d2 cero" -> True, "b0" -> 1, "b1" -> 0, "b2" -> 0, "torsion H0" -> {}, "torsion H1" -> {}, "SNF d2" -> {{1, 32}}}` |
| Dunce | `N|thHsL`sHoI`RPOwLG` | `{"n" -> 15, "aristas" -> 46, "triangulos" -> 32, "K4" -> 0, "d1.d2 cero" -> True, "b0" -> 1, "b1" -> 0, "b2" -> 0, "torsion H0" -> {}, "torsion H1" -> {}, "SNF d2" -> {{1, 32}}}` |

Lectura: `b1`=rango libre de H₁, `torsion H1`={3} ⇒ H₁ = ℤ/3 en las tres de 13; H₁ = 0 en G14a/b/c y el Dunce Hat; `d1.d2 cero` confirma ∂₁∂₂=0. Coincide con la SNF propia, con sympy y con lo previo. El código WL enviado y las salidas íntegras están en `wolfram_codigo_y_salidas.json`.

## 2. Certificados y no-pertenencia a 𝔍_S

### 2.1 Comandos ejecutados (`atascadas` recompilado)

```
./atascadas --modo verificar < cand14.g6   (ídem cand14b.g6, cand14c.g6, cand13.g6, dunce.g6, atascadas14_lista.g6)
./atascadas --modo icert --prof 2 < cand14.g6   (ídem cand14b.g6, cand14c.g6)
./atascadas --modo traza < grafica14_mas01.g6 ; < cand14b_mas03.g6 ; < cand14c_mas.g6 ; < dunce.g6
```

Salidas: G14a/b/c → `0-Dis=0 I_SV=0 I_S=0 (atascada=1)`; icert → `I-CONTRAIBLE: en I_S tras 1 pegado(s) de arista I4: {0,1}` / `{0,3}` / `{2,3}` con gráficas finales `M_b@bFHNEk@~|k}U?`, `MCB@thku?~Lylk}[?`, `M@r@d`ifbiFfo}~o?` (iguales a los archivos `*_mas*.g6`); las 51 de la lista: 51 × `I_S=0 (atascada=1)`, 51 × `chi=1 conexa=1 aciclica=1 betti=1 0 0`; G13a y Dunce Hat: `I_S=0 (atascada=1)`; Dunce Hat+{5,7}: `I_S=1 (atascada=0)` con 9 aristas I_S-contraíbles. Salidas completas en la carpeta `salidas_atascadas/`.

### 2.2 Re-verificación de las trazas con Python independiente

Para cada paso "borrar vértice v / arista uv" se recalculó la vecindad (abierta o común) en la gráfica **actual** (tras los borrados previos), se comparó con la impresa, se comprobó el criterio declarado (K1: |N|=1; cono: `is_cone` y 0-Dis; 0-Dis: eliminación sucesiva de vértices dominados hasta K1), se comprobó que N es Z₂-acíclica y que N ∈ 𝔍_S con el decisor exacto independiente, y al final que queda exactamente K₁.

| traza | gráfica | pasos | vecindades coinciden | criterios válidos | N ∈ 𝔍_S (decisor indep.) | termina en K₁ |
|---|---|---|---|---|---|---|
| traza_G14a_mas01.txt | `M_b@bFHNEk@~|k}U?` | 18 | sí | sí | sí | sí |
| traza_G14b_mas03.txt | `MCB@thku?~Lylk}[?` | 19 | sí | sí | sí | sí |
| traza_G14c_mas23.txt | `M@r@d`ifbiFfo}~o?` | 18 | sí | sí | sí | sí |
| traza_dunce.txt | `N|thHsL`sHoI`RPOwLG` | — | — | — | — | NO es I_S (sin traza; coincide con §2.3) |
| traza_dunce.txt | `N|thHsL`sHoI`VPOwLG` | 16 | sí | sí | sí | sí |

Nota de etiquetado: `dunce.py` construye el Dunce Hat con etiquetas 1..15 de la Fig. 2A y networkx asigna índices g6 por orden de inserción; se reconstruyó esa correspondencia (orden 1,4,13,12,11,3,14,15,10,5,2,6,7,8,9) y se comprobó que la primera línea de `dunce.g6` es exactamente esa gráfica (32 triángulos dados = 32 triángulos del complejo de cliques, sin K₄) y que la segunda es la primera más la arista {5,7} del artículo, que en el g6 es {9,12}.

### 2.3 Atascamiento y decisión exacta de 𝔍_S (Python independiente)

Atascada := Z₂-acíclica, ninguna N(v) Z₂-acíclica, ninguna N(u,v) Z₂-acíclica ni vacía. Como 𝔍_S ⇒ Z₂-acíclica, una gráfica atascada no admite ningún primer borrado 𝔍_S y por tanto no es 𝔍_S (sin depender de la Tabla 1).

- Las 51 de `atascadas14_lista.g6`: **51/51 atascadas** (0 vecindades abiertas acíclicas, 0 comunes acíclicas, 0 aristas sin triángulo; grado mínimo 4, máximo ≤ n−2 en todas). Son 51 clases de isomorfismo distintas (`labelg`) y coinciden una a una con las de `atascadas14_final.txt`.
- Las 3 de 13: `L?qa``{wttym~o` atascada; `L?qa`p{wttym~o` y `L?qahp{wttym~o` no son atascadas (tienen las aristas I_S-contraíbles {4,7} y {4,7},{5,6}, respectivamente, que son las pegadas) pero el decisor exacto da **no 𝔍_S** para las 4 etiquetadas de `cand13_cerradura.txt` (≤ 111 llamadas cada una gracias a la poda Z₂).
- Dunce Hat (Fig. 2A): atascado y no 𝔍_S; Dunce Hat + {5,7}: N(5,7) (= {0,5,7,10,11} en g6) es 𝔍_S, y la gráfica es 𝔍_S (decisor independiente: True, 88 llamadas; traza de 16 pasos verificada).
- G14a/b/c: no 𝔍_S (decisor independiente: False, 46–48 llamadas); G14a+{0,1}, G14b+{0,3}, G14c+{2,3}: la arista añadida es la única diferencia, N(u,v) = {5,8,10,12,13} / {7,9,12,13} / {6,7,10,11,13} es 𝔍_S, y G+e es 𝔍_S (True; 141–146 llamadas; trazas de 18/19/18 pasos verificadas). Por tanto G14a/b/c ∈ 𝔍∖𝔍_S.
- Las 29 de `I_no_IS_14.txt`: el decisor exacto independiente da **no 𝔍_S** en las 29 (≤ 111 llamadas cada una); su homología entera es trivial (§1).
- Las 48 atascadas de torsión y las 30 de la muestra de torsión: H₁ = ℤ/3 ≠ 0 ⇒ no contráctiles ⇒ no 𝔍 ni 𝔍_S.

Validación del decisor independiente contra la Tabla 1 de [DEFH23] / `--modo tabla`: conexas con n=6: 𝔍_S = 68 = acíclicas; n=7: 403 (acíclicas 403, χ=1: 404); n=8: 3798 (0-Dis 3791). Coincide en los tres casos con `atascadas --modo tabla` y con la tabla del artículo.

## 3. Lema de piezas casi-atascadas, n = 10 y 11 (archivo `casi_atascadas_10_11.txt`)

`geng -c 10 -q | ./atascadas --modo casi` (5 s) y `geng -c 11 -q r/8 | ./atascadas --modo casi`, r=0..7 en paralelo (2 min 53 s): **0 piezas** en 11,716,571 y 1,006,700,565 gráficas conexas (totales = OEIS A001349). Además `--modo atascadas` sobre los mismos barridos: 0 atascadas con 10 y 11 vértices. Con `casi_3_9.txt` (0 piezas para 3 ≤ n ≤ 9): no hay piezas casi-atascadas con ≤ 11 vértices.

**Consecuencia.** Si una atascada G con n vértices tuviera vértice de corte u, G = A ∪_u B con |A| + |B| = n + 1 y ambas piezas casi-atascadas (o atascadas) con ≥ 12 vértices; luego n ≥ 23. Toda atascada con **n ≤ 22** es 2-conexa (antes n ≤ 18). ⚠ La cota "2·11 − 1 = 21" indicada en el plan es correcta pero no es la que da el argumento (2·12 − 2 = 22; con piezas ≤ 9 el mismo cálculo da 18, que es la cota del README). Recomiendo usar 22 en el manuscrito o, si se prefiere ser conservador, 21, pero no mezclar ambas.

## 4. Datos estructurales (archivos `estructura.csv`, `estructura.md`)

Reimplementación del despliegue en disco (corte en aristas con ≠ 2 triángulos, pegado de esquinas, recorrido del borde) y de la palabra de frontera. Coincidencias con `atascadas14_final.txt`: vértices del disco 24/25/26 y lados del borde 15/16/18 para G14a/b/c; las palabras coinciden salvo rotación cíclica e inversión de sentido (p. ej. G14a: `10 5 12 5 10 13 9 12 9 13 10 5 12 9 13` previa = inversa de la obtenida). |Aut| coincide (1, 2, 2; G13a: 8; Dunce Hat: 2). G13a: borde = a³ sobre el 4-ciclo 8–10–9–11 (rotación 3), como en el README. Matiz adicional: de las 48 atascadas de torsión, 45 son discos con patrón a³ (sobre 4- o 5-ciclos), 2 se despliegan en un **anillo** y 1 en un complejo **desconexo** (dos 4-ciclos disjuntos de aristas en 3 triángulos): ver §4 de `estructura.md`.

## 5. Resumen de discrepancias

- Homología entera: **ninguna** (116 gráficas, 3 métodos).
- Certificados/trazas/𝔍_S: **ninguna**.
- Atascamiento de las 51 + 3 + Dunce Hat: **ninguna**.
- Lema de 2-conexidad: resultado esperado (0 piezas) confirmado; sólo se corrige la cota del plan (22 en vez de 21).
- Despliegue en disco: coincide con lo previo en las gráficas clave; la descripción "las 48 de torsión son discos con borde a³" debe matizarse a 45 discos + 2 anillos + 1 desconexo.
