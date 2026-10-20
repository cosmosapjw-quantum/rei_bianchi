#!/usr/bin/env python3
"""Bounded verification router; requires the selected Rust/offline runtime.

No dependency installation, benchmark, external upload or source formatting is
performed. Per-stage original commands/logs remain in their receipt files.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

parser=argparse.ArgumentParser()
parser.add_argument("output",type=Path)
parser.add_argument("--stage",choices=("tests","native","all"),default="all")
args=parser.parse_args()
out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
here=Path(__file__).resolve().parent
base=here.parent/"repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019"
env=dict(os.environ,CARGO_TARGET_DIR=str(out/"target"))
records=[]
def run(argv,label):
    with (out/(label+".log")).open("w") as stream:
        result=subprocess.run(argv,env=env,stdout=stream,stderr=subprocess.STDOUT)
    records.append({"name":label,"argv":argv,"exit":result.returncode})
    (out/"COMMANDS.json").write_text(json.dumps(records,indent=2)+"\n")
    if result.returncode:
        raise SystemExit(label+" FAILED")
if args.stage in ("tests","all"):
    for name,manifest in [("parent",base/"parent/br05/Cargo.toml"),("br06",base/"br06/Cargo.toml"),("native_rates",here/"native_rates/Cargo.toml"),("rates",here/"rates/Cargo.toml"),("photon",here/"photon/Cargo.toml"),("atomic",here/"atomic_theory/catalog/Cargo.toml")]:
        run(["cargo","test","--offline","--locked","--manifest-path",str(manifest),"--all-targets"],"TEST_"+name)
        run(["cargo","clippy","--offline","--locked","--manifest-path",str(manifest),"--all-targets","--","-D","warnings"],"CLIPPY_"+name)
if args.stage in ("native","all"):
    science=out/"native_science"
    run([sys.executable,str(here/"integration/RUN_STAGE.py"),str(science)],"NATIVE_SCIENCE")
    run([sys.executable,str(here/"integration/VERIFY_RESTORE.py"),str(science)],"NATIVE_GOLDEN")
print(json.dumps({"status":"PASS","stage":args.stage,"commands":len(records)}))
