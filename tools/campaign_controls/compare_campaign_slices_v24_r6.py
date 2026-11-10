#!/usr/bin/env python3
"""Compare ALL historical selected residues with fresh v2.4 driver receipts (classifier v2.2).
Read only inputs. One JSON result file; exit nonzero on any discrepancy.
The historical manifest must come from a PASS, stable inventory R2.
"""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,pathlib,sys
KEYS={'conexas','chi1','aciclicas','I','I_indecisas','I_S','I_SV','3-Dis','2-Dis','1-Dis','0-Dis','-1-Dis'}
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def compare(campaign,history,driver):
 campaign=campaign.resolve();history=history.resolve();driver=driver.resolve()
 spec=importlib.util.spec_from_file_location('exact_driver',driver);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 cfg,ch=mod.load_config(campaign/'config.json'); locks=mod._hold_worker_locks(cfg)
 if cfg['mode']!='tabla':raise ValueError('requires tabla mode')
 inventory=json.loads((history/'summary.json').read_text()); manifest=history/'selected_slices.jsonl';mh=sha(manifest)
 frozen={p:sha(p) for p in (driver,campaign/'config.json',campaign/'aggregate.json',history/'summary.json')}
 if inventory.get('n')!=cfg['n'] or inventory.get('mod')!=cfg['mod']:raise ValueError('inventory partition mismatch')
 if inventory.get('PASS') is not True or inventory.get('schema')!='yuca_integrity_inventory_r2/1' or inventory['selected_slices_sha256']!=mh:raise ValueError('not a valid R2 inventory')
 if inventory['counted']!=cfg['mod'] or inventory.get('missing') not in (0,[]) or inventory.get('errors')!=0:raise ValueError('incomplete or failed inventory')
 # Recheck receipt membership instead of trusting an aggregate left from an earlier run.
 fresh_seen=bytearray(cfg['mod']);fresh_count=0
 for p in (campaign/'receipts').rglob('*.ok.json'):
  r=int(p.name.split('.')[0])
  if not 0<=r<cfg['mod'] or fresh_seen[r] or p!=mod.receipt_path(cfg,r):raise ValueError('duplicate, unexpected or misplaced fresh receipt')
  fresh_seen[r]=1;fresh_count+=1
 if fresh_count!=cfg['mod']:raise ValueError('incomplete fresh receipt coverage')
 found={'I_NO_IS':set(),'ACICLICA_NO_IS_INDECISA':set()}
 seen=bytearray(cfg['mod']);sums={k:0 for k in KEYS};discrepancies=[];nrows=0;oldtotals={k:0 for k in KEYS};mismatches=0
 with manifest.open() as f:
  for line in f:
   old=json.loads(line);r=old['r']
   if type(r) is not int or not 0<=r<cfg['mod'] or seen[r]:raise ValueError('duplicate or out-of-range residue')
   if old['n']!=cfg['n'] or old['mod']!=cfg['mod']:raise ValueError('different partition')
   c=old['counts']
   if set(c)!=KEYS or any(type(x) is not int or x<0 for x in c.values()):raise ValueError('invalid historical counts')
   seen[r]=1;nrows+=1;receipt=mod.strict_json(mod.receipt_path(cfg,r).read_text());new,records,_memo=mod.validate_receipt(cfg,ch,r,receipt)
   if set(new)!=KEYS or any(type(x) is not int or x<0 for x in new.values()):raise ValueError('invalid fresh counts')
   if set(old['records'])!=set(found) or any(not isinstance(v,list) or any(not isinstance(g,str) for g in v) for v in old['records'].values()):raise ValueError('invalid historical record categories')
   for k,gs in records.items():
    if found[k].intersection(gs):raise ValueError('duplicate graph across fresh residues')
    found[k].update(gs)
   bad={k:{'historical':c[k],'fresh':new[k]} for k in sorted(KEYS) if c[k]!=new[k]}
   badres={k: {'historical':sorted(old['records'][k]),'fresh':sorted(v)} for k,v in records.items() if sorted(old['records'][k])!=sorted(v)}
   if bad or badres:
    mismatches+=1
    if len(discrepancies)<100:discrepancies.append({'r':r,'counts':bad,'records':badres})
   for k in KEYS:sums[k]+=new[k];oldtotals[k]+=c[k]
 if nrows!=cfg['mod'] or not all(seen):raise ValueError('missing historical residue')
 aggregate=mod.strict_json((campaign/'aggregate.json').read_text())
 if aggregate.get('ok') is not True:raise ValueError('aggregate not successful')
 if aggregate['counts']!=sums or aggregate['coverage']!=cfg['mod'] or aggregate.get('mod')!=cfg['mod'] or aggregate.get('config_sha256')!=ch:raise ValueError('fresh aggregate mismatch')
 if found['I_NO_IS']&found['ACICLICA_NO_IS_INDECISA']:raise ValueError('contradictory fresh classes')
 if inventory['totals']!=oldtotals:raise ValueError('inventory totals disagree with manifest')
 # A change in any column matters; compare all 12 raw counters, including undecided.
 if sums!=inventory['totals'] and mismatches==0:raise ValueError('historical totals disagree with rows')
 if sha(manifest)!=mh:raise ValueError('historical manifest changed during comparison')
 _,final_ch=mod.load_config(campaign/'config.json')
 if final_ch!=ch or any(sha(p)!=h for p,h in frozen.items()):raise ValueError('input or driver changed during comparison')
 return {'PASS':mismatches==0,'mismatched_residues':mismatches,'n':cfg['n'],'mod':cfg['mod'],'compared':nrows,'columns':sorted(KEYS),'historical_manifest_sha256':mh,'config_sha256':ch,'driver_sha256':sha(driver),'counts':sums,'discrepancies':discrepancies}
def main():
 p=argparse.ArgumentParser();p.add_argument('--campaign',type=pathlib.Path,required=True);p.add_argument('--history',type=pathlib.Path,required=True);p.add_argument('--driver',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
 try:r=compare(a.campaign,a.history,a.driver)
 except Exception as e:r={'PASS':False,'error':repr(e)}
 with a.out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in r.items() if k!='discrepancies'}));return 0 if r['PASS'] else 1
if __name__=='__main__':sys.exit(main())
