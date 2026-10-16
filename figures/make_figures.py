#!/usr/bin/env python
"""make_figures.py — generates fig01..fig09 (+ fig06b, fig06c) of the manuscript
"Small non-strong I-contractible graphs and odd torsion in flag complexes" (PDF, SVG, PNG 300 dpi).

Usage:  python make_figures.py [--data DIR] [--out DIR] [--only fig07 ...]
  --only regenerates just the named figures (fig07 needs only atascadas14_final.txt).
  DIR (default ./proy) must contain atascadas14_final.txt, traza_G14_mas01.txt,
  traza_G14b_mas03.txt, traza_cand14c.txt.  Everything else is recomputed from the g6 strings.
Environment: python>=3.10, networkx, numpy, matplotlib (no scipy needed). Deterministic (no RNG).

Vertex labels are the g6 labels 0..n-1, except the dunce hat, drawn with the labels 1..15 of
DEFH23 Fig. 2A (mapping DUNCE_ORDER below).  Figure-style rules (figure-style skill) are applied via
apply_figure_style(); every figure passes the geometric render-then-verify check (bbox_check).
"""
import os, sys, re, math, argparse, collections, itertools
import numpy as np, networkx as nx
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Circle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from discos import *
from dibujo import *

# ------------------------------------------------------------------ style (figure-style skill)
def apply_figure_style(*, frame='none', sizes=(8, 7, 6)):
    base, secondary, tick = sizes
    mpl.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans'], 'font.size': base,
        'axes.labelsize': base, 'axes.titlesize': base, 'legend.fontsize': secondary,
        'xtick.labelsize': tick, 'ytick.labelsize': tick, 'axes.linewidth': 0.6,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.spines.left': frame != 'none', 'axes.spines.bottom': frame != 'none',
        'axes.grid': False, 'legend.frameon': False, 'figure.dpi': 200, 'savefig.dpi': 300,
        'savefig.bbox': 'tight', 'axes.titleweight': 'normal', 'axes.titlelocation': 'left',
        'lines.linewidth': 1.2, 'patch.linewidth': 0.6, 'pdf.fonttype': 42, 'ps.fonttype': 42,
        'svg.fonttype': 'none', 'figure.facecolor': 'white', 'savefig.facecolor': 'white'})

def panel_letter(ax, letter, dx=0.0, dy=1.0):
    ax.text(dx, dy, letter, transform=ax.transAxes, fontweight='bold', fontsize=plt.rcParams['font.size']+1, va='bottom', ha='left')

# ------------------------------------------------------------------ data
G13_G6 = 'L?qa``{wttym~o'
DUNCE_G6 = 'N|thHsL`sHoI`RPOwLG'
DUNCE_ORDER = [1, 4, 13, 12, 11, 3, 14, 15, 10, 5, 2, 6, 7, 8, 9]   # g6 index i  <->  DEFH23 Fig. 2A label DUNCE_ORDER[i]
G14 = {'G14a': ('M?b@bFHNEk@~|k}U?', (0, 1), 5),
       'G14b': ('M?B@thku?~Lylk}[?', (0, 3), 4),
       'G14c': ('M?r@d`ifbiFfo}~o?', (2, 3), 6)}        # g6, glued I4 edge, length of identification cycle
REC_WORD = {'G14a': '5 10 13 9 12 5 10 13 9 12 9 13 10 5 12',
            'G14b': '7 5 8 13 7 5 8 13 9 13 8 5 7 13 9 13',
            'G14c': '0 9 11 10 7 13 7 10 11 9 0 13 7 10 11 9 0 13'}   # boundary words as recorded in atascadas14_final.txt
LAYOUT = {}
LOG = []

def log(*a):
    s = ' '.join(str(x) for x in a); print(s); LOG.append(s)

def check(fig, stem):
    bad, out = bbox_check(fig)
    log(f'{stem}: text overlaps = {len(bad)}; texts outside figure box = {len(out)}' + (f'  {bad}' if bad else ''))
    return bad

