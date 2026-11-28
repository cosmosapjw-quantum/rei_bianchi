#!/usr/bin/env python3
import argparse
import json
from core import collect


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    a = p.parse_args()
    r = collect(a.manifest)
    print(json.dumps(r, sort_keys=True))
    return 0 if r["status"] == "COLLECTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
