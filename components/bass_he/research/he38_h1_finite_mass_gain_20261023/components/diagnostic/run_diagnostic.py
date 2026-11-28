#!/usr/bin/env python3
"""New HE38 finite-mass diagnostic and sharing-compression benchmark only."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ.setdefault(key,'1')
import argparse, contextlib, datetime, hashlib, json, pathlib, resource, shutil, sys, time, traceback

HERE=pathlib.Path(__file__).resolve().parent
EXPECTED_PARENT='7e6103b1f2a2aca36608e5d2fa99b94d3494ecb52f98377ae2e0b4b29e9ed745'
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(p,v): pathlib.Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
class Tee:
    def __init__(self,*streams): self.streams=streams
    def write(self,s):
        for stream in self.streams: stream.write(s);stream.flush()
    def flush(self):
        for stream in self.streams:stream.flush()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit-root',type=pathlib.Path,default=HERE.parents[1])
    parser.add_argument('--implementation-root',type=pathlib.Path)
    parser.add_argument('--parent-csv',type=pathlib.Path,default=HERE/'reused'/'h1_gain_moments.csv')
    parser.add_argument('--output-root',type=pathlib.Path,default=HERE)
    args=parser.parse_args()
    implementation=(args.implementation_root or args.unit_root/'components'/'finite_mass').resolve()
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    attempt=args.output_root/'attempts'/('attempt_'+stamp)
    attempt.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,attempt/'run_diagnostic.py')
    start=time.perf_counter();cpu=time.process_time()
    receipt={'schema':'he38.finite_mass_diagnostic.v1','workflow_version':'1.0.0','approval_version':'0.2',
      'started_utc':stamp,'command':[sys.executable,*sys.argv],'code_sha256':sha(__file__),
      'parent_csv_sha256':sha(args.parent_csv),'new_api_evaluations':0,'old_diagnostic_replays':0,
      'old_provider_benchmarks':0,'old_scientific_suite_replays':0,'new_IVPs':0,'new_renders':0,
      'budget_cpu_seconds':30,'budget_RSS_MiB':512,'input_scope':'Parent radial rows reused by identity; donor API called only as a dependency of the new finite-mass evaluation.'}
    dump(attempt/'START.json',receipt)
    code=0
    with (attempt/'stdout.txt').open('w') as stdout,(attempt/'stderr.txt').open('w') as stderr:
      with contextlib.redirect_stdout(Tee(sys.stdout,stdout)),contextlib.redirect_stderr(Tee(sys.stderr,stderr)):
       try:
        if receipt['parent_csv_sha256']!=EXPECTED_PARENT:raise ValueError('PARENT_INPUT_HASH_MISMATCH')
        import numpy as np
        import scipy
        from scipy.special import roots_laguerre, roots_legendre
        sys.path.insert(0,str(implementation))
        import h1_finite_mass as fm
        parent=np.genfromtxt(args.parent_csv,delimiter=',',names=True)
        T=parent['temperature_K']
        if len(T)!=129 or T[0]!=2000 or T[-1]!=200000:raise ValueError('EXPECTED_SAVED_129_T_GRID')
        ev=fm.FiniteMassModel().evaluate(T);receipt['new_api_evaluations']=1
        theta=fm.KB_J_K*T;alpha=ev.alpha_m3_s;beta=ev.beta_J_m3_s;x=fm.I_J/theta
        heat=ev.heat_per_pair_J_m3_s/alpha[:,None]/fm.EV_J
        heavy=ev.heavy_heat_per_pair_J_m3_s/alpha/fm.EV_J
        stf=ev.stf_coefficients_m3_s/alpha[:,None,None]
        U1=theta*alpha;U2=beta-(fm.I_J+theta)*alpha
        available=beta-fm.I_J*alpha
        rate_ratio=alpha/parent['alpha_native_m3_s']
        stf_ratio=fm.ZETA*ev.kappa2_m3_s/parent['kappa2_native_m3_s']
        expected_rate=1/np.sqrt(fm.ZETA);expected_stf=np.sqrt(fm.ZETA)
        assert np.max(np.abs(rate_ratio/expected_rate-1))<5e-14
        assert np.max(np.abs(stf_ratio/expected_stf-1))<5e-14
        assert np.max(np.abs(heat.sum(axis=1)+fm.I_EV))<2e-13
        assert np.max(np.abs(stf.sum(axis=1)+ev.kappa2_m3_s[:,None]/alpha[:,None]*np.array([fm.ZETA,fm.ETA])))<1e-12
        assert np.all(U2>0) and np.all(U2<U1)
        # Positive numerical relative-energy plus conditional-transfer integral.
        # q is the source-law CDF coordinate: Upsilon/theta=x*(x+t)/(x+(1-q)*t).
        tn,tw=roots_laguerre(128);qn,qw=roots_legendre(128);qn=(qn+1)/2;qw=qw/2
        prefactor=4*np.pi*fm.A0_M**2*fm.I_J*np.sqrt(8/(np.pi*fm.MU_KG))*np.sqrt(theta)*np.exp(-x)
        def quadrature(xv,pv,t=tn,w=tw,q=qn,z=qw):
            a=xv[:,None,None];b=t[None,:,None]
            integral=np.sum((a*b/(a+(1-q[None,None,:])*b))*w[None,:,None]*z[None,None,:],axis=(1,2))
            return pv*integral
        numerical=quadrature(x,prefactor)
        compressed=beta-theta*alpha
        relative=np.abs(numerical/compressed-1)
        t2,w2=roots_laguerre(192);q2,z2=roots_legendre(192);q2=(q2+1)/2;z2=z2/2
        hottest=quadrature(x[-1:],prefactor[-1:],t2,w2,q2,z2)[0]
        convergence=float(abs(hottest/numerical[-1]-1))
        assert np.max(relative)<2e-10 and convergence<2e-10
        # Same requested outputs and 129-temperature workload; input moments/nodes
        # are already resident for both methods and are excluded from timing.
        analytic_times=[];quad_times=[]
        for repeat in range(7):
            before=time.perf_counter_ns()
            for j in range(500): result=beta-theta*alpha
            analytic_times.append((time.perf_counter_ns()-before)*1e-9/500)
            before=time.perf_counter_ns(); resultq=quadrature(x,prefactor)
            quad_times.append((time.perf_counter_ns()-before)*1e-9)
        benchmark={'scope':'New source-sharing moment only, same 129 outputs; cached radial moments and quadrature setup excluded from both timings.',
          'method_reference':'Positive relative-energy Laguerre128 times conditional-transfer-CDF Legendre128',
          'method_compressed':'beta-theta*alpha','batches':7,'compressed_calls_per_batch':500,'quadrature_calls_per_batch':1,
          'compressed_seconds_per_129_outputs':analytic_times,'quadrature_seconds_per_129_outputs':quad_times,
          'median_compressed_seconds':float(np.median(analytic_times)),'median_quadrature_seconds':float(np.median(quad_times)),
          'median_speed_ratio':float(np.median(quad_times)/np.median(analytic_times)),
          'max_relative_error':float(relative.max()),'hottest_128_to_192_relative_change':convergence,
          'hottest_192_relative_error':float(abs(hottest/compressed[-1]-1)),
          'not_a_full_provider_or_IVP_speedup':True}
        masses={'m_e_kg':fm.ME_KG,'m_p_kg':fm.MP_KG,'m_H_kg':fm.MH_KG,'mu_kg':fm.MU_KG,
          'eta':fm.ETA,'zeta':fm.ZETA,'ion_fraction_inner':fm.ION_FRACTION_INNER,'electron_fraction_inner':fm.ELECTRON_FRACTION_INNER,
          'rate_ratio_exact_formula':'zeta^(-1/2)','rate_ratio':float(expected_rate),'rate_shift_ppm':float((expected_rate-1)*1e6),
          'electron_only_total_STF_ratio_exact_formula':'sqrt(zeta)','electron_only_total_STF_ratio':float(expected_stf),'electron_only_STF_shift_ppm':float((expected_stf-1)*1e6)}
        endpoints=[]
        for i in [0,64,128]:endpoints.append({'temperature_K':float(T[i]),'Q_e_per_event_eV':float(heat[i,0]),'Q_H_per_event_eV':float(heat[i,1]),'Q_p_per_event_eV':float(heat[i,2]),'Q_heavy_per_event_eV':float(heavy[i]),'electron_shift_from_minus_I_eV':float(-heavy[i]),'first_Jacobi_available_fraction':float(U1[i]/available[i]),'second_Jacobi_available_fraction':float(U2[i]/available[i]),'STF_coefficients_over_alpha':stf[i].tolist()})
        metrics={'schema':'he38.finite_mass_metrics.v1','status':'PASS_SCOPED','grid_count':129,'temperature_domain_K':[2000,200000],
          'model_identity':fm.MODEL_IDENTITY,'model_scope':fm.MODEL_SCOPE,'masses_and_exact_corrections':masses,
          'representative_rows':endpoints,'max_heat_conservation_error_eV':float(np.max(np.abs(heat.sum(axis=1)+fm.I_EV))),
          'positive_proton_heat_rows':int(np.count_nonzero(heat[:,2]>0)),
          'interpretation':'Positive proton Q is a product-birth moment; signed H removal and e net source refer to instantaneous kinetic moments. The map assumes common T/bulk and does not establish thermal equilibration.',
          'normalization':'Heat per event Q/r in eV. STF M_s,j/alpha before density factor nH for incoming e, ne for incoming H0.',
          'benchmark':benchmark}
        cols={'temperature_K':T,'alpha_finite_m3_s':alpha,'beta_finite_J_m3_s':beta,'gamma_finite_J2_m3_s':ev.gamma_J2_m3_s,
          'rate_ratio_to_saved_HE37':rate_ratio,'electron_only_total_STF_ratio_to_saved_HE37':stf_ratio,
          'Q_e_per_event_eV':heat[:,0],'Q_H_per_event_eV':heat[:,1],'Q_p_per_event_eV':heat[:,2],
          'Q_heavy_per_event_eV':heavy,'electron_shift_from_minus_I_eV':-heavy,
          'first_Jacobi_available_fraction':U1/available,'second_Jacobi_available_fraction':U2/available,
          'first_Jacobi_energy_per_event_eV':U1/alpha/fm.EV_J,'second_Jacobi_energy_per_event_eV':U2/alpha/fm.EV_J,
          'Lambda_compressed_J_m3_s':compressed,'Lambda_quadrature_J_m3_s':numerical,'Lambda_relative_error':relative}
        for s,name in enumerate(['e','H','p']):
            for j,inp in enumerate(['e','H']):cols['STF_'+name+'_from_'+inp+'_over_alpha']=stf[:,s,j]
        np.savetxt(attempt/'finite_mass_moments.csv',np.column_stack(list(cols.values())),delimiter=',',header=','.join(cols),comments='',fmt='%.17g')
        np.savez_compressed(attempt/'finite_mass_moments.npz',**cols,heat_per_pair_J_m3_s=ev.heat_per_pair_J_m3_s,
          stf_coefficients_m3_s=ev.stf_coefficients_m3_s,laguerre_nodes_128=tn,laguerre_weights_128=tw,
          transfer_CDF_nodes_128=qn,transfer_CDF_weights_128=qw,laguerre_nodes_192=t2,laguerre_weights_192=w2,
          transfer_CDF_nodes_192=q2,transfer_CDF_weights_192=z2)
        dump(attempt/'METRICS.json',metrics);dump(attempt/'BENCHMARK.json',benchmark)
        receipt['dependencies']={'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'model_identity':fm.MODEL_IDENTITY,
           'implementation_files':{str(p.relative_to(implementation)):sha(p) for p in sorted((implementation/'h1_finite_mass').rglob('*.py'))}}
        receipt['status']='PASS_SCOPED'
        print(json.dumps({'status':'PASS_SCOPED','attempt':str(attempt),'mass_corrections':masses,'representative_rows':endpoints,'benchmark':benchmark},ensure_ascii=False))
       except Exception as exc:
        code=1;receipt['status']='FAIL';receipt['failure']={'class':'implementation_or_numerical','type':type(exc).__name__,'message':str(exc)}
        traceback.print_exc()
    receipt.update(exit_code=code,wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,
       peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    if receipt['cpu_seconds']>30 or receipt['peak_RSS_KiB']>512*1024:
        receipt['budget_status']='EXCEEDED';code=1;receipt['exit_code']=1
    else:receipt['budget_status']='WITHIN_BUDGET'
    receipt['output_hashes']={p.name:sha(p) for p in sorted(attempt.iterdir()) if p.is_file() and p.name not in ('START.json','RESULT.json')}
    dump(attempt/'RESULT.json',receipt)
    dump(args.output_root/'LATEST_ATTEMPT.json',{'attempt':str(attempt.relative_to(args.output_root)),'status':receipt['status'],'receipt_sha256':sha(attempt/'RESULT.json')})
    print(json.dumps({'receipt':str(attempt/'RESULT.json'),'status':receipt['status'],'exit_code':code,'cpu_seconds':receipt['cpu_seconds'],'wall_seconds':receipt['wall_seconds'],'peak_RSS_KiB':receipt['peak_RSS_KiB']}))
    return code
if __name__=='__main__':sys.exit(main())
