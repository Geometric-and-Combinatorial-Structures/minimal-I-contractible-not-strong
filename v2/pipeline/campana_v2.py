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
  * classifier (v2/src/atascadas_v2.c): exit 0, stderr is exactly one summary line with the pinned version (v2.2), invalidos=0,
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
    leaves ROOT/INIT_FAILED.txt with the reason (nothing is deleted; v2.2 makes every subcommand refuse such a root);
  * aggregate refuses to run while a worker holds its lock, moves earlier outputs to aggregate_history/ (v2.2: before
    it takes any worker lock, so a failed run never leaves an old ok=true in place), and compares references strictly: exactly one CSV row
    with every column of the mode, unique --expect keys, any conflict between sources is fatal, and a requested
    comparison can never be empty; --labelg compares graph sets up to isomorphism;
  * status counts readable receipts and is explicitly not a certificate.

v2.2 (round 3 of the external audit: residues of H-22, H-23, H-24, H-29 and request S4), corrected by class:
  * init writes nothing before every input has been validated: it parses --geng-args and --cflags (shlex) and
    requires `geng --help` to exit 0 with some output before it creates ROOT;
  * a campaign exists only once init has finished: the last step of init writes ROOT/INIT_COMPLETE.json with the
    config hash; worker, status and aggregate refuse a root without it, or with ROOT/INIT_FAILED.txt, whatever
    config.json contains;
  * every JSON file the driver reads is parsed strictly (no NaN or Infinity, no repeated keys); JSON is written with
    allow_nan=False;
  * a receipt must have exactly the documented keys; its identities, exit codes and counters are integers of exact
    type (a boolean is not an integer); seconds is finite and >= 0; utc_start and utc_end have this driver's own UTC
    format, are ordered (5 s tolerance) and lie between the creation of the campaign and the validation (300 s
    tolerance); stored counters, records and commands are compared canonically, so 1 and true differ;
  * references: the CSV header must name each column once and every row must have as many fields as the header;
    --expect is given once per KEY=VALUE (write --expect=-1-Dis=V for the key that starts with '-'), so a requested
    comparison cannot be empty; the path and SHA-256 of every reference (CSV, graph6, labelg) go into aggregate.json;
  * aggregate takes ROOT/aggregate.lock, records the attempt in aggregate_attempts/<id>.json and archives earlier
    outputs to aggregate_history/<id>/ first; then it parses and checks every reference (CSV, --expect, graph6
    file, labelg), takes the worker locks and sums.  Any failure (refused reference, busy worker, invalid receipt)
    leaves aggregate.json with ok=false, status failed and the reason, and a failed attempt record; no earlier
    ok=true stays in the normal location; aggregate.json names its attempt_id;
  * status counts an unreadable or non-object receipt as unreadable instead of failing.

