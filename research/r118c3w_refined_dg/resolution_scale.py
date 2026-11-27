"""Scale audit for collisional equilibrium and resolved shear forcing."""
import numpy as np,json
from scipy.constants import c,G,electron_volt
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 h=np.genfromtxt(D.parent/'r118c3u_positive_owner/birth_1024_32ray/history.csv',names=True,delimiter=',')
 norm=D.parent/'r118c3u_positive_owner/birth_1024_32ray/NORMALIZATION.txt';nh0=float(norm.read_text().split('=')[1])*1e6
 H0=2.1842852410855023e-18;rho0=3*c*c*H0*H0/(8*np.pi*G)
 # Local validity intersection in the declared single-ion OU closure:
 # relaxation rate >= kappa H, collisional Knudsen <=0.1.
 from scipy.constants import k,m_e,e,epsilon_0,hbar
 T=h['T'];ne=h['ne']*1e6;v=np.sqrt(k*T/m_e);wp=np.sqrt(ne*e**2/(epsilon_0*m_e));nu=4*np.sqrt(2*np.pi)/3*ne*e**4*np.log((v/wp)/np.maximum(e**2/(4*np.pi*epsilon_0*k*T),hbar/(m_e*v)))/((4*np.pi*epsilon_0)**2*np.sqrt(m_e)*(k*T)**1.5)
 H=H0*h['h'];qmax=.1*nu*c/(wp*v)
 eq=[]
 for ratio in [1.,10.,100.]:
  qmin=np.sqrt(ratio*H/(nu-ratio*H));ok=qmin<qmax
  eq.append(dict(gamma_over_H=ratio,q_min_range=[float(min(qmin)),float(max(qmin))],q_max_range=[float(min(qmax)),float(max(qmax))],fraction_of_native_samples_with_overlap=float(np.mean(ok)),start=[float(qmin[0]),float(qmax[0])],end=[float(qmin[-1]),float(qmax[-1])]))
 rows={}
 for p in sorted(D.iterdir()):
  if not p.is_dir() or not (p/'RETURN.txt').exists():continue
  a=np.genfromtxt(p/'history.csv',names=True,delimiter=',');P=np.stack([a[k] for k in ['corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']],axis=1)
  # Orthonormal STF components in same basis as BASS.
  S=np.stack([(P[:,0]-P[:,1])/np.sqrt(2),(-P[:,0]-P[:,1]+2*P[:,2])/np.sqrt(6),np.sqrt(2)*P[:,3],np.sqrt(2)*P[:,4],np.sqrt(2)*P[:,5]],axis=1)
  fac=nh0/a['a']**3*electron_volt/rho0;force=3*fac[:,None]*S/a['h'][:,None]**2;ds=np.trapezoid(force,np.log(a['a']),axis=0)
  s=np.array([a[f'S{i}'][-1] for i in range(5)]);ulp=np.spacing(abs(s));u=float(np.linalg.norm(ulp));rows[p.name]=dict(direct_shear_source_integral=ds.tolist(),norm=float(np.linalg.norm(ds)),terminal_shear_ulp_norm=u,ratio_to_ulp=float(np.linalg.norm(ds)/u),component_ratio_to_ulp=(abs(ds)/ulp).tolist())
 out=dict(thermal=dict(nu_range=[float(min(nu)),float(max(nu))],wp_range=[float(min(wp)),float(max(wp))],H_range=[float(min(H)),float(max(H))],eq=eq),shear=rows,scope='conditional OU fluid and background-variation overlap; direct frozen-trajectory STF source integral only, not a rigorous coupled-feedback upper bound')
 (D/'RESOLUTION_SCALE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
