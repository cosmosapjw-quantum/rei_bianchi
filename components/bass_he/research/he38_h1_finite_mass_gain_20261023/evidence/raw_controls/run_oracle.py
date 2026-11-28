import argparse, datetime, hashlib, json, os, platform, resource, sys, time, traceback
from pathlib import Path
import numpy as np
from raw_oracle import evaluate, DIRECTIONS, KB

ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(path,data):
    with open(path,'x') as f:json.dump(data,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('attempt');args=ap.parse_args()
    out=ROOT/'attempts'/args.attempt
    out.mkdir(parents=True,exist_ok=False)
    contract=json.loads((ROOT/'CONTRACT.json').read_text())
    start=time.perf_counter();cpu=time.process_time()
    sources={str(p):sha(p) for p in [ROOT/'raw_oracle.py',ROOT/'run_oracle.py',ROOT/'CONTRACT.json']}
    prodroot=Path('/tmp/he38_implementation/h1_finite_mass')
    prodsources={str(p):sha(p) for p in sorted(prodroot.rglob('*.py'))}
    put(out/'START.json',{"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "source_hashes":sources,"comparison_source_hashes":prodsources,"contract":contract,
         "python":sys.version,"platform":platform.platform(),"numpy":np.__version__,
         "pid":os.getpid(),"rlimit_as":resource.getrlimit(resource.RLIMIT_AS),
         "rlimit_cpu":resource.getrlimit(resource.RLIMIT_CPU)})
    cases=[]
    try:
        for T,nr,nu in contract['case_list']:
            name=f'T{T}_L{nr}_U{nu}'
            cs=time.process_time();ws=time.perf_counter()
            raw=evaluate(T,nr,nu)
            with open(out/(name+'.npz'),'xb') as f:np.savez(f,**raw)
            row={"name":name,"T":T,"nradial":nr,"ntransfer":nu,
                 "raw_path":str(out/(name+'.npz')),"sha256":sha(out/(name+'.npz')),
                 "CPU_s":time.process_time()-cs,"wall_s":time.perf_counter()-ws,
                 "COM_nodes":27,"incoming_directions":24,"outgoing_direction_pairs":36,
                 "outgoing_velocity_triples":nr*nu*27*36,
                 "raw_response_tensor_blocks":3*2*2}
            put(out/(name+'_RECEIPT.json'),row)
            cases.append(row)
        # Raw oracle results are sealed before importing the implementation.
        sys.path.insert(0,'/tmp/he38_implementation')
        from h1_finite_mass import FiniteMassModel
        model=FiniteMassModel()
        comparisons=[]
        max_scaled=0.;max_relative=0.;all_pass=True
        for case in cases:
            raw=np.load(case['raw_path'])
            native=model.evaluate(case['T'])
            scale=float(raw['rate_prefactor_m3_s']);theta=KB*case['T']
            expected_rate=float(native.alpha_m3_s[0])/scale
            expected_heat=np.asarray(native.heat_per_pair_J_m3_s[0])/(theta*scale)
            expected_coeff=np.asarray(native.stf_coefficients_m3_s[0])/scale
            expected_J=expected_coeff[:,:,None,None,None]*DIRECTIONS[None,None,:,:,:]
            delta=raw['linear_STF']-expected_J
            scaled_perblock=np.max(np.abs(delta),axis=(-2,-1))/np.maximum(
                1.,np.max(np.abs(expected_J),axis=(-2,-1)))
            rel_perblock=np.linalg.norm(delta,axis=(-2,-1))/np.linalg.norm(expected_J,axis=(-2,-1))
            heatdiff=raw['unperturbed_heat']-expected_heat
            heat_scaled=np.abs(heatdiff)/np.maximum(1.,np.abs(expected_heat))
            heat_rel=np.abs(heatdiff)/np.abs(expected_heat)
            oracle_heavy=float(np.sum(raw['unperturbed_heat'][1:]))
            expected_heavy=float(native.heavy_heat_per_pair_J_m3_s[0])/(theta*scale)
            rate_relative=abs(float(raw['dimensionless_rate'])/expected_rate-1.)
            # All structural-zero diagnostics are normalized by gross tensor scale.
            gross=max(1.,float(np.max(np.abs(expected_J))),float(np.max(np.abs(expected_heat))))
            zero_heat=float(np.max(np.abs(raw['linear_heat'])))/gross
            zero_rate=float(np.max(np.abs(raw['linear_rate'])))/max(1.,expected_rate)
            zero_stf=float(np.max(np.abs(raw['unperturbed_STF'])))/gross
            conservation=abs(float(np.sum(raw['unperturbed_heat']))+
                             float(raw['x'])*float(raw['dimensionless_rate']))/gross
            max_case=max(float(np.max(scaled_perblock)),float(np.max(heat_scaled)),
                         rate_relative,zero_heat,zero_rate,zero_stf,conservation)
            heavy_relative=abs(oracle_heavy-expected_heavy)/abs(expected_heavy)
            case_pass=max_case<=contract['scaled_gate'] and float(np.max(rel_perblock))<=contract['nonzero_relative_gate'] and heavy_relative<=contract['nonzero_relative_gate']
            all_pass=all_pass and case_pass;max_scaled=max(max_scaled,max_case)
            max_relative=max(max_relative,float(np.max(rel_perblock)),float(np.max(heat_rel)),heavy_relative)
            comparisons.append({"name":case["name"],"status":"PASS" if case_pass else "FAIL",
                "rate_relative_error":rate_relative,"heat_scaled_errors":heat_scaled.tolist(),
                "heat_relative_errors":heat_rel.tolist(),"heavy_combined_relative_error":heavy_relative,
                "STF_scaled_errors_output_input_direction":scaled_perblock.tolist(),
                "STF_relative_errors_output_input_direction":rel_perblock.tolist(),
                "dimensionless_oracle_heat":raw['unperturbed_heat'].tolist(),
                "dimensionless_expected_heat":expected_heat.tolist(),
                "dimensionless_expected_coefficients":expected_coeff.tolist(),
                "dimensionless_oracle_coefficients":np.einsum('scdij,dij->scd',raw['linear_STF'],DIRECTIONS).tolist(),
                "max_scaled_error":max_case,"linear_heat_zero_scaled":zero_heat,
                "linear_rate_zero_scaled":zero_rate,"unperturbed_STF_zero_scaled":zero_stf,
                "total_heat_conservation_scaled":conservation,
                "pointwise_energy_scaled":float(raw["max_pointwise_energy_scaled_defect"]),
                "pointwise_momentum_scaled":float(raw["max_pointwise_momentum_scaled_defect"])})
        coarse=np.load(cases[2]['raw_path']);fine=np.load(cases[3]['raw_path'])
        refinement={}
        for key in ['dimensionless_rate','unperturbed_heat','linear_STF']:
            a=coarse[key];b=fine[key];diff=np.asarray(b-a)
            refinement[key]={"maximum_absolute_difference":float(np.max(np.abs(diff))),
                "maximum_scaled_difference":float(np.max(np.abs(diff)/np.maximum(1.,np.abs(b)))),
                "norm_relative_difference":float(np.linalg.norm(diff.ravel())/np.linalg.norm(np.asarray(b).ravel()))}
        stable=all(sha(p)==h for p,h in prodsources.items())
        all_pass=all_pass and stable
        result={"status":"PASS_SCOPED" if all_pass else "FAIL_RETAINED","cases":cases,
          "comparisons":comparisons,"hot_case_refinement":refinement,
          "refinement_scope":"200000K only, 48x32 ->72x48; measured difference not certified error bound",
          "max_scaled_error":max_scaled,"max_reported_relative_error":max_relative,
          "production_identity":model.identity,"production_source_hashes_unchanged":stable,
          "counts":{"new_full_raw_quadrature_cases":len(cases),"base_temperatures":3,
                    "hottest_refinement_cases":1,"input_STF_directions":2,
                    "input_species":2,"output_species":3,"response_tensor_blocks":48,
                    "outgoing_velocity_triples":sum(c['outgoing_velocity_triples'] for c in cases),
                    "radial_COM_incoming_nodes":sum(c['nradial']*27*24 for c in cases),
                    "new_IVP":0,"old_suite_replays":0,"render":0,"benchmark":0},
          "CPU_s":time.process_time()-cpu,"wall_s":time.perf_counter()-start,
          "maxRSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          "limits":"Selected conditional model, fixed finite quadrature, binary64; no empirical angular validation or global certified quadrature bound"}
        put(out/'RESULT.json',result)
        print(json.dumps({k:result[k] for k in ['status','max_scaled_error','max_reported_relative_error','CPU_s','wall_s','maxRSS_KiB','counts']}))
        return 0 if all_pass else 1
    except BaseException as exc:
        put(out/'FAILURE.json',{"error":repr(exc),"traceback":traceback.format_exc(),
            "completed_cases":cases,"CPU_s":time.process_time()-cpu,
            "wall_s":time.perf_counter()-start,"maxRSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        raise
if __name__=='__main__':sys.exit(main())

