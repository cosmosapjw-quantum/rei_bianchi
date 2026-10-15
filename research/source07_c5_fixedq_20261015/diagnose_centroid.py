"""Independent Python continuous-blackbody fixed-log-bin centroid diagnosis."""
import math
import json
from pathlib import Path
from scipy.integrate import quad
from scipy.special import roots_legendre
import numpy as np
G=6.67430e-8
H0=67.4e5/3.085677581491367e24
Y=.2454
MP=1.67262192595e-24
nH0=3*H0*H0/(8*math.pi*G)*(0.0224/.674**2)*(1-Y)/MP
h=nH0*(21**3)*(1-0.0002); he=nH0*21**3*Y/(4*(1-Y))
c=29979245800.
dt=1e10
p={
'HI':(13.6,.4298,5.475e4,32.88,2.963,0.,0.,0.),
'HeI':(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),
}
binding={'HI':13.598434599702,'HeI':24.587389011}
def sigma(k,e):
 th,e0,s0,ya,pw,yw,y0,y1=p[k]
 if e<th:return 0.
 x=e/e0-y0;y=math.hypot(x,y1)
 return s0*((x-1)**2+yw*yw)*y**(pw/2-5.5)*(1+math.sqrt(y/ya))**(-pw)*1e-18
def rate(e):
 return [c*h*sigma('HI',e),c*he*sigma('HeI',e)]
kt=50000*1.380649e-16/1.602176634e-12
def shape(e):return e*e/math.expm1(e/kt)
norm=quad(shape,13.6,100,epsabs=1e-12,epsrel=1e-13)[0]
def frac(e):
 a,b=rate(e);lam=a+b
 loss=-math.expm1(-lam*dt)
 return loss,sum(loss*r/lam*(e-binding[k]) for r,k in zip([a,b],['HI','HeI'])) if lam else 0.
reference=[quad(lambda e:shape(e)*frac(e)[i]/norm,13.6,24.59,epsabs=1e-13)[0]+quad(lambda e:shape(e)*frac(e)[i]/norm,24.59,100,epsabs=1e-13)[0] for i in [0,1]]
rows=[]
for N in [64,128,256,512,1024,2048,4096]:
 edges=np.geomspace(13.6,433,N+1)
 acc0=acc1=0.
 for lo,hi in zip(edges[:-1],edges[1:]):
  a=max(13.6,lo);b=min(100,hi)
  if b<=a:continue
  count=quad(shape,a,b,epsabs=1e-11)[0]/norm
  mom=quad(lambda e:e*shape(e),a,b,epsabs=1e-10)[0]/norm
  x0,x1=frac(mom/count)
  acc0+=count*x0;acc1+=count*x1
 rows.append({"N":N,"absorption_rel_err":acc0/reference[0]-1,"heating_rel_err":acc1/reference[1]-1,"total_source_count":sum(quad(shape,max(13.6,lo),min(100,hi))[0]/norm for lo,hi in zip(edges[:-1],edges[1:]) if min(100,hi)>max(13.6,lo))})
out={"neutral":{"nHI":h,"nHeI":he},"continuous_source_reference":{"fraction_absorbed":reference[0],"heating_ev_per_input_photon":reference[1]},"centroid_refinement":rows}
Path(__file__).parent.joinpath("evidence/CENTROID_DIAGNOSIS.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
