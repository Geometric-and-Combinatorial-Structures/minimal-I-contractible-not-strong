"""dibujo.py — drawing primitives for the manuscript figures (English labels).
Companion of make_figures.py. Requires discos.py in the same directory."""
import math, itertools, collections, re
import numpy as np, networkx as nx
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from discos import *

RED = '#c0392b'; AMBER = '#e69f00'; AMBER_DK = '#8a5a00'; BLUE = '#0072b2'; GREEN = '#2a9d5b'; PURPLE = '#7b3fa0'
FILL = '#eef3fa'; EDGE = '#555555'; NODE_EC = '#222222'

def node(ax, xy, text, r=0.055, fc='white', ec=NODE_EC, tc='black', fs=6, lw=0.8, bold=False, z=5):
    ax.add_patch(Circle(xy, r, fc=fc, ec=ec, lw=lw, zorder=z))
    if str(text) != '':
        ax.text(xy[0], xy[1], str(text), ha='center', va='center', fontsize=fs, color=tc,
                fontweight='bold' if bold else 'normal', zorder=z+1)

def title(ax, s):
    ax.set_title(s, loc='left', x=0.06, pad=3)

# ---------------------------------------------------------------- unfolded disc
def draw_disk(ax, U, cycle, word, segments, label_map=None, radius=1.0, node_r=0.058, fs=6,
              arc_r=1.13, seg_colors=None, show_arcs=True, lw_bd=1.8, node_style=None, extra_edges=()):
    """cycle: disk vertices along the boundary starting at word[0] (clockwise from top).
    segments: list of (start_idx, end_idx, label) with label in {'a', 'a⁻¹', 'spur'}."""
    lm = label_map or (lambda x: x)
    D = U['D']; k = len(cycle); pos = tutte(D, cycle, radius=radius)
    for dt in U['dtris']:
        ax.add_patch(Polygon([pos[v] for v in dt], closed=True, fc=FILL, ec='none', zorder=1))
    bset = {frozenset(e) for e in U['boundary_edges']}
    for a, b in D.edges():
        if frozenset((a, b)) in bset: continue
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color=EDGE, lw=0.7, zorder=2, solid_capstyle='round')
    for i in range(k):
        a, b = cycle[i], cycle[(i+1) % k]
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color=RED, lw=lw_bd, zorder=3, solid_capstyle='round')
    for a, b, col, lw in extra_edges:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color=col, lw=lw, zorder=3, solid_capstyle='round')
    bd = set(cycle); ns = node_style or {}
    for v in D.nodes():
        if v in ns:
            fc, ec, tc = ns[v]; node(ax, pos[v], lm(U['label'][v]), r=node_r, fc=fc, ec=ec, tc=tc, fs=fs, lw=1.2, bold=(v in bd))
        elif v in bd:
            node(ax, pos[v], lm(U['label'][v]), r=node_r, fc='white', ec=RED, tc=RED, fs=fs, lw=1.2, bold=True)
        else:
            node(ax, pos[v], lm(U['label'][v]), r=node_r, fs=fs)
    def ang(i): return math.pi/2 - 2*math.pi*(i % k)/k
    if show_arcs:
        for j, (s, e, lab) in enumerate(segments):
            a0 = ang(s); a1 = a0 - 2*math.pi*(e-s)/k
            col = seg_colors[j] if seg_colors else RED
            gap = 0.18*2*math.pi/k; th = np.linspace(a0-gap, a1+gap, 60)
            ax.plot(arc_r*np.cos(th), arc_r*np.sin(th), color=col, lw=0.9, zorder=2)
            inv = lab.endswith('⁻¹')
            if lab != 'spur':
                if not inv: p1 = (arc_r*np.cos(th[-1]), arc_r*np.sin(th[-1])); p0 = (arc_r*np.cos(th[-4]), arc_r*np.sin(th[-4]))
                else: p1 = (arc_r*np.cos(th[0]), arc_r*np.sin(th[0])); p0 = (arc_r*np.cos(th[3]), arc_r*np.sin(th[3]))
                ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='-|>,head_length=0.35,head_width=0.18', color=col, lw=0.9, shrinkA=0, shrinkB=0), zorder=4)
            am = (a0+a1)/2; rr = arc_r+0.10
            ax.text(rr*np.cos(am), rr*np.sin(am), lab, ha='center', va='center', fontsize=fs+1, color=col,
                    fontstyle='italic' if lab != 'spur' else 'normal', zorder=4)
    ax.set_aspect('equal'); ax.set_xlim(-1.32, 1.32); ax.set_ylim(-1.32, 1.32); ax.axis('off')
    return pos

def word_string(word, segments, label_map=None, sep=' | '):
    lm = label_map or (lambda x: x); k = len(word)
    return sep.join(' '.join(str(lm(word[i % k])) for i in range(s, e)) for s, e, lab in segments)

