"""Export the fixed reference dataset, or evaluate its opt-in interpolant."""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
from .core import ContractError,NumericalFailure,load_contract
from .table import build_table,evaluate

INPUTS={
 'OPTICAL_SAMPLES.json':'8786e138a3829b3b82fa2488c775b66c3629a757d4213d4bb33fb3b4f54701ee',
 'SAMPLING_DIAGNOSTICS.json':'0885832450887d1bc1d1c90d36cb6412669bad0cc4fbd96e369146e319058184'}

def load_table(root):
    root=Path(root);load_contract(root/'contract/PREREGISTRATION.json');values=[]
    for name,sha in INPUTS.items():
        path=root/'data'/name
        if path.is_symlink():raise ContractError('input symlink forbidden')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=sha:raise ContractError('reference source identity mismatch')
        values.append(json.loads(raw))
    return build_table(*values)

def write_new(path,value):
    """Atomic, same-directory create-only publication with fsync; never replace."""
    path=Path(path)
    payload=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
        os.link(tmp,path)  # Fails for an existing file or symlink.
        dfd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:
        os.unlink(tmp)

def main(argv=None):
    import sys
    p=argparse.ArgumentParser(prog='bass-he-optical-sampling')
    p.add_argument('--root',required=True,type=Path)
    sub=p.add_subparsers(dest='action',required=True)
    e=sub.add_parser('export');e.add_argument('--out',required=True,type=Path)
    q=sub.add_parser('evaluate');q.add_argument('R',type=float)
    q.add_argument('--allow-midpoint-only',action='store_true')
    q.add_argument('--production',action='store_true');q.add_argument('--out',type=Path)
    args=p.parse_args(argv)
    try:
        t=load_table(args.root)
        value=t if args.action=='export' else evaluate(t,args.R,allow_midpoint_only=args.allow_midpoint_only,production=args.production)
        if args.out:write_new(args.out,value)
        else:print(json.dumps(value,sort_keys=True,indent=2,allow_nan=False))
        return 0
    except (ContractError,NumericalFailure,OSError,ValueError) as exc:
        print(type(exc).__name__+': '+str(exc),file=sys.stderr);return 2