# ------------------------------------------------------------------ fig01
def moore_schematic(ax, cyc4=((8, 10), (10, 9), (9, 11), (11, 8)), sq=None, label='a = 8–10–9–11', homology='M(ℤ/3, 1):  H₁ = ℤ/3,  H₂ = 0'):
    ax.add_patch(Circle((-0.9, 0), 0.62, fc=FILL, ec='none'))
    for j in range(3):
        a0 = np.pi/2 - 2*np.pi*j/3; a1 = a0 - 2*np.pi/3
        t = np.linspace(a0-0.06, a1+0.06, 50)
        ax.plot(-0.9+0.62*np.cos(t), 0.62*np.sin(t), color=RED, lw=1.8)
        p0 = (-0.9+0.62*np.cos(t[-4]), 0.62*np.sin(t[-4])); p1 = (-0.9+0.62*np.cos(t[-1]), 0.62*np.sin(t[-1]))
        ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='-|>,head_length=0.4,head_width=0.2', color=RED, lw=1.5, shrinkA=0, shrinkB=0))
        am = (a0+a1)/2
        ax.text(-0.9+0.78*np.cos(am), 0.78*np.sin(am), 'a', ha='center', va='center', fontsize=8, color=RED, fontstyle='italic')
    ax.text(-0.9, 0, 'D²', ha='center', va='center', fontsize=8)
    ax.annotate('', xy=(0.35, 0), xytext=(-0.12, 0), arrowprops=dict(arrowstyle='-|>', color='black', lw=0.9))
    ax.text(0.12, 0.1, '∂D² ↦ a³', ha='center', va='bottom', fontsize=7)
    sq = sq or {8: (0.95, 0.45), 10: (0.5, 0), 9: (0.95, -0.45), 11: (1.4, 0)}
    for u, v in cyc4: ax.plot([sq[u][0], sq[v][0]], [sq[u][1], sq[v][1]], color=RED, lw=1.8)
    for v, p in sq.items(): node(ax, p, v, r=0.1, fc='white', ec=RED, tc=RED, fs=6, lw=1.2, bold=True)
    ax.text(0.95, -0.72, label, ha='center', va='top', fontsize=7, color=RED, fontstyle='italic')
    ax.text(0.25, -1.1, homology, ha='center', va='center', fontsize=7)
    ax.set_xlim(-1.65, 1.65); ax.set_ylim(-1.3, 1.0); ax.set_aspect('equal'); ax.axis('off')

def fig01():
    """Hook first (reviewer round 1): (a) the triple-wrapped disc, (b) its meaning (Moore space), (c) the graph."""
    G = g6(G13_G6); U = unfold(G)
    assert (G.number_of_nodes(), G.number_of_edges(), len(U['tris'])) == (13, 40, 28)
    word, cyc = align_word(boundary_word(U, U['cycles'][0]), U['cycles'][0], [10, 9, 11, 8]*3)
    segs = [(0, 4, 'a'), (4, 8, 'a'), (8, 12, 'a')]
    fig = plt.figure(figsize=(6.85, 2.75))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.1, 0.95, 0.95], wspace=0.06, left=0.01, right=0.99, top=0.9, bottom=0.03)
    axa, axb, axc = [fig.add_subplot(gs[0, i]) for i in range(3)]
    draw_disk(axa, U, cyc, word, segs)
    title(axa, 'Δ(G₁₃): disc, boundary wraps 3× around a')
    axa.text(0, -1.45, 'boundary word  ' + word_string(word, segs), ha='center', va='center', fontsize=7, color=RED)
    axa.set_ylim(-1.55, 1.32)
    moore_schematic(axb); axb.set_ylim(-2.15, 1.85); title(axb, 'Moore space M(ℤ/3, 1)')
    sc, pos = best_concentric(G, center=12, r2=2.0); LAYOUT['G13'] = pos
    cyc4 = [(8, 10), (10, 9), (9, 11), (11, 8)]
    draw_graph(axc, G, pos, red_edges=cyc4, red_nodes=(8, 9, 10, 11), node_r=0.13, fs=6)
    title(axc, 'G₁₃: 13 vertices, 40 edges')
    axc.text(0, -2.45, 'red: 4-cycle a = 8–10–9–11 (edges in 3 triangles)', ha='center', va='center', fontsize=7, color=RED)
    axc.set_ylim(-2.65, 2.3)
    for a_, l in zip((axa, axb, axc), 'abc'): panel_letter(a_, l)
    return fig

# ------------------------------------------------------------------ fig02
def swapped_G13():
    """G13 with 10<->11 swapped on the middle boundary turn. Returns (U with new labels, cycle, word, lab)."""
    G = g6(G13_G6); U = unfold(G)
    w0, c0 = align_word(boundary_word(U, U['cycles'][0]), U['cycles'][0], [10, 9, 11, 8]*3)
    lab = dict(U['label'])
    for i in range(4):
        dv = c0[4+i]; lab[dv] = {10: 11, 11: 10}.get(lab[dv], lab[dv])
    Us = dict(U); Us['label'] = lab
    cyc = c0[4:]+c0[:4]; word = [lab[v] for v in cyc]
    assert word == [11, 9, 10, 8, 10, 9, 11, 8, 10, 9, 11, 8], word
    H = nx.Graph(); H.add_nodes_from(range(13))
    for dt in U['dtris']: H.add_edges_from(itertools.combinations([lab[x] for x in dt], 2))
    disk_tris = {tuple(sorted(lab[x] for x in dt)) for dt in U['dtris']}
    false = [t for t in triangles(H) if t not in disk_tris]
    Hs = nx.Graph(); Hs.add_nodes_from(sorted(H.nodes())); Hs.add_edges_from(H.edges())
    return Us, cyc, word, lab, H, false, nx.to_graph6_bytes(Hs, header=False).decode().strip()

