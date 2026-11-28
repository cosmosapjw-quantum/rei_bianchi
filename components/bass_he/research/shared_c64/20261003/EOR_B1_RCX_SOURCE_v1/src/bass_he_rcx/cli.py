"""Run declared optical models. No physical-source labels or output replacement."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .optical import ContractError, NumericalFailure, solve_partial_wave, partial_sum


def _object(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ContractError('DUPLICATE_JSON_KEY: '+k)
        out[k]=v
    return out


def _constant(x):raise ContractError('NONFINITE_JSON_VALUE: '+x)


def load_config(path: str | Path):
    p=Path(path)
    if p.is_symlink():raise ContractError('input symlink not supported')
    try:data=json.loads(p.read_text(),object_pairs_hook=_object,parse_constant=_constant)
    except (ValueError,TypeError,UnicodeError) as e:raise ContractError('invalid JSON') from e
    keys={'schema','data_class','energy_over_E0','ell_values','edges','potential_over_E0','widths_over_E0'}
    if not isinstance(data,dict) or set(data)!=keys:raise ContractError('exact input schema keys required')
    if data['schema']!='bass-he.declared-optical-model.v1' or data['data_class']!='MANUFACTURED_REFERENCE':
        raise ContractError('only declared manufactured reference inputs admitted by this release')
    ell=data['ell_values']
    if not isinstance(ell,list) or not ell or any(type(l) is not int or not 0<=l<=32 for l in ell):
        raise ContractError('ell_values: nonempty distinct list of integers 0..32 required')
    if len(ell)!=len(set(ell)):raise ContractError('duplicate partial waves')
    return data


def write_new(path: str | Path, value):
    path=Path(path)
    if path.exists() or path.is_symlink():raise FileExistsError(str(path))
    blob=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(blob);f.flush();os.fsync(f.fileno())
        # Atomic no-replace publication, including races after exists() above.
        os.link(tmp,path)
        dfd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def main(argv=None):
    p=argparse.ArgumentParser(prog='bass-he-optical-reference')
    p.add_argument('--input',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--request-rct',action='store_true')
    args=p.parse_args(argv)
    try:
        if args.request_rct:raise ContractError('SOURCE_UNAVAILABLE: physical RCT table and channel attribution not admitted')
        if args.out.exists() or args.out.is_symlink():raise FileExistsError(str(args.out))
        x=load_config(args.input)
        rows=[solve_partial_wave(x['energy_over_E0'],l,x['edges'],x['potential_over_E0'],x['widths_over_E0']) for l in x['ell_values']]
        out={'schema':'bass-he.optical-reference-run.v1','input':x,'partial_waves':rows,
             'partial_sum':partial_sum(rows),'physical_RCT_prediction':False}
        write_new(args.out,out)
        return 0
    except (ContractError,NumericalFailure,OSError,ValueError) as e:
        print(type(e).__name__+': '+str(e),file=sys.stderr);return 2
