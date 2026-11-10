#!/usr/bin/env python3
"""Bind homology to the successful finalizer output of one explicit SLURM aggregate job."""
import sys
sys.dont_write_bytecode=True
import argparse,pathlib,re,json
from verify_campaign_state_r6 import state,sha,require
def verify(run,job):
 require(re.fullmatch(r'[0-9]+',str(job)) is not None,'job id must be numeric')
 run=pathlib.Path(run).resolve();m,c,ch,p=state(run)
 approval=m.strict_json((run/('attempt_'+str(job))/'attempt.json').read_text())
 require(approval.get('PASS') is True,'finalizer attempt was not PASS')
 agg=run/'campaign/aggregate.json';data=m.strict_json(agg.read_text())
 ident=approval.get('attempt_id')
 require(isinstance(ident,str) and pathlib.Path(ident).name==ident and data.get('attempt_id')==ident,'approved attempt id mismatch')
 record=run/'campaign/aggregate_attempts'/(ident+'.json');rec=m.strict_json(record.read_text())
 require(sha(agg)==approval['aggregate_sha256'] and sha(record)==approval['driver_attempt_sha256'],'aggregate/driver attempt differs from approved job')
 require(data.get('ok') is True and rec.get('status')=='ok' and rec.get('config_sha256')==ch==data.get('config_sha256'),'current attempt not complete for this config')
 require(rec.get('aggregate_sha256')==sha(agg),'terminal aggregate_sha256 does not match published aggregate')
 require(rec.get('slurm_job_id')==str(job),'driver attempt belongs to another SLURM job')
 expected_names={'I_NO_IS.g6','ACICLICA_NO_IS_INDECISA.g6'} if c['mode']=='tabla' else {'ATASCADA.g6'}
 graphs=approval.get('graph_sha256')
 require(isinstance(graphs,dict) and set(graphs)==expected_names and all(isinstance(v,str) and re.fullmatch(r'[0-9a-f]{64}',v) for v in graphs.values()),'approved graph map missing or invalid')
 require({p.name:sha(p) for p in (run/'campaign').glob('*.g6')}==graphs,'graph outputs differ from approved job')
 require({p.name:sha(p) for p in (run/('attempt_'+str(job))/'graphs').glob('*.g6')}==graphs,'approved graph snapshots missing or changed')
 return {'PASS':True,'job_id':str(job),'attempt_id':ident,'aggregate_sha256':sha(agg),'graph_sha256':graphs}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--job-id',required=True);a=p.parse_args()
 print(json.dumps(verify(a.run,a.job_id)))
