"""Published provenance stays usable after moving a bundle to another machine."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

BUNDLE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUNDLE))
from common import portable_input_reference


class PortableInputReferenceTests(unittest.TestCase):
    def test_moving_config_and_data_together_preserves_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            refs = [portable_input_reference(root / name / 'data/observations.csv',
                                             root / name / 'config.json')
                    for name in ('first-machine', 'second-machine')]
        self.assertEqual(refs[0], refs[1])
        self.assertEqual(refs[0], ('data/observations.csv', 'config_directory'))

    def test_template_input_with_external_config_uses_template_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch('common.HERE', root / 'template'):
                ref = portable_input_reference(root / 'template/data/observations.csv',
                                               root / 'configuration/config.json')
        self.assertEqual(ref, ('data/observations.csv', 'template_directory'))

    def test_external_input_omits_machine_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with patch('common.HERE', root / 'template'):
                ref = portable_input_reference(root / 'external-location/observations.csv',
                                               root / 'configuration/config.json')
        self.assertEqual(ref, ('observations.csv', 'filename_only'))
        self.assertFalse(Path(ref[0]).is_absolute())


if __name__ == '__main__':
    unittest.main()