def fig02():
    GD = g6(DUNCE_G6); UD = unfold(GD); mp = lambda i: DUNCE_ORDER[i]
    assert (GD.number_of_nodes(), GD.number_of_edges(), len(UD['tris'])) == (15, 46, 32)
    word, cyc = align_word(boundary_word(UD, UD['cycles'][0]), UD['cycles'][0], [0, 1, 5, 10, 0, 1, 5, 10, 0, 10, 5, 1])
    word, cyc = word[::-1], cyc[::-1]; wl = [mp(x) for x in word]
    r = next(r for r in range(12) if wl[r:]+wl[:r] == [1, 2, 3, 4, 1, 2, 3, 4, 1, 4, 3, 2])
    word, cyc = word[r:]+word[:r], cyc[r:]+cyc[:r]
    segs = [(0, 4, 'a'), (4, 8, 'a'), (8, 12, 'a⁻¹')]
    fig = plt.figure(figsize=(6.85, 2.95))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.78], wspace=0.08, left=0.01, right=0.99, top=0.9, bottom=0.02)
    axa, axb, axc = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2])
    draw_disk(axa, UD, cyc, word, segs, label_map=mp, node_r=0.062)
    title(axa, 'Dunce hat, 15 vertices (DEFH23 Fig. 2A)')
    axa.text(0, -1.42, 'boundary word  ' + word_string(word, segs, label_map=mp), ha='center', va='center', fontsize=7, color=RED)
    Us, cyc2, word2, lab, H, false, g6s = swapped_G13()
    log('fig02b swapped graph g6 =', g6s, '; edges =', H.number_of_edges(), '; false triangles =', false,
        '; K4 =', [q for q in nx.enumerate_all_cliques(H) if len(q) == 4])
    assert false == [(1, 4, 11), (2, 5, 10)]
    segs2 = [(0, 4, 'a⁻¹'), (4, 8, 'a'), (8, 12, 'a')]
    l2d = collections.defaultdict(list)
    for dv, l in lab.items(): l2d[l].append(dv)
    D = Us['D']; ns = {}; extra = []
    for a, b, cc in false:
        da, db = l2d[a][0], l2d[b][0]
        extra.append((da, db, PURPLE, 1.8)); ns[da] = ('#e6d5f0', PURPLE, 'black'); ns[db] = ('#e6d5f0', PURPLE, 'black')
        for dx_ in (da, db):
            for c_ in l2d[cc]:
                if D.has_edge(dx_, c_): extra.append((dx_, c_, PURPLE, 1.8)); ns[c_] = ('#e6d5f0', PURPLE, PURPLE)
    draw_disk(axb, Us, cyc2, word2, segs2, node_r=0.062, node_style=ns, extra_edges=extra)
    title(axb, 'G₁₃, 10↔11 swapped on one turn: not flag')
    axb.text(0, -1.42, 'boundary word  ' + word_string(word2, segs2), ha='center', va='center', fontsize=7, color=RED)
    axb.text(0, -1.58, 'cliques 1–4–11 and 2–5–10 are not faces of the disc', ha='center', va='center', fontsize=7, color=PURPLE)
    axb.set_ylim(-1.7, 1.32); axa.set_ylim(-1.7, 1.32)
    pattern_panel(axc)
    for a_, l in zip((axa, axb, axc), 'abc'): panel_letter(a_, l)
    return fig

def pattern_panel(ax):
    """(c) the two identification patterns side by side: a^3 (torsion) vs a.a.a^-1 (dunce hat, contractible)."""
    def polygon(cx, cy, dirs, name, verdict, col):
        ax.add_patch(Circle((cx, cy), 0.55, fc=FILL, ec='none'))
        for j, d in enumerate(dirs):
            a0 = np.pi/2 - 2*np.pi*j/3; a1 = a0 - 2*np.pi/3
            t = np.linspace(a0-0.07, a1+0.07, 50)
            ax.plot(cx+0.55*np.cos(t), cy+0.55*np.sin(t), color=RED, lw=1.6)
            if d > 0: p0 = (cx+0.55*np.cos(t[-4]), cy+0.55*np.sin(t[-4])); p1 = (cx+0.55*np.cos(t[-1]), cy+0.55*np.sin(t[-1]))
            else: p0 = (cx+0.55*np.cos(t[3]), cy+0.55*np.sin(t[3])); p1 = (cx+0.55*np.cos(t[0]), cy+0.55*np.sin(t[0]))
            ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='-|>,head_length=0.35,head_width=0.18', color=RED, lw=1.4, shrinkA=0, shrinkB=0))
            am = (a0+a1)/2
            ax.text(cx+0.72*np.cos(am), cy+0.72*np.sin(am), 'a' if d > 0 else 'a⁻¹', ha='center', va='center', fontsize=7, color=RED, fontstyle='italic')
        ax.text(cx, cy+0.08, name, ha='center', va='center', fontsize=7)
        ax.text(cx, cy-0.12, verdict, ha='center', va='center', fontsize=7, color=col)
    polygon(0, 1.3, (1, 1, 1), 'a·a·a', 'H₁ = ℤ/3', PURPLE)
    ax.text(0, 0.22, 'G₁₃ and 45 of the 48 torsion\nstuck graphs on 14 vertices', ha='center', va='center', fontsize=7)
    polygon(0, -1.0, (1, 1, -1), 'a·a·a⁻¹', 'contractible', GREEN)
    ax.text(0, -2.08, 'dunce hat (15 vertices),\nG14a, G14b, G14c', ha='center', va='center', fontsize=7)
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-2.35, 2.1); ax.set_aspect('equal'); ax.axis('off')
    title(ax, 'Two patterns')

