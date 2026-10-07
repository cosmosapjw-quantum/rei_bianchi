"""160-digit Decimal exact-binary-input primitive oracle; does not use candidate quadrature."""
from decimal import Decimal as D, getcontext
import csv,json,pathlib,argparse
getcontext().prec=160
class DecimalMath:
 @staticmethod
 def exp(x):return D(x).exp()
 @staticmethod
 def log(x):return D(x).ln()
 @staticmethod
 def expm1(x):return D(x).exp()-1
mp=DecimalMath()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input',type=pathlib.Path,required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
rows=list(csv.DictReader(args.input.open()))
def value(s):return D.from_float(float(s))
def i0(t,a,b):return b-a if not t else (mp.exp(t*b)-mp.exp(t*a))/t
def i1(t,a,b):return (b*b-a*a)/2 if not t else (mp.exp(t*b)*(t*b-1)-mp.exp(t*a)*(t*a-1))/(t*t)
def z(t,a,b,family):
 if family==0:return i0(t,a,b)
 if family==1:return i0(t,a,b)-i1(t,a,b)
 if family==2:return i1(t,a,b)
 raise ValueError("unknown panel family")
metrics={'log_fraction':0.,'normalized_mean':0.,'mean_exp_eta_relative':0.,'amplitude_log_parts':0.};fail=[];errors=[]
for index,r in enumerate(rows):
 l,hi,beta,a,b=map(value,[r['l'],r['r'],r['beta'],r['a'],r['b']]); width=hi-l; ya=(a-l)/width;yb=(b-l)/width;front=int(r['family'])
 count=z(beta,ya,yb,front);fraction=count/z(beta,D(0),D(1),front)
 mean=mp.exp(l)*z(beta+width,ya,yb,front)/count
 mu=(mp.exp(-a)*mean-1)/mp.expm1(b-a)
 e={'log_fraction':float(abs(value(r['ln_fraction'])-mp.log(fraction))), 'normalized_mean':float(abs(value(r['normalized_mean'])-mu)), 'mean_exp_eta_relative':float(abs(value(r['mean_exp_eta'])/mean-1)), 'amplitude_log_parts':float(abs(value(r['ln_n_hi'])+value(r['ln_n_lo'])-value(r['ln_n'])-mp.log(fraction)))}
 for k,v in e.items():metrics[k]=max(metrics[k],v)
 passed=e['log_fraction']<=3e-12 and e['normalized_mean']<=5e-13 and e['mean_exp_eta_relative']<=3e-12 and e['amplitude_log_parts']<=3e-12
 errors.append({'row':index,**e,'passed':passed})
 if not passed:fail.append({'row':index,'input':r,'error':e})
report={'oracle':'stdlib Decimal160 digits, exact binary64 inputs, independent analytic exponential primitives','cases':len(rows),'component_checks':4*len(rows),'max_errors':metrics,'failed':fail,'all_passed':not fail,'errors':errors}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['errors','failed']},indent=2));print('failures',len(fail));assert not fail