v2.3 (round 4 of the external audit: residues of H-22 and H-29), driver only (the classifier stays v2.2):
  * an executable is run only as the bytes that were hashed: aggregate copies labelg into a private read-only
    file of the attempt (aggregate_attempts/<id>.tools/), checks its SHA-256 before and after every run and
    refuses any difference; labelg must pass a self-test (P4 and a relabelled P4 coincide, P4 and K1,3 differ)
    and return graph6 strings of the right order; the reference files (CSV, graph6, labelg) are hashed again at
    the end and any change fails the attempt; workers check the SHA-256 of the pinned geng and classifier before
    and after every slice and publish nothing on a difference; init pins the SHA-256 of geng that it compared with
    --expect-geng-sha256 (computed once) and verifies every pinned file again before it writes INIT_COMPLETE.json;
  * every write of aggregate is inside its transaction, the first record of the attempt included; the attempt
    record becomes terminal (status ok or problems, with the SHA-256 of the aggregate it is about to
    publish) before aggregate.json is published, and the summary is printed before as well; publishing
    aggregate.json is the last operation, so aggregate.json with ok=true always belongs to an attempt whose record
    is terminal and names its hash.  A modification restored to the same bytes between two checks, or a change of
    the bytes of a running process, is not detected (the auditor's stated limit).

Exit codes of the classifier (v2.2): 0 ok, 1 usage, 2 capacity, 3 invalid records, 4 inconsistency or read error,
5 disconnected input or mixed orders, 6 write error on stdout/stderr; 6 takes priority over every other code in every
exit of the program, early ones included (v2.2).

Subcommands:
  init      --root R --n N --mod M --workers W --mode tabla|atascadas --geng PATH --geng-args="-c" --source atascadas_v2.c
            (write --geng-args=VALUE with '=' because the value starts with '-')
            --expect-geng-version TOKEN --expect-geng-sha256 HEX      (both required; TOKEN as printed, e.g. 2.9301)
            [--cflags "-O3 -std=c11 -Wall -Wextra -Wpedantic -Werror"] [--protect DIR ...]
            creates R (which must not exist), copies geng, the source and this driver into R/bin (read-only),
            compiles the classifier there and pins all SHA-256.
  worker    --config R/config.json --worker-id i [--procs P]     (P concurrent pipelines, one CPU each)
  status    --config R/config.json
  aggregate --config R/config.json [--jobs J] [--reference-csv data/table_cardinalities.csv]
            [--expect KEY=VALUE] ... (once per key; --expect=-1-Dis=V for the key that starts with '-')
            [--reference-g6 FILE [--labelg PATH]]   writes R/aggregate.json and R/<record class>.g6; exit 0 only if
            coverage is exact, all receipts validate, all invariants hold and all requested comparisons are equal.
"""
import argparse, concurrent.futures, csv, datetime, fcntl, hashlib, json, math, os, re, shlex, shutil, subprocess, sys
import threading
import time, uuid
from pathlib import Path

SCHEMA = "campana_v2/2"
CLASSIFIER_VERSION = "v2.2"
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
RECEIPT_KEYS = frozenset({
    "schema", "r", "mod", "config_sha256", "cmd_geng", "cmd_classifier", "exit_geng", "exit_classifier", "seconds",
    "utc_start", "utc_end", "host", "worker_id", "slurm_job_id", "slurm_array_job_id", "slurm_array_task_id", "status",
    "geng_stderr", "geng_stderr_sha256", "classifier_stderr", "classifier_stderr_sha256", "result_stdout",
    "result_stdout_sha256", "counts", "records", "memo"})          # the keys of a complete receipt (v2.2)
UTC_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{6})?\+00:00")
CLOCK_ORDER_TOLERANCE = 5.0      # s: utc_end may precede utc_start by at most this (wall-clock steps)
CLOCK_WINDOW_TOLERANCE = 300.0   # s: receipt times lie between the creation of the campaign and the validation
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


def _reject_constant(name):
    raise ValueError(f"non-finite number {name} in JSON")


def _unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError(f"repeated JSON key {k!r}")
        d[k] = v
    return d


def strict_json(text):
    """json.loads that refuses NaN, Infinity and repeated keys (v2.2)."""
    return json.loads(text, parse_constant=_reject_constant, object_pairs_hook=_unique_pairs)


def is_int(x):
    """An integer of exact type: a boolean is not an integer here (v2.2)."""
    return type(x) is int


def parse_utc(s):
    """This driver's own UTC timestamps (datetime.isoformat() with +00:00); anything else is refused (v2.2)."""
    if not isinstance(s, str) or not UTC_RE.fullmatch(s):
        raise ValueError(f"not a UTC timestamp of this driver: {str(s)[:40]!r}")
    return datetime.datetime.fromisoformat(s)


def json_bytes(obj):
    """The exact bytes atomic_json writes: sorted keys, ASCII, no NaN or Infinity, final newline."""
    return (json.dumps(obj, sort_keys=True, allow_nan=False) + "\n").encode()


def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp." + uuid.uuid4().hex)
    with open(tmp, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def atomic_json(path, obj):
    atomic_bytes(path, json_bytes(obj))


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
def _verify_files(cfg):
    for name, item in cfg["files"].items():
        if sha_file(item["path"]) != item["sha256"]:
            raise ValueError(f"pinned file changed: {name} {item['path']}")


def load_config(path, verify=True):
    path = Path(path)
    cfg = strict_json(path.read_text())
    if not isinstance(cfg, dict) or cfg.get("schema") != SCHEMA:
        raise ValueError("unknown config schema")
    cfgsha = sha_bytes(canonical(cfg))
    root = Path(cfg["root"])
    if path.resolve().parent != root.resolve():
        raise ValueError(f"config.json is not in its campaign root {root}")
    # v2.2 (H-23): a root exists as a campaign only once init has finished, and never after a failed init
    if (root / "INIT_FAILED.txt").exists():
        raise ValueError("init of this campaign failed (INIT_FAILED.txt): the root cannot be used; start a new one")
    if verify:
        pin = Path(path).with_name("config.sha256")
        if not pin.exists() or pin.read_text().strip() != cfgsha:
            raise ValueError("config.json differs from its pinned hash config.sha256 (a campaign cannot be edited)")
        _verify_files(cfg)
        if sha_file(Path(__file__).resolve()) != cfg["files"]["driver"]["sha256"]:
            raise ValueError("this driver differs from the one pinned at init: run " + cfg["files"]["driver"]["path"])
    try:
        mark = strict_json((root / "INIT_COMPLETE.json").read_text())
    except (OSError, ValueError) as e:
        raise ValueError("init of this campaign did not finish (INIT_COMPLETE.json missing or unreadable)") from e
    if not isinstance(mark, dict) or mark.get("schema") != SCHEMA or mark.get("config_sha256") != cfgsha:
        raise ValueError("INIT_COMPLETE.json does not certify this config.json")
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


def validate_receipt(cfg, cfgsha, r, d, now=None):
    """Strict schema (v2.2, H-24): exactly RECEIPT_KEYS; exact integer types; finite non-negative seconds; ordered UTC
    times of this driver inside the life of the campaign; streams re-checked and summaries compared canonically."""
    if not isinstance(d, dict):
        raise SliceError("receipt is not a JSON object")
    if set(d) != RECEIPT_KEYS:
        raise SliceError(f"receipt keys differ from the schema: missing {sorted(RECEIPT_KEYS - set(d))}, "
                         f"unexpected {sorted(set(d) - RECEIPT_KEYS)[:10]}")
    if d["schema"] != SCHEMA or d["status"] != "complete":
        raise SliceError("receipt not complete")
    if not (is_int(d["r"]) and d["r"] == r and is_int(d["mod"]) and d["mod"] == cfg["mod"]
            and d["config_sha256"] == cfgsha):
        raise SliceError("receipt identity mismatch")
    w = d["worker_id"]
    if not is_int(w) or not (0 <= w < cfg["workers"]) or r % cfg["workers"] != w:
        raise SliceError(f"worker {w!r} does not own residue {r} (workers={cfg['workers']})")
    if not isinstance(d["host"], str) or not d["host"]:
        raise SliceError("receipt provenance missing or malformed: host")
    for k in ("slurm_job_id", "slurm_array_job_id", "slurm_array_task_id"):
        if d[k] is not None and (not isinstance(d[k], str) or not d[k]):
            raise SliceError("receipt provenance malformed: " + k)
    sec = d["seconds"]
    if type(sec) not in (int, float) or not math.isfinite(sec) or sec < 0:
        raise SliceError("receipt provenance missing or malformed: seconds")
    try:
        t0, t1, born = parse_utc(d["utc_start"]), parse_utc(d["utc_end"]), parse_utc(cfg.get("created_utc"))
    except ValueError as e:
        raise SliceError("receipt provenance malformed: " + str(e)) from e
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if (t0 - t1).total_seconds() > CLOCK_ORDER_TOLERANCE:
        raise SliceError("receipt times out of order (utc_end before utc_start)")
    if (born - t0).total_seconds() > CLOCK_WINDOW_TOLERANCE or (t1 - now).total_seconds() > CLOCK_WINDOW_TOLERANCE:
        raise SliceError("receipt times outside the life of the campaign")
    g, c = commands(cfg, r)
    if canonical(d["cmd_geng"]) != canonical(g) or canonical(d["cmd_classifier"]) != canonical(c):
        raise SliceError("receipt commands differ from config")
    if not (is_int(d["exit_geng"]) and d["exit_geng"] == 0 and is_int(d["exit_classifier"])
            and d["exit_classifier"] == 0):
        raise SliceError("nonzero (or non-integer) exit status in receipt")
    for name in ("geng_stderr", "classifier_stderr", "result_stdout"):
        if not isinstance(d[name], str) or sha_bytes(d[name].encode()) != d[name + "_sha256"]:
            raise SliceError("stored stream hash mismatch: " + name)
    counts, records, memo = check_slice(cfg, d["geng_stderr"], d["classifier_stderr"], d["result_stdout"], r)
    if (canonical(counts) != canonical(d["counts"]) or canonical(records) != canonical(d["records"])
            or canonical(memo) != canonical(d["memo"])):
        raise SliceError("receipt summary differs from its stored streams")
    return counts, records, memo


# ------------------------------------------------------------------------------------------------ run one slice
def _check_pinned(cfg, when):
    """v2.3 (class of H-22, round 4): the executables a slice runs are the pinned bytes, before and after it runs."""
    for key in ("geng", "classifier"):
        f = cfg["files"][key]
        if sha_file(f["path"]) != f["sha256"]:
            raise SliceError(f"pinned {key} {f['path']} changed {when} the slice: nothing is published")


def run_slice(cfg, cfgsha, r, worker_id):
    dst = receipt_path(cfg, r)
    if dst.exists():
        try:
            old = strict_json(dst.read_text())
        except ValueError as e:
            raise SliceError(f"existing receipt unreadable: {e}") from e
        validate_receipt(cfg, cfgsha, r, old)
        return "resumed"
    g, c = commands(cfg, r)
    _check_pinned(cfg, "before")
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
         "slurm_job_id": os.environ.get("SLURM_JOB_ID") or None,
         "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID") or None,
         "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID") or None, "status": "failed"}
    for name, data in (("geng_stderr", box.get("err", b"")), ("classifier_stderr", err), ("result_stdout", out)):
        d[name] = data.decode("utf-8", errors="replace")
        d[name + "_sha256"] = sha_bytes(d[name].encode())
    try:
        _check_pinned(cfg, "while running")
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
    try:  # v2.2 (H-23): syntax errors are found before anything is written
        geng_args, cflags = shlex.split(a.geng_args), shlex.split(a.cflags)
    except ValueError as e:
        raise SystemExit(f"--geng-args or --cflags cannot be parsed ({e}); nothing was written")
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
    if gh.returncode != 0 or not ghelp.strip():  # v2.2 (H-23)
        raise SystemExit(f"geng --help exited {gh.returncode} or printed nothing; refusing to pin this generator")
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
        _init_populate(a, root, protected, gorig, gver, gtok, ghelp, geng_args, cflags)
    except BaseException as e:
        # nothing is deleted: the directory stays, without config.json (workers refuse it), with the reason
        with open(root / "INIT_FAILED.txt", "a") as f:
            f.write(f"{utcnow()} init failed: {e}\n")
        raise


