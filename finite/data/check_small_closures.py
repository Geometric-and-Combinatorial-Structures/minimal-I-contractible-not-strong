"""Recompute the three finite pruned closures and check the eight K4-free graphs.

Python standard library only. Complete graph states are memoised. Isomorphism
uses joint colour refinement and an exact adjacency-preserving backtracking map.
Run without options to compare the deposited JSON, or --write to regenerate it.
"""
from pathlib import Path
from functools import lru_cache
from itertools import combinations
from collections import Counter,defaultdict
import argparse,csv,json
ROOT=Path(__file__).resolve().parent
SEEDS={'G14a':'M?b@bFHNEk@~|k}U?','G14b':'M?B@thku?~Lylk}[?','G14c':'M?r@d`ifbiFfo}~o?'}

def decode(s):
 n=ord(s[0])-63;bits=[(ord(c)-63>>j)&1 for c in s[1:] for j in range(5,-1,-1)];A=[0]*n
 for bit,(u,v) in zip(bits,((u,v) for v in range(1,n) for u in range(v))):
  if bit:A[u]|=1<<v;A[v]|=1<<u
 return tuple(A)
def encode(A):
 bits=[int(bool(A[u]>>v&1)) for v in range(1,len(A)) for u in range(v)]
 bits += [0]*((-len(bits))%6)
 return chr(63+len(A))+''.join(chr(63+sum(bits[i+j]<<(5-j) for j in range(6))) for i in range(0,len(bits),6))
def vertices(mask):return [i for i in range(mask.bit_length()) if mask>>i&1]
def induced(A,mask):
 vs=vertices(mask);return tuple(sum(1<<j for j,v in enumerate(vs) if A[u]>>v&1) for u in vs)
def edge(A,u,v,add):
 B=list(A)
 if add:B[u]|=1<<v;B[v]|=1<<u
 else:B[u]&=~(1<<v);B[v]&=~(1<<u)
 return tuple(B)
def cliques(A,k):return [c for c in combinations(range(len(A)),k) if all(A[u]>>v&1 for u,v in combinations(c,2))]
@lru_cache(None)
def strong(A):
 n=len(A)
 if not n:return False
 if n==1:return True
 full=(1<<n)-1
 if any(a==(full^(1<<u)) for u,a in enumerate(A)):return True
 seen=1
 while True:
  expanded=seen
  for u in vertices(seen):expanded|=A[u]
  if expanded==seen:break
  seen=expanded
 if seen!=full:return False
 for u in sorted(range(n),key=lambda u:A[u].bit_count()):
  if strong(induced(A,A[u])) and strong(induced(A,full^(1<<u))):return True
 for u,v in cliques(A,2):
  if strong(induced(A,A[u]&A[v])) and strong(edge(A,u,v,False)):return True
 return False

def colours(A,B):
 n=len(A);ca=[a.bit_count() for a in A];cb=[b.bit_count() for b in B]
 for _ in range(n):
  sa=[(ca[u],tuple(sorted(ca[v] for v in vertices(A[u])))) for u in range(n)]
  sb=[(cb[u],tuple(sorted(cb[v] for v in vertices(B[u])))) for u in range(n)]
  keys={s:i for i,s in enumerate(sorted(set(sa+sb)))};na=[keys[x] for x in sa];nb=[keys[x] for x in sb]
  if Counter(na)!=Counter(nb):return None
  if na==ca and nb==cb:break
  ca,cb=na,nb
 return ca,cb

def isomorphic(A,B):
 pair=colours(A,B)
 if pair is None:return False
 ca,cb=pair;mapping={};used=set();n=len(A)
 def visit():
  if len(mapping)==n:return True
  candidates=[]
  for u in range(n):
   if u in mapping:continue
   vs=[v for v in range(n) if v not in used and ca[u]==cb[v] and all(bool(A[u]>>x&1)==bool(B[v]>>y&1) for x,y in mapping.items())]
   if not vs:return False
   candidates.append((len(vs),u,vs))
  _,u,vs=min(candidates)
  for v in vs:
   mapping[u]=v;used.add(v)
   if visit():return True
   used.remove(v);del mapping[u]
  return False
 return visit()

