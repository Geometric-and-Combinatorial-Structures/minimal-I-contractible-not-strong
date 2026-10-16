#!/usr/bin/env python3
"""Independent check of Table B.1 (tables/stuck51.tex) and Fig. 7 (figures/fig07.pdf, the mosaic of the
51 stuck Z/2-acyclic K4-free graphs on 14 vertices).

Every value is recomputed from the graph6 strings; data/stuck_14_K4free.{g6,tsv} and
data/structure_84_graphs.csv are only compared against.

  python3 verification/check_table_B1_fig07.py --table paper/tables/stuck51.tex --figure paper/figures/fig07.pdf

Run from the repository root (needs networkx; --figure also needs poppler's pdftotext).
Exit status 0 iff every check passes.

Checks
  T1  the 51 table strings are exactly the 51 strings of data/stuck_14_K4free.g6 / .tsv, pairwise non-isomorphic
  T2  edges m and triangles t: table = TSV = recomputed
  T3  H_1: table = TSV = exact integer homology of the clique complex (Smith normal form, tools/clique_homology.py);
      all other reduced homology groups vanish
  T4  |Aut|: table = TSV = number of automorphisms (networkx GraphMatcher)
  T5  I4 column: '({a,b})' exactly for the H_1 = 0 rows, {a,b} a non-edge, equal to the TSV entry; 'no' otherwise
  T6  unfolding (glue only across edges in exactly two triangles): the result is a surface; disc / annulus /
      annulus + disc as stated in the table; for discs: disc vertices and boundary length = TSV = structure CSV,
      k = number of edges in exactly three triangles = table = CSV, |rotation number| of the boundary word around
      the identification cycle = 3 for pattern a^3 and 1 for a a a^{-1}; '(+spur)' iff an edge lies in four triangles
  T7  the 47-edge graph: its edges in three triangles form two vertex-disjoint 4-cycles (Section 6, Fig. 7 legend '**')
  T8  every edge of every graph lies in at least two triangles (Section 7); graphs with an edge in four triangles listed
  T9  counts stated in Section 6: torsion graphs by edges 43 (25), 44 (18), 45 (4), 47 (1); torsion discs on cycles of
      length 4 (25), 5 (18), 6 (2), all with pattern a^3; two annuli; one annulus + disc; table order
  F1  figure: every table string appears once; caption '<m> edges · H1 = ...' agrees; marks '*' exactly on the annuli
      and '**' exactly on the annulus + disc; every word of text lies inside the page box
"""
import argparse, collections, csv, itertools, re, subprocess, sys, warnings

warnings.filterwarnings("ignore", category=UserWarning, module="networkx")

sys.path.insert(0, "tools")
import clique_homology as ch  # noqa: E402
import networkx as nx  # noqa: E402
from networkx.algorithms.isomorphism import GraphMatcher  # noqa: E402

FAILS = []


def check(cond, tag, msg):
    if not cond:
        FAILS.append(f"{tag}: {msg}")
    return cond


def g6_decode(s):
    n = ord(s[0]) - 63
    bits = []
    for c in s[1:]:
        v = ord(c) - 63
        bits += [(v >> (5 - k)) & 1 for k in range(6)]
    G = nx.Graph()
    G.add_nodes_from(range(n))
    b = 0
    for j in range(1, n):
        for i in range(j):
            if bits[b]:
                G.add_edge(i, j)
            b += 1
    return G


def unescape_tex(s):
    for a, b in [(r"\textasciitilde{}", "~"), (r"\textasciigrave{}", "`"), (r"\textbackslash{}", "\\"),
                 (r"\^{}", "^"), (r"\_", "_"), (r"\}", "}"), (r"\{", "{")]:
        s = s.replace(a, b)
    return s


ROW = re.compile(r"^(\d+) & \\texttt\{(.*?)\} & (\d+) & (\d+) & (.*?) & (.*?) & (\d+) & (.*?) \\\\$", re.M)


