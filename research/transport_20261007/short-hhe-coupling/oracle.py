"""Independent 80-digit Decimal affine-solution integrals of exact binary64 inputs."""
import csv,decimal,json,pathlib
D=pathlib.Path(__file__).resolve().parent
ctx=decimal.getcontext();ctx.prec=80
V=decimal.Decimal
F=lambda x:V.from_float(float(x))
EPS=F('1.602176634e-12')
checks=[]
for index,row in enumerate(csv.DictReader((D/'results/kernel_samples.csv').open())):
 f,q,h,e=[F(row[k]) for k in ['f','q','h','e']];rates=[F(row[f'r{i}']) for i in range(3)];lam=sum(rates)
 def integral(k):return (1-(-k*h).exp())/k if k else h
 if lam:
  n=f*(-lam*h).exp()+q/lam*(1-(-lam*h).exp())
  ni=(f-q/lam)*integral(lam)+q*h/lam
  ei=EPS*e*((f-q/lam)*integral(lam+1)+q/lam*integral(V(1)))
 else:
  n=f+q*h;ni=f*h+q*h*h/2
  ei=EPS*e*(f*integral(V(1))+q*(1-(h+1)*(-h).exp()))
 expected={'n':n,'u':EPS*e*(-h).exp()*n,'qn':q*h,'qe':EPS*e*q*integral(V(1)),'red':ei}
 expected.update({f'a{i}':rates[i]*ni for i in range(3)})
 expected.update({f'b{i}':rates[i]*ei for i in range(3)})
 for key,truth in expected.items():
  actual=F(row[key]);error=abs(actual-truth)
  ratio=error/(abs(truth)*V('3e-12')) if truth else (V(0) if actual==0 else V('Infinity'))
  checks.append(dict(case=index,component=key,absolute_error=float(error),tolerance_ratio=float(ratio),passed=ratio<=1))
result={'method':'80-digit Decimal exact-input integral of independently written affine N(t) solution','component_checks':len(checks),'maximum_live_oracle_samples':1,'passed':all(c['passed'] for c in checks),'worst_tolerance_ratio':max(c['tolerance_ratio'] for c in checks),'checks':checks}
(D/'results/INDEPENDENT_KERNEL_ORACLE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
raise SystemExit(0 if result['passed'] else 1)
