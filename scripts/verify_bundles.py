"""Execute every local figure bundle in isolation and check upstream archives."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import ast
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_all_figures import collect


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(entry, originals, font_cache):
    archive = ROOT / entry['bundle_path']
    if sha(archive) != entry['bundle_sha256']:
        raise ValueError(f'Changed bundle: {entry["id"]}')
    record = {'id': entry['id'], 'kind': entry['kind'],
              'bundle_sha256': entry['bundle_sha256']}
    with tempfile.TemporaryDirectory(prefix='figure-bundle-') as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(archive) as bundle:
            if bundle.testzip():
                raise ValueError(f'Corrupt bundle: {entry["id"]}')
            for name in bundle.namelist():
                path = Path(name)
                if path.is_absolute() or '..' in path.parts:
                    raise ValueError(f'Unsafe archive member: {name}')
            bundle.extractall(folder)
        work = folder / entry['id']
        if not (work / 'README.md').is_file():
            raise ValueError(f'Missing instructions: {entry["id"]}')
        if entry['kind'] == 'upstream':
            for name in ['UPSTREAM_LICENSE.txt', 'PROVENANCE.json', 'DEPENDENCIES.md']:
                if not (work / name).is_file():
                    raise ValueError(f'Missing {name}: {entry["id"]}')
            if not list((work / 'upstream').glob('*')):
                raise ValueError(f'Missing source snapshot: {entry["id"]}')
            # Syntax checks do not import or execute optional upstream packages.
            for source in work.rglob('*.py'):
                ast.parse(source.read_text(encoding='utf-8'), filename=source.name)
            return {**record, 'status': 'integrity_checked_not_executed'}
        environment = dict(os.environ)
        for key in ['PYTHONPATH', 'PYTHONHOME']:
            environment.pop(key, None)
        environment.update(MPLBACKEND='Agg', MPLCONFIGDIR=str(font_cache), PYTHONDONTWRITEBYTECODE='1')
        command = ['run.py', '--formats', 'png', 'svg']
        result = subprocess.run([sys.executable, *command], cwd=work, env=environment,
                                text=True, capture_output=True, timeout=180)
        if result.returncode:
            raise RuntimeError(f'{entry["id"]} failed:\n{result.stdout}\n{result.stderr}')
        pngs, svgs = list((work / 'output').glob('*.png')), list((work / 'output').glob('*.svg'))
        if len(pngs) != 1 or len(svgs) != 1:
            raise ValueError(f'Expected one PNG/SVG pair: {entry["id"]}')
        png, svg = pngs[0], svgs[0]
        with Image.open(png) as image, Image.open(originals[entry['id']]) as reference:
            rgb, expected = image.convert('RGBA'), reference.convert('RGBA')
            if min(image.size) < 300 or all(lo == hi for lo, hi in rgb.getextrema()):
                raise ValueError(f'Empty or undersized PNG: {entry["id"]}')
            record['png'] = {'path': str(png.relative_to(work)), 'sha256': sha(png),
                             'dimensions': list(image.size),
                             'rgba_pixels_equal': rgb.size == expected.size and rgb.tobytes() == expected.tobytes()}
        if not ET.parse(svg).getroot().tag.endswith('svg'):
            raise ValueError(f'Invalid SVG: {entry["id"]}')
        record.update(status='passed', command=['python', *command], exit_code=result.returncode,
                      working_directory='.',
                      stdout=result.stdout.replace(str(work), '.').strip(),
                      stderr=result.stderr.replace(str(folder), '<temporary>').strip(),
                      svg={'path': str(svg.relative_to(work)), 'sha256': sha(svg), 'valid_xml': True},
                      original_image=str(originals[entry['id']].relative_to(ROOT)),
                      byte_identical_png=sha(png) == sha(originals[entry['id']]))
        return record


def main():
    manifest = json.loads((ROOT / 'dist/figure_code_manifest.json').read_text())
    entries = manifest['entries']
    if len(entries) != 34 or sum(e['kind'] == 'local' for e in entries) != 26:
        raise ValueError('Expected 26 local bundles and 8 upstream references.')
    originals = {item['id']: item['image'] for item in collect()}
    before = {name: sha(path) for name, path in originals.items()}
    # Font discovery is independent of figure code/data. Share only this cache,
    # while every runnable archive retains its own empty extraction directory.
    with tempfile.TemporaryDirectory(prefix='figure-font-cache-') as font_cache:
        environment = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME'}}
        environment.update(MPLCONFIGDIR=font_cache, MPLBACKEND='Agg')
        subprocess.run([sys.executable, '-c', 'import matplotlib.font_manager'],
                       env=environment, check=True, capture_output=True, timeout=180)
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(lambda entry: verify(entry, originals, font_cache), entries))
    if before != {name: sha(path) for name, path in originals.items()}:
        raise ValueError('Verification modified source images.')
    local = [r for r in results if r['kind'] == 'local']
    report = {'status': 'passed', 'local_bundle_count': len(local), 'upstream_reference_count': 8,
              'python_version': platform.python_version(),
              'isolation': 'Each ZIP extracted into a fresh temporary directory; PYTHONPATH/PYTHONHOME removed.',
              'original_images_unchanged': True,
              'pixel_identical_count': sum(r['png']['rgba_pixels_equal'] for r in local),
              'byte_identical_png_count': sum(r['byte_identical_png'] for r in local),
              'image_comparison_note': 'Pixel/byte equality is informational across platforms and font installations.',
              'entries': results}
    (ROOT / 'dist/figure_code_execution.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'Passed: {len(local)} isolated plotting runs; 8 upstream integrity checks.')


if __name__ == '__main__':
    main()
