#!/usr/bin/env python3
"""Prepare an interactive notebook copy under the repository's results directory."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=ROOT / "results/notebook")
args = parser.parse_args()
output = args.output.resolve()
if output == ROOT / "results" or not output.is_relative_to(ROOT / "results"):
    parser.error("--output must be a new subdirectory of the repository's results/")
try:
    output.mkdir(parents=True, exist_ok=False)
except OSError as error:
    parser.error(str(error))
destination = output / "reproduce.ipynb"
shutil.copy2(ROOT / "notebooks/reproduce.ipynb", destination)
print("Open this copy in Jupyter: " + str(destination))
