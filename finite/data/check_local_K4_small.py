"""Reproduce the small K4-free reduction check using an explicit generator."""
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
from pathlib import Path
import sys,json,subprocess,hashlib
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(B/'certificates'))
from finite_checks import *
import argparse
p=argparse.ArgumentParser(description='Re-enumerate connected K4-free graphs through order 8. Accepts any geng producing the recorded streams.');p.add_argument('--geng',required=True,type=Path);p.add_argument('--require-digest',action='store_true',help='Also require the original executable digest');args=p.parse_args()
geng=args.geng.resolve()
results=[]
for n in range(2,9):
 p=subprocess.run([str(geng),'-kc',str(n)],capture_output=True,check=True)
 retained=[]; total=0; candidates=0
 for s in p.stdout.decode().splitlines():
  A=decode(s);total+=1
  if any((A[u]&A[v]).bit_count()==1 for u,v in cliques(A,2)):continue
  admissible=[u for u,a in enumerate(A) if tree(induced(A,a))]
  if len(admissible)>1:continue
  candidates+=1; f=[len(A),len(cliques(A,2)),len(cliques(A,3))]
  if f[0]-f[1]+f[2]!=1:continue
  free,torsion=h1(A)
  if free==0 and all(d%2 for d in torsion): retained.append({'graph6':s,'admissible_vertices':admissible})
 results.append({'order':n,'connected_K4_free_graphs':total,'local_candidates':candidates,'almost_stuck':retained,'generator_stderr':p.stderr.decode().strip(),'stream_sha256':hashlib.sha256(p.stdout).hexdigest()})
 assert not retained
G=['L?qa``{wttym~o','L?qa`p{wttym~o','L?qahp{wttym~o']
report={'geng_sha256':hashlib.sha256(geng.read_bytes()).hexdigest(),'options':'-kc n','almost_stuck_definition':'order >= 2, Z2-acyclic, no admissible edge and at most one admissible vertex','local_criterion':'vertex link tree; edge common neighbourhood has one vertex','runs':results,'G13_variants':[{'graph6':s,'K4_count':len(cliques(decode(s),4)),'H1_free_and_torsion':h1(decode(s))} for s in G]}
assert all(x['K4_count']==0 for x in report['G13_variants'])
report=json.loads(json.dumps(report))
reference=json.loads((B/'provenance/local_K4_small_checks.json').read_text())
if args.require_digest: assert report['geng_sha256']==reference['geng_sha256']
assert len(report['runs'])==len(reference['runs'])==7
assert report['G13_variants']==reference['G13_variants']
for got,old in zip(report['runs'],reference['runs']):
 for key in ('order','connected_K4_free_graphs','local_candidates','almost_stuck','stream_sha256'):assert got[key]==old[key]
 for key in ('generator_stderr',):got.pop(key,None)
print(json.dumps(report,indent=2))
