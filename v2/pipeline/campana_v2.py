#!/usr/bin/env python3
"""campana_v2.py — pipeline v2 for exhaustive enumerations (findings H-02, H-03, H-04, H-16, H-17 of the external audit).

Standard library only.  One campaign = one directory ROOT with an immutable config.json.  The residues r = 0..mod-1 of
`geng [args] n r/mod` are partitioned STATICALLY among `workers` worker ids (r ≡ id mod workers), so no two workers can
ever process the same slice; a worker id is protected by an exclusive lock, so it cannot run twice at the same time.
Each slice is published as receipts/<r//1000>/<r>.ok.json only after BOTH processes of the pipeline exit with status 0
and every check below passes; the file is written to a unique temporary name, fsync'ed and renamed atomically.
A failed slice is kept as <r>.failed.<uuid>.json and never counts as done.

Checks of one slice (function check_slice):
  * generator: exit 0; stderr is an optional '>A' header (with n and class=r/mod) and exactly one '>Z' line;
  * classifier (v2/src/atascadas_v2.c): exit 0, stderr is exactly one summary line with the pinned version (v2.1), invalidos=0,
    errores=0 and the campaign order n (or n=0 for an empty slice);
  * number of graphs read by the classifier = N reported by the generator;
  * mode tabla: chain -1-Dis <= 0-Dis <= 1-Dis <= 2-Dis <= 3-Dis <= I_SV <= I_S <= I <= aciclicas <= chi1 <= conexas,
    aciclicas = I + I_indecisas, and the stdout records (I_NO_IS / ACICLICA_NO_IS_INDECISA) are valid graph6 strings of
    order n, pairwise distinct, in disjoint classes, with |I_NO_IS| = I - I_S and |INDECISA| = I_indecisas;
  * mode atascadas: encontradas <= pasa_aristas <= pasa_vecindades <= pasa_chi <= pasa_cono <= total and the stdout
    records are |encontradas| distinct valid graph6 strings of order n.
The receipt stores the commands, exit codes, host, SLURM ids, times, the three output streams verbatim and their
SHA-256; the aggregate re-validates every receipt from those stored streams.

v2.1 (round 2 of the external audit: H-22, H-23, H-24, H-29):
  * the summary line is parsed with a strict grammar: exactly the keys of the mode, each once, non-negative decimal
    integers, version equal to the pinned classifier, memo_aciertos <= memo_consultas; the generator's stderr must be
    an optional '>A' header naming n and class=r/mod, then exactly one '>Z N graphs generated [in T sec]' line;
  * a receipt must name the worker that owns its residue (r mod workers = worker_id) and carry its provenance;
  * init validates n, mod, workers, mode and the geng pins before touching the disk: the version token printed by
    `geng --version` (compared exactly, e.g. 2.9301; nauty prints 10000*version + HAVE_TLS, so no dotted conversion)
    and the SHA-256 of the binary, both required; it creates ROOT exclusively (it must not exist), refuses protected
    historical directories, stores the full `geng --version` output in config.json and the full `geng --help` output in
    bin/geng_help.txt, and pins the driver itself, the classifier, the source, geng, the help file and config.json
    (config.sha256); workers and aggregate refuse to run if any pinned file changed; a failure after ROOT was created
    leaves ROOT/INIT_FAILED.txt with the reason and no config.json (nothing is deleted);
  * aggregate refuses to run while a worker holds its lock, moves earlier outputs to aggregate_history/ before it
    starts (a failed run never leaves an old ok=true behind), and compares references strictly: exactly one CSV row
    with every column of the mode, unique --expect keys, any conflict between sources is fatal, and a requested
    comparison can never be empty; --labelg compares graph sets up to isomorphism;
  * status counts readable receipts and is explicitly not a certificate.

Exit codes of the classifier (v2.1): 0 ok, 1 usage, 2 capacity, 3 invalid records, 4 inconsistency or read error,
5 disconnected input or mixed orders, 6 write error on stdout/stderr.

Subcommands:
  init      --root R --n N --mod M --workers W --mode tabla|atascadas --geng PATH --geng-args="-c" --source atascadas_v2.c
            (write --geng-args=VALUE with '=' because the value starts with '-')
            --expect-geng-version TOKEN --expect-geng-sha256 HEX      (both required; TOKEN as printed, e.g. 2.9301)
            [--cflags "-O3 -std=c11 -Wall -Wextra -Wpedantic -Werror"] [--protect DIR ...]
            creates R (which must not exist), copies geng, the source and this driver into R/bin (read-only),
            compiles the classifier there and pins all SHA-256.
  worker    --config R/config.json --worker-id i [--procs P]     (P concurrent pipelines, one CPU each)
  status    --config R/config.json
  aggregate --config R/config.json [--jobs J] [--reference-csv data/table_cardinalities.csv] [--expect KEY=VALUE ...]
            [--reference-g6 FILE [--labelg PATH]]   writes R/aggregate.json and R/<record class>.g6; exit 0 only if
            coverage is exact, all receipts validate, all invariants hold and all requested comparisons are equal.
"""
import argparse, concurrent.futures, csv, datetime, fcntl, hashlib, json, os, re, shlex, shutil, subprocess, sys
import threading
import time, uuid
from pathlib import Path

