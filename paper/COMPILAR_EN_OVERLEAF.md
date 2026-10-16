# Compilación del preprint en Overleaf

Este directorio es autocontenido. Cargarlo completo o importar su ZIP, manteniendo las subcarpetas.

- Documento principal: `main.tex`.
- Compilador: **pdfLaTeX**.
- Bibliografía: BibTeX, ejecutado automáticamente por Overleaf.
- Clase: `amsart`, 11 puntos.
- Fuente: Palatino para texto y matemáticas (`mathpazo`); Courier para monoespaciado.
- Márgenes: una pulgada.
- Figuras: once PDF vectoriales locales en `figures/`; no se necesita conversión SVG, acceso a GitHub ni `shell-escape`.

Se conserva el estilo bibliográfico numérico anterior para no alterar el texto y orden de las referencias. `elsarticle-num.bst` se incluye en el directorio y funciona sin la clase Elsevier.

Si se importan archivos sobre un proyecto anterior, seleccionar **Recompile from scratch**. No seleccionar una sección como documento principal.

Compilación local equivalente:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Base textual: versión 3 (16-oct-2026, `CAMBIOS_v3.md`) con las correcciones de la versión 4 (16-oct-2026), listadas en `CAMBIOS_v4.md`: premisas explícitas del control A001349 y cotas condicionadas (H-26), generador de tablas sin la fila 13 duplicada (H-27), Tabla 2 en una página apaisada con la leyenda completa (H-28), tabla de las 20 gráficas de orden 12 en 2-Dis∖1-Dis (Apéndice B.2), rutas fuera de la Observación 5.1(ii), procedencia del script p011 como corroboración forense, §4.6, §8 y Apéndice D al día con el repositorio, leyenda de la Fig. 9 con la reserva H14, y cadenas graph6 y opciones de línea de órdenes que ahora se copian del PDF sin alteración.

Paquetes añadidos en la versión 4: `pdflscape` (la página de la Tabla 2 se muestra girada en el visor) y `adjustbox` (reduce la tabla sólo si no cabe). Ambos forman parte de TeX Live y están en Overleaf.

`build.sh` produce `main.pdf` (antes usaba `-jobname=main_v2`).
