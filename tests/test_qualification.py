"""Fictional, offline cases for CREASTO's report and register entry points."""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'scripts'))
from qualify_report import SKILL_SCRIPTS, qualify_report

PRODUCT = 'creasto-web-development'


def example(count=1):
    today = date.today().isoformat()
    report = dict(schema_version=2, demo=True, project_key=PRODUCT, product='Fictional studio',
                  target_customer='Fictional companies', search_scope='Offline fixture',
                  verdict='Fictional test data', generated_at=today, prospects=[])
    for index in range(count):
        brief = f'https://example.org/fictional/brief/{index}'
        report['prospects'].append(dict(
            name=f'Fictional company {index}', entity_url=f'https://example.org/fictional/{index}',
            type='Company', stage='High intent', evidence_status='verified', role_basis='observed',
            pain_signal='Fictional website request', evidence='Fictional paid website brief',
            why_fit='Website design', why_now='Fictional open call', target_role='Owner',
            source_title='Fictional brief', source_type='Company post', source_url=brief,
            checked_at=today, signal_date=today, suggested_channel='Public reply',
            next_step='Review brief', cta='Discuss?', opener='Discuss?', caution='Fictional',
            contact_route=dict(status='verified', label='Reply to the project thread',
                               url=brief + '#reply', source_url=brief, checked_at=today,
                               note='Fictional invitation to freelancers.'),
            dimensions=dict(pain_strength=5, product_fit=5, timing=5, reachability=5, evidence_quality=5),
            eligibility=dict(buyer_request='website-development', compensation='paid',
                             project_status='open', applicant_access='freelancer_or_agency_permitted',
                             upfront_requirement='none', cost_source_url=brief + '/terms',
                             free_submission_evidence='The fictional terms allow free public replies.')))
    return report


class TestQualification(unittest.TestCase):
    def test_reject_ineligible_or_unknown_even_at_full_score(self):
        rejected = {
            'buyer_request': ['unverified', 'ai-ugc'],
            'project_status': ['closed', 'expired', 'unknown'],
            'compensation': ['unpaid', 'unknown'],
            'applicant_access': ['employee_only', 'restricted', 'unknown'],
            'upfront_requirement': ['minimum_wallet_balance', 'purchased_connects', 'paid_bid',
                                    'subscription', 'membership', 'application_credits', 'deposit',
                                    'wallet_recharge', 'paid_verification', 'other_payment', 'unknown'],
            'free_submission_evidence': ['', None, 'unknown'],
            'cost_source_url': ['', 'no source'],
            'deadline': [(date.today() - timedelta(days=1)).isoformat()],
        }
        for field, values in rejected.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    report = example()
                    report['prospects'][0]['eligibility'][field] = value
                    with self.assertRaises(ValueError):
                        qualify_report(report, PRODUCT)

    def test_unverified_original_request(self):
        report = example()
        report['prospects'][0]['evidence_status'] = 'uncertain'
        with self.assertRaises(ValueError):
            qualify_report(report, PRODUCT)

    def test_missing_eligibility_or_contact_route(self):
        report = example()
        prospect = report['prospects'][0]
        findings = prospect.pop('eligibility')
        with self.assertRaises(ValueError):
            qualify_report(report, PRODUCT)
        prospect['eligibility'] = findings
        prospect['contact_route'] = dict(status='not_found', note='No permitted method')
        prospect['dimensions']['reachability'] = 1
        with self.assertRaises(ValueError):
            qualify_report(report, PRODUCT)

    def test_ugc_is_explicit_and_has_separate_history(self):
        report = example()
        report['project_key'] = 'creasto-ai-ugc'
        report['prospects'][0]['eligibility']['buyer_request'] = 'ai-ugc'
        with self.assertRaises(ValueError):
            qualify_report(report, PRODUCT)
        self.assertEqual(len(qualify_report(report, 'creasto-ai-ugc')['prospects']), 1)

    def test_reports_export_only_the_qualified_count_and_route_proof(self):
        for count in [0, 3]:
            with self.subTest(count=count), tempfile.TemporaryDirectory() as folder:
                run = Path(folder)
                raw, qualified = run / 'analysis.json', run / 'qualified.json'
                raw.write_text(json.dumps(example(count)), encoding='utf-8')
                subprocess.run([sys.executable, BASE / 'scripts/qualify_report.py', raw, qualified],
                               check=True, capture_output=True)
                md, sheet = run / 'report.md', run / 'prospects.csv'
                subprocess.run([sys.executable, SKILL_SCRIPTS / 'generate_report.py', qualified, md,
                                '--csv', sheet, '--state', run / 'state.json', '--new-only'],
                               check=True, capture_output=True)
                markdown = md.read_text()
                self.assertIn(f'{count} potential customers', markdown)
                with sheet.open(newline='') as stream:
                    rows = [r for r in csv.DictReader(stream) if r['record_type'] == 'prospect']
                self.assertEqual(len(rows), count)
                for row in rows:
                    self.assertTrue(row['contact_url'].endswith('#reply'))
                    for item in ('Reply to the project thread', 'allow free public replies', '/terms'):
                        self.assertIn(item, row['contact_note'])
                        self.assertIn(item, markdown)

    def test_failed_report_cannot_be_exported_or_registered(self):
        with tempfile.TemporaryDirectory() as folder:
            run = Path(folder)
            report = example(2)
            # Exercise the real-research register branch using a disposable register.
            report['demo'] = False
            selected = qualify_report(report, PRODUCT)['prospects'][0]['id']
            report['prospects'][1]['eligibility']['upfront_requirement'] = 'unknown'
            raw = run / 'analysis.json'
            raw.write_text(json.dumps(report))
            qualified = run / 'qualified.json'
            result = subprocess.run([sys.executable, BASE / 'scripts/qualify_report.py', raw, qualified],
                                    capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(qualified.exists())
            register = run / 'register.csv'
            header = (BASE / 'data/lead-register.csv').read_text().splitlines()[0] + '\n'
            register.write_text(header)
            command = [sys.executable, BASE / 'scripts/lead_register.py', '--register', register,
                       'record', '--product', PRODUCT, '--report-json', raw, '--id', selected]
            result = subprocess.run(command, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('upfront_requirement', result.stderr.decode())
            self.assertEqual(register.read_text(), header)
            report['prospects'].pop()
            raw.write_text(json.dumps(report))
            subprocess.run(command, capture_output=True, check=True)
            self.assertEqual(len(register.read_text().splitlines()), 2)
