#!/usr/bin/env python3
"""campana_v2.py — pipeline v2 for exhaustive enumerations (findings H-02, H-03, H-04, H-16, H-17 of the external audit).

Standard library only.  One campaign = one directory ROOT with an immutable config.json.  The residues r = 0..mod-1 of
`geng [args] n r/mod` are partitioned STATICALLY among `workers` worker ids (r ≡ id mod workers), so no two workers can
ever process the same slice; a worker id is protected by an exclusive lock, so it cannot run twice at the same time.
Each slice is published as receipts/<r//1000>/<r>.ok.json only after BOTH processes of the pipeline exit with status 0
and every check below passes; the file is written to a unique temporary name, fsync'ed and renamed atomically.
A failed slice is kept as <r>.failed.<uuid>.json and never counts as done.

Checks of one slice (function check_slice):
  * generator: exit 0, no '>E' line, exactly one '>Z N graphs generated' line;
  * classifier (v2/src/atascadas_v2.c): exit 0, stderr is exactly one summary line with version=v2, invalidos=0,
    errores=0 and the campaign order n (or n=0 for an empty slice);
  * number of graphs read by the classifier = N reported by the generator;
  * mode tabla: chain -1-Dis <= 0-Dis <= 1-Dis <= 2-Dis <= 3-Dis <= I_SV <= I_S <= I <= aciclicas <= chi1 <= conexas,
    aciclicas = I + I_indecisas, and the stdout records (I_NO_IS / ACICLICA_NO_IS_INDECISA) are valid graph6 strings of
    order n, pairwise distinct, in disjoint classes, with |I_NO_IS| = I - I_S and |INDECISA| = I_indecisas;
  * mode atascadas: encontradas <= pasa_aristas <= pasa_vecindades <= pasa_chi <= pasa_cono <= total and the stdout
    records are |encontradas| distinct valid graph6 strings of order n.
The receipt stores the commands, exit codes, host, SLURM ids, times, the three output streams verbatim and their
SHA-256; the aggregate re-validates every receipt from those stored streams.

Subcommands:
  init      --root R --n N --mod M --workers W --mode tabla|atascadas --geng PATH --geng-args="-c" --source atascadas_v2.c
            (write --geng-args=VALUE with '=' because the value starts with '-')
            [--cflags "-O3 -std=c11"] [--expect-geng-version 2.8]
            copies geng and the source into R/bin (read-only), compiles the classifier there, pins all SHA-256.
  worker    --config R/config.json --worker-id i [--procs P]     (P concurrent pipelines, one CPU each)
  status    --config R/config.json
  aggregate --config R/config.json [--jobs J] [--reference-csv data/table_cardinalities.csv] [--expect KEY=VALUE ...]
            [--reference-g6 FILE]   writes R/aggregate.json and R/<record class>.g6; exit 0 only if coverage is exact,
            all receipts validate, all invariants hold and all requested comparisons are equal.
"""
import argparse, concurrent.futures, datetime, fcntl, hashlib, json, os, re, shlex, shutil, subprocess, sys, threading
import time, uuid
from pathlib import Path

SCHEMA = "campana_v2/1"
TABLE_KEYS = ["conexas", "chi1", "aciclicas", "I", "I_indecisas", "I_S", "I_SV", "3-Dis", "2-Dis", "1-Dis", "0-Dis",
              "-1-Dis"]
TABLE_CHAIN = ["-1-Dis", "0-Dis", "1-Dis", "2-Dis", "3-Dis", "I_SV", "I_S", "I", "aciclicas", "chi1", "conexas"]
SEARCH_KEYS = ["total", "pasa_cono", "pasa_chi", "pasa_vecindades", "pasa_aristas", "encontradas"]
SEARCH_CHAIN = ["encontradas", "pasa_aristas", "pasa_vecindades", "pasa_chi", "pasa_cono", "total"]
MEMO_KEYS = ["memo_consultas", "memo_aciertos", "memo_colisiones_hash"]
TABLE_CLASSES = ["I_NO_IS", "ACICLICA_NO_IS_INDECISA"]
CSV_COLUMNS = {"conexas": "connected", "chi1": "chi=1", "aciclicas": "Z2-acyclic", "I": "I-contractible",
               "I_indecisas": "I-undecided", "I_S": "strong I-contractible (J_S)", "I_SV": "J_VS", "3-Dis": "3-Dis",
               "2-Dis": "2-Dis", "1-Dis": "1-Dis", "0-Dis": "0-Dis", "-1-Dis": "(-1)-Dis"}


