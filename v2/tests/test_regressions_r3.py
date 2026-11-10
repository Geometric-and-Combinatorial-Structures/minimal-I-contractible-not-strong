#!/usr/bin/env python3
"""Regression tests for the findings of round 3 of the external audit (H-22, H-23, H-24, H-29, H-35; request S4).

Every case reproduces a counterexample of the auditor's round-3 report (AUDIT_OUT/ronda3/DICTAMEN_RONDA3.md) or
extends it to the class of inputs it belongs to: the report asks for the defects to be closed by class, not by
example.

Groups
  init        H-23  unparsable --geng-args or --cflags, `geng --help` failing (exit 42) or silent: nothing is
                    written.  A failure after ROOT exists, injected at the chmod of config.sha256 and at the
                    final marker, leaves INIT_FAILED.txt and every subcommand refuses the root; a root whose
                    INIT_COMPLETE.json is missing (init cut short) or certifies another config is refused.
  receipt     H-24  the auditor's five patches (NaN and Infinity seconds, nonsense and reversed UTC times, booleans
                    as identity); a systematic mutation of every key of a real receipt with values of the wrong
                    type, out of range or of another format; every missing key; extra keys; the clock tolerances
                    on both sides of their bounds; NaN, Infinity, a repeated key and `true` for 1 in the receipt
                    files, refused by aggregate and by the resuming worker and counted unreadable by status.
  reference   H-22  repeated CSV column (the auditor's case), uneven rows, empty column name, non-integer cell,
                    non-UTF-8 and missing files, --expect without value, --expect=-1-Dis=V, the old batch form,
                    repeated and malformed --expect values, empty graph6 reference, --labelg without
                    --reference-g6; the path and SHA-256 of every reference recorded in aggregate.json.
  aggregate   H-29  a busy worker lock after an earlier ok=true (the auditor's aggregate_active) leaves ok=false
                    in the normal location, the earlier result archived and a failed attempt record; a concurrent
                    aggregate is refused and touches nothing; status survives null, [], {} and scalar receipts;
                    no attempt record is left in state started.
  classifier  S4    every early exit of the classifier (usage errors, --version, lack of memory) reports a write
                    error on its streams with status 6; the ordinary statuses are unchanged.
  harness     H-35  the argv recorded in a result never carries local directories (absolute paths that do not
                    exist yet and --option=PATH are normalized), so check_portable accepts it.

Usage: python3 tests/test_regressions_r3.py --work DIR [--out results/v2.4/regressions_r3.json] [--bin BINARY]
       [--driver DRIVER --source SOURCE] [--sections init,receipt,reference,aggregate,classifier,harness]
--bin, --driver and --source run the same cases against an older classifier, driver and source (sensitivity
check: with the v2.1 files most cases must fail).  Requires gcc, geng and labelg (nauty) on PATH and build/atascadas_v2 (./build.sh).
Exit status 0 only if every case behaves as stated.
"""
import argparse, copy, csv, datetime, fcntl, hashlib, importlib.util, json, os, re, resource, shutil, subprocess, sys
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
PUBLISHED = REPO / "data" / "raw_classifier_reference.csv"
SECTIONS = ["init", "receipt", "reference", "aggregate", "classifier", "harness"]
HOME = os.path.expanduser("~")
M = None
W = None
RESULTS = []


