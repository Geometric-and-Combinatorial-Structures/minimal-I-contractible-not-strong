#!/usr/bin/env python3
"""Regression tests for round 5 of the external audit (residue of H-29; H-37; pin of labelg), closed by class.

Groups
  preserve  H-29  the auditor's counterexample (the open of the first record of a new attempt fails before the earlier
                  outputs are archived; v2.3 replaced the earlier aggregate.json by the failed one without keeping its
                  bytes) and a sweep over every file-system event of a successful aggregate, with the auditor's event
                  model (open, write, flush, close, fsync, rename, mkdir; before and after each), in three modes: one
                  failure, a persistent failure from that event on, and a crash (os._exit) at that event.  In every run
                  the bytes of the earlier aggregate.json must still be in the campaign (in place or in
                  aggregate_history/), and the certificate contract must hold: exit 0 if and only if aggregate.json
                  names the attempt of this invocation, its record is terminal ok and names the SHA-256 of
                  aggregate.json; the one allowed exception is a failure or a crash after the final rename of
                  aggregate.json took effect (coherent success, nonzero exit), which is why the real exit status is
                  part of the contract; and aggregate.json with ok=true must name an attempt whose record is terminal
                  ok with its SHA-256.  Two cases with two faults in sequence: an error just after the final rename
                  followed by a failure to write the failed aggregate.json (ok=true stays with a record that says
                  failed: that invariant holds only in the fault model of the sweep, while the contract still
                  rejects), and the move to the history failing in the attempt and again in the handler (the earlier
                  aggregate.json stays in place byte for byte, nothing replaces it, the record keeps
                  preservation_error).
  labelpin        --expect-labelg-sha256: the right SHA-256 is accepted and recorded, a wrong one refuses before any use,
                  a malformed one or one without --labelg is a usage error.
  harness   H-37  tests/run_sanitizers.sh with TMPDIR containing spaces, parentheses and brackets: 19 runs, both positive
                  controls report, the other 17 have no report and the documented exit status.

Usage: python3 tests/test_regressions_r5.py --work DIR [--out results/v2.4/regressions_r5.json] [--driver DRIVER]
       [--sanitizer-script SCRIPT] [--sections preserve,labelpin,harness]
--driver and --sanitizer-script run the same cases against older files (sensitivity: with v2.3 the preserve,
labelpin and harness groups must fail).  Requires gcc, geng and labelg on PATH and ./build.sh outputs.
Exit status 0 only if every case behaves as stated.
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
SANITIZERS = HERE / "run_sanitizers.sh"
GENG = shutil.which("geng")
LABELG = shutil.which("labelg")
SECTIONS = ["preserve", "labelpin", "harness"]
HOME = os.path.expanduser("~")
G14A = "M?b@bFHNEk@~|k}U?"
W = None
RESULTS = []

INJECT = r'''
import atexit, builtins, importlib.util, io, json, os, sys
from pathlib import Path
driver, rootstr, mode, rest = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[5:]
target = int(sys.argv[4]) if mode != "stages" else None
# mode "stages": a JSON list of [kind, "eq" | "prefix", path relative to ROOT, count]; stage s+1 is armed only after
# stage s has failed `count` matching events
stages = json.loads(sys.argv[4]) if mode == "stages" else []
ROOT, MAIN = Path(rootstr).resolve(), os.getpid()
spec = importlib.util.spec_from_file_location("campana", driver)
m = importlib.util.module_from_spec(spec)
sys.modules["campana"] = m
spec.loader.exec_module(m)
trace, state = [], {"failed": False, "stage": 0, "left": stages[0][3] if stages else 0}


def inroot(p):
    try:
        return Path(p).absolute().is_relative_to(ROOT)
    except (TypeError, ValueError):
        return False


def event(kind, path):
    if os.getpid() != MAIN or not inroot(path):
        return
    trace.append([kind, str(path)])
    i = len(trace)
    if mode == "count":
        return
    if mode == "stages":
        s = state["stage"]
        if s < len(stages):
            kind_s, how, rel_s, _ = stages[s]
            rel = str(Path(path).absolute().relative_to(ROOT))
            if kind == kind_s and (rel == rel_s if how == "eq" else rel.startswith(rel_s)):
                state["left"] -= 1
                if state["left"] == 0:
                    state["stage"] = s + 1
                    state["left"] = stages[s + 1][3] if s + 1 < len(stages) else 0
                raise OSError(f"injected stage {s + 1} failure at event {i} {kind} {rel}")
        return
    if (mode == "single" and i == target) or (mode == "persistent" and (i >= target)):
        raise OSError(f"injected {mode} failure at event {i} {kind}")
    if mode == "crash" and i == target:
        os._exit(137)


atexit.register(lambda: os.getpid() == MAIN and sys.stderr.write("\nTRACE=" + json.dumps(trace) + "\n"))


class Proxy:
    def __init__(self, f, path):
        self.f, self.path = f, path

    def __getattr__(self, k):
        return getattr(self.f, k)

    def __enter__(self):
        self.f.__enter__()
        return self

    def __exit__(self, *a):
        event("close.before", self.path)
        r = self.f.__exit__(*a)
        event("close.after", self.path)
        return r

    def write(self, data):
        event("write.before", self.path)
        r = self.f.write(data)
        event("write.after", self.path)
        return r

    def flush(self):
        event("flush.before", self.path)
        r = self.f.flush()
        event("flush.after", self.path)
        return r


def wrap_open(real):
    def f(path, mode="r", *a, **k):
        if isinstance(mode, str) and any(x in mode for x in "wax+") and inroot(path):
            event("open.before", path)
            v = real(path, mode, *a, **k)
            event("open.after", path)
            return Proxy(v, path)
        return real(path, mode, *a, **k)
    return f


builtins.open = wrap_open(builtins.open)
io.open = wrap_open(io.open)
real_fsync, real_replace, real_mkdir = os.fsync, os.replace, os.mkdir


def fsync(fd):
    try:
        p = os.readlink(f"/proc/self/fd/{fd}")
    except OSError:
        p = ""
    event("fsync.before", p)
    r = real_fsync(fd)
    event("fsync.after", p)
    return r


def replace(a, b, *x, **y):
    event("replace.before", b)
    r = real_replace(a, b, *x, **y)
    event("replace.after", b)
    return r


def mkdir(p, *x, **y):
    event("mkdir.before", p)
    r = real_mkdir(p, *x, **y)
    event("mkdir.after", p)
    return r


os.fsync, os.replace, os.mkdir = fsync, replace, mkdir
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
    print(("PASS " if ok else "FAIL ") + f"[{group}] {name}", json.dumps(info)[:230], flush=True)


def last_line(text):
    lines = [l for l in (text or "").strip().splitlines() if l.strip() and not l.startswith("TRACE=")]
    return lines[-1][:200] if lines else ""


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def geng_pins(geng):
    out = subprocess.run([str(geng), "--version"], capture_output=True, text=True)
    mm = re.search(r"version\s+([0-9]+\.[0-9]+)", out.stdout + out.stderr)
    return ["--expect-geng-version", mm.group(1) if mm else "none", "--expect-geng-sha256", sha(geng)]


def drv(*args):
    p = subprocess.run([sys.executable, str(DRIVER)] + [str(a) for a in args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def inj(root, mode, k, *args):
    p = subprocess.run([sys.executable, str(W / "inject_r5.py"), str(DRIVER), str(root), mode, str(k)]
                       + [str(a) for a in args], capture_output=True, text=True)
    mt = re.search(r"^TRACE=(.*)$", p.stderr, re.M)
    return p.returncode, p.stdout, p.stderr, (json.loads(mt.group(1)) if mt else None)


def campaign(name, n=3, mod=2, geng=None):
    root = W / name
    geng = geng or GENG
    rc, _, e = drv("init", "--root", root, "--n", n, "--mod", mod, "--workers", 1, "--mode", "tabla", "--geng", geng,
                   "--geng-args=-c", "--source", SOURCE, *geng_pins(geng))
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


def record(root, aid):
    try:
        return json.loads((root / "aggregate_attempts" / f"{aid}.json").read_text())
    except (OSError, ValueError, TypeError):
        return {}


def attempt_ids(root):
    d = root / "aggregate_attempts"
    return {p.stem for p in d.glob("*.json")} if d.exists() else set()


def preserved(root, before):
    """Where the exact bytes of the earlier aggregate.json are now (in place or in the history)."""
    spots = [root / "aggregate.json"] + sorted((root / "aggregate_history").glob("*/aggregate.json"))
    return [str(p.relative_to(root)) for p in spots if p.is_file() and p.read_bytes() == before]


def certified(root, new):
    a = agg_json(root)
    if a.get("ok") is not True or a.get("attempt_id") not in new:
        return False
    rec = record(root, a.get("attempt_id"))
    return rec.get("status") == "ok" and rec.get("aggregate_sha256") == sha(root / "aggregate.json")


def consistent(root):
    a = agg_json(root)
    if a.get("ok") is not True:
        return True
    rec = record(root, a.get("attempt_id"))
    return rec.get("status") == "ok" and rec.get("aggregate_sha256") == sha(root / "aggregate.json")


# --------------------------------------------------------------------------------------------------------- preserve
def preserve_cases():
    G = "preserve"
    root, cfg = campaign("pv")
    args = ["aggregate", "--config", cfg, "--jobs", 1]
    drv(*args)
    drv(*args)       # the history directory now exists: the event numbering of the sweep runs is stable from here
    rc, _, _, trace = inj(root, "count", 0, *args)
    n_ev = len(trace or [])
    pub = max((i + 1 for i, (k, p) in enumerate(trace or []) if k == "replace.after" and p.endswith("/aggregate.json")),
              default=None)
    first_open = next((i + 1 for i, (k, p) in enumerate(trace or []) if k == "open.before" and "/aggregate_attempts/" in p),
                      None)
    case(G, f"a successful aggregate goes through {n_ev} file-system events (final rename of aggregate.json: event {pub})",
         rc == 0 and n_ev > 0 and pub is not None and first_open is not None, exit=rc, first_record_open=first_open)
    # the auditor's counterexample
    drv(*args)
    before = (root / "aggregate.json").read_bytes()
    old = json.loads(before)
    ids0 = attempt_ids(root)
    rc, _, err, _ = inj(root, "single", first_open, *args)
    new = attempt_ids(root) - ids0
    a = agg_json(root)
    spots = preserved(root, before)
    case(G, "auditor's counterexample (the open of the first record fails): the attempt fails and the earlier "
            "aggregate's bytes are kept", rc != 0 and a.get("ok") is False and a.get("attempt_id") in new
         and any(s.startswith("aggregate_history/") for s in spots)
         and record(root, old.get("attempt_id")).get("status") == "ok", exit=rc, kept_at=spots, said=last_line(err))
    bad = {"single": [], "persistent": [], "crash": []}
    allowed_crash_success = []
    for k in range(1, n_ev + 1):
        for mode in ("single", "persistent", "crash"):
            drv(*args)
            before = (root / "aggregate.json").read_bytes()
            ids0 = attempt_ids(root)
            rc, _, err, _ = inj(root, mode, k, *args)
            new = attempt_ids(root) - ids0
            spots = preserved(root, before)
            cert = certified(root, new)
            problems = []
            if not spots:
                problems.append("earlier aggregate lost")
            if not consistent(root):
                problems.append("ok=true without a terminal record naming its digest")
            if rc == 0 and not cert:
                problems.append("exit 0 without a certificate for this attempt")
            if rc != 0 and cert:
                if mode in ("crash", "persistent") and pub is not None and k >= pub:
                    allowed_crash_success.append((mode, k))     # the final rename had taken effect
                else:
                    problems.append("this attempt certified although the invocation failed")
            if mode == "single" and rc != 0:
                a = agg_json(root)
                started = [i for i in new if record(root, i).get("status") == "started"]
                untouched = not new and (root / "aggregate.json").is_file() \
                    and (root / "aggregate.json").read_bytes() == before     # failed before any attempt existed
                if not (untouched or (a.get("ok") is False and a.get("attempt_id") in new and not started)):
                    problems.append("single failure did not end in a failed aggregate.json of this attempt")
            if problems:
                bad[mode].append({"event": k, "kind": trace[k - 1][0], "exit": rc, "problems": problems})
    for mode in ("single", "persistent", "crash"):
        case(G, f"{mode} fault at each of the {n_ev} events: earlier aggregate kept, ok=true only with a terminal ok "
                f"record naming its digest, certificate contract holds",
             n_ev > 0 and not bad[mode], failing_events=len(bad[mode]),
             failing_event_numbers=[b["event"] for b in bad[mode]], failures=bad[mode][:10])
    case(G, "the only coherent success with a nonzero exit comes after the final rename took effect",
         all(k >= (pub or 0) for _, k in allowed_crash_success), after_final_rename=allowed_crash_success)
    # two faults in sequence (outside the model of the sweep)
    drv(*args)
    before = (root / "aggregate.json").read_bytes()
    ids0 = attempt_ids(root)
    spec = [["replace.after", "eq", "aggregate.json", 1], ["open.before", "prefix", "aggregate.json.tmp.", 1]]
    rc, _, err, _ = inj(root, "stages", json.dumps(spec), *args)
    new = attempt_ids(root) - ids0
    a = agg_json(root)
    rec = record(root, a.get("attempt_id"))
    case(G, "two faults: an error just after the final rename, then the failed aggregate.json cannot be written: "
            "ok=true stays with a record that says failed (the invariant needs the fault model); the contract rejects",
         rc != 0 and a.get("ok") is True and a.get("attempt_id") in new and rec.get("status") == "failed"
         and not consistent(root) and not certified(root, new) and bool(preserved(root, before)),
         exit=rc, record_status=rec.get("status"), said=last_line(err))
    drv(*args)
    before = (root / "aggregate.json").read_bytes()
    ids0 = attempt_ids(root)
    rc, _, err, _ = inj(root, "stages", json.dumps([["replace.before", "prefix", "aggregate_history/", 2]]), *args)
    new = attempt_ids(root) - ids0
    recs = [record(root, i) for i in sorted(new)]
    case(G, "two faults: the move to the history fails in the attempt and again in the handler: the earlier "
            "aggregate.json stays in place byte for byte, nothing replaces it, the record keeps preservation_error",
         rc != 0 and (root / "aggregate.json").read_bytes() == before and len(recs) == 1
         and recs[0].get("status") == "failed" and bool(recs[0].get("preservation_error")),
         exit=rc, records=[{k: r.get(k) for k in ("status", "preservation_error")} for r in recs], said=last_line(err))


# --------------------------------------------------------------------------------------------------------- labelpin
def labelpin_cases():
    G = "labelpin"
    fake = W / "geng_g14a.sh"
    fake.write_text("#!/bin/sh\ncase \"$1\" in --version) echo 'Nauty&Traces version 2.9301 (test fixture)'; exit 0;; "
                    "--help) echo 'test fixture: prints one graph'; exit 0;; esac\n"
                    f"echo '{G14A}'\necho '>Z 1 graphs generated in 0.00 sec' >&2\n")
    fake.chmod(0o755)
    root, cfg = campaign("lp", n=14, mod=1, geng=fake)
    lab = W / "labelg_given"
    shutil.copy2(LABELG, lab)
    ref = W / "ref_g14a.g6"
    ref.write_text(G14A + "\n")
    base = ["aggregate", "--config", cfg, "--jobs", 1, "--reference-g6", ref, "--labelg", lab]
    rc, _, err = drv(*base, "--expect-labelg-sha256", sha(lab))
    a = agg_json(root)
    rec = next((x for x in a.get("references", []) if x.get("kind") == "labelg"), {})
    case(G, "the right --expect-labelg-sha256 is accepted and recorded", rc == 0 and a.get("ok") is True
         and rec.get("expected_sha256") == sha(lab), exit=rc, said=last_line(err))
    rc, _, err = drv(*base, "--expect-labelg-sha256", "0" * 64)
    a = agg_json(root)
    case(G, "a wrong --expect-labelg-sha256 refuses the attempt before labelg is used", rc != 0
         and a.get("ok") is False and "differs from --expect-labelg-sha256" in err, exit=rc, said=last_line(err))
    rc, _, err = drv(*base, "--expect-labelg-sha256", "xyz")
    case(G, "a malformed --expect-labelg-sha256 is refused", rc != 0 and agg_json(root).get("ok") is not True, exit=rc)
    rc, _, err = drv("aggregate", "--config", cfg, "--jobs", 1, "--expect-labelg-sha256", sha(lab))
    case(G, "--expect-labelg-sha256 without --labelg is refused", rc != 0 and agg_json(root).get("ok") is not True,
         exit=rc)


# ---------------------------------------------------------------------------------------------------------- harness
def harness_cases():
    G = "harness"
    tmp = W / "tmp dir (with parens) [and brackets]"
    tmp.mkdir()
    out = W / "sanitizer with spaces.txt"
    env = dict(os.environ, TMPDIR=str(tmp))
    # a script given with --sanitizer-script is run from tests/, as in the repository, because it finds build/ and
    # ../data/ from its own location; the temporary copy is removed afterwards
    script, copy = SANITIZERS, None
    if SANITIZERS.parent != HERE:
        copy = HERE / f".sanitizer_under_test_{os.getpid()}.sh"
        shutil.copyfile(SANITIZERS, copy)
        script = copy
    try:
        p = subprocess.run(["bash", str(script), str(out)], capture_output=True, text=True, env=env)
    finally:
        if copy is not None:
            copy.unlink(missing_ok=True)
    log = out.read_text(errors="replace") if out.exists() else ""
    runs = re.search(r"# runs: (\d+)", log)
    verdict = [l for l in p.stdout.splitlines() if l.startswith("SANITIZERS:")]
    case(G, "run_sanitizers.sh with TMPDIR containing spaces, parentheses and brackets: 19 runs, PASS",
         p.returncode == 0 and runs is not None and runs.group(1) == "19" and verdict and "PASS" in verdict[-1]
         and "19 of 19" in verdict[-1], exit=p.returncode, verdict=verdict[-1:] if verdict else last_line(p.stderr),
         script_sha256=sha(SANITIZERS))
    # a local path can reach the log in three forms: absolute, with HOME shown as ~, or only partly (messages are cut
    # at 110 characters); a 24-character prefix of each form must not occur
    forms = {"work directory, absolute": str(W), "temporary directory, absolute": str(tmp),
             "repository, absolute": str(REPO), "home directory": HOME}
    if HOME and str(W).startswith(HOME + "/"):
        forms["work directory, with HOME shown as ~"] = "~" + str(W)[len(HOME):]
    leaks = sorted(name for name, f in forms.items() if f and f[:24] in log)   # recorded by kind, not by content
    case(G, "... and its log records no local path, in any form", out.exists() and not leaks, log_bytes=len(log),
         leaked_forms=leaks)


# ------------------------------------------------------------------------------------------------------------- main
def main():
    global DRIVER, SANITIZERS, W
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default=str(HERE / "results" / "v2.4" / "regressions_r5.json"))
    ap.add_argument("--driver", default=str(DRIVER), help="driver under test (default pipeline/campana_v2.py)")
    ap.add_argument("--sanitizer-script", default=str(SANITIZERS), help="sanitizer battery under test")
    ap.add_argument("--sections", default=",".join(SECTIONS), help="comma-separated subset of " + ",".join(SECTIONS))
    a = ap.parse_args()
    DRIVER, SANITIZERS = Path(a.driver).resolve(), Path(a.sanitizer_script).resolve()
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
    (W / "inject_r5.py").write_text(INJECT)
    started = provenance.utc_now()
    prov = provenance.record(binaries=[(V2 / "build" / "atascadas_v2", ["--version"])],
                             sources=[SOURCE, DRIVER, SANITIZERS, V2 / "build.sh", Path(__file__)],
                             tools=["geng", "labelg"])
    funcs = {"preserve": preserve_cases, "labelpin": labelpin_cases, "harness": harness_cases}
    for s in SECTIONS:
        if s in sections:
            try:
                funcs[s]()
            except Exception as e:  # noqa: BLE001
                case(s, "section ran to the end", False, error=f"{type(e).__name__}: {e}"[:300])
    res = {"all_pass": all(r["pass"] for r in RESULTS), "n_cases": len(RESULTS),
           "n_failed": sum(not r["pass"] for r in RESULTS), "cases": RESULTS,
           "tools": {"geng": provenance.display_path(GENG), "labelg": provenance.display_path(LABELG),
                     "python": sys.version.split()[0]},
           "driver_under_test": provenance.display_path(DRIVER),
           "sanitizer_script_under_test": provenance.display_path(SANITIZERS), "sections": sections,
           "started_utc": started, "finished_utc": provenance.utc_now(), "provenance": prov}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(provenance.check_portable(json.dumps(res, indent=1) + "\n"))
    print(f"{res['n_cases']} cases, {res['n_failed']} failed:", "ALL PASS" if res["all_pass"] else "SOME CASES FAILED")
    sys.exit(0 if res["all_pass"] else 1)


if __name__ == "__main__":
    main()
