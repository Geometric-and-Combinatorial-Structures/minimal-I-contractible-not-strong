#!/usr/bin/env python3
"""Check article identity, migration coverage, local links and distributed metadata."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import subprocess
import shutil
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from integrity import payload


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-git-baseline", action="store_true")
    args = parser.parse_args()
    provenance = json.loads((ROOT / "PROVENANCE.json").read_text())
    article = json.loads((ROOT / provenance["article_identity"]).read_text())["files"]
    for name, digest in article.items():
        assert hashlib.sha256((ROOT / "paper" / name).read_bytes()).hexdigest() == digest, name
    with (ROOT / provenance["git_migration"]).open(newline="") as stream:
        migration = list(csv.DictReader(stream, delimiter="\t"))
    names = [r["old_path"] for r in migration]
    assert len(names) == len(set(names)) == 212
    moved = [r["new_path"] for r in migration if r["disposition"] == "moved"]
    assert len(moved) == len(set(moved))
    for row in migration:
        assert row["disposition"] in {"kept", "moved", "superseded", "removed"}
        assert bool(row["new_path"]) == (row["disposition"] != "removed"), row
        if row["disposition"] != "removed":
            destination = ROOT / row["new_path"]
            assert destination.is_file() or (row["new_path"] == "finite/certificates" and destination.is_dir()), row
        if row["disposition"] in {"kept", "moved"}:
            assert git_blob((ROOT / row["new_path"]).read_bytes()) == row["old_blob"], row
        if row["disposition"] == "moved":
            assert row["old_blob"] != "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    baseline_checked = False
    baseline_reason = "No Git metadata (source archive); snapshot inventory checked"
    git_available = shutil.which("git") is not None
    if (ROOT / ".git").exists() and not git_available:
        baseline_reason = "Git unavailable; snapshot inventory checked"
    if (ROOT / ".git").exists() and git_available:
        probe = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e",
                                provenance["base_commit"] + "^{tree}"], capture_output=True, text=True)
        available = probe.returncode == 0
        if not available:
            shallow = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--is-shallow-repository"], capture_output=True, text=True)
            if shallow.returncode == 0 and shallow.stdout.strip() == "true":
                baseline_reason = "Baseline absent from shallow history; use git fetch --unshallow for this extra comparison"
            else:
                baseline_reason = "Historical baseline unavailable: " + (probe.stderr.strip() or "Git object probe failed")
    else:
        available = False
    if available:
        proc = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "-z", provenance["base_commit"]],
                              capture_output=True, check=True)
        old = {}
        for item in proc.stdout.split(b"\0"):
            if item:
                head, name = item.split(b"\t")
                mode, kind, sha = head.decode().split()
                old[name.decode()] = (sha, mode)
        assert old == {r["old_path"]: (r["old_blob"], r["old_mode"]) for r in migration}
        baseline_checked = True
        baseline_reason = "Complete baseline tree compared"
    if args.require_git_baseline and not baseline_checked:
        parser.error(baseline_reason)
    selection = json.loads((ROOT / provenance["selection_migration"]).read_text())
    assert len(selection) == len({r["source_path"] for r in selection}) == 212
    for row in selection:
        if row["disposition"] == "unchanged":
            assert hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest() == row["source_sha256"], row
        elif row["disposition"] == "updated":
            assert (ROOT / row["destination"]).is_file(), row
        else:
            assert row["disposition"] == "omitted" and row["destination"] is None
    links = 0
    for name, path in payload(ROOT):
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
                target = match.group(1).split("#")[0]
                if not target or re.match(r"^[a-z]+:", target):
                    continue
                assert (path.parent / unquote(target)).exists(), (name, target)
                links += 1
        if path.suffix not in {".pdf", ".png"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            assert not re.search(r"/(?:home|Users)/[A-Za-z][^/\s]+/", text), name
            assert not re.search(r"sk-ant-[A-Za-z0-9_-]{20,}", text), name
            assert not re.search(r"(?:ghp_|github_pat_)[A-Za-z0-9_]{30,}", text), name
            assert "-----BEGIN " + "OPENSSH PRIVATE KEY-----" not in text, name
    closure = json.loads((ROOT / "verification/closures51/run.json").read_text())
    assert closure["PASS"] and closure["classifier_exit"] == 0 and closure["exact_class_sets_equal"]
    assert closure["non_strong_isomorphism_classes"] == closure["reference_classes"] == 2271
    for name, digest in closure["inputs"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    print(json.dumps({"article_files_unchanged": len(article), "old_git_files": len(migration),
        "baseline_tree_checked": baseline_checked, "baseline_tree_reason": baseline_reason,
        "imported_selection_files": len(selection), "closure_regeneration_inputs_unchanged": True,
        "local_markdown_links": links, "distributed_metadata_checked": True}, indent=2))


if not __debug__:
    raise RuntimeError("Run without -O")
if __name__ == "__main__":
    main()
