"""Independent direct-gamma/Cartesian Wick author reference for even fields."""
from pathlib import Path
import sys,json,time,functools,math
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path[:0]=[str(HERE),str(ROOT/'exact_weights/deps'),str(ROOT/'issue_resolution/h_numerics')]
import numpy as np,mpmath as mp
from guarded_foreign import AnalyticForeign,CD,LD
from run_sentinel import inputs,nodes
mp.mp.dps=70
def mr(x):
 a,b=LD(x).as_integer_ratio();return mp.mpf(a)/b
def mc(z):return mp.mpc(mr(z.real),mr(z.imag))

def oracle(g,side):
 g=[mc(x)for x in g];A=[g[0].real,g[1].real];var0=[1/(2*x)for x in A];d=g[7:10];R=g[10:13];base=g[2];prec=A[side-1]
 @functools.lru_cache(maxsize=20000)
 def integrand(gamma):
  # Direct gamma variable, not the candidate's finite Boys coefficient construction.
  x=gamma*gamma;change=x/(prec+x);var=var0.copy();var[side-1]=1/(2*(prec+x));v=sum(var)
  dd=[d[a]-(1 if side==1 else -1)*change*R[a]for a in range(3)]
  ne=[[g[3],g[4]],[g[5],g[6]]]
  ne[side-1]=[ne[side-1][ang]-change*R[a]for ang,a in enumerate([0,2])]
  pref=base*(prec/(prec+x))**mp.mpf('1.5')*mp.exp(-prec*x/(prec+x)*sum(z*z for z in R))*2/mp.sqrt(mp.pi)
  mu=[]
  for mean in dd:
   arr=[mp.mpf(1),mean]
   for k in range(2,10):arr.append(mean*arr[-1]+(k-1)*v*arr[-2])
   mu.append(arr)
  ans=[]
  for n in range(5):
   M=mp.mpc(0);L=[mp.mpc(0),mp.mpc(0)]
   for i in range(n+1):
    for j in range(n-i+1):
     k=n-i-j;ii=[2*i,2*j,2*k];c=mp.mpf(math.factorial(n))/(math.factorial(i)*math.factorial(j)*math.factorial(k))
     M+=c*mp.fprod(mu[a][ii[a]]for a in range(3))
     for ang,a in enumerate([0,2]):L[ang]+=c*mp.fprod(mu[b][ii[b]+(b==a)]for b in range(3))
   vals=[M,ne[0][0]*M+var[0]/v*(L[0]-dd[0]*M),ne[0][1]*M+var[0]/v*(L[1]-dd[2]*M),M,ne[1][0]*M-var[1]/v*(L[0]-dd[0]*M),ne[1][1]*M-var[1]/v*(L[1]-dd[2]*M)]
   ans.append([pref*z for z in vals])
  return ans
 return lambda n,c:mp.quad(lambda gam:integrand(gam)[n][c],[0,1,mp.inf]),integrand

def main():
 out=HERE/'FIELD_RESULTS.json'
 if out.exists():raise FileExistsError(out)
 h=AnalyticForeign(HERE/'cache');inp=inputs();a=float(inp['exponents'][3]);b=float(inp['exponents'][8]);speed=float(inp['v']);t,_=nodes(128)
 cases=[]
 for name,z,sgn,side,ii,jj in [('actual_z3',3.,1,1,51,79),('actual_z0',0.,-1,2,3,98)]:
  _,g=h.even_geometry(a,b,np.array([t[ii]]),np.array([t[jj]]),z,sgn*speed,side);cases.append((name,side,g.reshape(13,1)))
 A=LD('.7');B=LD('1.3');m1=np.array([.2+.1j,-.1+.15j,.4-.2j],CD);m2=np.array([-.3+.05j,.2-.1j,-.2+.1j],CD);C=np.array([.1,-.2,.05],LD)
 n1=m1-np.array([.12,.04,-.13],LD);n2=m2-np.array([-.09,.01,.11],LD)
 g=np.array([A,B,1.25+.3j,n1[0],n1[2],n2[0],n2[2],*(m1-m2),*(m1-C)],CD).reshape(13,1);cases.append(('noncollinear',1,g))
 gc=g.copy();gc[10:]=0;cases.append(('coincident_insert2',2,gc))
 checks=[];rawcases=[];start=time.perf_counter()
 for name,side,g in cases:
  got=h.even_packed(g,np.ones((5,1),np.float64),side)['raw_fields'].reshape(5,6)
  ref,integrand=oracle(g[:,0],side)
  for n in range(5):
   for c in [0,1,5]:
    expected=ref(n,c);scaled=abs(mc(got[n,c])-expected)/max(1,abs(expected))
    row={'case':name,'side':side,'power':2*n,'component':c,'ref_real':mp.nstr(expected.real,65),'ref_imag':mp.nstr(expected.imag,65),'scaled_error':float(scaled),'PASS':bool(scaled<=mp.mpf('2e-15'))};checks.append(row)
  rawcases.append({'case':name,'side':side,'inputs':[[str(x.real),str(x.imag)]for x in g[:,0]],'cache_info':str(integrand.cache_info())})
  print(json.dumps({'case':name,'done':len(checks),'elapsed':time.perf_counter()-start,'max_error':max(x['scaled_error']for x in checks)}),flush=True)
 result={'status':'PASS'if all(x['PASS']for x in checks)else'FAIL','checks':checks,'cases':rawcases,'count':len(checks),'max_scaled_error':max(x['scaled_error']for x in checks),'wall_seconds':time.perf_counter()-start,'identity':h.identity,'reference':'mp70 direct gamma[0,infinity], Cartesian multinomial and one-dimensional Gaussian moments; no Boys/finite-lambda coefficient recursion'}
 out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
 if result['status']=='FAIL':raise SystemExit(1)
if __name__=='__main__':main()
