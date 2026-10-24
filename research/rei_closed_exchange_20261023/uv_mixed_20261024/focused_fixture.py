"""One authorized fixture group; run only through run_bounded_fixture.py."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BEFORE_SHA256 = 'f551026241d2838852f1eea5a8f3df3c966006e68f70044a97ae8ce594677067'
AFTER_SHA256 = 'c8dc1d8e8ad1ee72693bae20b86367b0e1aa1e52e9ff307575d21ca0b9279f77'


def encoded(value):
    if isinstance(value, Fraction):
        return {'type': 'Fraction', 'numerator': value.numerator, 'denominator': value.denominator}
    if isinstance(value, float):
        return {'type': 'float', 'hex': value.hex(), 'repr': repr(value)}
    return {'type': 'int', 'value': value}


def load_source(filename, expected_hash, name):
    path = HERE / filename
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        raise RuntimeError(f'{filename}: immutable source SHA mismatch: {actual_hash}')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    epsilon = Fraction(1, 2**54)
    moments = (1, 1 + epsilon, 0, 0, 1.0)
    base = (0, 0, 0, 0, 0)
    rows = []
    for version, filename, source_hash in (
        ('before', 'closed_exchange_before.py', BEFORE_SHA256),
        ('after', 'closed_exchange.py', AFTER_SHA256),
    ):
        module = load_source(filename, source_hash, f'closed_exchange_{version}')
        for mode in ('finite', 'external'):
            expected = (epsilon, 1, -epsilon, 0, -1 if mode == 'finite' else 0)
            for function in ('energy_source', 'source_jvp'):
                if function == 'energy_source':
                    actual = module.energy_source(1, moments, feed_mode=mode)
                else:
                    actual = module.source_jvp(1, base, moments, dchi=0, feed_mode=mode)
                component_equal = [a == e for a, e in zip(actual, expected)]
                mismatched_indices = [i for i, equal in enumerate(component_equal) if not equal]
                length_equal = len(actual) == len(expected)
                if version == 'before':
                    expected_pattern = length_equal and mismatched_indices == [2] and actual[2] == 0.0
                else:
                    expected_pattern = length_equal and all(component_equal)
                row = {
                    'version': version, 'function': function, 'mode': mode,
                    'source_sha256': source_hash,
                    'actual': [encoded(value) for value in actual],
                    'expected': [encoded(value) for value in expected],
                    'component_equal': component_equal,
                    'length_equal': length_equal,
                    'mismatched_indices': mismatched_indices,
                    'all_components_equal': length_equal and all(component_equal),
                    'expected_pattern_observed': expected_pattern,
                }
                rows.append(row)
                print(json.dumps({'check': row}, sort_keys=True), flush=True)
    before = [row for row in rows if row['version'] == 'before']
    after = [row for row in rows if row['version'] == 'after']
    success = len(before) == 4 and len(after) == 4 and all(row['expected_pattern_observed'] for row in rows)
    summary = {
        'fixture_group_count': 1, 'checks_per_version': 4, 'total_checks': len(rows),
        'epsilon': encoded(epsilon), 'chi': 1,
        'moments': [encoded(value) for value in moments], 'jvp_base': list(base), 'dchi': 0,
        'expected_old_red_checks': sum(not row['all_components_equal'] for row in before),
        'repaired_green_checks': sum(row['all_components_equal'] for row in after),
        'contract_pattern_observed': success,
    }
    print(json.dumps({'summary': summary}, sort_keys=True), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
