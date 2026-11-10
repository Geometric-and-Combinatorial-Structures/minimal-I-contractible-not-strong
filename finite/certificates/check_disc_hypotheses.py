"""Exact finite checks of the five disc-unfolding certificates (Python stdlib).
Run from any directory. Compare the deposited JSON by default; --write regenerates it.
Only edge pairs of original triangle incidence two are glued.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter,defaultdict
import argparse, json, sys
GRAPHS={
'G13':'L?qa``{wttym~o',
'G14a':'M?b@bFHNEk@~|k}U?',
'G14b':'M?B@thku?~Lylk}[?',
'G14c':'M?r@d`ifbiFfo}~o?',
'D15':'N|thHsL`sHoI`RPOwLG'}
TARGET_WORDS={
'G13':[10,9,11,8]*3,
'G14a':[12,5,10,13,9,12,5,10,13,9,12,9,13,10,5],
'G14b':[13,7,5,8,13,7,5,8,13,9,13,8,5,7,13,9],
'G14c':[13,7,10,11,9,0,13,7,10,11,9,0,13,0,9,11,10,7],
'D15':[0,1,5,10,0,1,5,10,0,10,5,1]}
def decode(s):
 n=ord(s[0])-63;assert 0<n<63
 bits=[(ord(c)-63>>i)&1 for c in s[1:] for i in range(5,-1,-1)]
 return n,{(i,j) for bit,(i,j) in zip(bits,((i,j) for j in range(1,n) for i in range(j))) if bit}
def adjacency(vs,es):
 d={v:set() for v in vs}
 for a,b in es:d[a].add(b);d[b].add(a)
 return d
def connected(d):
 if not d:return False
 seen=set();todo=[next(iter(d))]
 while todo:
  v=todo.pop()
  if v not in seen:seen.add(v);todo.extend(d[v]-seen)
 return len(seen)==len(d)
def check(name,s):
 n,E=decode(s);T=[t for t in combinations(range(n),3) if all(e in E for e in combinations(t,2))]
 assert all(not all(e in E for e in combinations(t,2)) for t in combinations(range(n),4))
 inc=defaultdict(list)
 for i,t in enumerate(T):
  for e in combinations(t,2):inc[e].append(i)
 assert set(inc)==E
 parent={(i,v):(i,v) for i,t in enumerate(T) for v in t}
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 def union(a,b):parent[find(a)]=find(b)
 for e,ts in inc.items():
  if len(ts)==2:
   for v in e:union((ts[0],v),(ts[1],v))
 roots=sorted({find(c) for c in parent});ids={r:i for i,r in enumerate(roots)}
 faces=[tuple(ids[find((i,v))] for v in t) for i,t in enumerate(T)]
 labels={ids[r]:r[1] for r in roots}
 lifted=Counter(tuple(sorted(e)) for t in faces for e in combinations(t,2))
 assert len({tuple(sorted(t)) for t in faces})==len(T)
 assert all(len(set(t))==3 for t in faces)
 assert set(lifted.values())<= {1,2}
 boundary={e for e,c in lifted.items() if c==1};bdv=set(v for e in boundary for v in e)
 B=adjacency(bdv,boundary);D=adjacency(labels,lifted)
 assert connected(D) and connected(B) and all(len(z)==2 for z in B.values())
 linkrecords=[]
 for v in labels:
  le=[tuple(w for w in t if w!=v) for t in faces if v in t]
  lv={w for e in le for w in e};L=adjacency(lv,le)
  deg=sorted(map(len,L.values()));is_path=connected(L) and deg.count(1)==2 and all(d in(1,2) for d in deg)
  is_cycle=connected(L) and all(d==2 for d in deg)
  assert is_path if v in bdv else is_cycle
  linkrecords.append({'vertex':v,'original_label':labels[v],'type':'path' if v in bdv else 'cycle','vertices':sorted(lv),'edges':[list(e) for e in sorted(le)]})
 chi=len(labels)-len(lifted)+len(faces);assert chi==1
 fibres=defaultdict(list)
 for v,l in labels.items():fibres[l].append(v)
 assert all(len(fibres[labels[v]])==1 for v in labels if v not in bdv)
 edgefibres=defaultdict(list)
 for e in lifted:edgefibres[tuple(sorted(labels[v] for v in e))].append(e)
 for original,es in edgefibres.items():
  if len(inc[original])==2:assert len(es)==1 and lifted[es[0]]==2
  else:assert len(es)==len(inc[original]) and all(e in boundary for e in es)
 # Traversal chooses the smallest lifted vertex and then its smallest neighbour.
 cycle=[min(B)];previous=None
 while True:
  v=cycle[-1];w=min(B[v]-({previous} if previous is not None else set()))
  if w==cycle[0]:break
  cycle.append(w);previous=v
 assert len(cycle)==len(B)
 rawword=[labels[v] for v in cycle];target=TARGET_WORDS[name]
 assert any(w[i:]+w[:i]==target for w in (rawword,rawword[::-1]) for i in range(len(w)))
 singular={e for e in inc if len(inc[e])!=2};S=adjacency({v for e in singular for v in e},singular)
 assert connected(S) and len(singular)-len(S)+1==1
 # A spanning tree leaves one oriented edge; its signed traversal is the degree.
 seen={min(S)};todo=list(seen);tree=set()
 while todo:
  v=todo.pop()
  for w in sorted(S[v]):
   if w not in seen:seen.add(w);todo.append(w);tree.add(tuple(sorted((v,w))))
 chord,=singular-tree
 degree=sum(1 if (u,v)==chord else -1 if (v,u)==chord else 0 for u,v in zip(target,target[1:]+target[:1]))
 assert abs(degree)==(3 if name=='G13' else 1)
 return {'graph':name,'graph6':s,'f_vector':[len(labels),len(lifted),len(faces)],'euler_characteristic':chi,'connected':True,'boundary_components':1,'boundary_length':len(boundary),'interior_link_cycles':len(labels)-len(bdv),'boundary_link_paths':len(bdv),'interior_injective':True,'only_boundary_identifications':True,'boundary_word':target,'attaching_degree':degree,'singular_edges':sorted(singular),'lifted_vertex_labels':labels,'lifted_triangles':faces,'vertex_link_certificates':linkrecords}
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--write',action='store_true',help='explicitly replace the deposited certificate')
 parser.add_argument('--certificate',type=Path,default=Path(__file__).with_name('disc_hypotheses.json'))
 args=parser.parse_args()
 result=[check(n,s) for n,s in GRAPHS.items()]
 # Round-trip normalises tuple/list and integer/string dictionary keys.
 canonical=json.loads(json.dumps(result))
 if args.write:
  args.certificate.write_text(json.dumps(canonical,indent=2)+'\n')
 else:
  try: supplied=json.loads(args.certificate.read_text())
  except (OSError,ValueError) as error: parser.exit(1,'Certificate cannot be read: '+str(error)+'\n')
  if supplied!=canonical: parser.exit(1,'Certificate differs from the reconstructed disc data.\n')
 for r in result: print(r['graph'],r['f_vector'],'chi',r['euler_characteristic'],'boundary',r['boundary_length'])
 print('All five disc hypotheses and deposited records verified.')
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__=='__main__': main()
