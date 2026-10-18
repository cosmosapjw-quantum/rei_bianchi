"""Frozen Unit8 C: cold-electron KN kernel and first event; no full transport."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[key]='1'
import hashlib,json,signal,sys,time,shutil
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad,solve_ivp
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[2]
CON=json.loads((ROOT/'spec/GAMMA_TRANSFER_CONTRACT.json').read_text()); C=CON['constants']
ME=C['mec2_eV']; RE=C['re_cm']; ST=8*np.pi*RE**2/3; E0=CON['inputs']['E_gamma_eV']
GL={n:np.polynomial.legendre.leggauss(n) for n in (64,128)}

def angular(E,n=64):
    mu,w=GL[n]; xx=np.asarray(E)[...,None]/ME; t=xx*(1-mu); rr=1/(1+t); loss=t/(1+t)
    ds=np.pi*RE**2*rr**2*(rr+1/rr-(1-mu**2))
    return np.stack([np.sum(w*ds*loss**m,axis=-1) for m in (0,1,2)],axis=-1)

def closed(x):
    return 3*ST/4*((1+x)/x**3*(2*x*(1+x)/(1+2*x)-np.log1p(2*x))+np.log1p(2*x)/(2*x)-(1+3*x)/(1+2*x)**2)

def rdr(r,x):
    mu=1-(1/r-1)/x
    return np.pi*RE**2/x*(r+1/r-(1-mu*mu))

def r_adaptive(E):
    x=E/ME; lo=1/(1+2*x)
    return np.array([quad(lambda r:rdr(r,x)/ST*(1-r)**m,lo,1,epsabs=1e-13,epsrel=2e-12)[0]*ST for m in (0,1,2)])

def input_copies():
    manifest={}
    for name in ('history','kinetics','source'):
        info=CON['inputs'][name]; dest=ROOT/'inputs/laneC'/Path(info['path']).name
        original=ROOT/CON['inputs']['unit7_root']/info['path']; src=dest if dest.exists() else original
        digest=hashlib.sha256(src.read_bytes()).hexdigest()
        if digest!=info['sha256']: raise ValueError('Immutable input mismatch '+name)
        if src!=dest: shutil.copyfile(src,dest)
        manifest[name]={'frozen_original':str(original),'portable_path':str(dest.relative_to(ROOT)),'sha256':digest}
    (ROOT/'inputs/laneC/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def recoil_bins():
    x=E0/ME; kmax=E0*2*x/(1+2*x); edges=np.linspace(0,kmax,257); lo=1-edges[1:]/E0; hi=1-edges[:-1]/E0
    g,w=GL[64]; r=(lo[:,None]+hi[:,None])/2+(hi-lo)[:,None]/2*g
    ds=rdr(r,x)*(hi-lo)[:,None]/2*w; K=E0*(1-r); sig=angular(E0)[0]
    p=ds.sum(axis=1)/sig; k1=(ds*K).sum(axis=1)/sig; k2=(ds*K*K).sum(axis=1)/sig; out=E0*p-k1
    return edges,np.column_stack((p,k1,k2,out))

class Bath:
    def __init__(self,meta): self.m=meta
    def H(self,z):
        x=1+z;m=self.m
        return m['H0_s-1']*np.sqrt(m['Omega_r']*x**4+m['Omega_m']*x**3+m['Omega_Lambda'])
    def rates(self,z,E):
        sig=angular(E); ne=self.m['nb0_cm-3']*self.m['Ye']*(1+z)**3
        return ne[...,None]*C['c_cm_s']*sig/self.H(z)[...,None] if np.ndim(ne) else ne*C['c_cm_s']*sig/self.H(z)
    def thermal(self,z,E):
        kT=C['kB_J_K']*CON['inputs']['T0_K']*(1+z)/C['eV_J']; theta=kT/ME
        return {'kBT_eV':float(kT),'theta_e':float(theta),'sqrt_3theta_e':float(np.sqrt(3*theta)),'4kBT_over_E':float(4*kT/E)}
    def event(self,zs):
        end=np.log((1+zs)/10001)
        def A(u):
            z=(1+zs)*np.exp(-u)-1; E=E0*np.exp(-u)
            return self.rates(z,E)[0]
        tauend=quad(A,0,end,epsabs=1e-10,epsrel=2e-11)[0]; stop=min(tauend,40.)
        sol=solve_ivp(lambda t,u:[1/A(u[0])],(0,stop),[0.],method='DOP853',rtol=1e-10,atol=1e-12,dense_output=True)
        if not sol.success: raise RuntimeError(sol.message)
        vals={}
        for n in (64,128):
            x,w=GL[n]; t=stop*(1+x)/2; wt=w*stop/2*np.exp(-t); u=sol.sol(t)[0]; E=E0*np.exp(-u); sig=angular(E)
            frac=sig[:,1]/sig[:,0]; ust=float(sol.sol(stop)[0]); Est=E0*np.exp(-ust); survival=np.exp(-stop)
            vals[n]=np.array([np.sum(wt*E*frac),np.sum(wt*E*(1-frac))+survival*Est,np.sum(wt*(E0-E))+survival*(E0-Est),np.sum(wt*u)/(-np.expm1(-stop)),np.sum(wt)])
        res=vals[128]; refin=float(np.max(abs(vals[128][:3]-vals[64][:3])/np.maximum(abs(res[:3]),1e-300)))
        inv=[]
        for tau in (np.log(2),1.,10.,stop):
            if tau>stop: continue
            uu=float(sol.sol(tau)[0]); recovered=quad(A,0,uu,epsabs=1e-11,epsrel=2e-11)[0]
            inv.append(abs(recovered-tau)/max(tau,1e-300))
        quant={}
        collision=-np.expm1(-tauend)
        for p in (.05,.5,.95):
            target=-np.log1p(-p); conditional=target>tauend
            if conditional: target=-np.log1p(-p*collision)
            # target never exceeds tau_stop40 for the specified probabilities.
            uu=float(sol.sol(target)[0]); zz=(1+zs)*np.exp(-uu)-1; EE=E0*np.exp(-uu)
            quant[str(p)]={'u':uu,'z':float(zz),'prior_redshift_loss_eV':float(E0-EE),'conditional_on_collision':bool(conditional),'thermal_before_collision':self.thermal(zz,EE)}
        return {'z_source':float(zs),'u_endpoint':float(end),'tau_endpoint':float(tauend),'log_endpoint_no_collision_probability':float(-tauend),'endpoint_no_collision_probability':float(np.exp(-tauend)),'collision_probability_endpoint':float(collision),'tau_stop':float(stop),'u_stop':float(ust),'K_eV':float(res[0]),'photon_first_event_or_stop_eV':float(res[1]),'redshift_before_first_event_or_stop_eV':float(res[2]),'mean_collision_u':float(res[3]),'probability_integral':float(res[4]),'probability_closure_abs':float(abs(res[4]+np.exp(-stop)-1)),'energy_ledger_relative':float(abs(res[:3].sum()/E0-1)),'tau_inverse_relative_max':float(max(inv,default=0)),'collision_integral64_128_relative_max':refin,'quantiles':quant,'thermal_at_emission':self.thermal(zs,E0),'rate_over_H_at_emission':self.rates(zs,E0).tolist(),'tail_probability_bound':float(np.exp(-40)) if tauend>40 else 0.,'tail_energy_bound_eV':float(E0*np.exp(-40)) if tauend>40 else 0.}

def source_nodes(F,z,n):
    # Equal-F midpoint targets are strictly inside the finite raw-F measure.
    targets=F[0]+(np.arange(n)+.5)*(F[-1]-F[0])/n
    # Locate the strict bracketing original cell, skipping all preceding flat cells.
    hi=np.searchsorted(F,targets,side='right'); lo=hi-1
    return z[lo]+(targets-F[lo])/(F[hi]-F[lo])*(z[hi]-z[lo])

def csv(path,arr,header): np.savetxt(ROOT/path,arr,delimiter=',',header=header,comments='',fmt='%.17g')

def run():
    started=time.perf_counter()
    def timeout(*_): raise TimeoutError('Frozen30s cumulative numerical budget exhausted')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(30)
    manifest=input_copies(); meta=json.loads((ROOT/'inputs/laneC/BE_KINETICS_RESULT.json').read_text()); source=json.loads((ROOT/'inputs/laneC/DECAY_SPECTRUM_RESULT.json').read_text())
    hist=np.genfromtxt(ROOT/'inputs/laneC/be_kinetics_history.csv',delimiter=',',names=True); bath=Bath(meta)
    F=hist['Fdecay'];z=hist['z'];delta=float(F[-1]-F[0]); N0=meta['nb0_cm-3']*meta['YBe7']; amp=N0*.104*delta
    if np.any(np.diff(F)<0): raise ValueError('Raw cumulative source F not monotone')
    energies=np.sort(np.r_[np.geomspace(1000,1e6,257),E0]); sig=angular(energies); sig128=angular(energies,128); means=energies*sig[:,1]/sig[:,0]; var=energies**2*(sig[:,2]/sig[:,0]-(sig[:,1]/sig[:,0])**2)
    csv('evidence/kn_cross_sections.csv',np.column_stack((energies,sig,means,energies-means,var)),'E_eV,sigma0_cm2,sigma1_cm2,sigma2_cm2,mean_K_eV,mean_Eout_eV,variance_K_eV2')
    testsE=np.array(CON['numerics']['independent_r_integral_test_eV']); rawr=np.array([r_adaptive(E) for E in testsE]); rawa=angular(testsE)
    angref=float(np.max(abs(sig-sig128)/sig128)); radref=float(np.max(abs(rawr-rawa)/rawr)); closederr=float(np.max(abs(angular(testsE)[:,0]-closed(testsE/ME))/angular(testsE)[:,0]))
    low=angular(1e-6*ME)/ST; lowerrs=[abs(low[0]/(1-2e-6)-1),abs(low[1]/1e-6-1),abs(low[2]/(1.4e-12)-1)]
    higherr=float(abs(closed(1e6)/(3*ST/(8e6)*(np.log(2e6)+.5))-1))
    edges,kernel=recoil_bins(); csv('evidence/gamma_first_collision_kernel.csv',np.column_stack((edges[:-1],edges[1:],kernel)),'K_lo_eV,K_hi_eV,probability,K_first_eV,K_second_eV2,Eout_first_eV')
    sums=kernel.sum(axis=0); se=angular(E0); target=np.array([1,E0*se[1]/se[0],E0**2*se[2]/se[0],E0*(1-se[1]/se[0])]); kernelerr=float(np.max(abs(sums-target)/target)); binclosure=float(np.max(abs(kernel[:,1]+kernel[:,3]-E0*kernel[:,0]))/E0)
    x0=E0/ME; kmax=edges[-1]
    kquant={str(p):float(brentq(lambda K:quad(lambda r:rdr(r,x0)/se[0],1-K/E0,1,epsabs=1e-13,epsrel=2e-12)[0]-p,0,kmax)) for p in (.05,.5,.95)}
    thermalKT=C['kB_J_K']*CON['inputs']['T0_K']*(1+z)/C['eV_J'];theta=thermalKT/ME; rr=bath.rates(z,np.full(len(z),E0))
    csv('evidence/gamma_history_rates.csv',np.column_stack((z,F,rr[:,0],rr[:,1],theta,np.sqrt(3*theta),4*thermalKT/E0)),'z,Fdecay,Gamma0_over_H,Gamma1_over_H,theta_e,sqrt_3theta_e,4kBT_over_Egamma')
    allsource={}; averages={}
    for n in (128,256):
        nodes=source_nodes(F,z,n); events=[bath.event(zz) for zz in nodes]; allsource[n]=events
        averages[n]={key:float(np.mean([row[key] for row in events])) for key in ('K_eV','photon_first_event_or_stop_eV','redshift_before_first_event_or_stop_eV','mean_collision_u','tau_endpoint')}
        (ROOT/f'results/laneC/raw/source{n}.json').write_text(json.dumps(events,indent=2)+'\n')
    events=allsource[256]; keys=['z_source','tau_endpoint','log_endpoint_no_collision_probability','endpoint_no_collision_probability','collision_probability_endpoint','tau_stop','u_stop','K_eV','photon_first_event_or_stop_eV','redshift_before_first_event_or_stop_eV','mean_collision_u']
    csv('evidence/gamma_first_collision_history.csv',np.column_stack(([delta/256]*256,*[[r[key] for r in events] for key in keys])),'raw_dF_weight,'+','.join(keys))
    qevents={key:bath.event(meta[key]) for key in ('z10','z50','z90')}
    refinement={key:abs(averages[128][key]/averages[256][key]-1) for key in averages[256]}
    rows=[*allsource[128],*events,*qevents.values()]; probmax=max(row['probability_closure_abs'] for row in rows); ledgermax=max(row['energy_ledger_relative'] for row in rows); invmax=max(row['tau_inverse_relative_max'] for row in rows); intref=max(row['collision_integral64_128_relative_max'] for row in rows)
    wf=CON['acceptance']['Wolfram_reuse'];wr=np.array([wf['sigma0_over_sigmaT'],wf['sigma1_over_sigmaT'],wf['meanK_over_E']]);actual=np.array([se[0]/ST,se[1]/ST,se[1]/se[0]]);werr=float(np.max(abs(actual/wr-1)))
    positivity=bool(np.all(sig>=0) and np.all(kernel>=0) and np.all(sig[:,1]<=sig[:,0]) and np.all(sig[:,2]<=sig[:,1]) and all(row['K_eV']>=0 and row['K_eV']<=E0 and row['photon_first_event_or_stop_eV']>=0 and row['redshift_before_first_event_or_stop_eV']>=0 for row in rows))
    checks={'angular_refinement':angref<=1e-9,'independent_r':radref<=1e-9,'closed_total':closederr<=1e-8,'published_sigmaT':abs(ST/C['sigmaT_published_rounded_cm2']-1)<=1e-10,'Thomson_limits':max(lowerrs)<=1e-5,'high_x':higherr<=2e-5,'kernel_closures':max(kernelerr,binclosure)<=1e-10,'first_event_closures':max(probmax,ledgermax)<=1e-8,'inverse_tau':invmax<=1e-7,'source_energy_refinement':max(refinement[k] for k in ('K_eV','photon_first_event_or_stop_eV','redshift_before_first_event_or_stop_eV'))<=3e-4,'source_mean_u_refinement':refinement['mean_collision_u']<=1e-3,'collision_integral_refinement':intref<=1e-8,'positivity_and_bounds':positivity,'Wolfram_reuse_declared_rounding':werr<=1e-8}
    elapsed=time.perf_counter()-started;signal.alarm(0)
    yields={}
    for key in ('K_eV','photon_first_event_or_stop_eV','redshift_before_first_event_or_stop_eV'):
        v=averages[256][key];yields[key]={'per_emitted_source_gamma_eV':v,'per_initial_Be7_donor_eV':v*.104*delta,'per_cosmic_baryon_eV':v*.104*delta*meta['YBe7'],'per_present_comoving_cm3_eV':v*amp,'frame':'electron/photon at first event or carried stop; cosmological loss before first event/stop; not common-late-epoch photon energy density'}
    result={'contract_id':CON['contract_id'],'authority_requested':'Astra','executor_requested':'gpt-6.1-sol','executor_observed':'UNKNOWN','input_manifest':manifest,'sigmaT_cm2':ST,'source_N0_cm-3':N0,'source_DeltaF':delta,'source_gamma_count_per_present_comoving_cm3':amp,'normalization':'actual raw-F finite source; direct primordial Li excluded; no conditional amplitude renormalization','exact_477600eV':{'sigma0_cm2':float(se[0]),'sigma1_cm2':float(se[1]),'sigma2_cm2':float(se[2]),'sigma0_over_sigmaT':float(se[0]/ST),'mean_K_eV':float(E0*se[1]/se[0]),'mean_Eout_eV':float(E0*(1-se[1]/se[0])),'variance_K_eV2':float(E0**2*(se[2]/se[0]-(se[1]/se[0])**2)),'K_support_eV':[0,float(kmax)],'K_quantiles_eV':kquant},'source_quantile_events':qevents,'source_averages_128':averages[128],'source_averages_256':averages[256],'yield_units':yields,'source_refinement_relative':refinement,'residuals':{'angular64_128_relative':angref,'angular_vs_r_relative':radref,'closed_total_relative':closederr,'published_sigmaT_relative':abs(ST/C['sigmaT_published_rounded_cm2']-1),'low_x_relative':lowerrs,'high_x_relative':higherr,'kernel_moments_relative':kernelerr,'kernel_bin_energy_relative':binclosure,'first_event_probability_abs':probmax,'first_event_energy_relative':ledgermax,'inverse_tau_relative':invmax,'collision_integral64_128_relative':intref,'Wolfram_declared_rounding_relative':werr},'tail_probability_bound_per_gamma':float(np.exp(-40)),'tail_energy_bound_per_gamma_eV':float(E0*np.exp(-40)),'solver':'DOP853 inverse tau ODE rtol1e-10 atol1e-12; independent adaptive u quadrature epsrel2e-11; first-event GL64/128; angular GL64/128','checks':{k:bool(v) for k,v in checks.items()},'wall_time_s':elapsed,'versions':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},'scope':'Cold stationary free-electron first Compton event; actual donor source with cosmological redshift; gross kinetic-transfer lower bound only within cold downscattering model, not finite-temperature net deposited heat. No full cascade, common-epoch scattered-photon spectrum, H or NCP.','next_algorithm':'Conservative photon-energy redshift advection plus number-conserving KN gain/loss operator; bin-integrated electron-K handoff; finite-temperature detailed balance near kBT; electron Coulomb/ionization/inverse-Compton cooling before heat. Not executed.','status':'NUMERICAL_CHECKS_PASS_REVIEW_PENDING' if all(checks.values()) else 'NUMERICAL_FAILURE_AUTHORITY_REQUIRED'}
    np.savez(ROOT/'results/laneC/raw/kernel_comparisons.npz',E_test=testsE,angular=rawa,independent_r=rawr,energy_table=energies,angular64=sig,angular128=sig128)
    (ROOT/'evidence/GAMMA_TRANSFER_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2)); return result
if __name__=='__main__':
    try: run()
    except BaseException as exc:
        (ROOT/'results/laneC/raw/failure.json').write_text(json.dumps({'error_type':type(exc).__name__,'error':str(exc)},indent=2)+'\n');raise
