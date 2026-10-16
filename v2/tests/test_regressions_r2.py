#!/usr/bin/env python3
"""Regression tests for the findings of round 2 of the external audit (H-18, H-22, H-23, H-24, H-25, H-29).

The cases reproduce the auditor's adversarial scripts (AUDIT_OUT/ronda2/scripts/r2_code_adversarial.py,
r2_pipeline_adversarial2.py, r2_pipeline_extra.py) with the expected outcome of each one, adapted only where v2.1
changes the interface on purpose (summary version v2.1, the icert_truncados key of mode tabla, new init options).

Usage: python3 tests/test_regressions_r2.py --work DIR [--out results/v2.1/regressions_r2.json]
       [--bin BINARY] [--sections classifier,slice,receipt,campaign]
Requires gcc, geng and labelg (nauty) on PATH, and build/atascadas_v2 from ./build.sh.
Exit status 0 only if every case behaves as stated.
"""
import argparse, concurrent.futures, copy, importlib.util, json, os, shlex, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import provenance  # noqa: E402
V2 = HERE.parent
REPO = V2.parent
DRIVER = V2 / "pipeline" / "campana_v2.py"
SOURCE = V2 / "src" / "atascadas_v2.c"
BIN = V2 / "build" / "atascadas_v2"
GENG = shutil.which("geng")
LABELG = shutil.which("labelg")


def geng_pins(geng):
    """--expect-geng-version (the token printed by geng --version) and --expect-geng-sha256 for this geng."""
    import hashlib, re
    out = subprocess.run([str(geng), "--version"], capture_output=True, text=True)
    m = re.search(r"version\s+([0-9]+\.[0-9]+)", out.stdout + out.stderr)
    h = hashlib.sha256(Path(geng).read_bytes()).hexdigest()
    return ["--expect-geng-version", m.group(1) if m else "none", "--expect-geng-sha256", h]
spec = importlib.util.spec_from_file_location("campana", DRIVER)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
RESULTS = []


def case(group, name, ok, **info):
    RESULTS.append({"group": group, "case": name, "pass": bool(ok), **info})
    print(("PASS " if ok else "FAIL ") + f"[{group}] {name}", json.dumps(info, default=str)[:200], flush=True)