# ------------------------------------------------------------------ fig03-05
def g14_layout(name):
    if name not in LAYOUT:
        s, e, k = G14[name]; G = g6(s)
        r, word, segs = segment_pattern([int(x) for x in REC_WORD[name].split()], k)
        LAYOUT[name] = best_ring(G, word[:k])[1]
    return LAYOUT[name]

def fig_G14(name):
    s, e, k = G14[name]; G = g6(s); U = unfold(G)
    word0 = [int(x) for x in REC_WORD[name].split()]
    w_al, c_al = align_word(boundary_word(U, U['cycles'][0]), U['cycles'][0], word0)
    r, word, segs = segment_pattern(word0, k); cyc = c_al[r:]+c_al[:r]
    assert [U['label'][v] for v in cyc] == word
    ntri = len(U['tris']); nb = len(cyc)
    fig = plt.figure(figsize=(6.85, 3.3))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1.0], wspace=0.05, left=0.01, right=0.99, top=0.92, bottom=0.02)
    axa, axb = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    draw_disk(axa, U, cyc, word, segs, node_r=0.06)
    cyc_lbl = '–'.join(str(x) for x in word[:k])
    title(axa, f'Unfolded disc: {ntri} triangles, {nb}-gon boundary')
    axa.text(0, -1.42, 'boundary word  ' + word_string(word, segs), ha='center', va='center', fontsize=7, color=RED)
    spur = [sg for sg in segs if sg[2] == 'spur']
    extra = f'; spur {word[spur[0][0]]}–{word[spur[0][0]+1]} twice' if spur else ''
    axa.text(0, -1.58, f'a = {k}-cycle {cyc_lbl}; word a·a·a⁻¹ (dunce-hat pattern){extra}', ha='center', va='center', fontsize=7, color=RED)
    axa.set_ylim(-1.7, 1.32)
    pos = g14_layout(name)
    N = sorted(set(G[e[0]]) & set(G[e[1]])); H = G.subgraph(N)
    mult = edge_tri_multiplicity(G)
    cut_edges = [tuple(ed) for ed, c_ in mult.items() if c_ != 2]
    cyc_edges = [(word[i], word[(i+1) % k]) for i in range(k)]
    assert {frozenset(x) for x in cyc_edges} <= {frozenset(x) for x in cut_edges}
    others = [ed for ed in cut_edges if frozenset(ed) not in {frozenset(x) for x in cyc_edges}]
    Gp = G.copy(); Gp.add_edge(*e)
    draw_graph(axb, Gp, pos, node_r=0.13, red_edges=cut_edges, red_nodes=set(word[:k]), dashed_edges=[e],
               amber_nodes=N, amber_edges=list(H.edges()), blue_nodes=e)
    ends = [v for v in N if H.degree(v) == 1]; path = nx.shortest_path(H, ends[0], ends[1])
    assert len(path) == len(N) and H.number_of_edges() == len(N)-1, 'N(u,v) is not an induced path'
    title(axb, f'{name}: {G.number_of_nodes()} vertices, {G.number_of_edges()} edges')
    axb.text(0, -2.45, f'glued edge {{{e[0]},{e[1]}}} (dashed);  N({e[0]},{e[1]}) = path {"–".join(map(str, path))}', ha='center', va='center', fontsize=7)
    if others:
        o = others[0]; txt = f'red: cycle a (edges in 3 triangles) and {min(o)}–{max(o)} (in {mult[frozenset(o)]} triangles)'
    else:
        txt = 'red: identification cycle a (edges in 3 triangles)'
    axb.text(0, -2.62, txt, ha='center', va='center', fontsize=7, color=RED)
    axb.set_ylim(-2.75, 2.3)
    for a_, l in zip((axa, axb), 'ab'): panel_letter(a_, l)
    log(f'{name}: word={word}; segments={segs}; N{e}={path}; edges in !=2 triangles={sorted(tuple(sorted(x)) for x in cut_edges)}; multiplicities={ {tuple(sorted(x)): mult[frozenset(x)] for x in cut_edges} }')
    return fig

