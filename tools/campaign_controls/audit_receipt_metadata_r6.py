#!/usr/bin/env python3
"""Additional metadata checks. Read-only receipts; cooperative producers must be stopped."""
import sys
sys.dont_write_bytecode=True
import argparse,datetime,hashlib,json,math,pathlib,importlib.util
def check_receipt(d,r):
 if type(d.get('r')) is not int or d['r']!=r:raise ValueError('r must be an exact integer')
 for k in ('mod','worker_id','exit_geng','exit_classifier'):
  if type(d.get(k)) is not int:raise ValueError(k+' must be an exact integer')
 for k in ('exit_geng','exit_classifier'):
  if d[k]!=0:raise ValueError(k+' is not zero')
 duration=d.get('seconds')
 if type(duration) not in (int,float) or not math.isfinite(duration) or duration<0:raise ValueError('seconds must be finite and nonnegative')
 dates=[]
 for k in ('utc_start','utc_end'):
  s=d.get(k)
  if not isinstance(s,str):raise ValueError(k+' is not text')
  dt=datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
  if dt.tzinfo is None or dt.utcoffset()!=datetime.timedelta(0):raise ValueError(k+' must be UTC')
  dates.append(dt)
 if dates[1]<dates[0]:raise ValueError('UTC end precedes start')
 if not isinstance(d.get('host'),str) or not d['host'].strip():raise ValueError('empty host')
def scan(campaign):
 root=pathlib.Path(campaign).resolve()
 spec=importlib.util.spec_from_file_location('receipt_driver',root/'bin/campana_v2.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 cfg,ch=mod.load_config(root/'config.json')
 h=hashlib.sha256();count=0;seen=set()
 classes=mod.TABLE_CLASSES if cfg['mode']=='tabla' else ['ATASCADA']
 graphs={k:set() for k in classes}
 for p in sorted((root/'receipts').rglob('*.ok.json')):
  r=int(p.name.split('.')[0])
  if not 0<=r<cfg['mod'] or r in seen or p!=root/'receipts'/str(r//1000)/(str(r)+'.ok.json'):raise ValueError('invalid receipt membership')
  data=p.read_bytes();_counts,records,_memo=mod.validate_receipt(cfg,ch,r,mod.strict_json(data))
  for k,values in records.items():
   if graphs[k].intersection(values):raise ValueError('graph repeated across receipts')
   graphs[k].update(values)
  h.update(str(p.relative_to(root)).encode()+b'\0'+hashlib.sha256(data).digest())
  seen.add(r);count+=1
 if count!=cfg['mod']:raise ValueError('incomplete coverage')
 if cfg['mode']=='tabla' and graphs[classes[0]]&graphs[classes[1]]:raise ValueError('graph in two classes across receipts')
 expected={k+'.g6':hashlib.sha256(''.join(g+'\n' for g in sorted(values)).encode()).hexdigest() for k,values in graphs.items()}
 return {'PASS':True,'count':count,'expected_graph_sha256':expected,'receipt_manifest_sha256':h.hexdigest(),'limitation':'Metadata and content digest, not authentication; producers must be stopped.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--campaign',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 try:r=scan(a.campaign)
 except Exception as e:r={'PASS':False,'error':repr(e)}
 with pathlib.Path(a.out).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
 print(json.dumps(r));return 0 if r['PASS'] else 1
if __name__=='__main__':raise SystemExit(main())
