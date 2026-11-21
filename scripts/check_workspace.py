#!/usr/bin/env python3
"""Quick no-network diagnostic for the long-term customer finder workspace."""
from pathlib import Path
import subprocess
import sys
BASE = Path(__file__).resolve().parents[1]
required = [
    'AGENTS.md', 'README.md', 'products/main.md', 'data/lead-register.csv',
    '.agents/skills/first-customer-finder/SKILL.md',
    '.agents/skills/first-customer-finder/scripts/generate_report.py',
    '.agents/skills/first-customer-finder/scripts/prospect_data.py',
    '.agents/skills/first-customer-finder/references/report-artifact.md',
    'scripts/lead_register.py',
]
missing = [p for p in required if not (BASE/p).is_file()]
if missing:
    print('MISSING: ' + ', '.join(missing)); sys.exit(1)
result = subprocess.run([sys.executable, str(BASE/'scripts/lead_register.py'), 'verify'], cwd=BASE)
if result.returncode:sys.exit(result.returncode)
text=(BASE/'products/main.md').read_text(encoding='utf-8')
print('SUCCESS: workspace structure and register are valid.')
if 'NOT_SET' in text:
    print('NEXT: tell Codex your product URL/description once to complete the profile.')
print('NOTE: web research and GitHub permissions are not tested by this diagnostic.')
