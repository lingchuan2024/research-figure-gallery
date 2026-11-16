"""Make a portable zip of this template bundle, excluding environments/caches."""
from pathlib import Path
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent


def main():
    subprocess.run([sys.executable, str(HERE / 'verify.py')], check=True)
    target = HERE / 'dist/rerank-plot-templates.zip'
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        for path in sorted(HERE.rglob('*')):
            relative = path.relative_to(HERE)
            if not path.is_file() or set(relative.parts) & {'.cache', '__pycache__', '.venv', 'dist'} or path.name == '.DS_Store':
                continue
            archive.write(path, Path('rerank-plot-templates') / relative)
    print(f'{target} ({target.stat().st_size / 1024 / 1024:.2f} MiB)')


if __name__ == '__main__':
    main()
