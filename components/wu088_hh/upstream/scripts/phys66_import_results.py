"""Attach new analytic components to old, unchanged hash-verified PHYS64 results."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from wu088_hh.phys66_campaign_ledger import inspect_archive
from wu088_hh.phys66_radial_budget import to_jsonable

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,default=ROOT/'research/hh_phys64_20261018/ncp_run/SOURCE_RESULTS.zip')
    p.add_argument('--out',type=Path,default=ROOT/'research/hh_phys66_20261018/c5c8/results/INHERITED_NCP_LEDGER.json');a=p.parse_args()
    r=inspect_archive(a.archive);a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(to_jsonable(r),indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:r[k] for k in ('schema','manifest_payload_count','inherited_total_success_count','extended_cases_verified','new_NCP_jobs_executed','total_numerical_error_certified')},indent=2))
if __name__=='__main__':main()
