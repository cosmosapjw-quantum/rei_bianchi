"""CLI for the existing R31AA hash-locked lightweight replay."""
import argparse
import json
from pathlib import Path

from local_candidate import replay


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    result = replay(a.input)
    payload = json.dumps(result, indent=2, allow_nan=False)+'\n'
    a.out.write_text(payload)
    print(payload, end='')


if __name__ == '__main__':
    main()
