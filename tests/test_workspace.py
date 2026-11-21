"""Self-contained integration tests for the bundled business-only register."""
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'scripts'))
import lead_register as mod

class TestWorkspace(unittest.TestCase):
    def test_full_original_skill_present(self):
        self.assertTrue((BASE/'.agents/skills/first-customer-finder/SKILL.md').is_file())
        self.assertTrue((BASE/'.agents/skills/first-customer-finder/references/research-framework.md').is_file())
        self.assertTrue((BASE/'.agents/skills/first-customer-finder/scripts/generate_report.py').is_file())

    def test_registry_header(self):
        self.assertEqual(mod.read_rows(BASE/'data/lead-register.csv'),[])

    def test_protected_spreadsheet_fields(self):
        self.assertEqual(mod.protected('=HYPERLINK(1)'),"'=HYPERLINK(1)")
        self.assertEqual(mod.protected('An Example LLC'),'An Example LLC')

    def test_register_keys_and_id_validation(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'register.csv'
            mod.save_rows(path,[{'product_key':'https://product.example', 'prospect_id':mod.prospect_id('https://example.org'),
              'entity_name':'Example Org','entity_url':'https://example.org', 'source_url':'https://example.org/issues/1',
              'signal_date':'2026-11-01','first_seen':'2026-11-01','last_seen':'2026-11-02',
              'review':'unreviewed','contact_status':'new'}])
            self.assertEqual(len(mod.read_rows(path)),1)

if __name__=='__main__':
    unittest.main()
