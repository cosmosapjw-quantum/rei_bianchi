#!/usr/bin/env python3
"""New saved-state moments only: no RHS or ODE execution, no scientific promotion.

Reconstruct the exact open-segment threshold convention of run_event_coupled.
Reference volume is the initial comoving physical cm^3; proper = reference/a^3.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
import numpy as np
import characteristics
from events import native_jump_energies

HERE=Path(__file__).resolve().parent
EV=1.602176634e-12
C=29979245800.
CHI=np.array([13.598434599702,24.587389011,54.41776])

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def moments(run,n1dir):
    identity=json.loads((run/'IDENTITY.json').read_text())
    result=json.loads((run/'RESULT.json').read_text())
    if result['status']!='COMPUTED_NOT_REVIEWED' or len(result['history'])!=129:
        raise ValueError('REQUIRES_COMPLETED_129_EPOCH_SAVED_RUN')
    n1=module('recovered_moment_n1',n1dir/'provider.py')
    p=n1.HistoryProvider(identity['args']['shear'])
    binary=n1dir/'native/target/release/rei_n1_native'
    checks={
        'n1_bytes':sha(n1dir/'provider.py')==identity['n1_sha'],
        'binary_bytes':sha(binary)==identity['native_sha'],
        'source_input_bytes':p.identity==identity['input_identity'],
        'events_code_bytes':sha(HERE/'events.py')==identity['events_sha'],
        'base_as_run_bytes':sha(run/'base_driver_as_run.py')==identity['base_sha'],
        'event_driver_as_run_bytes':sha(run/'driver_as_run.py')==identity['driver_sha'],
    }
    if not all(checks.values()):raise ValueError(f'IDENTITY_MISMATCH:{checks}')
    with np.load(run/'history.npz') as a:
        u=a['u'];states=a['scaled_states']*a['scales'];q=a['q'];mu=a['mu'];weights=a['weights']
    expected=characteristics.make_grid(identity['args']['energy'],identity['args']['angle'],p.q_max_eV)
    checks['saved_grid_exact']=all(np.array_equal(v,w) for v,w in zip((q,mu,weights),expected))
    checks['saved_epoch_exact']=np.array_equal(u,np.linspace(0,1,129))
    checks['json_epoch_exact']=np.array_equal(u*p.end_time_s,[r['time_s'] for r in result['history']])
    if not all(checks.values()):raise ValueError(f'GRID_OR_EPOCH_MISMATCH:{checks}')
    bounds=np.array(json.loads((run/'EVENTS.json').read_text())['boundaries'])
    knots=np.array(sorted(set([10.,13.60,24.59,54.42,50000.]+native_jump_energies(p.tables['emissivity']))))
    extended=np.r_[0.,knots,np.inf]
    rows=[];max_shift=0.;native=n1.Native(binary)
    try:
        for ii,(uu,y) in enumerate(zip(u,states)):
            segment=max(0,min(len(bounds)-2,int(np.searchsorted(bounds,uu,side='left'))-1))
            um=.5*(bounds[segment]+bounds[segment+1]);gm=p.geometry(float(um*p.end_time_s))
            em=characteristics.geometry_nodes(q,mu,gm)[0]
            cell=np.searchsorted(knots,em,side='right');lo=extended[cell];hi=extended[cell+1]
            t=float(uu*p.end_time_s);g=p.geometry(t)
            e,m,ratio=characteristics.geometry_nodes(q,mu,g);ee=e.copy()
            low=ee<=lo;high=ee>=hi;ee[low]=np.nextafter(lo[low],np.inf);ee[high]=np.nextafter(hi[high],0.)
            shift=float(np.max(abs(ee-e)/e));max_shift=max(max_shift,shift)
            if shift>64*np.finfo(float).eps:raise ValueError('EVENT_SPECTRAL_CELL_MISMATCH')
            inside=(em>10.)&(em<50000.);active=em<50000.
            source=np.zeros(len(q))
            source[inside]=p.tables['emissivity'].photon_emission_log(ee[inside],g['z'])*weights[inside]/ratio[inside]**3
            sigma=np.zeros((len(q),3));sigma[active]=native.call('SIGMA',ee[active]).reshape(-1,3)
            U=y[4:4+len(q)];N=U/ee;volume=g['a_rel']**3
            h,he1,he2=y[:3]
            absorbers=np.array([g['nH']*(1-h),g['nHe']*(1-he1-he2),g['nHe']*he1])
            gamma=C*(N@sigma)/volume
            per_absorber=C*EV*np.sum(N[:,None]*sigma*(ee[:,None]-CHI),axis=0)/volume
            heat=absorbers*per_absorber
            counters=y[4+len(q):]
            row=dict(time_s=t,z=g['z'],source_number_ref_cm3_s=float(source.sum()),
                source_energy_ref_erg_cm3_s=float(EV*np.dot(source,ee)),
                source_number_proper_cm3_s=float(source.sum()/volume),
                source_energy_proper_erg_cm3_s=float(EV*np.dot(source,ee)/volume),
                cumulative_source_number_ref_cm3=float(counters[4]),
                cumulative_source_energy_ref_erg_cm3=float(counters[2]),
                radiation_energy_ref_erg_cm3=float(EV*U.sum()),
                radiation_energy_proper_erg_cm3=float(EV*U.sum()/volume),
                photoheat_HI_per_absorber_erg_s=float(per_absorber[0]),
                photoheat_HeI_per_absorber_erg_s=float(per_absorber[1]),
                photoheat_HeII_per_absorber_erg_s=float(per_absorber[2]),
                photoheat_HI_proper_erg_cm3_s=float(heat[0]),
                photoheat_HeI_proper_erg_cm3_s=float(heat[1]),
                photoheat_HeII_proper_erg_cm3_s=float(heat[2]),
                total_photoheat_proper_erg_cm3_s=float(heat.sum()),
                GammaHI_s=float(gamma[0]),GammaHeI_s=float(gamma[1]),GammaHeII_s=float(gamma[2]),
                photon_cm3=float(N.sum()/volume))
            rows.append(row)
    finally:native.close()
    original_match={}
    for key in ['GammaHI_s','GammaHeI_s','GammaHeII_s','photon_cm3']:
        new=np.array([r[key] for r in rows]);old=np.array([r[key] for r in result['history']])
        scale=max(abs(old));original_match[key]=float(max(abs(new-old))/scale if scale else max(abs(new-old)))
    if max(original_match.values())>1e-13:raise ValueError(f'SAVED_OBSERVABLE_RECONSTRUCTION_MISMATCH:{original_match}')
    hashes={name:sha(run/name) for name in ['IDENTITY.json','RESULT.json','history.npz','EVENTS.json','driver_as_run.py','base_driver_as_run.py']}
    return dict(status='POSTPROCESSED_NO_ODE_NO_PROMOTION',run=run.name,saved_file_sha256=hashes,
        implementation_sha256=sha(__file__),characteristics_sha256=sha(HERE/'characteristics.py'),
        characteristics_run_identity='NOT_SEPARATELY_RECORDED_IN_ORIGINAL_IDENTITY; grid checked byte-exact; implementation from published source',
        identity_checks=checks,original_observable_reconstruction_scaled_errors=original_match,
        max_one_sided_relative_energy_shift=max_shift,native_calls='SIGMA only; no RHS',
        units='cgs; reference initial physical cm^3; proper = reference/a_rel^3; cumulative source counters are integrals per reference cm^3',
        heat_definition='primary photoelectron excess power only: c sum_i N_i sigma_ia (E_i-chi_a) EV/a^3; total proper photoheat=sum_a n_abs,a H_a. Cooling, Compton, CI and expansion are not included in this diagnostic.',
        spectral_field_target=1e-3,accepted_gas_domain=result['checks'].get('accepted_gas_domain','NOT_MEASURED'),
        history=rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--n1',type=Path,default=HERE.parent/'n1');a=p.parse_args()
    out=a.run/'MOMENTS_RECOVERED.json'
    if out.exists():raise FileExistsError(out)
    r=moments(a.run,a.n1);out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='history'},indent=2))
if __name__=='__main__':main()
