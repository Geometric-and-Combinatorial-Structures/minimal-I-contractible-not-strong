#!/usr/bin/env python3
"""Regenerate the finite closures of the 51 deposited seeds with the current C core.

Requires a C11 compiler and nauty labelg. This does not enumerate a graph universe.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from processes import run_process

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new output directory")
    parser.add_argument("--cc", default="cc")
    parser.add_argument("--labelg", default="labelg")
    parser.add_argument("--timeout", type=float, default=1200, help="positive finite limit per external command, in seconds")
    args = parser.parse_args()
    output = args.output.resolve()
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 100000:
        parser.error("--timeout must be finite and in (0, 100000] seconds")
    if output.is_relative_to(ROOT) and (not output.relative_to(ROOT).parts or output.relative_to(ROOT).parts[0] not in ("results", "build")):
        parser.error("Inside the repository, use a new directory under root results/ or build/")
    if output.exists():
        parser.error("Output directory already exists")
    cc = shutil.which(args.cc)
    labelg = shutil.which(args.labelg)
    if not cc or not labelg:
        parser.error("Both the C compiler and nauty labelg are required")
    output.mkdir(parents=True, exist_ok=False)
    source = ROOT / "v2/src/atascadas_v2.c"
    seeds = ROOT / "data/stuck_14_K4free.g6"
    reference = ROOT / "finite/data/acyclic_not_strong_14_closure.tsv"
    inputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in [source, seeds, reference]}
    report = {"schema": 1, "PASS": False, "date_utc": datetime.now(timezone.utc).isoformat(),
              "full_census_rerun": False, "classifier": "current C core v2.2",
              "inputs": inputs, "labelg_sha256": digest(Path(labelg)), "errors": []}
    started = time.monotonic()
    try:
        compiled = run_process([cc, "-O3", "-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                                   "-o", str(output / "classifier"), str(source)], capture_output=True, text=True, timeout=args.timeout)
        (output / "compile.stdout").write_text(compiled.stdout)
        (output / "compile.stderr").write_text(compiled.stderr)
        compiled.check_returncode()
        version = run_process([str(output / "classifier"), "--version"], capture_output=True, text=True, timeout=args.timeout)
        version.check_returncode()
        report["classifier_version"] = version.stdout.strip()
        if "v2.2" not in report["classifier_version"]:
            raise ValueError("Unexpected classifier version")
        with seeds.open() as stream, (output / "closures.raw").open("w") as stdout, (output / "closures.stderr").open("w") as stderr:
            run = run_process([str(output / "classifier"), "--modo", "cerradura"], stdin=stream, stdout=stdout, stderr=stderr, timeout=args.timeout)
        report["classifier_exit"] = run.returncode
        run.check_returncode()
        lines = (output / "closures.raw").read_text().splitlines()
        if any("TRUNCADA" in line for line in lines):
            raise ValueError("Closure search was truncated")
        raw = [line.split()[1] for line in lines if line.startswith("NO_I_S ")]
        if sum(line.startswith("== cerradura de ") for line in lines) != 51:
            raise ValueError("Not all 51 seed closures were processed")
        with reference.open(newline="") as stream:
            records = list(csv.DictReader(stream, delimiter="\t"))
        for name, graphs in [("generated", raw), ("reference", [r["graph6"] for r in records])]:
            (output / (name + ".g6")).write_text("\n".join(graphs) + "\n")
            proc = run_process([labelg, "-q", str(output / (name + ".g6")), str(output / (name + ".canonical.g6"))],
                                  capture_output=True, text=True, timeout=args.timeout)
            proc.check_returncode()
        generated = set((output / "generated.canonical.g6").read_text().splitlines())
        expected = set((output / "reference.canonical.g6").read_text().splitlines())
        if generated != expected or len(expected) != len(records) or len(generated) != 2271:
            raise ValueError("Regenerated closure classes differ from the catalog")
        if inputs != {name: digest(ROOT / name) for name in inputs} or digest(Path(labelg)) != report["labelg_sha256"]:
            raise ValueError("Inputs changed during execution")
        report.update(PASS=True, seeds=51, generated_non_strong_records=len(raw),
                      non_strong_isomorphism_classes=len(generated), reference_classes=len(expected),
                      inputs_unchanged=True, exact_class_sets_equal=True,
                      classifier_sha256=digest(output / "classifier"),
                      output_sha256={name: digest(output / name) for name in ["closures.raw", "closures.stderr", "generated.canonical.g6", "reference.canonical.g6"]})
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        report["errors"].append(str(error))
    report["seconds"] = round(time.monotonic() - started, 3)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
