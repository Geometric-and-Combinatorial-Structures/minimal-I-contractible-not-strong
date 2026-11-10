"""Whole-repository byte inventory. Hashes establish consistency, not authorship."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "SHA256SUMS.txt"
IGNORED_DIRS = {"__pycache__", ".ipynb_checkpoints"}
IGNORED_PATHS = {".git", "build", "results", ".venv", "v2/build", "v2/tests/results"}
IGNORED_FILES = {".DS_Store"}
BUILD_SUFFIXES = (".pyc", ".pyo", ".o", ".aux", ".log", ".blg", ".out", ".toc",
                  ".brf", ".fls", ".fdb_latexmk", ".synctex.gz")


def payload(root):
    """All distributed files; generated directories are deliberately excluded."""
    root = Path(root)
    out = []
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            p = Path(parent) / name
            if name not in IGNORED_DIRS and p.relative_to(root).as_posix() not in IGNORED_PATHS and p.is_symlink():
                raise ValueError("Symbolic link in source tree: " + str(p.relative_to(root)))
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and (Path(parent) / d).relative_to(root).as_posix() not in IGNORED_PATHS)
        for name in sorted(files):
            p = Path(parent) / name
            relative = p.relative_to(root).as_posix()
            generated = (name.endswith((".pyc", ".pyo")) or
                         (relative.startswith(("paper/", "supplement/")) and name.endswith(BUILD_SUFFIXES)))
            if (relative != MANIFEST and relative not in IGNORED_PATHS and name not in IGNORED_FILES and
                    relative not in {"src/atascadas", "quick-verification.json"} and not generated):
                out.append((relative, p))
    return sorted(out)


def write_manifest(root):
    lines = [hashlib.sha256(p.read_bytes()).hexdigest() + "  " + name
             for name, p in payload(root)]
    (Path(root) / MANIFEST).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def verify(root=ROOT):
    root = Path(root)
    expected = {}
    for line in (root / MANIFEST).read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise ValueError("Malformed SHA256SUMS.txt record")
        digest, name = match.groups()
        p = Path(name)
        if p.is_absolute() or ".." in p.parts or p.as_posix() != name or name in expected:
            raise ValueError("Unsafe or repeated manifest path: " + name)
        expected[name] = digest
    actual = dict(payload(root))
    if set(actual) != set(expected):
        raise ValueError("Source inventory differs: " + ", ".join(sorted(set(actual) ^ set(expected))))
    for name, p in actual.items():
        if hashlib.sha256(p.read_bytes()).hexdigest() != expected[name]:
            hint = (" Run an interactive notebook copy under results/; keep the distributed notebook unchanged."
                    if name.endswith(".ipynb") else "")
            raise ValueError("Source bytes differ: " + name + hint)
    return {"files": len(actual), "all_bytes_match": True,
            "manifest_sha256": hashlib.sha256((root / MANIFEST).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="maintainer action: replace the current inventory")
    args = parser.parse_args()
    try:
        result = {"files_written": write_manifest(ROOT)} if args.write else verify()
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
