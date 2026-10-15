#!/usr/bin/env python3
"""Run on the authorized owner PC; stage a frozen archive to a fresh NCP task.

This script transfers source only. It does not build or launch any case.
The existing project SSH record supplies connection arguments without printing
the remote endpoint or identity path.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shlex
import subprocess
import tarfile

TASK = "/root/REI_FLRW_COVARIANT_20261015_003"
RECORD = Path("/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/axbi_goal_20261014/execution/NCP_ACCESS_RECOVERY_20261014.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    if hashlib.sha256(args.archive.read_bytes()).hexdigest() != args.sha256:
        raise SystemExit("archive byte identity mismatch")
    with tarfile.open(args.archive, "r:gz") as archive:
        members = archive.getmembers()
        if any(not m.isfile() or PurePosixPath(m.name).is_absolute()
               or ".." in PurePosixPath(m.name).parts for m in members):
            raise SystemExit("archive must contain only repo-relative regular files")
        manifest = archive.extractfile("SOURCE_SHA256SUMS.txt").read().decode()
        for line in manifest.splitlines():
            expected, name = line.split("  ", 1)
            data = archive.extractfile(name).read()
            if hashlib.sha256(data).hexdigest() != expected:
                raise SystemExit("source member byte identity mismatch")
    saved = json.loads(RECORD.read_text())
    previous = shlex.split(saved["command"])
    identity = previous[previous.index("-i") + 1]
    ssh = ["ssh", "-T", "-i", identity, "-o", "IdentitiesOnly=yes",
           "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
           "-o", "StrictHostKeyChecking=yes", "-o", "UpdateHostKeys=no",
           "-o", "ControlMaster=no", "-o", "ControlPath=none", "-p", "22",
           saved["user"] + "@" + saved["host"]]
    command = " && ".join([
        "umask 077", "mkdir " + shlex.quote(TASK),
        "mkdir " + shlex.quote(TASK + "/stage"),
        "tar -xzf - -C " + shlex.quote(TASK + "/stage"),
        "cd " + shlex.quote(TASK + "/stage"),
        "sha256sum --quiet -c SOURCE_SHA256SUMS.txt"])
    with args.archive.open("rb") as source:
        subprocess.run(ssh + [command], stdin=source, check=True)
    print(json.dumps({"status": "SOURCE_STAGED_ONLY", "task": TASK,
                      "archive_sha256": args.sha256, "builds": 0, "case_launches": 0}))


if __name__ == "__main__":
    main()
