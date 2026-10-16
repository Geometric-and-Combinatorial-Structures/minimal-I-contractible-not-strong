"""Implementación independiente (no reutiliza código de atascadas.c ni homZ del proyecto).

- parse_g6 / to_g6 : graph6 (propio)
- cliques          : complejo de cliques por extensión recursiva (propio)
- boundary_matrices: matrices frontera enteras con orientación por orden de vértices
- snf_diag         : forma normal de Smith (diagonal) por eliminación entera exacta (Python int)
- homology_Z       : Betti enteros y coeficientes de torsión por dimensión
- z2_acyclic       : homología reducida Z2 trivial (rango sobre GF(2) con bitmasks)
- is_cone, is_0dis : cono / 0-desmantelable (dominación)
- is_IS            : decisión exacta de strong I-contraíble con memo y poda por Z2
"""
from functools import lru_cache
from itertools import combinations
import sys

sys.setrecursionlimit(100000)

# ---------- graph6 ----------
def parse_g6(s):
    s = s.strip()
    if s.startswith('>>graph6<<'):
        s = s[10:]
    data = [ord(c) - 63 for c in s]
    if data[0] <= 62:
        n = data[0]; k = 1
    else:
        n = (data[1] << 12) | (data[2] << 6) | data[3]; k = 4
    bits = []
    for d in data[k:]:
        for b in range(5, -1, -1):
            bits.append((d >> b) & 1)
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].add(j); adj[j].add(i)
            idx += 1
    return n, adj

