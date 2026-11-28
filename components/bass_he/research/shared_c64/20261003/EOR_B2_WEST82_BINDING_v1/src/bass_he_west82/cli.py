"""Source-bound table export and declared-model computation. Never a physical fit."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .optical import ContractError, NumericalFailure, solve_partial_wave, partial_sum
from .source import load_resonances


def _pairs(items):
    d={}
    for k,v in items:
        if k in d:raise ContractError('DUPLICATE_JSON_KEY')
        d[k]=v
    return d


def _nonfinite(x):raise ContractError('NONFINITE_JSON_VALUE')


def write_new(path,value):
    p=Path(path)
    if p.exists() or p.is_symlink():raise FileExistsError(str(p))
    b=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    fd,t=tempfile.mkstemp(prefix='.'+p.name+'.',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
        os.link(t,p)
        d=os.open(p.parent,os.O_RDONLY)
        try:os.fsync(d)
        finally:os.close(d)
    finally:
        if os.path.exists(t):os.unlink(t)


def main(argv=None):
    p=argparse.ArgumentParser(prog='bass-he-west82')
    sub=p.add_subparsers(dest='cmd',required=True)
    t=sub.add_parser('table');t.add_argument('--root',required=True,type=Path);t.add_argument('--out',required=True,type=Path)
    s=sub.add_parser('solve');s.add_argument('--input',required=True,type=Path);s.add_argument('--out',required=True,type=Path)
    s.add_argument('--physical-rct',action='store_true')
    a=p.parse_args(argv)
    try:
        if a.out.exists() or a.out.is_symlink():raise FileExistsError(str(a.out))
        if a.cmd=='table':
            result=load_resonances(a.root/'data/WEST82_TABLE_I.json',a.root/'source/PhysRevA.26.3164.pdf')
        else:
            if a.physical_rct:raise ContractError('PHYSICAL_RCT_ARRAYS_AND_MODEL_ADMISSION_REQUIRED')
            if a.input.is_symlink():raise ContractError('INPUT_SYMLINK_REFUSED')
            m=json.loads(a.input.read_text(),object_pairs_hook=_pairs,parse_constant=_nonfinite)
            required={'data_class','energy_over_E0','ell_values','edges','potential_over_E0','widths_over_E0'}
            if not isinstance(m,dict) or set(m)!=required or m['data_class']!='MANUFACTURED_REFERENCE':
                raise ContractError('DECLARED_MANUFACTURED_SCHEMA_REQUIRED')
            ls=m['ell_values']
            if not isinstance(ls,list) or not ls or any(type(l) is not int or not 0<=l<=64 for l in ls) or len(set(ls))!=len(ls):
                raise ContractError('DISTINCT_INTEGER_PARTIAL_WAVES_REQUIRED')
            rows=[solve_partial_wave(m['energy_over_E0'],l,m['edges'],m['potential_over_E0'],m['widths_over_E0']) for l in ls]
            result={'schema':'bass-he.west82.reference-run.v1','input':m,'partial_waves':rows,
                    'partial_sum':partial_sum(rows),'physical_RCT_prediction':False}
        write_new(a.out,result);return 0
    except (ContractError,NumericalFailure,OSError,ValueError,OverflowError) as e:
        print(type(e).__name__+': '+str(e),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
