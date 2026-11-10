#!/usr/bin/env python3
"""Independent adjudication of every raw undecided graph; never changes raw counts.
Input is a PASS historical inventory OR an already validated/aggregated campaign.
This does not replace receipt validation, per-slice comparison or campaign completeness.
Writes a NEW output directory, outside its input directory; integer homology in all
dimensions, and Ripser over F2/F3 through dimension2 at graph flag-complex threshold1.
"""
import argparse,hashlib,importlib.util,json,sys,time,platform
from pathlib import Path
KEYS=['conexas','chi1','aciclicas','I','I_indecisas','I_S','I_SV','3-Dis','2-Dis','1-Dis','0-Dis','-1-Dis']
CHAIN=['-1-Dis','0-Dis','1-Dis','2-Dis','3-Dis','I_SV','I_S','I','aciclicas','chi1','conexas']
CLASSES=['I_NO_IS','ACICLICA_NO_IS_INDECISA']
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def valid(s,n):
 if not 1<=n<=16 or not s or ord(s[0])-63!=n:return False
 bits=n*(n-1)//2
 return len(s)==1+(bits+5)//6 and all(63<=ord(c)<=126 for c in s[1:]) and (not bits%6 or not((ord(s[-1])-63)&((1<<(6-bits%6))-1)))
