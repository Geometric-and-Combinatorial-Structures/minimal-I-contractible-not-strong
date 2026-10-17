#!/usr/bin/env python3
"""Input-robustness tests of atascadas_v2 (findings H-18, H-19, H-20 of the external audit).

Usage: python3 test_robustness.py --build ../build --out results/v2.2/robustness.json
Each case fixes the expected exit status of v2 and, where relevant, the counted totals or a required substring of the
output.  The behaviour of v1 (src/atascadas.c) on the same input is recorded for the report but is not checked.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import provenance  # noqa: E402

K16 = "O" + "~" * 20            # complete graph on 16 vertices (120 bits = 20 characters)
CASES = [
    # name, mode, stdin, expected exit, expected summary fields (subset), required substring in stdout+stderr
    ("valid K3", "tabla", "Bw\n", 0, {"conexas": "1", "I_S": "1", "invalidos": "0"}, None),
    ("header on same line (H-18)", "tabla", ">>graph6<<Bw\n", 0, {"conexas": "1"}, None),
    ("header-only line then graph", "tabla", ">>graph6<<\nBw\n", 0, {"conexas": "1"}, None),
    ("CRLF line ending", "tabla", "Bw\r\n", 0, {"conexas": "1"}, None),
    ("truncated record M (H-18)", "tabla", "M\n", 3, {"conexas": "0", "invalidos": "1"}, "g6 inválido"),
    ("character above 126", "tabla", "B\x7f\n", 3, {"invalidos": "1"}, None),
    ("character below 63", "tabla", "B!\n", 3, {"invalidos": "1"}, None),
    ("non-zero padding bits", "tabla", "Bx\n", 3, {"invalidos": "1"}, None),
    ("order 0", "tabla", "?\n", 3, {"invalidos": "1"}, None),
    ("order 17 (> MAXN)", "tabla", "P" + "~" * 23 + "\n", 3, {"invalidos": "1"}, None),
    ("empty line in counting mode", "tabla", "Bw\n\nBw\n", 3, {"conexas": "2", "invalidos": "1"}, None),
    ("line longer than buffer", "tabla", "B" * 5000 + "\nBw\n", 3, {"conexas": "1", "invalidos": "1"},
     "demasiado largo"),
    ("extra text in counting mode", "tabla", "Bw extra\n", 3, {"conexas": "0", "invalidos": "1"}, None),
    ("sparse6 record", "tabla", ":Bw\n", 3, {"invalidos": "1"}, None),
    ("mixed orders", "tabla", "Bw\nC~\n", 5, {"conexas": "1"}, "orden distinto"),
    ("disconnected input in tabla", "tabla", "B_\n", 5, {"conexas": "0"}, "no conexa"),
    ("empty input", "tabla", "", 0, {"n": "0", "conexas": "0"}, None),
    ("K16 in tabla (H-19)", "tabla", K16 + "\n", 0, {"n": "16", "conexas": "1", "aciclicas": "1", "-1-Dis": "1"},
     None),
    ("K16 in verificar (H-19)", "verificar", K16 + "\n", 0, {}, "aciclica=1"),
    ("C4 is not stuck (H-20)", "verificar", "Cl\n", 0, {}, "sin_movimientos=1  atascada=0"),
    ("comments and text allowed in verificar", "verificar", "# comment\n\nCl label\n", 0, {}, "== Cl"),
    ("atascadas mode rejects invalid", "atascadas", "M\n", 3, {"total": "0", "invalidos": "1"}, None),
    ("unknown mode", "foo", "Bw\n", 1, {}, "modo desconocido"),
    ("unknown option", "tabla --bar", "Bw\n", 1, {}, "uso:"),
    ("invalid --prof", "tabla --prof -1", "Bw\n", 1, {}, "uso:"),
]


def run(binary, mode, text):
    args = [binary, "--modo"] + mode.split()
    p = subprocess.run(args, input=text.encode("latin-1"), capture_output=True, timeout=120)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def summary(err):
    ls = [l for l in err.splitlines() if l.startswith("n=")]
    return dict(re.findall(r"(\S+?)=(\S+)", ls[-1])) if ls else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=str(HERE.parent / "build"))
    ap.add_argument("--out", default=str(HERE / "results" / "v2.2" / "robustness.json"))
    a = ap.parse_args()
    v1 = str(Path(a.build) / "atascadas_v1")
    v2 = str(Path(a.build) / "atascadas_v2")
    started = provenance.utc_now()
    prov = provenance.record(binaries=[(v1, None), (v2, ["--version"])],
                             sources=[HERE.parent / "src" / "atascadas_v2.c", Path(__file__)])
    out = []
    for name, mode, text, ec, fields, sub in CASES:
        rc, so, se = run(v2, mode, text)
        s = summary(se)
        ok = rc == ec and all(s.get(k) == v for k, v in fields.items())
        if sub is not None:
            ok = ok and (sub in so or sub in se)
        try:
            rc1, so1, se1 = run(v1, mode, text)
            v1info = {"exit": rc1, "summary": se1.strip().splitlines()[-1][:160] if se1.strip() else ""}
        except Exception as e:  # noqa: BLE001
            v1info = {"error": str(e)[:100]}
        out.append({"case": name, "pass": ok, "v2_exit": rc, "expected_exit": ec, "v2_summary": s, "v1": v1info})
        print(("PASS " if ok else "FAIL ") + name, "v2 exit", rc, "| v1:", v1info, flush=True)
    res = {"all_pass": all(c["pass"] for c in out), "cases": out, "started_utc": started,
           "finished_utc": provenance.utc_now(), "provenance": prov}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(provenance.check_portable(json.dumps(res, indent=1, ensure_ascii=False) + "\n"))
    print("ALL PASS" if res["all_pass"] else "SOME CASES FAILED")
    sys.exit(0 if res["all_pass"] else 1)


if __name__ == "__main__":
    main()
