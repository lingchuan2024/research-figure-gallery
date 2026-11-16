"""Validate the unified one-preview-per-chart-type editorial catalog."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def load_families(available_codes=None):
    families = json.loads((ROOT / 'docs/catalog/figure_families.json').read_text())['families']
    ids = [f['id'] for f in families]
    members = [code for f in families for code in f['members']]
    if len(ids) != len(set(ids)) or len(members) != len(set(members)):
        raise ValueError('Every chart type and source variant must occur exactly once.')
    if available_codes is not None and set(members) != set(available_codes):
        raise ValueError('Chart types must partition all source variants without omissions.')
    for family in families:
        if family['representative'] not in family['members']:
            raise ValueError('Representative is not a member: ' + family['id'])
        if not family.get('title') or not family.get('caution') or not family.get('uses'):
            raise ValueError('Missing chart-type explanation: ' + family['id'])
        covered = set()
        for use in family['uses']:
            if not all(use.get(key) for key in ('purpose', 'placement', 'data', 'source_codes')):
                raise ValueError('Incomplete use case: ' + family['id'])
            if not set(use['source_codes']) <= set(family['members']):
                raise ValueError('Use case references another chart type: ' + family['id'])
            covered.update(use['source_codes'])
        if covered != set(family['members']):
            raise ValueError('Every source variant needs a corresponding use case: ' + family['id'])
    return families
