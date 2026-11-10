#!/usr/bin/env python3
"""Exercise witness exports and reject damaged evidence and invalid runs."""
from pathlib import Path
import importlib.util
import json
import os
import csv
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "finite/certificates"))
from integrity import verify, write_manifest
from finite_checks import decode, strong, h1
from finite_isomorphism import isomorphic, pairwise_nonisomorphic
from processes import run_process
from output_paths import generated_output
import time
import signal


def command(*args, environment=None):
    return subprocess.run([sys.executable, "-P", *map(str, args)], cwd=ROOT,
                          env=environment or dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                          capture_output=True, text=True, timeout=float(os.environ.get("GRAPH_CHECK_TIMEOUT", "60")))


class ReproductionTests(unittest.TestCase):
    def test_label_preserving_exports(self):
        records = json.loads((ROOT / "finite/certificates/disc_hypotheses.json").read_text())
        figures = json.loads((ROOT / "tools/figures/witness_data.json").read_text())["graphs"]
        aliases = {"G13": "G13", "G14a": "Ga", "G14b": "Gb", "G14c": "Gc"}
        for row in records:
            with self.subTest(graph=row["graph"]):
                output = command(ROOT / "generate.py", "--graph", row["graph"], "--format", "json")
                self.assertEqual(output.returncode, 0, output.stderr)
                graph = json.loads(output.stdout)
                self.assertEqual(graph["graph6"], row["graph6"])
                self.assertEqual(len(graph["edges"]), graph["m"])
                self.assertFalse(strong(decode(graph["graph6"])))
                self.assertEqual(h1(decode(graph["graph6"])), (0, (3,)) if row["graph"] == "G13" else (0, ()))
                if row["graph"] in aliases:
                    figure = figures[aliases[row["graph"]]]
                    self.assertEqual(graph["n"], figure["n"])
                    self.assertEqual({tuple(e) for e in graph["edges"]}, {tuple(sorted(e)) for e in figure["edges"]})
                if row["graph"] != "G13":
                    extension = command(ROOT / "generate.py", "--graph", row["graph"], "--extension")
                    self.assertEqual(extension.returncode, 0, extension.stderr)
                    self.assertTrue(strong(decode(extension.stdout.strip())))

    def test_bad_arguments(self):
        for args in [("--graph", "unknown"), ("--graph", "G13", "--extension")]:
            self.assertNotEqual(command(ROOT / "generate.py", *args).returncode, 0)
        for limit in ("0", "-1", "nan", "inf", "200000", "1e7"):
            self.assertNotEqual(command(ROOT / "reproduce.py", "--timeout", limit).returncode, 0)

    def test_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "keep.txt"
            marker.write_text("preserved")
            result = command(ROOT / "reproduce.py", "--output", tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), "preserved")
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["keep.txt"])

    def test_optimized_interpreter_is_rejected(self):
        result = command(ROOT / "reproduce.py", environment=dict(os.environ, PYTHONOPTIMIZE="1"))
        self.assertNotEqual(result.returncode, 0)

    def test_inventory_detects_mutation_and_extra_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = root / "certificate.json"
            payload.write_text('{"degree": 3}\n')
            write_manifest(root)
            self.assertEqual(verify(root)["files"], 1)
            payload.write_text('{"degree": 1}\n')
            with self.assertRaises(ValueError):
                verify(root)
            payload.write_text('{"degree": 3}\n')
            (root / "unlisted.py").write_text("pass\n")
            with self.assertRaises(ValueError):
                verify(root)

    def test_isomorphism_empty_and_unequal_orders(self):
        self.assertTrue(isomorphic((), ()))
        self.assertFalse(isomorphic((), (0,)))
        self.assertFalse(isomorphic((0,), ()))
        self.assertFalse(isomorphic((0,), (0,0)))
        with self.assertRaises(AssertionError):
            pairwise_nonisomorphic(["A_", "A_"])

    def test_generated_files_and_worktree_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.py").write_text("pass\n")
            write_manifest(root)
            for relative in [".git", ".DS_Store", ".venv/config", "results/notebook/reproduce.ipynb", "build/document/main.log"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("generated metadata")
            self.assertEqual(verify(root)["files"], 1)
            (root / "source.py").write_text("modified\n")
            with self.assertRaises(ValueError):
                verify(root)

    def test_nested_generated_names_are_not_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "input.py").write_text("pass\n")
            write_manifest(root)
            for relative in ["data/build/x.json", "paper/results/x.tex", "data/x.log", "data/quick-verification.json"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("unexpected input")
                with self.assertRaises(ValueError):
                    verify(root)
                path.unlink()

    def test_generated_output_guard(self):
        for path in [ROOT, ROOT / "data/tmp", ROOT / "paper/build/tmp", ROOT / "supplement/figures"]:
            with self.assertRaises(ValueError):
                generated_output(path)
        self.assertEqual(generated_output(ROOT / "results/example"), ROOT / "results/example")

    @unittest.skipUnless(os.name == "posix", "process-group semantics require POSIX")
    def test_timeout_stops_descendant_and_retains_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = str(Path(tmp) / "orphan.txt")
            child = "import time; from pathlib import Path; time.sleep(3); Path(" + repr(marker) + ").write_text('orphan')"
            parent = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); print('started',flush=True); time.sleep(30)"
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                run_process([sys.executable, "-c", parent], capture_output=True, text=True, timeout=2)
            self.assertIn("started", caught.exception.stdout)
            time.sleep(1.2)
            self.assertFalse(Path(marker).exists())

    @unittest.skipUnless(os.name == "posix", "process-group semantics require POSIX")
    def test_timeout_does_not_wait_for_a_detached_pipe_holder(self):
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = Path(tmp) / "child.pid"
            parent = ("import subprocess,sys,time; from pathlib import Path; "
                      "p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)'],start_new_session=True); "
                      "Path(" + repr(str(pidfile)) + ").write_text(str(p.pid)); print(p.pid,flush=True); time.sleep(20)")
            try:
                with self.assertRaises(subprocess.TimeoutExpired) as caught:
                    run_process([sys.executable, "-c", parent], capture_output=True, text=True, timeout=2)
                self.assertIsInstance(caught.exception.stdout, str)
                self.assertEqual(int(caught.exception.stdout.strip()), int(pidfile.read_text()))
            finally:
                if pidfile.exists():
                    try:
                        os.kill(int(pidfile.read_text()), signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_notebook_copy_preserves_distributed_input(self):
        (ROOT / "results").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "results") as tmp:
            output = Path(tmp) / "interactive"
            original = (ROOT / "notebooks/reproduce.ipynb").read_bytes()
            result = command(ROOT / "tools/copy_notebook.py", "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((output / "reproduce.ipynb").read_bytes(), original)
            self.assertNotEqual(command(ROOT / "tools/copy_notebook.py", "--output", output).returncode, 0)
            (output / "reproduce.ipynb").write_text("autosaved interactive output")
            self.assertEqual((ROOT / "notebooks/reproduce.ipynb").read_bytes(), original)

    def test_semantic_checker_rejects_changed_degree(self):
        records = json.loads((ROOT / "finite/certificates/disc_hypotheses.json").read_text())
        records[0]["attaching_degree"] = 1
        with tempfile.TemporaryDirectory() as tmp:
            certificate = Path(tmp) / "changed.json"
            certificate.write_text(json.dumps(records))
            result = command(ROOT / "finite/certificates/check_disc_hypotheses.py", "--certificate", certificate)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("differs", result.stderr)

    def test_semantic_checker_rejects_swapped_membership(self):
        # Recompute byte hashes deliberately: this must fail mathematically.
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "finite"
            shutil.copytree(ROOT / "finite", copied, ignore=shutil.ignore_patterns("__pycache__"))
            table = copied / "data/acyclic_not_strong_14_closure.tsv"
            with table.open(newline="") as stream:
                reader = csv.DictReader(stream, delimiter="\t")
                fields = reader.fieldnames
                records = list(reader)
            first = next(r for r in records if r["I_contractible"] == "1" and r["K4_count"] != "0")
            second = next(r for r in records if r["I_contractible"] == "0" and r["K4_count"] != "0")
            first["I_contractible"], second["I_contractible"] = "0", "1"
            for target, data in [(table, records), (copied / "data/I_not_strong_14_closure.tsv",
                                                 [r for r in records if r["I_contractible"] == "1"])]:
                with target.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
                    writer.writeheader()
                    writer.writerows(data)
            manifest = copied / "integrity_manifest.json"
            data = json.loads(manifest.read_text())
            for record in data["files"]:
                raw = (copied / record["path"]).read_bytes()
                record["bytes"] = len(raw)
                record["sha256"] = hashlib.sha256(raw).hexdigest()
            manifest.write_text(json.dumps(data, indent=2) + "\n")
            (copied / "integrity_manifest.sha256").write_text(hashlib.sha256(manifest.read_bytes()).hexdigest() + "\n")
            byte_check = command(copied / "check_integrity.py")
            self.assertEqual(byte_check.returncode, 0, byte_check.stderr)
            result = command(copied / "data/check_tables.py", "--timeout", os.environ.get("GRAPH_CHECK_TIMEOUT", "60"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("I_contractible", result.stderr)


if __name__ == "__main__":
    unittest.main()
