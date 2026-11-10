#!/usr/bin/env python3
"""Equivalence and regression tests: src/atascadas.c (v1) versus v2/src/atascadas_v2.c (v2).

Usage:  python3 test_equivalence.py --build ../build --out results/v2.4/equivalence.json [--nmax-table 10] [--procs 8]
The report records the SHA-256 and --version of every binary and source it exercised (key "provenance").

Binaries expected in --build: atascadas_v1, atascadas_v2, atascadas_v2_weak (v2 with a 6-bit hash, -DHASH_WEAK_BITS=6),
atascadas_v1_weak (v1 with its hash truncated to 6 bits).  geng (nauty) must be on PATH.

Checks (each one PASS/FAIL in the JSON report; exit status 0 only if all pass):
  T1  --modo tabla, all connected graphs n = 1..nmax: the 13 v1 summary fields are identical for v1 and v2, the
      multisets of stdout lines are identical, v2 reports invalidos=0 errores=0, and (n >= 3) the row equals
      data/raw_classifier_reference.csv.
  T2  --modo atascadas on geng -C -d4 -D(n-2) n, n = 5..10: identical stdout and counters.
  T3  --modo casi on geng -c n, n = 3..9: identical stdout and counters (all zero, as in the paper).
  T4  --modo 2dis_no_1dis on geng -c n, n = 1..9 (expect 0) and on data/strictly_2dis_12.g6 (expect all 20).
  T5  special graphs (G13 x3, G14a/b/c and their one-edge extensions, the 51 stuck graphs, dunce hat D15 and
      D15+{9,12}): I_S decision (traza), icert outcome and cerradura output identical for v1, v2 and v2_weak;
      expected values from the paper.
  T6  --modo verificar on all connected graphs n = 1..8: v2 and v2_weak byte-identical (exact keys make the answer
      independent of the hash); the final 0-Dis/I_SV/I_S of v2 equal those of v1.  Also reports how many graphs
      v1_weak classifies differently from v1 (demonstration of finding H-01; not a pass/fail criterion).
"""
import argparse, collections, csv, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
import provenance  # noqa: E402
V1_FIELDS = ["n", "conexas", "chi1", "aciclicas", "I", "I_indecisas", "I_S", "I_SV", "3-Dis", "2-Dis", "1-Dis",
             "0-Dis", "-1-Dis"]