def to_g6(n, adj):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if j in adj[i] else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for i in range(0, len(bits), 6):
        v = 0
        for b in bits[i:i+6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out

def edges_of(adj):
    return sorted((i, j) for i in range(len(adj)) for j in adj[i] if i < j)

# ---------- complejo de cliques ----------
def cliques(adj, verts=None):
    """Todas las cliques (como tuplas ordenadas) del subgrafo inducido en verts."""
    if verts is None:
        verts = range(len(adj))
    verts = sorted(verts)
    vs = set(verts)
    out = []
    def ext(cl, cand):
        out.append(tuple(cl))
        for v in sorted(cand):
            if cl and v < cl[-1]:
                continue
            ext(cl + [v], cand & adj[v])
    ext([], vs)
    return [c for c in out if c]

def boundary_matrices(cl):
    """Devuelve (faces_by_dim, mats) con mats[k] = matriz de ∂_k : C_k -> C_{k-1}
    como lista de filas (listas de int) de tamaño |faces[k-1]| x |faces[k]|."""
    bydim = {}
    for c in cl:
        bydim.setdefault(len(c) - 1, []).append(c)
    for k in bydim:
        bydim[k].sort()
    maxd = max(bydim)
    index = {k: {f: i for i, f in enumerate(bydim[k])} for k in bydim}
    mats = {}
    for k in range(1, maxd + 1):
        rows = len(bydim[k - 1]); cols = len(bydim[k])
        M = [[0] * cols for _ in range(rows)]
        for j, f in enumerate(bydim[k]):
            for t in range(len(f)):
                face = f[:t] + f[t+1:]
                M[index[k - 1][face]][j] = (-1) ** t
        mats[k] = M
    return bydim, mats

# ---------- Smith normal form entera (propia) ----------
def snf_diag(M):
    """Forma normal de Smith de una matriz entera (lista de listas). Devuelve la lista de
    invariantes d_1 | d_2 | ... (positivos), rango = len(lista)."""
    A = [row[:] for row in M]
    if not A or not A[0]:
        return []
    m, n = len(A), len(A[0])
    diag = []
    r = 0  # fila/columna actual
    while r < m and r < n:
        # buscar pivote no nulo con menor valor absoluto en la submatriz
        piv = None
        for i in range(r, m):
            for j in range(r, n):
                if A[i][j] != 0 and (piv is None or abs(A[i][j]) < abs(A[piv[0]][piv[1]])):
                    piv = (i, j)
        if piv is None:
            break
        i, j = piv
        A[r], A[i] = A[i], A[r]
        for row in A:
            row[r], row[j] = row[j], row[r]
        while True:
            p = A[r][r]
            done = True
            # eliminar columna r por debajo
            for i in range(r + 1, m):
                if A[i][r] != 0:
                    q = A[i][r] // p
                    if q:
                        Ai, Ar = A[i], A[r]
                        for j in range(r, n):
                            Ai[j] -= q * Ar[j]
                    if A[i][r] != 0:
                        # el residuo es menor que |p|: intercambiar filas y repetir
                        A[r], A[i] = A[i], A[r]
                        done = False
                        break
            if not done:
                continue
            # eliminar fila r a la derecha
            for j in range(r + 1, n):
                if A[r][j] != 0:
                    q = A[r][j] // p
                    if q:
                        for i in range(r, m):
                            A[i][j] -= q * A[i][r]
                    if A[r][j] != 0:
                        for row in A:
                            row[r], row[j] = row[j], row[r]
                        done = False
                        break
            if not done:
                continue
            # p divide a toda la submatriz restante?
            bad = None
            for i in range(r + 1, m):
                for j in range(r + 1, n):
                    if A[i][j] % p != 0:
                        bad = (i, j); break
                if bad: break
            if bad is None:
                break
            # sumar la fila bad[0] a la fila r y repetir
            Ar, Ab = A[r], A[bad[0]]
            for j in range(r, n):
                Ar[j] += Ab[j]
        diag.append(abs(A[r][r]))
        r += 1
    # normalizar cadena de divisibilidad (d_i | d_{i+1}) mediante gcd/lcm
    from math import gcd
    d = diag
    changed = True
    while changed:
        changed = False
        for i in range(len(d)):
            for j in range(i + 1, len(d)):
                if d[j] % d[i] != 0:
                    g = gcd(d[i], d[j]); l = d[i] * d[j] // g
                    d[i], d[j] = g, l
                    changed = True
    return sorted(d)

def homology_Z(adj, verts=None):
    """Devuelve dict k -> (betti_k, [torsiones]) para el complejo de cliques (homología no reducida)."""
    cl = cliques(adj, verts)
    if not cl:
        return {}
    bydim, mats = boundary_matrices(cl)
    maxd = max(bydim)
    rank = {0: 0}; tors = {0: []}
    for k in range(1, maxd + 1):
        d = snf_diag(mats[k])
        rank[k] = len(d)
        tors[k] = [x for x in d if x > 1]
    rank[maxd + 1] = 0; tors[maxd + 1] = []
    H = {}
    for k in range(0, maxd + 1):
        betti = len(bydim[k]) - rank[k] - rank[k + 1]
        H[k] = (betti, sorted(tors[k + 1]))
    return H

def fmt_H(H):
    parts = []
    for k in sorted(H):
        b, t = H[k]
        s = []
        if b: s.append(f"Z^{b}" if b > 1 else "Z")
        s += [f"Z/{x}" for x in t]
        parts.append(f"H{k}=" + ("+".join(s) if s else "0"))
    return " ".join(parts)

def is_contractible_homology(H):
    """Homología de un punto: H0 = Z, resto 0 (condición necesaria de contractibilidad)."""
    if H.get(0) != (1, []):
        return False
    return all(H[k] == (0, []) for k in H if k > 0)

# ---------- Z2 ----------
def _rank_gf2(rows):
    """rows: lista de enteros (bitmasks). Rango sobre GF(2)."""
    basis = {}
    r = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v; r += 1; break
    return r

def z2_betti(adj, verts):
    """Betti reducidos sobre Z2 del complejo de cliques de G[verts]."""
    verts = sorted(verts)
    if not verts:
        return None
    cl = cliques(adj, verts)
    bydim = {}
    for c in cl:
        bydim.setdefault(len(c) - 1, []).append(c)
    maxd = max(bydim)
    idx = {k: {f: i for i, f in enumerate(bydim[k])} for k in bydim}
    rank = {}
    for k in range(1, maxd + 1):
        rows = []
        for f in bydim[k]:
            m = 0
            for t in range(len(f)):
                m |= 1 << idx[k - 1][f[:t] + f[t+1:]]
            rows.append(m)
        rank[k] = _rank_gf2(rows)
    rank[0] = 1  # aumentación (reducida): rango de eps: C0 -> Z2 es 1 si hay vértices
    rank[maxd + 1] = 0
    return [len(bydim[k]) - rank[k] - rank[k + 1] for k in range(maxd + 1)]

def z2_acyclic(adj, verts):
    """Verdadero si G[verts] es no vacío y tiene homología reducida Z2 nula."""
    if not verts:
        return False
    b = z2_betti(adj, verts)
    return all(x == 0 for x in b)

# ---------- cono / 0-Dis / I_S ----------
def is_cone(adj, verts):
    verts = set(verts)
    if not verts:
        return False
    return any(adj[v] & verts == verts - {v} for v in verts)

def is_0dis(adj, verts):
    """0-desmantelable: eliminar sucesivamente vértices dominados (N[v] ⊆ N[w], w≠v) hasta K1."""
    S = set(verts)
    if not S:
        return False
    while len(S) > 1:
        found = None
        for v in S:
            Nv = (adj[v] & S) | {v}
            for w in S:
                if w != v and Nv <= ((adj[w] & S) | {w}):
                    found = v; break
            if found is not None:
                break
        if found is None:
            return False
        S.remove(found)
    return True

class ISSolver:
    """Decisión exacta de I_S (strong I-contraíble) sobre subgrafos (V', E') de una gráfica base.
    Estado = frozenset de aristas + frozenset de vértices (para vértices aislados). Reglas:
      K1 ∈ I_S; G ∈ I_S si existe v con N(v) ∈ I_S y G−v ∈ I_S, o arista uv con N(u,v) ∈ I_S y G−uv ∈ I_S.
    Poda: I_S ⇒ Z2-acíclico (teorema), así que estados no Z2-acíclicos son falsos.
    """
    def __init__(self, limit=2_000_000):
        self.memo = {}
        self.calls = 0
        self.limit = limit

    def solve(self, n, adj):
        V = frozenset(range(n))
        E = frozenset(edges_of(adj))
        return self._is(V, E)

    def _adj(self, V, E):
        adj = {v: set() for v in V}
        for (a, b) in E:
            adj[a].add(b); adj[b].add(a)
        return adj

    def _is(self, V, E):
        key = (V, E)
        if key in self.memo:
            return self.memo[key]
        self.calls += 1
        if self.calls > self.limit:
            raise RuntimeError("límite de llamadas")
        if len(V) == 0:
            return False
        if len(V) == 1:
            self.memo[key] = True; return True
        adj = self._adj(V, E)
        full = [set() for _ in range(max(V) + 1)]
        for v in V: full[v] = adj[v]
        if not z2_acyclic(full, V):
            self.memo[key] = False; return False
        res = False
        # borrados de vértices
        for v in sorted(V, key=lambda x: len(adj[x])):
            Nv = frozenset(adj[v])
            if not Nv:
                continue
            NE = frozenset(e for e in E if e[0] in Nv and e[1] in Nv)
            if self._is(Nv, NE):
                V2 = V - {v}
                E2 = frozenset(e for e in E if v not in e)
                if self._is(V2, E2):
                    res = True; break
        if not res:
            for e in sorted(E):
                a, b = e
                N = frozenset(adj[a] & adj[b])
                if not N:
                    continue
                NE = frozenset(f for f in E if f[0] in N and f[1] in N)
                if self._is(N, NE):
                    if self._is(V, E - {e}):
                        res = True; break
        self.memo[key] = res
        return res

# ---------- utilidades estructurales ----------
def triangles(adj):
    n = len(adj)
    return [(i, j, k) for i in range(n) for j in adj[i] if j > i for k in adj[i] & adj[j] if k > j]

def k4s(adj):
    return [c for c in cliques(adj) if len(c) == 4]

def edge_triangle_count(adj):
    cnt = {}
    for (a, b, c) in triangles(adj):
        for e in ((a, b), (a, c), (b, c)):
            cnt[e] = cnt.get(e, 0) + 1
    for e in edges_of(adj):
        cnt.setdefault(e, 0)
    return cnt

def unfold_disk(adj):
    """Despliegue (reimplementación): corta el complejo 2-dim a lo largo de las aristas con ≠ 2 triángulos
    y pega las esquinas a través de las aristas con exactamente 2 triángulos. Devuelve un dict con
    el tipo de superficie obtenida y, si es un disco, la palabra de frontera (etiquetas originales)."""
    tri = triangles(adj)
    cnt = edge_triangle_count(adj)
    tri_of_edge = {}
    for ti, (a, b, c) in enumerate(tri):
        for e in ((a, b), (a, c), (b, c)):
            tri_of_edge.setdefault(e, []).append(ti)
    # union-find sobre esquinas (ti, v)
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry: parent[rx] = ry
    for ti, t in enumerate(tri):
        for v in t: find((ti, v))
    for e, ts in tri_of_edge.items():
        if len(ts) == 2:
            for v in e:
                union((ts[0], v), (ts[1], v))
    # vértices desplegados
    roots = sorted(set(find(x) for x in list(parent)))
    rid = {r: i for i, r in enumerate(roots)}
    label = {rid[r]: r[1] for r in roots}  # etiqueta original
    utri = [tuple(sorted(rid[find((ti, v))] for v in t)) for ti, t in enumerate(tri)]
    uedges = {}
    for t in utri:
        for e in ((t[0], t[1]), (t[0], t[2]), (t[1], t[2])):
            uedges[e] = uedges.get(e, 0) + 1
    nV, nE, nF = len(roots), len(uedges), len(utri)
    chi = nV - nE + nF
    manifold = all(c <= 2 for c in uedges.values())
    bedges = [e for e, c in uedges.items() if c == 1]
    # componentes de frontera
    badj = {}
    for a, b in bedges:
        badj.setdefault(a, []).append(b); badj.setdefault(b, []).append(a)
    bvertex_ok = all(len(v) == 2 for v in badj.values())
    comps = 0; seen = set(); cycles = []
    for s in badj:
        if s in seen: continue
        comps += 1
        cyc = [s]; seen.add(s); prev = None; cur = s
        while True:
            nxt = [w for w in badj[cur] if w != prev]
            if not nxt: break
            w = nxt[0]
            if w == s: break
            cyc.append(w); seen.add(w); prev, cur = cur, w
        cycles.append(cyc)
    # conexidad del complejo desplegado
    tadj = {i: set() for i in range(nV)}
    for t in utri:
        for a in t:
            for b in t:
                if a != b: tadj[a].add(b)
    s0 = 0; seen2 = {s0}; st = [s0]
    while st:
        v = st.pop()
        for w in tadj[v]:
            if w not in seen2: seen2.add(w); st.append(w)
    connected = len(seen2) == nV
    is_disk = manifold and bvertex_ok and connected and comps == 1 and chi == 1
    out = dict(n_tri=nF, cortes=[e for e, c in cnt.items() if c != 2], vertices_disco=nV, aristas_disco=nE, chi=chi,
               variedad=manifold, conexa=connected, componentes_frontera=comps, es_disco=is_disk)
    if is_disk:
        word = [label[v] for v in cycles[0]]
        out['palabra'] = word
        out['lados_borde'] = len(word)
        out.update(analyze_word(word, adj))
    return out

def analyze_word(word, adj):
    """La palabra de frontera recorre un ciclo C de G (los vértices distintos de la palabra).
    Devuelve el ciclo, la longitud k, el número de rotación (grado del recorrido), la periodicidad
    cíclica mínima de la palabra y la descomposición en tramos ±."""
    L = len(word)
    verts = sorted(set(word))
    k = len(verts)
    # el ciclo identificado: aristas usadas por la palabra
    used = set()
    for i in range(L):
        a, b = word[i], word[(i + 1) % L]
        used.add((min(a, b), max(a, b)))
    is_cycle = len(used) == k and all(sum(1 for e in used if v in e) == 2 for v in verts)
    res = dict(ciclo_vertices=verts, k=k, borde_es_ciclo=is_cycle)
    if not is_cycle:
        return res
    # orientar el ciclo
    cyc = [verts[0]]; prev = None
    while len(cyc) < k:
        cur = cyc[-1]
        nb = [e[0] if e[1] == cur else e[1] for e in used if cur in e]
        nxt = nb[0] if nb[0] != prev else nb[1]
        prev = cur; cyc.append(nxt)
    pos = {v: i for i, v in enumerate(cyc)}
    steps = []
    for i in range(L):
        d = (pos[word[(i + 1) % L]] - pos[word[i]]) % k
        steps.append(1 if d == 1 else -1)
    rot = sum(steps) // k if sum(steps) % k == 0 else sum(steps) / k
    # tramos de signo constante (cíclicamente)
    # rotar para empezar en cambio de signo
    start = next((i for i in range(L) if steps[i] != steps[i - 1]), 0)
    s2 = steps[start:] + steps[:start]
    runs = []
    for s in s2:
        if runs and runs[-1][0] == s: runs[-1][1] += 1
        else: runs.append([s, 1])
    # periodicidad cíclica mínima de la palabra
    per = L
    for p in range(1, L + 1):
        if L % p == 0 and all(word[i] == word[(i + p) % L] for i in range(L)):
            per = p; break
    res.update(ciclo_orientado=cyc, pasos=steps, numero_rotacion=rot, periodo_palabra=per, repeticiones=L // per,
               tramos=[(('+' if s > 0 else '-'), l) for s, l in runs],
               patron=''.join(('a' if s > 0 else 'A') * l for s, l in runs))
    return res

def automorphisms(adj):
    """Todos los automorfismos (como tuplas imagen) vía GraphMatcher y un conjunto generador pequeño."""
    import networkx as nx
    from networkx.algorithms.isomorphism import GraphMatcher
    n = len(adj)
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges_of(adj))
    auts = sorted(tuple(m[i] for i in range(n)) for m in GraphMatcher(G, G).isomorphisms_iter())
    ident = tuple(range(n))
    def compose(p, q):  # p∘q
        return tuple(p[q[i]] for i in range(n))
    def closure(gens):
        S = {ident}; frontier = [ident]
        while frontier:
            new = []
            for s in frontier:
                for g in gens:
                    c = compose(g, s)
                    if c not in S: S.add(c); new.append(c)
            frontier = new
        return S
    gens = []
    S = {ident}
    # greedy: añadir el automorfismo de mayor orden no generado todavía
    def order(p):
        o = 1; c = p
        while c != ident: c = compose(p, c); o += 1
        return o
    remaining = sorted(set(auts) - S, key=lambda p: -order(p))
    while remaining:
        g = remaining[0]; gens.append(g); S = closure(gens)
        remaining = [p for p in remaining if p not in S]
    def cycles(p):
        seen = set(); out = []
        for i in range(n):
            if i in seen or p[i] == i: continue
            c = [i]; j = p[i]
            while j != i: c.append(j); j = p[j]
            seen.update(c); out.append(tuple(c))
        return out
    return dict(orden=len(auts), generadores=[cycles(g) for g in gens], ordenes_generadores=[order(g) for g in gens])

def is_connected(adj, verts):
    verts = set(verts)
    if not verts: return False
    s = next(iter(verts)); seen = {s}; st = [s]
    while st:
        v = st.pop()
        for w in adj[v] & verts:
            if w not in seen:
                seen.add(w); st.append(w)
    return seen == verts