def parse_table(path):
    rows = []
    for m in ROW.finditer(open(path, encoding="utf-8").read()):
        kp = m.group(8)
        r = dict(idx=int(m.group(1)), g6=unescape_tex(m.group(2)), m=int(m.group(3)), t=int(m.group(4)),
                 H1={"$0$": "0", r"$\ZZ/3$": "Z/3"}.get(m.group(5), m.group(5)), I4=m.group(6),
                 aut=int(m.group(7)), kp=kp)
        if "/" in kp:
            r["kind"] = "disc"
            r["k"] = int(kp.split("/")[0])
            r["pattern"] = "a^3" if "a^{3}" in kp else "a a a^-1" if "a^{-1}" in kp else "?"
            r["spur"] = "spur" in kp
        else:
            r["kind"] = {"annulus": "annulus", "not a disc": "annulus+disc"}.get(kp.strip(), kp)
        rows.append(r)
    return rows


def triangles(G):
    return [t for t in itertools.combinations(sorted(G), 3)
            if G.has_edge(t[0], t[1]) and G.has_edge(t[0], t[2]) and G.has_edge(t[1], t[2])]


def unfold(G):
    """Glue the triangles of the clique complex only across edges in exactly two triangles."""
    T = triangles(G)
    inc = collections.defaultdict(list)
    for ti, t in enumerate(T):
        for e in itertools.combinations(t, 2):
            inc[e].append(ti)
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tpar = list(range(len(T)))

    def tfind(x):
        while tpar[x] != x:
            tpar[x] = tpar[tpar[x]]
            x = tpar[x]
        return x

    for ti, t in enumerate(T):
        for v in t:
            find((ti, v))
    interior = [e for e, ts in inc.items() if len(ts) == 2]
    for e in interior:
        t1, t2 = inc[e]
        for v in e:
            parent[find((t1, v))] = find((t2, v))
        tpar[tfind(t1)] = tfind(t2)
    cut_sides = [(ti, e) for e, ts in inc.items() if len(ts) != 2 for ti in ts]

    def side_id(ti, e):
        return ("i", e) if len(inc[e]) == 2 else ("c", ti, e)

    # surface check: the link of every corner class is a path (boundary) or a cycle (interior)
    links = collections.defaultdict(nx.MultiGraph)
    for ti, t in enumerate(T):
        for v in t:
            a, b = [tuple(sorted((v, x))) for x in t if x != v]
            links[find((ti, v))].add_edge(side_id(ti, a), side_id(ti, b))
    surface = True
    for L in links.values():
        degs = [d for _, d in L.degree()]
        if not nx.is_connected(L) or max(degs) > 2 or sum(1 for d in degs if d == 1) not in (0, 2):
            surface = False
    comps = collections.defaultdict(list)
    for ti in range(len(T)):
        comps[tfind(ti)].append(ti)
    out = []
    for ts in comps.values():
        S = set(ts)
        V = {find((ti, v)) for ti in ts for v in T[ti]}
        E = sum(1 for e in interior if inc[e][0] in S) + sum(1 for (ti, e) in cut_sides if ti in S)
        chi = len(V) - E + len(ts)
        B = nx.MultiGraph()
        for (ti, e) in cut_sides:
            if ti in S:
                B.add_edge(find((ti, e[0])), find((ti, e[1])), side=(ti, e))
        words = []
        for comp in nx.connected_components(B):
            H = B.subgraph(comp)
            if any(d != 2 for _, d in H.degree()):
                words.append(None)
                continue
            start = next(iter(comp))
            seq, prev_key, cur = [start], None, start
            while True:
                nxt = [(w, k) for _, w, k in H.edges(cur, keys=True) if (min(cur, w), max(cur, w), k) != prev_key]
                w, k = nxt[0]
                prev_key = (min(cur, w), max(cur, w), k)
                if w == start:
                    break
                seq.append(w)
                cur = w
            words.append([c[1] for c in seq])  # corner class -> vertex of G
        nb = B.number_of_edges() and nx.number_connected_components(B)
        kind = "disc" if (chi, nb) == (1, 1) else "annulus" if (chi, nb) == (0, 2) else f"chi={chi},b={nb}"
        out.append(dict(kind=kind, chi=chi, nb=nb, ntri=len(ts), nvert=len(V), words=words))
    out.sort(key=lambda c: -c["ntri"])
    return surface, out


