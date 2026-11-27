"""Bounded author numerical controls; heavy target implementation is C++."""
from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parent.parent;HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(ROOT/'exact_weights/deps')]
import numpy as np,mpmath as mp
from guarded_foreign import AnalyticForeign,CD,LD
mp.mp.dps=80
def mr(x):
 a,b=LD(x).as_integer_ratio();return mp.mpf(a)/b
def mc(z):return mp.mpc(mr(z.real),mr(z.imag))
def run():
 h=AnalyticForeign(HERE/'cache');xs=np.array([complex(a,b) for a in [-32,-8,-.5,-1e-8,0,1e-8,.5,8,32,63.999999,64,64.000001,128,1e6,1e12] for b in [0,2,-2]],CD)
 f=h.boys(xs);rows=[];eps=mr(np.finfo(LD).eps)
 for i,x in enumerate(xs):
  for j in range(10):
   ref=mp.hyp1f1(mp.mpf(j)+mp.mpf('.5'),mp.mpf(j)+mp.mpf('1.5'),-mc(x))/(2*j+1)
   ratio=abs(mc(f[i,j])-ref)/(eps*max(1,abs(ref)))
   rows.append({'x':[str(x.real),str(x.imag)],'order':j,'error_over_eps':float(ratio),'PASS':bool(ratio<=128)})
 result={'status':'PASS' if all(r['PASS'] for r in rows) else 'FAIL','count':len(rows),'max_error_over_eps':max(r['error_over_eps']for r in rows),'rows':rows,'identity':h.identity,'reference':'mp80 independent1F1; exact longdouble input conversion'}
 out=HERE/'BOYS_RESULTS.json'
 if out.exists():raise FileExistsError(out)
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','count','max_error_over_eps']}),flush=True)
 return result
if __name__=='__main__':sys.exit(0 if run()['status']=='PASS' else 1)
