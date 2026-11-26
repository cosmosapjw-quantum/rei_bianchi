import numpy as np,json,hashlib
from pathlib import Path
from scipy.interpolate import RegularGridInterpolator
from scipy.integrate import simpson
from scipy.constants import elementary_charge,epsilon_0,m_e,c,h,k
D=Path(__file__).resolve().parent;P=D.parent/'r118c3b_ff_balance/gauntff.dat'
r=np.array([list(map(float,l.split('#')[0].split())) for l in P.read_text().splitlines() if len(l.split('#')[0].split())==81][:146])
interp=RegularGridInterpolator((-16+.2*np.arange(146),-6+.2*np.arange(81)),r)
e2=elementary_charge**2/(4*np.pi*epsilon_0)*1e9;me=m_e*1e3;cc=c*100;kk=k*1e7;hh=h*1e7
pref=32*np.pi*e2**3/(3*me*cc**3)*np.sqrt(2*np.pi/(3*me*kk))*kk/hh
x=np.geomspace(1e-10,60,8193);rows=[]
for T in (8,10,20,50,100,132,236,1e3,1e4):
 for z in (1,2):
  g=interp(np.c_[np.log10(x),np.full(len(x),np.log10(z*z*13.605693122994/(8.617333262145e-5*T)))])
  gb=simpson(g*np.exp(-x)*x,x=np.log(x))
  physical=pref*np.sqrt(T)*gb;legacy=1.43e-27*np.sqrt(T)*(1.1+.34*np.exp(-(5.5-np.log10(T))**2/3))
  rows.append(dict(T=T,Z=z,integrated_gaunt=float(gb),physical=float(physical),legacy=float(legacy),ratio=float(physical/legacy)))
print('prefactor',pref,'rows',rows)
(D/'ABSOLUTE.json').write_text(json.dumps(dict(prefactor=float(pref),rows=rows,sha=hashlib.sha256(P.read_bytes()).hexdigest()),indent=2)+'\n')