SCHEMA = "campana_v2/2"
CLASSIFIER_VERSION = "v2.1"
MAXN_CLASSIFIER = 16
PROTECTED_DEFAULT = ["/lustre/proyectos/p029/busqueda_minimal"]   # historical experiment: read-only
TABLE_KEYS = ["conexas", "chi1", "aciclicas", "I", "I_indecisas", "I_S", "I_SV", "3-Dis", "2-Dis", "1-Dis", "0-Dis",
              "-1-Dis"]
TABLE_CHAIN = ["-1-Dis", "0-Dis", "1-Dis", "2-Dis", "3-Dis", "I_SV", "I_S", "I", "aciclicas", "chi1", "conexas"]
SEARCH_KEYS = ["total", "pasa_cono", "pasa_chi", "pasa_vecindades", "pasa_aristas", "encontradas"]
SEARCH_CHAIN = ["encontradas", "pasa_aristas", "pasa_vecindades", "pasa_chi", "pasa_cono", "total"]
MEMO_KEYS = ["memo_consultas", "memo_aciertos", "memo_colisiones_hash"]
TABLE_SUMMARY = ["n"] + TABLE_KEYS + ["invalidos", "errores", "icert_truncados"] + MEMO_KEYS + ["version"]
SEARCH_SUMMARY = ["n"] + SEARCH_KEYS + ["invalidos", "errores"] + MEMO_KEYS + ["version"]
TABLE_CLASSES = ["I_NO_IS", "ACICLICA_NO_IS_INDECISA"]
UINT = re.compile(r"0|[1-9][0-9]*")
ZLINE = re.compile(r">Z ([0-9]+) graphs generated(?: in [0-9]+(?:\.[0-9]+)? sec)?")
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
    cfgsha = sha_bytes(canonical(cfg))
    if verify:
        pin = Path(path).with_name("config.sha256")
        if not pin.exists() or pin.read_text().strip() != cfgsha:
            raise ValueError("config.json differs from its pinned hash config.sha256 (a campaign cannot be edited)")
        for name, item in cfg["files"].items():
            if sha_file(item["path"]) != item["sha256"]:
                raise ValueError(f"pinned file changed: {name} {item['path']}")
        if sha_file(Path(__file__).resolve()) != cfg["files"]["driver"]["sha256"]:
            raise ValueError("this driver differs from the one pinned at init: run " + cfg["files"]["driver"]["path"])
    return cfg, cfgsha


