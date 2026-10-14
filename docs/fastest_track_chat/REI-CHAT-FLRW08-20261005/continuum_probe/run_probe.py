"""Reproduce only six short trajectories and independent numerical references."""
import argparse,csv,gzip,hashlib,json,os,platform,subprocess,time
from pathlib import Path
import numpy as np
import scipy
from reference import Reference,coefficients,HUBBLE,END

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
TASK='REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL'
OUTPUTS=ROOT/'.cuh/fastest-track/REI-CHAT-FLRW08/continuum-probe/outputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def command(argv,directory,name):
    r=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True)
    (directory/(name+'.stdout')).write_text(r.stdout);(directory/(name+'.stderr')).write_text(r.stderr)
    save(directory/(name+'.command.json'),{'argv':argv,'cwd':str(ROOT),'returncode':r.returncode})
    if r.returncode:raise RuntimeError(name+' failed; raw evidence retained')
    return r.stdout
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reuse-native',type=Path);args=parser.parse_args()
    # Runtime is validated before allocation and output creation.
    assert platform.python_version().startswith('3.12.')
    assert scipy.__version__=='1.17.0' and np.__version__=='2.4.2'
    intent=json.loads((ROOT/'.cuh/fastest-track/REI-CHAT-FLRW08/continuum-probe/intent.json').read_text())
    for p,d in intent['inputs'].items():assert sha(ROOT/p)==d,p
    start=time.perf_counter();run=OUTPUTS/time.strftime('%Y%m%dT%H%M%S')
    run.mkdir(parents=True,exist_ok=False)
    rustc='/home/cosmosapjw/.rustup/toolchains/1.94.1-x86_64-unknown-linux-gnu/bin/rustc'
    native_run=run
    if args.reuse_native:
        native_run=args.reuse_native.resolve().parent
        native=json.loads(args.reuse_native.read_text())
        # Require completed six-run receipt; reference-only continuation is explicit.
        assert len(native['discrete_runs'])==6 and all(x['time_s']==END for x in native['discrete_runs'])
        save(run/'reuse_native.json',{'path':str(args.reuse_native.resolve()),'sha256':sha(args.reuse_native),'new_trajectory_calls':0})
    else:
        command([rustc,'--edition=2021','--crate-name','rei_microphysics','--crate-type','rlib','-O',str(ROOT/'rust/rei_microphysics/src/lib.rs'),'-o',str(run/'librei_microphysics.rlib')],run,'build_library')
        command([rustc,'--edition=2021','-O',str(HERE/'paired_probe.rs'),'--extern','rei_microphysics='+str(run/'librei_microphysics.rlib'),'-o',str(run/'paired_probe')],run,'build_driver')
        native=json.loads(command([str(run/'paired_probe')],run,'paired_probe'));save(run/'native.json',native)
    refs={};metas={};agreement=[]
    for geometry in HUBBLE:
        model=Reference(native,geometry);refs[geometry]={};metas[geometry]={}
        for method in ['DOP853','RK45']:
            v,meta=model.solve(method);refs[geometry][method]=v;metas[geometry][method]=meta
            save(run/(geometry+'_'+method+'.json'),{'state':v.tolist(),'observables':model.observables(v).tolist(),'solver':meta})
        agreement.append(float(np.max(np.abs(refs[geometry]['DOP853']-refs[geometry]['RK45'])/model.scale)))
    coefficient_error=0.
    for sample in native['coefficient_samples']:
        py=coefficients(sample['temperature_k'])
        for x,key in zip(py,['alpha_rr','beta_ci','rr_kinetic','alpha_dr','dr_energy']):
            y=np.array(sample[key]);coefficient_error=max(coefficient_error,float(np.max(np.abs(x-y)/np.maximum(np.abs(y),1e-300))))
    sigma=np.array(native['sigma_cm2']);evaluated=Reference(native,'FLRW').sigma
    assert np.array_equal(sigma==0,evaluated==0)
    sigma_error=float(np.max(np.abs(sigma-evaluated)/np.maximum(np.abs(sigma),1e-300)))
    comparison=[];parity=[]
    for row in native['discrete_runs']:
        geometry=row['geometry'];model=Reference(native,geometry);v=model.from_native(row);ref=refs[geometry]['DOP853'];obs=model.observables(v);robs=model.observables(ref)
        row['individual_error_vs_DOP853']={'gas4_signed':(v[:4]-ref[:4]).tolist(),'temperature_k_signed':float(obs[4]-robs[4]),'full_state_scaled_max':float(np.max(np.abs(v-ref)/model.scale)),'projected_state_scaled_max':float(np.max(np.abs(model.project(v)-ref)/model.scale)),'photon_number_signed':float(obs[-8]-robs[-8]),'photon_energy_signed':float(obs[-7]-robs[-7]),'lowest_node_photons_per_h':float(model.unpack(v)[1][:,0].sum())}
        level={1.25e9:'T0',6.25e8:'T1',3.125e8:'T2'}[row['macro_dt_s']]
        path=ROOT/'runs/rei_fastest_v1/paired/curves'/(level+'_'+geometry+'.csv.gz')
        with gzip.open(path,'rt') as f:
            historical=next(x for x in csv.DictReader(f) if float(x['time_s'])==END)
        pn=model.unpack(v)[1].sum()+model.unpack(v)[2].sum();pu=(model.unpack(v)[1]*model.e).sum()+model.unpack(v)[3].sum()
        actual={'x_HII':v[0],'x_HeII':v[1],'x_HeIII':v[2],'w_ev_per_h':v[3],'temperature_K':obs[4],'photon_n':pn,'photon_u_ev_per_h':pu,'lower_guard_n':model.unpack(v)[2].sum(),'lower_guard_u':model.unpack(v)[3].sum()}
        actual.update(dict(zip(['escape_ev_per_h','redshift_work_ev_per_h','thermal_work_ev_per_h','source_n','source_u','absorbed_n'],row['ledgers'])))
        differences={k:float(actual[k]-float(historical[k])) for k in actual}
        scales={'x_HII':1.,'x_HeII':1.,'x_HeIII':1.,'w_ev_per_h':model.initial[3],'temperature_K':50000.,'photon_n':.05,'photon_u_ev_per_h':.685,'lower_guard_n':.05,'lower_guard_u':.685,'escape_ev_per_h':model.initial[3],'redshift_work_ev_per_h':.685,'thermal_work_ev_per_h':model.initial[3],'source_n':.05,'source_u':.685,'absorbed_n':.05}
        scaled={k:abs(v)/scales[k] for k,v in differences.items()}
        parity.append({'geometry':geometry,'level':level,'path':str(path.relative_to(ROOT)),'sha256':sha(path),'endpoint_absolute_differences':differences,'normalization_scales':{k:float(v) for k,v in scales.items()},'endpoint_scaled_absolute_differences':scaled,'scaled_tolerance':1e-12,'status':'PASS' if max(scaled.values())<=1e-12 else 'FAIL'})
    for dt in [1.25e9,6.25e8,3.125e8]:
        rows={x['geometry']:x for x in native['discrete_runs'] if x['macro_dt_s']==dt}
        contrast=np.array(rows['BI']['gas'])-rows['FLRW']['gas']
        reference=refs['BI']['DOP853'][:4]-refs['FLRW']['DOP853'][:4]
        method_contrast=refs['BI']['RK45'][:4]-refs['FLRW']['RK45'][:4]
        comparison.append({'macro_dt_s':dt,'discrete_BI_minus_FLRW_gas4':contrast.tolist(),'DOP853_BI_minus_FLRW_gas4':reference.tolist(),'RK45_BI_minus_FLRW_gas4':method_contrast.tolist(),'contrast_error_vs_DOP853':(contrast-reference).tolist(),'sign_admission':'NOT_ESTABLISHED'})
    model=Reference(native,'FLRW');d=model.rhs(0,model.initial)/END;derivatives=[]
    for row in native['small_dt_trials']:
        v=model.project(model.from_native(row['state']));approx=(v-model.initial)/row['dt_s'];err=np.max(np.abs((approx-d)*END/model.scale))
        derivatives.append({'dt_s':row['dt_s'],'scaled_derivative_error_times_1e10':float(err),'gas4_secant':approx[:4].tolist(),'gas4_analytic_derivative':d[:4].tolist()})
    result={'task_id':TASK,'scientific_admission':'HOLD','continuum_time_error_certificate':'NOT_ESTABLISHED','time_interval_s':[0,END],'grid':{'spectral_subdivisions':8,'n_mu':8,'n_phi':16},'new_full_campaign_executions':0,'production_source_modified':False,'discrete_runs':native['discrete_runs'],'reference_comparison':{'status':'PASS' if max(agreement)<=1e-8 else 'FAIL','methods':['DOP853','RK45'],'scaled_max_endpoint_disagreement':max(agreement),'per_geometry_scaled_disagreement':dict(zip(HUBBLE,agreement)),'solver_metadata':metas,'rigorous_enclosure':False},'contrast_comparison':comparison,'coefficient_binding':{'max_relative_error':coefficient_error,'sigma_max_relative_error':sigma_error,'zero_cutoffs_match':True},'initial_derivative_consistency':derivatives,'lowest_node_witness':native['lowest_node_witness'],'boundary_model':'PROJECTED_LIMIT_P_M_DT_P; lowest node eliminated, flux lambda1*p1 directly to guard','full_domain_finite_generator':'DOES_NOT_EXIST_AT_OCCUPIED_10EV_NODE','historical_endpoint_parity':parity,'raw_output_directory':str(run.relative_to(ROOT)),'binary_sha256':sha(native_run/'paired_probe'),'included_source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'rust/rei_microphysics/src').glob('*.rs'))},'runtime':{'python':platform.python_version(),'scipy':scipy.__version__,'numpy':np.__version__,'rustc':command([rustc,'--version'],run,'rustc_version').strip()},'wall_seconds':time.perf_counter()-start,'paired_calls':{'trajectory_macro_calls':112,'initial_derivative_diagnostic_calls':4,'boundary_witness_calls':2},'reference_endpoint_gas4':{g:{m:v[:4].tolist() for m,v in methods.items()} for g,methods in refs.items()}}
    result['native_output_directory']=str(native_run.relative_to(ROOT));result['binary_sha256']=sha(native_run/'paired_probe')
    save(HERE/'RESULTS.json',result)
    print(json.dumps({'raw_output_directory':str(run),'reference_scaled_disagreement':max(agreement),'coefficient_relative_error':coefficient_error,'sigma_relative_error':sigma_error,'scientific_admission':'HOLD'}))
if __name__=='__main__':main()
