#!/usr/bin/env python3
"""Control independiente de F4 (R6-F4, n=14, mod 2000000, modo tabla), 6-nov-2026.
Entradas: evidencia de F4 copiada de YUCA, evidencia de F1 n14 (tar de F1), valores provisionales
de INSUMOS/FILA14_PROVISIONAL_2026-11-02 y la tabla eight_K4_free.tex del suplemento del borrador 4.
1) Cotejo de las doce columnas con F1 n14 y con los provisionales; valores derivados.
2) I_NO_IS: comparacion por isomorfismo (networkx) con la tabla del suplemento y con F1 n14; K4-libre y m.
3) ACICLICA_NO_IS_INDECISA: igualdad literal con F1 n14 y con las adjudicaciones de F4.
4) Homologia propia de las 625: Betti reducidos sobre F2,F3,F5,F7 (eliminacion propia) y homologia entera
   por forma normal de Smith (sympy); comparacion con el adjudicador de F4. No usa ripser ni scripts de Astra."""
import json,os,sys,hashlib,collections,time,re,itertools
import numpy as np, sympy, networkx as nx
from sympy import Matrix, ZZ
from sympy.matrices.normalforms import smith_normal_form
E,F1,PROV,TEX=sys.argv[1:5]
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
def g6_decode(s):
    b=[ord(ch)-63 for ch in s]; n=b[0]; assert n<63
    bits=[]
    for x in b[1:]: bits+=[(x>>k)&1 for k in range(5,-1,-1)]
    adj=[[0]*n for _ in range(n)]; k=0
    for j in range(1,n):
        for i in range(j):
            if bits[k]: adj[i][j]=adj[j][i]=1
            k+=1
    return n,adj
def G(s):
    n,adj=g6_decode(s); g=nx.Graph(); g.add_nodes_from(range(n))
    g.add_edges_from((i,j) for i in range(n) for j in range(i+1,n) if adj[i][j]); return g
def cliques(n,adj):
    out=[[(v,) for v in range(n)]]
    while out[-1]:
        nxt=[]
        for c in out[-1]:
            for v in range(c[-1]+1,n):
                if all(adj[u][v] for u in c): nxt.append(c+(v,))
        out.append(nxt)
    return out[:-1]
def boundary(faces,d):
    idx={f:i for i,f in enumerate(faces[d-1])}
    M=np.zeros((len(faces[d-1]),len(faces[d])),dtype=np.int64)
    for j,f in enumerate(faces[d]):
        for k in range(len(f)): M[idx[f[:k]+f[k+1:]],j]=(-1)**k
    return M
def rank_mod(M,p):
    A=(M%p).astype(np.int64).copy(); r=0; rows,cols=A.shape
    for c in range(cols):
        piv=None
        for i in range(r,rows):
            if A[i,c]%p: piv=i;break
        if piv is None: continue
        A[[r,piv]]=A[[piv,r]]; inv=pow(int(A[r,c]),-1,p); A[r]=(A[r]*inv)%p
        for i in range(rows):
            if i!=r and A[i,c]%p: A[i]=(A[i]-A[i,c]*A[r])%p
        r+=1
        if r==rows: break
    return r
def reduced_betti(faces,p):
    dims=len(faces); f=[1]+[len(x) for x in faces]; ranks=[1]
    for d in range(1,dims): ranks.append(rank_mod(boundary(faces,d),p))
    ranks.append(0)
    return [f[i+1]-ranks[i]-ranks[i+1] for i in range(dims)]
def integral_hom(faces):
    dims=len(faces); snf=[]
    for d in range(1,dims):
        S=smith_normal_form(Matrix(boundary(faces,d).tolist()),domain=ZZ)
        snf.append([abs(S[i,i]) for i in range(min(S.shape)) if S[i,i]!=0])
    res=[]
    for d in range(dims):
        nd=len(faces[d]); rk_out=1 if d==0 else len(snf[d-1]); rk_in=len(snf[d]) if d<dims-1 else 0
        tors=[int(x) for x in (snf[d] if d<dims-1 else []) if x>1]
        res.append((nd-rk_out-rk_in,sorted(tors)))
    return res
t0=time.time(); bad=0
print('sympy',sympy.__version__,'numpy',np.__version__,'networkx',nx.__version__)
# 1) doce columnas
agg=json.load(open(f'{E}/main/campaign/aggregate.json')); C=agg['counts']
f1p=f'{F1}/n14/n14_final_raw_counts.json'; f1=json.load(open(f1p)); f1c=f1.get('counts',f1)
pv=json.load(open(f'{PROV}/n14_final_raw_counts.json')); pvc=pv.get('counts',pv)
print('aggregate.json sha256',sha(f'{E}/main/campaign/aggregate.json'))
print('F1 n14_final_raw_counts.json sha256',sha(f1p)); print('provisional n14_final_raw_counts.json sha256',sha(f'{PROV}/n14_final_raw_counts.json'))
keys=['conexas','chi1','aciclicas','I','I_indecisas','I_S','I_SV','3-Dis','2-Dis','1-Dis','0-Dis','-1-Dis']
assert sorted(keys)==sorted(C.keys()), (sorted(C), keys)
rows=[]
for k in keys:
    ok=(C[k]==f1c.get(k)==pvc.get(k)); bad+= not ok
    rows.append((k,C[k],f1c.get(k),pvc.get(k),'igual' if ok else 'DISTINTO'))
