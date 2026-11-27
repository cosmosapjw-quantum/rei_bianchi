#!/usr/bin/env python3
"""Emit scoped HH ENERGY06D artifacts from sealed ENERGY06C read-only witnesses."""
import argparse, json, os, pathlib, hashlib, sys
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from birth_correlation import inspect
from c1_tail_contract import uniform_selected_kummer_tail


def write_json(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True)
    args=ap.parse_args()
    out=pathlib.Path(args.out).resolve()
    if out.exists():
        raise SystemExit('ENERGY06D_REFUSE_EXISTING_OUTPUT_NAMESPACE')
    out.mkdir(parents=True)
    n=inspect(ROOT)
    write_json(out/'ANGULAR_BIRTH.json',n)
    mat=[]
    for k in (1,3,5,7):
        for r in range(3):
            row=uniform_selected_kummer_tail(k,r)
            mat.append({x:(str(y) if isinstance(y,Fraction) else y) for x,y in row.items()})
    write_json(out/'C1_SERIES_TAIL.json',{'status':'AUXILIARY_SELECTED_HYPERGEOMETRIC_TAIL_ONLY',
                                      'replaces_old_source_bound':False,'cases':mat,
                                      'full_box_holomorphic_admission':None,
                                      'C1_new_science_dispatch':0})
    return 0
if __name__=='__main__':raise SystemExit(main())
