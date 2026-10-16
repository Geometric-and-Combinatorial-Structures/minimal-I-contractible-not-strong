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

Base textual: v2 de la auditoría (título corto), seleccionada expresamente por el autor; sobre ella se aplicaron las correcciones de la versión 3 (16-oct-2026), listadas en `CAMBIOS_v3.md`: enunciados textuales de las Conjeturas 14 y 15 (versión editorial) con nota sobre el preprint, filas 12 y 13 de la tabla descritas de forma coherente con la tabla, commit del repositorio corregido (`4a059b5` en lugar de `83d5ffe`), evidencia de procedencia del script p011 (prueba Y-F01) y una referencia nueva (preprint arXiv v2).

`build.sh` produce `main.pdf` (antes usaba `-jobname=main_v2`).
