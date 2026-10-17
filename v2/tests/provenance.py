"""Provenance record attached to every v2.1/v2.2 test result.

Each result file says which binaries, sources and tools it exercised: path, SHA-256, size, modification time
and, for the classifier binaries and the nauty tools, the first line printed by --version.  Times are UTC.
Paths are recorded relative to the repository root; for a file outside the repository only its name is recorded, so
a result file never carries the directories of the machine that produced it (check_portable enforces this).
Standard library only.
"""
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]      # v2/tests/provenance.py -> repository root


def display_path(path):
    """Path relative to the repository root; outside the repository, only the file name."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return f"{p.name} (outside the repository)"


def _display_arg(arg):
    """A command-line argument as it is recorded.  v2.2 (H-35 of round 3): besides an existing path, any absolute path
    (also one that does not exist yet, e.g. a new --out file) and the value of --option=PATH are shown like
    display_path, so the recorded argv never carries the directories of the machine and check_portable never refuses
    a result only because of where it was asked to be written."""
    if arg.startswith("--") and "=" in arg:
        opt, _, val = arg.partition("=")
        return opt + "=" + _display_arg(val)
    try:
        if os.path.isabs(arg) or os.path.exists(arg):
            return display_path(arg)
    except (OSError, ValueError):
        pass
    return arg


def check_portable(text):
    """Refuse a result text that contains the absolute path of the repository or of the home directory."""
    for local in {str(REPO), str(Path.home())}:
        if len(local) > 1 and local in text:
            raise SystemExit("result would record a local path (repository root or home directory); refusing to write it")
    return text


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _first_line(cmd):
    try:
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
    except Exception as e:  # noqa: BLE001 - recorded, not raised
        return {"error": str(e)[:200]}
    text = (p.stdout + p.stderr).decode("utf-8", "replace").strip()
    return {"exit": p.returncode, "first_line": text.splitlines()[0][:200] if text else ""}


def file_record(path, version_args=None):
    """version_args: arguments that make the program print its version, or None to skip (v1 has no --version)."""
    p = Path(path)
    if not p.exists():
        return {"path": display_path(p), "missing": True}
    st = p.stat()
    r = {"path": display_path(p), "sha256": sha256(p), "bytes": st.st_size,
         "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime))}
    if version_args is not None:
        r["version"] = _first_line([str(p)] + list(version_args))
    return r


def record(binaries=(), sources=(), tools=()):
    """binaries: (path, version_args or None); sources: paths hashed only; tools: names looked up on PATH."""
    out = {"recorded_utc": utc_now(), "python": sys.version.split()[0], "platform": platform.platform(),
           "argv": [_display_arg(x) for x in sys.argv]}
    out["binaries"] = {Path(b).name: file_record(b, va) for b, va in binaries}
    out["sources"] = {Path(s).name: file_record(s) for s in sources}
    out["tools"] = {}
    for name in tools:
        w = shutil.which(name)
        out["tools"][name] = file_record(w, ["--version"]) if w else {"missing": True}
    gcc = shutil.which("gcc")
    out["gcc"] = _first_line([gcc, "--version"]) if gcc else {"missing": True}
    return out
