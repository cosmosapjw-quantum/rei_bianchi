#!/usr/bin/env python3
"""Targeted zero-rate J domain regression; first observed failure is retained."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
from run_control import atomic_bytes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('owner_interval_domain_probe', args.interval)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    try:
        value = module.response_j(module.IV(0), module.IV(-1))
    except ArithmeticError as error:
        outcome = {'check_id': 'J_ZERO_RATE_NEGATIVE_WIDTH_REJECTED', 'passed': True,
                   'observed_exception': type(error).__name__, 'message': str(error)}
    else:
        outcome = {'check_id': 'J_ZERO_RATE_NEGATIVE_WIDTH_REJECTED', 'passed': False,
                   'expected': 'ArithmeticError for negative width',
                   'observed_return': value.json(),
                   'physical_six_control_inputs_affected': False}
    atomic_bytes(args.output, (json.dumps(outcome, indent=2) + '\n').encode())
    print(json.dumps(outcome))
    return 0 if outcome['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
