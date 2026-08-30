#!/usr/bin/env python3
"""Mutate only disposable copies of the exact budget helper, not production physics."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
CASES = [
    ('drop_remainders', 'full.remainder_radius+half.remainder_radius', 'Fraction(0)',
     'test_nonlinear_remainders_are_summed_not_erased'),
    ('reverse_difference', 'half.center-full.center,', 'full.center-half.center,',
     'test_difference_sign_and_all_corners_agree_with_direct_rationals'),
    ('relax_strict_limit', 'delta.bound<limit', 'delta.bound<=limit',
     'test_source_binary64_strict_threshold_is_not_replaced_or_relaxed'),
]


def main(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    source = (ROOT / 'paired_budget.py').read_bytes()
    text = source.decode('utf-8')
    records = []
    for name, old, new, test in CASES:
        if text.count(old) != 1:
            raise RuntimeError('mutation anchor is not unique: ' + name)
        with tempfile.TemporaryDirectory(prefix='rei-budget-mutant-') as temp:
            work = Path(temp)
            (work / 'tests').mkdir()
            (work / 'paired_budget.py').write_text(text.replace(old, new), encoding='utf-8')
            shutil.copy2(ROOT / 'tests/test_paired_budget.py', work / 'tests/test_paired_budget.py')
            command = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                       'tests/test_paired_budget.py::' + test, '--tb=short', '--junitxml=result.xml']
            run = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                 timeout=30, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
            log = (run.stdout + run.stderr).encode('utf-8')
            (output / (name + '.log')).write_bytes(log)
            suites = list(ET.parse(work / 'result.xml').getroot().iter('testsuite'))
            failures = sum(int(item.get('failures', '0')) for item in suites)
            errors = sum(int(item.get('errors', '0')) for item in suites)
            if run.returncode != 1 or failures != 1 or errors:
                raise RuntimeError('mutation did not reach the intended assertion: ' + name)
            records.append({'mutation': name, 'test': test, 'exit': run.returncode,
                            'assertion_failures': failures, 'collection_errors': errors,
                            'log_sha256': hashlib.sha256(log).hexdigest()})
    result = {'scope': 'EXACT_BUDGET_HELPER_ONLY_NOT_CANONICAL_MAP',
              'source_sha256': hashlib.sha256(source).hexdigest(), 'mutations': records}
    (output / 'MUTATIONS.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: check_mutations.py OUTPUT_DIRECTORY')
    main(sys.argv[1])
