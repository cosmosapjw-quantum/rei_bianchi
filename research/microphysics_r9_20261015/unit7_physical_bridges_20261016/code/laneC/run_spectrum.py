"""Conservative frozen Unit7 lane C pushforward of raw lane B decay measure."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[key]='1'
import json,signal,time,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
class Measure:
    """Positive piecewise constant dD/dz from piecewise linear descending F(z)."""
    def __init__(self,z,F):
        self.z=np.asarray(z); self.F=np.asarray(F); self.s=-np.diff(F)/np.diff(z)
        if np.any(self.s<0): raise ValueError('Input invariant failure: negative raw-F cell decay increment')
        dz=np.diff(z); zl=self.z[:-1]; zh=self.z[1:]
        cell=np.column_stack((self.s*dz,self.s*np.log1p(dz/(1+zl)),self.s*dz/((1+zl)*(1+zh))))
        self.prefix=np.vstack((np.zeros(3),np.cumsum(cell,axis=0)))
    def primitive(self,x):
        x=np.clip(np.asarray(x),self.z[0],self.z[-1]); i=np.minimum(np.searchsorted(self.z,x,side='right')-1,len(self.s)-1)
        lo=self.z[i]; d=x-lo
        piece=np.stack((self.s[i]*d,self.s[i]*np.log1p(d/(1+lo)),self.s[i]*d/((1+lo)*(1+x))),axis=-1)
        return self.prefix[i]+piece
    def moments(self,E,lo,hi,amplitude=1):
        lo=np.asarray(lo); hi=np.asarray(hi)
        # Zero energy edges map explicitly to infinite redshift, with no division by zero.
        a=np.full(np.broadcast(lo,hi).shape,np.inf); np.divide(E,hi,out=a,where=hi>0); a=a-1
        b=np.full(np.broadcast(lo,hi).shape,np.inf); np.divide(E,lo,out=b,where=lo>0); b=b-1
        vals=self.primitive(b)-self.primitive(a)
        return vals*np.array([1,E,E*E])*amplitude
    def stats(self,E):
        vals=self.prefix[-1]*[1,E,E*E]; mean=vals[1]/vals[0]
        quant={str(p):float(E/(1+np.interp(self.F[-1]+p*(self.F[0]-self.F[-1]),self.F[::-1],self.z[::-1]))) for p in (.05,.16,.5,.84,.95)}
        return {'mean_eV':float(mean),'standard_deviation_eV':float(np.sqrt(vals[2]/vals[0]-mean**2)),'quantiles_eV':quant}

def peak_width(E,q):
    i=int(np.argmax(q)); xx=E[i-1:i+2]; yy=q[i-1:i+2]
    # Dimensionless local coordinates improve fit conditioning and preserve branch scaling.
    d=xx[1]; scale=xx[-1]-xx[0]; coef=np.polyfit((xx-d)/scale,yy/yy[1],2)
    xv=-coef[1]/(2*coef[0]); mode=d+scale*xv; height=yy[1]*np.polyval(coef,xv)
    half=height/2
    il=np.flatnonzero(q[:i]<=half)[-1]; ir=i+np.flatnonzero(q[i:]<=half)[0]
    left=np.interp(half,q[il:il+2],E[il:il+2]); right=np.interp(half,q[ir-1:ir+1][::-1],E[ir-1:ir+1][::-1])
    return {'mode_eV':float(mode),'peak_cm-3_eV-1':float(height),'half_height_lower_eV':float(left),'half_height_upper_eV':float(right),'FWHM_eV':float(right-left),'method':'quadratic local interpolation through 3 native rate-derived dn/dE samples; half-height roots linear in E,q against interpolated peak height'}

def toy_checks():
    m=Measure(np.array([1.,3.]),np.array([1.,0.])); vals=m.moments(12,np.array([3,4]),np.array([4,6]))
    targets=np.array([[.5,6*np.log(4/3),6],[.5,6*np.log(3/2),12]])
    # M2 in [3,4] is 6*(4-3)=6; the other is 12.
    total=m.moments(12,0,100); expect=np.array([1,6*np.log(2),18])
    tails=sum(m.moments(12,a,b)[0] for a,b in ((0,3.5),(3.5,5),(5,100)))
    outside=np.array([m.moments(12,0,2),m.moments(12,7,100)])
    return {'bin_relative':float(np.max(abs(vals-targets)/targets)),'total_relative':float(np.max(abs(total-expect)/expect)),'cropped_number_closure':float(abs(tails-1)),'outside_support_absolute':float(np.max(abs(outside))),'values':vals.tolist(),'total':total.tolist()}

def run():
    tic=time.perf_counter()
    def timeout(*_): raise TimeoutError('15-second C numerical budget exhausted')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(15)
    con=json.loads((ROOT/'spec/DECAY_SPECTRUM_CONTRACT.json').read_text()); bm=json.loads((ROOT/'evidence/BE_KINETICS_RESULT.json').read_text())
    data=np.genfromtxt(ROOT/'evidence/be_kinetics_history.csv',delimiter=',',names=True)
    z=data['z']; F=data['Fdecay']; b=data['x_Be3']; deriv=data['dF_dz']; m=Measure(z[::-1],F[::-1]); mc=Measure(z[::-2],F[::-2])
    N0=bm['nb0_cm-3']*bm['YBe7']; YH=con['input_history']['donor_YH_protium_per_baryon_for_ratio_check']; nH0=bm['nb0_cm-3']*YH; XBe=bm['YBe7']/YH
    delta=float(F[-1]-F[0]); edges=np.arange(4001)*.025
    output=[edges[:-1],edges[1:]]; headers=['E_lo_eV','E_hi_eV']; profile=[z]; profile_headers=['z']; results={}; compare={}; closure={}; cdf={}
    for branch in con['model']['branches']:
        name=branch['id']; frac=branch['fraction']; emit=branch['E_emit_eV']; amp=N0*frac
        moments=m.moments(emit,edges[:-1],edges[1:],amp); total=m.prefix[-1]*[1,emit,emit*emit]*amp
        E=emit/(1+z); q=amp*(-deriv)*(1+z)**2/emit
        output.extend(moments.T); headers.extend([f'{name}_{v}' for v in ('N_cm-3','M1_eV_cm-3','M2_eV2_cm-3')])
        profile.extend([E,q]); profile_headers.extend([f'{name}_E_eV',f'{name}_q_cm-3_eV-1'])
        stats=m.stats(emit); peak=peak_width(E,q)
        crop={label:float(m.moments(emit,lo,hi,amp)[0]) for label,lo,hi in (('below',0,12),('inside',12,35),('above',35,100))}
        full={label:float(m.moments(emit,lo,hi,amp)[0]) for label,lo,hi in (('below',0,edges[0]),('inside',edges[0],edges[-1]),('above',edges[-1],np.inf))}
        # Independent quadrature uses raw rate-derived derivative mapped by physical Jacobian.
        independent=np.array([np.trapezoid(q,E),np.trapezoid(q*E,E)])
        compare[name]={'M0_relative':float(abs(independent[0]-total[0])/total[0]),'M1_relative':float(abs(independent[1]-total[1])/total[1]),'independent_M0_cm-3':float(independent[0]),'independent_M1_eV_cm-3':float(independent[1])}
        coarsestats=mc.stats(emit); cdferr=float(np.max(abs(np.interp(z[::-1],mc.z,mc.F)-F[::-1]))/delta)
        cdf[name]={'CDF_max_absolute':cdferr,'mean_relative':abs(coarsestats['mean_eV']/stats['mean_eV']-1),'quantile_max_relative':max(abs(coarsestats['quantiles_eV'][key]/value-1) for key,value in stats['quantiles_eV'].items())}
        closure[name]={'bin_M0_relative':float(abs(moments[:,0].sum()-N0*frac*delta)/(N0*frac*delta)),'bin_M1_relative':float(abs(moments[:,1].sum()-total[1])/total[1]),'bin_M2_relative':float(abs(moments[:,2].sum()-total[2])/total[2]),'cropped_number_relative':float(abs(sum(crop.values())-N0*frac*delta)/(N0*frac*delta)),'full_export_number_relative':float(abs(sum(full.values())-N0*frac*delta)/(N0*frac*delta))}
        results[name]={'branch_fraction':frac,'E_emit_eV':emit,'computed_support_eV':[float(E[0]),float(E[-1])],'N_cm-3':float(total[0]),'M1_eV_cm-3':float(total[1]),'M2_eV2_cm-3':float(total[2]),**stats,**peak,'cropped_12_35_eV_number_cm-3':crop,'export_0_100_eV_number_cm-3':full,'conditional_statistics_denominator_cm-3':float(total[0])}
    # Source emission rates are separate from freely redshifted present spectra.
    rate=N0*(1+z)**3*bm['lambda_s-1']*b
    profile.extend([rate,rate*.896*861800,rate*.104*384200,rate*.104*477600])
    profile_headers.extend(['R_phys_cm-3_s-1','nu_ground_source_eV_cm-3_s-1','nu_excited_source_eV_cm-3_s-1','gamma_source_eV_cm-3_s-1'])
    g=results['ground']; x=results['excited']; ratio=384200/861800
    scaling={'count_ratio_relative':abs((x['N_cm-3']/g['N_cm-3'])/(.104/.896)-1)}
    for key in ('mean_eV','standard_deviation_eV','mode_eV','FWHM_eV'):
        scaling[key+'_relative']=abs(x[key]/g[key]/ratio-1)
    scaling['quantiles_relative']=max(abs(x['quantiles_eV'][key]/val/ratio-1) for key,val in g['quantiles_eV'].items())
    toy=toy_checks(); enu=.896*861800+.104*384200; egamma=.104*477600; recoil=.896*56.5+.104*11.2
    combinedN=g['N_cm-3']+x['N_cm-3']; combinedE=g['M1_eV_cm-3']+x['M1_eV_cm-3']
    checks={'normalization_identity':abs(nH0*XBe/N0-1)<=1e-15,'input_increments_nonnegative':bool(np.all(m.s>=0)),'number_closures':max(v[k] for v in closure.values() for k in ('bin_M0_relative','cropped_number_relative','full_export_number_relative'))<=1e-11,'moment_closures':max(v[k] for v in closure.values() for k in ('bin_M1_relative','bin_M2_relative'))<=1e-10,'toy':max(toy[k] for k in ('bin_relative','total_relative','cropped_number_closure','outside_support_absolute'))<=1e-11,'branch_scaling':max(scaling.values())<=1e-10,'independent_kinetic_jacobian':max(v[k] for v in compare.values() for k in ('M0_relative','M1_relative'))<=.003,'coarsened_native':max(v[k] for v in cdf.values() for k in ('CDF_max_absolute','mean_relative','quantile_max_relative'))<=.003}
    elapsed=time.perf_counter()-tic; signal.alarm(0)
    result={'authority_requested':'Astra','executor_requested':'gpt-6.1-sol','executor_observed':'UNKNOWN','N0_cm-3':N0,'DeltaF':delta,'normalization_identity':{'YH':YH,'XBe7_per_H':XBe,'nH0_cm-3':nH0,'nH0_XBe7_cm-3':nH0*XBe,'nb0_YBe7_cm-3':N0,'relative_residual':abs(nH0*XBe/N0-1)},'F_zmax_early_input':float(F[0]),'one_minus_F_zmin':float(1-F[-1]),'computed_surviving_a_plus_b':bm['surviving_fraction_end'],'residual_policy':'Raw 1-F endpoint includes accumulation residual; separately integrated surviving a+b underflows to zero. No endpoint replacement. Uncomputed late-decay fraction needs extended kinetics or explicit F(0).','normalization_policy':'Absolute counts from raw cumulative F, no division by DeltaF; conditional statistics divide by actual branch count. Direct primordial Li7 excluded.','branches':results,'combined':{'present_N_cm-3':combinedN,'present_energy_density_eV_cm-3':combinedE,'present_mean_energy_eV':combinedE/combinedN},'emission_bookkeeping':{key:{'per_donor_full_decay_eV':value,'per_initial_donor_computed_window_eV':value*delta,'per_cosmic_baryon_computed_window_eV':value*delta*bm['YBe7']} for key,value in [('nu_paper_line',enu),('nuclear_gamma_source',egamma),('initial_daughter_recoil_approximate',recoil)]},'closure_residuals':closure,'branch_scaling_residuals':scaling,'independent_kinetic_jacobian':compare,'coarsened_native':cdf,'toy_checks':toy,'checks':{key:bool(value) for key,value in checks.items()},'wall_time_s':elapsed,'versions':{'python':sys.version,'numpy':np.__version__},'scope':'Specified FLRW trace-kinetic model; paper-line freely streaming ultrarelativistic neutrino approximation, all propagated flavors summed; no present electron-flavor prediction, exact-Q closure, deposited-heat model, neutrino mass measurement or late-time extension. Photon/recoil source energy is not deposited heat.','status':'NUMERICAL_CHECKS_PASS_REVIEW_PENDING' if all(checks.values()) else 'NUMERICAL_FAILURE_AUTHORITY_REQUIRED'}
    np.savetxt(ROOT/'evidence/decay_neutrino_spectrum.csv',np.column_stack(output),delimiter=',',header=','.join(headers),comments='',fmt='%.17g')
    np.savetxt(ROOT/'evidence/decay_neutrino_profile.csv',np.column_stack(profile),delimiter=',',header=','.join(profile_headers),comments='',fmt='%.17g')
    (ROOT/'evidence/DECAY_SPECTRUM_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2)); return result
if __name__=='__main__':
    try: run()
    except BaseException as exc:
        (ROOT/'code/laneC/raw/failure.json').write_text(json.dumps({'error_type':type(exc).__name__,'error':str(exc)},indent=2)+'\n'); raise