def load_driver(path):
    spec = importlib.util.spec_from_file_location("campana", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def scrub(text):
    """Local directories never enter the results (check_portable refuses them)."""
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


def init(root, n=3, mod=2, workers=1, mode="tabla", geng=None, geng_args="-c", extra=(), runner=None):
    geng = geng or GENG
    args = ["init", "--root", root, "--n", n, "--mod", mod, "--workers", workers, "--mode", mode, "--geng", geng,
            f"--geng-args={geng_args}", "--source", SOURCE, *geng_pins(geng), *extra]
    if runner:      # the driver run through a wrapper that injects a failure
        p = subprocess.run([sys.executable] + [str(x) for x in runner] + [str(x) for x in args],
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr
    return drv(*args)


def campaign(name, workers=1):
    """A complete campaign n=3, mod=2, mode tabla: init, every worker, aggregate.  Returns (root, config, exit)."""
    root = W / name
    rc, _, e = init(root, workers=workers)
    if rc != 0:
        raise RuntimeError(f"init of {name} failed: {last_line(e)}")
    cfg = root / "config.json"
    for w in range(workers):
        rcw, _, e = drv("worker", "--config", cfg, "--worker-id", w)
        if rcw != 0:
            raise RuntimeError(f"worker {w} of {name} failed: {last_line(e)}")
    return root, cfg, drv("aggregate", "--config", cfg, "--jobs", 1)[0]


def agg_json(root):
    try:
        return json.loads((root / "aggregate.json").read_text())
    except (OSError, ValueError):
        return {}


def read_bytes(path):
    try:
        return path.read_bytes()
    except OSError:
        return None


def history(root):
    d = root / "aggregate_history"
    return sorted(d.iterdir()) if d.is_dir() else []


def attempts(root):
    d = root / "aggregate_attempts"
    return sorted(d.glob("*.json")) if d.exists() else []


def dt(ts):
    return datetime.datetime.fromisoformat(ts)


def shift(ts, seconds):
    return (dt(ts) + datetime.timedelta(seconds=seconds)).isoformat()


# ------------------------------------------------------------------------------------------------------ init (H-23)
INJECT = r'''
import importlib.util, os, sys
driver, mode, target = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("campana", driver)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
if mode == "chmod":
    real = os.chmod
    def chmod(p, *a, **k):
        if os.path.basename(str(p)) == target:
            raise PermissionError("injected failure at chmod " + target)
        return real(p, *a, **k)
    os.chmod = chmod
else:
    real_aj = m.atomic_json
    def aj(path, obj, *a, **k):
        if os.path.basename(str(path)) == target:
            raise OSError("injected failure writing " + target)
        return real_aj(path, obj, *a, **k)
    m.atomic_json = aj
sys.argv = [driver] + sys.argv[4:]
m.main()
'''


def refusals(cfg):
    """Exit status and last stderr line of worker, status and aggregate on one campaign."""
    out = {}
    for sub, args in (("worker", ("worker", "--config", cfg, "--worker-id", 0)), ("status", ("status", "--config", cfg)),
                      ("aggregate", ("aggregate", "--config", cfg, "--jobs", 1))):
        rc, _, e = drv(*args)
        out[sub] = (rc, last_line(e))
    return out


def init_cases():
    G = "init"
    for name, tag, kw in (("unclosed quote in --geng-args", "gengargs", {"geng_args": "-c '"}),
                          ("unclosed quote in --cflags", "cflags", {"extra": ("--cflags=-O3 '",)})):
        root = W / ("i_" + tag)
        rc, _, e = init(root, **kw)
        case(G, name + ": refused before ROOT exists", rc != 0 and not root.exists(), exit=rc,
             root_exists=root.exists(), said=last_line(e))
    for name, tag, body in (("geng --help exits 42", "help42", 'if [ "$1" = "--help" ]; then exit 42; fi\n'),
                            ("geng --help prints nothing", "helpsilent", 'if [ "$1" = "--help" ]; then exit 0; fi\n')):
        fake = W / f"fake_{tag}.sh"
        fake.write_text("#!/bin/sh\n" + body + f'exec "{GENG}" "$@"\n')
        fake.chmod(0o755)
        root = W / ("i_" + tag)
        rc, _, e = init(root, geng=fake)
        case(G, name + ": refused before ROOT exists", rc != 0 and not root.exists(), exit=rc,
             root_exists=root.exists(), said=last_line(e))
    inj = W / "inject.py"
    inj.write_text(INJECT)
    for name, mode, target in (("failure at the chmod of config.sha256", "chmod", "config.sha256"),
                               ("failure writing the final marker", "atomic", "INIT_COMPLETE.json")):
        root = W / ("i_late_" + mode)
        rc, _, e = init(root, runner=[inj, DRIVER, mode, target])
        cfg = root / "config.json"
        failed, marker, late = (root / "INIT_FAILED.txt").exists(), (root / "INIT_COMPLETE.json").exists(), cfg.exists()
        case(G, name + ": init fails late and leaves INIT_FAILED.txt and no marker",
             rc != 0 and failed and not marker and late, exit=rc, init_failed=failed, marker=marker,
             config_written=late)
        out = refusals(cfg)
        case(G, name + ": worker, status and aggregate refuse the root",
             all(v[0] != 0 for v in out.values()) and "INIT_FAILED" in out["worker"][1], refusals=out)
    root = W / "i_good"
    rc, _, e = init(root)
    cfg, mk = root / "config.json", root / "INIT_COMPLETE.json"
    try:
        mark = json.loads(mk.read_text())
    except (OSError, ValueError):
        mark = {}
    rcw = drv("worker", "--config", cfg, "--worker-id", 0)[0]
    # config_sha256 is the SHA-256 of the canonical JSON of the config (sorted keys, compact separators), as since v2.0
    csha = hashlib.sha256(canon(json.loads(cfg.read_text())).encode()).hexdigest() if cfg.exists() else None
    pin = (root / "config.sha256").read_text().split()[0] if (root / "config.sha256").exists() else None
    case(G, "a finished init certifies its config in INIT_COMPLETE.json (= config.sha256) and the worker runs",
         rc == 0 and csha is not None and mark.get("config_sha256") == csha == pin and rcw == 0, exit=rc, worker=rcw)
    saved = mk.read_text() if mk.exists() else None
    if mk.exists():
        mk.unlink()
    out = refusals(cfg)
    case(G, "a root without INIT_COMPLETE.json (init cut short) is refused by worker, status and aggregate",
         all(v[0] != 0 for v in out.values()) and "did not finish" in out["worker"][1], refusals=out)
    mk.write_text(json.dumps({"schema": getattr(M, "SCHEMA", "campana_v2/2"), "config_sha256": "0" * 64,
                              "utc": "2026-10-17T00:00:00+00:00"}))
    rcw, _, e = drv("worker", "--config", cfg, "--worker-id", 0)
    case(G, "an INIT_COMPLETE.json that certifies another config is refused",
         rcw != 0 and "does not certify" in e, exit=rcw, said=last_line(e))
    if saved is not None:
        mk.write_text(saved)


# --------------------------------------------------------------------------------------------------- receipts (H-24)
INTS = ("r", "mod", "worker_id", "exit_geng", "exit_classifier")
STREAMS = ("geng_stderr", "classifier_stderr", "result_stdout")


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def wrong_values(k, v):
    """Values that must make the receipt invalid when they replace v under key k."""
    if k in INTS:
        out = [True, False, None, str(v), float(v), v + 1, -1, [], {}]
    elif k == "seconds":
        out = [True, False, None, str(v), float("nan"), float("inf"), float("-inf"), -0.001, [], {}]
    elif k in ("utc_start", "utc_end"):
        out = [None, 5, "", "yesterday", v.replace("+00:00", "Z"), v.replace("+00:00", "+01:00"), v[:10], v + " ",
               "2026-13-01T00:00:00+00:00", "2000-01-01T00:00:00+00:00", "2100-01-01T00:00:00+00:00"]
    elif k == "host":
        out = [None, "", 5, True, [], {}]
    elif k.startswith("slurm_"):
        out = ["", 5, 0, True, [], {}]
    elif k == "config_sha256" or k.endswith("_sha256"):
        out = [None, "", "0" * 64, v.upper(), v[:-1], 5]
    elif k == "schema":
        out = [None, "", "campana_v2/1", 2]
    elif k == "status":
        out = [None, "", "running", "failed", True]
    elif k in ("cmd_geng", "cmd_classifier"):
        out = [None, [], v + ["x"], v[:-1], " ".join(v), {}]
    elif k in STREAMS:
        out = [None, 5, v + "x", v + "\n", []]
    elif k in ("counts", "memo"):
        out = [None, [], {}, {**v, "extra": 0}]
        out += [{**v, kk: x + 1} for kk, x in v.items()] + [{**v, kk: float(x)} for kk, x in v.items()]
        out += [{**v, kk: (x == 1) if x in (0, 1) else str(x)} for kk, x in v.items()]
        out += [{kk: x for kk, x in v.items() if kk != drop} for drop in v]
    elif k == "records":
        out = [None, [], {}, {**v, "extra": []}] + [{**v, kk: list(x) + ["Bw"]} for kk, x in v.items()]
        out += [{kk: x for kk, x in v.items() if kk != drop} for drop in v]
    else:
        out = [None]
    return [x for x in out if canon(x) != canon(v) or type(x) is not type(v)]


def receipt_cases():
    G = "receipt"
    root, cfgp, rca = campaign("rc")
    cfg, cfgsha = M.load_config(cfgp)
    p0, p1 = M.receipt_path(cfg, 0), M.receipt_path(cfg, 1)
    d0 = json.loads(p0.read_text())

    def verdict(d, **kw):
        try:
            M.validate_receipt(cfg, cfgsha, 0, d, **kw)
            return "accepted"
        except M.SliceError as e:
            return "rejected: " + str(e)[:120]
        except Exception as e:  # noqa: BLE001  (a crash is not a controlled refusal)
            return f"crashed: {type(e).__name__}: {e}"[:160]

    v = verdict(copy.deepcopy(d0))
    case(G, "baseline: the real receipt of slice 0 is accepted", rca == 0 and v == "accepted", aggregate=rca, verdict=v)
    patches = {"nan_seconds": {"seconds": float("nan")}, "infinity_seconds": {"seconds": float("inf")},
               "nonsense_utc": {"utc_start": "yesterday", "utc_end": "tomorrow"},
               "reversed_utc": {"utc_end": shift(d0["utc_start"], -3600)},
               "boolean_identity": {"r": False, "exit_geng": False, "exit_classifier": False}}
    for name, patch in patches.items():
        v = verdict({**copy.deepcopy(d0), **patch})
        case(G, f"auditor's patch {name} rejected", v.startswith("rejected"), verdict=v)
    v = verdict({**copy.deepcopy(d0), "utc_end": shift(d0["utc_start"], -3600)})
    case(G, "reversed times are rejected by the order check itself", "out of order" in v, verdict=v)
    total = 0
    for k in sorted(d0):
        vals, bad = wrong_values(k, d0[k]), []
        for x in vals:
            d = copy.deepcopy(d0)
            d[k] = x
            res = verdict(d)
            if not res.startswith("rejected"):
                bad.append((repr(x)[:40], res))
        total += len(vals)
        case(G, f"every wrong value of {k} rejected ({len(vals)} values)", vals and not bad, not_rejected=bad[:5])
    bad = []
    for k in sorted(d0):
        d = copy.deepcopy(d0)
        del d[k]
        res = verdict(d)
        if not res.startswith("rejected"):
            bad.append((k, res))
    case(G, f"every single missing key rejected ({len(d0)} keys; {total} wrong values above)", not bad,
         not_rejected=bad[:5])
    for extra in ({"extra": 1}, {"error": "x"}, {"comment": None}):
        v = verdict({**copy.deepcopy(d0), **extra})
        case(G, f"extra key {next(iter(extra))!r} rejected", v.startswith("rejected"), verdict=v)
    case(G, "the schema keys are exactly the keys the worker writes",
         set(d0) == set(getattr(M, "RECEIPT_KEYS", ())), keys=len(d0))
    born, end = cfg.get("created_utc", d0["utc_start"]), dt(d0["utc_end"])
    tol = [("utc_start 4 min before the campaign was created: accepted", {"utc_start": shift(born, -240)}, {}, True),
           ("utc_start 6 min before the campaign was created: rejected", {"utc_start": shift(born, -360)}, {}, False),
           ("utc_end 4 s before utc_start: accepted", {"utc_end": shift(d0["utc_start"], -4)}, {}, True),
           ("utc_end 6 s before utc_start: rejected", {"utc_end": shift(d0["utc_start"], -6)}, {}, False),
           ("utc_end 4 min after the validation: accepted", {"utc_end": shift(d0["utc_end"], 240)}, {"now": end}, True),
           ("utc_end 6 min after the validation: rejected", {"utc_end": shift(d0["utc_end"], 360)}, {"now": end}, False)]
    for name, patch, kw, want in tol:
        v = verdict({**copy.deepcopy(d0), **patch}, **kw)
        case(G, "clock tolerance: " + name, (v == "accepted") if want else v.startswith("rejected"), verdict=v)
    text0, text1 = p0.read_text(), p1.read_text()

    def file_case(name, path, text, original):
        if text == original:
            case(G, name + ": mutation applied", False)
            return
        path.write_text(text)
        rcs, out, _ = drv("status", "--config", cfgp)
        st = json.loads(out) if rcs == 0 and out.strip() else {}
        rcag, _, _ = drv("aggregate", "--config", cfgp, "--jobs", 1)
        agg = agg_json(root)
        before = path.read_bytes()
        rcw, _, ew = drv("worker", "--config", cfgp, "--worker-id", 0)
        untouched = path.read_bytes() == before
        path.write_text(original)
        case(G, name + ": status counts it unreadable, aggregate and the resuming worker refuse it",
             st.get("ok_receipts_unreadable") == 1 and rcag != 0 and agg.get("ok") is False and rcw != 0 and untouched,
             unreadable=st.get("ok_receipts_unreadable"), aggregate=rcag, worker=rcw, receipt_untouched=untouched)

    file_case("NaN in the receipt file", p0, re.sub(r'"seconds": [-+0-9.eE]+', '"seconds": NaN', text0), text0)
    file_case("Infinity in the receipt file", p0, re.sub(r'"seconds": [-+0-9.eE]+', '"seconds": Infinity', text0), text0)
    file_case("repeated key in the receipt file", p0, text0.replace("{", '{"r": 0, ', 1), text0)
    file_case("true written for r = 1", p1, text1.replace('"r": 1,', '"r": true,', 1), text1)
    rcag = drv("aggregate", "--config", cfgp, "--jobs", 1)[0]
    case(G, "with the receipts restored aggregate succeeds again", rcag == 0 and agg_json(root).get("ok") is True,
         exit=rcag)


# ------------------------------------------------------------------------------------------------- references (H-22)
def reference_cases():
    G = "reference"
    root, cfgp, rca = campaign("rf")
    case(G, "baseline campaign n=3 aggregates", rca == 0 and agg_json(root).get("ok") is True, exit=rca)

    def run(*extra):
        n0 = len(attempts(root))
        rc, _, err = drv("aggregate", "--config", cfgp, "--jobs", 1, *extra)
        return rc, err, agg_json(root), len(attempts(root)) - n0

    rows = list(csv.reader([l for l in PUBLISHED.read_text().splitlines() if l.strip() and not l.startswith("#")]))
    header = [h.strip() for h in rows[0]]
    row3 = next(r for r in rows[1:] if r[header.index("n")].strip() == "3")
    i = header.index("connected")
    first = list(row3)
    first[i] = "999"
    f = W / "duplicate_column.csv"
    f.write_text(",".join(header + ["connected"]) + "\n" + ",".join(first + [row3[i]]) + "\n")
    rc, err, agg, _ = run("--reference-csv", f)
    case(G, "repeated CSV column (first says 999, last the true value) refused",
         rc != 0 and agg.get("ok") is False and "once" in err, exit=rc, said=last_line(err))
    for name, txt in (("a row longer than the header", "n,connected\n3,2,7\n"),
                      ("a row shorter than the header", "n,connected,chi=1\n3,2\n"),
                      ("an empty column name", "n,,connected\n3,1,2\n"),
                      ("a non-integer cell", "n,connected\n3,2.0\n")):
        f = W / (re.sub(r"\W+", "_", name) + ".csv")
        f.write_text(txt)
        rc, err, agg, _ = run("--reference-csv", f)
        case(G, f"CSV with {name} refused", rc != 0 and agg.get("ok") is False and "Traceback" not in err, exit=rc,
             said=last_line(err))
    f = W / "latin1.csv"
    f.write_bytes(b"n,connected\n3,\xff\n")
    rc, err, agg, _ = run("--reference-csv", f)
    case(G, "non-UTF-8 CSV refused cleanly", rc != 0 and agg.get("ok") is False and "UTF-8" in err
         and "Traceback" not in err, exit=rc, said=last_line(err))
    rc, err, agg, _ = run("--reference-csv", W / "does_not_exist.csv")
    case(G, "missing CSV refused cleanly", rc != 0 and agg.get("ok") is False and "cannot read" in err
         and "Traceback" not in err, exit=rc, said=last_line(err))
    before = read_bytes(root / "aggregate.json")
    rc, err, agg, na = run("--expect")
    case(G, "--expect without a value is a usage error that starts no attempt",
         rc == 2 and na == 0 and read_bytes(root / "aggregate.json") == before, exit=rc, new_attempts=na)
    rc, _, good, _ = run()
    v = good.get("counts", {}).get("-1-Dis")
    rc, err, agg, _ = run(f"--expect=-1-Dis={v}")
    case(G, "--expect=-1-Dis=V with the true value is compared and accepted", rc == 0 and agg.get("ok") is True
         and agg.get("comparison", {}).get("-1-Dis", {}).get("equal") is True, exit=rc, value=v)
    rc, err, agg, _ = run(f"--expect=-1-Dis={(v or 0) + 1}")
    case(G, "--expect=-1-Dis=V with a wrong value fails the comparison", rc != 0 and agg.get("ok") is False
         and agg.get("comparison", {}).get("-1-Dis", {}).get("equal") is False, exit=rc)
    rc, err, agg, na = run("--expect", "conexas=2", "-1-Dis=1")
    case(G, "the old batch form --expect K=V -1-Dis=V is a usage error", rc == 2 and na == 0, exit=rc)
    for name, args in (("repeated --expect key", ("--expect", "conexas=2", "--expect", "conexas=2")),
                       ("unknown --expect key", ("--expect", "nada=1")),
                       ("negative --expect value", ("--expect=conexas=-1",)),
                       ("--expect value with a leading zero", ("--expect", "conexas=02")),
                       ("--expect value with a decimal point", ("--expect", "conexas=2.0")),
                       ("--expect with an empty value", ("--expect", "conexas=")),
                       ("--expect without '='", ("--expect", "conexas"))):
        rc, err, agg, _ = run(*args)
        case(G, name + " refused", rc != 0 and agg.get("ok") is False, exit=rc, said=last_line(err))
    e6 = W / "empty.g6"
    e6.write_text("")
    rc, err, agg, _ = run("--reference-g6", e6)
    case(G, "empty graph6 reference refused", rc != 0 and agg.get("ok") is False and "empty" in err, exit=rc)
    rc, err, agg, _ = run("--labelg", LABELG)
    case(G, "--labelg without --reference-g6 refused", rc != 0 and agg.get("ok") is False, exit=rc)
    g6 = W / "one.g6"
    g6.write_text("Bw\n")
    rc, err, agg, _ = run("--reference-csv", PUBLISHED, "--reference-g6", g6, "--labelg", LABELG)
    recs = {r.get("kind"): r for r in agg.get("references") or []}
    want = {"csv": sha(PUBLISHED), "graph6": sha(g6), "labelg": sha(LABELG)}
    last = json.loads(attempts(root)[-1].read_text()) if attempts(root) else {}
    case(G, "every reference recorded with path and SHA-256 in aggregate.json and the attempt (failed comparison)",
         rc != 0 and agg.get("ok") is False and all(recs.get(k, {}).get("sha256") == h for k, h in want.items())
         and all(recs.get(k, {}).get("path") for k in want) and last.get("references") == agg.get("references"),
         exit=rc, kinds=sorted(recs))
    rc, err, agg, _ = run("--reference-csv", PUBLISHED)
    recs = agg.get("references") or []
    case(G, "a successful comparison records the CSV with its SHA-256",
         rc == 0 and agg.get("ok") is True and len(recs) == 1 and recs[0].get("sha256") == sha(PUBLISHED), exit=rc)


# -------------------------------------------------------------------------------------------------- aggregate (H-29)
def aggregate_cases():
    G = "aggregate"
    root, cfgp, rca = campaign("ag")
    agg = agg_json(root)
    att = {p.stem: json.loads(p.read_text()) for p in attempts(root)}
    case(G, "a successful aggregate names its attempt, recorded with status ok",
         rca == 0 and agg.get("ok") is True and att.get(agg.get("attempt_id"), {}).get("status") == "ok", exit=rca)
    first = agg.get("attempt_id")
    with open(root / "workers" / "0.lock", "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rc, _, err = drv("aggregate", "--config", cfgp, "--jobs", 1)
    agg = agg_json(root)
    aid = str(agg.get("attempt_id"))
    hist = root / "aggregate_history" / aid / "aggregate.json"
    old = json.loads(hist.read_text()) if hist.exists() else {}
    recp = root / "aggregate_attempts" / f"{aid}.json"
    rec = json.loads(recp.read_text()) if recp.exists() else {}
    case(G, "busy worker lock after an earlier ok=true: ok=false in place, earlier result archived, attempt failed",
         rc != 0 and agg.get("ok") is False and agg.get("status") == "failed" and old.get("ok") is True
         and old.get("attempt_id") == first and rec.get("status") == "failed", exit=rc, archived_ok=old.get("ok"),
         attempt_status=rec.get("status"), said=last_line(err))
    before, na0, nh0 = read_bytes(root / "aggregate.json"), len(attempts(root)), len(history(root))
    with open(root / "aggregate.lock", "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rc, _, err = drv("aggregate", "--config", cfgp, "--jobs", 1)
    case(G, "a second aggregate while one runs is refused and touches nothing",
         rc != 0 and "another aggregate" in err and before is not None and read_bytes(root / "aggregate.json") == before
         and len(attempts(root)) == na0 and len(history(root)) == nh0, exit=rc)
    cfg, _ = M.load_config(cfgp)
    p0 = M.receipt_path(cfg, 0)
    saved = p0.read_text()
    for txt in ("null", "[]", "{}", '"text"', "1"):
        p0.write_text(txt)
        rc, out, err = drv("status", "--config", cfgp)
        st = json.loads(out) if rc == 0 and out.strip() else {}
        case(G, f"status survives a receipt that contains {txt} and counts it unreadable",
             rc == 0 and st.get("ok_receipts") == 1 and st.get("ok_receipts_unreadable") == 1, exit=rc,
             said=last_line(err))
    p0.write_text(saved)
    rc = drv("aggregate", "--config", cfgp, "--jobs", 1)[0]
    states = sorted({str(json.loads(p.read_text()).get("status")) for p in attempts(root)})
    case(G, "with the receipt restored aggregate succeeds again and no attempt is left in state started",
         rc == 0 and agg_json(root).get("ok") is True and "started" not in states, exit=rc, attempt_states=states)


# --------------------------------------------------------------------------------------------------- classifier (S4)
def classifier_cases():
    G = "classifier"

    def run(args, full=None, limit=None):
        kw = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
        fh = open("/dev/full", "wb") if full else None
        if full:
            kw[full] = fh
        pre = (lambda: resource.setrlimit(resource.RLIMIT_AS, (limit, limit))) if limit else None
        try:
            return subprocess.run([str(BIN)] + args, input=b"Bw\n", preexec_fn=pre, **kw).returncode
        finally:
            if fh:
                fh.close()

    for name, args in (("unknown option", ["--nada"]), ("option without its value", ["--modo"]),
                       ("unknown mode", ["--modo", "nada"]), ("invalid --prof", ["--modo", "icert", "--prof", "x"])):
        normal, full = run(args), run(args, full="stderr")
        case(G, f"{name}: status 1, and 6 when stderr cannot be written", normal == 1 and full == 6, normal=normal,
             dev_full=full)
    normal, full = run(["--version"]), run(["--version"], full="stdout")
    case(G, "--version: status 0, and 6 when stdout cannot be written", normal == 0 and full == 6, normal=normal,
         dev_full=full)
    lim = next((m << 20 for m in (96, 128, 160, 192, 256, 384, 512) if run(["--modo", "tabla"], limit=m << 20) == 2),
               None)
    full = run(["--modo", "tabla"], full="stderr", limit=lim) if lim else None
    case(G, "lack of memory (address-space limit): status 2, and 6 when stderr cannot be written",
         lim is not None and full == 6, limit_mib=(lim >> 20) if lim else None, dev_full=full)


# ------------------------------------------------------------------------------------------------------ harness (H-35)
def harness_cases():
    G = "harness"
    probes = {f"{HOME}/no/such/dir/new.json": "new.json (outside the repository)",
              f"--out={HOME}/x/y.json": "--out=y.json (outside the repository)",
              str(REPO / "v2" / "tests" / "results" / "not_yet.json"): "v2/tests/results/not_yet.json",
              "relative/new.json": "relative/new.json", "-c": "-c"}
    for arg, want in probes.items():
        got = provenance._display_arg(arg)
        case(G, f"argv entry recorded as {want!r}", got == want, got=got)
    saved = sys.argv
    sys.argv = [saved[0], "--out", f"{HOME}/no/such/new.json", f"--work={REPO}/tmp/w"]
    try:
        r = provenance.record()
    finally:
        sys.argv = saved
    try:
        provenance.check_portable(json.dumps(r))
        ok = True
    except Exception:  # noqa: BLE001
        ok = False
    case(G, "a result asked to be written to a new absolute path is portable",
         ok and not any(HOME in a for a in r["argv"]), argv=r["argv"])


# ------------------------------------------------------------------------------------------------------------- main
def main():
    global BIN, DRIVER, SOURCE, M, W
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default=str(HERE / "results" / "v2.4" / "regressions_r3.json"))
    ap.add_argument("--bin", default=str(BIN), help="classifier under test (default build/atascadas_v2)")
    ap.add_argument("--driver", default=str(DRIVER), help="driver under test (default pipeline/campana_v2.py)")
    ap.add_argument("--source", default=str(SOURCE),
                    help="classifier source compiled by init (default src/atascadas_v2.c; give the matching older "
                         "source together with an older --driver)")
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
    if not BIN.exists():
        raise SystemExit(f"{BIN} missing: run ./build.sh")
    M = load_driver(DRIVER)
    started = provenance.utc_now()
    prov = provenance.record(binaries=[(BIN, ["--version"])],
                             sources=[SOURCE, DRIVER, V2 / "build.sh", Path(__file__)], tools=["geng", "labelg"])
    funcs = {"init": init_cases, "receipt": receipt_cases, "reference": reference_cases,
             "aggregate": aggregate_cases, "classifier": classifier_cases, "harness": harness_cases}
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
           "binary_under_test": provenance.display_path(BIN), "driver_under_test": provenance.display_path(DRIVER),
           "source_under_test": provenance.display_path(SOURCE),
           "classifier_version_pinned_by_driver": getattr(M, "CLASSIFIER_VERSION", None), "sections": sections,
           "started_utc": started, "finished_utc": provenance.utc_now(), "provenance": prov}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(provenance.check_portable(json.dumps(res, indent=1) + "\n"))
    print(f"{res['n_cases']} cases, {res['n_failed']} failed:", "ALL PASS" if res["all_pass"] else "SOME CASES FAILED")
    sys.exit(0 if res["all_pass"] else 1)


if __name__ == "__main__":
    main()
