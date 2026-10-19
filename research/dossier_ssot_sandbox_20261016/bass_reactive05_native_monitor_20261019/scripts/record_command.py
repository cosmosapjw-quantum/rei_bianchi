#!/usr/bin/env python3
"""Run an explicitly supplied command; preserve stdout, stderr and SHA receipts."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prefix', type=Path, required=True)
    p.add_argument('--cwd', type=Path)
    p.add_argument('command', nargs=argparse.REMAINDER)
    args = p.parse_args()
    command = args.command[1:] if args.command[0] == '--' else args.command
    args.prefix.parent.mkdir(parents=True, exist_ok=True)
    stdout = args.prefix.with_suffix('.stdout.log')
    stderr = args.prefix.with_suffix('.stderr.log')
    receipt = args.prefix.with_suffix('.receipt.json')
    if any(p.exists() for p in (stdout, stderr, receipt)):
        raise FileExistsError('refusing to overwrite an execution record')
    start = datetime.now(timezone.utc).isoformat()
    tick = time.perf_counter()
    with stdout.open('xb') as out, stderr.open('xb') as err:
        result = subprocess.run(command, cwd=args.cwd, stdout=out, stderr=err, check=False)
    report = dict(command=command, cwd=str(args.cwd or Path.cwd()), started_utc=start,
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  wall_s=time.perf_counter()-tick, exit_code=result.returncode,
                  stdout_sha256=hashlib.sha256(stdout.read_bytes()).hexdigest(),
                  stderr_sha256=hashlib.sha256(stderr.read_bytes()).hexdigest())
    receipt.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