def segment_pattern(word, k, prefer=('a', 'a', 'a⁻¹')):
    """Split a cyclic boundary word into traversals of a k-cycle a (forward 'a', backward 'a⁻¹')
    and 2-step spurs x y x. Returns (rotation, rotated word, segments) preferring the pattern `prefer`."""
    n = len(word); results = []
    for r in range(n):
        w = word[r:]+word[:r]; A = w[:k]; p = 0; segs = []; ok = True
        while p < n:
            blk = [w[(p+i) % n] for i in range(k+1)]
            if blk == A+[A[0]]: segs.append((p, p+k, 'a')); p += k
            elif blk == [A[0]]+A[:0:-1]+[A[0]]: segs.append((p, p+k, 'a⁻¹')); p += k
            elif w[p] == A[0] and w[(p+2) % n] == A[0] and w[(p+1) % n] not in A: segs.append((p, p+2, 'spur')); p += 2
            else: ok = False; break
        if ok and p == n: results.append((r, w, segs))
    for r, w, segs in results:
        if tuple(l for _, _, l in segs if l != 'spur') == tuple(prefer): return r, w, segs
    return results[0] if results else None

def period(w):
    for k in range(1, len(w)+1):
        if len(w) % k == 0 and w == w[:k]*(len(w)//k): return k
    return len(w)

# ---------------------------------------------------------------- node-link drawings
def draw_graph(ax, G, pos, node_r=0.07, fs=6, red_edges=(), dashed_edges=(), amber_nodes=(), amber_edges=(),
               red_nodes=(), lw=0.7, edge_color=EDGE, label=True, bold_cycle_lw=1.8, node_colors=None,
               hide_nodes=(), hide_edges=(), blue_nodes=()):
    red = {frozenset(e) for e in red_edges}; dsh = {frozenset(e) for e in dashed_edges}; amb = {frozenset(e) for e in amber_edges}
    hid = {frozenset(e) for e in hide_edges}
    for a, b in G.edges():
        e = frozenset((a, b))
        if e in hid or a in hide_nodes or b in hide_nodes: continue
        x = [pos[a][0], pos[b][0]]; y = [pos[a][1], pos[b][1]]
        if e in amb: ax.plot(x, y, color=AMBER, lw=4.5, zorder=2.5, solid_capstyle='round')   # halo
        if e in dsh: ax.plot(x, y, color=BLUE, lw=1.6, ls=(0, (3, 2)), zorder=3)
        elif e in red: ax.plot(x, y, color=RED, lw=bold_cycle_lw, zorder=3)
        elif e in amb: ax.plot(x, y, color=AMBER_DK, lw=0.9, zorder=3)
        else: ax.plot(x, y, color=edge_color, lw=lw, zorder=2)
    for v in G.nodes():
        if v in hide_nodes: continue
        if node_colors and v in node_colors: fc, ec, tc = node_colors[v]
        elif v in blue_nodes: fc, ec, tc = 'white', BLUE, BLUE
        elif v in amber_nodes: fc, ec, tc = AMBER, (RED if v in red_nodes else AMBER_DK), 'black'
        elif v in red_nodes: fc, ec, tc = 'white', RED, RED
        else: fc, ec, tc = 'white', NODE_EC, 'black'
        node(ax, pos[v], v if label else '', r=node_r, fc=fc, ec=ec, tc=tc, fs=fs, lw=1.2 if ec != NODE_EC else 0.8,
             bold=(v in red_nodes or v in blue_nodes))
    ax.set_aspect('equal'); ax.axis('off')
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]; m = node_r*2.2
    ax.set_xlim(min(xs)-m, max(xs)+m); ax.set_ylim(min(ys)-m, max(ys)+m)

def order_along(H):
    nodes = list(H.nodes())
    if not nodes: return []
    start = min(nodes, key=lambda v: H.degree(v)); order = []; seen = set()
    def dfs(v):
        order.append(v); seen.add(v)
        for w in sorted(H[v], key=lambda w: H.degree(w)):
            if w not in seen: dfs(w)
    dfs(start)
    for v in nodes:
        if v not in seen: order.append(v)
    return order

def concentric_layout(G, center=None, r1=1.0, r2=1.9, inner_rot=0.0, outer_rot=None):
    """center vertex at origin, N(center) on a ring ordered along the induced subgraph, rest outside."""
    if center is None: center = max(G.nodes(), key=lambda v: (G.degree(v), -v))
    ring1 = order_along(G.subgraph(G[center]))
    pos = {center: np.zeros(2)}; n1 = len(ring1); ang1 = {}
    for i, v in enumerate(ring1):
        a = math.pi/2 + inner_rot + 2*math.pi*i/n1; ang1[v] = a
        pos[v] = r1*np.array([math.cos(a), math.sin(a)])
    rest = [v for v in G.nodes() if v != center and v not in ring1]
    def mean_ang(v):
        nb = [ang1[w] for w in G[v] if w in ang1]
        return math.atan2(sum(math.sin(a) for a in nb), sum(math.cos(a) for a in nb)) if nb else 0.0
    rest.sort(key=mean_ang); n2 = len(rest)
    base = mean_ang(rest[0]) if outer_rot is None else outer_rot
    for i, v in enumerate(rest):
        a = base + 2*math.pi*i/n2; pos[v] = r2*np.array([math.cos(a), math.sin(a)])
    return pos

