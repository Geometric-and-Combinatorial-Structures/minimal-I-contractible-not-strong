#!/usr/bin/env python3
"""Regression tests for the findings of round 4 of the external audit (residues of H-22 and H-29), closed by class.

Groups
  init         class of H-22 at init: the copy of geng modified between its check against --expect-geng-sha256 and
                     the marker (during the compilation of the classifier) makes init fail and the root refused.
  labelg       H-22  the auditor's race (the labelg given to aggregate replaced by a constant canonizer at its first
                     use, which made v2.2 accept G14a against K14); the frozen copy replaced before its first run
                     and at the moment of a run; a constant and an identity "canonizer" given from the start (the
                     self-test refuses them); a graph6 or CSV reference changed during the attempt; what is recorded.
  transaction  H-29  the auditor's fault (the final write of the attempt record fails after success); a single write
                     failure at each write operation of a successful aggregate, a persistent failure from each
                     operation on, and a crash (os._exit) at each operation; a summary that cannot be printed.  In
                     every case aggregate.json with ok=true must belong to an attempt whose record is terminal (ok)
                     and names the SHA-256 of aggregate.json, and the failing attempt is never certified.
  worker       class of H-22 for the workers: the pinned classifier modified between two slices and the pinned
                     geng modified while a slice runs publish no receipt; once restored, the worker resumes.

Usage: python3 tests/test_regressions_r4.py --work DIR [--out results/v2.4/regressions_r4.json]
       [--driver DRIVER] [--source SOURCE] [--bin BINARY] [--sections init,labelg,transaction,worker]
--driver runs the same cases against an older driver (sensitivity: with v2.2 most cases must fail).
Requires gcc, geng and labelg (nauty) on PATH and build/atascadas_v2 (./build.sh).  Exit status 0 only if every case
behaves as stated.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys
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
PUBLISHED = REPO / "data" / "table_cardinalities.csv"
SECTIONS = ["init", "labelg", "transaction", "worker"]
HOME = os.path.expanduser("~")
G14A = "M?b@bFHNEk@~|k}U?"          # data/minimal_I_not_strong_14.g6, first graph
K14 = "M" + "~" * 15 + "_"           # the complete graph on 14 vertices
W = None
RESULTS = []

INJECT = r'''
import atexit, importlib.util, os, pathlib, shutil, subprocess, sys
driver, mode, arg, rest = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
spec = importlib.util.spec_from_file_location("campana", driver)
m = importlib.util.module_from_spec(spec)
sys.modules["campana"] = m
spec.loader.exec_module(m)


def overwrite(path, src_bytes, mode_after=0o500):
    os.chmod(path, 0o700)
    with open(path, "wb") as f:
        f.write(src_bytes)
    os.chmod(path, mode_after)


if mode in ("count", "fail_at", "fail_from", "crash_at"):
    k = int(arg)
    state = {"n": 0}
    real_replace, real_fsync, real_write_text = os.replace, os.fsync, pathlib.Path.write_text

    def tick():
        state["n"] += 1
        i = state["n"]
        if (mode == "fail_at" and i == k) or (mode == "fail_from" and i >= k):
            raise OSError(f"injected write failure at operation {i}")
        if mode == "crash_at" and i == k:
            os._exit(137)

    def replace(a, b, *x, **y):
        tick()
        return real_replace(a, b, *x, **y)

    def fsync(fd):
        tick()
        return real_fsync(fd)

    def write_text(self, *x, **y):
        tick()
        return real_write_text(self, *x, **y)

    os.replace, os.fsync, pathlib.Path.write_text = replace, fsync, write_text
    if mode == "count":
        atexit.register(lambda: sys.stderr.write(f"\nOPS={state['n']}\n"))
elif mode == "attempt_ok_fail":          # the auditor's injection of round 4
    real_aj = m.atomic_json

    def aj(path, obj, *x, **y):
        if pathlib.Path(path).parent.name == "aggregate_attempts" and isinstance(obj, dict) and obj.get("status") == "ok":
            raise OSError("injected final attempt write failure")
        return real_aj(path, obj, *x, **y)
    m.atomic_json = aj
elif mode == "canon_replace_original":   # the auditor's race of round 4: the GIVEN labelg replaced at first use
    real_canon, done = m._canonical, {"x": False}
    fake = open(arg, "rb").read()

    def canonical(tool, *x, **y):
        if not done["x"]:
            overwrite(tool["path"] if isinstance(tool, dict) else tool, fake, 0o700)
            done["x"] = True
        return real_canon(tool, *x, **y)
    m._canonical = canonical
elif mode == "frozen_modify_after_freeze":
    fake = open(arg, "rb").read()
    if not hasattr(m, "_freeze_tool"):
        sys.stderr.write("NOT APPLICABLE: this driver has no frozen copy\n")
    else:
        real_freeze = m._freeze_tool

        def freeze(*x, **y):
            t = real_freeze(*x, **y)
            overwrite(t["frozen_copy"], fake)
            return t
        m._freeze_tool = freeze
elif mode == "frozen_modify_during_run":
    fake = open(arg, "rb").read()
    real_run = subprocess.run

    def run(cmd, *x, **y):
        c0 = str(cmd[0]) if isinstance(cmd, (list, tuple)) and cmd else ""
        if c0.endswith(".tools/labelg"):
            overwrite(c0, fake)
        return real_run(cmd, *x, **y)
    subprocess.run = run
elif mode == "ref_modify":
    real_hold = m._hold_worker_locks

    def hold(*x, **y):
        with open(arg, "a") as f:
            f.write("# changed during the attempt\n")
        return real_hold(*x, **y)
    m._hold_worker_locks = hold
elif mode == "classifier_modify_between_slices":
    real_rs, calls = m.run_slice, {"n": 0}

    def rs(cfg, *x, **y):
        res = real_rs(cfg, *x, **y)
        calls["n"] += 1
        if calls["n"] == 1:
            p = cfg["files"]["classifier"]["path"]
            overwrite(p, open(p, "rb").read() + b"\0", 0o555)
        return res
    m.run_slice = rs
elif mode == "geng_modify_during_slice":
    RealPopen = subprocess.Popen

    class Popen(RealPopen):
        def __init__(self, cmd, *x, **y):
            super().__init__(cmd, *x, **y)
            c0 = str(cmd[0]) if isinstance(cmd, (list, tuple)) and cmd else ""
            if c0.endswith("/geng"):
                overwrite(c0, open(c0, "rb").read() + b"\n", 0o555)
    subprocess.Popen = Popen
elif mode == "geng_modify_during_compile":
    real_run = subprocess.run

    def run(cmd, *x, **y):
        if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "gcc" and "-o" in cmd:
            g = os.path.join(os.path.dirname(str(cmd[cmd.index("-o") + 1])), "geng")
            if os.path.exists(g):
                overwrite(g, open(g, "rb").read() + b"\n", 0o755)
        return real_run(cmd, *x, **y)
    subprocess.run = run
elif mode != "none":
    raise SystemExit("unknown injection mode " + mode)
sys.argv = [driver] + rest
m.main()
'''


def scrub(text):
    for local, shown in ((str(W), "<work>"), (str(REPO), "<repo>"), (HOME, "~")):
        if local and local != "None":
            text = text.replace(local, shown)
    return text


def case(group, name, ok, **info):
    info = json.loads(scrub(json.dumps(info, default=str)))
    RESULTS.append({"group": group, "case": name, "pass": bool(ok), **info})
    print(("PASS " if ok else "FAIL ") + f"[{group}] {name}", json.dumps(info)[:220], flush=True)


def last_line(text):
    lines = [l for l in (text or "").strip().splitlines() if l.strip()]
    return lines[-1][:200] if lines else ""


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def geng_pins(geng):
    out = subprocess.run([str(geng), "--version"], capture_output=True, text=True)
    m = re.search(r"version\s+([0-9]+\.[0-9]+)", out.stdout + out.stderr)
    return ["--expect-geng-version", m.group(1) if m else "none", "--expect-geng-sha256", sha(geng)]


def drv(*args):
    p = subprocess.run([sys.executable, str(DRIVER)] + [str(a) for a in args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def inj(mode, arg, *args):
    p = subprocess.run([sys.executable, str(W / "inject_r4.py"), str(DRIVER), mode, str(arg)] + [str(a) for a in args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def init(root, n=3, mod=2, geng=None):
    geng = geng or GENG
    return drv("init", "--root", root, "--n", n, "--mod", mod, "--workers", 1, "--mode", "tabla", "--geng", geng,
               "--geng-args=-c", "--source", SOURCE, *geng_pins(geng))


def campaign(name, n=3, mod=2, geng=None):
    root = W / name
    rc, _, e = init(root, n, mod, geng)
    if rc != 0:
        raise RuntimeError(f"init of {name} failed: {last_line(e)}")
    cfg = root / "config.json"
    rcw, _, e = drv("worker", "--config", cfg, "--worker-id", 0)
    if rcw != 0:
        raise RuntimeError(f"worker of {name} failed: {last_line(e)}")
    return root, cfg


def agg_json(root):
    try:
        return json.loads((root / "aggregate.json").read_text())
    except (OSError, ValueError):
        return {}


def attempt_record(root, aid):
    try:
        return json.loads((root / "aggregate_attempts" / f"{aid}.json").read_text())
    except (OSError, ValueError, TypeError):
        return {}


def attempt_ids(root):
    d = root / "aggregate_attempts"
    return {p.stem for p in d.glob("*.json")} if d.exists() else set()


def g6_decode(s):
    n = ord(s[0]) - 63
    bits = [((ord(ch) - 63) >> (5 - i)) & 1 for ch in s[1:] for i in range(6)]
    pairs = [(i, j) for j in range(1, n) for i in range(j)]
    return n, {pq for pq, b in zip(pairs, bits) if b}


def g6_encode(n, edges):
    e = {(min(a, b), max(a, b)) for a, b in edges}
    bits = [1 if (i, j) in e else 0 for j in range(1, n) for i in range(j)]
    bits += [0] * (-len(bits) % 6)
    return chr(63 + n) + "".join(chr(63 + int("".join(map(str, bits[i:i + 6])), 2)) for i in range(0, len(bits), 6))


def relabel(s):
    n, e = g6_decode(s)
    perm = list(range(n))[::-1]
    return g6_encode(n, {(perm[a], perm[b]) for a, b in e})


def restore(path, data, mode=0o555):
    os.chmod(path, 0o700)
    Path(path).write_bytes(data)
    os.chmod(path, mode)


# ------------------------------------------------------------------------------------------------------------- init
def init_cases():
    G = "init"
    wrap = W / "geng_wrapper_init.sh"
    wrap.write_text(f'#!/bin/sh\nexec "{GENG}" "$@"\n')
    wrap.chmod(0o755)
    root = W / "init_geng_changed"
    p = inj("geng_modify_during_compile", 0, "init", "--root", root, "--n", 3, "--mod", 2, "--workers", 1, "--mode",
            "tabla", "--geng", wrap, "--geng-args=-c", "--source", SOURCE, *geng_pins(wrap))
    failed, marker = (root / "INIT_FAILED.txt").exists(), (root / "INIT_COMPLETE.json").exists()
    q = drv("worker", "--config", root / "config.json", "--worker-id", 0)
    case(G, "copy of geng modified after its check, before the marker: init fails and the worker refuses the root",
         p[0] != 0 and failed and not marker and q[0] != 0, exit=p[0], init_failed=failed, marker=marker, worker=q[0],
         said=last_line(p[2]))
    root2 = W / "init_normal"
    p = init(root2, 3, 2, wrap)
    c = json.loads((root2 / "config.json").read_text()) if (root2 / "config.json").exists() else {}
    case(G, "control: a normal init pins the SHA-256 given in --expect-geng-sha256 and certifies the campaign",
         p[0] == 0 and c.get("files", {}).get("geng", {}).get("sha256") == sha(wrap)
         and (root2 / "INIT_COMPLETE.json").exists(), exit=p[0])


# ----------------------------------------------------------------------------------------------------------- labelg
def labelg_cases():
    G = "labelg"
    fake_geng = W / "geng_g14a.sh"
    fake_geng.write_text("#!/bin/sh\ncase \"$1\" in --version) echo 'Nauty&Traces version 2.9301 (test fixture)'; exit 0;; "
                         "--help) echo 'test fixture: prints one graph'; exit 0;; esac\n"
                         f"echo '{G14A}'\necho '>Z 1 graphs generated in 0.00 sec' >&2\n")
    fake_geng.chmod(0o755)
    root, cfg = campaign("g14", n=14, mod=1, geng=fake_geng)
    lab = W / "labelg_given"
    shutil.copy2(LABELG, lab)
    const = W / "labelg_constant.py"
    const.write_text("#!/usr/bin/env python3\nimport sys\nfor line in sys.stdin:\n    print(" + repr(K14) + ")\n")
    const.chmod(0o755)
    ident = W / "labelg_identity.sh"
    ident.write_text("#!/bin/sh\ncat\n")
    ident.chmod(0o755)
    refs = {"k14": K14, "same": relabel(G14A), "ident": G14A}
    for k, g in refs.items():
        (W / f"ref_{k}.g6").write_text(g + "\n")

    def agg(ref, tool, mode=None, arg=""):
        base = ["aggregate", "--config", cfg, "--jobs", 1, "--reference-g6", W / f"ref_{ref}.g6", "--labelg", tool]
        p = inj(mode, arg, *base) if mode else drv(*base)
        a = agg_json(root)
        return p, a, a.get("comparison", {}).get("I_NO_IS_set", {})

    case(G, "fixture: the relabelled G14a differs from G14a as a string", refs["same"] != G14A, relabelled=refs["same"])
    p, a, c = agg("same", lab)
    case(G, "real labelg: G14a against a relabelling of itself is accepted", p[0] == 0 and a.get("ok") is True
         and c.get("equal") is True, exit=p[0], said=last_line(p[2]))
    p, a, c = agg("k14", lab)
    case(G, "real labelg: G14a against K14 is refused", p[0] != 0 and a.get("ok") is False and c.get("equal") is False,
         exit=p[0])
    p, a, c = agg("k14", lab, "canon_replace_original", const)
    shutil.copy2(LABELG, lab)
    case(G, "auditor's race (given labelg replaced by a constant canonizer at its first use): G14a against K14 refused",
         p[0] != 0 and a.get("ok") is False and c.get("equal") is not True, exit=p[0], said=last_line(p[2]))
    case(G, "... and the change of the given labelg during the attempt is reported",
         "changed during the attempt" in json.dumps(a.get("problems", [])), problems=a.get("problems", [])[:3])
    p, a, c = agg("same", lab, "frozen_modify_after_freeze", const)
    case(G, "frozen copy replaced before its first run: the attempt is refused", p[0] != 0 and a.get("ok") is not True
         and "changed before it was run" in p[2], exit=p[0], said=last_line(p[2]))
    p, a, c = agg("same", lab, "frozen_modify_during_run", const)
    case(G, "frozen copy replaced at the moment of a run: its output is refused", p[0] != 0 and a.get("ok") is not True
         and "changed while it ran" in p[2], exit=p[0], said=last_line(p[2]))
    p, a, c = agg("k14", const)
    case(G, "constant canonizer given from the start: refused by the self-test", p[0] != 0 and a.get("ok") is not True
         and "self-test" in p[2], exit=p[0], said=last_line(p[2]))
    p, a, c = agg("ident", ident)
    case(G, "identity 'canonizer' given from the start: refused by the self-test", p[0] != 0
         and a.get("ok") is not True and "self-test" in p[2], exit=p[0], said=last_line(p[2]))
    rr = W / "ref_mod.g6"
    rr.write_text(refs["same"] + "\n")
    p = inj("ref_modify", rr, "aggregate", "--config", cfg, "--jobs", 1, "--reference-g6", rr, "--labelg", lab)
    a = agg_json(root)
    case(G, "graph6 reference changed during the attempt: refused", p[0] != 0 and a.get("ok") is False
         and "changed during the attempt" in json.dumps(a.get("problems", [])), exit=p[0])
    p, a, c = agg("same", lab)
    rec = next((x for x in a.get("references", []) if x.get("kind") == "labelg"), {})
    frozen = Path(rec.get("frozen_copy", "/nonexistent"))
    case(G, "recorded labelg: SHA-256 of the given file; a read-only frozen copy with those bytes ran the comparison",
         p[0] == 0 and rec.get("sha256") == sha(lab) and frozen.is_file() and sha(frozen) == rec.get("sha256")
         and (frozen.stat().st_mode & 0o777) == 0o500 and rec.get("sha256", "-") in c.get("compared", ""),
         exit=p[0], keys=sorted(rec))
    root3, cfg3 = campaign("c3")
    csvc = W / "published_copy.csv"
    shutil.copyfile(PUBLISHED, csvc)
    p = inj("ref_modify", csvc, "aggregate", "--config", cfg3, "--jobs", 1, "--reference-csv", csvc)
    a = agg_json(root3)
    case(G, "CSV reference changed during the attempt: refused", p[0] != 0 and a.get("ok") is False
         and "changed during the attempt" in json.dumps(a.get("problems", [])), exit=p[0])


# ------------------------------------------------------------------------------------------------------ transaction
def transaction_cases():
    G = "transaction"
    root, cfg = campaign("tx")
    agg_args = ["aggregate", "--config", cfg, "--jobs", 1]

    def consistent():
        """aggregate.json with ok=true belongs to a terminal ok attempt that names the SHA-256 of aggregate.json."""
        a = agg_json(root)
        if a.get("ok") is not True:
            return True
        at = attempt_record(root, a.get("attempt_id"))
        return at.get("status") == "ok" and at.get("aggregate_sha256") == sha(root / "aggregate.json")

    rc = drv(*agg_args)[0]
    a = agg_json(root)
    at = attempt_record(root, a.get("attempt_id"))
    case(G, "success: exit 0, ok=true, the attempt is ok and names the SHA-256 of aggregate.json", rc == 0
         and a.get("ok") is True and at.get("status") == "ok" and at.get("aggregate_sha256") == sha(root / "aggregate.json"),
         exit=rc, attempt=at.get("status"))
    p = inj("attempt_ok_fail", 0, *agg_args)
    a = agg_json(root)
    at = attempt_record(root, a.get("attempt_id"))
    case(G, "auditor's fault (the final write of the attempt record fails): exit != 0, ok=false, attempt failed",
         p[0] != 0 and a.get("ok") is False and at.get("status") == "failed", exit=p[0], aggregate_ok=a.get("ok"),
         attempt=at.get("status"))
    drv(*agg_args)
    p = inj("count", 0, *agg_args)
    m = re.search(r"OPS=(\d+)", p[2])
    n_ops = int(m.group(1)) if m else 0
    case(G, f"a successful aggregate performs {n_ops} write operations (fsync, rename, file write)", p[0] == 0 and n_ops > 0,
         exit=p[0])
    bad = {"single": [], "persistent": [], "crash": []}
    for k in range(1, n_ops + 1):
        for kind, mode in (("single", "fail_at"), ("persistent", "fail_from"), ("crash", "crash_at")):
            drv(*agg_args)                       # the same starting state for every injection
            before = attempt_ids(root)
            p = inj(mode, k, *agg_args)
            new = attempt_ids(root) - before
            a = agg_json(root)
            at = attempt_record(root, a.get("attempt_id"))
            certified_new = a.get("ok") is True and a.get("attempt_id") in new
            if kind == "single":
                started = [s for s in new if attempt_record(root, s).get("status") == "started"]
                good = p[0] != 0 and a.get("ok") is not True and at.get("status") == "failed" and not started
            else:
                good = p[0] != 0 and not certified_new and consistent()
            if not good:
                bad[kind].append({"k": k, "exit": p[0], "ok": a.get("ok"), "attempt": at.get("status"),
                                  "certified_new": certified_new})
    case(G, f"one write failure at each of the {n_ops} operations: never ok=true; the attempt ends failed",
         n_ops > 0 and not bad["single"], failures=bad["single"][:5])
    case(G, f"persistent write failure from each of the {n_ops} operations on: the attempt is never certified",
         n_ops > 0 and not bad["persistent"], failures=bad["persistent"][:5])
    case(G, f"crash at each of the {n_ops} operations: the attempt is never certified; an ok=true left in place "
            "belongs to a terminal attempt that names its hash", n_ops > 0 and not bad["crash"], failures=bad["crash"][:5])
    drv(*agg_args)
    with open("/dev/full", "w") as full:
        q = subprocess.run([sys.executable, str(DRIVER)] + [str(x) for x in agg_args], stdout=full,
                           stderr=subprocess.PIPE, text=True)
    a = agg_json(root)
    at = attempt_record(root, a.get("attempt_id"))
    case(G, "the summary cannot be printed (stdout on a full device): exit != 0, no ok=true, attempt failed",
         q.returncode != 0 and a.get("ok") is not True and at.get("status") == "failed", exit=q.returncode,
         aggregate_ok=a.get("ok"), attempt=at.get("status"))


# ----------------------------------------------------------------------------------------------------------- worker
def worker_cases():
    G = "worker"
    wrap = W / "geng_wrapper.sh"
    wrap.write_text(f'#!/bin/sh\nexec "{GENG}" "$@"\n')
    wrap.chmod(0o755)
    for name, mode, key in (("the pinned classifier modified after the first slice", "classifier_modify_between_slices",
                             "classifier"),
                            ("the pinned geng modified while a slice runs", "geng_modify_during_slice", "geng")):
        root = W / ("wk_" + key)
        rc, _, e = init(root, 3, 2, wrap)
        cfg = root / "config.json"
        c = json.loads(cfg.read_text())
        target = Path(c["files"][key]["path"])
        original = target.read_bytes()
        p = inj(mode, 0, "worker", "--config", cfg, "--worker-id", 0)
        rec = sorted((root / "receipts").rglob("*.ok.json")) if (root / "receipts").exists() else []
        expected_left = 1 if key == "classifier" else 0
        case(G, f"{name}: no receipt from the changed executable and the worker fails", rc == 0 and p[0] != 0
             and len(rec) == expected_left, exit=p[0], ok_receipts=len(rec), said=last_line(p[2]))
        restore(target, original)
        q = drv("worker", "--config", cfg, "--worker-id", 0)
        rec = sorted((root / "receipts").rglob("*.ok.json"))
        r = drv("aggregate", "--config", cfg, "--jobs", 1)
        case(G, f"{name}: once restored, the worker completes and the campaign aggregates", q[0] == 0 and len(rec) == 2
             and r[0] == 0 and agg_json(root).get("ok") is True, exit=q[0], aggregate=r[0])


# ------------------------------------------------------------------------------------------------------------- main
def main():
    global BIN, DRIVER, SOURCE, W
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default=str(HERE / "results" / "v2.4" / "regressions_r4.json"))
    ap.add_argument("--bin", default=str(BIN), help="classifier recorded in the provenance (default build/atascadas_v2)")
    ap.add_argument("--driver", default=str(DRIVER), help="driver under test (default pipeline/campana_v2.py)")
    ap.add_argument("--source", default=str(SOURCE), help="classifier source compiled by init")
    ap.add_argument("--sections", default=",".join(SECTIONS), help="comma-separated subset of " + ",".join(SECTIONS))
    a = ap.parse_args()
    BIN, DRIVER, SOURCE = Path(a.bin).resolve(), Path(a.driver).resolve(), Path(a.source).resolve()
    sections = [s for s in a.sections.split(",") if s]
    unknown = set(sections) - set(SECTIONS)
    if unknown:
        raise SystemExit(f"unknown sections: {sorted(unknown)}")
    W = Path(a.work).resolve()
    if W.exists():
        shutil.rmtree(W)
    W.mkdir(parents=True)
    for tool in ("gcc", "geng", "labelg"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} is required on PATH")
    (W / "inject_r4.py").write_text(INJECT)
    started = provenance.utc_now()
    prov = provenance.record(binaries=[(BIN, ["--version"])],
                             sources=[SOURCE, DRIVER, V2 / "build.sh", Path(__file__)], tools=["geng", "labelg"])
    funcs = {"init": init_cases, "labelg": labelg_cases, "transaction": transaction_cases, "worker": worker_cases}
    for s in SECTIONS:
        if s in sections:
            try:
                funcs[s]()
            except Exception as e:  # noqa: BLE001  (a section that cannot run is a failure, not a crash of the suite)
                case(s, "section ran to the end", False, error=f"{type(e).__name__}: {e}"[:300])
    res = {"all_pass": all(r["pass"] for r in RESULTS), "n_cases": len(RESULTS),
           "n_failed": sum(not r["pass"] for r in RESULTS), "cases": RESULTS,
           "tools": {"geng": provenance.display_path(GENG), "labelg": provenance.display_path(LABELG),
                     "python": sys.version.split()[0]},
           "driver_under_test": provenance.display_path(DRIVER), "source_under_test": provenance.display_path(SOURCE),
           "sections": sections, "started_utc": started, "finished_utc": provenance.utc_now(), "provenance": prov}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(provenance.check_portable(json.dumps(res, indent=1) + "\n"))
    print(f"{res['n_cases']} cases, {res['n_failed']} failed:", "ALL PASS" if res["all_pass"] else "SOME CASES FAILED")
    sys.exit(0 if res["all_pass"] else 1)


if __name__ == "__main__":
    main()
