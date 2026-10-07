"""Independent Decimal160 oracle for explicit cutoff endpoint geometry."""
import argparse,hashlib,json,math,resource,subprocess,time
from decimal import Decimal as D,getcontext
from pathlib import Path
getcontext().prec=160
getcontext().Emin=-999999999
getcontext().Emax=999999999
root=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--probe',type=Path,default=root/'target/tail_anchor_probe');a.add_argument('--output',type=Path,default=root/'evidence/tail_anchor');a=a.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
def d(x):return D.from_float(float(x))
inputs=[]
for c,r in [(13.6,[3.,0.,0.]),(24.59,[1.,2.,0.]),(54.42,[1.,2.,3.])]:
 for e in [c,math.nextafter(c,math.inf),c*1.001,100.,50000.]:
  for f,q in [(0.,-math.inf),(-math.inf,0.),(-1000.,-1100.)]:inputs.append([f,q,*r,e,c])
inputs.extend([[0.,0.,0.,0.,0.,14.,13.6],[-1000.,-math.inf,1e6,0.,0.,14.,13.6],[-math.inf,-math.inf,0.,0.,0.,13.6,13.6]])
(out/'CASES.json').write_text(json.dumps([[str(x) if not math.isfinite(x) else x for x in r] for r in inputs],indent=2)+'\n')
t=time.perf_counter();p=subprocess.run([str(a.probe.resolve())],input=''.join(' '.join(map(str,r))+'\n' for r in inputs),text=True,capture_output=True);(out/'NATIVE.stdout').write_text(p.stdout);(out/'NATIVE.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
records=[];worst=D(0);h_worst=D(0);budget_worst=D(0);roundtrip_worst=0;count=0;zero=0
for i,(row,line) in enumerate(zip(inputs,p.stdout.splitlines(),strict=True)):
 lf,lq,*other=row;rates=list(map(d,other[:3]));e,c=map(d,other[3:]);parts=line.split('|');hf,endf,anchor_rel=map(float,parts[0].split(','));h=d(hf);got=[tuple(map(float,q.split(','))) for q in parts[1:]]
 f=D(0) if lf==-math.inf else d(lf).exp();q=D(0) if lq==-math.inf else d(lq).exp();lam=sum(rates);eps=d(1.602176634e-12)
 he=(e/c).ln();he_err=abs(h/he-1) if he else abs(h);h_worst=max(h_worst,he_err);assert he_err<D('3e-15'),(i,'geometry',str(he_err))
 def J(k):return h if k==0 else (1-(-k*h).exp())/k
 if h==0: N=f;C=D(0);K=D(0)
 else:
  N=f*(-lam*h).exp()+q*J(lam)
  C=f*J(lam)+q*(h*h/2 if lam==0 else (h-J(lam))/lam)
  K=eps*e*(f*J(lam+1)+q*(1-(1+h)*(-h).exp() if lam==0 else (J(1)-J(lam+1))/lam))
 owners=[N,eps*c*N,*[r*C for r in rates],*[r*K for r in rates],K,q*h,q*eps*e*J(1),D(0),D(0)]
 exported=owners[:];exported[11]=exported[0];exported[12]=exported[1];exported[0]=D(0);exported[1]=D(0)
 for j,(ref,(hi,lo)) in enumerate(zip(owners+exported,got,strict=True)):
  count+=1
  if ref==0:zero+=1;assert hi==-math.inf and lo==0;continue
  err=abs((d(hi)+d(lo)-ref.ln()).exp()-1);worst=max(worst,err);assert err<=D('3e-12'),(i,j,str(err))
  records.append({'case':i,'owner_index':j,'relative_error':float(err),'log_hi':hi,'log_lo':lo})
 # Endpoint anchor differs from generic exponential geometry by the explicit
 # round-trip defect; this is audited, not redistributed to make energy exact.
 energy_in=eps*e*f+owners[10]
 balance=owners[1]+sum(owners[5:8])+owners[8]-energy_in
 budget_err=abs(balance/energy_in) if energy_in else abs(balance);budget_worst=max(budget_worst,budget_err)
 assert budget_err<=D('3e-12'),(i,'energy anchor consistency',str(budget_err))
 roundtrip_worst=max(roundtrip_worst,abs(anchor_rel))
(out/'ORACLE_RECORDS.json').write_text(json.dumps(records,indent=2)+'\n')
r={'status':'PASS','cases':len(inputs),'owner_checks_including_export':count,'exact_zero_owners':zero,'max_positive_owner_relative_error':float(worst),'positive_owner_gate':3e-12,'max_h_relative_error_vs_exact_log_ratio':float(h_worst),'geometry_gate':3e-15,'max_exact_formula_energy_anchor_defect_relative':float(budget_worst),'max_reported_binary64_endpoint_roundtrip_relative':roundtrip_worst,'precision_decimal_digits':160,'scope':'fixed-rate single-characteristic positive owners plus explicit cutoff endpoint; no physical event topology shift','cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,'wall_seconds':time.perf_counter()-t,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'source_sha256':hashlib.sha256((root/'src/tail.rs').read_bytes()).hexdigest()}
(out/'ORACLE_RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
