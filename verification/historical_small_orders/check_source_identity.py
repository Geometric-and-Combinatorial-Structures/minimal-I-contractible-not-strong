#!/usr/bin/env python3
"""Check retained historical source identities, without running a census."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    identity = json.loads((HERE / 'SOURCE_IDENTITY.json').read_text())
    project = ROOT / 'src/atascadas.c'
    assert hashlib.sha256(project.read_bytes()).hexdigest() == identity['project_classifier_sha256']
    for record in identity['files']:
        assert hashlib.sha256((HERE / record['file']).read_bytes()).hexdigest() == record['sha256']
    anchor = '      if(si && !ac){ printf("ERROR IS_NO_ACICLICA %s\\n",line); }'
    addition = r'      printf("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n",line,n,chi(A,FULL),ac,sv,si,dm1,d0,d1,d2,d3);'
    original = project.read_text()
    assert original.count(anchor) == 1
    assert (HERE / 'atascadas_classify.c').read_text() == original.replace(anchor, anchor + '\n' + addition)
    original = (ROOT / 'verification/atascadas_memo_exacto.c').read_text()
    anchor = 'int si= sv || (ac && is_graph(A)); if(si) c_is++;'
    addition = 'if(ac && !sv){ printf("AUDIT_NON_IVS %s\\n",line); fflush(stdout); }\n      '
    assert original.count(anchor) == 1
    assert (HERE / 'exact_n11_capture.c').read_text() == original.replace(anchor, addition + anchor)
    records = ROOT / 'finite/provenance'
    small = json.loads((records / 'small_order_counts.json').read_text())
    assert [r['n'] for r in small] == list(range(3, 10))
    assert sum(r['counts']['connected'] for r in small) == 273191
    for row in small:
        assert row['mismatch_count'] == 0 and row['mismatches'] == []
        assert row['counts']['acyclic'] == row['counts']['ISV']
    row10 = dict(re.findall(r'(\S+)=(\d+)', (records / 'separate_order10_census.txt').read_text()))
    assert row10['connected'] == '11716571'
    assert row10['acyclic'] == row10['I_SV'] == '2343148'
    exact = json.loads((records / 'exact_n11_summary.json').read_text())
    assert sorted((r['res'], r['mod']) for r in exact['runs']) == [(r, 4) for r in range(4)]
    assert all(r['exit_geng'] == r['exit_classifier'] == 0 for r in exact['runs'])
    assert exact['sum']['connected'] == 1006700565
    assert exact['sum']['acyclic'] == exact['sum']['I_S'] == exact['sum']['I'] == 166978401
    assert exact['sum']['I_undecided'] == 0
    assert exact['sum']['I_SV'] == 166978389 and len(exact['non_ISV']) == 12
    print(json.dumps({'status': 'PASS', 'source_digests': len(identity['files']) + 1,
                      'instrumentation_only_transformations': 2,
                      'retained_small_order_rows': 9,
                      'scope': 'Source identities and recorded counter equalities only; no census executed.'}, indent=2))


if not __debug__:
    raise RuntimeError('Run without -O: assertions are required.')
if __name__ == '__main__':
    main()
