#!/usr/bin/env python3
"""Mutation tests of the fixed finite-evidence manifest, using system temporary files.

For each inventoried file, flip one byte at the first/middle/last positions and
at the beginning of every nonempty TSV cell, JSON token, or text line. Restore
each mutation. These are specified tests, not an exhaustive test of all possible
byte edits. The digest check covers all bytes; semantic checkers are separate.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,re,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from check_integrity import check_file,verify

def offsets(path,data):
    positions={0,len(data)//2,len(data)-1} if data else set()
    if path.suffix=='.tsv':
        positions.update(m.start() for m in re.finditer(rb'[^\t\r\n]+',data))
    elif path.suffix in ('.json','.jsonl'):
        positions.update(m.start() for m in re.finditer(rb'"(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?|true|false|null',data))
    else:
        positions.update(m.start() for m in re.finditer(rb'[^\r\n]+',data))
    return sorted(positions)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args()
    verify(a.root); records=json.loads((a.root/'integrity_manifest.json').read_text())['files']; results=[]
    with tempfile.TemporaryDirectory(prefix='finite-evidence-test-') as tmp:
        target=Path(tmp)/'mutation'
        for r in records:
            path=a.root/r['path']; raw=path.read_bytes(); target.write_bytes(raw); assert check_file(target,r)
            positions=offsets(path,raw)
            with target.open('r+b',buffering=0) as f:
                for i in positions:
                    f.seek(i);f.write(bytes([raw[i]^1]))
                    assert not check_file(target,r),(r['path'],i)
                    f.seek(i);f.write(raw[i:i+1])
            assert target.read_bytes()==raw and check_file(target,r)
            # Appending also covers a hypothetical empty record.
            with target.open('ab') as f: f.write(b'X')
            assert not check_file(target,r)
            results.append({'path':r['path'],'one_byte_substitutions_rejected':len(positions),'append_rejected':True})
    verify(a.root)
    print(json.dumps({'tested_files':len(results),'one_byte_substitutions':sum(x['one_byte_substitutions_rejected'] for x in results),
      'all_inputs_preserved':True,'scope':'byte integrity against fixed manifest; semantic checks run separately',
      'files':results},indent=2))
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__=='__main__': main()