def rotation(word, cyc_edges):
    """Signed number of turns of the cyclic boundary word around the cycle formed by cyc_edges."""
    C = nx.Graph(list(cyc_edges))
    if not (nx.is_connected(C) and all(d == 2 for _, d in C.degree())):
        return None
    cyc = [e[0] for e in nx.find_cycle(C)]
    succ = {cyc[i]: cyc[(i + 1) % len(cyc)] for i in range(len(cyc))}
    s = 0
    for u, v in zip(word, word[1:] + word[:1]):
        if tuple(sorted((u, v))) in cyc_edges:
            s += 1 if succ[u] == v else -1
    return s / len(cyc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default="paper/tables/stuck51.tex")
    ap.add_argument("--figure", default=None)
    a = ap.parse_args()
    rows = parse_table(a.table)
    g6_file = [l.split()[0] for l in open("data/stuck_14_K4free.g6") if l.strip() and not l.startswith("#")]
    tsv = {l.split("\t")[0]: l.rstrip("\n").split("\t") for l in open("data/stuck_14_K4free.tsv") if not l.startswith("#")}
    st = {r["g6"]: r for r in csv.DictReader(open("data/structure_84_graphs.csv", encoding="utf-8"))}
    print(f"table {a.table}: {len(rows)} rows; data/stuck_14_K4free.g6: {len(g6_file)} lines; TSV: {len(tsv)} rows")

    # T1
    check(len(rows) == 51 and sorted(r["idx"] for r in rows) == list(range(1, 52)), "T1", "row numbers are not 1..51")
    check(sorted(r["g6"] for r in rows) == sorted(g6_file) == sorted(tsv), "T1", "table strings differ from data files")
    Gs = {r["g6"]: g6_decode(r["g6"]) for r in rows}
    byhash = collections.defaultdict(list)
    for s, G in Gs.items():
        byhash[nx.weisfeiler_lehman_graph_hash(G, iterations=4)].append(s)
    iso_pairs = [(x, y) for grp in byhash.values() for x, y in itertools.combinations(grp, 2) if nx.is_isomorphic(Gs[x], Gs[y])]
    check(not iso_pairs, "T1", f"isomorphic pairs {iso_pairs}")

    mult4, minmult, disc_stats = [], 99, collections.Counter()
    kinds = {}
    for r in rows:
        s, G, tr, sr = r["g6"], Gs[r["g6"]], tsv[r["g6"]], st.get(r["g6"], {})
        tag = f"row {r['idx']} {s}"
        T = triangles(G)
        # T2
        check(r["m"] == int(tr[1]) == G.number_of_edges(), "T2", f"{tag}: edges {r['m']} / {tr[1]} / {G.number_of_edges()}")
        check(r["t"] == int(tr[2]) == len(T), "T2", f"{tag}: triangles {r['t']} / {tr[2]} / {len(T)}")
        # T3
        adj = [set(G[v]) for v in range(G.number_of_nodes())]
        _, res = ch.homology(G.number_of_nodes(), adj)
        free1, tors1 = res[1]
        H1 = "0" if (free1 == 0 and not tors1) else "+".join(["Z"] * free1 + [f"Z/{x}" for x in tors1])
        others_zero = all(f == 0 and not to for k, (f, to) in res.items() if k != 1)
        tsvH1 = {"trivial": "0"}.get(tr[3], tr[3])
        check(r["H1"] == tsvH1 == H1 and others_zero, "T3", f"{tag}: H1 {r['H1']} / {tr[3]} / {H1}, others zero {others_zero}")
        # T4
        aut = sum(1 for _ in GraphMatcher(G, G).isomorphisms_iter())
        check(r["aut"] == int(tr[5]) == aut, "T4", f"{tag}: |Aut| {r['aut']} / {tr[5]} / {aut}")
        # T5
        mI = re.fullmatch(r"\(\$\\\{(\d+),(\d+)\\\}\$\)", r["I4"].strip())
        if H1 == "0":
            ok = bool(mI) and not G.has_edge(int(mI.group(1)), int(mI.group(2))) and \
                tr[4] == f"yes ({{{mI.group(1)},{mI.group(2)}}})"
            check(ok, "T5", f"{tag}: I4 cell {r['I4']!r}, TSV {tr[4]!r}")
        else:
            check(r["I4"].strip() == "no" and tr[4] == "no", "T5", f"{tag}: I4 cell {r['I4']!r}, TSV {tr[4]!r}")
        # T6
        mult = {tuple(sorted(e)): len(set(G[e[0]]) & set(G[e[1]])) for e in G.edges()}
        minmult = min(minmult, min(mult.values()))
        if max(mult.values()) >= 4:
            mult4.append((r["idx"], sorted(e for e, k in mult.items() if k >= 4)))
        surface, parts = unfold(G)
        kind = "+".join(p["kind"] for p in parts)
        kinds[r["idx"]] = kind
        check(surface, "T6", f"{tag}: unfolding is not a surface")
        check(kind == r["kind"], "T6", f"{tag}: unfolding {kind}, table says {r['kind']!r}")
        if kind == "disc":
            p = parts[0]
            word = p["words"][0]
            e3 = {e for e, k in mult.items() if k == 3}
            rot = rotation(word, e3)
            spur = any(k >= 4 for k in mult.values())
            check(rot is not None, "T6", f"{tag}: edges in three triangles do not form one cycle")
            check(r["k"] == len(e3) == int(sr.get("k_ciclo") or -1), "T6", f"{tag}: k {r['k']} / {len(e3)} / {sr.get('k_ciclo')}")
            want = {"a^3": 3, "a a a^-1": 1}[r["pattern"]]
            check(rot is not None and abs(rot) == want == abs(int(sr.get("numero_rotacion") or 0)), "T6",
                  f"{tag}: |rotation| {rot} vs pattern {r['pattern']} / CSV {sr.get('numero_rotacion')}")
            check(r["spur"] == spur == bool(sr.get("espolones", "").strip()), "T6", f"{tag}: spur {r['spur']} / {spur} / {sr.get('espolones')!r}")
            check(p["nvert"] == int(tr[6]) == int(sr["vertices_disco"]) and len(word) == int(tr[7]) == int(sr["lados_borde"]),
                  "T6", f"{tag}: disc vertices {p['nvert']} / {tr[6]} / {sr['vertices_disco']}, boundary {len(word)} / {tr[7]} / {sr['lados_borde']}")
            disc_stats[(H1, len(e3), r["pattern"])] += 1
        # T7
        if kind == "annulus+disc":
            cut = nx.Graph([e for e, k in mult.items() if k == 3])
            comps = [cut.subgraph(c) for c in nx.connected_components(cut)]
            ok = r["m"] == 47 and len(comps) == 2 and all(c.number_of_nodes() == 4 and c.number_of_edges() == 4 and
                                                          all(d == 2 for _, d in c.degree()) for c in comps) and \
                all(k in (2, 3) for k in mult.values())
            check(ok, "T7", f"{tag}: edges in three triangles do not form two disjoint 4-cycles")
    # T8
    check(minmult >= 2, "T8", f"some edge lies in fewer than two triangles (min {minmult})")
    # T9
    tors = [r for r in rows if r["H1"] == "Z/3"]
    by_m = collections.Counter(r["m"] for r in tors)
    check(dict(by_m) == {43: 25, 44: 18, 45: 4, 47: 1}, "T9", f"torsion graphs by edges {dict(by_m)}")
    disc_k = collections.Counter()
    for (h, k, pat), c in disc_stats.items():
        if h == "Z/3":
            disc_k[k] += c
    check(dict(disc_k) == {4: 25, 5: 18, 6: 2}, "T9", f"torsion discs by cycle length {dict(disc_k)}")
    check(all(pat == "a^3" for (h, k, pat) in disc_stats if h == "Z/3"), "T9", "a torsion disc without pattern a^3")
    check(all(pat == "a a a^-1" for (h, k, pat) in disc_stats if h == "0"), "T9", "a contractible disc without pattern a a a^-1")
    check(sum(c for (h, k, pat), c in disc_stats.items() if h == "0") == 3, "T9", "not exactly three contractible discs")
    kc = collections.Counter(kinds.values())
    check(kc == {"disc": 48, "annulus": 2, "annulus+disc": 1}, "T9", f"unfoldings {dict(kc)}")
    order_ok = [r["H1"] for r in rows[:3]] == ["0"] * 3 and all(rows[i]["m"] <= rows[i + 1]["m"] for i in range(3, 50))
    check(order_ok, "T9", "table order is not: contractible first, then torsion by number of edges")
    print("unfoldings:", dict(kc), "| torsion by edges:", dict(sorted(by_m.items())), "| torsion discs by k:", dict(sorted(disc_k.items())))
    print("graphs with an edge in four triangles (row, edges):", mult4, "| minimum edge multiplicity:", minmult)
    print("non-disc rows:", {i: k for i, k in kinds.items() if k != "disc"})

    # F1
    if a.figure:
        raw = subprocess.run(["pdftotext", "-raw", a.figure, "-"], capture_output=True, text=True, check=True).stdout
        for r in rows:
            n_occ = raw.count(r["g6"])
            if not check(n_occ == 1, "F1", f"row {r['idx']}: graph6 string found {n_occ} times in the figure text"):
                continue
            after = raw[raw.find(r["g6"]) + len(r["g6"]):].lstrip("\n").split("\n")[0]
            mm = re.match(r"(\d+) edges · H₁ = (0|ℤ/3)\s*(\**)\s*$", after)
            if not check(bool(mm), "F1", f"row {r['idx']}: caption {after!r} not understood"):
                continue
            want_mark = {"annulus": "*", "annulus+disc": "**"}.get(kinds[r["idx"]], "")
            check(int(mm.group(1)) == r["m"] and {"0": "0", "ℤ/3": "Z/3"}[mm.group(2)] == r["H1"] and mm.group(3) == want_mark,
                  "F1", f"row {r['idx']}: caption {after!r}, expected {r['m']} edges, H1 {r['H1']}, mark {want_mark!r}")
        bbox = subprocess.run(["pdftotext", "-bbox", a.figure, "-"], capture_output=True, text=True, check=True).stdout
        W, Hh = [float(x) for x in re.search(r'<page width="([\d.]+)" height="([\d.]+)"', bbox).groups()]
        words = [(float(p), float(q), float(r_), float(s), w) for p, q, r_, s, w in
                 re.findall(r'<word xMin="([\d.-]+)" yMin="([\d.-]+)" xMax="([\d.-]+)" yMax="([\d.-]+)">(.*?)</word>', bbox)]
        outside = [w for w in words if w[0] < 0 or w[1] < 0 or w[2] > W or w[3] > Hh]
        check(not outside, "F1", f"words outside the page box: {outside[:5]}")
        legend = [l for l in raw.split("\n") if l.startswith(("Red:", "* ", "G14"))]
        print(f"figure {a.figure}: page {W:.1f} x {Hh:.1f} pt, {len(words)} words, max xMax {max(w[2] for w in words):.1f}, "
              f"min xMin {min(w[0] for w in words):.1f}; legend lines: {legend}")

    print("RESULT:", "PASS (all checks)" if not FAILS else f"FAIL ({len(FAILS)})")
    for f in FAILS:
        print("  ", f)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
