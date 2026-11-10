#!/usr/bin/env python3
"""Read-only SHA-256 and inventory check of the finite supplementary evidence.

This verifies bytes, not mathematical claims or historical execution. The
manifest is the fixed baseline; it is not an authentication mechanism against
simultaneous replacement of both payload and manifest. No files are written.
"""
import argparse,hashlib,json
from pathlib import Path
SCOPES=('data','certificates','provenance')

def payload(root):
    paths=[]
    for directory in SCOPES:
        p=root/directory
        if p.is_symlink() or not p.is_dir(): raise ValueError('Invalid evidence directory: '+directory)
        for f in p.rglob('*'):
            if f.is_symlink(): raise ValueError('Symbolic link in evidence: '+f.relative_to(root).as_posix())
            if f.is_file(): paths.append(f)
    paths.extend((root/'figures').glob('*.tsv'))
    for f in paths:
        if f.is_symlink(): raise ValueError('Symbolic link in evidence')
    return sorted(paths)

def check_file(path,record):
    if path.is_symlink() or not path.is_file(): return False
    data=path.read_bytes()
    return len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256']

def verify(root):
    manifest=root/'integrity_manifest.json'; expected=(root/'integrity_manifest.sha256').read_text().strip()
    raw=manifest.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('Integrity manifest differs from its fixed digest')
    m=json.loads(raw); assert m['schema']==1
    records=m['files']; names=[r['path'] for r in records]
    if len(names)!=len(set(names)): raise ValueError('Duplicate manifest path')
    actual={p.relative_to(root).as_posix() for p in payload(root)}
    if actual!=set(names): raise ValueError('Evidence inventory differs: '+str(sorted(actual^set(names))))
    for r in records:
        p=Path(r['path'])
        if p.is_absolute() or '..' in p.parts: raise ValueError('Unsafe manifest path')
        if not check_file(root/p,r): raise ValueError('Evidence bytes differ: '+r['path'])
    return len(records)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--expected-sha256',help='externally supplied digest of integrity_manifest.json');a=p.parse_args()
    try:
        if a.expected_sha256 and hashlib.sha256((a.root/'integrity_manifest.json').read_bytes()).hexdigest()!=a.expected_sha256.lower():
            raise ValueError('Integrity manifest differs from the externally supplied digest')
        count=verify(a.root)
    except (OSError,ValueError,KeyError,AssertionError) as e: p.exit(1,str(e)+'\n')
    print(json.dumps({'integrity_files_checked':count,'mathematical_validation':False,'all_bytes_match':True}))
if not __debug__: raise RuntimeError('Optimised Python disables required assertions; run without -O.')
if __name__=='__main__': main()
