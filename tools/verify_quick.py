#!/usr/bin/env python3
"""Run the mandatory finite checks, with no optional silent skips.

Python 3.11+ standard library only. No census, network, compiler or scheduler.
The source tree is not written; output is a JSON report on standard output.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import math
ROOT=Path(__file__).resolve().parents[1]
CHECKS=[
 'finite/check_integrity.py',
 'finite/certificates/check_disc_hypotheses.py',
 'finite/certificates/check_certificates.py',
 'finite/data/check_unfoldings.py',
 'finite/data/check_small_closures.py',
 'finite/data/check_tables.py',
 'finite/data/check_adamaszek.py',
 'finite/data/check_local_K4_records.py',
 'finite/provenance/check_records.py',
 'tools/check_local_K4_catalogue.py',
 'tools/check_cardinalities.py',
]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout',type=float,default=600,help='wall-time limit per check')
    a=parser.parse_args()
    if not math.isfinite(a.timeout) or a.timeout<=0:parser.error('--timeout must be finite and positive')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    results=[]
    for check in CHECKS:
        start=time.monotonic()
        command=[sys.executable,'-P',str(ROOT/check)]
        if check.endswith('check_tables.py'):command+=['--timeout',str(a.timeout)]
        try:
            r=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=a.timeout)
            results.append({'check':check,'exit':r.returncode,'seconds':round(time.monotonic()-start,3),
                            'command':command,'stdout':r.stdout,'stderr':r.stderr})
        except subprocess.TimeoutExpired:
            results.append({'check':check,'exit':124,'seconds':round(time.monotonic()-start,3),'stderr':'Timeout; no result certified'})
        except OSError as error:
            results.append({'check':check,'exit':127,'seconds':round(time.monotonic()-start,3),'stderr':str(error)})
        if results[-1]['exit']:
            print(json.dumps({'PASS':False,'executed':results,'full_census_rerun':False},indent=2));return 1
    print(json.dumps({'PASS':True,'executed':results,'full_census_rerun':False},indent=2));return 0
if __name__=='__main__':sys.exit(main())
