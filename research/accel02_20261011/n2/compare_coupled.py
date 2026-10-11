"""Compare actual shared-epoch coupled histories; no permission to relax gates."""
from pathlib import Path
import argparse,json
import numpy as np


def compare_paths(coarse,fine):
    a=json.loads((coarse/'RESULT.json').read_text());b=json.loads((fine/'RESULT.json').read_text())
    ia=json.loads((coarse/'IDENTITY.json').read_text());ib=json.loads((fine/'IDENTITY.json').read_text())
    protected=['base_sha','driver_sha','events_sha','n1_sha','native_sha','input_identity']
    identities_equal={k:ia[k]==ib[k] for k in protected}
    physics_equal={k:ia['args'][k]==ib['args'][k] for k in ['energy','angle','shear']}
    times=np.array([r['time_s'] for r in a['history']]);tf=np.array([r['time_s'] for r in b['history']])
    if len(times)!=129 or not np.array_equal(times,tf):raise ValueError('SHARED_EPOCHS_NOT_IDENTICAL')
    fields=['xHII','xHeII','xHeIII','T_K','ne_cm3','photon_cm3','GammaHI_s','GammaHeI_s','GammaHeII_s']
    errors={}
    absolute={}
    for k in fields:
        aa=np.array([r[k] for r in a['history']]);bb=np.array([r[k] for r in b['history']])
        absolute[k]=float(max(abs(aa-bb)));scale=float(max(abs(bb)))
        errors[k]=absolute[k]/scale if scale else absolute[k]
    energy_max=max(b['max_endpoint_energy_ledger'],max(abs(r['energy_ledger_scaled']) for r in b['history']))
    number_max=max(b['max_endpoint_number_ledger'],max(abs(r['number_ledger_scaled']) for r in b['history']))
    checked=b['checks'].copy();checked['energy_ledger']=energy_max<=1e-9;checked['number_ledger']=number_max<=1e-9
    checked['sampled_gas_domain']=all(np.isfinite([r[k] for k in ['xHII','xHeII','xHeIII','T_K']]).all() and
        0<=r['xHII']<=1 and r['xHeII']>=0 and r['xHeIII']>=0 and r['xHeII']+r['xHeIII']<=1 and 1<=r['T_K']<=1e6 for r in b['history'])
    return dict(status='PASS_SHARED_DISCRETIZATION_TIME_ONLY' if all(identities_equal.values()) and all(physics_equal.values()) and max(errors.values())<=2e-6 and all(checked.values()) else 'FAIL',
                source_identity_equal=identities_equal,physics_equal=physics_equal,observable_scaled_errors=errors,
                observable_absolute_errors=absolute,time_field_target=2e-6,fine_native_checks=checked,
                fine_max_energy_initial_scale=energy_max,fine_max_number_NH_scale=number_max,
                fine_strict_min_accepted_photon_energy=b['min_accepted_photon_energy'],
                fine_all_accepted_gas_domain='NOT_EXPLICITLY_MEASURED_IN_ORIGINAL_RUN',
                sample_count=len(times),spectral_angular_status='NOT_EVALUATED_BY_SAME_GRID_TIME_COMPARISON',
                scientific_ceiling='conditional selected band primary-only CaseA native history; no CR/RCT admission or continuum error bound')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('coarse',type=Path);p.add_argument('fine',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=compare_paths(a.coarse,a.fine);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
    raise SystemExit(0 if r['status']=='PASS_SHARED_DISCRETIZATION_TIME_ONLY' else 1)