def receipt_path(cfg, r):
    return Path(cfg["root"]) / "receipts" / str(r // 1000) / f"{r}.ok.json"


def commands(cfg, r):
    g = [cfg["files"]["geng"]["path"]] + cfg["geng_args"] + [str(cfg["n"]), f"{r}/{cfg['mod']}"]
    c = [cfg["files"]["classifier"]["path"], "--modo", cfg["mode"]]
    return g, c


# ------------------------------------------------------------------------------------------------ slice checks
def expected_version(cfg):
    return cfg.get("classifier_summary_version", CLASSIFIER_VERSION)


def parse_summary(classifier_stderr, mode="tabla", version=CLASSIFIER_VERSION):
    """Strict grammar: one line of single-space separated KEY=VALUE tokens with exactly the keys of the mode, each
    once; every value except version is a non-negative decimal integer; version is the pinned classifier's."""
    lines = classifier_stderr.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != 1:
        raise SliceError("classifier stderr is not exactly one summary line: " + repr(classifier_stderr[:200]))
    want = TABLE_SUMMARY if mode == "tabla" else SEARCH_SUMMARY
    pairs = {}
    for tok in lines[0].split(" "):
        k, sep, v = tok.partition("=")
        if not sep or not k:
            raise SliceError("summary token is not KEY=VALUE: " + repr(tok[:60]))
        if k in pairs:
            raise SliceError("repeated summary key: " + k)
        pairs[k] = v
    if set(pairs) != set(want):
        raise SliceError(f"summary keys differ: missing {sorted(set(want) - set(pairs))}, "
                         f"unexpected {sorted(set(pairs) - set(want))}")
    if pairs["version"] != version:
        raise SliceError(f"classifier version {pairs['version']!r}, expected {version!r}")
    out = {}
    for k in want:
        if k == "version":
            continue
        if not UINT.fullmatch(pairs[k]):
            raise SliceError(f"summary value is not a non-negative integer: {k}={pairs[k]!r}")
        out[k] = int(pairs[k])
    if out["memo_aciertos"] > out["memo_consultas"]:
        raise SliceError("memo_aciertos > memo_consultas")
    return out


def generator_count(geng_stderr, n=None, r=None, mod=None):
    """The generator's stderr must be an optional '>A ...' header followed by exactly one
    '>Z N graphs generated [in T sec]' line, and nothing else.  When the header is present it must name the order n
    and the slice class=r/mod (geng omits class= when mod = 1)."""
    lines = [l for l in geng_stderr.split("\n") if l != ""]
    if not (1 <= len(lines) <= 2) or (len(lines) == 2 and not lines[0].startswith(">A ")):
        raise SliceError("generator stderr is not '[>A header] >Z count': " + repr(geng_stderr[:300]))
    if len(lines) == 2:
        toks = lines[0].split()
        if n is not None and f"n={n}" not in toks:
            raise SliceError("generator header names another order: " + lines[0][:200])
        cls = [t for t in toks if t.startswith("class=")]
        if r is not None and mod is not None:
            if (mod > 1 and cls != [f"class={r}/{mod}"]) or (mod == 1 and cls not in ([], ["class=0/1"])):
                raise SliceError(f"generator header names another slice than {r}/{mod}: " + lines[0][:200])
    m = ZLINE.fullmatch(lines[-1])
    if not m:
        raise SliceError("generator count line not understood: " + repr(lines[-1][:120]))
    return int(m.group(1))


def check_slice(cfg, geng_stderr, classifier_stderr, result_stdout, r=None):
    """Returns (counts, records, memo).  Raises SliceError on any inconsistency."""
    n = cfg["n"]
    generated = generator_count(geng_stderr, n, r, cfg["mod"])
    s = parse_summary(classifier_stderr, cfg["mode"], expected_version(cfg))
    if s["invalidos"] != 0 or s["errores"] != 0:
        raise SliceError("classifier reported invalid records or errors")
    keys = TABLE_KEYS if cfg["mode"] == "tabla" else SEARCH_KEYS
    counts = {k: s[k] for k in keys}
    memo = {k: s[k] for k in MEMO_KEYS}
    if cfg["mode"] == "tabla":
        memo["icert_truncados"] = s["icert_truncados"]
    order = s["n"]
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
    if not isinstance(d, dict) or d.get("schema") != SCHEMA or d.get("status") != "complete":
        raise SliceError("receipt not complete")
    if d.get("r") != r or d.get("mod") != cfg["mod"] or d.get("config_sha256") != cfgsha:
        raise SliceError("receipt identity mismatch")
    for k, typ in (("worker_id", int), ("host", str), ("utc_start", str), ("utc_end", str)):
        v = d.get(k)
        if not isinstance(v, typ) or isinstance(v, bool) or (typ is str and not v):
            raise SliceError("receipt provenance missing or malformed: " + k)
    if not isinstance(d.get("seconds"), (int, float)) or isinstance(d.get("seconds"), bool) or d["seconds"] < 0:
        raise SliceError("receipt provenance missing or malformed: seconds")
    if not (0 <= d["worker_id"] < cfg["workers"]) or r % cfg["workers"] != d["worker_id"]:
        raise SliceError(f"worker {d['worker_id']} does not own residue {r} (workers={cfg['workers']})")
    g, c = commands(cfg, r)
    if d.get("cmd_geng") != g or d.get("cmd_classifier") != c:
        raise SliceError("receipt commands differ from config")
    if d.get("exit_geng") != 0 or d.get("exit_classifier") != 0:
        raise SliceError("nonzero exit status in receipt")
    for name in ("geng_stderr", "classifier_stderr", "result_stdout"):
        if not isinstance(d.get(name), str) or sha_bytes(d[name].encode()) != d.get(name + "_sha256"):
            raise SliceError("stored stream hash mismatch: " + name)
    counts, records, memo = check_slice(cfg, d["geng_stderr"], d["classifier_stderr"], d["result_stdout"], r)
    if counts != d.get("counts") or records != d.get("records") or memo != d.get("memo"):
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
                                                           d["result_stdout"], r)
        d["status"] = "complete"
        validate_receipt(cfg, cfgsha, r, d)
    except SliceError as e:
        d["error"] = str(e)
        atomic_json(dst.with_name(f"{r}.failed.{uuid.uuid4().hex}.json"), d)
        raise
    atomic_json(dst, d)
    return "new"