# ------------------------------------------------------------------ fig06
def parse_trace(path):
    steps = []; g6s = None
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        m0 = re.match(r'== traza I_S de (\S+)', line)
        if m0: g6s = m0.group(1); continue
        m = re.match(r'(\d+)\. borrar (arista|vertice) \{?([\d,]+)\}?: N\(([\d,]+)\) = \{([\d,]*)\}\s+\[(.*)\]', line)
        if m:
            kind = 'edge' if m.group(2) == 'arista' else 'vertex'
            elem = tuple(int(x) for x in m.group(3).split(','))
            N = [int(x) for x in m.group(5).split(',')] if m.group(5) else []
            steps.append((int(m.group(1)), kind, elem, N, m.group(6)))
    return g6s, steps

def fig_cert(trace_path, base_name, glued, ncols=4):
    g6s, steps = parse_trace(trace_path)
    G = g6(g6s); G0 = g6(G14[base_name][0])
    assert set(map(frozenset, G.edges())) == set(map(frozenset, G0.edges())) | {frozenset(glued)}, 'trace graph != base + glued edge'
    pos = g14_layout(base_name)
    npan = len(steps)+2; nrows = math.ceil(npan/ncols)
    fig, axs = plt.subplots(nrows, ncols, figsize=(6.85, 1.75*nrows)); axs = axs.ravel()
    H = G.copy(); ax = axs[0]
    draw_graph(ax, H, pos, node_r=0.2, fs=6, dashed_edges=[glued], blue_nodes=glued)
    ax.set_title(f'start: {base_name}+{{{glued[0]},{glued[1]}}}\n{H.number_of_nodes()} vertices, {H.number_of_edges()} edges', loc='left', fontsize=7, pad=2)
    for i, (k, kind, elem, N, why) in enumerate(steps, start=1):
        ax = axs[i]
        if kind == 'edge':
            u, v = elem; assert H.has_edge(u, v), (k, elem)
            assert sorted(set(H[u]) & set(H[v])) == sorted(N), (k, N)
            draw_graph(ax, H, pos, node_r=0.2, fs=6, red_edges=[elem], amber_nodes=N, amber_edges=list(H.subgraph(N).edges()), red_nodes=elem)
            ttl = f'step {k}: delete edge {{{u},{v}}}\nN({u},{v}) = {{{",".join(map(str, N))}}}'
            H.remove_edge(u, v)
        else:
            (v,) = elem; assert v in H and sorted(H[v]) == sorted(N), (k, N)
            draw_graph(ax, H, pos, node_r=0.2, fs=6, red_nodes=[v], amber_nodes=N, amber_edges=list(H.subgraph(N).edges()),
                       red_edges=[(v, w) for w in H[v]], bold_cycle_lw=1.2)
            ttl = f'step {k}: delete vertex {v}\nN({v}) = {{{",".join(map(str, N))}}}'
            H.remove_node(v)
        ax.set_title(ttl, loc='left', fontsize=7, pad=2)
    assert H.number_of_nodes() == 1 and H.number_of_edges() == 0, (H.nodes(), H.edges())
    ax = axs[len(steps)+1]; draw_graph(ax, H, pos, node_r=0.2, fs=6)
    ax.set_title(f'end: K₁ = {{{list(H.nodes())[0]}}}', loc='left', fontsize=7, pad=2)
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    for a_ in axs:
        a_.set_xlim(min(xs)-0.45, max(xs)+0.45); a_.set_ylim(min(ys)-0.45, max(ys)+0.45); a_.set_aspect('equal'); a_.axis('off')
    for a_ in axs[npan:]: a_.set_visible(False)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.94, bottom=0.01, wspace=0.08, hspace=0.3)
    fig.text(0.01, 0.995, f'Both {base_name} and {base_name}+{{{glued[0]},{glued[1]}}} = {g6s} are contractible (H₁ = H₂ = 0); only strong I-contractibility changes:\n'
             f'{base_name} is stuck (no I_S move), {base_name}+{{{glued[0]},{glued[1]}}} reduces to K₁ in {len(steps)} I_S moves.', ha='left', va='top', fontsize=7)
    log(f'certificate {base_name}+{glued}: {len(steps)} steps replayed, ends in K1 = {list(H.nodes())}')
    return fig

