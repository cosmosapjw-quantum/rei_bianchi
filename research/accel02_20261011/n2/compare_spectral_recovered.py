#!/usr/bin/env python3
"""Compare saved 128/256 energy histories, frozen 1e-3 budget. No ODE execution."""
from pathlib import Path
import argparse,difflib,hashlib,json
import numpy as np
HERE=Path(__file__).resolve().parent
FIELDS=['xHII','xHeII','xHeIII','T_K','ne_cm3','photon_cm3','GammaHI_s','GammaHeI_s','GammaHeII_s']
MOMENTS=['source_number_ref_cm3_s','source_energy_ref_erg_cm3_s','source_number_proper_cm3_s',
 'source_energy_proper_erg_cm3_s','cumulative_source_number_ref_cm3','cumulative_source_energy_ref_erg_cm3',
 'radiation_energy_ref_erg_cm3','radiation_energy_proper_erg_cm3',
 'photoheat_HI_per_absorber_erg_s','photoheat_HeI_per_absorber_erg_s','photoheat_HeII_per_absorber_erg_s',
 'photoheat_HI_proper_erg_cm3_s','photoheat_HeI_proper_erg_cm3_s','photoheat_HeII_proper_erg_cm3_s','total_photoheat_proper_erg_cm3_s']
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metric(aa,bb,epochs):
    aa=np.array(aa);bb=np.array(bb);scale=float(max(abs(bb[epochs])))
    delta=abs(aa[epochs]-bb[epochs]);j=int(np.argmax(delta));i=int(epochs[j])
    return dict(scaled_error=float(delta[j]/scale if scale else delta[j]),absolute_error=float(delta[j]),
                fine_whole_history_amplitude=scale,fine_all129_amplitude=float(max(abs(bb))),worst_epoch_index=i)
def main():
    p=argparse.ArgumentParser();p.add_argument('coarse',type=Path);p.add_argument('fine',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    ar,br=[read(x/'RESULT.json') for x in (a.coarse,a.fine)]
    ai,bi=[read(x/'IDENTITY.json') for x in (a.coarse,a.fine)]
    am,bm=[read(x/'MOMENTS_RECOVERED.json') for x in (a.coarse,a.fine)]
    protected=['base_sha','events_sha','n1_sha','native_sha','input_identity','semantics']
    identities={k:ai[k]==bi[k] for k in protected}
    identities.update({k:ai['args'][k]==bi['args'][k] for k in ['angle','shear','rtol','max_step']})
    identities['energy_grid_intentional_128_to_256']=ai['args']['energy']==128 and bi['args']['energy']==256
    identities['all_moment_identity_checks']=all(am['identity_checks'].values()) and all(bm['identity_checks'].values())
    times=np.array([r['time_s'] for r in ar['history']]);tf=np.array([r['time_s'] for r in br['history']])
    if len(times)!=129 or not np.array_equal(times,tf):raise ValueError('SHARED_EPOCH_MISMATCH')
    # The changed driver adds fail-closed accepted-gas instrumentation and stricter
    # sampled+endpoint reporting only. Preserve its exact diff for independent review.
    diff=''.join(difflib.unified_diff((a.coarse/'driver_as_run.py').read_text().splitlines(True),
         (a.fine/'driver_as_run.py').read_text().splitlines(True),fromfile='coarse_as_run',tofile='fine_as_run'))
    comparisons={}
    for count,epochs in [('129',np.arange(129)),('65',np.arange(0,129,2))]:
        rows={}
        for fields,left,right in [(FIELDS,ar,br),(MOMENTS,am,bm)]:
            for k in fields:
                m=metric([r[k] for r in left['history']],[r[k] for r in right['history']],epochs)
                m.update(worst_time_s=float(times[m['worst_epoch_index']]),
                    worst_z=float(br['history'][m['worst_epoch_index']]['z']),
                    pass_budget=(m['scaled_error']<=1e-3 if m['fine_whole_history_amplitude']>0 else m['absolute_error']==0.))
                rows[k]=m
        comparisons[count]=dict(fields=rows,pass_all_fields=all(r['pass_budget'] for r in rows.values()),
                    max_scaled_error=max(r['scaled_error'] for r in rows.values()))
    checks={}
    for name,r in [('coarse',ar),('fine',br)]:
        checks[name]=dict(r['checks']);checks[name]['energy_ledger']=max(r['max_endpoint_energy_ledger'],max(abs(x['energy_ledger_scaled']) for x in r['history']))<=1e-9
        checks[name]['number_ledger']=max(r['max_endpoint_number_ledger'],max(abs(x['number_ledger_scaled']) for x in r['history']))<=1e-9
    passed=all(identities.values()) and all(all(v.values()) for v in checks.values()) and all(v['pass_all_fields'] for v in comparisons.values())
    result=dict(status='SPECTRAL_FIELDS_PASS_PENDING_INDEPENDENT_REVIEW' if passed else 'SPECTRAL_REFINEMENT_FAIL',
        method='max_abs(coarse-fine) / max_abs(fine) over the same selected whole-history shared epochs; 65 retains original CONTRACT.md sampling,129 is additional; zero fine amplitude requires exact zero difference',
        frozen_field_budget=1e-3,identity_checks=identities,driver_sha_equal=ai['driver_sha']==bi['driver_sha'],
        driver_change_scope='accepted-gas/finite checks and endpoint+sample ledger reporting only; exact diff retained for review',
        driver_as_run_diff=diff,native_checks=checks,comparisons=comparisons,
        coarse_all_accepted_gas_domain='NOT_MEASURED',fine_all_accepted_gas_domain=br['checks'].get('accepted_gas_domain','NOT_MEASURED'),
        angular_status='NOT_EVALUATED',continuum_error_bound='NOT_ESTABLISHED',
        scientific_ceiling='conditional source-band-limited primary-only CaseA gas+photon history, isotropic CMB bath; no CR/RCT or observer visibility admission',
        files={str(x):sha(x) for d in (a.coarse,a.fine) for x in [d/'RESULT.json',d/'IDENTITY.json',d/'history.npz',d/'MOMENTS_RECOVERED.json']},
        postprocess_code_sha256=sha(HERE/'postprocess_moments_recovered.py'),comparison_code_sha256=sha(Path(__file__)))
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],identity_checks=identities,native_checks=checks,
        maxima={k:v['max_scaled_error'] for k,v in comparisons.items()},
        failed_fields={k:[f for f,v in c['fields'].items() if not v['pass_budget']] for k,c in comparisons.items()}),indent=2))
    return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