def drv(*args):
    p = subprocess.run([sys.executable, str(DRIVER)] + [str(a) for a in args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def init(root, n=3, mod=2, workers=1, mode="tabla", geng=GENG, geng_args="-c", source=SOURCE, extra=(), pin=True):
    """pin=False leaves out the geng pins, so a case can pass its own (or none)."""
    return drv("init", "--root", root, "--n", n, "--mod", mod, "--workers", workers, "--mode", mode, "--geng", geng,
               f"--geng-args={geng_args}", "--source", source, *(geng_pins(geng) if pin else []), *extra)


# --------------------------------------------------------------------------------------------- classifier (H-18, H-25)
def classifier_cases(W):
    def run(name, args, data, want, redirect=None):
        kw = {}
        if redirect:
            full = open("/dev/full", "wb")
            kw = {"stdout": full if redirect == "stdout" else subprocess.PIPE,
                  "stderr": full if redirect == "stderr" else subprocess.PIPE}
        else:
            kw = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
        p = subprocess.run([str(BIN)] + args, input=data, **kw)
        case("classifier", name, p.returncode == want, exit=p.returncode, expected=want)
    for suffix in (b"\x00", b"\x00garbage", b"\x00\xff"):
        run("NUL without final newline " + suffix.hex(), ["--modo", "tabla"], b"Bw" + suffix, 3)
    run("NUL inside a terminated line", ["--modo", "tabla"], b"Bw\x00bad\nBw\n", 3)
    run("valid line without final newline", ["--modo", "tabla"], b"Bw", 3)
    run("inline header without final newline", ["--modo", "tabla"], b">>graph6<<Bw", 3)
    run("stdout write error (/dev/full)", ["--modo", "verificar"], b"Bw\n", 6, "stdout")
    run("stderr write error (/dev/full)", ["--modo", "tabla"], b"Bw\n", 6, "stderr")
    run("--prof empty", ["--modo", "icert", "--prof", ""], b"Bw\n", 1)
    run("--prof with a blank", ["--modo", "icert", "--prof", " 3"], b"Bw\n", 1)
    run("--prof 2 accepted", ["--modo", "icert", "--prof", "2"], b"Bw\n", 0)
    run("valid input accepted", ["--modo", "tabla"], b"Bw\nBo\n", 0)
    run("header-only line accepted", ["--modo", "tabla"], b">>graph6<<\nBw\n", 0)
    fd = os.open(str(W), os.O_RDONLY)          # a directory as stdin: read error, not a normal EOF
    try:
        p = subprocess.run([str(BIN), "--modo", "tabla"], stdin=fd, capture_output=True)
    finally:
        os.close(fd)
    case("classifier", "input read error", p.returncode == 4, exit=p.returncode)
    v = subprocess.run([str(BIN), "--version"], capture_output=True, text=True).stdout.split()
    case("classifier", "version string is v2.1", len(v) > 1 and v[1] == "v2.1", version=" ".join(v[:2]))
    b = (V2 / "build.sh").read_text()
    case("classifier", "build.sh compiles without -march=native", "-march=native" not in b.replace("no -march=native", ""))


# --------------------------------------------------------------------------------------------- slice checks (H-24)
CFG = {"geng_args": ["-c"], "n": 3, "mode": "atascadas", "mod": 1, "workers": 1, "root": "/fixture",
       "files": {"geng": {"path": "/fixture/geng"}, "classifier": {"path": "/fixture/classifier"}}}
BASE = {"n": "3", "total": "1", "pasa_cono": "0", "pasa_chi": "0", "pasa_vecindades": "0", "pasa_aristas": "0",
        "encontradas": "0", "invalidos": "0", "errores": "0", "memo_consultas": "0", "memo_aciertos": "0",
        "memo_colisiones_hash": "0", "version": "v2.1"}
GEN1 = ">Z 1 graphs generated in 0.00 sec\n"


def summary(s):
    return " ".join(f"{k}={v}" for k, v in s.items()) + "\n"


def slice_cases():
    def check(name, s=None, out="", gen=GEN1, want=True, extra="", c=None, r=None):
        try:
            M.check_slice(c or CFG, gen, summary(BASE if s is None else s).rstrip("\n") + extra + "\n", out, r)
            got = True
            why = ""
        except M.SliceError as e:
            got, why = False, str(e)[:120]
        case("slice", name, got == want, accepted=got, expected=want, reason=why)
    check("baseline accepted")
    s = dict(BASE, n="0", total="0")
    check("empty slice accepted", s, gen=">Z 0 graphs generated\n")
    check("negative search counter rejected", dict(BASE, pasa_aristas="-1"), want=False)
    check("negative memo counter rejected", dict(BASE, memo_consultas="-4"), want=False)
    check("memo hits above queries rejected", dict(BASE, memo_aciertos="12"), want=False)
    check("collisions may exceed queries (one per probe)", dict(BASE, memo_consultas="2", memo_colisiones_hash="9"))
    check("repeated version keys rejected", want=False, extra=" version=v1 version=v2.1")
    check("repeated order keys rejected", want=False, extra=" n=99 n=3")
    check("unparsed trailing text rejected", want=False, extra=" CORRUPTED RECORD")
    check("summary of another mode rejected", want=False, extra=" modo=casi")
    check("another classifier version rejected", dict(BASE, version="v2"), want=False)
    check("repeated generator count rejected", gen=">Z 1 graphs generated\n>Z 1 graphs generated\n", want=False)
    check("generator error line rejected", gen=">Z 1 graphs generated\n>E fault\n", want=False)
    check("indented generator error rejected", gen=">Z 1 graphs generated\n >E fault\n", want=False)
    check("generator count mismatch rejected", gen=">Z 2 graphs generated\n", want=False)
    hdr = ">A /x/geng -cX0x100d1D2 n=3 e=2-3 class=0/2\n"
    c2 = dict(CFG, mod=2, workers=1)
    check("generator header of the right slice accepted", gen=hdr + GEN1, c=c2, r=0)
    check("generator header of another slice rejected", gen=hdr + GEN1, c=c2, r=1, want=False)
    check("generator header of another order rejected", gen=hdr.replace("n=3", "n=4") + GEN1, c=c2, r=0, want=False)
    check("generator error before the count rejected", gen=">E fault\n" + GEN1, want=False)
    s = dict(BASE, total="0")
    check("order of an empty but labelled slice accepted", s, gen=">Z 0 graphs generated\n")
    s = dict(BASE, **{k: "2" for k in ("total", "pasa_cono", "pasa_chi", "pasa_vecindades", "pasa_aristas",
                                       "encontradas")})
    check("duplicate graph record rejected", s, out="Bw\nBw\n", gen=">Z 2 graphs generated\n", want=False)
    check("invalid graph6 padding rejected", s, out="Bv\nBw\n", gen=">Z 2 graphs generated\n", want=False)
    check("graph of another order rejected", s, out="C~\nBw\n", gen=">Z 2 graphs generated\n", want=False)
    ct = dict(CFG, mode="tabla")
    st = {k: "0" for k in M.TABLE_KEYS}
    st.update(n="3", conexas="1", invalidos="0", errores="0", icert_truncados="0", version="v2.1",
              **{k: "0" for k in M.MEMO_KEYS})
    check("valid table summary accepted", st, c=ct)
    check("table summary without icert_truncados rejected", {k: v for k, v in st.items() if k != "icert_truncados"},
          c=ct, want=False)
    check("negative table counter rejected", dict(st, **{"-1-Dis": "-8"}), c=ct, want=False)
    check("broken acyclic identity rejected", dict(st, I="1"), c=ct, want=False)
    check("broken inclusion rejected", dict(st, **{"0-Dis": "1"}), c=ct, want=False)
    sp = dict(st, aciclicas="1", chi1="1", I="1")
    check("missing I_NO_IS record rejected", sp, c=ct, want=False)
    check("present I_NO_IS record accepted", sp, c=ct, out="I_NO_IS Bw\n")
    s2 = dict(sp, conexas="2", chi1="2", aciclicas="2", I_indecisas="1")
    check("same graph in two classes rejected", s2, c=ct, out="I_NO_IS Bw\nACICLICA_NO_IS_INDECISA Bw\n",
          gen=">Z 2 graphs generated\n", want=False)
    check("unknown record class rejected", s2, c=ct, out="UNKNOWN Bw\n", gen=">Z 2 graphs generated\n", want=False)


def receipt_cases():
    co, re_, me = M.check_slice(CFG, GEN1, summary(BASE), "")
    g, c = M.commands(CFG, 0)
    rec = {"schema": M.SCHEMA, "status": "complete", "r": 0, "mod": 1, "config_sha256": "fixture", "cmd_geng": g,
           "cmd_classifier": c, "exit_geng": 0, "exit_classifier": 0, "counts": co, "records": re_, "memo": me,
           "geng_stderr": GEN1, "classifier_stderr": summary(BASE), "result_stdout": "", "worker_id": 0,
           "host": "fixture", "utc_start": "2026-10-16T00:00:00Z", "utc_end": "2026-10-16T00:00:01Z", "seconds": 1}
    for k in ("geng_stderr", "classifier_stderr", "result_stdout"):
        rec[k + "_sha256"] = M.sha_bytes(rec[k].encode())
    mods = {"baseline": {}, "generator exit 42": {"exit_geng": 42}, "classifier exit 42": {"exit_classifier": 42},
            "both exit 42": {"exit_geng": 42, "exit_classifier": 42}, "wrong residue": {"r": 1},
            "wrong modulus": {"mod": 2}, "wrong config hash": {"config_sha256": "wrong"},
            "wrong command": {"cmd_classifier": ["wrong"]}, "altered stream": {"classifier_stderr": summary(BASE) + "x"},
            "altered counts": {"counts": dict(co, total=100)}, "worker 99 of 1": {"worker_id": 99},
            "worker id as boolean": {"worker_id": False}, "negative seconds": {"seconds": -1},
            "missing provenance": None}
    for name, mod in mods.items():
        d = copy.deepcopy(rec)
        if mod is None:
            for k in ("worker_id", "host", "utc_start", "utc_end", "seconds"):
                del d[k]
        else:
            d.update(mod)
        try:
            M.validate_receipt(CFG, "fixture", 0, d)
            got = True
        except M.SliceError:
            got = False
        want = name == "baseline"
        case("receipt", name + (" accepted" if want else " rejected"), got == want, accepted=got)
    c2 = dict(CFG, mod=2, workers=2)
    d = copy.deepcopy(rec)
    d.update(mod=2, r=1, worker_id=0)
    d["cmd_geng"], d["cmd_classifier"] = M.commands(c2, 1)
    try:
        M.validate_receipt(c2, "fixture", 1, d)
        got = True
    except M.SliceError:
        got = False
    case("receipt", "worker that does not own the residue rejected", not got, accepted=got)
    d = copy.deepcopy(rec)
    d["classifier_stderr"] = summary(dict(BASE, memo_consultas="999"))
    d["classifier_stderr_sha256"] = M.sha_bytes(d["classifier_stderr"].encode())
    d["memo"] = dict(d["memo"], memo_consultas=999)
    try:
        M.validate_receipt(CFG, "fixture", 0, d)
        got = True
    except M.SliceError:
        got = False
    case("receipt", "coherently rewritten receipt is not authenticated (documented limitation)", got, accepted=got)


# --------------------------------------------------------------------------------------------- campaigns (H-22, H-23, H-29)
def campaign_cases(W):
    rc, o, e = init(W / "c")
    cfg = W / "c" / "config.json"
    rcw = drv("worker", "--config", cfg, "--worker-id", 0)[0]
    rca = drv("aggregate", "--config", cfg, "--jobs", 1)[0]
    agg = json.loads((W / "c" / "aggregate.json").read_text())
    case("campaign", "real campaign n=3 aggregates", rc == 0 and rcw == 0 and rca == 0 and agg["ok"])
    refs = {"reference without the requested row": "n,connected\n4,6\n",
            "reference without the requested columns": "n\n3\n",
            "reference with two conflicting rows": "n,connected\n3,999\n3,2\n",
            "reference with an empty cell": "n,connected,chi=1\n3,2,\n"}
    for name, txt in refs.items():
        f = W / (name.replace(" ", "_") + ".csv")
        f.write_text(txt)
        rcr = drv("aggregate", "--config", cfg, "--jobs", 1, "--reference-csv", f)[0]
        ok = json.loads((W / "c" / "aggregate.json").read_text())["ok"]
        case("reference", name + " refused", rcr != 0 and not ok, exit=rcr)
    full = REPO / "data" / "table_cardinalities.csv"
    rcr = drv("aggregate", "--config", cfg, "--jobs", 1, "--reference-csv", full)[0]
    agg = json.loads((W / "c" / "aggregate.json").read_text())
    case("reference", "published row n=3 compared on all 12 columns", rcr == 0 and agg["ok"]
         and len(agg["comparison"]) == 12 and all(v["equal"] for v in agg["comparison"].values()), exit=rcr)
    f = W / "conflict.csv"
    f.write_text("n,connected\n3,999\n")
    rcr = drv("aggregate", "--config", cfg, "--jobs", 1, "--reference-csv", f, "--expect", "conexas=2")[0]
    case("reference", "--expect cannot override a conflicting reference", rcr != 0, exit=rcr)
    rcr, _, er = drv("aggregate", "--config", cfg, "--jobs", 1, "--expect", "conexas=2", "conexas=2")
    case("reference", "repeated --expect key refused", rcr != 0 and "repeated" in er, exit=rcr)
    rcr, _, er = drv("aggregate", "--config", cfg, "--jobs", 1, "--expect", "conexas=-2")
    case("reference", "negative --expect value refused", rcr != 0, exit=rcr)
    # H-29: a failed aggregation never leaves an earlier ok=true behind; status is not a certificate
    drv("aggregate", "--config", cfg, "--jobs", 1)
    rp = W / "c" / "receipts" / "0" / "0.ok.json"
    saved = rp.read_text()
    rp.write_text("")
    rcr = drv("aggregate", "--config", cfg, "--jobs", 1)[0]
    stale = (W / "c" / "aggregate.json").exists() and json.loads((W / "c" / "aggregate.json").read_text()).get("ok")
    hist = list((W / "c" / "aggregate_history").glob("*/aggregate.json"))
    case("aggregate", "empty receipt fails and leaves no earlier ok=true", rcr != 0 and not stale and hist,
         exit=rcr, history=len(hist))
    st = json.loads(drv("status", "--config", cfg)[1])
    case("aggregate", "status counts the empty receipt as unreadable and says it is not a certificate",
         st["ok_receipts"] == 1 and st["ok_receipts_unreadable"] == 1 and "not a certificate" in st["note"], status=st)
    rp.write_text(saved)
    # aggregate refuses while a producer holds its lock
    import fcntl
    with open(W / "c" / "workers" / "0.lock", "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rcr, _, er = drv("aggregate", "--config", cfg, "--jobs", 1)
    case("aggregate", "aggregate refused while a worker holds its lock", rcr != 0 and "producers run" in er, exit=rcr)
    # a classifier that exits 42 publishes nothing
    s42 = W / "exit42.c"
    t = SOURCE.read_text()
    i = t.rfind("return 0;")
    s42.write_text(t[:i] + "return 42;" + t[i + len("return 0;"):])
    init(W / "c42", source=s42)
    rcw = drv("worker", "--config", W / "c42" / "config.json", "--worker-id", 0)[0]
    oks = list((W / "c42" / "receipts").rglob("*.ok.json"))
    fails = [json.loads(x.read_text()) for x in (W / "c42" / "receipts").rglob("*.failed.*.json")]
    case("campaign", "classifier exit 42 publishes no receipt", rcw != 0 and not oks and fails
         and all(f["exit_classifier"] == 42 for f in fails), failed=len(fails))
    # init: geng version contract, order, exclusivity, protected paths, edits after init, driver pin
    tok, sha = geng_pins(GENG)[1], geng_pins(GENG)[3]
    dotted = "2.9.3" if tok.startswith("2.93") else tok + ".0"   # a dotted name, never the printed token
    rc1 = init(W / "v1", pin=False, extra=["--expect-geng-version", tok, "--expect-geng-sha256", sha])[0]
    rc2 = init(W / "v2", pin=False, extra=["--expect-geng-version", dotted, "--expect-geng-sha256", sha])[0]
    rc3 = init(W / "v3", pin=False, extra=["--expect-geng-version", "1.0.0", "--expect-geng-sha256", sha])[0]
    rc3b = init(W / "v3b", pin=False, extra=["--expect-geng-sha256", sha])[0]
    case("init", f"geng version token compared exactly: {tok} accepted; {dotted}, 1.0.0 and a missing option refused "
         "before touching the disk", rc1 == 0 and rc2 != 0 and rc3 != 0 and rc3b != 0
         and not any((W / d).exists() for d in ("v2", "v3", "v3b")), exits=[rc1, rc2, rc3, rc3b])
    rc5 = init(W / "v5", pin=False, extra=["--expect-geng-version", tok, "--expect-geng-sha256", "0" * 64])[0]
    rc5b = init(W / "v5b", pin=False, extra=["--expect-geng-version", tok, "--expect-geng-sha256", "xyz"])[0]
    rc5c = init(W / "v5c", pin=False, extra=["--expect-geng-version", tok])[0]
    case("init", "geng SHA-256 pin required and exact; refused before touching the disk", rc5 != 0 and rc5b != 0
         and rc5c != 0 and not any((W / d).exists() for d in ("v5", "v5b", "v5c")), exits=[rc5, rc5b, rc5c])
    s2 = W / "v2src.c"
    s2.write_text(Path(SOURCE).read_text(encoding="utf-8").replace('#define VERSION "v2.1"', '#define VERSION "v2"'),
                  encoding="utf-8")
    rcf = init(W / "vfail", source=s2)[0]
    rcfw = drv("worker", "--config", W / "vfail" / "config.json", "--worker-id", 0)[0]
    case("init", "failure after mkdir leaves INIT_FAILED.txt, no config, and a worker that refuses",
         rcf != 0 and (W / "vfail" / "INIT_FAILED.txt").exists() and not (W / "vfail" / "config.json").exists()
         and rcfw != 0, exits=[rcf, rcfw])
    rc6 = init(W / "bad_order", n=99)[0]
    case("init", "order 99 refused before touching the disk", rc6 != 0 and not (W / "bad_order").exists(), exit=rc6)
    rc7 = init(W / "bad_mode", mode="casi")[0]
    case("init", "unknown mode refused before touching the disk", rc7 != 0 and not (W / "bad_mode").exists())
    rc8, _, e8 = init(W / "c")
    case("init", "existing root refused", rc8 != 0 and "already exists" in e8, exit=rc8)
    (W / "prot").mkdir()
    rc9, _, e9 = init(W / "prot" / "inside", extra=["--protect", W / "prot"])
    case("init", "root inside a protected directory refused", rc9 != 0 and "protected" in e9
         and not (W / "prot" / "inside").exists(), exit=rc9)
    env = dict(os.environ, CAMPANA_PROTECT=str(W / "prot"))
    p = subprocess.run([sys.executable, str(DRIVER), "init", "--root", str(W / "prot" / "env"), "--n", "3", "--mod",
                        "2", "--workers", "1", "--mode", "tabla", "--geng", GENG, "--geng-args=-c", "--source",
                        str(SOURCE), *geng_pins(GENG)], capture_output=True, text=True, env=env)
    case("init", "CAMPANA_PROTECT honoured", p.returncode != 0 and "protected" in p.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        rs = list(ex.map(lambda i: init(W / "racy"), range(2)))
    case("init", "two concurrent inits on one new root: exactly one succeeds",
         sorted(r[0] == 0 for r in rs) == [False, True], exits=[r[0] for r in rs])
    init(W / "ed")
    cj = W / "ed" / "config.json"
    os.chmod(cj, 0o644)
    d = json.loads(cj.read_text())
    d["workers"] = 2
    cj.write_text(json.dumps(d, sort_keys=True) + "\n")
    rce, _, ee = drv("worker", "--config", cj, "--worker-id", 0)
    case("init", "edited config refused by the worker", rce != 0 and "config.sha256" in ee, exit=rce)
    init(W / "dp")
    other = W / "campana_v2_edited.py"
    other.write_text(DRIVER.read_text() + "\n# edited\n")
    p = subprocess.run([sys.executable, str(other), "worker", "--config", str(W / "dp" / "config.json"),
                        "--worker-id", "0"], capture_output=True, text=True)
    case("init", "a driver other than the pinned one refused", p.returncode != 0 and "pinned" in p.stderr)
    # graph sets compared as labelled strings or up to isomorphism (G14a through a one-graph generator)
    g14a = "M?b@bFHNEk@~|k}U?"
    fake = W / "geng_one.sh"
    fake.write_text("#!/bin/bash\ncase \"$1\" in --version) echo 'Nauty&Traces version 2.8090 (fake)'; exit 0;; "
                    "--help) echo help; exit 0;; esac\n"
                    f"echo '{g14a}'\necho '>Z 1 graphs generated in 0.00 sec' >&2\n")
    os.chmod(fake, 0o755)
    rci = init(W / "iso", n=14, mod=1, geng=fake)[0]
    rcw = drv("worker", "--config", W / "iso" / "config.json", "--worker-id", 0)[0]
    relabelled = subprocess.run([LABELG, "-q"], input=g14a + "\n", capture_output=True, text=True).stdout.strip()
    ref = W / "ref.g6"
    ref.write_text(relabelled + "\n")
    rs = drv("aggregate", "--config", W / "iso" / "config.json", "--jobs", 1, "--reference-g6", ref)[0]
    rl = drv("aggregate", "--config", W / "iso" / "config.json", "--jobs", 1, "--reference-g6", ref,
             "--labelg", LABELG)[0]
    agg = json.loads((W / "iso" / "aggregate.json").read_text())
    case("reference", "graph sets: labelled strings differ, labelg makes them equal",
         rci == 0 and rcw == 0 and relabelled != g14a and rs != 0 and rl == 0
         and agg["comparison"]["I_NO_IS_set"]["equal"], exits=[rci, rcw, rs, rl])


def main():
    global BIN
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default=str(HERE / "results" / "v2.1" / "regressions_r2.json"))
    ap.add_argument("--bin", default=str(BIN),
                    help="classifier binary under test (default build/atascadas_v2); an older binary here shows "
                         "whether the classifier cases are sensitive to the v2.1 changes")
    ap.add_argument("--sections", default="classifier,slice,receipt,campaign",
                    help="comma-separated subset of classifier,slice,receipt,campaign")
    a = ap.parse_args()
    BIN = Path(a.bin).resolve()
    sections = set(a.sections.split(","))
    unknown = sections - {"classifier", "slice", "receipt", "campaign"}
    if unknown:
        raise SystemExit(f"unknown sections: {sorted(unknown)}")
    W = Path(a.work).resolve()
    if W.exists():
        shutil.rmtree(W)
    W.mkdir(parents=True)
    for tool in ("gcc", "geng", "labelg"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} is required on PATH")
    if not BIN.exists():
        raise SystemExit(f"{BIN} missing: run ./build.sh")
    started = provenance.utc_now()
    prov = provenance.record(binaries=[(BIN, ["--version"])],
                             sources=[SOURCE, DRIVER, V2 / "build.sh", Path(__file__)], tools=["geng", "labelg"])
    if "classifier" in sections:
        classifier_cases(W)
    if "slice" in sections:
        slice_cases()
    if "receipt" in sections:
        receipt_cases()
    if "campaign" in sections:
        campaign_cases(W)
    res = {"all_pass": all(r["pass"] for r in RESULTS), "n_cases": len(RESULTS),
           "n_failed": sum(not r["pass"] for r in RESULTS), "cases": RESULTS,
           "tools": {"geng": provenance.display_path(GENG), "labelg": provenance.display_path(LABELG),
                     "python": sys.version.split()[0]},
           "binary_under_test": provenance.display_path(BIN), "sections": sorted(sections), "started_utc": started,
           "finished_utc": provenance.utc_now(), "provenance": prov}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(provenance.check_portable(json.dumps(res, indent=1) + "\n"))
    print(f"{res['n_cases']} cases, {res['n_failed']} failed:", "ALL PASS" if res["all_pass"] else "SOME CASES FAILED")
    sys.exit(0 if res["all_pass"] else 1)


if __name__ == "__main__":
    main()
