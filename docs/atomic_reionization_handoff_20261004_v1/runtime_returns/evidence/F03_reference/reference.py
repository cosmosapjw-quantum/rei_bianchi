from pathlib import Path
import json,hashlib
import numpy as np
from scipy.integrate import solve_ivp
r=Path.cwd();p=r/'docs/atomic_reionization_handoff_20261004_v1/threads/rei_bianchi/CONTROLLED_FIXTURE.json';a=json.loads(p.read_text());c=a['constants'];chi=np.array(list(c['threshold_eV'].values()));E=np.array(a['photons']['energy_eV']);sigma=np.array(list(a['photons']['sigma_cm2'].values()));alpha=np.array(list(a['rates']['alpha_cm3_s'].values()));beta=np.array(list(a['rates']['electron_impact_cm3_s'].values()));nh=a['initial']['n_H_cm3'];nhe=a['initial']['n_He_cm3'];kb=c['k_B_erg_K'];ev=c['eV_erg'];clight=c['c_cm_s'];i=a['initial'];pop=np.array([nh*(1-i['x_HII']),nh*i['x_HII'],nhe*i['x_HeI'],nhe*i['x_HeII'],nhe*i['x_HeIII']]);initial=np.r_[pop,np.log(i['T_K']),i['photon_density_cm3'],0.,np.zeros(15)]
# Independent coordinates: five populations, lnT, photons, escape and15 ledgers.
def rhs(t,z):
 lower=z[[0,2,3]];upper=z[[1,3,4]];ne=z[1]+z[3]+2*z[4];npart=sum(z[:5])+ne;T=np.exp(z[5]);photo=clight*sigma*lower[:,None]*z[6:9][None,:];ci=lower*ne*beta;rr=upper*ne*alpha;j=photo.sum(axis=1)+ci-rr
 dp=np.array([-j[0],j[0],-j[1],j[1]-j[2],j[2]]);du=ev*((photo*(E[None,:]-chi[:,None])).sum()-(chi*ci).sum())-1.5*kb*T*rr.sum();dlnT=2*du/(3*kb*npart*T)-j.sum()/npart;escape=(rr*(chi*ev+1.5*kb*T)).sum();return np.r_[dp,dlnT,-photo.sum(axis=0),escape,photo.ravel(),ci,rr]
results={}
for method in ['DOP853','Radau']:
 sol=solve_ivp(rhs,[0,a['integration']['t_end_s']],initial,method=method,rtol=2e-12,atol=np.r_[np.full(5,1e-18),1e-13,np.full(3,1e-18),1e-29,np.full(15,1e-18)])
 assert sol.success
 z=sol.y[:,-1];results[method]={'observables':[z[1]/nh,z[3]/nhe,z[4]/nhe,z[5]],'T':float(np.exp(z[5])),'populations':z[:5].tolist(),'photons':z[6:9].tolist(),'escape':z[9],'evaluations':sol.nfev}
print(json.dumps(results,indent=2));assert max(abs(np.array(results['DOP853']['observables'])-results['Radau']['observables']))<1e-9
out={'fixture_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'coordinate_basis':'five populations plus lnT; no Rust flow code','methods':results,'finite_reference_scaled_acceptance':2e-4,'uniform_error_claim':False};(r/'.cuh/fastest-track/REI-F03/reference.json').write_text(json.dumps(out,indent=2)+'\n')
