#!/usr/bin/env python3
"""Maintain a minimal, GitHub-reviewable PUBLIC ORGANIZATION lead register.

This is not a scraper, CRM, or outreach tool. Never store personal profiles here.
"""
import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

from qualify_report import SERVICES, qualify_report

BASE = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = BASE / '.agents' / 'skills' / 'first-customer-finder' / 'scripts'
sys.path.insert(0, str(SKILL_SCRIPTS))
from prospect_data import canonical_url, normalize_report, prospect_id, read_state  # noqa: E402

FIELDS = ('product_key', 'prospect_id', 'entity_name', 'entity_url', 'source_url',
          'signal_date', 'first_seen', 'last_seen', 'review', 'contact_status')
REVIEWS = {'unreviewed', 'keep', 'maybe', 'reject'}
STATUSES = {'new', 'contacted', 'replied', 'not_interested', 'customer'}
REGISTER = BASE / 'data' / 'lead-register.csv'


def protected(value):
    """Avoid spreadsheet formula execution in user-visible business names."""
    value = str(value or '').strip()
    if value.lstrip().startswith(('=', '+', '-', '@')):
        return "'" + value
    return value


def read_rows(path):
    if not path.is_file():
        raise ValueError('Register missing: ' + str(path))
    with path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError('Unexpected register header; do not silently overwrite it')
        rows = list(reader)
    seen = set()
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError('Malformed register row')
        key = (row['product_key'], row['prospect_id'])
        if key in seen:
            raise ValueError('Duplicate register key: ' + repr(key))
        seen.add(key)
        if not row['product_key'].strip() or prospect_id(row['entity_url']) != row['prospect_id']:
            raise ValueError('Invalid product key or entity ID: ' + repr(key))
        if row['review'] not in REVIEWS or row['contact_status'] not in STATUSES:
            raise ValueError('Invalid review/contact status for ' + repr(key))
        for k in ('first_seen', 'last_seen'):
            date.fromisoformat(row[k])
    return rows


def save_rows(path, rows):
    # This file is committed through a human-reviewed PR; no silent network writes.
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--register', type=Path, default=REGISTER, help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('list', help='Show saved organization IDs and URLs')
    s.add_argument('--product', required=True)
    s = sub.add_parser('seed-state', help='Seed fresh, ignored upstream state.json from register')
    s.add_argument('--product', required=True)
    s.add_argument('--out', type=Path, required=True)
    s = sub.add_parser('record', help='Record explicitly selected business IDs from verified JSON')
    s.add_argument('--product', required=True)
    s.add_argument('--report-json', type=Path, required=True)
    s.add_argument('--id', dest='ids', action='append', required=True, help='Verified organization ID; repeat per org')
    s = sub.add_parser('review', help='Apply explicit user decision')
    s.add_argument('--product', required=True)
    s.add_argument('--id', required=True)
    s.add_argument('--decision', choices=sorted(REVIEWS - {'unreviewed'}), required=True)
    s = sub.add_parser('status', help='Apply explicit user-reported outreach outcome')
    s.add_argument('--product', required=True)
    s.add_argument('--id', required=True)
    s.add_argument('--value', choices=sorted(STATUSES), required=True)
    sub.add_parser('verify', help='Validate registry and the stable IDs')
    args = p.parse_args()

    try:
        rows = read_rows(args.register)
        if args.command == 'verify':
            print(f'OK: {len(rows)} public-organization register rows; no contact actions performed.')
            return
        if not args.product.strip():
            raise ValueError('Provide stable product key')
        product_rows = [row for row in rows if row['product_key'] == args.product]
        if args.command == 'list':
            print(json.dumps(product_rows, ensure_ascii=False, indent=2))
            return
        if args.command == 'seed-state':
            if args.out.exists() or args.out.is_symlink():
                raise ValueError('State path exists; choose a fresh ignored workspace path')
            state = {'schema_version': 1, 'project_key': args.product, 'demo': False,
                     'profile': {'prefer': [], 'avoid': []}, 'prospects': {}}
            for row in product_rows:
                status = row['contact_status']
                review = row['review']
                state['prospects'][row['prospect_id']] = {
                    'id': row['prospect_id'],
                    'first_seen': row['first_seen'] + 'T00:00:00Z',
                    'last_seen': row['last_seen'] + 'T00:00:00Z',
                    'status': status,
                    'feedback': review if review != 'unreviewed' else None,
                    'latest': {'entity_url': row['entity_url']},
                }
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open('x', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            read_state(args.out)
            print(f'Seeded {len(product_rows)} dedupe entries at {args.out} (not for GitHub).')
            return
        if args.command == 'record':
            with args.report_json.open('r', encoding='utf-8') as f:
                raw = json.load(f)
            analysis = qualify_report(raw, args.product) if args.product in SERVICES else normalize_report(raw)
            if analysis.get('demo') or analysis['project_key'] != args.product or analysis['schema_version'] != 2:
                raise ValueError('Only validated v2 real research for the matching product is allowed')
            candidates = {p['id']: p for p in analysis['prospects']}
            if len(set(args.ids)) != len(args.ids):
                raise ValueError('Duplicate --id selection')
            missing = set(args.ids) - set(candidates)
            if missing:
                raise ValueError('Prospect IDs not found in validated research: ' + repr(sorted(missing)))
            known = {(row['product_key'], row['prospect_id']): row for row in rows}
            today = date.today().isoformat()
            added = 0
            for entity_id in args.ids:
                prospect = candidates[entity_id]
                entity_type = str(prospect.get('type', '')).lower().strip()
                permitted = {'company', 'organization', 'organisation', 'project',
                             'business', 'nonprofit', 'non-profit', 'startup', 'agency', 'team'}
                if entity_type not in permitted:
                    raise ValueError(f'ID {entity_id} lacks an explicit organizational type; never save personal profiles')
                # Entity type is supplied by research; independently verify that the URL is an organization.
                key = args.product, entity_id
                if key in known:
                    # Do not silently change review/status or overwrite original evidence.
                    continue
                row = {
                    'product_key': args.product,
                    'prospect_id': entity_id,
                    'entity_name': protected(prospect['name']),
                    'entity_url': canonical_url(prospect['entity_url']),
                    'source_url': prospect['source_url'],
                    'signal_date': prospect.get('signal_date') or '',
                    'first_seen': today,
                    'last_seen': today,
                    'review': 'unreviewed',
                    'contact_status': 'new',
                }
                rows.append(row)
                added += 1
            save_rows(args.register, rows)
            print(f'Added {added} business-only lead register row(s). Review PR before merging. No outreach sent.')
            return
        matches = [row for row in rows if row['product_key'] == args.product and row['prospect_id'] == args.id]
        if len(matches) != 1:
            raise ValueError('Unknown or nonunique prospect ID for this product')
        row = matches[0]
        if args.command == 'review':
            row['review'] = args.decision
        elif args.command == 'status':
            row['contact_status'] = args.value
        row['last_seen'] = date.today().isoformat()
        save_rows(args.register, rows)
        print('Updated reviewed organizational record. Save through PR to persist. No outreach sent.')
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as e:
        p.exit(1, f'Error: {e}\n')


if __name__ == '__main__':
    main()