class SliceError(Exception):
    pass


# ------------------------------------------------------------------------------------------------ utilities
def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp." + uuid.uuid4().hex)
    with open(tmp, "x") as f:
        json.dump(obj, f, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def valid_g6(s, n):
    """strict graph6 check for order n (1..62): length, character range and zero padding"""
    if not s or not (1 <= n <= 62) or ord(s[0]) - 63 != n:
        return False
    nbits = n * (n - 1) // 2
    if len(s) != 1 + (nbits + 5) // 6:
        return False
    if any(not (63 <= ord(c) <= 126) for c in s[1:]):
        return False
    if nbits % 6:
        pad = 6 - nbits % 6
        if (ord(s[-1]) - 63) & ((1 << pad) - 1):
            return False
    return True


# ------------------------------------------------------------------------------------------------ config
def load_config(path, verify=True):
    cfg = json.loads(Path(path).read_text())
    if cfg.get("schema") != SCHEMA:
        raise ValueError("unknown config schema")
    if verify:
        for name, item in cfg["files"].items():
            if sha_file(item["path"]) != item["sha256"]:
                raise ValueError(f"pinned file changed: {name} {item['path']}")
    return cfg, sha_bytes(canonical(cfg))


def receipt_path(cfg, r):
    return Path(cfg["root"]) / "receipts" / str(r // 1000) / f"{r}.ok.json"


def commands(cfg, r):
    g = [cfg["files"]["geng"]["path"]] + cfg["geng_args"] + [str(cfg["n"]), f"{r}/{cfg['mod']}"]
    c = [cfg["files"]["classifier"]["path"], "--modo", cfg["mode"]]
    return g, c


# ------------------------------------------------------------------------------------------------ slice checks
def parse_summary(classifier_stderr):
    lines = classifier_stderr.splitlines()
    if len(lines) != 1 or not lines[0].startswith("n="):
        raise SliceError("classifier stderr is not exactly one summary line: " + repr(classifier_stderr[:200]))
    pairs = dict(re.findall(r"(\S+?)=(\S+)", lines[0]))
    return pairs


def check_slice(cfg, geng_stderr, classifier_stderr, result_stdout):
    """Returns (counts, records, memo).  Raises SliceError on any inconsistency."""
    n = cfg["n"]
    if any(l.startswith(">E") for l in geng_stderr.splitlines()):
        raise SliceError("generator reported an error")
    z = re.findall(r"^>Z\s+(\d+)\s+graphs generated", geng_stderr, re.M)
    if len(z) != 1:
        raise SliceError("generator count line missing or repeated")
    generated = int(z[0])
    s = parse_summary(classifier_stderr)
    if s.get("version") != "v2":
        raise SliceError("classifier is not v2")
    if s.get("invalidos") != "0" or s.get("errores") != "0":
        raise SliceError("classifier reported invalid records or errors")
    keys = TABLE_KEYS if cfg["mode"] == "tabla" else SEARCH_KEYS
    try:
        counts = {k: int(s[k]) for k in keys}
        memo = {k: int(s[k]) for k in MEMO_KEYS}
        order = int(s["n"])
    except (KeyError, ValueError) as e:
        raise SliceError("summary field missing or not an integer: " + repr(e))
    total = counts["conexas"] if cfg["mode"] == "tabla" else counts["total"]
    if order != n and not (order == 0 and total == 0):
        raise SliceError(f"wrong graph order {order}")
    if total != generated:
        raise SliceError(f"classifier read {total} graphs, generator produced {generated}")
    chain = TABLE_CHAIN if cfg["mode"] == "tabla" else SEARCH_CHAIN
    for a, b in zip(chain, chain[1:]):
        if counts[a] > counts[b]:
            raise SliceError(f"inclusion violated: {a} > {b}")
    records = {}
    if cfg["mode"] == "tabla":
        if counts["aciclicas"] != counts["I"] + counts["I_indecisas"]:
            raise SliceError("aciclicas != I + I_indecisas")
        records = {k: [] for k in TABLE_CLASSES}
        for line in result_stdout.splitlines():
            q = line.split()
            if len(q) != 2 or q[0] not in records or not valid_g6(q[1], n):
                raise SliceError("unrecognised result line: " + line[:120])
            records[q[0]].append(q[1])
        if len(records["I_NO_IS"]) != counts["I"] - counts["I_S"]:
            raise SliceError("number of I_NO_IS records != I - I_S")
        if len(records["ACICLICA_NO_IS_INDECISA"]) != counts["I_indecisas"]:
            raise SliceError("number of INDECISA records != I_indecisas")
        if set(records["I_NO_IS"]) & set(records["ACICLICA_NO_IS_INDECISA"]):
            raise SliceError("graph in two classes")
    else:
        records = {"ATASCADA": []}
        for line in result_stdout.splitlines():
            if not valid_g6(line, n):
                raise SliceError("unrecognised result line: " + line[:120])
            records["ATASCADA"].append(line)
        if len(records["ATASCADA"]) != counts["encontradas"]:
            raise SliceError("number of found graphs != encontradas")
    for k, v in records.items():
        if len(v) != len(set(v)):
            raise SliceError("repeated graph in " + k)
    return counts, records, memo


def validate_receipt(cfg, cfgsha, r, d):
    if d.get("schema") != SCHEMA or d.get("status") != "complete":
        raise SliceError("receipt not complete")
    if d["r"] != r or d["mod"] != cfg["mod"] or d["config_sha256"] != cfgsha:
        raise SliceError("receipt identity mismatch")
    g, c = commands(cfg, r)
    if d["cmd_geng"] != g or d["cmd_classifier"] != c:
        raise SliceError("receipt commands differ from config")
    if d["exit_geng"] != 0 or d["exit_classifier"] != 0:
        raise SliceError("nonzero exit status in receipt")
    for name in ("geng_stderr", "classifier_stderr", "result_stdout"):
        if sha_bytes(d[name].encode()) != d[name + "_sha256"]:
            raise SliceError("stored stream hash mismatch: " + name)
    counts, records, memo = check_slice(cfg, d["geng_stderr"], d["classifier_stderr"], d["result_stdout"])
    if counts != d["counts"] or records != d["records"] or memo != d["memo"]:
        raise SliceError("receipt summary differs from its stored streams")
    return counts, records, memo


# ------------------------------------------------------------------------------------------------ run one slice
def run_slice(cfg, cfgsha, r, worker_id):
    dst = receipt_path(cfg, r)
    if dst.exists():
        validate_receipt(cfg, cfgsha, r, json.loads(dst.read_text()))
        return "resumed"
    g, c = commands(cfg, r)
    t0 = time.monotonic()
    start = utcnow()
    pg = subprocess.Popen(g, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    box = {}
    reader = threading.Thread(target=lambda: box.__setitem__("err", pg.stderr.read()))
    reader.start()
    pc = subprocess.Popen(c, stdin=pg.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pg.stdout.close()
    out, err = pc.communicate()
    reader.join()
    eg = pg.wait()
    ec = pc.returncode
    d = {"schema": SCHEMA, "r": r, "mod": cfg["mod"], "config_sha256": cfgsha, "cmd_geng": g, "cmd_classifier": c,
         "exit_geng": eg, "exit_classifier": ec, "seconds": round(time.monotonic() - t0, 3), "utc_start": start,
         "utc_end": utcnow(), "host": os.uname().nodename, "worker_id": worker_id,
         "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID"),
         "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"), "status": "failed"}
    for name, data in (("geng_stderr", box.get("err", b"")), ("classifier_stderr", err), ("result_stdout", out)):
        d[name] = data.decode("utf-8", errors="replace")
        d[name + "_sha256"] = sha_bytes(d[name].encode())
    try:
        if eg != 0 or ec != 0:
            raise SliceError(f"nonzero exit status (geng {eg}, classifier {ec})")
        d["counts"], d["records"], d["memo"] = check_slice(cfg, d["geng_stderr"], d["classifier_stderr"],
                                                           d["result_stdout"])
        d["status"] = "complete"
        validate_receipt(cfg, cfgsha, r, d)
    except SliceError as e:
        d["error"] = str(e)
        atomic_json(dst.with_name(f"{r}.failed.{uuid.uuid4().hex}.json"), d)
        raise
    atomic_json(dst, d)
    return "new"


# ------------------------------------------------------------------------------------------------ subcommands
def cmd_init(a):
    root = Path(a.root).resolve()
    if (root / "config.json").exists():
        raise SystemExit("config.json already exists; workers resume from validated receipts")
    if not (1 <= a.workers <= a.mod):
        raise SystemExit("need 1 <= workers <= mod")
    binr = root / "bin"
    binr.mkdir(parents=True, exist_ok=True)
    geng = binr / "geng"
    src = binr / "atascadas_v2.c"
    cls = binr / "atascadas_v2"
    shutil.copy2(a.geng, geng)
    shutil.copy2(a.source, src)
    if sha_file(geng) != sha_file(a.geng) or sha_file(src) != sha_file(a.source):
        raise SystemExit("copy differs from original")
    cc = ["gcc"] + shlex.split(a.cflags) + ["-o", str(cls), str(src)]
    p = subprocess.run(cc, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("compilation failed:\n" + p.stderr)
    for f in (geng, src, cls):
        os.chmod(f, 0o555 if f != src else 0o444)
    gv = subprocess.run([str(geng), "--version"], capture_output=True, text=True)
    gver = (gv.stdout + gv.stderr).strip()
    if a.expect_geng_version and a.expect_geng_version not in gver:
        raise SystemExit(f"geng version {gver!r} does not contain {a.expect_geng_version!r}")
    cv = subprocess.run([str(cls), "--version"], capture_output=True, text=True)
    ccv = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    cfg = {"schema": SCHEMA, "root": str(root), "n": a.n, "mod": a.mod, "workers": a.workers, "mode": a.mode,
           "geng_args": shlex.split(a.geng_args), "compile_command": cc, "compiler": ccv,
           "geng_version": gver, "classifier_version": cv.stdout.strip(), "created_utc": utcnow(),
           "created_host": os.uname().nodename,
           "files": {"geng": {"path": str(geng), "sha256": sha_file(geng), "original": str(Path(a.geng).resolve())},
                     "source": {"path": str(src), "sha256": sha_file(src),
                                "original": str(Path(a.source).resolve())},
                     "classifier": {"path": str(cls), "sha256": sha_file(cls)}}}
    if a.mode not in ("tabla", "atascadas"):
        raise SystemExit("mode must be tabla or atascadas")
    atomic_json(root / "config.json", cfg)
    print(json.dumps({"config": str(root / "config.json"), "config_sha256": sha_bytes(canonical(cfg))}))


def cmd_worker(a):
    cfg, cfgsha = load_config(a.config)
    w = a.worker_id
    if not (0 <= w < cfg["workers"]):
        raise SystemExit("worker id out of range")
    lockp = Path(cfg["root"]) / "workers" / f"{w}.lock"
    lockp.parent.mkdir(parents=True, exist_ok=True)
    lockf = open(lockp, "a")
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit(f"worker {w} is already running elsewhere")
    slices = list(range(w, cfg["mod"], cfg["workers"]))
    stats = {"new": 0, "resumed": 0, "failed": 0}
    failures = []
    lock = threading.Lock()

    def job(r):
        try:
            res = run_slice(cfg, cfgsha, r, w)
        except Exception as e:  # noqa: BLE001  (every failure is recorded; the worker exits nonzero)
            with lock:
                stats["failed"] += 1
                failures.append((r, str(e)[:300]))
            return
        with lock:
            stats[res] += 1

    t0 = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.procs) as ex:
        list(ex.map(job, slices))
    load_config(a.config)  # pinned files unchanged at the end
    ok = sum(1 for r in slices if receipt_path(cfg, r).exists())
    marker = {"config_sha256": cfgsha, "worker": w, "workers": cfg["workers"], "slices": len(slices),
              "ok_receipts": ok, "this_run": stats, "failures_first": failures[:50], "seconds": time.monotonic() - t0,
              "host": os.uname().nodename, "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "utc": utcnow(),
              "complete": ok == len(slices) and stats["failed"] == 0}
    atomic_json(Path(cfg["root"]) / "workers" / f"{w}.json", marker)
    print(json.dumps({k: marker[k] for k in ("worker", "slices", "ok_receipts", "this_run", "complete")}))
    sys.exit(0 if marker["complete"] else 1)


def cmd_status(a):
    cfg, _ = load_config(a.config, verify=False)
    rec = Path(cfg["root"]) / "receipts"
    ok = failed = 0
    if rec.exists():
        for d in rec.iterdir():
            for f in d.iterdir():
                if f.name.endswith(".ok.json"):
                    ok += 1
                elif ".failed." in f.name:
                    failed += 1
    print(json.dumps({"mod": cfg["mod"], "ok_receipts": ok, "failed_files": failed,
                      "fraction": ok / cfg["mod"]}))


def _validate_shard(args):
    config, cfgsha, paths = args
    cfg, _ = load_config(config, verify=False)
    out = []
    for p in paths:
        r = int(Path(p).name.split(".")[0])
        if Path(p) != receipt_path(cfg, r):
            raise SliceError("receipt in wrong shard: " + p)
        counts, records, memo = validate_receipt(cfg, cfgsha, r, json.loads(Path(p).read_text()))
        out.append((r, counts, records, memo))
    return out


def cmd_aggregate(a):
    cfg, cfgsha = load_config(a.config)
    root = Path(cfg["root"])
    paths = sorted(str(p) for p in (root / "receipts").rglob("*.ok.json")) if (root / "receipts").exists() else []
    chunks = [paths[i:i + 2000] for i in range(0, len(paths), 2000)]
    keys = TABLE_KEYS if cfg["mode"] == "tabla" else SEARCH_KEYS
    sums = {k: 0 for k in keys}
    memo = {k: 0 for k in MEMO_KEYS}
    found = {}
    seen = bytearray(cfg["mod"])
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for part in ex.map(_validate_shard, [(a.config, cfgsha, ch) for ch in chunks]):
            for r, c, recs, m in part:
                if not (0 <= r < cfg["mod"]) or seen[r]:
                    raise SystemExit(f"unexpected or duplicate residue {r}")
                seen[r] = 1
                for k in keys:
                    sums[k] += c[k]
                for k in MEMO_KEYS:
                    memo[k] += m[k]
                for k, gs in recs.items():
                    S = found.setdefault(k, set())
                    if S.intersection(gs):
                        raise SystemExit(f"graph repeated between slices in class {k}")
                    S.update(gs)
    coverage = sum(seen)
    missing = [i for i, x in enumerate(seen) if not x][:20]
    problems = []
    if coverage != cfg["mod"]:
        problems.append(f"incomplete coverage {coverage}/{cfg['mod']}; first missing {missing}")
    chain = TABLE_CHAIN if cfg["mode"] == "tabla" else SEARCH_CHAIN
    for x, y in zip(chain, chain[1:]):
        if sums[x] > sums[y]:
            problems.append(f"inclusion violated in totals: {x} > {y}")
    if cfg["mode"] == "tabla":
        if sums["aciclicas"] != sums["I"] + sums["I_indecisas"]:
            problems.append("aciclicas != I + I_indecisas in totals")
        if found.get("I_NO_IS", set()) & found.get("ACICLICA_NO_IS_INDECISA", set()):
            problems.append("graph in two classes across slices")
    comparison = {}
    if a.reference_csv:
        rows = [l for l in Path(a.reference_csv).read_text().splitlines() if l and not l.startswith("#")]
        head = rows[0].split(",")
        for l in rows[1:]:
            v = l.split(",")
            if int(v[0]) == cfg["n"]:
                row = dict(zip(head, v))
                for k, col in CSV_COLUMNS.items():
                    if k in sums and col in row:
                        comparison[k] = {"actual": sums[k], "expected": int(row[col])}
    for e in a.expect or []:
        k, v = e.split("=", 1)
        if k not in sums:
            raise SystemExit("unknown key in --expect: " + k)
        comparison[k] = {"actual": sums[k], "expected": int(v)}
    if a.reference_g6:
        ref = {l.split()[0] for l in Path(a.reference_g6).read_text().splitlines() if l.strip() and l[0] != "#"}
        cls = "ATASCADA" if cfg["mode"] == "atascadas" else "I_NO_IS"
        got = found.get(cls, set())
        comparison[cls + "_set"] = {"actual": len(got), "expected": len(ref), "only_found": sorted(got - ref)[:20],
                                    "only_reference": sorted(ref - got)[:20]}
        comparison[cls + "_set"]["equal"] = got == ref
    for k, v in comparison.items():
        v.setdefault("equal", v["actual"] == v["expected"])
        if not v["equal"]:
            problems.append(f"comparison failed: {k}")
    load_config(a.config)
    result = {"config_sha256": cfgsha, "n": cfg["n"], "mod": cfg["mod"], "mode": cfg["mode"], "coverage": coverage,
              "counts": sums, "memo_totals": memo, "found_counts": {k: len(v) for k, v in found.items()},
              "comparison": comparison, "problems": problems, "ok": not problems, "utc": utcnow()}
    atomic_json(root / "aggregate.json", result)
    for k, gs in found.items():
        (root / f"{k}.g6").write_text("".join(g + "\n" for g in sorted(gs)))
    print(json.dumps({k: result[k] for k in ("n", "mod", "coverage", "counts", "found_counts", "problems", "ok")}))
    sys.exit(0 if result["ok"] else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = p.add_subparsers(dest="cmd", required=True)
    q = sp.add_parser("init")
    q.add_argument("--root", required=True)
    q.add_argument("--n", type=int, required=True)
    q.add_argument("--mod", type=int, required=True)
    q.add_argument("--workers", type=int, required=True)
    q.add_argument("--mode", required=True)
    q.add_argument("--geng", required=True)
    q.add_argument("--geng-args", required=True)
    q.add_argument("--source", required=True)
    q.add_argument("--cflags", default="-O3 -std=c11 -Wall -Wextra -Wpedantic -Werror")
    q.add_argument("--expect-geng-version", default=None)
    q = sp.add_parser("worker")
    q.add_argument("--config", required=True)
    q.add_argument("--worker-id", type=int, required=True)
    q.add_argument("--procs", type=int, default=1)
    q = sp.add_parser("status")
    q.add_argument("--config", required=True)
    q = sp.add_parser("aggregate")
    q.add_argument("--config", required=True)
    q.add_argument("--jobs", type=int, default=4)
    q.add_argument("--reference-csv")
    q.add_argument("--expect", nargs="*")
    q.add_argument("--reference-g6")
    a = p.parse_args()
    {"init": cmd_init, "worker": cmd_worker, "status": cmd_status, "aggregate": cmd_aggregate}[a.cmd](a)


if __name__ == "__main__":
    main()
