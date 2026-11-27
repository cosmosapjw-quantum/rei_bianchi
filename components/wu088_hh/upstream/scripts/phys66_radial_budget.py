"""Source-locked PHYS66 radial components; no total-error certification."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from wu088_hh.phys66_radial_budget import certificate,plan_radius,to_jsonable,numeric_summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz')
    p.add_argument('--out',type=Path,default=ROOT/'research/hh_phys66_20261018/local_verification/results/COEFFICIENT_RADIAL_BOUNDS.json')
    a=p.parse_args()
    certificates=[certificate(a.source,64,T,3) for T in (39,43,55,65,75)]
    result={'schema':'PHYS66_R5_SOURCE_V1','certificates':certificates,
            'display_noncertifying':[numeric_summary(c) for c in certificates],
            'planning_goals_chosen_not_total_tolerances':{1:'1e-30',2:'1e-54',3:'1e-78'},
            'plan':plan_radius(64,{1:'1e-30',2:'1e-54',3:'1e-78'}),'HH_R10':'OFF'}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(to_jsonable(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(result['display_noncertifying'],indent=2,allow_nan=False))
    print('ANALYTIC_COMPONENT_RADIUS',result['plan']['outer'])
if __name__=='__main__':main()
