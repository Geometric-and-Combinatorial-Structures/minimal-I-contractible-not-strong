#!/usr/bin/env python3
"""Verify the finite evidence and write reports into a new output directory.

Python 3.11+ standard library. --extended also requires a C11 compiler.
Neither route enumerates the large graph universes or uses the network.
"""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from integrity import verify
from processes import run_process
from output_paths import generated_output


def run_check(name, command, timeout, output):
    started = time.monotonic()
    record = {"name": name, "command": command}
    try:
        proc = run_process(command, cwd=ROOT, text=True, encoding='utf-8', errors='replace', capture_output=True,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                                       GRAPH_CHECK_TIMEOUT=str(timeout)), timeout=timeout)
        record.update(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    except subprocess.TimeoutExpired as error:
        record.update(exit_code=124, stdout=error.stdout or "", stderr=(error.stderr or "") + "\nTime limit exceeded; check incomplete.")
    except Exception as error:
        record.update(exit_code=125, stdout="", stderr=type(error).__name__ + ": " + str(error))
    record["seconds"] = round(time.monotonic() - started, 3)
    (output / (name + ".stdout.txt")).write_text(record.pop("stdout"), encoding="utf-8")
    (output / (name + ".stderr.txt")).write_text(record.pop("stderr"), encoding="utf-8")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="a directory that does not yet exist")
    parser.add_argument("--extended", action="store_true", help="also compare current C recurrences on all labelled graphs of order at most five")
    parser.add_argument("--cc", default="cc", help="C compiler for --extended")
    parser.add_argument("--timeout", type=float, default=600, help="positive finite time limit per subprocess in seconds")
    parser.add_argument("--require-git-baseline", action="store_true", help="require the historical Git-tree comparison")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Python 3.11 or later is required")
    if not __debug__ or os.environ.get("PYTHONOPTIMIZE") not in (None, "", "0"):
        parser.error("Run without -O, -OO or PYTHONOPTIMIZE; finite checks use assertions")
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 100000:
        parser.error("--timeout must be finite and in (0, 100000] seconds")
    output = (args.output or ROOT / "results" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])).resolve()
    try:
        output = generated_output(output)
    except ValueError as error:
        parser.error(str(error))
    try:
        output.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        parser.error(str(error))
    report = {"schema": 1, "PASS": False, "python": sys.version.split()[0],
              "route": "extended" if args.extended else "finite",
              "full_census_rerun": False, "checks": [], "errors": [], "scope_notes": []}
    try:
        report["source_integrity_before"] = verify(ROOT)
        commands = [("repository", [sys.executable, "-P", str(ROOT / "tools/check_repository.py")]),
                    ("finite", [sys.executable, "-P", str(ROOT / "tools/verify_quick.py"), "--timeout", str(args.timeout)]),
                    ("secondary", [sys.executable, "-P", str(ROOT / "tools/check_secondary_results.py")]),
                    ("historical_sources", [sys.executable, "-P", str(ROOT / "verification/historical_small_orders/check_source_identity.py")]),
                    ("article_table", [sys.executable, "-P", str(ROOT / "tools/generate_cardinalities.py"), "--csv", str(ROOT / "data/cardinalities.csv"),
                                       "--output", str(ROOT / "paper/tables/cardinalities.tex"), "--check"]),
                    ("supplement_tables", [sys.executable, "-P", str(ROOT / "tools/build_supplement_tables.py"), "--check"]),
                    ("interfaces", [sys.executable, "-P", str(ROOT / "tests/test_reproduction.py")]),
                    ("byte_mutations", [sys.executable, "-P", str(ROOT / "finite/certificates/test_certificate_integrity.py")]),
                    ("notebook", [sys.executable, "-P", str(ROOT / "tests/run_notebook.py")])]
        if args.require_git_baseline:
            next(command for name, command in commands if name == "repository").append("--require-git-baseline")
        if args.extended:
            commands.append(("current_recurrences", [sys.executable, "-P", str(ROOT / "verification/current_recurrences/implementation_correspondence.py"),
                            "--cc", args.cc, "--output-dir", str(output / "current_recurrences")]))
        for name, command in commands:
            # The finite driver has eleven separately bounded stages.
            limit = args.timeout * 12 if name == "finite" else args.timeout
            record = run_check(name, command, limit, output)
            report["checks"].append(record)
            if record["exit_code"]:
                raise ValueError("Required check failed or is incomplete: " + name)
            if name == "repository":
                metadata = json.loads((output / "repository.stdout.txt").read_text(encoding="utf-8"))
                report["scope_notes"].append("Git baseline comparison: " + metadata["baseline_tree_reason"])
        report["source_integrity_after"] = verify(ROOT)
        report["PASS"] = True
    except (OSError, ValueError) as error:
        report["errors"].append(str(error))
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["PASS" if report["PASS"] else "FAIL", "Route: " + report["route"], "Full census rerun: no"]
    lines.extend(r["name"] + ": " + ("PASS" if r["exit_code"] == 0 else "FAIL") for r in report["checks"])
    lines.extend(report["errors"])
    lines.extend(report["scope_notes"])
    (output / "report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("Reports: " + str(output))
    return 0 if report["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
