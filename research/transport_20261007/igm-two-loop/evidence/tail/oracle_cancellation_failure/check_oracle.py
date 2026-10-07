from pathlib import Path
import subprocess,json,math,time,resource,hashlib
from decimal import Decimal as D, localcontext, getcontext
getcontext().prec=100
getcontext().Emin=-999999999
getcontext().Emax=999999999
b=Path(__file__).resolve().parent

cases=[]
def add(f,q,r,h,e): cases.append([f,q,*r,h,e])
for h in [0,1e-100,1e-12,1e-6,0.1,1,8]:
 for f,q in [(0.,-math.inf),(-math.inf,0.),(-1000.,-900.),(0.,0.)]: add(f,q,[0,0,0],h,50000)
for z in [1e-12,.249999999,.25,.250000001,1,10,100,800,1100,1e6]:
 for f,q in [(0.,-math.inf),(-math.inf,0.),(-1000.,-900.),(0.,0.)]: add(f,q,[z/.001,0,0],.001,14)
for r in [[1e-200,0,0],[1,2,3],[1e3,2e3,1e3],[1e-8,0,0]]:
 for h in [1e-12,.1,1,3]:add(-745.,-1000.,r,h,50000)
add(0,0,[1e300,0,0],1e-300,14)
add(-1100,-1000,[1.3662730718869406e6,0,0],.0008,13.7)
input_text=''.join(' '.join(repr(x) for x in c)+'\n' for c in cases)
(b/'CASES.json').write_text(json.dumps(cases,indent=2)+'\n')
t0=time.perf_counter();p=subprocess.run([str(b/'probe')],input=input_text,text=True,capture_output=True);(b/'ORACLE_NATIVE.stdout').write_text(p.stdout);(b/'ORACLE_NATIVE.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
worst=D(0);records=[];checks=0;zeros=0;underflow=0
names=['n','u','an0','an1','an2','be0','be1','be2','red','qn','qe','outn','oute']
def mp(x): return D.from_float(float(x))
for ci,(c,line) in enumerate(zip(cases,p.stdout.splitlines(),strict=True)):
 f,q,*rest=c;r=rest[:3];h,e=rest[3:];f=D(0) if f==-math.inf else mp(f).exp();q=D(0) if q==-math.inf else mp(q).exp();h=mp(h);e=mp(e);r=list(map(mp,r));lam=sum(r);eps=mp(1.602176634e-12)
 def J(k):return h if k==0 else (1-(-k*h).exp())/k
 if h==0: N=f;C=D(0);K=D(0)
 else:
  N=f*(-lam*h).exp()+q*J(lam)
  # independent analytic time integrals, high precision; adapt precision for tinyz.
  with localcontext() as ctx:
   ctx.prec=800 if (h and abs(h)<D('1e-70')) or (lam and abs(lam*h)<D('1e-70')) else 160
   cs=h*h/2 if lam==0 else (h-J(lam))/lam
   ks=1-(1+h)*(-h).exp() if lam==0 else (J(1)-J(lam+1))/lam
   C=f*J(lam)+q*cs;K=eps*e*(f*J(lam+1)+q*ks)
 ref=[N,eps*e*(-h).exp()*N,*[x*C for x in r],*[x*K for x in r],K,q*h,q*eps*e*J(1),D(0),D(0)]
 logpart,valuepart,loss,lowpart=line.split('|');gl=list(map(float,logpart.split(',')));gv=list(map(float,valuepart.split(',')));glo=list(map(float,lowpart.split(',')))
 for j,x in enumerate(ref):
  checks+=1
  if x==0:
   zeros+=1;assert gl[j]==-math.inf,(ci,names[j],gl[j]);continue
  assert math.isfinite(gl[j]),(ci,names[j],'lost positive')
  err=abs((mp(gl[j])+mp(glo[j])-x.ln()).exp()-1);worst=max(worst,err)
  if gv[j]==0:underflow+=1
  records.append({'case':ci,'owner':names[j],'log_hi':gl[j],'log_lo':glo[j],'ref_log':str(x.ln()),'relative_error':float(err),'pass':err<=D('3e-12')})
  assert err<=D('3e-12'),(ci,c,names[j],str(err),gl[j],str(x.ln()))
(b/'ORACLE_RECORDS.json').write_text(json.dumps(records,indent=2)+'\n')
result={'status':'PASS','cases':len(cases),'owner_checks':checks,'exact_zero_owners':zeros,'positive_zero_readouts':underflow,'max_positive_owner_relative_error':float(worst),'target':3e-12,'oracle_precision_dps':'Decimal100 logs;Decimal160/800 analytic integral workspace','reference':'Exact positive exponential characteristic solution; independent high precision closed integral formula','underflow_cert_scope':'Represented positive tail readout loss only; no IVP, quadrature, total roundoff bound','elapsed_wall_seconds':time.perf_counter()-t0,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'source_sha256':hashlib.sha256((b/'../../repo/research/transport_20261007/igm-two-loop/src/tail.rs').resolve().read_bytes()).hexdigest()}
(b/'ORACLE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
