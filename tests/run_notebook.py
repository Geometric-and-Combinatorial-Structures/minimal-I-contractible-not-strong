#!/usr/bin/env python3
"""Execute the plain-Python cells of the committed notebook in order."""
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
os.chdir(ROOT)
notebook = json.loads((ROOT / "notebooks/reproduce.ipynb").read_text(encoding="utf-8"))
namespace = {"__name__": "__notebook__"}
count = 0
for i, cell in enumerate(notebook["cells"]):
    if cell["cell_type"] == "code":
        exec(compile("".join(cell["source"]), "notebooks/reproduce.ipynb:cell" + str(i + 1), "exec"), namespace)
        count += 1
print("PASS:", count, "notebook cells executed")
