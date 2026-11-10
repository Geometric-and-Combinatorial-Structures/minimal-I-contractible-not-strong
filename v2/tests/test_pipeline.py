#!/usr/bin/env python3
"""Fault-injection tests of v2/pipeline/campana_v2.py (findings H-02, H-03, H-04 of the external audit).

Usage: python3 test_pipeline.py --work /tmp/pipeline_tests --out results/v2.4/pipeline.json
Requires geng on PATH and gcc.  Every case states what must happen; the script exits 0 only if all cases behave so.
"""
import argparse, fcntl, json, os, shlex, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V2 = HERE.parent
sys.path.insert(0, str(HERE))
import provenance  # noqa: E402
DRIVER = str(V2 / "pipeline" / "campana_v2.py")
SOURCE = str(V2 / "src" / "atascadas_v2.c")
CSV = str(V2.parent / "data" / "raw_classifier_reference.csv")
GENG = shutil.which("geng")


def geng_pins(geng):
    """--expect-geng-version (the token printed by geng --version) and --expect-geng-sha256 for this geng."""
    import hashlib, re
    out = subprocess.run([str(geng), "--version"], capture_output=True, text=True)
    m = re.search(r"version\s+([0-9]+\.[0-9]+)", out.stdout + out.stderr)
    h = hashlib.sha256(Path(geng).read_bytes()).hexdigest()
    return ["--expect-geng-version", m.group(1) if m else "none", "--expect-geng-sha256", h]


