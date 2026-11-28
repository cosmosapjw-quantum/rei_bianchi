import math,json
from scipy.integrate import quad
B=27.0;k=0.7
res=[]
for j in [0,20,64,1000]:
 L=j*(j+1)
 def terms(x):
  r=B+x; w=-math.expm1(-x); wp=math.exp(-x); beta=r-B/2
  f=complex(wp+(L+1/(k*k))*w/(r*r), -2*(k+1/(k*r))*wp+w/(k*r*r))
  p=complex(wp,w/(k*r))
  energy=abs(p)**2+B*(w/r)**2+(1-B/r)*L*(w/r)**2
  rhs=2*(f*(beta*p.conjugate()+complex(0,w/k))).real
  flux=(f*w).imag
  return energy,rhs,flux
 vals=[quad(lambda x:terms(x)[a],0,math.inf,epsabs=2e-10,epsrel=5e-13,limit=300) for a in range(3)]
 left=vals[0][0]+B/2;right=vals[1][0]
 res.append({'j':j,'lhs_with_trace':left,'rhs_with_coulomb_flux':right,'relative_residual':abs(left-right)/max(abs(left),abs(right)), 'flux_plus_k':vals[2][0]+k,'quad_abs_error_max':max(v[1] for v in vals)})
print(json.dumps(res,indent=2))