def ring_layout(G, outer, r_out=2.0, r_in=1.0, center=None, rot=np.pi/2, inner_rot=0.0):
    """`outer` cycle on a regular polygon (clockwise from angle rot); remaining vertices evenly on an inner
    ring, ordered by the circular mean angle of their outer neighbours."""
    pos = {}; ko = len(outer); ang = {}
    for i, v in enumerate(outer):
        a = rot - 2*np.pi*i/ko; ang[v] = a; pos[v] = r_out*np.array([np.cos(a), np.sin(a)])
    rest = [v for v in G.nodes() if v not in outer and v != center]
    if center is not None: pos[center] = np.zeros(2)
    def mean_ang(v):
        nb = [ang[w] for w in G[v] if w in ang]
        return math.atan2(sum(math.sin(a) for a in nb), sum(math.cos(a) for a in nb)) if nb else 0.0
    rest.sort(key=mean_ang); n = len(rest)
    for i, v in enumerate(rest):
        a = inner_rot + mean_ang(rest[0]) + 2*np.pi*i/n; pos[v] = r_in*np.array([np.cos(a), np.sin(a)])
    return pos

def seg_point_dist(p, a, b):
    ab = b-a; den = float(np.dot(ab, ab))
    if den == 0: return float(np.linalg.norm(p-a))
    t = np.clip(np.dot(p-a, ab)/den, 0, 1); return float(np.linalg.norm(p-(a+t*ab)))

def layout_clearance(G, pos):
    m = 1e9
    for a, b in G.edges():
        for v in G.nodes():
            if v in (a, b): continue
            m = min(m, seg_point_dist(pos[v], pos[a], pos[b]))
    return m

def score(G, pos, node_r=0.13):
    """min(edge-to-nonincident-vertex clearance, half the smallest vertex distance minus node radius)."""
    cl = layout_clearance(G, pos)
    dmin = min(np.linalg.norm(pos[a]-pos[b]) for a in G for b in G if a < b)
    return min(cl, dmin/2 - node_r)

def best_concentric(G, center=None, r2=2.0):
    best = (-9, None)
    for ir in np.linspace(0, 2*np.pi/8, 17):
        for orot in np.linspace(0, 2*np.pi/4, 25):
            pos = concentric_layout(G, center=center, r2=r2, inner_rot=ir, outer_rot=orot)
            sc = score(G, pos)
            if sc > best[0]: best = (sc, pos)
    return best

def best_ring(G, outer, fine=True, node_r=0.13):
    k = len(outer); best = (-9, None)
    centers = [None, max(G.nodes(), key=lambda v: (G.degree(v), -v))] if fine else [None]
    r_ins = (0.9, 1.1, 1.3) if fine else (1.0, 1.2)
    n_ir, n_rot = (12, 8) if fine else (6, 4)
    for center in centers:
        for r_in in r_ins:
            for ir in np.linspace(0, 2*np.pi/len(G), n_ir):
                for rot in np.linspace(np.pi/2, np.pi/2+2*np.pi/k, n_rot):
                    pos = ring_layout(G, outer, r_in=r_in, center=center, rot=rot, inner_rot=ir)
                    sc = score(G, pos, node_r=node_r)
                    if sc > best[0]: best = (sc, pos)
    return best

# ---------------------------------------------------------------- render-then-verify
def bbox_check(fig):
    """figure-style §9.1: overlapping visible text boxes (tick labels of axis-off axes excluded)
    and texts outside the figure box. Returns (overlaps, outside)."""
    fig.canvas.draw(); r = fig.canvas.get_renderer(); tick = set()
    for ax in fig.axes:
        if not ax.axison:
            tick |= set(ax.get_xticklabels(which='both')+ax.get_yticklabels(which='both'))
            tick |= {ax.xaxis.label, ax.yaxis.label, ax.xaxis.offsetText, ax.yaxis.offsetText}
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible() and t not in tick]
    bad = []
    for i, (a, ba) in enumerate(texts):
        for b, bb in texts[i+1:]:
            if ba.overlaps(bb): bad.append((a.get_text(), b.get_text()))
    out = [t.get_text() for t, bt in texts if not (fig.bbox.contains(bt.x0, bt.y0) and fig.bbox.contains(bt.x1, bt.y1))]
    return bad, out

def save_all(fig, stem, outdir='figures'):
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(f'{outdir}/{stem}.{ext}', dpi=300, facecolor='white')
