#!/usr/bin/env python3
"""Create a host/build-bound tuning profile from a topology pool benchmark."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from wu088_hh.autotune import make_tuning_profile


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pool-report',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--locality-tie-fraction',type=float,default=0.02)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError('new tuning profile path required')
    report=json.loads(a.pool_report.read_text())
    profile=make_tuning_profile(report,report_sha256=sha256_file(a.pool_report),locality_tie_fraction=a.locality_tie_fraction)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f:
        json.dump(profile,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'status':'HOST_TUNING_PROFILE_CREATED_NOT_PROVIDER_PROMOTED','profile':str(a.out),'selected':profile['selected']}))
if __name__=='__main__':main()
