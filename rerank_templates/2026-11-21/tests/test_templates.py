"""Unit tests for strict CSV/config validation and rendering across F01/F02/F06/F07/F08/F09."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
import unittest

TEMPLATE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEMPLATE_DIR))
import numpy as np
import common


class TemplateContractTests(unittest.TestCase):
    def setUp(self):
        self.cfg = common.load_config(TEMPLATE_DIR / 'config.json')
        self.obs = common.read_csv_rows(TEMPLATE_DIR / 'data/demo/observations.csv')

    def test_rejects_unpaired_questions(self):
        broken = [r for r in self.obs if not (r['question_id'] == 'q001' and r['method'] == 'agent_rerank')]
        with self.assertRaisesRegex(ValueError, 'Pairing mismatch'):
            common.validate_observations(broken, self.cfg)

    def test_rejects_reserved_all_subset(self):
        broken = copy.deepcopy(self.obs)
        broken[0]['subset'] = 'All'
        with self.assertRaisesRegex(ValueError, 'reserved'):
            common.validate_observations(broken, self.cfg)

    def test_rejects_measured_placeholder_conditions(self):
        measured = json.loads((TEMPLATE_DIR / 'config.measured.example.json').read_text(encoding='utf-8'))
        with self.assertRaisesRegex(ValueError, 'Fill conditions'):
            common.validate_config(measured)

    def test_rejects_fractional_token_count(self):
        broken = copy.deepcopy(self.obs)
        broken[0]['main_input_tokens'] = '1234.5'
        with self.assertRaisesRegex(ValueError, 'integer count'):
            common.validate_observations(broken, self.cfg)

    def test_normalize_rows_preserves_nan_for_empty_row(self):
        mat = np.array([[4, 1], [0, 0], [2, 2]])
        probs = common.normalize_rows(mat)
        self.assertAlmostEqual(probs[0, 0], 0.8)
        self.assertTrue(np.isnan(probs[1, 0]))
        self.assertTrue(np.isnan(probs[1, 1]))
        self.assertAlmostEqual(probs[2, 1], 0.5)

    def test_bounded_paired_plot_renders_to_custom_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cfg = copy.deepcopy(self.cfg)
            cfg['score'] = {'label': 'nDCG@10', 'kind': 'bounded', 'scale': 1.0, 'unit': 'score', 'delta_unit': 'score'}
            cfg_path = tmp_path / 'bounded_cfg.json'
            cfg_path.write_text(json.dumps(cfg), encoding='utf-8')
            out_dir = tmp_path / 'out'
            subprocess.run([
                sys.executable, str(TEMPLATE_DIR / 'plot_paired.py'),
                '--data', str(TEMPLATE_DIR / 'data/demo/observations_bounded.csv'),
                '--config', str(cfg_path),
                '--output-dir', str(out_dir),
                '--formats', 'png',
            ], check=True)
            self.assertTrue((out_dir / 'paired.png').is_file())
            self.assertTrue((out_dir / 'paired_summary.csv').is_file())
            self.assertTrue((out_dir / 'paired_provenance.json').is_file())


if __name__ == '__main__':
    unittest.main()
