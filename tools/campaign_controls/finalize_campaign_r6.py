#!/usr/bin/env python3
"""Run v2.4 aggregate once; require its NEW terminal attempt and all frozen comparisons."""
import sys
sys.dont_write_bytecode=True
import argparse,datetime,fcntl,json,pathlib,subprocess
from verify_campaign_state_r6 import sha,state,validate_attempt,KEYS
def main():
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 run=pathlib.Path(a.run).resolve();out=pathlib.Path(a.out).resolve();out.mkdir(exist_ok=False)
 result={'PASS':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[]}
 def execute(name,cmd):
  proc=subprocess.run(cmd,cwd=run,capture_output=True)
  (out/(name+'.stdout')).write_bytes(proc.stdout);(out/(name+'.stderr')).write_bytes(proc.stderr)
  result['commands'].append({'argv':cmd,'exit':proc.returncode})
  if proc.returncode:raise RuntimeError(name+' exit '+str(proc.returncode))
 try:
  lock=(run/'finalizer_r6.lock').open('a')
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for name in ('EXECUTION_SHA256.txt','REFERENCES_SHA256.txt'):execute(name,['sha256sum','-c',name])
  mod,cfg,ch,plan=state(run);py=(run/'PYTHON_PATH.txt').read_text().strip()
  drv=run/'campaign/bin/campana_v2.py'
  cmd=[py,str(drv),'aggregate','--config',str(run/'campaign/config.json'),'--jobs','1']
  if plan['mode']=='tabla':
   raw=mod.strict_json((run/'input/raw_counts.json').read_text())
   cmd+=['--reference-csv',str(run/'input/raw_table.csv')]+['--expect='+k+'='+str(raw[k]) for k in KEYS]
  else:cmd+=['--expect=encontradas=51','--reference-g6',str(run/'input/reference51.g6'),'--labelg',str(run/'input/labelg'),'--expect-labelg-sha256',sha(run/'input/labelg')]
  execute('metadata_before',[py,str(run/'scripts/audit_receipt_metadata_r6.py'),'--campaign',str(run/'campaign'),'--out',str(out/'metadata_before.json')])
  previous={p.name for p in (run/'campaign/aggregate_attempts').glob('*.json')}
  # Preserve the prior published bytes outside campaign BEFORE driver cleanup can replace them.
  # Failure to preserve aborts before the aggregate command; prior state is not promoted to approval.
  result['previous_state_sha256']={}
  prior=run/'campaign/aggregate.json'
  if prior.exists():
   dest=out/'previous_state';dest.mkdir()
   prior_bytes=prior.read_bytes();(dest/'aggregate.json').write_bytes(prior_bytes)
   result['previous_state_sha256']['aggregate.json']=sha(dest/'aggregate.json')
   if prior.read_bytes()!=prior_bytes:raise ValueError('previous aggregate changed during preservation')
   try:old_data=mod.strict_json(prior_bytes.decode())
   except (ValueError,UnicodeError):old_data=None
   old_id=old_data.get('attempt_id') if isinstance(old_data,dict) else None
   files=[(src,PathTarget) for src in (run/'campaign').glob('*.g6') for PathTarget in [dest/'graphs'/src.name]]
   if isinstance(old_id,str) and old_id not in ('','.','..') and pathlib.Path(old_id).name==old_id:
    old_record=run/'campaign/aggregate_attempts'/(old_id+'.json')
    if old_record.is_file():files.append((old_record,dest/'attempt_records'/old_record.name))
   for src,target in files:
    target.parent.mkdir(exist_ok=True)
    before_sha=sha(src);target.write_bytes(src.read_bytes())
    if sha(src)!=before_sha or sha(target)!=before_sha:raise ValueError('previous state changed during preservation')
    result['previous_state_sha256'][str(target.relative_to(dest))]=before_sha
  execute('aggregate',cmd)
  data,record,rp=validate_attempt(run,cmd[2:],previous)
  agg=run/'campaign/aggregate.json';agghash=sha(agg);rechash=sha(rp)
  (out/'aggregate_snapshot.json').write_bytes(agg.read_bytes())
  (out/'driver_attempt_snapshot.json').write_bytes(rp.read_bytes())
  result.update(aggregate_sha256=agghash,driver_attempt_sha256=rechash,attempt_id=data['attempt_id'])
  before=mod.strict_json((out/'metadata_before.json').read_text())
  expected_graphs=before['expected_graph_sha256']
  actual_graphs={p.name:sha(p) for p in (run/'campaign').glob('*.g6')}
  if actual_graphs!=expected_graphs:raise ValueError('graph outputs differ from validated receipt records')
  (out/'graphs').mkdir()
  for name,digest in expected_graphs.items():
   snapshot=out/'graphs'/name;snapshot.write_bytes((run/'campaign'/name).read_bytes())
   if sha(snapshot)!=digest:raise ValueError('graph output changed while snapshotting')
  result['graph_sha256']=expected_graphs
  result['frozen_tool_sha256']={}
  for ref in data['references']:
   if ref['kind']=='labelg':
    original=pathlib.Path(ref['frozen_copy'])
    (out/'tools').mkdir(exist_ok=True);snapshot=out/'tools/labelg'
    snapshot.write_bytes(original.read_bytes());snapshot.chmod(0o500)
    if sha(snapshot)!=ref['sha256']:raise ValueError('frozen labelg changed during snapshot')
    result['frozen_tool_sha256']['labelg']=ref['sha256']

  if plan['mode']=='tabla':
   execute('compare',[py,str(run/'scripts/compare_campaign_slices_v24_r6.py'),'--campaign',str(run/'campaign'),'--history',str(run/'input'),'--driver',str(drv),'--out',str(out/'per_slice.json')])
  execute('metadata_after',[py,str(run/'scripts/audit_receipt_metadata_r6.py'),'--campaign',str(run/'campaign'),'--out',str(out/'metadata_after.json')])
  before=mod.strict_json((out/'metadata_before.json').read_text());after=mod.strict_json((out/'metadata_after.json').read_text())
  if before['receipt_manifest_sha256']!=after['receipt_manifest_sha256']:raise ValueError('receipts changed during finalization')
  if after['expected_graph_sha256']!=expected_graphs:raise ValueError('receipt graph sets changed during finalization')
  if {p.name:sha(p) for p in (run/'campaign').glob('*.g6')}!=expected_graphs:raise ValueError('graph outputs changed during finalization')
  if {p.name:sha(p) for p in (out/'graphs').glob('*.g6')}!=expected_graphs:raise ValueError('graph snapshots changed during finalization')
  validate_attempt(run,cmd[2:],previous)
  if {p.name:sha(p) for p in (out/'tools').glob('*')}!=result['frozen_tool_sha256']:raise ValueError('tool snapshots changed during finalization')
  if sha(agg)!=agghash or sha(rp)!=rechash:raise ValueError('aggregation/attempt changed during finalization')
  for name in ('EXECUTION_SHA256.txt','REFERENCES_SHA256.txt'):execute('final_'+name,['sha256sum','-c',name])
  result['PASS']=True
 except Exception as e:result['error']=repr(e)
 (out/'attempt.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print(json.dumps(result,indent=2,allow_nan=False));return 0 if result['PASS'] else 1
if __name__=='__main__':raise SystemExit(main())
