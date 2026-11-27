"""Compare the new accumulator with saved independent R7 outcomes; no oracle replay."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from heang_contract import Event, integrate_events
from heang_contract.exact_events import numbers

UNIT = Path(__file__).resolve().parents[1]
ORACLE = UNIT / 'theory/WITNESS_RESULTS.json'
ORACLE_SHA256 = '18d02cb7c94efba5d4129f71fc4ba1b2afb8d57a7cfcbca09eb4cd3da1797658'
MANIFEST_SHA256 = 'd1ab2796ef737f95de7e6e5d176b6f8336f51b3f2ec96c198feedd953136bac9'


def raw_record(raw):
    return {'N': numbers(raw.N), 'P': numbers(raw.P), 'R': numbers(raw.R)}


def axis_D(raw, axis):
    a = tuple(F(x) for x in axis)
    # S=R/2, K=tr(R)/2; the comparison axis comes from the saved oracle.
    projected_S = sum(a[i] * raw.R[i][j] * a[j] / 2 for i in range(3) for j in range(3))
    return str((3 * projected_S - raw.K) / 2)


def main():
    data = ORACLE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == ORACLE_SHA256
    assert hashlib.sha256((UNIT / 'code/SOURCE_MANIFEST.json').read_bytes()).hexdigest() == MANIFEST_SHA256
    saved = json.loads(data)
    checks = []
    event_count = 0
    for case in saved['cases']:
        for label, law in case['laws'].items():
            # Only W matters for the outgoing shell. I=1 is an explicit
            # arbitrary rational internal threshold for this comparison.
            bundle = integrate_events([Event.from_dict(e) for e in law['events']],
                                      case['m'], case['M'], F(case['W']) + 1, 1)
            event_count += len(law['events'])
            actual = {'electron': raw_record(bundle.electron), 'proton': raw_record(bundle.proton),
                      'C12': numbers(bundle.C12), 'D_e': axis_D(bundle.electron, case['axis']),
                      'D_p': axis_D(bundle.proton, case['axis']),
                      'K_e': str(bundle.electron.K), 'K_p': str(bundle.proton.K)}
            expected = {key: law[key] for key in ('electron', 'proton', 'C12', 'D_e', 'D_p')}
            expected.update(K_e=case['K_e'], K_p=case['K_p'])
            for key in actual:
                checks.append({'case': case['id'], 'law': label, 'quantity': key,
                               'expected': expected[key], 'actual': actual[key],
                               'pass': actual[key] == expected[key]})
    failed = [row for row in checks if not row['pass']]
    output = {'schema': 'he_ang.saved_oracle_correspondence.v1', 'oracle_sha256': ORACLE_SHA256,
              'implementation_manifest_sha256': MANIFEST_SHA256,
              'saved_cases': len(saved['cases']), 'saved_events_consumed': event_count,
              'check_count': len(checks), 'failure_count': len(failed), 'checks': checks,
              'oracle_regeneration': 0, 'old_X1_or_HE38_execution': 0,
              'scope': 'new implementation versus saved exact manufactured R7; arbitrary rational kinetic units',
              'empirical_admission': False, 'runtime_activation': False}
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
