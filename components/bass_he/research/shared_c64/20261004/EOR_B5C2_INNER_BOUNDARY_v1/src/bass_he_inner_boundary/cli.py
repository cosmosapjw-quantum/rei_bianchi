"""Explicit local atomic-boundary CLI. No physical-curve or scattering promotion."""
from __future__ import annotations
import argparse,json,os,tempfile,hashlib,sys
from pathlib import Path
from .core import ua_limit,radial_seed,ContractError,NumericalFailure


def _pairs(ps):
 d={}
 for k,v in ps:
  if k in d:raise ContractError('duplicate JSON key: '+k)
  d[k]=v
 return d


def write_create_only(path,obj):
 path=Path(path)
 if path.exists() or path.is_symlink():raise FileExistsError(str(path))
 b=(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
 fd,temp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
  os.link(temp,path) # atomic create-if-absent, never replace an existing output
  dfd=os.open(path.parent,os.O_RDONLY)
  try:os.fsync(dfd)
  finally:os.close(dfd)
 finally:
  if os.path.exists(temp):os.unlink(temp)
 return hashlib.sha256(b).hexdigest()


def main(argv=None):
 p=argparse.ArgumentParser(prog='bass-he-inner-boundary');s=p.add_subparsers(dest='cmd',required=True)
 for name in ('ua','seed'):
  c=s.add_parser(name)
  if name=='seed':c.add_argument('input',type=Path)
  c.add_argument('--out',type=Path,required=True);c.add_argument('--production',action='store_true')
 a=p.parse_args(argv)
 try:
  if a.production:raise ContractError('PRODUCTION_NOT_AUTHORIZED; local polynomial is not the actual inner optical curve')
  if a.cmd=='ua':out=ua_limit(branch='2p_sigma_to_1s_sigma')
  else:
   if a.input.is_symlink():raise ContractError('input symlink forbidden')
   req=json.loads(a.input.read_text(),object_pairs_hook=_pairs,parse_constant=lambda x:(_ for _ in ()).throw(ContractError('nonfinite JSON constant')))
   keys={'schema','input_kind','ell','coulomb','potential','width','energy','radius','order'}
   if not isinstance(req,dict) or set(req)!=keys or req['schema']!='bass-he.b5c2.local-polynomial.v1' or req['input_kind']!='DECLARED_LOCAL_MODEL':raise ContractError('exact declared-local-polynomial input schema required')
   out=radial_seed(**{k:v for k,v in req.items() if k not in ('schema','input_kind')})
   out['request_sha256']=hashlib.sha256(a.input.read_bytes()).hexdigest()
  sha=write_create_only(a.out,out)
  print(json.dumps({'written':str(a.out),'sha256':sha,'physical_accuracy_certified':False}));return 0
 except (ContractError,NumericalFailure,OSError,json.JSONDecodeError,OverflowError) as e:
  print(type(e).__name__+': '+str(e),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
