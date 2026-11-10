#!/usr/bin/env python3
"""Generate the 643 connected K4-free classes of orders 2 through 7.

This optional small generation requires an explicit nauty geng executable.
The mandatory finite verifier reads the resulting catalogue without geng.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {2: 1, 3: 2, 4: 5, 5: 17, 6: 82, 7: 536}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geng', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/local_K4')
    args = parser.parse_args()
    geng = args.geng.resolve()
    reference = json.loads((ROOT / 'finite/provenance/local_K4_small_checks.json').read_text())
    old = {r['order']: r for r in reference['runs']}
    digest = hashlib.sha256(geng.read_bytes()).hexdigest()
    streams, runs = [], []
    for n, expected in COUNTS.items():
        run = subprocess.run([str(geng), '-kc', str(n)], capture_output=True, check=True, timeout=60)
        lines = run.stdout.splitlines()
        assert run.stdout.endswith(b'\n') and len(lines) == expected
        counts = re.findall(rb'^>Z\s+(\d+)\s+graphs generated', run.stderr, re.M)
        assert len(counts) == 1 and int(counts[0]) == expected
        assert all(line and line[0] - 63 == n for line in lines)
        stream_hash = hashlib.sha256(run.stdout).hexdigest()
        runs.append({'order': n, 'options': ['-kc', str(n)], 'exit': run.returncode,
                     'connected_K4_free_graphs': expected, 'stream_sha256': stream_hash,
                     'generator_stderr': run.stderr.decode().strip(),
                     'matches_retained_historical_stream': stream_hash == old[n]['stream_sha256']})
        streams.append(run.stdout)
    assert hashlib.sha256(geng.read_bytes()).hexdigest() == digest
    data = b''.join(streams)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    catalogue = args.output_dir / 'connected_n2_7.g6'
    catalogue.write_bytes(data)
    report = {'generated_utc': datetime.now(timezone.utc).isoformat(),
              'universe': 'all connected K4-free graphs of each order 2 through 7, up to isomorphism',
              'generator': 'nauty geng', 'geng_sha256': digest,
              'same_generator_digest_as_retained_record': digest == reference['geng_sha256'],
              'catalogue': catalogue.name, 'catalogue_sha256': hashlib.sha256(data).hexdigest(),
              'classes': sum(COUNTS.values()), 'runs': runs,
              'scope': 'Fresh bounded generation, not a large-census rerun. A stored catalogue alone does not prove exhaustive coverage.'}
    (args.output_dir / 'generation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if not __debug__:
    raise RuntimeError('Run without -O: assertions are required.')
if __name__ == '__main__':
    main()
