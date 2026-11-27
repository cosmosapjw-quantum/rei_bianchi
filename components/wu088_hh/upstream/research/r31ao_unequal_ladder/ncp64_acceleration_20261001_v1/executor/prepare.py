#!/usr/bin/env python3
import argparse
import json
from core import prepare_manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    a = p.parse_args()
    r = prepare_manifest(a.manifest)
    print(json.dumps(r, sort_keys=True))
    return 0 if r["status"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