def invariant(A):return tuple(sorted(a.bit_count() for a in A))
def closure(seed):
 start=decode(seed);states=[(start,False,[])];buckets=defaultdict(list);buckets[invariant(start)].append(0);cursor=0
 while cursor<len(states):
  A,is_strong,path=states[cursor];cursor+=1
  if is_strong:continue
  for u,v in combinations(range(len(A)),2):
   if A[u]>>v&1 or not strong(induced(A,A[u]&A[v])):continue
   B=edge(A,u,v,True);key=invariant(B)
   if any(isomorphic(B,states[i][0]) for i in buckets[key]):continue
   buckets[key].append(len(states));states.append((B,strong(B),path+[[u,v]]))
 return states

def compute():
 reports={};eight=[]
 for name,seed in SEEDS.items():
  states=closure(seed);reports[name]={'seed':seed,'non_strong':sum(not s for _,s,_ in states),'strong_boundary':sum(s for _,s,_ in states),'states':[{'graph6':encode(A),'strong':s,'added_edges':path} for A,s,path in states]}
  for A,s,path in states:
   if s or cliques(A,4):continue
   cert=None
   for u,v in combinations(range(len(A)),2):
    if not (A[u]>>v&1) and strong(induced(A,A[u]&A[v])) and strong(edge(A,u,v,True)):cert=[u,v];break
   assert cert is not None
   eight.append({'graph6':encode(A),'edges':len(cliques(A,2)),'seed':name,'added_edges':path,'certifying_edge':cert,'strong':False})
 expected={'G14a':(16,32),'G14b':(10,16),'G14c':(5,8)}
 assert all((r['non_strong'],r['strong_boundary'])==expected[n] for n,r in reports.items())
 assert len(eight)==8
 assert all(not isomorphic(decode(a['graph6']),decode(b['graph6'])) for a,b in combinations(eight,2))
 return {'closures':reports,'K4_free_I_not_IS':eight}

def check_deposited_tables(result):
 rows=list(csv.DictReader((ROOT/'K4_free_I_not_strong_14.tsv').open(),delimiter='\t'))
 assert len(rows)==8
 by_graph={r['graph6']:r for r in result['K4_free_I_not_IS']}
 for row in rows:
  record=by_graph[row['graph6']]
  assert int(row['edges'])==record['edges'] and row['seed']==record['seed']
  assert json.loads(row['added_edges'])==record['added_edges']
  assert json.loads(row['certifying_edge'])==record['certifying_edge'] and row['strong_I_contractible']=='no'
 d=json.loads((ROOT/'D15_published_triangles.json').read_text());labels=d['graph6_to_published']
 assert sorted(labels)==list(range(1,16))
 assert {tuple(sorted(labels[v] for v in t)) for t in cliques(decode(d['graph6']),3)}=={tuple(sorted(t)) for t in d['published_triangles']}
 assert {labels[v] for v in d['certificate_edge_graph6']}==set(d['certificate_edge_published'])=={5,7}
 mapping=list(csv.DictReader((ROOT/'D15_label_correspondence.tsv').open(),delimiter='\t'))
 assert [(int(r['graph6_vertex']),int(r['DEFH_Figure_2A_vertex'])) for r in mapping]==list(enumerate(labels))
 allrows=list(csv.DictReader((ROOT/'acyclic_not_strong_14_closure.tsv').open(),delimiter='\t'))
 assert len(allrows)==2271
 positives=[]
 for row in allrows:
  A=decode(row['seed_graph6'])
  for u,v in json.loads(row['added_edges']):
   assert not A[u]>>v&1 and strong(induced(A,A[u]&A[v]))
   A=edge(A,u,v,True)
  assert encode(A)==row['graph6']
  assert len(cliques(A,2))==int(row['edges']) and len(cliques(A,4))==int(row['K4_count'])
  if row['I_contractible']=='1':positives.append(row)
 assert len(positives)==29
 assert positives==list(csv.DictReader((ROOT/'I_not_strong_14_closure.tsv').open(),delimiter='\t'))
 assert {r['graph6'] for r in positives if r['K4_count']=='0'}==set(by_graph)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
 result=compute();target=ROOT/'small_closure_certificates.json'
 if args.write:target.write_text(json.dumps(result,indent=2)+'\n')
 else:
  if json.loads(target.read_text())!=result:parser.exit(1,'Deposited closure record differs.\n')
  check_deposited_tables(result)
 print(json.dumps({'closure_sizes':{n:[r['non_strong'],r['strong_boundary']] for n,r in result['closures'].items()},'K4_free_non_strong':len(result['K4_free_I_not_IS']),'all_eight_have_one_edge_certificates':True,'tables_and_addition_paths_checked':not args.write},indent=2))
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__=='__main__': main()
