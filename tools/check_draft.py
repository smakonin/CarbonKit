"""Validate the static draft and synthetic fixtures, not full system conformance.

Run after installing requirements-dev.txt. No real personal records are used.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from datetime import datetime
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links = set(), []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, 'Duplicate ID: ' + attrs['id']
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])

pages = {f: Page(f) for f in ROOT.glob('*.html')}
links = 0
for path, page in pages.items():
    for link in page.links:
        u = urlsplit(link)
        if u.scheme or u.netloc:
            assert u.scheme in ('https', 'mailto'), 'Unexpected external scheme'
            continue
        target = (path.parent / unquote(u.path)).resolve() if u.path else path
        if target.is_dir():
            target = target / 'index.html'
        assert target.is_relative_to(ROOT), 'Link escapes site root'
        assert target.exists(), f'Broken link {path.name}: {link}'
        if u.fragment and target in pages:
            assert unquote(u.fragment) in pages[target].ids, f'Broken anchor: {link}'
        links += 1

records = {}
validators = {}
for kind in ('activity', 'estimate'):
    schema = json.loads((ROOT / 'schemas/0.1' / f'{kind}.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validators[kind] = Draft202012Validator(schema)
    records[kind] = json.loads((ROOT / 'examples' / f'synthetic-{kind}.json').read_text())
    validators[kind].validate(records[kind])

def time(s):
    t = datetime.fromisoformat(s.replace('Z', '+00:00'))
    assert t.tzinfo is not None, 'Timezone required'
    return t

def check_fixture(a, e, real_inventory=False):
    """Selected semantic checks for the single electricity fixture method only."""
    validators['activity'].validate(a)
    validators['estimate'].validate(e)
    assert time(a['start']) < time(a['end']), 'Invalid interval'
    assert e['activity_ids'] == [a['id']], 'Wrong activity linkage'
    assert e['subject_ref'] == a['subject_ref'], 'Cross-subject estimate'
    f = e['factors'][0]
    assert len(e['factors']) == 1, 'Fixture method uses one factor'
    assert a['boundary']['geography'] == f['geography'], 'Wrong geography'
    assert time(f['valid_from']) <= time(a['start']) < time(a['end']) <= time(f['valid_to']), 'Factor outside validity'
    assert not (real_inventory and f['synthetic']), 'Synthetic factor in real inventory'
    if a['quantity']['value'] is None:
        assert e['amount']['value'] is None, 'Missing must not become zero'
        return
    canonical = json.dumps(a, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')
    assert hashlib.sha256(canonical).hexdigest() == e['calculation']['input_sha256'], 'Input digest mismatch'
    assert hashlib.sha256((ROOT/'examples/synthetic-factor.txt').read_bytes()).hexdigest() == f['artifact_sha256'], 'Factor artifact mismatch'
    assert Decimal(str(a['quantity']['value'])) * Decimal(str(f['value'])) == Decimal(str(e['amount']['value'])), 'Wrong calculation'
    u = e['uncertainty']
    if u['status'] == 'quantified':
        assert u['lower'] <= e['amount']['value'] <= u['upper'], 'Invalid uncertainty bounds'

activity, estimate = records['activity'], records['estimate']
check_fixture(activity, estimate)

def rejected(action):
    try:
        action()
    except Exception:
        return
    raise AssertionError('Invalid fixture unexpectedly accepted')

# These cases catch actual interoperability errors, not just presence of fields.
bad = deepcopy(activity); bad['quantity']['unit'] = 'W'
rejected(lambda: validators['activity'].validate(bad))
bad = deepcopy(activity); bad['quality'] = 'missing'
rejected(lambda: validators['activity'].validate(bad))
bad = deepcopy(activity); bad['end'] = bad['start']
rejected(lambda: check_fixture(bad, estimate))
bad_estimate = deepcopy(estimate); bad_estimate['factors'][0]['geography'] = 'OTHER'
rejected(lambda: check_fixture(activity, bad_estimate))
bad_estimate = deepcopy(estimate); bad_estimate['factors'][0]['valid_to'] = '2025-01-01T00:00:00Z'
rejected(lambda: check_fixture(activity, bad_estimate))
bad_estimate = deepcopy(estimate); bad_estimate['amount']['value'] = 10
rejected(lambda: check_fixture(activity, bad_estimate))
rejected(lambda: check_fixture(activity, estimate, real_inventory=True))
missing = deepcopy(activity); missing['quality'] = 'missing'; missing['quantity']['value'] = None
missing['coverage'] = {'status':'unknown', 'reason':'No source observation'}
missing_e = deepcopy(estimate); missing_e['amount']['value'] = None
check_fixture(missing, missing_e)
missing_e['amount']['value'] = 0
rejected(lambda: check_fixture(missing, missing_e))
print(f'PASS: {len(pages)} pages, {links} local links/assets, 2 schemas, synthetic arithmetic/digests, and 8 rejection cases.')
print('Scope: static draft and selected fixture checks only. Consent, storage, revisions, overlap and full conformance await implementation.')
