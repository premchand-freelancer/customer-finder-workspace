"""Validate a CREASTO shortlist before handing it to the installed report generator."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
import re

SKILL_SCRIPTS = Path(__file__).resolve().parents[1] / '.agents/skills/first-customer-finder/scripts'
sys.path.insert(0, str(SKILL_SCRIPTS))
from prospect_data import iso_date, normalize_report, public_url, text_field

SERVICES = {
    'creasto-web-development': 'website-development',
    'creasto-ai-ugc': 'ai-ugc',
}


# These sites are excluded for CREASTO even if a model incorrectly labels
# their application route as free. Only the repository owner may change this list.
EXCLUDED_PLATFORMS = (
    'freelancer.com', 'freelancer.in', 'freelancer.co.uk',
    'freelancer.com.au', 'upwork.com',
)


def reject_excluded_platform(prospect):
    """Reject known pay-to-bid marketplaces before evaluating AI-reported cost."""
    route = prospect.get('contact_route') or {}
    findings = prospect.get('eligibility') or {}
    locations = {
        'entity_url': prospect.get('entity_url'),
        'source_url': prospect.get('source_url'),
        'contact_route.url': route.get('url'),
        'contact_route.source_url': route.get('source_url'),
        'eligibility.cost_source_url': findings.get('cost_source_url'),
    }
    for field, url in locations.items():
        if not isinstance(url, str):
            continue
        hostname = (urlsplit(url).hostname or '').lower().rstrip('.')
        for blocked in EXCLUDED_PLATFORMS:
            if hostname == blocked or hostname.endswith('.' + blocked):
                raise ValueError(f'{field} points to excluded platform {blocked}')
    # Also catch platform disclosure in source labels even when the URL is shortened.
    clues = (prospect.get('source_title'), prospect.get('source_type'),
             prospect.get('suggested_channel'), route.get('label'),
             route.get('note'), findings.get('free_submission_evidence'))
    for value in clues:
        if not isinstance(value, str):
            continue
        for blocked in EXCLUDED_PLATFORMS:
            if re.search(r'(?<![a-z0-9])' + re.escape(blocked) + r'(?![a-z0-9])', value, re.I):
                raise ValueError(f'Prospect references excluded platform {blocked}')


def check_eligibility(prospect, service):
    """Check recorded findings. The researcher must inspect the cited public pages."""
    reject_excluded_platform(prospect)
    findings = prospect.get('eligibility')
    if not isinstance(findings, dict):
        raise ValueError('Missing eligibility findings')
    required = {
        'buyer_request': service,
        'project_status': 'open',
        'compensation': 'paid',
        'applicant_access': 'freelancer_or_agency_permitted',
        'upfront_requirement': 'none',
    }
    for key, expected in required.items():
        if findings.get(key) != expected:
            raise ValueError(f'eligibility.{key} must be {expected!r}')
    if findings.get('deadline') is not None:
        if iso_date(findings['deadline'], 'deadline') < date.today():
            raise ValueError('Application deadline has passed')
    route = prospect['contact_route']
    if route['status'] != 'verified':
        raise ValueError('A verified, permitted application route is required')
    proof = text_field(findings, 'free_submission_evidence')
    if proof.casefold().strip(' .') in {'unknown', 'uncertain', 'unverified', 'n/a', 'none', 'tbd'}:
        raise ValueError('Describe the evidence that this submission route is free')
    proof_url = public_url(findings.get('cost_source_url'))
    return f"Allowed method: {route['label']}. Free submission evidence: {proof} ({proof_url})"


def qualify_report(raw, product):
    data = normalize_report(raw)
    if data.get('schema_version') != 2 or data.get('project_key') != product:
        raise ValueError('Expected a v2 report for ' + product)
    for prospect in data['prospects']:
        try:
            summary = check_eligibility(prospect, SERVICES[product])
        except ValueError as exc:
            raise ValueError(f"{prospect['name']}: {exc}") from exc
        # The upstream Markdown and CSV exporters both display the route note.
        route = prospect['contact_route']
        if not route['note'].endswith(summary):
            route['note'] = f"{route['note']} {summary}"
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('qualified', type=Path, help='Fresh qualified JSON for the report generator')
    parser.add_argument('--product', choices=SERVICES, default='creasto-web-development')
    args = parser.parse_args()
    try:
        report = qualify_report(json.loads(args.input.read_text(encoding='utf-8')), args.product)
        with args.qualified.open('x', encoding='utf-8') as output:
            json.dump(report, output, ensure_ascii=False, indent=2)
            output.write('\n')
        print(f"Qualified {len(report['prospects'])} opportunities.")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
