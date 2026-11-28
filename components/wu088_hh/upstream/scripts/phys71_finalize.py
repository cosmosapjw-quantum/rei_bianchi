#!/usr/bin/env python3
"""Reuse complete PHYS71 numerical evidence and correct only its analytic bound."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from wu088_hh.phys71_finalize import finalize


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--campaign',type=Path,default=ROOT/'research/hh_phys71_20261020/d3/run_l36_t65_stable_errors')
    p.add_argument('--low-archive',type=Path,default=ROOT/'research/hh_phys68_20261019/profiles/PROFILE_PANEL_PAYLOADS_20261019.zip')
    p.add_argument('--band-archive',type=Path,default=ROOT/'archives/PHYS69_BAND_PAYLOADS_20261019.zip')
    args=p.parse_args()
    print(json.dumps(finalize(ROOT,args.campaign,args.low_archive,args.band_archive),sort_keys=True))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'status':'FAIL','error':type(exc).__name__,'message':str(exc),'HH_R10':'OFF'}),file=sys.stderr)
        raise SystemExit(1)