def g6_decode(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits.extend((v >> (5 - k)) & 1 for k in range(6))
    E = set()
    b = 0
    for j in range(1, n):
        for i in range(j):
            if bits[b]:
                E.add((i, j))
            b += 1
    return n, E


def g6_encode(n, E):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in E or (j, i) in E else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(63 + n)
    for k in range(0, len(bits), 6):
        v = 0
        for x in bits[k:k + 6]:
            v = (v << 1) | x
        out += chr(63 + v)
    return out


def add_edge(s, u, v):
    n, E = g6_decode(s)
    E.add((min(u, v), max(u, v)))
    return g6_encode(n, E)


def run_pipe(geng_args, binary, mode_args, stdin_text=None):
    """geng | binary (or text | binary).  Returns (geng_rc, bin_rc, stdout, stderr_of_binary)."""
    if stdin_text is None:
        g = subprocess.Popen(["geng", "-q"] + geng_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        c = subprocess.Popen([binary] + mode_args, stdin=g.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        g.stdout.close()
        out, err = c.communicate()
        g.wait()
        return g.returncode, c.returncode, out.decode(), err.decode()
    c = subprocess.run([binary] + mode_args, input=stdin_text.encode(), capture_output=True)
    return 0, c.returncode, c.stdout.decode(), c.stderr.decode()


def parse_summary(err):
    line = [l for l in err.splitlines() if l.startswith("n=")][-1]
    return dict(re.findall(r"(\S+?)=(\S+)", line))


def table_run(binary, n, procs):
    """Full --modo tabla over geng -c n, split in res/mod slices; returns summed v1 fields, all stdout lines, extras."""
    mod = procs if n >= 9 else 1
    def one(r):
        args = ["-c", str(n)] + ([f"{r}/{mod}"] if mod > 1 else [])
        return run_pipe(args, binary, ["--modo", "tabla"])
    with ThreadPoolExecutor(max_workers=procs) as ex:
        res = list(ex.map(one, range(mod)))
    tot = collections.Counter()
    extras = collections.Counter()
    lines = []
    rcs = []
    for grc, brc, out, err in res:
        rcs.append((grc, brc))
        s = parse_summary(err)
        for f in V1_FIELDS[1:]:
            tot[f] += int(s[f])
        for f in ("invalidos", "errores", "icert_truncados", "memo_consultas", "memo_colisiones_hash"):
            if f in s:
                extras[f] += int(s[f])
        lines.extend(out.splitlines())
    return dict(tot), sorted(lines), dict(extras), rcs


def load_csv_rows():
    # Read by field name; the raw undecided counter is the final CSV column.
    columns = ["connected", "chi=1", "Z2-acyclic", "I-contractible", "I-undecided",
               "strong I-contractible (J_S)", "J_VS", "3-Dis", "2-Dis", "1-Dis", "0-Dis", "(-1)-Dis"]
    with (REPO / "data/raw_classifier_reference.csv").open(newline="") as stream:
        return {int(row["n"]): [int(row[key]) for key in columns] for row in csv.DictReader(stream)}


def csv_from_fields(t):
    # CSV order: connected, chi=1, Z2-acyclic, I, I-undecided, J_S, J_VS, 3-Dis, 2-Dis, 1-Dis, 0-Dis, (-1)-Dis
    return [t["conexas"], t["chi1"], t["aciclicas"], t["I"], t["I_indecisas"], t["I_S"], t["I_SV"], t["3-Dis"],
            t["2-Dis"], t["1-Dis"], t["0-Dis"], t["-1-Dis"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=str(HERE.parent / "build"))
    ap.add_argument("--out", default=str(HERE / "results" / "v2.4" / "equivalence.json"))
    ap.add_argument("--nmax-table", type=int, default=10)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--weak-nmax", type=int, default=7)
    a = ap.parse_args()
    B = Path(a.build)
    v1, v2, v2w, v1w = (str(B / x) for x in ("atascadas_v1", "atascadas_v2", "atascadas_v2_weak", "atascadas_v1_weak"))
    report = {"started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "started_utc": provenance.utc_now(), "checks": []}
    report["provenance"] = provenance.record(
        binaries=[(v1, None), (v2, ["--version"]), (v2w, ["--version"]), (v1w, None)],
        sources=[HERE.parent / "src" / "atascadas_v2.c", REPO / "src" / "atascadas.c", B / "atascadas_v1_weak.c",
                 REPO / "data" / "raw_classifier_reference.csv", Path(__file__)],
        tools=["geng"])

    def check(name, ok, **detail):
        report["checks"].append({"name": name, "pass": bool(ok), **detail})
        print(("PASS " if ok else "FAIL ") + name, json.dumps(detail)[:300], flush=True)

    # ---------------- T1 tabla
    csv = load_csv_rows()
    for n in range(1, a.nmax_table + 1):
        t1, l1, _, rc1 = table_run(v1, n, a.procs)
        t2, l2, x2, rc2 = table_run(v2, n, a.procs)
        ok = t1 == t2 and l1 == l2 and x2.get("invalidos", 0) == 0 and x2.get("errores", 0) == 0
        ok = ok and all(g == 0 and b == 0 for g, b in rc1 + rc2)
        if n >= 3:
            ok = ok and csv_from_fields(t2) == csv[n]
        check(f"T1 tabla n={n}", ok, v2=t2, v2_extras=x2, csv=csv.get(n), stdout_lines=len(l2))

    # ---------------- T2 atascadas
    for n in range(5, 11):
        args = ["-C", "-d4", f"-D{n - 2}", str(n)]
        r1 = run_pipe(args, v1, ["--modo", "atascadas"])
        r2 = run_pipe(args, v2, ["--modo", "atascadas"])
        s1, s2 = parse_summary(r1[3]), parse_summary(r2[3])
        keys = ["n", "total", "pasa_cono", "pasa_chi", "pasa_vecindades", "pasa_aristas", "encontradas"]
        ok = r1[2] == r2[2] and all(s1[k] == s2[k] for k in keys) and r2[1] == 0 and s2["invalidos"] == "0"
        check(f"T2 atascadas n={n}", ok, v2={k: s2[k] for k in keys})

    # ---------------- T3 casi
    for n in range(3, 10):
        r1 = run_pipe(["-c", str(n)], v1, ["--modo", "casi"])
        r2 = run_pipe(["-c", str(n)], v2, ["--modo", "casi"])
        s1, s2 = parse_summary(r1[3]), parse_summary(r2[3])
        ok = r1[2] == r2[2] and s1["encontradas"] == s2["encontradas"] == "0" and s1["total"] == s2["total"]
        check(f"T3 casi n={n}", ok and r2[1] == 0, total=s2["total"], encontradas=s2["encontradas"])

    # ---------------- T4 2dis_no_1dis
    for n in range(1, 10):
        r1 = run_pipe(["-c", str(n)], v1, ["--modo", "2dis_no_1dis"])
        r2 = run_pipe(["-c", str(n)], v2, ["--modo", "2dis_no_1dis"])
        ok = r1[2] == r2[2] == "" and r2[1] == 0
        check(f"T4 2dis_no_1dis n={n}", ok)
    d21 = [l.split()[0] for l in open(REPO / "data" / "strictly_2dis_12.g6") if l.strip() and not l.startswith("#")]
    txt = "".join(s + "\n" for s in d21)
    r1 = run_pipe(None, v1, ["--modo", "2dis_no_1dis"], txt)
    r2 = run_pipe(None, v2, ["--modo", "2dis_no_1dis"], txt)
    ok = r1[2] == r2[2] and len(r2[2].splitlines()) == len(d21) == 20 and r2[1] == 0
    check("T4 2dis_no_1dis 20 graphs of order 12", ok, found=len(r2[2].splitlines()))

    # ---------------- T5 special graphs
    def g6list(fname):
        return [l.split()[0] for l in open(REPO / "data" / fname) if l.strip() and not l.startswith("#")]
    G13 = g6list("acyclic_not_strong_13.g6")
    G14 = {"G14a": "M?b@bFHNEk@~|k}U?", "G14b": "M?B@thku?~Lylk}[?", "G14c": "M?r@d`ifbiFfo}~o?"}
    ext = {"G14a": (0, 1), "G14b": (0, 3), "G14c": (2, 3)}
    D15 = g6list("dunce_hat_15.g6")[0]
    stuck51 = g6list("stuck_14_K4free.g6")
    special = {f"G13_{i}": s for i, s in enumerate(G13)}
    special.update(G14)
    special.update({k + "+{%d,%d}" % ext[k]: add_edge(s, *ext[k]) for k, s in G14.items()})
    special["D15"] = D15
    special["D15+{9,12}"] = add_edge(D15, 9, 12)
    expected_IS = {k: (("+" in k)) for k in special}       # only the one-edge extensions are in I_S
    txt = "".join(s + "\n" for s in special.values())
    outs = {}
    for name, b in (("v1", v1), ("v2", v2), ("v2_weak", v2w)):
        tr = run_pipe(None, b, ["--modo", "traza"], txt)[2]
        blocks = tr.split("== traza I_S de ")[1:]
        outs[name] = [("NO es I_S" not in blk) for blk in blocks]
    got = dict(zip(special.keys(), outs["v2"]))
    ok = outs["v1"] == outs["v2"] == outs["v2_weak"] and got == expected_IS
    check("T5 traza I_S of special graphs", ok, v2=got)
    txt51 = "".join(s + "\n" for s in stuck51)
    r = {name: run_pipe(None, b, ["--modo", "traza"], txt51)[2].count("NO es I_S") for name, b in
         (("v1", v1), ("v2", v2), ("v2_weak", v2w))}
    check("T5 traza: the 51 stuck graphs are not in I_S", r["v1"] == r["v2"] == r["v2_weak"] == 51, counts=r)

    def icert_outcomes(b, text):
        o = run_pipe(None, b, ["--modo", "icert"], text)[2]
        res = []
        for blk in o.split("== ")[1:]:
            if "I-CONTRAIBLE" in blk:
                res.append("CERT " + blk.split("I4:")[1].split("\n")[0].strip())
            elif "INDECISO" in blk:
                res.append("TRUNC")
            else:
                res.append("NONE")
        return res
    texts = {"special": txt, "stuck51": txt51}
    for tn, tx in texts.items():
        o1, o2, o2w = icert_outcomes(v1, tx), icert_outcomes(v2, tx), icert_outcomes(v2w, tx)
        check(f"T5 icert outcomes ({tn})", o1 == o2 == o2w, v2=collections.Counter(x.split()[0] for x in o2))
    for k in ("G14a", "G14b", "G14c", "D15"):
        t = special[k] + "\n"
        c1 = sorted(run_pipe(None, v1, ["--modo", "cerradura"], t)[2].splitlines())
        c2 = sorted(run_pipe(None, v2, ["--modo", "cerradura"], t)[2].splitlines())
        c2w = sorted(run_pipe(None, v2w, ["--modo", "cerradura"], t)[2].splitlines())
        trunc = any("TRUNCADA" in l for l in c2)
        same = (c1 == c2 == c2w) if not trunc else (c2 == c2w)
        check(f"T5 cerradura {k}", same, lines=len(c2), truncated=trunc,
              n_IS=sum(l.startswith("I_S ") for l in c2), n_NOIS=sum(l.startswith("NO_I_S ") for l in c2))

    # ---------------- T6 verificar on all connected graphs n <= 8
    def final_flags(o):
        return re.findall(r"0-Dis=(\d)  I_SV=(\d)  I_S=(\d)", o)
    diff_v1w = 0
    total = 0
    for n in range(1, 9):
        r1 = run_pipe(["-c", str(n)], v1, ["--modo", "verificar"])
        r2 = run_pipe(["-c", str(n)], v2, ["--modo", "verificar"])
        f1, f2 = final_flags(r1[2]), final_flags(r2[2])
        ok = f1 == f2 and len(f2) > 0 and r2[1] == 0
        info = {"graphs": len(f2)}
        if n <= a.weak_nmax:   # a 6-bit hash makes every probe chain long: the weak builds are run only up to weak_nmax
            r2w = run_pipe(["-c", str(n)], v2w, ["--modo", "verificar"])
            r1w = run_pipe(["-c", str(n)], v1w, ["--modo", "verificar"])
            f1w = final_flags(r1w[2])
            ok = ok and r2[2] == r2w[2] and r2w[1] == 0
            nd = sum(1 for x, y in zip(f1, f1w) if x != y)
            diff_v1w += nd
            total += len(f2)
            info.update(v2_weak_identical=r2[2] == r2w[2],
                        v2_weak_hash_collisions=int(parse_summary(r2w[3])["memo_colisiones_hash"]),
                        v1_weak_misclassified=nd)
        check(f"T6 verificar n={n}", ok, **info)
    report["H01_demo"] = {"graphs": total, "v1_with_6bit_hash_misclassified": diff_v1w}
    report["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    report["finished_utc"] = provenance.utc_now()
    report["all_pass"] = all(c["pass"] for c in report["checks"])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(provenance.check_portable(json.dumps(report, indent=1) + "\n"))
    print("ALL PASS" if report["all_pass"] else "SOME CHECKS FAILED", "H01 demo:", report["H01_demo"])
    sys.exit(0 if report["all_pass"] else 1)


if __name__ == "__main__":
    main()
