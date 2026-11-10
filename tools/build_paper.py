#!/usr/bin/env python3
"""Compile a temporary source copy into a new output directory.

The deposited bibliography is used by default. --refresh-bibliography explicitly
allows BibTeX to replace it in the temporary build and records the resulting hash.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from processes import run_process
from output_paths import generated_output

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'paper')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--refresh-bibliography', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve()
    try:
        output = generated_output(args.output or ROOT / "build" / source.name)
    except ValueError as error:
        parser.error(str(error))
    if not (source / 'main.tex').is_file():
        parser.error('The source directory must contain main.tex')
    if not args.refresh_bibliography and not (source / 'main.bbl').is_file():
        parser.error('A deposited main.bbl is required; use --refresh-bibliography to generate a new one')
    if output == source or output.is_relative_to(source) or any(output == ROOT / n or output.is_relative_to(ROOT / n) for n in ['paper', 'supplement']):
        parser.error('Build output must be outside both distributed document directories')
    try:
        output.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        parser.error('Use a new output directory: ' + str(error))
    manifest = {str(p.relative_to(source)): sha(p) for p in sorted(source.rglob('*'))
                if p.is_file() and p.suffix in ['.tex', '.bib', '.bbl', '.tikzstyles', '.bst', '.sty', '.cls']}
    command = ['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error']
    if not args.refresh_bibliography:
        command.append('-bibtex-')
    command.append('main.tex')
    report = {'command': command, 'source_sha256': manifest, 'exit_code': 127,
              'temporary_path_used': True, 'refresh_bibliography': args.refresh_bibliography,
              'errors': []}
    with tempfile.TemporaryDirectory(prefix='graph_document_') as tmp:
        work = Path(tmp) / 'document'
        shutil.copytree(source, work, ignore=shutil.ignore_patterns('main.pdf', '*.aux', '*.log', '*.fls',
                        '*.fdb_latexmk', '*.out', '*.brf', '*.blg', 'build', 'results'))
        try:
            if args.refresh_bibliography:
                (work / "main.bbl").unlink(missing_ok=True)
            result = run_process(command, cwd=work, text=True, encoding='utf-8', errors='replace',
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
            (output / 'compile.stdout').write_text(result.stdout, encoding='utf-8')
            report['exit_code'] = result.returncode
            if (work / 'main.bbl').exists():
                report['compiled_bbl_sha256'] = sha(work / 'main.bbl')
                if not args.refresh_bibliography and report['compiled_bbl_sha256'] != manifest['main.bbl']:
                    raise ValueError('The deposited bibliography changed during compilation')
            if result.returncode == 0 and not (work / 'main.pdf').is_file():
                raise ValueError('Compilation returned zero but produced no PDF')
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            report['exit_code'] = 1
            report['errors'].append(str(error))
        for suffix in ['log', 'aux', 'bbl', 'blg', 'fls', 'brf', 'out']:
            f = work / ('main.' + suffix)
            if f.is_file():
                shutil.copy2(f, output / f.name)
        if report['exit_code'] == 0:
            shutil.copy2(work / 'main.pdf', output / 'main.pdf')
    report['PASS'] = report['exit_code'] == 0
    (output / 'build.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'PASS': report['PASS'], 'exit_code': report['exit_code'],
                      'output': str(output), 'source_files': len(manifest), 'errors': report['errors']}))
    return 0 if report['PASS'] else 1


if __name__ == '__main__':
    sys.exit(main())
