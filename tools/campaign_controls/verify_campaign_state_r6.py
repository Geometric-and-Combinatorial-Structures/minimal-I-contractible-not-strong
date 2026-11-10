#!/usr/bin/env python3
"""Read-only checks for the fixed v2.4 campaign and its final aggregation attempt."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,pathlib
SOURCE_SHA='bd18224f907971e298a3997fad156628ed0f4aca0737beec3e7c900599782e8a'
DRIVER_SHA='d417c200bb4a9e7d8274899332f44a7a9890003310f1bc6d8b7d5b640cd362a3'
KEYS=['conexas','chi1','aciclicas','I','I_indecisas','I_S','I_SV','3-Dis','2-Dis','1-Dis','0-Dis','-1-Dis']
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def state(run):
 run=pathlib.Path(run).resolve();root=run/'campaign';driver=root/'bin/campana_v2.py'
 require((run/'init.exit').read_text().strip()=='0','init.exit is not zero')
 require(sha(driver)==DRIVER_SHA,'wrong v2.4 driver')
 spec=importlib.util.spec_from_file_location('audited_v24_driver',driver)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 cfg,ch=mod.load_config(root/'config.json')
 plan=mod.strict_json((run/'plan.json').read_text())
 require(cfg['files']['source']['sha256']==SOURCE_SHA,'wrong C source')
 for k in ('n','mod','mode','workers'):require(cfg[k]==plan[k],'plan/config mismatch: '+k)
 require(cfg['classifier_summary_version']=='v2.2','not classifier v2.2')
 mark=mod.strict_json((root/'INIT_COMPLETE.json').read_text())
 require(mark['config_sha256']==ch,'INIT_COMPLETE mismatch')
 return mod,cfg,ch,plan
def validate_attempt(run,argv,previous):
 run=pathlib.Path(run).resolve();mod,cfg,ch,plan=state(run);root=run/'campaign'
 data=mod.strict_json((root/'aggregate.json').read_text());ident=data.get('attempt_id')
 require(isinstance(ident,str) and ident and pathlib.Path(ident).name==ident,'unsafe/missing attempt_id')
 current={p.name for p in (root/'aggregate_attempts').glob('*.json')}
 require(current-set(previous)=={ident+'.json'},'aggregation attempt is stale, absent, or concurrent')
 p=root/'aggregate_attempts'/(ident+'.json');record=mod.strict_json(p.read_text())
 require(record.get('attempt_id')==ident and record.get('status')=='ok' and record.get('problems')==[],'attempt record not terminal ok')
 require(record.get('argv')==argv,'attempt argv is not this invocation')
 require(record.get('config_sha256')==ch==data.get('config_sha256'),'attempt/config hash mismatch')
 require(record.get('references')==data.get('references'),'reference records disagree')
 require(record.get('aggregate_sha256')==sha(root/'aggregate.json'),'terminal aggregate_sha256 does not match exact published bytes')
 require(mod.parse_utc(record['utc_end'])>=mod.parse_utc(record['utc_start']),'attempt time reversed')
 require(data.get('ok') is True and data.get('problems')==[] and data.get('coverage')==plan['mod'],'aggregate incomplete or failed')
 for k in ('n','mod','mode'):require(data.get(k)==plan[k],'aggregate plan mismatch: '+k)
 if plan['mode']=='tabla':
  raw=mod.strict_json((run/'input/raw_counts.json').read_text())
  require(set(data['comparison'])==set(KEYS) and data['counts']==raw,'all 12 raw counters must agree')
  require(all(v.get('equal') is True and v.get('actual')==raw[k]==v.get('expected') for k,v in data['comparison'].items()),'raw comparison failed')
  refs=[dict(kind='csv',path=str((run/'input/raw_table.csv').resolve()),sha256=sha(run/'input/raw_table.csv'),row_n=plan['n'])]
  wanted=set(KEYS)
 else:
  require(data['counts']['encontradas']==51,'F3 must find 51')
  require(data['comparison']['ATASCADA_set']['equal'] is True,'canonical reference does not match')
  require(data['comparison']['ATASCADA_set']['actual']==51==data['comparison']['ATASCADA_set']['expected'],'canonical comparison cardinality')
  refs=[dict(kind='graph6',path=str((run/'input/reference51.g6').resolve()),sha256=sha(run/'input/reference51.g6'),graphs=51),dict(kind='labelg',path=str((run/'input/labelg').resolve()),sha256=sha(run/'input/labelg'),frozen_copy=str(root/'aggregate_attempts'/(ident+'.tools')/'labelg'),expected_sha256=sha(run/'input/labelg'))]
  tools=root/'aggregate_attempts'/(ident+'.tools');tool=tools/'labelg'
  require(tools.is_dir() and not tools.is_symlink() and (tools.stat().st_mode&0o777)==0o700,'attempt tools directory is not private')
  require(tool.is_file() and not tool.is_symlink() and (tool.stat().st_mode&0o777)==0o500,'frozen labelg is not a regular read-only executable')
  require(sha(tool)==sha(run/'input/labelg'),'frozen labelg differs from approved campaign copy')
  wanted={'ATASCADA_set','encontradas'}
 require(data['references']==refs,'references do not match the frozen campaign')
 require(set(data['requested_comparisons'])==wanted,'missing/unexpected requested comparison')
 return data,record,p
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
 m,c,h,plan=state(a.run)
 print(json.dumps({'PASS':True,'config_sha256':h,'phase':plan['phase'],'INIT_COMPLETE':True}))
