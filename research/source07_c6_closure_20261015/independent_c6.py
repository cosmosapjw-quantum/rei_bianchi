"""Independent continuum MD14/BB50K frozen-gas Verner source-rate reference.
No Rust code imports, no q-grid closure or historical gas/cosmological ODE.
"""
from pathlib import Path
import json,math
from scipy.integrate import quad
fit=[
 (13.60,0.4298,5.475e4,32.88,2.963,0.,0.,0.),
 (24.59,13.61,949.2,1.469,3.188,2.039,0.4434,2.136),
 (54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)
]
binding=[13.598434599702,24.587389011,54.41776]
kT=50000*1.380649e-16/1.602176634e-12
c=29979245800.0
DT=1e10
edges=[13.6,24.59,54.42,100.]
def ph(E):return E*E/math.expm1(E/kT)
znorm=sum(quad(ph,l,h,epsabs=1e-13,epsrel=1e-13)[0] for l,h in zip(edges,edges[1:]))
def sigma(E,par):
 eth,e0,s0,ya,p,yw,y0,y1=par
 if E<eth:return 0.
 x=E/e0-y0;y=math.hypot(x,y1)
 return s0*((x-1.)**2+yw*yw)*y**(p/2.-5.5)*(1.+math.sqrt(y/ya))**(-p)*1e-18
def calc(n):
 def f(E,ix):
  rate=[c*Ni*sigma(E,parameter) for Ni,parameter in zip(n,fit)]
  r=sum(rate);loss=-math.expm1(-r*DT)
  if ix<3:return (ph(E)/znorm)*(loss*rate[ix]/r if r else 0.0)
  if ix==3:return (ph(E)/znorm)*(sum(loss*rr/r*(E-binding[j]) for j,rr in enumerate(rate)) if r else 0)
  if ix==4:return (ph(E)/znorm)*(sum(loss*rr/r*binding[j] for j,rr in enumerate(rate)) if r else 0)
  raise ValueError(ix)
 return [sum(quad(lambda E:f(E,i),lo,hi,epsabs=1e-14,epsrel=2e-12,limit=300)[0]
       for lo,hi in zip(edges,edges[1:])) for i in range(5)]
g0=6.67430e-8;m_p=1.67262192595e-24;h0=67.4e5/3.085677581491367e24
rho=3*h0*h0/(8*math.pi*g0)
Y=.2454
nh0=(1-Y)*(0.0224/.674**2)*rho/m_p
nh=nh0*21**3
He=nh*Y/(4*(1-Y))
rate_N=4.298036114764196e-8
conditions={
 "owner_initial":{"neutral_cm3":[nh*(1.-.0002),He,0.0]},
 "manufactured_HeII":{"neutral_cm3":[nh*(1.-.0002),He,2e-5]},
 "HeII_only":{"neutral_cm3":[0.0,0.0,2e-5]},
}
for data in conditions.values():
 moments=calc(data["neutral_cm3"])
 data["continuous_absorbed_per_H"]=[x*rate_N for x in moments[:3]]
 data["continuous_heat_eV_per_H"]=moments[3]*rate_N
 data["continuous_binding_eV_per_H"]=moments[4]*rate_N
 print(data["neutral_cm3"],data["continuous_absorbed_per_H"],data["continuous_heat_eV_per_H"])
Path(__file__).parent.joinpath("evidence/INDEPENDENT_C6.json").write_text(json.dumps({"source":"BB50K normalized 13.6..100eV; physical frozen Verner","absorbers":conditions,"rate_N_per_H":rate_N,"dt_s":DT},indent=2))