def _init_populate(a, root, protected, gorig, gver, gtok, ghelp, geng_args, cflags):
    binr = root / "bin"
    os.mkdir(binr)
    geng, src, cls, drv = binr / "geng", binr / "atascadas_v2.c", binr / "atascadas_v2", binr / "campana_v2.py"
    me = Path(__file__).resolve()
    for orig, dst in ((gorig, geng), (a.source, src), (me, drv)):
        shutil.copy2(orig, dst)
        if sha_file(dst) != sha_file(orig):
            raise SystemExit("copy differs from original: " + str(orig))
    gsha = sha_file(geng)            # v2.3 (class of H-22): hashed once; this value is the one pinned
    if gsha != a.expect_geng_sha256.lower():
        raise SystemExit("copied geng differs from --expect-geng-sha256 (the original changed during init)")
    helpf = binr / "geng_help.txt"
    with open(helpf, "x") as f:
        f.write(ghelp)
    cc = ["gcc"] + cflags + ["-o", str(cls), str(src)]
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
           "geng_args": geng_args, "compile_command": cc, "compiler": ccv,
           "geng_version": gver, "geng_version_token": gtok, "geng_help_sha256": sha_file(helpf),
           "classifier_version": cv.stdout.strip(), "classifier_summary_version": CLASSIFIER_VERSION,
           "protected": protected, "created_utc": utcnow(), "created_host": os.uname().nodename,
           "files": {"geng": {"path": str(geng), "sha256": gsha, "original": str(gorig)},
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
    sys.stdout.flush()
    try:                             # v2.3: every pinned file is still the pinned bytes when init certifies
        _verify_files(cfg)
    except ValueError as e:
        raise SystemExit(f"{e} during init: the campaign is not certified")
    # v2.2 (H-23): the very last step.  Workers, status and aggregate require this marker, so a failure at any earlier
    # point (INIT_FAILED.txt is then written by cmd_init) leaves a root that every subcommand refuses.
    atomic_json(root / "INIT_COMPLETE.json", {"schema": SCHEMA, "config_sha256": cfgsha, "utc": utcnow()})


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
                d = strict_json(f.read_text())
                r = int(f.name.split(".")[0])
                good = (isinstance(d, dict) and d.get("schema") == SCHEMA and d.get("status") == "complete"
                        and is_int(d.get("r")) and d.get("r") == r and f == receipt_path(cfg, r))
            except Exception:  # noqa: BLE001  (v2.2, H-29: anything that is not a readable receipt object counts as unreadable)
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
        try:
            d = strict_json(Path(p).read_text())
        except ValueError as e:
            raise SliceError(f"receipt {p} unreadable: {e}") from e
        counts, records, memo = validate_receipt(cfg, cfgsha, r, d)
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


CANON_CONTROLS = ("Ch", "Cp", "Cs")   # graph6 of order 4: P4, a relabelled P4, the star K1,3 (also 3 edges)


def _freeze_tool(src, dest_dir, name):
    """v2.3 (H-22, round 4): a private read-only copy of an external tool, made from the bytes that are hashed."""
    data = Path(src).read_bytes()
    dest_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    dest = dest_dir / name
    with open(dest, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(dest, 0o500)
    return {"kind": name, "path": str(Path(src).resolve()), "sha256": sha_bytes(data), "frozen_copy": str(dest)}


def _run_frozen(tool, args, text):
    """Run the frozen copy only if its bytes are the hashed ones, and accept its output only if they still are."""
    if sha_file(tool["frozen_copy"]) != tool["sha256"]:
        raise SystemExit(f"the frozen copy of {tool['kind']} changed before it was run: refusing")
    p = subprocess.run([tool["frozen_copy"], *args], input=text, capture_output=True, text=True)
    if sha_file(tool["frozen_copy"]) != tool["sha256"]:
        raise SystemExit(f"the frozen copy of {tool['kind']} changed while it ran: refusing its output")
    return p


def _canonical_list(tool, graphs):
    p = _run_frozen(tool, ["-q"], "".join(g + "\n" for g in graphs))
    out = p.stdout.split()
    if p.returncode != 0 or len(out) != len(graphs):
        raise SystemExit("labelg failed or returned a different number of graphs: " + p.stderr[:300])
    return out


def _canonical(tool, graphs, n):
    out = _canonical_list(tool, sorted(graphs))
    bad = [x for x in out if not valid_g6(x, n)]
    if bad:
        raise SystemExit(f"labelg returned {len(bad)} strings that are not graph6 of order {n}")
    return set(out)


def _canonizer_selftest(tool):
    """A canonizer identifies a graph with a relabelling of it and separates non-isomorphic graphs (v2.3)."""
    a, b, c = _canonical_list(tool, list(CANON_CONTROLS))
    if not (a == b and a != c and all(valid_g6(x, 4) for x in (a, b, c))):
        raise SystemExit("labelg failed its self-test (P4, a relabelled P4 and the star K1,3): not a canonizer")


def _read_reference(path, what):
    try:
        data = path.read_bytes()
    except OSError as e:
        raise SystemExit(f"cannot read the {what} {path}: {e}")
    try:
        return data, data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise SystemExit(f"the {what} {path} is not UTF-8 text ({e})")


def _load_references(a, cfg, tools_dir):
    """Parse and check every reference before any worker lock is taken or any count is summed (v2.2, H-22).
    cmd_aggregate calls it after it has recorded the attempt and archived the earlier outputs, so a refused
    reference leaves aggregate.json with ok=false.  Returns the expected values (key, value, source), the requested
    comparisons, the graph6 reference, labelg and, for aggregate.json, the path and SHA-256 of every reference."""
    keys = TABLE_KEYS if cfg["mode"] == "tabla" else SEARCH_KEYS
    out = {"expected": [], "requested": [], "g6": None, "labelg": None, "records": []}
    if a.reference_csv:
        if cfg["mode"] != "tabla":
            raise SystemExit("--reference-csv applies to mode tabla only")
        path = Path(a.reference_csv).resolve()
        data, text = _read_reference(path, "reference CSV")
        lines = [l for l in text.splitlines() if l.strip() and not l.startswith("#")]
        rows = list(csv.reader(lines))
        if not rows:
            raise SystemExit("reference CSV has no header")
        header = [h.strip() for h in rows[0]]
        repeated = sorted({h for h in header if header.count(h) > 1})
        if repeated or any(not h for h in header):
            raise SystemExit(f"reference CSV header must name each column once (repeated or empty: {repeated})")
        if "n" not in header:
            raise SystemExit("reference CSV has no column n")
        uneven = [i + 2 for i, row in enumerate(rows[1:]) if len(row) != len(header)]
        if uneven:
            raise SystemExit(f"reference CSV rows {uneven[:5]} do not have as many fields as the header")
        table = [dict(zip(header, (c.strip() for c in row))) for row in rows[1:]]
        hits = [row for row in table if row["n"] == str(cfg["n"])]
        if len(hits) != 1:
            raise SystemExit(f"reference CSV must have exactly one row with n={cfg['n']} (found {len(hits)})")
        for k in keys:
            col = CSV_COLUMNS.get(k)
            if col is None:
                continue
            v = hits[0].get(col, "")
            if col not in header or not UINT.fullmatch(v):
                raise SystemExit(f"reference CSV lacks a non-negative integer in column {col!r} (for {k})")
            out["expected"].append((k, int(v), "csv:" + col))
            out["requested"].append(k)
        out["records"].append({"kind": "csv", "path": str(path), "sha256": sha_bytes(data), "row_n": cfg["n"]})
    seen = set()
    for e in a.expect or []:
        k, sep, v = e.partition("=")
        if not sep or k not in keys or not UINT.fullmatch(v):
            raise SystemExit(f"bad --expect {e!r}: use KEY=VALUE with a counter of this mode and an integer >= 0 "
                             "(write --expect=-1-Dis=V for the key that starts with '-')")
        if k in seen:
            raise SystemExit("repeated --expect key " + k)
        seen.add(k)
        out["expected"].append((k, int(v), "expect"))
        out["requested"].append(k)
    if a.labelg and not a.reference_g6:
        raise SystemExit("--labelg needs --reference-g6")
    if a.reference_g6:
        path = Path(a.reference_g6).resolve()
        data, text = _read_reference(path, "reference graph6 file")
        ref = [l.split()[0] for l in text.splitlines() if l.strip() and not l.startswith("#")]
        bad = [g for g in ref if not valid_g6(g, cfg["n"])]
        if bad:
            raise SystemExit(f"reference graph6 file has {len(bad)} invalid strings for n={cfg['n']}")
        if len(set(ref)) != len(ref):
            raise SystemExit("reference graph6 file repeats a string")
        if not ref:
            raise SystemExit("reference graph6 file is empty (state a zero count with --expect instead)")
        out["g6"] = ref
        out["records"].append({"kind": "graph6", "path": str(path), "sha256": sha_bytes(data), "graphs": len(ref)})
        if a.labelg:
            lp = Path(a.labelg).resolve()
            if not lp.is_file() or not os.access(lp, os.X_OK):
                raise SystemExit(f"labelg {lp} is not an executable file")
            tool = _freeze_tool(lp, tools_dir, "labelg")   # v2.3: run from a frozen copy, never from lp
            _canonizer_selftest(tool)
            out["labelg"] = tool
            out["records"].append(tool)
    return out


def cmd_aggregate(a):
    cfg, cfgsha = load_config(a.config)
    root = Path(cfg["root"])
    alock = open(root / "aggregate.lock", "a")
    try:
        fcntl.flock(alock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("another aggregate of this campaign is running (aggregate.lock)")
    attempt = (datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + "-"
               + uuid.uuid4().hex[:8])
    record = {"attempt_id": attempt, "config_sha256": cfgsha, "status": "started", "utc_start": utcnow(),
              "host": os.uname().nodename, "slurm_job_id": os.environ.get("SLURM_JOB_ID") or None,
              "argv": sys.argv[1:], "references": None}
    rec_path = root / "aggregate_attempts" / f"{attempt}.json"
    try:
        atomic_json(rec_path, record)    # v2.3: inside the transaction, so even this write failing publishes ok=false
        earlier = [p for p in [root / "aggregate.json"] + sorted(root.glob("*.g6")) if p.exists()]
        if earlier:  # v2.2 (H-29): first of all, so a failed attempt never leaves an earlier ok=true in place
            hist = root / "aggregate_history" / attempt
            hist.mkdir(parents=True)
            for p in earlier:
                os.replace(p, hist / p.name)
        refs = _load_references(a, cfg, root / "aggregate_attempts" / f"{attempt}.tools")  # (H-22) before locks
        record["references"] = refs["records"]
        atomic_json(rec_path, record)
        locks = _hold_worker_locks(cfg)  # noqa: F841  (held until the process exits)
        result = _aggregate(a, cfg, cfgsha, root, refs, attempt)
        data = json_bytes(result)
        # v2.3 (H-29, round 4): the attempt record becomes terminal, with the SHA-256 of the aggregate, BEFORE the
        # aggregate is published; the summary is printed before as well; publishing aggregate.json is the last
        # operation, so a failure anywhere leaves no ok=true for this attempt.
        record.update(status="ok" if result["ok"] else "problems", problems=result["problems"], utc_end=utcnow(),
                      aggregate_sha256=sha_bytes(data))
        atomic_json(rec_path, record)
        print(json.dumps({k: result[k] for k in ("n", "mod", "coverage", "counts", "found_counts", "problems", "ok")}))
        sys.stdout.flush()
        atomic_bytes(root / "aggregate.json", data)
    except BaseException as e:
        msg = f"{type(e).__name__}: {e}"[:2000]
        record.update(status="failed", error=msg, utc_end=utcnow())
        try:  # the normal location says explicitly that this attempt failed
            atomic_json(root / "aggregate.json", {"config_sha256": cfgsha, "attempt_id": attempt, "status": "failed",
                                                  "ok": False, "problems": [msg], "utc": utcnow()})
        finally:
            atomic_json(rec_path, record)
        raise
    sys.exit(0 if result["ok"] else 1)


def _aggregate(a, cfg, cfgsha, root, refs, attempt):
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

    requested = list(refs["requested"])
    for k, v, source in refs["expected"]:
        expect(k, v, source)
    if refs["g6"] is not None:
        cls = "ATASCADA" if cfg["mode"] == "atascadas" else "I_NO_IS"
        requested.append(cls + "_set")
        ref_lines = refs["g6"]
        ref = set(ref_lines)
        got = found.get(cls, set())
        g6rec = [x for x in refs["records"] if x["kind"] == "graph6"][0]
        entry = {"actual": len(got), "expected": len(ref), "sources": [f"g6:{g6rec['path']}@{g6rec['sha256']}"]}
        if refs["labelg"]:
            rc, gc = _canonical(refs["labelg"], ref, cfg["n"]), _canonical(refs["labelg"], got, cfg["n"])
            entry.update(compared="up to isomorphism (labelg -q run from a frozen copy with SHA-256 "
                                  + refs["labelg"]["sha256"] + ", checked before and after each run)",
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
    for rec in refs["records"]:      # v2.3 (H-22): the references are still the hashed bytes at the end
        try:
            now = sha_file(rec["path"])
        except OSError:
            now = None
        if now != rec["sha256"]:
            problems.append(f"reference {rec['kind']} {rec['path']} changed during the attempt (SHA-256 now {now})")
    load_config(a.config)
    result = {"config_sha256": cfgsha, "attempt_id": attempt, "n": cfg["n"], "mod": cfg["mod"], "mode": cfg["mode"],
              "coverage": coverage, "counts": sums, "memo_totals": memo, "found_counts": {k: len(v) for k, v in found.items()},
              "comparison": comparison, "requested_comparisons": sorted(set(requested)), "references": refs["records"],
              "problems": problems, "ok": not problems, "utc": utcnow()}
    for k, gs in found.items():
        tmp = root / f"{k}.g6.tmp.{uuid.uuid4().hex}"
        tmp.write_text("".join(g + "\n" for g in sorted(gs)))
        os.replace(tmp, root / f"{k}.g6")
    return result


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
    q.add_argument("--expect", action="append", metavar="KEY=VALUE",
                   help="once per key (v2.2); write --expect=-1-Dis=V for the key that starts with '-'")
    q.add_argument("--reference-g6")
    q.add_argument("--labelg", help="nauty labelg: compare --reference-g6 up to isomorphism (run from a frozen "
                                    "private copy checked by SHA-256 before and after each run, after a self-test)")
    a = p.parse_args()
    {"init": cmd_init, "worker": cmd_worker, "status": cmd_status, "aggregate": cmd_aggregate}[a.cmd](a)


if __name__ == "__main__":
    main()
