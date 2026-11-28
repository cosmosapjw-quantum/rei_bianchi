"""Actual frozen107 target primitive; C++ handles grid evaluation and reductions."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sys,json,time,ctypes,hashlib,resource
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path[:0]=[str(HERE),str(ROOT/'exact_weights/deps'),str(ROOT/'issue_resolution/h_numerics')]
import numpy as np,mpmath as mp
from guarded_foreign import AnalyticForeign,ptr,DP,CD,LD
from run_sentinel import inputs,nodes,exact_weights,contract
mp.mp.dps=70
def mr(x):
 a,b=LD(x).as_integer_ratio();return mp.mpf(a)/b
def mc(z):return mp.mpc(mr(z.real),mr(z.imag))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atom(path,**kw):
 if path.exists():raise FileExistsError(path)
 tmp=path.with_suffix('.tmp')
 with tmp.open('wb') as f:np.savez_compressed(f,**kw)
 os.replace(tmp,path)
def gamma_sectors(h,a,b,t,z,q,gs,gw,side,W):
 # Source-preserving full reviewed radial geometry once/plane; repeated original reducer.
 sectors=np.zeros((len(gs),5,2,3),CD)
 masks=[]
 for k in range(5):
  w=np.zeros_like(W);w[2*k]=W[2*k];masks.append(w)
 for ig,gamma in enumerate(gs):
  extra=LD(gamma)**2;R=np.array([2,0,z],LD)
  geo,packed,rad=h._ingredients(a,b,t[:,None],t[None,:],[0,0,0],-R,0,q,extra1=extra if side==1 else 0,extra2=extra if side==2 else 0,foreign=-R,order=1)
  for k,w in enumerate(masks):
   out=np.empty((2,3),CD);sa=np.empty((2,3),LD)
   code=h.lib.hguard_foreign(geo[8].size,ptr(packed),2*packed.size,ptr(rad),2*rad.size,ptr(w,DP),w.size,ptr(out),2*out.size,ptr(sa),sa.size)
   if code:raise RuntimeError(code)
   sectors[ig,k]=out
 return np.stack([h.gamma_sum(sectors[:,k],gw)for k in range(5)]),sectors

def main():
 if (HERE/'TARGET_RESULTS.json').exists():raise FileExistsError('target results immutable')
 h=AnalyticForeign(HERE/'cache');inp=inputs();a=float(inp['exponents'][3]);b=float(inp['exponents'][8]);speed=float(inp['v'])
 norm0=np.sqrt(2)*float(inp['pref'])*(2*a/np.pi)**.75*(2*b/np.pi)**.75
 norm=norm0*np.array([[1,2*np.sqrt(a),2*np.sqrt(a)],[1,2*np.sqrt(b),2*np.sqrt(b)]])
 gs,gw=nodes(80);gw*=2/np.sqrt(np.pi);rows=[];arithmetic=[];bridges=[]
 start=time.perf_counter();eps=mr(np.finfo(LD).eps)
 for B in [16,128]:
  t,w=nodes(B);U,V=exact_weights(t,w);W=contract(U,V,inp['C'])[0]
  for sign in [1,-1]:
   for side in [1,2]:
    name=f'B{B}_side{side}_s{sign}'
    tick=time.perf_counter();cpu=time.process_time()
    old=np.stack([h.foreign_plane(a,b,t[:,None],t[None,:],3.,sign*speed,g,side,W)[0]for g in gs]);baseline=h.gamma_sum(old,gw)
    baseline_wall=time.perf_counter()-tick;baseline_cpu=time.process_time()-cpu
    tick=time.perf_counter();cpu=time.process_time()
    even=h.even_foreign(a,b,t[:,None],t[None,:],3.,sign*speed,side,W)
    even_wall=time.perf_counter()-tick
    odd=[];oddsa=[]
    for g in gs:
     val,sa,_=h.odd_plane(a,b,t[:,None],t[None,:],3.,sign*speed,g,side,W);odd.append(val);oddsa.append(sa)
    odd=np.stack(odd);oddsa=np.stack(oddsa);oddvalue=h.gamma_sum(odd,gw);combined=even['total']+oddvalue
    split_wall=time.perf_counter()-tick;split_cpu=time.process_time()-cpu
    sector_ref,sector_planes=gamma_sectors(h,a,b,t,3.,sign*speed,gs,gw,side,W)
    diff=abs((combined-baseline)*norm);sector_diff=abs((even['per_sector']-sector_ref)*norm)
    if B==16:
     # Full actual native contraction replay, small grid only.
     raw=even['raw_fields'].reshape(-1,5,6);we=W[::2].reshape(5,-1)
     for k in range(5):
      for c in range(6):
       vals=[mc(raw[i,k,c])*mr(we[k,i])for i in range(raw.shape[0])]
       ref=mp.fsum(vals);sa=mp.fsum(abs(x)for x in vals);error=abs(mc(even['per_sector'].reshape(5,6)[k,c])-ref)
       ratio=error/(eps*sa)if sa else mp.mpf(0)
       arithmetic.append({'case':name,'power':2*k,'component':c,'ratio_eps_sumabs':float(ratio),'PASS':bool(ratio<=128)})
     # Odd-only independent code path same-source bridge at distinct gamma nodes.
     wo=np.zeros_like(W);wo[1::2]=W[1::2]
     for ig in [0,39,79]:
      ref,sa,_=h.foreign_plane(a,b,t[:,None],t[None,:],3.,sign*speed,gs[ig],side,wo)
      gap=np.abs(odd[ig]-ref);den=np.maximum(sa,LD(1e-4900))*np.finfo(LD).eps
      bridges.append({'case':name,'gamma_index':ig,'exact':bool(np.array_equal(ref,odd[ig])),'max_eps_sumabs':float(np.max(gap/den)),'PASS':bool(np.all(gap<=128*den))})
    row={'case':name,'B':B,'side':side,'sign':sign,'full_foreign_max_abs_difference_Eh':float(diff.max()),'sector_max_abs_difference_Eh':float(sector_diff.max()),'sector_by_power_max_Eh':[float(x.max())for x in sector_diff],
     'baseline_power_wall_seconds':baseline_wall,'baseline_power_cpu_seconds':baseline_cpu,'split_wall_seconds':split_wall,'split_cpu_seconds':split_cpu,'even_wall_seconds':even_wall,'observed_speed_ratio':baseline_wall/split_wall,
     'original_2e7_H_screen_PASS':bool(np.all(diff<=2e-7)),'identity':h.identity}
    # Keep complete fields only when needed for independent review; no sign conjugation is imposed.
    saved={'even_fields':even['raw_fields']}if B==16 or sign==1 else {}
    atom(HERE/(name+'.npz'),baseline=baseline,full_gamma_planes=old,combined=combined,even=even['total'],even_per=even['per_sector'],even_sumabs=even['sumabs'],even_per_sumabs=even['per_sector_sumabs'],gamma_even_ref=sector_ref,gamma_even_planes=sector_planes,odd=oddvalue,odd_gamma_planes=odd,odd_plane_sumabs=oddsa,gamma_weights=gw,gamma_nodes=gs,W=W,t=t,norm=norm,metadata=json.dumps(row),**saved)
    rows.append(row);print(json.dumps(row),flush=True)
 # Checked symmetry is a diagnostic from separately evaluated signs, not assigned values.
 conjugacy=[]
 for B in [16,128]:
  for side in [1,2]:
   with np.load(HERE/f'B{B}_side{side}_s1.npz')as p,np.load(HERE/f'B{B}_side{side}_s-1.npz')as m:
    conjugacy.append({'B':B,'side':side,'max_abs':float(np.max(abs(p['combined'].conj()-m['combined']))),'even_sector_max_abs':float(np.max(abs(p['even_per'].conj()-m['even_per'])))})
 result={'status':'PASS_SCOPED_PRIMITIVE'if all(r['original_2e7_H_screen_PASS']for r in rows)and all(r['PASS']for r in arithmetic+bridges)else'FAIL','rows':rows,'arithmetic':arithmetic,'odd_bridges':bridges,'conjugacy':conjugacy,'wall_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'source_sha256':{str(p.relative_to(ROOT)):sha(p)for p in [HERE/'analytic.cpp',HERE/'guarded_foreign.py',HERE/'build_native.py',Path(__file__),ROOT/'production/radial_power/radial_power.cpp']},'claim_ceiling':'Actual ia3ib8z3 foreign primitive only. No orbital/all94 convergence, no gamma rigorous bound or physics admission. Single sequential timing per configuration; same reviewedpower scalar baseline.'}
 (HERE/'TARGET_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
 if result['status'].startswith('FAIL'):raise SystemExit(1)
if __name__=='__main__':main()
