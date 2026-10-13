
"""discos.py — core helpers: g6 parsing, clique triangles, disk unfolding (cut along edges in
!=2 triangles, glue corners across edges in exactly 2 triangles), Tutte embedding, boundary word."""
import itertools, collections
import numpy as np
import networkx as nx

def g6(s):
    return nx.from_graph6_bytes(s.encode())

def triangles(G):
    return [tuple(sorted(c)) for c in nx.enumerate_all_cliques(G) if len(c) == 3]

def unfold(G, tris=None):
    """Return dict with disk structure. tris defaults to clique triangles.
    corners (t,v) are glued across edges contained in exactly two triangles of `tris`."""
    if tris is None:
        tris = triangles(G)
    tri_of_edge = collections.defaultdict(list)
    for i, t in enumerate(tris):
        for e in itertools.combinations(t, 2):
            tri_of_edge[frozenset(e)].append(i)
    # union-find on corners
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for i, t in enumerate(tris):
        for v in t: find((i, v))
    for e, ts in tri_of_edge.items():
        if len(ts) == 2:
            for v in e:
                union((ts[0], v), (ts[1], v))
    roots = sorted({find(c) for c in parent}, key=lambda r: (r[1], r[0]))
    idx = {r: k for k, r in enumerate(roots)}
    cls = {c: idx[find(c)] for c in parent}          # corner -> disk vertex id
    label = {idx[r]: r[1] for r in roots}            # disk vertex -> original label
    dtris = [tuple(cls[(i, v)] for v in t) for i, t in enumerate(tris)]
    dedge_count = collections.Counter()
    for dt in dtris:
        for e in itertools.combinations(dt, 2):
            dedge_count[frozenset(e)] += 1
    D = nx.Graph()
    D.add_nodes_from(range(len(roots)))
    D.add_edges_from(tuple(e) for e in dedge_count)
    boundary_edges = [tuple(e) for e, c in dedge_count.items() if c == 1]
    B = nx.Graph(boundary_edges)
    # boundary cycle(s)
    cycles = []
    for comp in nx.connected_components(B):
        H = B.subgraph(comp)
        if all(d == 2 for _, d in H.degree()):
            cyc = [next(iter(comp))]
            prev = None
            while True:
                nb = [w for w in H[cyc[-1]] if w != prev]
                nxt = nb[0]
                if nxt == cyc[0]: break
                prev = cyc[-1]; cyc.append(nxt)
            cycles.append(cyc)
        else:
            cycles.append(None)
    return dict(tris=tris, dtris=dtris, D=D, label=label, cls=cls,
                boundary_edges=boundary_edges, cycles=cycles,
                tri_of_edge=tri_of_edge, dedge_count=dedge_count)

def tutte(D, cycle, radius=1.0, rot=np.pi/2):
    """Tutte embedding: boundary cycle on a regular polygon (first vertex at angle rot, clockwise order)."""
    n = D.number_of_nodes(); k = len(cycle)
    pos = np.zeros((n, 2)); fixed = np.zeros(n, bool)
    for j, v in enumerate(cycle):
        a = rot - 2*np.pi*j/k
        pos[v] = radius*np.array([np.cos(a), np.sin(a)]); fixed[v] = True
    free = [v for v in range(n) if not fixed[v]]
    if free:
        fi = {v: i for i, v in enumerate(free)}
        A = np.zeros((len(free), len(free))); b = np.zeros((len(free), 2))
        for v in free:
            nb = list(D[v]); A[fi[v], fi[v]] = len(nb)
            for w in nb:
                if fixed[w]: b[fi[v]] += pos[w]
                else: A[fi[v], fi[w]] -= 1
        sol = np.linalg.solve(A, b)
        for v in free: pos[v] = sol[fi[v]]
    return {v: pos[v] for v in range(n)}

def boundary_word(U, cycle):
    return [U['label'][v] for v in cycle]

def align_word(word, cycle, target):
    """Rotate/reverse (word, cycle) so that word == target (list of labels). Returns (word, cycle) or raises."""
    k = len(word)
    for rev in (False, True):
        w = word[::-1] if rev else word; c = cycle[::-1] if rev else cycle
        for r in range(k):
            if w[r:]+w[:r] == target:
                return w[r:]+w[:r], c[r:]+c[:r]
    raise ValueError('target word not found: %s vs %s' % (target, word))

def edge_tri_multiplicity(G):
    tris = triangles(G); cnt = collections.Counter()
    for t in tris:
        for e in itertools.combinations(t, 2): cnt[frozenset(e)] += 1
    return cnt
