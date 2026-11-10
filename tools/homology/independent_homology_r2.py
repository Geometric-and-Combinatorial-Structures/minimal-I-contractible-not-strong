#!/usr/bin/env python3
"""Auditor's independent graph6, integer SNF and certificate validation."""
import itertools,json,re,subprocess,sys,time,pathlib,random
BASE=pathlib.Path(__file__).resolve().parents[1]
REPO=BASE/'inputs/repo/minimal-I-contractible-not-strong'
BIN=BASE/'scratch/cleanroom'
def decode(s):
    n=ord(s[0])-63
    if not 0<=n<=16: raise ValueError(n)
    a=[set() for _ in range(n)];p=0
    for j in range(1,n):
        for i in range(j):
            if ((ord(s[1+p//6])-63)>>(5-p%6))&1:a[i].add(j);a[j].add(i)
            p+=1
    return a
def encode(a,vertices=None):
    v=sorted(range(len(a)) if vertices is None else vertices)
    bits=[int(v[j] in a[v[i]]) for j in range(1,len(v)) for i in range(j)]
    bits += [0]*((-len(bits))%6)
    return chr(len(v)+63)+''.join(chr(63+sum(bits[p+k]<<(5-k) for k in range(6))) for p in range(0,len(bits),6))
def lines(path):
    return [s.split()[0] for s in pathlib.Path(path).read_text().splitlines() if s and not s.startswith('#')]
def classify(gs,mode='classify'):
    p=subprocess.run([str(BIN),mode],input='\n'.join(gs)+'\n',text=True,capture_output=True,check=True)
    if mode=='classify':
        return [dict(zip(p.stdout.splitlines()[0].split('\t'),s.split('\t'))) for s in p.stdout.splitlines()[1:]]
    if mode=='strong':return [int(s.split('\t')[-1]) for s in p.stdout.splitlines()]
    return p.stdout
def smith_diagonal(mat,ncols=None):
    """Own integer Euclidean row/column reduction, with divisibility repair."""
    A=[list(map(int,row)) for row in mat];m=len(A);n=len(A[0]) if m else (ncols or 0)
    d=[];k=0
    while k<min(m,n):
        candidates=[(abs(A[i][j]),i,j) for i in range(k,m) for j in range(k,n) if A[i][j]]
        if not candidates:break
        _,i,j=min(candidates)
        A[k],A[i]=A[i],A[k]
        for row in A:row[k],row[j]=row[j],row[k]
        while True:
            changed=False
            for i in range(k+1,m):
                if A[i][k]:
                    q=A[i][k]//A[k][k]
                    A[i]=[x-q*y for x,y in zip(A[i],A[k])]
                    if A[i][k]:A[k],A[i]=A[i],A[k]
                    changed=True;break
            if changed:continue
            for j in range(k+1,n):
                if A[k][j]:
                    q=A[k][j]//A[k][k]
                    for i in range(m):A[i][j]-=q*A[i][k]
                    if A[k][j]:
                        for row in A:row[k],row[j]=row[j],row[k]
                    changed=True;break
            if changed:continue
            bad=next(((i,j) for i in range(k+1,m) for j in range(k+1,n) if A[i][j]%A[k][k]),None)
            if bad is None:break
            i,j=bad
            A[k]=[x+y for x,y in zip(A[k],A[i])]
        if A[k][k]<0:A[k]=[-x for x in A[k]]
        d.append(A[k][k]);k+=1
    assert all(b%a==0 for a,b in zip(d,d[1:]))
    return d
def integer_homology(s):
    a=decode(s);n=len(a)
    faces=[[] for _ in range(n)]
    for k in range(1,n+1):
        for v in itertools.combinations(range(n),k):
            if all(j in a[i] for i,j in itertools.combinations(v,2)):faces[k-1].append(v)
        if not faces[k-1]:break
    while faces and not faces[-1]:faces.pop()
    ds=[[]];ranks=[0];boundary=[None]
    for k in range(1,len(faces)):
        ix={v:i for i,v in enumerate(faces[k-1])}
        A=[[0]*len(faces[k]) for _ in faces[k-1]]
        for j,v in enumerate(faces[k]):
            for t in range(k+1):A[ix[v[:t]+v[t+1:]]][j]=(-1)**t
        if k>1:
            prev=boundary[-1]
            assert all(sum(prev[i][z]*A[z][j] for z in range(len(A)))==0 for i in range(len(prev)) for j in range(len(A[0])))
        d=smith_diagonal(A)
        ds.append(d);ranks.append(len(d));boundary.append(A)
    ds.append([]);ranks.append(0)
    h=[{'dimension':k,'free_rank':len(faces[k])-ranks[k]-ranks[k+1]-(k==0),'torsion':[x for x in ds[k+1] if x>1]} for k in range(len(faces))]
    return {'g6':s,'face_counts':[len(f) for f in faces],'reduced_homology':h,'boundary_smith':ds[1:-1]}
