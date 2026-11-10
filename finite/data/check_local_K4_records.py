"""Read-only check of the preserved restricted K4-free survivor records."""
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'certificates'))
from finite_checks import *
R=Path(__file__).resolve().parent
def counters(path):return {a:int(b) for a,b in (x.split('=') for x in path.read_text().split())}
def rank2(cols):
 piv={}
 for x in cols:
  while x:
   k=x.bit_length()-1
   if k in piv:x^=piv[k]
   else:piv[k]=x;break
 return len(piv)
def betti(A):
 es=cliques(A,2);ix={e:i for i,e in enumerate(es)};ts=cliques(A,3)
 r=rank2([sum(1<<ix[e] for e in __import__('itertools').combinations(t,2)) for t in ts]);c=components(A)
 return [c,len(es)-len(A)+c-r,len(ts)-r]
result=[]
for n in range(5,13):
 paths=[R/f'restricted_K4_records/cnt_{n}.txt'] if n<12 else [R/f'restricted_K4_records/cnt_12_{i}.txt' for i in range(8)]
 cs=[counters(p) for p in paths];count={k:sum(c[k] for c in cs) for k in cs[0]}
 lines=(R/f'restricted_K4_records/surv_{n}.g6').read_text().splitlines()
 if n==12:
  assert lines==sum([(R/f'restricted_K4_records/surv_12_{i}.g6').read_text().splitlines() for i in range(8)],[])
 assert len(lines)==count['after_euler'];hom=[]
 for s in lines:
  A=decode(s);assert len(A)==n and not cliques(A,4)
  assert all(not tree(induced(A,a)) for a in A)
  assert all((A[u]&A[v]).bit_count()!=1 for u,v in cliques(A,2))
  assert len(A)-len(cliques(A,2))+len(cliques(A,3))==1
  h=betti(A);assert h!=[1,0,0];hom.append(h)
 result.append({'order':n,**count,'Z2_acyclic_survivors':0,'survivor_stream_sha256':hashlib.sha256((R/f'restricted_K4_records/surv_{n}.g6').read_bytes()).hexdigest()})
assert result[-1]['total']==914568002
record=json.loads((B/'provenance/local_K4_restricted_records.json').read_text())
assert record['runs']==result
# Preserve the historical schema for comparison; name the coefficient field
# explicitly in the current report without modifying the retained source record.
reported=[]
for row in result:
 current=dict(row)
 current['F_2_acyclic_survivors']=current.pop('Z2_acyclic_survivors')
 reported.append(current)
print(json.dumps({'source_type':'preserved separate computation','scope':'counters, every preserved survivor, and local filter contract checked; generating large universes was not repeated','runs':reported},indent=2))