open(f'{E}/../f4_out/cotejo_F4_vs_F1_n14_y_provisionales.tsv','w').write('columna\tF4\tF1_n14\tprovisional\testado\n'+''.join('\t'.join(map(str,r))+'\n' for r in rows))
print('12 columnas F4 = F1 n14 = provisional:', sum(r[4]=='igual' for r in rows),'/12')
der={'I-I_S':C['I']-C['I_S'],'aciclicas-I':C['aciclicas']-C['I'],'I_S-I_SV':C['I_S']-C['I_SV'],'2-Dis-1-Dis':C['2-Dis']-C['1-Dis'],
     'chi1-aciclicas':C['chi1']-C['aciclicas'],'aciclicas-I_S':C['aciclicas']-C['I_S'],'conos':C['-1-Dis']}
print('derivados',der)
chain=[C[k] for k in ['conexas','chi1','aciclicas','I','I_S','I_SV','3-Dis','2-Dis','1-Dis','0-Dis','-1-Dis']]
print('cadena monotona:', all(a>=b for a,b in zip(chain,chain[1:])))
crit={'conos=20797002':C['-1-Dis']==20797002,'I-I_S=8':der['I-I_S']==8,'aciclicas-I=I_indecisas=625':der['aciclicas-I']==C['I_indecisas']==625}
print('criterios numericos',crit); bad+=sum(not v for v in crit.values())
# 2) I_NO_IS
nois=[l.strip() for l in open(f'{E}/main/campaign/I_NO_IS.g6') if l.strip()]
tex=open(TEX).read()
cells=re.findall(r'\\texttt\{(.*?)\}\s*&\s*(\d+)\s*&',tex)
def unesc(s): return s.replace('\\textasciitilde{}','~').replace('\\textasciigrave{}','`').replace('\\}','}').replace('\\{','{').replace('\\textbackslash{}','\\\\'[0]).replace('\\_','_')
S3=[(unesc(s),int(m)) for s,m in cells]
print('tabla suplemento: filas',len(S3),'sha256 tex',sha(TEX))
GN=[G(s) for s in nois]; GS=[G(s) for s,_ in S3]
M=[[nx.is_isomorphic(a,b) for b in GS] for a in GN]
perm=[[j for j in range(len(GS)) if M[i][j]] for i in range(len(GN))]
bij = len(GN)==len(GS)==8 and all(len(p)==1 for p in perm) and len({p[0] for p in perm})==8
print('I_NO_IS vs tabla (isomorfismo): biyeccion', bij)
for i,s in enumerate(nois):
    j=perm[i][0] if perm[i] else None
    k4=any(all(GN[i].has_edge(a,b) for a,b in itertools.combinations(q,2)) for q in itertools.combinations(range(14),4))
    print(f'   F4[{i}] m={GN[i].number_of_edges()} K4={k4} -> tabla fila {j} (m tabla={S3[j][1] if j is not None else None})')
    bad+= (j is None) or k4 or GN[i].number_of_edges()!=S3[j][1]
bad+= not bij
gs=[l.rstrip('\n').split('\t') for l in open(f'{F1}/n14/graph_slices.tsv') if l.strip()]
f1nois=sorted(x[2] for x in gs if x[1]=='I_NO_IS'); f1aci=sorted(x[2] for x in gs if x[1]=='ACICLICA_NO_IS_INDECISA')
print('F1 graph_slices: I_NO_IS',len(f1nois),'ACICLICA',len(f1aci), 'tipos',dict(collections.Counter(x[1] for x in gs)))
print('I_NO_IS F4 = F1 (literal, como conjunto):', sorted(nois)==f1nois); bad+= sorted(nois)!=f1nois
# 3) ACICLICA
aci=[l.rstrip('\n') for l in open(f'{E}/main/campaign/ACICLICA_NO_IS_INDECISA.g6') if l.strip()]
adj=[json.loads(l) for l in open(f'{E}/homology_adjudications.jsonl')]
print('ACICLICA F4',len(aci),'distintas',len(set(aci)),'= F1 (literal):',sorted(aci)==f1aci,'| = adjudicaciones F4:',sorted(aci)==sorted(x['g6'] for x in adj))
bad+= sorted(aci)!=f1aci or sorted(aci)!=sorted(x['g6'] for x in adj)
f1adj={json.loads(l)['g6']:json.loads(l) for l in open(f'{F1}/n14_homology/adjudications.jsonl')}
same_dec=sum(f1adj.get(x['g6'],{}).get('decision')==x['decision'] and f1adj[x['g6']]['integer_homology']['reduced_homology']==x['integer_homology']['reduced_homology'] for x in adj)
print('adjudicaciones F4 iguales a F1 n14 (decision y homologia entera):',same_dec,'/',len(adj)); bad+= same_dec!=len(adj)
# 4) homologia propia
cnt=collections.Counter(); mism=0; fc=0; dec=collections.Counter()
for x in adj:
    nn,A=g6_decode(x['g6']); assert nn==14
    faces=cliques(nn,A)
    b={p:tuple(reduced_betti(faces,p)) for p in (2,3,5,7)}
    ih=integral_hom(faces)
    cnt[(b[2],b[3],b[5],b[7],tuple((f,tuple(t)) for f,t in ih))]+=1
    ak=tuple((h['free_rank'],tuple(h['torsion'])) for h in x['integer_homology']['reduced_homology'])
    mism+= ak!=tuple((f,tuple(t)) for f,t in ih); fc+= x['integer_homology']['face_counts']!=[len(fs) for fs in faces]
    dec[x['decision']]+=1
print(f'homologia propia: {len(adj)} graficas | decision F4: {dict(dec)} | desacuerdos homologia entera: {mism} | caras: {fc}')
for k,v in cnt.items(): print(f'   {v}: b(F2)={k[0]} b(F3)={k[1]} b(F5)={k[2]} b(F7)={k[3]} H~ entera (rango libre, torsion)={k[4]}')
bad+=mism+fc
print(f'segundos {time.time()-t0:.1f}'); print('RESULTADO:', 'CONCUERDA' if bad==0 else f'DISCREPA ({bad})')