# ------------------------------------------------------------------ fig07
def load_atascadas14(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or not line.strip(): continue
        parts = [p.strip() for p in line.rstrip('\n').split(' | ')]
        g6s, m, t, h1, icon, aut, nd, nb, word = parts[:9]
        flag = 'frontera no conexa' in word
        wl = [int(x) for x in re.sub(r'\[.*\]', '', word).split()]
        rows.append(dict(g6=g6s, edges=int(m), tris=int(t), H1=h1, contractible=icon.startswith('SÍ'), aut=int(aut), word=wl, nondisc=flag))
    return rows

def fig07(rows, ncols=6):
    assert len(rows) == 51 and len({r['g6'] for r in rows}) == 51
    for r_ in rows:
        G = g6(r_['g6']); assert G.number_of_edges() == r_['edges'] and len(triangles(G)) == r_['tris']
        assert not [q for q in nx.enumerate_all_cliques(G) if len(q) == 4], 'K4 found'
        mult = edge_tri_multiplicity(G); r_['cut'] = [tuple(e) for e, c_ in mult.items() if c_ != 2]
        if r_['contractible']:
            name = {v[0]: k for k, v in G14.items()}[r_['g6']]; r_['pos'] = g14_layout(name); r_['k'] = G14[name][2]
        elif r_['nondisc']:
            C = nx.Graph(r_['cut']); cyc = nx.cycle_basis(C)[0]; r_['k'] = ('nd', len(cyc), C.number_of_edges())
            r_['pos'] = best_ring(G, cyc, fine=False, node_r=0.1)[1]
        else:
            k = period(r_['word']); outer = r_['word'][:k]; r_['k'] = k
            assert all(G.has_edge(outer[i], outer[(i+1) % k]) for i in range(k))
            r_['pos'] = best_ring(G, outer, fine=False, node_r=0.1)[1]
    contr = [r for r in rows if r['contractible']]; tors = sorted([r for r in rows if not r['contractible']], key=lambda r: (r['edges'], r['g6']))
    assert len(contr) == 3 and all(r['H1'] == 'trivial' for r in contr) and all(r['H1'] == 'Z/3' for r in tors)
    order = contr + tors; nrows = 1 + math.ceil(len(tors)/ncols)
    fig, axs = plt.subplots(nrows, ncols, figsize=(6.85, 1.08*nrows+0.3))
    cells = [(0, j) for j in range(3)] + [(1+i//ncols, i % ncols) for i in range(len(tors))]
    for ax in axs.ravel(): ax.axis('off')
    for r_, (i, j) in zip(order, cells):
        ax = axs[i, j]; G = g6(r_['g6'])
        draw_graph(ax, G, r_['pos'], node_r=0.11, label=False, red_edges=r_['cut'], lw=0.4, bold_cycle_lw=1.1,
                   node_colors={v: ('white', NODE_EC, 'black') for v in G})
        h1 = 'H₁ = 0' if r_['H1'] == 'trivial' else 'H₁ = ℤ/3'
        extra = ''
        if r_['nondisc']: extra = ' *' if r_['k'][2] == 5 else ' **'
        if r_['contractible']:
            nm = {v[0]: k for k, v in G14.items()}[r_['g6']]
            extra = f"\n{nm}: a = {r_['k']}-cycle" + (' + spur' if nm == 'G14b' else '')
        ax.set_title(f"{r_['g6']}\n{r_['edges']} edges · {h1}{extra}", loc='left', fontsize=6, pad=1.5)
        ax.set_xlim(-2.4, 2.4); ax.set_ylim(-2.4, 2.4)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.955, bottom=0.01, wspace=0.08, hspace=0.42)
    fig.canvas.draw(); rr = fig.canvas.get_renderer()
    bbs = [axs[0, j].get_tightbbox(rr).transformed(fig.transFigure.inverted()) for j in range(3)]
    x0 = min(b.x0 for b in bbs)-0.005; x1 = max(b.x1 for b in bbs)+0.005; y0 = min(b.y0 for b in bbs)-0.006; y1 = max(b.y1 for b in bbs)+0.006
    fig.patches.append(FancyBboxPatch((x0, y0), x1-x0, y1-y0, boxstyle='round,pad=0.002', transform=fig.transFigure, fc='none', ec=GREEN, lw=1.2))
    fig.text(x1+0.03, (y0+y1)/2,
             'Green box: the 3 contractible stuck graphs G14a, G14b, G14c\n(I-contractible, not strong I-contractible; word a·a·a⁻¹ on the cycle a).\n'
             'Below: the 48 stuck graphs with H₁(Δ; ℤ) = ℤ/3, by edge count.\n'
             'Red: edges in ≠ 2 triangles; for discs, the identification cycle a\n'
             '(in G14b with a spur). * Annulus: a 4-cycle and a disjoint edge\n'
             'in 4 triangles. ** Annulus and disc: two disjoint 4-cycles.\n'
             'All 51 are K₄-free, ℤ₂-acyclic, with no I_S-contractible vertex\n'
             'or edge; all such graphs under H14 (geng -k -C -d4 -D12 14).', ha='left', va='center', fontsize=7)
    log('fig07: 51 graphs; edges histogram', dict(collections.Counter(r['edges'] for r in rows)), '; cycle lengths',
        dict(collections.Counter(str(r['k']) for r in rows)))
    return fig

# ------------------------------------------------------------------ fig08
def fig08():
    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    ax.set_xlim(-2.3, 2.3); ax.set_ylim(-1.75, 1.25); ax.set_aspect('equal'); ax.axis('off')
    ax.add_patch(Ellipse((-1.05, 0), 2.3, 1.7, fc=FILL, ec=EDGE, lw=0.9))
    ax.add_patch(Ellipse((1.05, 0), 2.3, 1.7, fc='#f7f0e6', ec=EDGE, lw=0.9))
    ax.text(-1.85, 0.6, 'A', fontsize=8, fontstyle='italic'); ax.text(1.75, 0.6, 'B', fontsize=8, fontstyle='italic')
    node(ax, (0, 0), 'u', r=0.11, fc='white', ec=RED, tc=RED, fs=7, lw=1.2, bold=True, z=6)
    w = (-1.15, 0.1)
    nb = [(-1.75, 0.35), (-1.7, -0.3), (-1.2, -0.5), (-0.65, -0.35), (-0.6, 0.4)]
    for i, p in enumerate(nb):
        ax.plot([w[0], p[0]], [w[1], p[1]], color=AMBER_DK, lw=0.8, zorder=3)
        q = nb[(i+1) % len(nb)]; ax.plot([p[0], q[0]], [p[1], q[1]], color=AMBER, lw=2.2, zorder=2.5)
        node(ax, p, '', r=0.06, fc=AMBER, ec=AMBER_DK, fs=5, z=6)
    node(ax, w, 'w', r=0.11, fc='white', ec=AMBER_DK, tc='black', fs=7, z=6)
    ax.text(-1.05, -1.05, 'N(w) = N_A(w), not acyclic', ha='center', va='center', fontsize=7, color=AMBER_DK)
    pts = [(0.7, 0.3), (1.1, -0.3), (1.5, 0.25), (0.75, -0.35), (1.35, -0.05)]
    for a_, b_ in [((0.7, 0.3), (1.5, 0.25)), ((0.7, 0.3), (0, 0)), ((0.75, -0.35), (0, 0)), ((1.1, -0.3), (0.75, -0.35)),
                   ((1.35, -0.05), (1.5, 0.25)), ((1.1, -0.3), (1.35, -0.05)), ((0.7, 0.3), (1.35, -0.05))]:
        ax.plot([a_[0], b_[0]], [a_[1], b_[1]], color=EDGE, lw=0.7, zorder=2)
    for p in pts: node(ax, p, '', r=0.06, fc='white', ec=EDGE, fs=5)
    ax.text(0, 1.05, 'G = A ∪_u B stuck, u a cut vertex  ⇒  A and B almost stuck', ha='center', va='center', fontsize=7)
    ax.text(0, -1.38, 'no almost-stuck pieces on ≤ 11 vertices', ha='center', va='center', fontsize=7)
    ax.text(0, -1.6, '⇒ stuck graphs on ≤ 22 vertices are 2-connected', ha='center', va='center', fontsize=7)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig

# ------------------------------------------------------------------ fig09
def box(ax, xy, w, h, text, fc='white', ec='#333333', fs=7, lw=0.8, bold=False, color='black'):
    ax.add_patch(FancyBboxPatch((xy[0]-w/2, xy[1]-h/2), w, h, boxstyle='round,pad=0.02,rounding_size=0.08', fc=fc, ec=ec, lw=lw, zorder=2))
    ax.text(xy[0], xy[1], text, ha='center', va='center', fontsize=fs, zorder=3, fontweight='bold' if bold else 'normal', color=color)

def arrow(ax, p, q, color='#333333'):
    ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>,head_length=0.35,head_width=0.18', color=color, lw=0.9, shrinkA=0, shrinkB=0), zorder=3)

def fig09():
    fig, ax = plt.subplots(figsize=(6.85, 3.6))
    ax.set_xlim(0, 13.7); ax.set_ylim(0, 7.2); ax.set_aspect('equal'); ax.axis('off')
    # top row: pipeline
    y = 6.1
    box(ax, (1.45, y), 2.5, 1.0, 'geng -C -d4 -D(n−2) n\n(-k for K₄-free)\nres/mod slices', fc='#eef3fa')
    box(ax, (6.3, y), 6.4, 1.0, 'Algorithm 1 — filter cascade (one slice per CPU, xargs -P 64)', fc='#fff5e0')
    box(ax, (11.9, y), 3.0, 1.0, 'stuck graphs\n(no I_S-contractible\nvertex or edge)', fc='#e9f5ec', ec=GREEN)
    arrow(ax, (2.72, y), (3.08, y)); arrow(ax, (9.52, y), (10.38, y))
    # cascade sub-boxes
    yc = 4.75; names = ['N(v) not\na cone', 'χ(Δ) = 1', 'N(v) not\nℤ₂-acyclic', 'N(u,v) not\nℤ₂-acyclic', 'full ℤ₂\nhomology']
    xs = [3.75, 5.05, 6.35, 7.65, 8.95]
    for xx, nm in zip(xs, names): box(ax, (xx, yc), 1.1, 0.9, nm, fs=6, fc='#fffaf0')
    for a_, b_ in zip(xs[:-1], xs[1:]): arrow(ax, (a_+0.58, yc), (b_-0.58, yc))
    arrow(ax, (6.3, y-0.52), (6.3, yc+0.5))
    # survivors for n = 13 under the cascade
    ax.text(3.1, 3.9, 'n = 13 survivors:', ha='left', va='center', fontsize=6, color='#555555')
    for xx, s in zip(xs, ['3.34×10¹²', '4.80×10¹¹', '1.57×10¹⁰', '218,516', '1 stuck']):
        ax.text(xx, 3.55, s, ha='center', va='center', fontsize=6, color='#555555')
    ax.text(1.45, 3.55, '2.10×10¹³ graphs', ha='center', va='center', fontsize=6, color='#555555')
    # bottom row: post-processing
    yb = 2.3
    box(ax, (2.0, yb), 3.2, 0.95, 'closure by I₄ gluings\n(all ℤ₂-acyclic non-I_S graphs)', fc='#eef3fa')
    box(ax, (6.3, yb), 3.2, 0.95, 'integer homology\n(Smith normal form)', fc='#eef3fa')
    box(ax, (10.6, yb), 3.2, 0.95, 'certificates\n(I₄ gluing + I_S deletion trace)', fc='#eef3fa')
    arrow(ax, (3.62, yb), (4.68, yb)); arrow(ax, (7.92, yb), (8.98, yb))
    # link stuck -> closure (route along the right then down then left)
    ax.plot([11.9, 11.9], [y-0.52, 3.1], color='#333333', lw=0.9); ax.plot([11.9, 2.0], [3.1, 3.1], color='#333333', lw=0.9)
    arrow(ax, (2.0, 3.1), (2.0, yb+0.5))
    # table of runs
    ax.text(0.2, 1.35, 'YUCA (ACARUS, UNISON; SLURM, 64-core AMD EPYC nodes):', ha='left', va='center', fontsize=7)
    rows = [('n = 12', '1.64×10¹¹ graphs', '8 min', '448 CPU', 'row 12 of the table (ℤ₂-acyclic = I_S)'),
            ('n = 13', '2.10×10¹³ graphs', '7 h 10 min', '448 CPU', '200,000 slices → 1 stuck graph (H₁ = ℤ/3)'),
            ('n = 14, K₄-free', '6.49×10¹³ graphs', '≈ 33 h', '896 CPU, 2 accounts', '2,000,000 slices → 51 stuck graphs')]
    for i, row in enumerate(rows):
        yy = 0.9 - 0.38*i
        for xx, s in zip([0.2, 2.3, 4.6, 5.9, 8.4], row):
            ax.text(xx, yy, s, ha='left', va='center', fontsize=7)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig

# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data', default='proy'); ap.add_argument('--out', default='figures')
    ap.add_argument('--only', nargs='*', default=None, help='regenerate only these figures, e.g. --only fig07')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    apply_figure_style()
    want = (lambda stem: True) if not a.only else (lambda stem: stem in a.only)
    def emit(make, stem):
        if want(stem):
            fig = make(); check(fig, stem); save_all(fig, stem, a.out); plt.close(fig)
    emit(fig01, 'fig01')
    emit(fig02, 'fig02')
    for name, stem in (('G14a', 'fig03'), ('G14b', 'fig04'), ('G14c', 'fig05')): emit(lambda name=name: fig_G14(name), stem)
    emit(lambda: fig_cert(os.path.join(a.data, 'traza_G14_mas01.txt'), 'G14a', (0, 1)), 'fig06')
    emit(lambda: fig_cert(os.path.join(a.data, 'traza_G14b_mas03.txt'), 'G14b', (0, 3)), 'fig06b')
    emit(lambda: fig_cert(os.path.join(a.data, 'traza_cand14c.txt'), 'G14c', (2, 3)), 'fig06c')
    emit(lambda: fig07(load_atascadas14(os.path.join(a.data, 'atascadas14_final.txt'))), 'fig07')
    emit(fig08, 'fig08')
    emit(fig09, 'fig09')
    if not a.only:   # the full log is written only by a full run
        with open(os.path.join(a.out, 'verify_log.txt'), 'w', encoding='utf-8') as f: f.write('\n'.join(LOG)+'\n')
    else:
        print('\n'.join(LOG))

if __name__ == '__main__':
    main()
