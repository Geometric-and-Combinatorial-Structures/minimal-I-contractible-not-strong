"""Finite graph arithmetic shared by read-only supplementary checks (stdlib)."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'data'))
from check_small_closures import (decode, encode, vertices, induced, edge,
                                 cliques, strong, colours, isomorphic)
from functools import lru_cache

def components(A):
    todo = set(range(len(A))); count = 0
    while todo:
        count += 1; stack = [min(todo)]
        while stack:
            u = stack.pop()
            if u not in todo: continue
            todo.remove(u); stack.extend(v for v in vertices(A[u]) if v in todo)
    return count

def cone(A):
    return any(a == ((1 << len(A))-1) ^ (1 << u) for u,a in enumerate(A))

def tree(A):
    return bool(A) and components(A) == 1 and sum(a.bit_count() for a in A) == 2*(len(A)-1)

@lru_cache(None)
def kdis(A, k):
    if not A: return False
    if len(A) == 1: return True
    full = (1 << len(A))-1
    for u in range(len(A)):
        L = induced(A, A[u])
        if (cone(L) if k == 0 else kdis(L,k-1)) and kdis(induced(A,full^(1<<u)),k):
            return True
    return False

def automorphisms(A):
    ca,_ = colours(A,A); mapping = {}; used = set()
    def visit():
        if len(mapping) == len(A): return 1
        choices = []
        for u in range(len(A)):
            if u in mapping: continue
            vs = [v for v in range(len(A)) if v not in used and ca[u] == ca[v]
                  and all(bool(A[u]>>x&1) == bool(A[v]>>y&1) for x,y in mapping.items())]
            if not vs: return 0
            choices.append((len(vs),u,vs))
        _,u,vs = min(choices); total = 0
        for v in vs:
            mapping[u]=v; used.add(v); total += visit(); used.remove(v); del mapping[u]
        return total
    return visit()

def smith_diagonal(matrix):
    """Unimodular row/column Euclidean reduction; return positive nonzero factors.

    At each stage the pivot divides the remaining block before it is frozen.
    Row/column swaps and subtraction of integer multiples preserve cokernels.
    """
    M=[list(r) for r in matrix]
    if not M or not M[0]: return []
    nr,nc=len(M),len(M[0]); k=0; out=[]
    while k < min(nr,nc):
        found=[(abs(M[i][j]),i,j) for i in range(k,nr) for j in range(k,nc) if M[i][j]]
        if not found: break
        _,i,j=min(found); M[k],M[i]=M[i],M[k]
        for row in M: row[k],row[j]=row[j],row[k]
        while True:
            if M[k][k] < 0: M[k]=[-x for x in M[k]]
            changed=False
            for i in range(k+1,nr):
                if M[i][k]:
                    q=M[i][k]//M[k][k]; M[i]=[x-q*y for x,y in zip(M[i],M[k])]
                    if M[i][k]: M[k],M[i]=M[i],M[k]
                    changed=True; break
            if changed: continue
            for j in range(k+1,nc):
                if M[k][j]:
                    q=M[k][j]//M[k][k]
                    for i in range(nr): M[i][j]-=q*M[i][k]
                    if M[k][j]:
                        for row in M: row[k],row[j]=row[j],row[k]
                    changed=True; break
            if changed: continue
            offender=next(((i,j) for i in range(k+1,nr) for j in range(k+1,nc) if M[i][j]%M[k][k]),None)
            if offender:
                i,_=offender; M[k]=[x+y for x,y in zip(M[k],M[i])]
            else: break
        out.append(abs(M[k][k])); k+=1
    assert all(b%a == 0 for a,b in zip(out,out[1:]))
    return out

@lru_cache(None)
def h1(A):
    """H1 of the clique complex: contract a spanning forest, then use d2.

    Non-tree edge coefficients identify the integral cycle lattice with Z^r.
    Contracting each tree component therefore gives the integral presentation
    of H1 with one generator per non-tree edge and one relation per triangle.
    """
    parent=list(range(len(A)))
    def find(u):
        while parent[u]!=u: u=parent[u]
        return u
    chords=[]
    for u,v in cliques(A,2):
        a,b=find(u),find(v)
        if a==b: chords.append((u,v))
        else: parent[a]=b
    ix={e:i for i,e in enumerate(chords)}; ts=cliques(A,3)
    M=[[0]*len(ts) for _ in chords]
    for j,(u,v,w) in enumerate(ts):
        for e,s in [((u,v),1),((v,w),1),((u,w),-1)]:
            if e in ix: M[ix[e]][j]=s
    factors=smith_diagonal(M)
    return len(chords)-len(factors),tuple(d for d in factors if d>1)
