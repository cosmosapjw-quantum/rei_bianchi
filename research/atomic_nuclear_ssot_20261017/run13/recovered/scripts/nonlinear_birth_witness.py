"""Manufactured scalar counterexample, NOT the native H/He/D model.

q' = J - lambda*q^2. Positive GL4 birth impulses and exact reaction subflows
have correct source moments but generally a second-order endpoint defect.
"""
from pathlib import Path
import mpmath as mp,csv,json
R=Path(__file__).resolve().parents[1]
def quadrature(dps=60):
 mp.mp.dps=dps
 x,w=mp.gauss_quadrature(4,'legendre')
 return [(x[k]+1)/2 for k in range(4)], [w[k]/2 for k in range(4)]
def impulse_flow(n=1,h=mp.mpf(1),j=mp.mpf(1),lam=mp.mpf(1)):
 nodes,weights=quadrature();v=mp.mpf(0);last=mp.mpf(0)
 for p in range(n):
  for z,w in zip(nodes,weights):
   t=h*(p+z)/n;delta=t-last;v=v/(1+lam*v*delta)+j*h*w/n;last=t
 return v/(1+lam*v*(h-last))
def witness():
 x,w=quadrature();edges=[mp.mpf(0),*x,mp.mpf(1)];cdf=mp.mpf(0);i2=mp.mpf(0);d2=mp.mpf(0)
 for j,(a,b) in enumerate(zip(edges[:-1],edges[1:])):
  if j:cdf+=w[j-1]
  i2+=cdf**2*(b-a)
  d2+=(b**3-a**3)/3-cdf*(b*b-a*a)+cdf*cdf*(b-a)
 assert abs(i2-mp.mpf(1)/3-d2)<mp.mpf('1e-55') and d2>0
 rows=[]
 for n in [1,2,4,8,16,32,64]:
  actual=impulse_flow(n);error=actual-mp.tanh(1)
  rows.append({'panels':n,'native_model':False,'endpoint':float(actual),'exact':float(mp.tanh(1)),'error':float(error),'scaled_error_n2':float(error*n*n)})
 for a,b in zip(rows,rows[1:]):b['observed_order']=float(mp.log(abs(a['error']/b['error']),2))
 with (R/'evidence/NONLINEAR_SOURCE_WITNESS.csv').open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[-1]));wr.writeheader();wr.writerows(rows)
 local=[]
 for h in [mp.mpf('0.1'),mp.mpf('0.01'),mp.mpf('0.001'),mp.mpf('0.0001')]:
  e=impulse_flow(1,h)-mp.tanh(h);local.append({'h':str(h),'error_over_h3':str(e/h**3),'predicted_coefficient':str(-d2)})
 rec={'model':'dimensionless q_prime=1-q^2,q(0)=0, exact tanh(t), NOT_HHeD','precision_digits':60,'D_GL4':str(d2),'cdf_identity_residual':str(i2-mp.mpf(1)/3-d2),'source_moments_max_error':str(max(abs(sum(wi*xi**k for xi,wi in zip(x,w))-mp.mpf(1)/(k+1)) for k in range(8))),'local_coefficient_checks':local,'global_final_observed_order':rows[-1]['observed_order']}
 (R/'evidence/NONLINEAR_SOURCE_WITNESS.json').write_text(json.dumps(rec,indent=2)+'\n');return rec
if __name__=='__main__':print(json.dumps(witness(),indent=2))
