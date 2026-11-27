"""Independent Decimal Gauss-Legendre oracle of the direct two-body stress."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import json,sys,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from energy_gain import SexticLaw,FULL_WITNESS
from nonthermal_d_birth import HE4_REST_MEV,GAMMA_MEV

law=SexticLaw(FULL_WITNESS)
def dec(x):return D(x.numerator)/D(x.denominator)

def legendre(n,x):
 p0=D(1);p1=x
 for k in range(2,n+1):p0,p1=p1,((2*k-1)*x*p1-(k-1)*p0)/k
 return p1,n*(x*p1-p0)/(x*x-1)

def direct(n,precision):
 with localcontext() as ctx:
  ctx.prec=precision+10
  a=D('3727.3794118');m=D('1875.61294500');e=D(330)
  s=a*a+2*a*e;b=e*(s/4-m*m).sqrt()/s.sqrt();e0=(a+e)/2
  z=D(14297)/52500
  def fun(u):
   q=(1-u*u)*(D(1411)/10000-u*u/4+D(33)/25*u**4)/z
   ep=e0+b*u;em=e0-b*u
   return q*((ep*ep-m*m)/ep+(em*em-m*m)/em)
  total=D(0);normalization=D(0);maxroot=D(0)
  for j in range(1,n//2+1):
   # Binary64 cos is only a root seed; Decimal Newton converges independently.
   x=D(str(math.cos(math.pi*(j-.25)/(n+.5))))
   for it in range(50):
    p,dp=legendre(n,x);dx=p/dp;x-=dx
    if abs(dx)<D(10)**(-precision-2):break
   else:raise ArithmeticError('Legendre root did not converge')
   p,dp=legendre(n,x);maxroot=max(maxroot,abs(p))
   w=2/((1-x*x)*dp*dp)
   total+=w*(fun(x)+fun(-x));normalization+=2*w
  return {'value':str(total),'nodes':n,'decimal_precision':precision,
          'root_residual_max':str(maxroot),'weight_sum_error':str(abs(normalization-2))}

values=[direct(16,50),direct(32,80)]
with localcontext() as ctx:
 ctx.prec=90
 v=D(values[1]['value']);delta=abs(v-D(values[0]['value']))
 # Numerical oracle stability scale, not a rigorous quadrature enclosure.
 allowance=delta+D('1e-42')
 rows=[]
 for n in range(7):
  t=law.trace_enclosure(n);lo=dec(t['lower_MeV_per_event']);hi=dec(t['upper_MeV_per_event'])
  inside=lo-allowance<=v<=hi+allowance
  if not inside:raise AssertionError('quadrature outside exact enclosure')
  rows.append(dict(order=n,lower_exact=str(t['lower_MeV_per_event']),upper_exact=str(t['upper_MeV_per_event']),width_exact=str(t['width_MeV_per_event']),lower_decimal=str(lo),upper_decimal=str(hi),width_decimal=str(hi-lo),quadrature_inside=inside))
 bins=law.bins(('-1','-4/5','-1/5','2/5','1'))
 wrong=sum(b['number']*(b['lo_x']+b['hi_x'])/2 for b in bins)
 result={'scope':'chosen normalized sextic law; conditional event; no physical rate',
  'method':'Decimal16/32-point Gauss-Legendre; direct [(Eplus^2-M^2)/Eplus+(Eminus^2-M^2)/Eminus] times explicit q, independent of moment series',
  'reference_runs':values,'resolution_precision_difference':str(delta),
  'numerical_oracle_uncertainty':str(allowance),'oracle_is_rigorous_interval':False,
  'intervals':rows,'r':str(law.trace_enclosure(0)['r']),'m2':str(law.even_moment(1)),
  'bin_number_total':str(sum(b['number'] for b in bins)),'bin_first_x_total':str(sum(b['first_x'] for b in bins)),
  'midpoint_mutant_first_x':str(wrong),'midpoint_mutant_kinetic_error_MeV':str(dec(law.trace_enclosure(0)['r']).sqrt()*dec((HE4_REST_MEV+GAMMA_MEV)/2)*dec(wrong)),
  'bins':[{k:str(v) for k,v in b.items()} for b in bins],
  'new_physical_IVPs':0,'old_science_replays':0,'physical_activation':False,'L4':False}
(ROOT/'evidence/NUMERICAL_REFERENCE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'trace_MeV_per_event':values[-1]['value'],'order4_width_MeV_per_event':rows[4]['width_decimal'],'all7_enclosures_contain_reference':all(t['quadrature_inside'] for t in rows),'precision_resolution_difference':str(delta),'midpoint_mutant_kinetic_error_MeV':result['midpoint_mutant_kinetic_error_MeV']}))
