"""Create-only original-native HE27 A/B cases; explicit finite budgets."""
from pathlib import Path
import sys,json,time,hashlib,os,resource,traceback,argparse
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
sys.path[:0]=[str(ROOT/'src'),str(REPO/'he25_proper_birth_20261016/src')]
from native import NativeOwner
from physics import Model
from transport import solve_transport
from reference import solve_reference
BINARY=Path('/root/HE25_NCP_BIRTH_20261016/build/he25_owner_server')
EXPECTED='22d11447300381d5cd02d06e13f312e3e2aa3716eaecf60d3bcdb4d436a434d5'
def atomic(p,v):
 tmp=p.with_suffix(p.suffix+'.partial')
 with tmp.open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
 os.link(tmp,p);tmp.unlink()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--lane',choices=['baseline','sourcecut'],required=True);p.add_argument('--method',choices=['transport','Radau','DOP853'],default='transport');p.add_argument('--source-module',choices=['sourcecut','sourcecut_v2','sourcecut_v3','sourcecut_fast'],default='sourcecut');p.add_argument('--source-table-nodes',type=int,default=512);p.add_argument('--m',type=int,default=4);p.add_argument('--angles',type=int,default=4);p.add_argument('--q',type=float,default=0);p.add_argument('--n',type=int,default=16);p.add_argument('--rtol',type=float,default=3e-11);p.add_argument('--atol',type=float,default=3e-13);a=p.parse_args()
 out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
 resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
 ident={'args':vars(a),'owner_source':'f7830e2f55e7a1938bc3c98f61b60651f8dae474','binary_sha256':hashlib.sha256(BINARY.read_bytes()).hexdigest(),'sha256':{str(f.relative_to(REPO)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in [ROOT/'src',REPO/'he25_proper_birth_20261016/src',REPO/'he26_moving_cutoff_20261016/src'] for f in folder.glob('*.py')}}
 atomic(out/'IDENTITY.json',ident);start=time.perf_counter()
 try:
  assert ident['binary_sha256']==EXPECTED
  if a.lane=='sourcecut':
   from importlib import import_module
   cls=import_module(a.source_module).SourceCutModel
  else:cls=Model
  with NativeOwner(BINARY,evidence_path=out/'native.jsonl.gz',expected_binary_sha256=EXPECTED) as owner:
   kwargs=dict(m=a.m,angles=a.angles,q=a.q)
   if a.lane=='sourcecut' and a.source_module in ['sourcecut_v2','sourcecut_v3','sourcecut_fast']:kwargs['source_table_nodes']=a.source_table_nodes
   model=cls(owner,**kwargs)
   if a.method=='transport':r=solve_transport(model,n=a.n,cohort_path=out/'birth_cohorts.npz')
   else:r=solve_reference(model,rtol=a.rtol,atol=a.atol,method=a.method)
   if hasattr(model,'source_diagnostics'):atomic(out/'SOURCE_DIAGNOSTICS.json',model.source_diagnostics)
   if hasattr(model,'source_table_diagnostics'):atomic(out/'SOURCE_TABLE_DIAGNOSTICS.json',model.source_table_diagnostics)
   r['native_calls']=owner.calls
  assert abs(r['number_defect'])<=3e-15 and abs(r['energy_defect_ev'])<=3e-12 and r['gas_positive'] and r['min_photon']>=0 and max(abs(v) for v in r['species_defect'])<=3e-12,'ORIGINAL_LEDGER_GATE'
  atomic(out/'RESULT.json',{'status':'NATIVE_VERIFIED_SCOPED','elapsed_s':time.perf_counter()-start,'result':r})
 except Exception as e:
  atomic(out/'FIRST_FAILURE.json',{'status':'HOLD_FIRST_FAILURE','error':str(e),'traceback':traceback.format_exc(),'elapsed_s':time.perf_counter()-start});raise
if __name__=='__main__':main()
