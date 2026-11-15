import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from pdf_fixture import write_pdf

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def test_real_pdf_cli_outputs_evidence_json(self):
        with tempfile.TemporaryDirectory() as temp:
            path = write_pdf(Path(temp) / 'test.pdf', ['The optical sensor prototype was tested in a laboratory chamber. Measurements showed 95 percent accuracy.'])
            run = subprocess.run([sys.executable, 'tools/assess.py', '--target', 'optical sensor',
                                  '--checklist', 'tests/fixtures/checklist.json', str(path)], cwd=ROOT,
                                 capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(result['predicted_trl'], 4)
            self.assertEqual(result['evidence_reference']['APCTT-C04'][0]['page'], 1)

    def test_optional_encoder_requires_local_store_without_importing_torch(self):
        from participant_module.semantic import SemanticRanker
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                SemanticRanker(Path(temp))
        self.assertNotIn('torch', sys.modules)
