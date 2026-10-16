#!/usr/bin/env python3
"""Final collection of the n = 14 K4-free full table (read-only on the run directory).

Rules (see yuca/README.md):
  * A slice r is DONE iff it appears in listas_t{r % 7}.txt.  Every r in 0..MOD-1 must be done.
  * Its result line is out/<r//1000>/<r>.log (main fronts) and/or out_m/<r//1000>/<r>.log, the latter only
    if r is listed in some listas_m_*.txt (middle fronts).  A slice processed twice must give identical lines.
  * Each slice is counted exactly once.  The found-graph registries enc_t*.txt (main) and enc_m_t*.txt
    (middle) are merged; their de-duplicated line counts must equal the sums of the counters
    I_indecisas (lines ACICLICA_NO_IS_INDECISA) and I - I_S (lines I_NO_IS).
Output: a report on stdout (key=value), plus files faltantes.txt, conflictos.txt, duplicadas.txt,
encontradas_unicas.txt in --out.   Python 3 standard library only.
Usage: recolectar_n14_tabla.py --base DIR --out DIR [--mod 2000000] [--nt 7] [--jobs 8]
"""
import argparse, glob, os, re, sys
from concurrent.futures import ProcessPoolExecutor

KEYS = ["conexas", "chi1", "aciclicas", "I", "I_indecisas", "I_S", "I_SV", "3-Dis", "2-Dis", "1-Dis", "0-Dis", "-1-Dis"]
LINE = re.compile(r"^n=(\d+) " + " ".join(re.escape(k) + r"=(\d+)" for k in KEYS) + r"$")

def read_set(path):
    s = set()
    if os.path.exists(path):
        with open(path) as f:
            for x in f:
                x = x.strip()
                if x: s.add(int(x))
    return s

def parse(path):
    try:
        with open(path) as f: txt = f.read()
    except FileNotFoundError:
        return None
    lines = [l for l in txt.splitlines() if l.strip()]
    if len(lines) != 1: return ("BAD", txt)
    m = LINE.match(lines[0])
    if not m: return ("BAD", txt)
    return ("OK", lines[0], int(m.group(1)), [int(g) for g in m.groups()[1:]])

def work(args):
    base, rs, medio = args
    out = []
    for r in rs:
        d = str(r // 1000)
        a = parse(os.path.join(base, "out", d, f"{r}.log"))
        b = parse(os.path.join(base, "out_m", d, f"{r}.log")) if r in medio else None
        out.append((r, a, b))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--mod", type=int, default=2000000); ap.add_argument("--nt", type=int, default=7)
    ap.add_argument("--n", type=int, default=14); ap.add_argument("--jobs", type=int, default=8)
    A = ap.parse_args(); os.makedirs(A.out, exist_ok=True)
    reg = [read_set(os.path.join(A.base, f"listas_t{t}.txt")) for t in range(A.nt)]
    bad_res = sum(1 for t in range(A.nt) for r in reg[t] if r % A.nt != t or not (0 <= r < A.mod))
    done = set().union(*reg)
    medio = set()
    for p in sorted(glob.glob(os.path.join(A.base, "listas_m_*.txt"))): medio |= read_set(p)
    faltantes = [r for r in range(A.mod) if r not in done]
    rs = sorted(done); chunk = 5000
    tasks = [(A.base, rs[i:i + chunk], medio) for i in range(0, len(rs), chunk)]
    tot = [0] * len(KEYS); usadas = 0; conflictos = []; duplicadas = []; sin_log = []; malos = []
    with ProcessPoolExecutor(max_workers=A.jobs) as ex:
        for res in ex.map(work, tasks):
            for r, a, b in res:
                cand = [x for x in (a, b) if x is not None]
                if any(x[0] == "BAD" for x in cand): malos.append(r); continue
                if not cand: sin_log.append(r); continue
                if len(cand) == 2:
                    duplicadas.append(r)
                    if cand[0][1] != cand[1][1]: conflictos.append(r); continue
                ok = cand[0]
                if ok[2] != A.n: malos.append(r); continue
                tot = [s + v for s, v in zip(tot, ok[3])]; usadas += 1
    # found graphs
    enc = {}
    for p in sorted(glob.glob(os.path.join(A.base, "enc_t*.txt")) + glob.glob(os.path.join(A.base, "enc_m_t*.txt"))):
        with open(p) as f:
            for l in f:
                l = l.strip()
                if l: enc.setdefault(l.split()[0], set()).add(l)
    T = dict(zip(KEYS, tot))
    checks = {
        "residuo_o_rango_incorrecto": bad_res, "faltantes": len(faltantes), "registradas_sin_log": len(sin_log),
        "logs_malformados": len(malos), "conflictos_entre_copias": len(conflictos), "rebanadas_contadas": usadas,
        "procesadas_dos_veces": len(duplicadas),
        "indecisas_lineas_unicas": len(enc.get("ACICLICA_NO_IS_INDECISA", ())), "indecisas_contador": T["I_indecisas"],
        "I_no_IS_lineas_unicas": len(enc.get("I_NO_IS", ())), "I_no_IS_contador": T["I"] - T["I_S"],
        "lineas_ERROR": sum(len(v) for k, v in enc.items() if k.startswith("ERROR")),
        "inclusiones_ok": int(T["-1-Dis"] <= T["0-Dis"] <= T["1-Dis"] <= T["2-Dis"] <= T["3-Dis"] <= T["I_SV"] <= T["I_S"] <= T["I"] <= T["aciclicas"] <= T["chi1"] <= T["conexas"]),
    }
    completo = (checks["faltantes"] == 0 and checks["registradas_sin_log"] == 0 and checks["logs_malformados"] == 0
                and checks["conflictos_entre_copias"] == 0 and bad_res == 0 and usadas == A.mod
                and checks["indecisas_lineas_unicas"] == checks["indecisas_contador"]
                and checks["I_no_IS_lineas_unicas"] == checks["I_no_IS_contador"] and checks["lineas_ERROR"] == 0
                and checks["inclusiones_ok"] == 1)
    for name, data in [("faltantes.txt", faltantes), ("conflictos.txt", conflictos), ("duplicadas.txt", duplicadas),
                       ("registradas_sin_log.txt", sin_log), ("logs_malformados.txt", malos)]:
        with open(os.path.join(A.out, name), "w") as f: f.write("".join(f"{r}\n" for r in data))
    with open(os.path.join(A.out, "encontradas_unicas.txt"), "w") as f:
        for k in sorted(enc):
            for l in sorted(enc[k]): f.write(l + "\n")
    print(f"n={A.n} " + " ".join(f"{k}={T[k]}" for k in KEYS))
    for k, v in checks.items(): print(f"{k}={v}")
    print(f"RESULTADO={'COMPLETO_Y_CONSISTENTE' if completo else 'INCOMPLETO_O_INCONSISTENTE'}")
    return 0 if completo else 1

if __name__ == "__main__":
    sys.exit(main())
