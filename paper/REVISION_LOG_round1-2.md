# REVISION_LOG — Revisión crítica iterativa (árbitro adversarial, "referee 2")

Manuscrito: *The smallest I-contractible graphs that are not strong I-contractible, and odd torsion in flag complexes on thirteen vertices* (Espinoza, Frías-Armenta, Hernández), snapshot `repo_snapshot_v1.tar.gz`, PDF `manuscript_v1.pdf` (38 pp.).
Entorno de verificación: conda `grafos` (python3 + networkx, gcc, nauty `geng`/`labelg`), `src/atascadas.c` compilado localmente, `tools/*.py` del repositorio y comprobaciones propias independientes (networkx).
Nota de proceso: la herramienta `update_step_status` no estaba disponible en esta sesión; el estado del paso se reporta en la respuesta final.

Severidades: **BLOQUEANTE** (impide aceptación tal cual), **MAYOR** (requiere corrección sustantiva del autor), **MENOR** (redacción/formato; aplicado por el revisor cuando no afecta afirmaciones matemáticas ni números).

---

## RONDA 1 (sobre el texto original)

### (1) Matemáticas

**R1-01 · BLOQUEANTE · `01_intro.tex` líneas 11–13 (cita en bloque de la Conjetura 14) y toda la narrativa derivada (abstract; §1 ítem (A); §1 "Methodological remark"; §5 Obs. (i); §7 último párrafo).**
La cita literal de la Conjetura 14 de [DEFH2023] está alterada: el manuscrito escribe *"The smallest graph … with trivial $\mathbb Z_2$-homology that is not strong I-contractible…"*, pero el original (arXiv:2109.06729v2, Conjecture 14, verificado en el PDF descargado) dice *"with trivial homology"*, y la convención explícita de ese artículo es $H_n(G):=H_n(G;\mathbb Z)$ (coeficientes enteros; §2 "To save on notation…"). Con la lectura literal (entera), las tres gráficas de 13 vértices con $H_1\cong\mathbb Z/3$ **no** refutan la primera oración de la Conjetura 14 (no tienen homología trivial). La refutación de ambas oraciones sigue siendo válida, pero vía $G_{14}^a$ (homología entera trivial, $\notin\mathfrak I_S$, 14 < 15), no vía torsión.
Hecho adicional que el manuscrito ya demuestra pero no enuncia: la menor gráfica $\mathbb Z$-acíclica fuera de $\mathfrak I_S$ tiene exactamente 14 vértices (porque las únicas $\mathbb Z_2$-acíclicas no-$\mathfrak I_S$ con ≤13 vértices son las tres de torsión).
*Propuesta:* (i) restituir la cita verbatim: `\textbf{Conjecture 14 of~\cite{DEFH2023}.} \emph{The smallest graph (in terms of vertices) with trivial homology that is not strong I-contractible is shown in Figure~2A. In particular this is the smallest graph that is I-contractible but not strong I-contractible.}` seguida de una aclaración: `In~\cite{DEFH2023} ``homology'' means integer homology of the clique complex, although the computations reported there (Ripser) use $\Ztwo$ coefficients; for $n\le 11$ the two notions coincide (Theorem~\ref{thm:A}).` (ii) Reescribir el ítem (A) del §1: `Read with integer coefficients, the first sentence of Conjecture~14 fails at $14$ vertices ($\Ga$ is $\ZZ$-acyclic and not in $\IS$); read with $\Ztwo$ coefficients---the invariant actually computed in~\cite{DEFH2023}---it fails already at $13$ vertices, and for a different reason: odd torsion.` (iii) Añadir a Theorem B la oración `In particular the smallest $\ZZ$-acyclic graphs that are not strong I-contractible also have exactly $14$ vertices.` (iv) Ajustar el abstract ("conjectured that it is the smallest graph with trivial homology…") y §7 último párrafo.

