"""Check the bundled demo, statistical contracts and generated outputs."""
from pathlib import Path
import csv
import hashlib
import json
import platform
import re
import subprocess
import sys
from PIL import Image
from common import HERE, np, matplotlib


def main():
    test = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE / 'tests'), '-v'],
                          cwd=HERE, text=True, capture_output=True)
    if test.returncode:
        raise RuntimeError(test.stdout + test.stderr)
    count = int(re.search(r'Ran (\d+) tests?', test.stderr).group(1))
    csv_hash = hashlib.sha256((HERE / 'data/demo/observations.csv').read_bytes()).hexdigest()
    config_hash = hashlib.sha256((HERE / 'config.json').read_bytes()).hexdigest()
    for name in ['forest', 'raincloud', 'pareto']:
        for fmt in ['png', 'svg', 'pdf']:
            path = HERE / 'figures' / f'{name}.{fmt}'
            if not path.is_file() or path.stat().st_size < 1000:
                raise ValueError(f'Missing or empty {path}. Run python run_all.py first.')
        with Image.open(HERE / 'figures' / f'{name}.png') as image:
            if min(image.size) < 500 or all(lo == hi for lo, hi in image.convert('RGB').getextrema()):
                raise ValueError(f'Empty or undersized {name}.png')
        provenance = json.loads((HERE / 'figures' / f'{name}_provenance.json').read_text())
        if provenance['input_sha256'] != csv_hash or provenance['config_sha256'] != config_hash:
            raise ValueError(f'Stale {name} output; rerun the bundled demo.')
        if provenance['data_kind'] != 'synthetic':
            raise ValueError('Bundled figures must remain labelled as synthetic.')
        if (provenance.get('input_csv') != 'data/demo/observations.csv'
                or provenance.get('input_csv_base') != 'config_directory'
                or provenance.get('config_file') != 'config.json'):
            raise ValueError(f'{name}: bundled input provenance must use portable references.')
        with (HERE / 'figures' / f'{name}_summary.csv').open(newline='', encoding='utf-8') as stream:
            summary = list(csv.DictReader(stream))
        if not summary or any(int(row['n']) <= 0 for row in summary):
            raise ValueError(f'{name}: empty summary or invalid sample count.')
    for document in ['README.md', 'DATA_FORMAT.md']:
        for link in re.findall(r'\]\(([^)]+)\)', (HERE / document).read_text()):
            if link.startswith(('http:', 'https:', '#')) or link == 'verification.json':
                continue
            if not (HERE / link.split('#')[0]).exists():
                raise ValueError(f'Broken local link: {document}: {link}')
    paths = [p for p in HERE.rglob('*') if p.is_file()
             and not set(p.relative_to(HERE).parts) & {'.cache', '__pycache__', '.venv', 'dist'}
             and p.name not in {'verification.json', '.DS_Store'}]
    record = {'status': 'passed', 'templates': 3, 'statistical_contract_tests': count,
              'formats': ['png', 'svg', 'pdf'], 'data_kind': 'synthetic',
              'python': platform.python_version(), 'matplotlib': matplotlib.__version__, 'numpy': np.__version__,
              'checks': ['statistical edge cases', 'demo input/output hashes', 'PNG nonempty and dimensions',
                         'PNG/SVG/PDF present', 'nonempty summary CSVs', 'documentation local links',
                         'portable input provenance'],
              'scope': 'Checks code and demo artifacts, not scientific validity of real experiment logs.',
              'sha256': {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}}
    (HERE / 'verification.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(f'Verified 3 runnable templates, {count} statistical contract tests, PNG/SVG/PDF and documentation.')


if __name__ == '__main__':
    main()
