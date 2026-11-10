#!/usr/bin/env python3
"""Reject unresolved references, missing glyphs and overfull boxes in TeX logs."""
import argparse
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("logs", nargs="+", type=Path)
args = parser.parse_args()
failures = []
pattern = re.compile(r"Overfull|Missing character|undefined|Rerun to get|^!|Warning:.*Citation", re.I)
for log in args.logs:
    for number, line in enumerate(log.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if pattern.search(line):
            failures.append(str(log) + ":" + str(number) + ": " + line)
if failures:
    parser.exit(1, "\n".join(failures) + "\n")
print("PASS:", len(args.logs), "document logs")
