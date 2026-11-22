"""Verify all six templates, provenance portability, and contract tests."""
from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE / 'figures'
STEMS = ['results_table', 'paired', 'budget_curve', 'rank_transition', 'tool_composition', 'trajectory']


def main():
    for stem in STEMS:
        for ext in ('png', 'svg', 'pdf'):
            p = FIG_DIR / f'{stem}.{ext}'
            assert p.is_file() and p.stat().st_size > 1000, f'Missing or empty artifact: {p}'
        summary = FIG_DIR / f'{stem}_summary.csv'
        prov_path = FIG_DIR / f'{stem}_provenance.json'
        assert summary.is_file() and summary.stat().st_size > 20, f'Missing summary: {summary}'
        prov = json.loads(prov_path.read_text(encoding='utf-8'))
        assert prov['template'] == stem
        assert prov['data_kind'] == 'synthetic'
        assert not str(prov['input_csv']).startswith('/'), f'Absolute path leaked in {prov_path}'
        assert len(prov['input_sha256']) == 64

    assert (HERE / 'templates_overview.png').is_file()
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE / 'tests'), '-v'], check=True)
    print('ALL TEMPLATE CHECKS AND UNIT TESTS PASSED.')


if __name__ == '__main__':
    main()