# ------------------------------------------------------------------------------------------------ subcommands
def _within(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def geng_version_token(gver):
    """The version token printed by `geng --version`, e.g. 2.9301 in 'Nauty&Traces version 2.9301 (32 bits)'.

    nauty prints NAUTYVERSIONID/10000, and nauty.h defines NAUTYVERSIONID as 10000*version + HAVE_TLS, so the last
    digit is a build flag and the encoding of the release differs between series (2.8.9 prints 2.8090, 2.9.3 prints
    2.9300 or 2.9301).  The token is therefore compared exactly as printed, never converted to a dotted release name;
    the SHA-256 of the binary is the strong pin."""
    m = re.search(r"version\s+([0-9]+\.[0-9]+)", gver)
    return m.group(1) if m else None


def cmd_init(a):
    # every check that does not need the disk comes first
    if a.mode not in ("tabla", "atascadas"):
        raise SystemExit("mode must be tabla or atascadas")
    if not (1 <= a.n <= MAXN_CLASSIFIER):
        raise SystemExit(f"need 1 <= n <= {MAXN_CLASSIFIER} (capacity of the classifier)")
    if a.mod < 1 or not (1 <= a.workers <= a.mod):
        raise SystemExit("need mod >= 1 and 1 <= workers <= mod")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", a.expect_geng_sha256):
        raise SystemExit("--expect-geng-sha256 must be 64 hexadecimal digits")
    gorig = Path(a.geng).resolve()
    if not gorig.is_file() or not os.access(gorig, os.X_OK):
        raise SystemExit(f"geng {gorig} is not an executable file")
    if sha_file(gorig) != a.expect_geng_sha256.lower():
        raise SystemExit("geng SHA-256 differs from --expect-geng-sha256")
    gv = subprocess.run([str(gorig), "--version"], capture_output=True, text=True)
    gver = (gv.stdout + gv.stderr).strip()
    gtok = geng_version_token(gver)
    if gv.returncode != 0 or gtok is None or gtok != a.expect_geng_version:
        raise SystemExit(f"geng --version printed {gver!r} (exit {gv.returncode}); "
                         f"--expect-geng-version must be its version token exactly, here {gtok!r}")
    gh = subprocess.run([str(gorig), "--help"], capture_output=True, text=True)
    ghelp = gh.stdout + gh.stderr
    if not Path(a.source).is_file():
        raise SystemExit(f"source {a.source} not found")
    if shutil.which("gcc") is None:
        raise SystemExit("gcc not found on PATH")
    root = Path(a.root).resolve()
    extra = [x for x in os.environ.get("CAMPANA_PROTECT", "").split(":") if x]
    protected = sorted({str(Path(x).resolve()) for x in PROTECTED_DEFAULT + list(a.protect or []) + extra})
    for P in protected:
        if _within(root, Path(P)):
            raise SystemExit(f"refusing to create a campaign inside the protected directory {P}")
    if not root.parent.is_dir():
        raise SystemExit(f"parent directory {root.parent} does not exist")
    try:
        os.mkdir(root)        # exclusive: fails if ROOT exists, also against a concurrent init
    except FileExistsError:
        raise SystemExit(f"{root} already exists: a campaign needs a new directory (workers resume from receipts)")
    try:
        _init_populate(a, root, protected, gorig, gver, gtok, ghelp)
    except BaseException as e:
        # nothing is deleted: the directory stays, without config.json (workers refuse it), with the reason
        with open(root / "INIT_FAILED.txt", "a") as f:
            f.write(f"{utcnow()} init failed: {e}\n")
        raise


def _init_populate(a, root, protected, gorig, gver, gtok, ghelp):
    binr = root / "bin"
    os.mkdir(binr)
    geng, src, cls, drv = binr / "geng", binr / "atascadas_v2.c", binr / "atascadas_v2", binr / "campana_v2.py"
    me = Path(__file__).resolve()
    for orig, dst in ((gorig, geng), (a.source, src), (me, drv)):
        shutil.copy2(orig, dst)
        if sha_file(dst) != sha_file(orig):
            raise SystemExit("copy differs from original: " + str(orig))
    if sha_file(geng) != a.expect_geng_sha256.lower():
        raise SystemExit("copied geng differs from --expect-geng-sha256 (the original changed during init)")
    helpf = binr / "geng_help.txt"
    with open(helpf, "x") as f:
        f.write(ghelp)
    cc = ["gcc"] + shlex.split(a.cflags) + ["-o", str(cls), str(src)]
    p = subprocess.run(cc, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("compilation failed:\n" + p.stderr)
    for f in (geng, src, cls, drv, helpf):
        os.chmod(f, 0o555 if f in (geng, cls) else 0o444)
    cv = subprocess.run([str(cls), "--version"], capture_output=True, text=True)
    words = cv.stdout.split()
    mx = re.search(r"MAXN=([0-9]+)", cv.stdout)
    if cv.returncode != 0 or len(words) < 2 or words[1] != CLASSIFIER_VERSION or not mx or a.n > int(mx.group(1)):
        raise SystemExit(f"classifier {cv.stdout.strip()!r} is not {CLASSIFIER_VERSION} or cannot take n={a.n}")
    ccv = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    cfg = {"schema": SCHEMA, "root": str(root), "n": a.n, "mod": a.mod, "workers": a.workers, "mode": a.mode,
           "geng_args": shlex.split(a.geng_args), "compile_command": cc, "compiler": ccv,
           "geng_version": gver, "geng_version_token": gtok, "geng_help_sha256": sha_file(helpf),
           "classifier_version": cv.stdout.strip(), "classifier_summary_version": CLASSIFIER_VERSION,
           "protected": protected, "created_utc": utcnow(), "created_host": os.uname().nodename,
           "files": {"geng": {"path": str(geng), "sha256": sha_file(geng), "original": str(gorig)},
                     "geng_help": {"path": str(helpf), "sha256": sha_file(helpf)},
                     "source": {"path": str(src), "sha256": sha_file(src),
                                "original": str(Path(a.source).resolve())},
                     "classifier": {"path": str(cls), "sha256": sha_file(cls)},
                     "driver": {"path": str(drv), "sha256": sha_file(drv), "original": str(me)}}}
    cfgsha = sha_bytes(canonical(cfg))
    for name, text in (("config.json", json.dumps(cfg, sort_keys=True) + "\n"), ("config.sha256", cfgsha + "\n")):
        with open(root / name, "x") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(root / name, 0o444)
    print(json.dumps({"config": str(root / "config.json"), "config_sha256": cfgsha}))


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
        raise SystemExit(f"worker {w} is already running elsewhere (or an aggregate holds its lock)")
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
    """Progress indicator only.  It reads each receipt but does not re-validate it against its streams: only aggregate
    certifies a campaign."""
    cfg, _ = load_config(a.config, verify=False)
    rec = Path(cfg["root"]) / "receipts"
    ok = unreadable = failed = 0
    for f in (sorted(rec.rglob("*")) if rec.exists() else []):
        if f.name.endswith(".ok.json"):
            try:
                d = json.loads(f.read_text())
                r = int(f.name.split(".")[0])
                good = (d.get("schema") == SCHEMA and d.get("status") == "complete" and d.get("r") == r
                        and f == receipt_path(cfg, r))
            except (ValueError, OSError):
                good = False
            ok += good
            unreadable += not good
        elif ".failed." in f.name:
            failed += 1
    print(json.dumps({"mod": cfg["mod"], "ok_receipts": ok, "ok_receipts_unreadable": unreadable,
                      "failed_files": failed, "fraction": ok / cfg["mod"],
                      "note": "progress indicator, not a certificate: only aggregate validates receipts"}))


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


def _hold_worker_locks(cfg):
    """Take every worker's lock without waiting: aggregate never sums while a producer of this campaign runs.
    (flock semantics across nodes depend on how the file system is mounted; see v2/README.md.)"""
    held = []
    d = Path(cfg["root"]) / "workers"
    d.mkdir(exist_ok=True)
    for w in range(cfg["workers"]):
        f = open(d / f"{w}.lock", "a")
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(f"worker {w} holds its lock: aggregate refuses to sum while producers run")
        held.append(f)
    return held


def _canonical(labelg, graphs):
    p = subprocess.run([labelg, "-q"], input="".join(g + "\n" for g in sorted(graphs)), capture_output=True,
                       text=True)
    out = p.stdout.split()
    if p.returncode != 0 or len(out) != len(graphs):
        raise SystemExit("labelg failed or returned a different number of graphs: " + p.stderr[:300])
    return set(out)


def cmd_aggregate(a):
    cfg, cfgsha = load_config(a.config)
    root = Path(cfg["root"])
    locks = _hold_worker_locks(cfg)  # noqa: F841  (held until the process exits)
    earlier = [p for p in [root / "aggregate.json"] + sorted(root.glob("*.g6")) if p.exists()]
    if earlier:  # a failed run must never leave an earlier ok=true in place
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        hist = root / "aggregate_history" / stamp
        hist.mkdir(parents=True)
        for p in earlier:
            os.replace(p, hist / p.name)
    paths = sorted(str(p) for p in (root / "receipts").rglob("*.ok.json")) if (root / "receipts").exists() else []
    chunks = [paths[i:i + 2000] for i in range(0, len(paths), 2000)]
    keys = TABLE_KEYS if cfg["mode"] == "tabla" else SEARCH_KEYS
    sums = {k: 0 for k in keys}
    memo = {}
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
                for k, v in m.items():
                    memo[k] = memo.get(k, 0) + v
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

    def expect(key, value, source):
        c = comparison.setdefault(key, {"actual": sums[key], "expected": value, "sources": []})
        if c["expected"] != value:
            problems.append(f"conflicting expected values for {key}: {c['expected']} ({', '.join(c['sources'])}) "
                            f"and {value} ({source})")
        c["sources"].append(source)

    requested = []
    if a.reference_csv:
        if cfg["mode"] != "tabla":
            raise SystemExit("--reference-csv applies to mode tabla only")
        requested += [k for k in keys if k in CSV_COLUMNS]
        lines = [l for l in Path(a.reference_csv).read_text().splitlines() if l.strip() and not l.startswith("#")]
        reader = csv.DictReader(lines)
        fields = reader.fieldnames or []
        rows = list(reader)
        hits = [row for row in rows if (row.get("n") or "").strip() == str(cfg["n"])]
        if "n" not in fields or len(hits) != 1:
            problems.append(f"reference CSV must have exactly one row with n={cfg['n']} (found {len(hits)})")
        else:
            for k in keys:
                col = CSV_COLUMNS.get(k)
                if col is None:
                    continue
                v = (hits[0].get(col) or "").strip()
                if col not in fields or not UINT.fullmatch(v):
                    problems.append(f"reference CSV lacks a non-negative integer in column {col!r} (for {k})")
                    continue
                expect(k, int(v), "csv:" + col)
    seen_expect = set()
    for e in a.expect or []:
        k, sep, v = e.partition("=")
        if not sep or k not in sums or not UINT.fullmatch(v):
            raise SystemExit(f"bad --expect {e!r}: use KEY=VALUE with a counter of this mode and an integer >= 0")
        if k in seen_expect:
            raise SystemExit("repeated --expect key " + k)
        seen_expect.add(k)
        requested.append(k)
        expect(k, int(v), "expect")
    if a.reference_g6:
        cls = "ATASCADA" if cfg["mode"] == "atascadas" else "I_NO_IS"
        requested.append(cls + "_set")
        ref_lines = [l.split()[0] for l in Path(a.reference_g6).read_text().splitlines()
                     if l.strip() and not l.startswith("#")]
        ref = set(ref_lines)
        got = found.get(cls, set())
        bad = [g for g in ref_lines if not valid_g6(g, cfg["n"])]
        if bad:
            problems.append(f"reference graph6 file has {len(bad)} invalid strings for n={cfg['n']}")
        if len(ref) != len(ref_lines):
            problems.append("reference graph6 file repeats a string")
        entry = {"actual": len(got), "expected": len(ref),
                 "sources": [f"g6:{Path(a.reference_g6).resolve()}@{sha_file(a.reference_g6)}"]}
        if a.labelg and not bad:
            rc, gc = _canonical(a.labelg, ref), _canonical(a.labelg, got)
            entry.update(compared="up to isomorphism (labelg -q, SHA-256 " + sha_file(a.labelg) + ")",
                         only_found=len(gc - rc), only_reference=len(rc - gc),
                         equal=rc == gc and len(rc) == len(ref) and len(gc) == len(got))
        else:
            entry.update(compared="labelled strings", only_found=sorted(got - ref)[:20],
                         only_reference=sorted(ref - got)[:20], equal=got == ref)
        comparison[cls + "_set"] = entry
    for k in requested:
        if k not in comparison:
            problems.append(f"requested comparison for {k} could not be made")
    for k, v in comparison.items():
        v.setdefault("equal", v["actual"] == v["expected"])
        if not v["equal"]:
            problems.append(f"comparison failed: {k}")
    load_config(a.config)
    result = {"config_sha256": cfgsha, "n": cfg["n"], "mod": cfg["mod"], "mode": cfg["mode"], "coverage": coverage,
              "counts": sums, "memo_totals": memo, "found_counts": {k: len(v) for k, v in found.items()},
              "comparison": comparison, "requested_comparisons": sorted(set(requested)), "problems": problems,
              "ok": not problems, "utc": utcnow()}
    for k, gs in found.items():
        tmp = root / f"{k}.g6.tmp.{uuid.uuid4().hex}"
        tmp.write_text("".join(g + "\n" for g in sorted(gs)))
        os.replace(tmp, root / f"{k}.g6")
    atomic_json(root / "aggregate.json", result)
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
    q.add_argument("--expect-geng-version", required=True,
                   help="version token printed by geng --version, compared exactly (e.g. 2.9301)")
    q.add_argument("--expect-geng-sha256", required=True, help="SHA-256 of the geng binary")
    q.add_argument("--protect", action="append", default=[], help="extra directory that must not contain ROOT")
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
    q.add_argument("--labelg", help="nauty labelg: compare --reference-g6 up to isomorphism")
    a = p.parse_args()
    {"init": cmd_init, "worker": cmd_worker, "status": cmd_status, "aggregate": cmd_aggregate}[a.cmd](a)


if __name__ == "__main__":
    main()