**R1-02 · MAYOR · `02_prelim.tex` §2.3 (frase "there are no edges in one or in four or more triangles in our examples"); `06_examples.tex` caption Fig. 4 ("pendant edge 13–9, which also lies in three triangles"); §6.2 párrafo "In all four graphs the vertices outside the identification cycle have an induced cycle as open neighbourhood…"; Tabla 3 columna $|E_3|$ "4 (+1 pendant)".**
Falso para $G_{14}^b$: la arista $\{9,13\}$ está en **cuatro** triángulos ($N(9,13)=\{0,1,3,4\}$, verificado con networkx y con `data/structure_84_graphs.csv`, columna `aristas_en_4mas_tri`). Lo mismo ocurre en las dos atascadas "anillo" (#48 arista {10,13}; #49 arista {10,11}). Consecuencias: (a) el vértice 9 de $G_{14}^b$ está fuera del ciclo de identificación y $N(9)$ tiene $b_1=2$ (no es un ciclo inducido); el vértice 13 tiene $N(13)$ con $b_1=3$; (b) la construcción de "desdoblado" del §2.3 debe cortar a lo largo de las aristas en **tres o más** triángulos (así lo hace el código: `espolones`).
*Propuesta:* §2.3: `let $E_{\ge 3}$ be the set of edges lying in three or more triangles (in our examples every edge lies in two, three or---in three of the $51$ graphs, including $\Gb$---four triangles)`; caption Fig. 4: `…the pendant edge $13\text{--}9$, which lies in four triangles`; §6.2: `In $\Dunce$, $\Ga$ and $\Gc$ the vertices outside the identification cycle have an induced cycle as open neighbourhood …; in $\Gb$ this holds for all vertices except $9$, the end of the pendant edge.`; Tabla 3: columna `$|E_{\ge3}|$`, entrada de $\Gb$ `5 (one in 4 triangles)`.

**R1-03 · MAYOR · `07_consequences.tex` Question 7.6 (`\begin{question}` tercera).**
Planteamiento lógicamente erróneo: la cota inferior (ningún complejo flag con ≤12 vértices tiene torsión impar en $H_1$) proviene de Adamaszek **sin** hipótesis de $\mathbb Z_2$-aciclicidad, y la existencia en 13 la da el Teorema A; luego 13 **ya es** el mínimo incondicional. La pregunta "Is 13 also the minimum without the $\mathbb Z_2$-acyclicity assumption" está respondida.
*Propuesta:* `Theorem~\ref{thm:A} and Adamaszek's classification~\cite{Adamaszek2014} show that $13$ is the smallest number of vertices of a flag complex with odd torsion in $H_1$. Are the three graphs of Theorem~\ref{thm:A} the only flag complexes on $13$ vertices with odd torsion in $H_1$ (our search covered only the $\Ztwo$-acyclic ones), and which torsion groups occur in $H_1$ on $13$ and $14$ vertices?`

**R1-04 · MAYOR · `06_examples.tex` Remark "Torsion in small flag complexes".**
Cita inexacta de [Adamaszek2014]: el teorema 1.1 de ese artículo dice (i) ≤10 vértices: libre de torsión; (ii) exactamente 4 gráficas con 11 vértices; (iii) existen **363** gráficas $L_i$ con 12 vértices tales que toda gráfica de 12 vértices con torsión es una $L_i$ o tiene $G\setminus v=K_i$. El número **394** es, en la Tabla 1 de Adamaszek, el de gráficas conexas "tame" con links cíclicos y torsión, no "el número de complejos flag con torsión en 12 vértices". Además, de los 363 $L_i$, 5 son $\simeq\mathbb{RP}^2\vee S^1$ (es decir $H_1\cong\mathbb Z/2\oplus\mathbb Z$, no $\cong\mathbb Z/2$). La conclusión "toda torsión en $H_1$ con ≤12 vértices es $\mathbb Z/2$" sí se sigue (para $G\setminus v=K_i$, $H_1(K_i)=\mathbb Z/2$ y Mayer–Vietoris da que la torsión de $H_1(G)$ es cociente de $\mathbb Z/2$), pero ese paso debe escribirse.
*Propuesta:* `Adamaszek~\cite{Adamaszek2014} proved that $H_1(\cl(G);\ZZ)$ is torsion-free for every graph on at most $10$ vertices, that exactly four graphs on $11$ vertices have torsion in $H_1$, and that every $12$-vertex graph with torsion in $H_1$ either is one of $363$ listed graphs or has a vertex $v$ with $G-v$ one of the four $11$-vertex graphs. All the listed complexes are homeomorphic or collapse to $\mathbb{RP}^2$ or are homotopy equivalent to $\mathbb{RP}^2\vee S^1$, so their torsion is $\ZZ/2$; and if $G-v$ is one of the four $11$-vertex graphs, the Mayer--Vietoris sequence of $\cl(G)=\cl(G-v)\cup\mathrm{cone}(\cl(\Nb(v)))$ shows that the torsion of $H_1(G)$ is a quotient of $\ZZ/2$. Hence no flag complex on at most $12$ vertices has odd torsion in $H_1$, and …` (Verificado: PDF de Adamaszek descargado vía Unpaywall, Theorem 1.1, Table 1 y §4.)

**R1-05 · MAYOR · `07_consequences.tex` Theorem D ("there are 32 pairwise non-isomorphic such graphs in the I4-closure of $G_{14}^a$ alone") y `04_algorithms.tex` §4.3 ("computed by the same breadth-first expansion without the stopping rule, recording for every supergraph whether it is in $\mathfrak I_S$").**
La "I$_4$-cerradura" se define en el Lema 3.2 como el conjunto de gráficas alcanzables por adiciones (I4) sucesivas (sin cota), pero el código (`src/atascadas.c`, función `cerradura`) **no expande** las gráficas que ya están en $\mathfrak I_S$ (correcto, pues sus (I4)-supergráficas están en $\mathfrak I_S$ por (F2)). El "32" cuenta entonces las gráficas de la *frontera* $\mathfrak I_S$ de esa expansión truncada, no "las gráficas de la cerradura con la propiedad (1)–(2)". Recomputado aquí: 16 gráficas no-$\mathfrak I_S$ + 32 gráficas $\mathfrak I_S$ de frontera, no isomorfas dos a dos (`labelg`); el dato no está en `data/` del repositorio.
*Propuesta:* Theorem D: `…and there are exactly $32$ pairwise non-isomorphic graphs $H+e\in\IS$ with $H$ in the $\mathrm{I}_4$-closure of $\Ga$, $H\notin\IS$ and $\Nb_H(e)\in\IS$.`; §4.3: `…by the same breadth-first expansion without the stopping rule, expanding only the graphs outside $\IS$ (a graph obtained from a member of $\IS$ by an (I4) addition is again in $\IS$ by (F2)) and recording the $\IS$ status of every graph reached.` Añadir `data/closure_G14a.tsv` (48 filas) al repositorio.

**R1-06 · MAYOR · `03_reduction.tex` Prop. 3.6 y `A_proofs.tex`; repositorio.**
La prueba de la Proposición 3.6 descansa en la corrida `--modo casi` sobre todas las gráficas conexas con $3\le n\le 11$, pero el repositorio **no contiene** ningún log de esa corrida (sólo el encabezado de `src/atascadas.c` menciona $n\le 9$, con cota "18 vértices"), y `verify.sh` no la reproduce. Verificado independientemente aquí: `geng -cq n | atascadas --modo casi` da 0 piezas casi atascadas para $n=3,\dots,11$ (n=11: 1 006 700 565 gráficas, 8 rebanadas, ≈4 min en 8 núcleos). *Propuesta:* añadir `yuca/logs/casi_n03-11.txt` (o `data/almost_stuck_counts.txt`) y un paso opcional en `verify.sh`; actualizar el comentario de `atascadas.c` (18→22).

**R1-07 · MAYOR · `03_reduction.tex` Lemma 3.5 (Z2test), prueba.**
No hay circularidad real (la igualdad $\mathbb Z_2$-acíclica $=\mathfrak I_S$ para $n\le12$ proviene de la Tabla, calculada con el decisor exacto de $\mathfrak I_S$ sobre *todas* las gráficas acíclicas, sin usar "atascadas"), pero la prueba cita el Teorema 6.1, que aparece después y cuya segunda parte depende del Lema 3.5. *Corregido (MENOR en redacción):* la prueba ahora cita sólo la Tabla 2 / Observación 5.1(i) y explicita la cota $n-1\le10$ del caso "almost stuck".

**R1-08 · MENOR · `02_prelim.tex` §2.1 "(I3) and (I4) can be realised by (I1) and (I2) [ChenYauYeh2001, Lemma 3]".** Según [DEFH2023, Lemma 3] la referencia es [7, Lemma 3.4] de Chen–Yau–Yeh. *Corregido* a `Lemma~3.4` (grado de verificación: a través de la atribución en DEFH2023; no se consultó el original de CYY).

**R1-09 · MENOR · `02_prelim.tex`, `04_algorithms.tex`, `07_consequences.tex`: "\cite[Fig.~3]{DEFH2023}" como evidencia de que "el orden de los borrados importa en $\mathfrak I_S$".** La Fig. 3 de DEFH2023 ilustra el Teorema 16, que trata de borrados de **vértices** en $\mathfrak I_{VS}$; para aristas en $\mathfrak I_S$ la evidencia es la gráfica de su Fig. 2B (y el Teorema D del presente manuscrito). *Corregido* a `\cite[Fig.~2B and Fig.~3]{DEFH2023}` con frase aclaratoria.

**R1-10 · MENOR (propuesta, no aplicado) · `02_prelim.tex` §2.2 "the standard example being the dunce hat with a 2-cell attached differently".** El dunce hat es contráctil; el ejemplo estándar de 2-complejo $\mathbb Z$-acíclico no contráctil es el complejo de presentación de un grupo perfecto no trivial (p. ej. $\langle a,b\mid a^5=b^3=(ab)^2\rangle$, esqueleto de la esfera de homología de Poincaré menos una 3-celda, que el propio DEFH2023 menciona). *Propuesta:* `(the standard examples are acyclic $2$-complexes with non-trivial perfect fundamental group, such as the spine of the Poincaré homology sphere with a $3$-cell removed)`.

**R1-11 · MENOR · `01_intro.tex` ítem (C)**: define "stuck" con vecindades "no $\mathbb Z_2$-acíclicas", mientras la Def. 3.1 usa "$\notin\mathfrak I_S$" (equivalentes sólo para $n\le14$, Lema 3.5). *Corregido* en redacción.

### (2) Números (ver `NUMERIC_CHECK.md` para la tabla completa)

**R1-12 · MAYOR · `03_reduction.tex` último párrafo: "computes the homology of $G$ itself for only 15 693 920 490 graphs".** Falso según el código y los logs: 15 693 920 490 es `pasa_vecindades` (gráficas que superan las pruebas de vecindades de vértices y pasan a la prueba de aristas); la homología de $G$ se calcula sólo para las que superan la prueba de aristas: `pasa_aristas` = **218 516** (n=13) y **13 536 597** (n=14). La Fig. 9 ya muestra 218 516 correctamente; la Tabla 1 omite la columna `pass_edges`. *Propuesta:* `…computes the common neighbourhoods for only $\num{15693920490}$ graphs and the homology of $G$ itself for only $\num{218516}$ graphs…`; añadir columna "pass $\Nb(u,v)$" (218 516 / 13 536 597) a la Tabla 1 y renombrar "pass $\Nb$" → "pass $\Nb(v)$".

**R1-13 · MAYOR · `04_algorithms.tex` §4.5: "geng (about 2.7 µs per graph); Algorithm 1 costs about 0.8 µs per graph".** Inconsistente con `sacct`: n=13: 7 tareas × 64 núcleos × 49.47 h = 1.14×10⁷ core-s / 2.10×10¹³ gráficas = **0.54 µs/gráfica** (geng + filtro, cota superior); n=14 K₄-libre: 1.01×10⁸ core-s / 6.49×10¹³ = **1.56 µs/gráfica**. *Propuesta:* sustituir por las cifras medidas por corrida o eliminar la frase.

**R1-14 · MAYOR · Apéndice D / `yuca/logs/n14_bitacora_p011.txt`.** El archivo registra un array **2079068** (nodo hpc-05, 11-oct 02:12–09:44, `-k -C -d4 -D12`, modo atascadas) que no aparece ni en el manuscrito ni en `yuca/README.md`; la bitácora del frente p011 real (array 2079156) está dentro de `n14_bitacora_p029.txt`. Si la corrida 2079068 aportó rebanadas a los registros, debe listarse en la Tabla 1/Apéndice D; si fue descartada, debe decirse y renombrar el log. *Decisión del autor.*

**R1-15 · MENOR · `04_algorithms.tex` §4.1 "matrices have at most 45×32 entries".** La atascada #51 tiene 47 aristas y 34 triángulos, y las gráficas de las cerraduras hasta 51 aristas. *Corregido* a "a few dozen rows and columns (at most $51\times 38$ for the graphs in the closures)" → se dejó como "at most about $50\times 40$" (ver texto).

**R1-16 · MENOR · `04_algorithms.tex` Tabla 1 / Apéndice D "≈33 h".** `sacct`: tareas de 2079102 ≈ 1-09:25 a 1-10:17 (33.4–34.3 h); bitácora: 11:23 (11-oct) → 21:41 (12-oct) = 34 h 18 min de pared. "≈33 h" es defendible como duración de tarea; se sugiere "about 34 h of wall time". No modificado.

**R1-17 · MENOR · `06_examples.tex` "canonical form \gsix{LtDzQNKmpKXT`V}".** La forma canónica depende de la herramienta (`labelg` por defecto da `L?j@aaVqxzLr~o`); las dos cadenas son isomorfas (verificado). *Corregido* a "isomorphic to".

**R1-18 · MENOR · `tables/table_cardinalities.tex` fila 14†.** La nota dice "sólo la clase K₄-libre" pero la celda da "$\mathfrak I\setminus\mathfrak I_S\ge29$", que incluye gráficas con $K_4$. *Corregido* a "stuck ($K_4$-free) $=51$; $\mathfrak I\setminus\mathfrak I_S$: exactly $8$ $K_4$-free, $\ge 29$ in total".

Todo lo demás coincide (ver NUMERIC_CHECK.md): 3 gráficas de 13 (40/41/42 aristas, $H_1=\mathbb Z/3$, cerradura exacta), 51 atascadas (25×43, 18+1×44, 4+2×45, 1×47; 48 con $\mathbb Z/3$), grados/|Aut|/$|E_3|$/disco/k de la Tabla 3, 51 filas de la Tabla B.1, trazas de 18/19/18/16 borrados válidas paso a paso, rutas a cono 11/12/12/8 válidas, 2271/29/2242/8/277, contadores de n=12/13/14, 2 000 000 rebanadas, 692 duplicadas, 0 faltantes, filas n≤10 de la Tabla 2 reproducidas (n≤9 por `verify.sh`, n=10 aquí), mapa de etiquetas del Dunce Hat, Mayer–Vietoris $H(G-v)\cong H(N(v))$ en los 4 ejemplos.

### (3) Inglés académico y estilo

**R1-19 · MENOR · `03_reduction.tex`**: `\end{figure} To test stuckness…` sin salto de párrafo. *Corregido.*
**R1-20 · MENOR · `04_algorithms.tex` §4.5**: "SLURM 24.11, Lustre file system, SLURM with a per-project…" (SLURM repetido). *Corregido.*
**R1-21 · MENOR · `04_algorithms.tex` Tabla 1**: encabezado "pass $N$" ambiguo. *Corregido* a "pass $\Nb(v)$" (la columna "pass $\Nb(u,v)$" se propone en R1-12).
**R1-22 · MENOR · abstract y §6.1 Remark**: "the smallest flag complexes with odd torsion" → "with odd torsion in $H_1$" (Adamaszek sólo cubre $H_1$). *Corregido.*
**R1-23 · MENOR · `05_table.tex` Obs. (ii) y §4.6**: "independent (unpublished, 2025) computation by the authors" — afirmación no verificable; sugerir citar como comunicación/dato en el repositorio o eliminar. No modificado.
**R1-24 · MENOR · `main.tex`**: los apéndices van después de la bibliografía; en elsarticle lo habitual es `\appendix` antes de `\bibliography`. No modificado (decisión editorial).
**R1-25 · MENOR · Figuras**: en el PDF las Figs. 5, 6 y 7 (G14c, certificado, mosaico) flotan a las pp. 34–38, después de los apéndices; usar `[p]` con `\clearpage` tras §6 o `\usepackage[section]{placeins}`. No modificado (no se puede recompilar aquí con el mismo motor; ver nota).
**R1-26 · MENOR · uso de "we"**: adecuado y uniforme; no hay voz pasiva excesiva. Sin cambios.
**R1-27 · MENOR · `01_intro.tex` ítem (C)**: "reduces the search space by three to four orders of magnitude" — la restricción de grados reduce sólo ×2.4; es la cascada la que reduce 10⁴–10⁵. *Corregido* a redacción precisa.

### (4) Bibliografía

Las 19 claves citadas existen en `refs.bib` (0 faltantes); 24 entradas no citadas (BibTeX no las imprime). Campos completos en todas las citadas (autor, título, año, revista, volumen, páginas, DOI; libros con editorial/serie/volumen).
**R1-28 · MENOR · `refs.bib` GhoshGhosh2021** ("A contractible graph with eleven vertices and no gluable edge") no se cita, pero por su título parece directamente relevante a la Conjetura 3 de Frías-Armenta discutida en §7.2 (transformar en $K_n$ pegando aristas). *No verificado el contenido*; el autor debe revisarlo y citarlo o eliminarlo.
**R1-29 · MENOR · `refs.bib`**: forma del apellido del tercer autor inconsistente entre entradas (`Hernández-Hernández, Héctor A.` en EFH2022 vs `Hernández, Héctor A.` en DEFH2023 y en la portada). Verificar contra las versiones publicadas.
**R1-30 · Verificación de citas que afirman contenido**: [DEFH2023] Conj. 14 (ver R1-01: alterada), Conj. 15 ✓, Thm 16 (12 vértices) ✓, Lemma 19 (0-Dis ⇒ I_SV) ✓, Conj. 27 ✓, Question 28 ✓, Fig. 2A/2B ✓, Fig. 3 (ver R1-09); [Adamaszek2014] ver R1-04; [ChenYauYeh2001, Lemma 3] ver R1-08; [DochtermannMatsushita2025] (equivalencia I ⇔ contráctil; I-homotopía = homotopía simple) no reverificado aquí (verificado en fase bibliográfica previa según memoria del proyecto); [FriasArmenta2020] "13-vertex counterexample" y numeración "Conjectures 3–5" no verificados; [EFH2022] "I_S ⊆ colapsable" y "Conjecture 27" (en DEFH2023 la conjetura se atribuye a [9]=EFH) parcialmente verificado; [BarmakMinian2012], [BouletFieuxJouve2010], [FieuxJouve2020], [Malen2023], [Jonsson2008], [Cohen1973], [Zeeman1963], [NowakowskiWinkler1983], [McKayPiperno2014], [Ivashchenko1993/1994a/1994b] citas genéricas, no verificadas en contenido.

### (5) Estructura

**R1-31 · MAYOR · Tabla 2 filas 13 y 14 "computation in progress" y §1 ítem (E).** Un árbitro de DM no aceptará filas "en cálculo"; o se completan antes del envío o se eliminan de la tabla (dejando sólo la frase sobre los tres/51 ejemplos) y se anuncian como trabajo en curso. *Decisión del autor.*
**R1-32 · MAYOR · Falta enunciar explícitamente el resultado "menor gráfica $\mathbb Z$-acíclica no-$\mathfrak I_S$ = 14"** (ver R1-01), que es la refutación literal de la Conjetura 14 y se sigue de lo ya demostrado.
**R1-33 · MENOR · Sobra**: la frase "(Non-flag triangulations of $M(\mathbb Z/3,1)$ exist with far fewer vertices; the flag condition is the obstruction.)" sin referencia; citar [Newman2019] o [Kogan2025] (ya en refs.bib) o eliminar.
**R1-34 · MENOR · Falta**: en el §4.6 "Validation" conviene indicar que `verify.sh` fue ejecutado por los autores y su salida (31 checks) está en el repositorio; en esta revisión `verify.sh` pasó 31/31.


---

## Correcciones aplicadas por el revisor tras la ronda 1 (sólo redacción/formato/citas; ningún número ni enunciado sustantivo fue alterado)

| # | archivo | cambio |
|---|---|---|
| R1-07 | `03_reduction.tex` | prueba del Lema 3.5: cita la Tabla 2/Obs. 5.1(i) en vez del Teorema 6.1 (elimina la apariencia de circularidad), explicita la cota $n-1\le 10$ del caso *almost stuck* |
| R1-08 | `02_prelim.tex` | `\cite[Lemma~3]{ChenYauYeh2001}` → `Lemma~3.4` |
| R1-09 | `02_prelim.tex`, `04_algorithms.tex`, `07_consequences.tex` | referencias a "Fig. 3 de DEFH2023" para el orden de borrados: ahora Fig. 2B (aristas, $\mathfrak I_S$) y Fig. 3/Thm 16 (vértices, $\mathfrak I_{VS}$) |
| R1-11 | `01_intro.tex` (C) | "stuck" descrito con $\notin\mathfrak I_S$ (equivalente a no-$\mathbb Z_2$-acíclico para $n\le14$) |
| R1-05 (parte) | `04_algorithms.tex` §4.3 | descripción de la cerradura conforme al código (no se expanden gráficas de $\mathfrak I_S$) |
| R1-15 | `04_algorithms.tex` §4.1 | tamaño de matrices: "a few dozen rows and columns (at most $51\times48$…)" |
| R1-17 | `06_examples.tex` | "canonical form" → "isomorphic to" |
| R1-18 | `tables/table_cardinalities.tex` | fila 14†: "stuck ($K_4$-free) $=51$; $\mathfrak I\setminus\mathfrak I_S$: exactly 8 $K_4$-free, $\ge29$ in total" |
| R1-19 | `03_reduction.tex` | salto de párrafo tras `\end{figure}` |
| R1-20 | `04_algorithms.tex` | "SLURM" duplicado |
| R1-21 | `04_algorithms.tex` Tabla 1 | encabezado "pass $N(v)$"; caption remite al Apéndice D para `pass_edges` |
| R1-22 | `main.tex` (abstract), `06_examples.tex` | "odd torsion" → "odd torsion in $H_1$" |
| R1-27 | `01_intro.tex` (C) | "three to four orders of magnitude" → descripción precisa (la restricción de grados reduce ×2.4; la cascada ≈10⁻³) |
| R2-01 | `03_reduction.tex` Def. 3.1 | "A graph $G$ **on at least two vertices** is stuck…" (sin esto $K_1$ es atascada y está en $\mathfrak I_S$) — **el autor debe confirmar** |
| R2-02 | `03_reduction.tex` Prop. 3.6 | "no almost stuck graph with $2\le n\le 11$ vertices" + nota sobre $K_2$ (sin esto $K_1$ es contraejemplo vacuo) — **el autor debe confirmar** |

Recompilado con `tectonic` (entorno conda `latex`): 0 errores, 0 referencias/citas indefinidas, 39 páginas (`paper/main.pdf` dentro de `paper_revised.tar.gz`). Copia intacta del original en `paper_orig_backup/` (no incluida en el tar).

---

## RONDA 2 (sobre el texto corregido)

### (1) Matemáticas

**R2-03 · MAYOR · `07_consequences.tex` Question 7.3 (`q:K4`).** "Is every graph in $\mathfrak I\setminus\mathfrak I_S$ on 14 vertices $K_4$-free? Equivalently, is the list of eight graphs complete?" La primera pregunta **ya tiene respuesta negativa en el propio manuscrito**: de las 29 gráficas de $\mathfrak I\setminus\mathfrak I_S$ halladas en las cerraduras, 21 contienen $K_4$ (`data/I_not_strong_14_closure.tsv`, columna `K4 count`). Las dos preguntas no son equivalentes. La pregunta abierta correcta es sobre las gráficas **atascadas**. *Propuesta:* `Is every stuck graph in $\I\setminus\IS$ on $14$ vertices $K_4$-free? Equivalently (Theorem~\ref{thm:C}(ii)), is every graph in $\I\setminus\IS$ on $14$ vertices one of the $29$ graphs of Section~\ref{sec:fourteen}?`

**R2-04 · MENOR · Def. 3.1 / Prop. 3.6 (casos límite $K_1$, $K_2$).** Aplicado (R2-01, R2-02); ver arriba. La prueba del Lema 3.3 ya usa $|A|,|B|\ge3$, así que el enunciado restringido basta para la 2-conexidad.

**R2-05 · MENOR · `03_reduction.tex` Lema 3.4**: "on $n\ge2$ vertices" — una gráfica 2-conexa tiene $\ge3$ vértices por convención; escribir "$n\ge 3$" o simplemente omitir. No modificado (cosmético).

**R2-06 · MENOR · `04_algorithms.tex` Tabla 1, fila $n=12$, columna "stuck" $=0$.** El modo *tabla* no evalúa "atascada"; el 0 se infiere de $\mathbb Z_2$-acíclica $=\mathfrak I_S$. Sugerir "0$^{*}$" con nota "(implied by Observation 5.1(i))" o "--". No modificado.

**R2-07 · MENOR · `01_intro.tex` §1 primer párrafo**: "Chen, Yau and Yeh proved that contractible transformations preserve the **simple** homotopy type". DEFH2023 cita de CYY sólo "if $G$ is I-contractible then $\Delta(G)$ is contractible" (Corollary 3.6); la preservación del tipo de homotopía *simple* se atribuye habitualmente a Boulet–Fieux–Jouve 2010 y a Dochtermann–Matsushita 2025. Verificar en el original de CYY o reescribir "preserve the homotopy type … [CYY]; in fact the simple homotopy type [BFJ2010, DM2025]". No modificado (no se consultó CYY).

**R2-08 · Re-verificación de R1-01 a R1-06 en el texto corregido**: siguen pendientes de decisión del autor (no se tocaron: cita de la Conjetura 14, arista en 4 triángulos de $G_{14}^b$, Question 7.6, Remark de Adamaszek, enunciado del "32", logs de `casi`). Las correcciones aplicadas no interactúan con ellos salvo R1-22 (ahora el abstract dice "odd torsion in $H_1$", coherente con la propuesta para R1-03/R1-04).

### (2) Números
Recontados sobre el texto corregido: no se introdujo ningún número nuevo salvo "$51\times48$" (R1-15; 51 aristas y 48 triángulos son los máximos sobre `acyclic_not_strong_14_closure.tsv`, calculados aquí) y "about $10^{-3}$" (218 516 + 13 536 597 vs. totales: $1.0\times10^{-8}$ para la homología completa; $7.5\times10^{-4}$ y $1.7\times10^{-3}$ para la fracción que llega a las pruebas de vecindad común). **Corrección R2-09 · MENOR**: la frase insertada en §1(C) dice "rejects all but a fraction of about $10^{-3}$ … before any homology of the whole graph is computed"; la fracción que llega a la homología completa es ≈10⁻⁸, y ≈10⁻³ la que llega a las pruebas de vecindad común. *Corregido* en la segunda pasada (ver tabla de cambios, R2-09).

### (3) Inglés y estilo
**R2-10 · MENOR**: tras la inserción en §1(C) la frase es larga; aceptable. "Fig." vs "Figure" se usa de forma consistente (`Fig.~\ref`). Captions terminan en punto. "neighbourhood" (ortografía británica) consistente en todo el texto; "labelled", "memoised", "realised" coherentes. OK.
**R2-11 · MENOR · PDF recompilado**: las figuras de §6 siguen flotando a las pp. 35–39 (tras los apéndices) por el uso de `[p]` con `\appendix` después de la bibliografía; recomendar `\clearpage` al final de §6 o mover `\appendix` antes de `\bibliography` (R1-24/R1-25).

### (4) Bibliografía
Sin cambios respecto a la ronda 1 (R1-28, R1-29, R1-30 pendientes). Las 19 claves citadas siguen resolviéndose (0 `Citation undefined` en `main.log`).

### (5) Estructura
Pendientes R1-31 (filas "in progress"), R1-32 (enunciar el mínimo 14 para $\mathbb Z$-acíclicas), R1-33, R1-34.
| R2-09 | `01_intro.tex` (C) | fracciones de la cascada: ≈10⁻³ antes de las vecindades comunes, ≈10⁻⁸ antes de la homología completa |
