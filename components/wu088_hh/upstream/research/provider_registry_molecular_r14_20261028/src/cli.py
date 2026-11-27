"""R14 one-case exact quadratic comparison CLI; a science run if invoked.

Usage (only within an explicitly authorized resource contract):
  python src/cli.py --input CASE.json --output RESULT.json
Both files are JSON. Output creation is exclusive and cannot overwrite evidence.
The CLI does not certify that the declared source is a physical bound.
"""
import argparse
import json
from pathlib import Path

from quadratic_convolution import run_case, serializable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; evidence cannot be overwritten')
    case = json.loads(args.input.read_text())
    result = run_case(case)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(serializable(result), ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
