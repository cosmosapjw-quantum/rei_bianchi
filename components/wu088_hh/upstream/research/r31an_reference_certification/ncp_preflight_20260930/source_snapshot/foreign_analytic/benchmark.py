"""Four matched alternating-order primitive timings, one native thread."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sys,json,time,hashlib,statistics,resource
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path[:0]=[str(HERE),str(ROOT/'exact_weights/deps'),str(ROOT/'issue_resolution/h_numerics')]
import numpy as np
from guarded_foreign import AnalyticForeign
from run_sentinel import inputs,nodes,exact_weights,contract
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=HERE/'BENCHMARK_RESULTS.json'
 if out.exists():raise FileExistsError(out)
 h=AnalyticForeign(HERE/'cache');inp=inputs();a=float(inp['exponents'][3]);b=float(inp['exponents'][8]);speed=float(inp['v'])
 t,w=nodes(128);U,V=exact_weights(t,w);W=contract(U,V,inp['C'])[0]
 gs,gw=nodes(80);gw*=2/np.sqrt(np.pi)
 norm0=np.sqrt(2)*float(inp['pref'])*(2*a/np.pi)**.75*(2*b/np.pi)**.75
 norm=norm0*np.array([[1,2*np.sqrt(a),2*np.sqrt(a)],[1,2*np.sqrt(b),2*np.sqrt(b)]])
 def baseline():
  planes=np.stack([h.foreign_plane(a,b,t[:,None],t[None,:],3.,speed,g,1,W)[0]for g in gs])
  return h.gamma_sum(planes,gw)
 def split():
  even=h.even_foreign(a,b,t[:,None],t[None,:],3.,speed,1,W)['total']
  planes=np.stack([h.odd_plane(a,b,t[:,None],t[None,:],3.,speed,g,1,W)[0]for g in gs])
  return even+h.gamma_sum(planes,gw)
 rows=[]
 # Prior target validation already warmed both loaded native paths. No extra warmup.
 for repeat in range(4):
  order=['baseline','split']if repeat%2==0 else['split','baseline'];r={'repeat':repeat,'order':order};values={}
  for name in order:
   tick=time.perf_counter();cpu=time.process_time();values[name]={'baseline':baseline,'split':split}[name]()
   r[name+'_wall_seconds']=time.perf_counter()-tick;r[name+'_cpu_seconds']=time.process_time()-cpu
  r['max_gap_Eh']=float(np.max(abs((values['baseline']-values['split'])*norm)))
  r['observed_wall_ratio']=r['baseline_wall_seconds']/r['split_wall_seconds']
  r['observed_cpu_ratio']=r['baseline_cpu_seconds']/r['split_cpu_seconds']
  rows.append(r);print(json.dumps(r),flush=True)
 med={n:statistics.median(r[n]for r in rows)for n in ('baseline_wall_seconds','split_wall_seconds','baseline_cpu_seconds','split_cpu_seconds')}
 result={'status':'PASS'if all(r['max_gap_Eh']<=2e-7 for r in rows)else'FAIL','case':'ia3 ib8 z3 B128 gamma80 side1 ETF+ full107','rows':rows,'medians':med,'median_wall_speed_ratio':med['baseline_wall_seconds']/med['split_wall_seconds'],'median_cpu_speed_ratio':med['baseline_cpu_seconds']/med['split_cpu_seconds'],'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'identity':h.identity,'source_sha256':sha(Path(__file__)),'scope':'Four repetitions on this host only; all geometry/native fields/reductions/allocations timed. Compilation and common frozen weights excluded equally. Previous target run warmed both implementations. FullH speed and hardware portability unmeasured. Independent review may share other CPUs; report CPU as well as wall time.'}
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
 if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
