#!/usr/bin/env python3
"""Independent saved-artifact arithmetic review; no ODE/native RHS execution."""
from pathlib import Path
import datetime,hashlib,json
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EVIDENCE=ROOT/'n2/evidence'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    coarse=EVIDENCE/'EVENT_COUPLED002';fine=EVIDENCE/'EVENT_COUPLED003_RECOVERED'
    comp=read(EVIDENCE/'EVENT_SPECTRAL_COMPARISON_RECOVERED.json')
    a,b=read(coarse/'RESULT.json'),read(fine/'RESULT.json')
    am,bm=read(coarse/'MOMENTS_RECOVERED.json'),read(fine/'MOMENTS_RECOVERED.json')
    ident=read(fine/'IDENTITY.json')
    ts=np.array([r['time_s'] for r in b['history']]);tc=np.array([r['time_s'] for r in a['history']])
    checks={'shared_129_times':len(ts)==129 and np.array_equal(ts,tc),
            'whole_interval':b['status']=='COMPUTED_NOT_REVIEWED' and b['failure'] is None and b['completed_segments']==ident['segment_count'],
            'z_endpoints':b['history'][0]['z']==15.899999999999999 and b['history'][-1]['z']==4.0,
            'as_run_driver':sha(fine/'driver_as_run.py')==ident['driver_sha'],
            'as_run_base':sha(fine/'base_driver_as_run.py')==ident['base_sha'],
            'native_binary':sha(ROOT/'n1/native/target/release/rei_n1_native')==ident['native_sha'],
            'n1_source':sha(ROOT/'n1/provider.py')==ident['n1_sha'],
            'events_source':sha(ROOT/'n2/events.py')==ident['events_sha'],
            'postprocessor_current':sha(ROOT/'n2/postprocess_moments_recovered.py')==comp['postprocess_code_sha256'],
            'comparator_current':sha(ROOT/'n2/compare_spectral_recovered.py')==comp['comparison_code_sha256']}
    checks['z_endpoints']=abs(b['history'][0]['z']-15.9)<4e-15 and b['history'][-1]['z']==4.0
    number=max(abs(r['number_ledger_scaled']) for r in b['history'])
    energy=max(abs(r['energy_ledger_scaled']) for r in b['history'])
    number=max(number,b['max_endpoint_number_ledger']);energy=max(energy,b['max_endpoint_energy_ledger'])
    checks['number_report_exact']=number==b['max_number_ledger'];checks['energy_report_exact']=energy==b['max_energy_ledger']
    checks['native_E_N_gates']=energy<=1e-9 and number<=1e-9
    with np.load(fine/'history.npz') as archive:
        states=archive['scaled_states']*archive['scales']
        checks['saved_npz_129']=states.shape==(129,522)
        checks['saved_npz_finite']=bool(np.isfinite(states).all())
        checks['sampled_photon_energy_positive']=bool((states[:,4:516]>=0).all())
        checks['gas_matches_saved_json']=all(np.array_equal(states[:,i],[r[k] for r in b['history']]) for i,k in enumerate(['xHII','xHeII','xHeIII']))
        checks['sampled_gas_domain']=bool((states[:,0]>=0).all() and (states[:,0]<=1).all() and (states[:,1:3]>=0).all() and (states[:,1:3].sum(axis=1)<=1).all())
    sets={};metrics_exact=True
    for count,ii in [('129',np.arange(129)),('65',np.arange(0,129,2))]:
        fields={}
        for field,reported in comp['comparisons'][count]['fields'].items():
            left,right=(a,b) if field in a['history'][0] else (am,bm)
            av=np.array([r[field] for r in left['history']])[ii];bv=np.array([r[field] for r in right['history']])[ii]
            scale=float(np.max(np.abs(bv)));delta=np.abs(av-bv);imax=int(np.argmax(delta));err=float(delta[imax]/scale if scale else delta[imax])
            exact=err==reported['scaled_error'] and int(ii[imax])==reported['worst_epoch_index']
            metrics_exact=metrics_exact and exact
            fields[field]={'scaled_error':err,'fine_amplitude':scale,'pass_budget':err<=1e-3 if scale else float(delta[imax])==0.0,'worst_epoch_index':int(ii[imax])}
        sets[count]={'fields':fields,'max_scaled_error':max(x['scaled_error'] for x in fields.values()),'failed_count':sum(not x['pass_budget'] for x in fields.values()),'total_fields':len(fields),'zero_amplitude_fields':[f for f,x in fields.items() if x['fine_amplitude']==0]}
    checks['all_comparison_metrics_exact']=metrics_exact
    files=[EVIDENCE/'EVENT_SPECTRAL_COMPARISON_RECOVERED.json',ROOT/'recovery/RECOVERY_INVENTORY.json',ROOT/'integration/CONTRACT.json',ROOT/'n2/CONTRACT.md',ROOT/'n2/postprocess_moments_recovered.py',ROOT/'n2/compare_spectral_recovered.py']
    files += [d/f for d in [coarse,fine] for f in ['RESULT.json','IDENTITY.json','history.npz','MOMENTS_RECOVERED.json','driver_as_run.py','base_driver_as_run.py']]
    output={'schema':'rei_accel02_saved_003_independent_arithmetic_v1','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'/root/recovery_review','science_solver_calls':0,'native_calls':0,'checks':checks,'all_identity_arithmetic_checks_pass':all(checks.values()),'energy_initial_scale_max':energy,'number_initial_nH_scale_max':number,'spectral':sets,'identities':[{'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files]}
    (HERE/'SAVED_ARITHMETIC.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'checks':checks,'energy':energy,'number':number,'spectral':{k:{f:v[f] for f in ['max_scaled_error','failed_count','total_fields','zero_amplitude_fields']} for k,v in sets.items()}},indent=2))
    return 0 if all(checks.values()) else 1
if __name__=='__main__':raise SystemExit(run())