def uct(h,p,dimension):
 by={x['dimension']:x for x in h}
 def torsion(i):return sum(t%p==0 for t in by.get(i,{}).get('torsion',[]))
 return [by.get(k,{}).get('free_rank',0)+torsion(k)+torsion(k-1) for k in range(dimension+1)]
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 group=ap.add_mutually_exclusive_group(required=True)
 group.add_argument('--inventory');group.add_argument('--campaign')
 ap.add_argument('--independent',required=True);ap.add_argument('--out',required=True)
 a=ap.parse_args();src=Path(a.inventory or a.campaign).resolve();out=Path(a.out).resolve()
 if out==src or src in out.parents:raise SystemExit('out must be a new directory outside the input directory')
 out.mkdir(parents=True,exist_ok=False);t0=time.monotonic();hashes={};errors=[]
 def read(p):
  p=Path(p);data=p.read_bytes();hashes[str(p)]=hashlib.sha256(data).hexdigest();return data.decode()
 def load(p):return json.loads(read(p))
 records={k:[] for k in CLASSES}
 try:
  if a.inventory:
   summary=load(src/'summary.json')
   if summary.get('PASS') is not True:raise ValueError('inventory is not PASS')
   n=summary['n'];mod=summary['mod'];counts=summary['totals']
   if summary.get('counted')!=mod or summary.get('unique_registered')!=mod or summary.get('missing')!=0 or summary.get('errors')!=0:raise ValueError('inventory coverage invalid')
   for line in read(src/'graph_slices.tsv').splitlines():
    row=line.split('\t')
    if len(row)!=3 or row[1] not in records or not 0<=int(row[0])<mod:raise ValueError('invalid graph_slices.tsv row')
    records[row[1]].append(row[2])
   source_kind='historical_inventory'
  else:
   cfg=load(src/'config.json');summary=load(src/'aggregate.json')
   n=cfg['n'];mod=cfg['mod'];counts=summary['counts']
   if summary.get('coverage')!=mod or summary.get('mod')!=mod:raise ValueError('campaign coverage invalid')
   if summary.get('config_sha256')!=hashlib.sha256(canonical(cfg)).hexdigest():raise ValueError('campaign/config hash mismatch')
   if 'ok' in summary and summary['ok'] is not True:raise ValueError('aggregate not ok')
   if 'all_comparisons_equal' in summary and summary['all_comparisons_equal'] is not True:raise ValueError('aggregate comparison failed')
   if 'ok' not in summary and 'all_comparisons_equal' not in summary:raise ValueError('unknown aggregate success schema')
   for k in CLASSES:
    lines=read(src/(k+'.g6')).splitlines()
    if any(not s or s.strip()!=s for s in lines):raise ValueError('blank/whitespace result record')
    records[k]=lines
    if 'found' in summary and summary['found'].get(k)!=sorted(lines):raise ValueError('aggregate found differs from file')
    if 'found_counts' in summary and summary['found_counts'].get(k)!=len(lines):raise ValueError('aggregate found_counts differs from file')
   source_kind='exact_campaign'
  if set(counts)!=set(KEYS) or any(type(v) is not int or v<0 for v in counts.values()):raise ValueError('invalid raw counters')
  if any(counts[x]>counts[y] for x,y in zip(CHAIN,CHAIN[1:])) or counts['aciclicas']!=counts['I']+counts['I_indecisas']:raise ValueError('raw counter invariants')
  if len(records['I_NO_IS'])!=counts['I']-counts['I_S'] or len(records['ACICLICA_NO_IS_INDECISA'])!=counts['I_indecisas']:raise ValueError('raw record counts mismatch')
  allgraphs=sum(records.values(),[])
  if len(allgraphs)!=len(set(allgraphs)) or any(not valid(g,n) for g in allgraphs):raise ValueError('duplicate/invalid graph6')
  independent=Path(a.independent).resolve();hashes[str(independent)]=digest(independent)
  spec=importlib.util.spec_from_file_location('independent_homology',independent)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  import numpy as np
  import ripser as ripser_module
  from ripser import ripser
  completed=0;passed=0
  with (out/'adjudications.jsonl').open('x') as stream:
   for graph in records['ACICLICA_NO_IS_INDECISA']:
    tg=time.monotonic();result={'g6':graph,'n':n}
    try:
     h=module.integer_homology(graph);result['integer_homology']=h
     reduced=h['reduced_homology'];full_dimension=max(2,len(reduced))
     expected2=uct(reduced,2,full_dimension);expected3=uct(reduced,3,full_dimension)
     nontrivial=any(x['free_rank'] or x['torsion'] for x in reduced)
     adjacency=module.decode(graph);dist=np.full((n,n),2,dtype=np.float64);np.fill_diagonal(dist,0)
     for i,row in enumerate(adjacency):
      for j in row:dist[i,j]=1
     bettis={}
     for prime in (2,3):
      persistence=ripser(dist,distance_matrix=True,maxdim=2,thresh=1,coeff=prime)['dgms']
      bettis[prime]=[int(sum(float(b)<=1 and float(e)>1 for b,e in dgm))-(k==0) for k,dgm in enumerate(persistence)]
     result.update(uct_mod2=expected2,uct_mod3=expected3,ripser_reduced_mod2=bettis[2],ripser_reduced_mod3=bettis[3],
      nontrivial_integer_homology=nontrivial,compatible_mod2_acyclic=not any(expected2),
      ripser_uct_match=bettis[2]==expected2[:3] and bettis[3]==expected3[:3])
     result['PASS']=nontrivial and not any(expected2) and result['ripser_uct_match']
     result['decision']='NO_I_POR_HOMOLOGIA_ENTERA' if result['PASS'] else 'NO_RESUELTA_O_INCONSISTENTE'
    except Exception as e:result.update(PASS=False,error=repr(e),decision='NO_EVALUADA')
    completed+=1;passed+=bool(result['PASS']);result['seconds']=time.monotonic()-tg
    stream.write(json.dumps(result,sort_keys=True)+'\n');stream.flush()
    if not result['PASS']:errors.append({'g6':graph,'kind':'homology_criterion_failed'})
    if completed%10==0:print('adjudicated',completed,'passed',passed,flush=True)
  for path,original in hashes.items():
   if digest(path)!=original:errors.append({'kind':'input_changed','path':path})
  final={'schema':'adjudicate_inventory_r2/1','source':str(src),'source_kind':source_kind,'n':n,'mod':mod,'raw_counts':counts,
    'raw_undecided':counts['I_indecisas'],'processed':completed,'certified_non_I':passed,'positive_records_unchanged':len(records['I_NO_IS']),
    'errors':errors,'PASS':not errors and completed==counts['I_indecisas'],'seconds':time.monotonic()-t0,
    'input_sha256':hashes,'versions':{'python':platform.python_version(),'numpy':np.__version__,'ripser':ripser_module.__version__},
    'method':'Integral reduced homology via independent Smith normal form; UCT beta_i(Fp)=rankHi + p-torsion summands Hi + p-torsion summands H(i-1). Ripser F2,F3 at threshold1 with edge distance1/nonedge2, maxdim2. Require integral nontriviality and F2-acyclicity in every dimension.',
    'limitation':'Does not prove source campaign completeness, receipt authenticity, positive I certificates, or independent F3 Betti numbers above dimension2. Raw counters are never adjusted.'}
  (out/'raw_counts_unchanged.json').write_text(json.dumps(counts,indent=2)+'\n')
 except Exception as e:
  final={'schema':'adjudicate_inventory_r2/1','PASS':False,'errors':[{'kind':'input_or_setup_error','error':repr(e)}],'seconds':time.monotonic()-t0,'input_sha256':hashes}
 (out/'summary.json').write_text(json.dumps(final,indent=2)+'\n');print(json.dumps(final,indent=2))
 raise SystemExit(0 if final['PASS'] else 1)
if __name__=='__main__':main()