def py(*args, check=None):
    p = subprocess.run([sys.executable, DRIVER] + [str(a) for a in args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def init(root, n, mod, workers, mode="tabla", geng=GENG, geng_args="-c", source=SOURCE):
    if Path(root).exists():
        shutil.rmtree(root)
    rc, o, e = py("init", "--root", root, "--n", n, "--mod", mod, "--workers", workers, "--mode", mode,
                  "--geng", geng, f"--geng-args={geng_args}", "--source", source, *geng_pins(geng))
    if rc != 0:
        raise RuntimeError("init failed: " + e)
    return str(Path(root) / "config.json")


def run_workers(cfg, workers, procs=2):
    return [py("worker", "--config", cfg, "--worker-id", w, "--procs", procs)[0] for w in range(workers)]


def write_exec(path, text):
    Path(path).write_text(text)
    os.chmod(path, 0o755)
    return str(path)


# v2.2: init requires `geng --help` to exit 0 (H-23), so every fake generator below answers --help like --version;
# the cases still test failures of the producer DURING enumeration, which is what they were written for.
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="/tmp/pipeline_tests")
    ap.add_argument("--out", default=str(HERE / "results" / "v2.4" / "pipeline.json"))
    a = ap.parse_args()
    W = Path(a.work)
    if W.exists():
        shutil.rmtree(W)
    W.mkdir(parents=True)
    started = provenance.utc_now()
    prov = provenance.record(sources=[DRIVER, SOURCE, CSV, Path(__file__)], tools=["geng"])
    results = []

    def case(name, ok, **info):
        results.append({"case": name, "pass": bool(ok), **info})
        print(("PASS " if ok else "FAIL ") + name, json.dumps(info)[:240], flush=True)

    # P1 normal campaign n=8 (mod 10, 3 workers, 2 pipelines each) equals the published row
    cfg = init(W / "p1", 8, 10, 3)
    rcs = run_workers(cfg, 3)
    rc, o, e = py("aggregate", "--config", cfg, "--reference-csv", CSV)
    agg = json.loads((W / "p1" / "aggregate.json").read_text())
    case("P1 normal campaign n=8 equals published row", rcs == [0, 0, 0] and rc == 0 and agg["ok"]
         and agg["coverage"] == 10 and all(v["equal"] for v in agg["comparison"].values()), counts=agg["counts"])

    # P2 resume: every receipt re-validated, nothing recomputed
    rc, o, e = py("worker", "--config", cfg, "--worker-id", 0, "--procs", 2)
    st = json.loads(o.strip().splitlines()[-1])
    case("P2 resume validates existing receipts", rc == 0 and st["this_run"]["new"] == 0
         and st["this_run"]["resumed"] == st["slices"], this_run=st["this_run"])

    # P3 the same worker id cannot run twice at the same time
    lockp = W / "p1" / "workers" / "1.lock"
    with open(lockp, "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rc, o, e = py("worker", "--config", cfg, "--worker-id", 1)
    case("P3 duplicate worker id refused", rc != 0 and "already running" in (o + e), exit=rc)

    # P4 producer emits graphs and exits 42 (the auditor's synthetic failure): nothing is published
    fake = write_exec(W / "geng_exit42.sh",
                      "#!/bin/bash\nif [ \"$1\" = --version ]; then echo 'Nauty&Traces version 0.0000 (fake)'; exit 0; fi\n"
                      "if [ \"$1\" = --help ]; then echo 'fake geng: help'; exit 0; fi\n"
                      f"{shlex.quote(GENG)} \"$@\"\nexit 42\n")
    cfg4 = init(W / "p4", 7, 4, 1, geng=fake)
    rcs = run_workers(cfg4, 1)
    okr = list((W / "p4" / "receipts").rglob("*.ok.json")) if (W / "p4" / "receipts").exists() else []
    fl = list((W / "p4" / "receipts").rglob("*.failed.*.json"))
    rc, o, e = py("aggregate", "--config", cfg4)
    case("P4 producer exit 42 is a failure; no receipt; aggregate refuses", rcs == [1] and not okr and len(fl) == 4
         and rc != 0, failed_files=len(fl), aggregate_exit=rc)

    # P5 producer prints an error line but exits 0
    fake = write_exec(W / "geng_E.sh",
                      "#!/bin/bash\nif [ \"$1\" = --version ]; then echo 'Nauty&Traces version 0.0000 (fake)'; exit 0; fi\n"
                      "if [ \"$1\" = --help ]; then echo 'fake geng: help'; exit 0; fi\n"
                      f"{shlex.quote(GENG)} \"$@\"\necho '>E simulated error' >&2\nexit 0\n")
    cfg5 = init(W / "p5", 7, 2, 1, geng=fake)
    rcs = run_workers(cfg5, 1)
    case("P5 producer '>E' line rejected", rcs == [1] and not list((W / "p5" / "receipts").rglob("*.ok.json")))

    # P6 producer without its count line (geng -q)
    fake = write_exec(W / "geng_q.sh",
                      "#!/bin/bash\nif [ \"$1\" = --version ]; then echo 'Nauty&Traces version 0.0000 (fake)'; exit 0; fi\n"
                      "if [ \"$1\" = --help ]; then echo 'fake geng: help'; exit 0; fi\n"
                      f"{shlex.quote(GENG)} -q \"$@\"\n")
    cfg6 = init(W / "p6", 7, 2, 1, geng=fake)
    rcs = run_workers(cfg6, 1)
    case("P6 missing '>Z' count line rejected", rcs == [1] and not list((W / "p6" / "receipts").rglob("*.ok.json")))

    # P7 producer truncates its output but reports the full count
    fake = write_exec(W / "geng_trunc.sh",
                      "#!/bin/bash\nif [ \"$1\" = --version ]; then echo 'Nauty&Traces version 0.0000 (fake)'; exit 0; fi\n"
                      "if [ \"$1\" = --help ]; then echo 'fake geng: help'; exit 0; fi\n"
                      f"{shlex.quote(GENG)} \"$@\" 2> >(cat >&2) | head -n 5\n")
    cfg7 = init(W / "p7", 7, 1, 1, geng=fake)
    rcs = run_workers(cfg7, 1)
    case("P7 truncated stream (count mismatch) rejected", rcs == [1]
         and not list((W / "p7" / "receipts").rglob("*.ok.json")))

    # P8 classifier with an extra stderr line; P9 classifier that is not v2
    src8 = W / "extra_stderr.c"
    s = Path(SOURCE).read_text()
    src8.write_text(s.replace("int main(int argc, char **argv) {",
                              "int main(int argc, char **argv) {\n  fprintf(stderr, \"aviso\\n\");", 1))
    cfg8 = init(W / "p8", 7, 2, 1, source=src8)
    rcs = run_workers(cfg8, 1)
    case("P8 unexpected classifier stderr rejected", rcs == [1]
         and not list((W / "p8" / "receipts").rglob("*.ok.json")))
    src9 = W / "not_pinned_version.c"
    import re
    VER = re.search(r'#define VERSION "([^"]+)"', s).group(1)
    assert f'#define VERSION "{VER}"' in s
    src9.write_text(s.replace(f'#define VERSION "{VER}"', '#define VERSION "v1x"', 1))
    rc9, _, e9 = py("init", "--root", W / "p9", "--n", 7, "--mod", 2, "--workers", 1, "--mode", "tabla",
                    "--geng", GENG, "--geng-args=-c", "--source", src9, *geng_pins(GENG))
    case(f"P9 classifier version other than {VER} refused at init", rc9 != 0 and f"is not {VER}" in e9
         and not (W / "p9" / "config.json").exists(), exit=rc9)

    # P10 pinned binary replaced after init
    cfg10 = init(W / "p10", 7, 2, 1)
    b = W / "p10" / "bin" / "atascadas_v2"
    os.chmod(b, 0o755)
    with open(b, "ab") as f:
        f.write(b"\0")
    rcs = run_workers(cfg10, 1)
    case("P10 modified pinned binary detected", rcs == [1])

    # P11 tampered receipts are detected by the aggregate (a campaign of its own: v2.1 configs cannot be edited)
    import hashlib
    cfg11 = init(W / "p11", 8, 10, 3)
    run_workers(cfg11, 3)
    rc0, _, _ = py("aggregate", "--config", cfg11)
    p3 = W / "p11" / "receipts" / "0" / "3.ok.json"
    good = p3.read_text()
    d = json.loads(good)
    d["counts"]["chi1"] += 1
    p3.write_text(json.dumps(d, sort_keys=True) + "\n")
    rc1, _, e1 = py("aggregate", "--config", cfg11)
    d = json.loads(good)
    d["result_stdout"] += "I_NO_IS " + "G" + "?" * 5 + "\n"
    d["result_stdout_sha256"] = hashlib.sha256(d["result_stdout"].encode()).hexdigest()
    p3.write_text(json.dumps(d, sort_keys=True) + "\n")
    rc2, _, e2 = py("aggregate", "--config", cfg11)
    p3.write_text(good)
    os.rename(p3, W / "p11" / "receipts" / "0" / "3.moved")
    rc3, o3, _ = py("aggregate", "--config", cfg11)
    os.rename(W / "p11" / "receipts" / "0" / "3.moved", p3)
    (W / "p11" / "receipts" / "1").mkdir(exist_ok=True)
    shutil.copy(p3, W / "p11" / "receipts" / "1" / "3.ok.json")
    rc4, _, e4 = py("aggregate", "--config", cfg11)
    case("P11 aggregate detects tampering", rc0 == 0 and rc1 != 0 and rc2 != 0 and rc3 != 0 and rc4 != 0,
         baseline=rc0, edited_counts=rc1, forged_record=rc2, missing_receipt=rc3, wrong_shard=rc4)

    # P12 stuck-graph search mode, n=9 (geng -C -d4 -D7 9): total equals the direct run
    cfg12 = init(W / "p12", 9, 5, 2, mode="atascadas", geng_args="-C -d4 -D7")
    rcs = run_workers(cfg12, 2)
    rc, o, e = py("aggregate", "--config", cfg12, "--expect", "total=12881", "--expect", "encontradas=0")
    agg = json.loads((W / "p12" / "aggregate.json").read_text())
    case("P12 search mode n=9 totals", rcs == [0, 0] and rc == 0 and agg["counts"]["total"] == 12881,
         counts=agg["counts"])

    res = {"all_pass": all(r["pass"] for r in results), "cases": results, "started_utc": started,
           "finished_utc": provenance.utc_now(), "provenance": prov}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(provenance.check_portable(json.dumps(res, indent=1) + "\n"))
    print("ALL PASS" if res["all_pass"] else "SOME CASES FAILED")
    sys.exit(0 if res["all_pass"] else 1)


if __name__ == "__main__":
    main()
