"""All-lane coherent quadratic auditor and independent-field falsification witness."""
from __future__ import annotations
import importlib.util,sys,json,time,subprocess,os,hashlib
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
LANES=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')
TRAINING=np.asarray([[-1,-1],[-1,0],[-1,1],[0,-1],[0,0],[0,1],[1,-1],[1,0],[1,1]],float)
WITHHELD=np.asarray([[-.5,-.5],[-.5,.5],[0,0],[.5,-.5],[.5,.5]],float)
FIELDS=('x_HII','x_HeII','x_HeIII','log_T')
def _load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
quad=_load('affine_tm_coherent_quad',HERE/'quadratic_fit.py')
def _env():
 e=dict(os.environ);e['PYTHONUNBUFFERED']='1';e['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
 for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):e[n]='1'
 return e
def _token(label):return hashlib.sha256(label.encode()).hexdigest()[:16]
def _endpoint(lane,mode,alpha=0.0,beta=0.0):
 cache=STAGE/'data'/'endpoint_cache'/lane.lower();label=f'{mode}:{alpha:+.6f}:{beta:+.6f}';tok=_token(label);jp=cache/f'{tok}.json';npz=cache/f'{tok}.npz';log=cache/f'{tok}.log'
 if not (jp.is_file() and npz.is_file()):
  cache.mkdir(parents=True,exist_ok=True);cmd=[sys.executable,str(HERE/'field_trial.py'),'--repo',str(REPO),'--lane',lane,'--mode',mode,'--alpha',str(alpha),'--beta',str(beta),'--json-output',str(jp),'--npz-output',str(npz)]
  with log.open('w') as h:r=subprocess.run(cmd,cwd=REPO,env=_env(),stdout=h,stderr=subprocess.STDOUT,text=True,timeout=180)
  if r.returncode:raise RuntimeError(f'endpoint worker failed {lane}/{label}: {log}')
 row=json.loads(jp.read_text());
 with np.load(npz,allow_pickle=False) as d:obs=np.array(d['observables'],copy=True)
 return row|{'mode':mode,'alpha':float(alpha),'beta':float(beta),'cache_token':tok},obs
def _run_grid(lane,points):
 rows=[];arr=[]
 for a,b in points:
  r,x=_endpoint(lane,'coherent',float(a),float(b));rows.append(r);arr.append(x)
 return rows,np.stack(arr)
def _outside(candidate,lower,upper):
 scale=np.maximum.reduce([np.abs(lower),np.abs(upper),np.full_like(lower,np.nextafter(0.0,1.0))]);tol=128*np.finfo(float).eps*scale
 raw=(candidate<lower)|(candidate>upper);rawmag=np.where(raw,np.maximum(lower-candidate,candidate-upper),0.0)
 mask=(candidate<lower-tol)|(candidate>upper+tol);mag=np.where(mask,np.maximum(lower-candidate,candidate-upper),0.0)
 return ([int(np.count_nonzero(mask[i])) for i in range(4)],[float(np.max(mag[i])) for i in range(4)],
         [int(np.count_nonzero(raw[i])) for i in range(4)],[float(np.max(rawmag[i])) for i in range(4)])
def run_lane(lane):
 started=time.perf_counter();tr,train=_run_grid(lane,TRAINING);wr,withheld=_run_grid(lane,WITHHELD);fit=quad.QuadraticEndpointFit.fit(TRAINING,train);pred=fit.evaluate(WITHHELD);absres=np.max(np.abs(pred-withheld),axis=(0,2));corn=train[(np.abs(TRAINING[:,0])==1)&(np.abs(TRAINING[:,1])==1)];lo=corn.min(0);hi=corn.max(0);glo,ghi=fit.exact_box(residual_absolute=absres[:,None]);width=[float(np.max(ghi[i]-glo[i])) for i in range(4)]
 adv=[]
 for name,mode in (('MAX_HEII_LOCAL','max-heii'),('MIN_HEII_LOCAL','min-heii')):
  row,x=_endpoint(lane,mode);counts,mags,raw_counts,raw_mags=_outside(x,lo,hi);adv.append({'name':name,'hard_gates_pass':bool(row['hard_gates_pass']),'local_error':float(row['local_error']),'endpoint_sha256':row['endpoint_sha256'],'outside_counts':dict(zip(FIELDS,counts)),'maximum_outside_magnitude':dict(zip(FIELDS,mags)),'raw_outside_counts':dict(zip(FIELDS,raw_counts)),'raw_maximum_outside_magnitude':dict(zip(FIELDS,raw_mags))})
 return {'lane':lane,'training_rows':tr,'withheld_rows':wr,'training_residual':float(fit.training_residual),'withheld_max_absolute_residual':dict(zip(FIELDS,map(float,absres))),'coherent_empirical_widths':dict(zip(FIELDS,width)),'coherent_all_hard_gates_pass':bool(all(r['hard_gates_pass'] for r in tr+wr)),'adversarial':adv,'adversarial_outside_count':int(sum(sum(a['outside_counts'].values()) for a in adv)),'elapsed_s':float(time.perf_counter()-started),'claim':'COHERENT_TWO_GLOBAL_PARAMETER_AUDITOR_ONLY'}
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--lane',choices=LANES,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();res=run_lane(a.lane);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'lane':a.lane,'elapsed_s':res['elapsed_s'],'outside':res['adversarial_outside_count']}))
if __name__=='__main__':main()
