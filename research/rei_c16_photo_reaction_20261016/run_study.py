"""Reproducible bounded source-aware photon/gas numerical investigation."""
from __future__ import annotations
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from time import perf_counter
import json,math,platform
import numpy as np
from test_source_aware import state_ref,ode_reference
import source_aware as s

ROOT=Path(__file__).resolve().parent
x0=state_ref()
proper_dt_s=5e10
n_H_cm3=1e-3
reference=ode_reference(x0,proper_dt_s,n_H_cm3)
refinements=[]
for steps in (1,2,4,8,16,32,64,128,256):
    start=perf_counter()
    out,led=s.evolve(x0,proper_dt_s,n_H_cm3,reaction_substeps=steps)
    wall=perf_counter()-start
    y=np.array([p.n_per_h for p in out.photons]+list(out.gas.__dict__.values()))
    refinements.append({
      'reaction_substeps':steps,'max_state_abs_difference':float(np.max(np.abs(y-reference))),
      'abs_number_residual':abs(led.number_residual),'abs_energy_residual_eV_per_H':abs(led.energy_residual_ev),
      'abs_H_nuclei_residual':abs(led.hydrogen_residual),'abs_He_nuclei_residual':abs(led.helium_residual),
      'photoevents_HI_HeI_HeII':list(led.photo_events),'heat_eV_per_H':led.photoheat_ev,
      'binding_eV_per_H':led.binding_energy_ev,'wall_seconds':wall,
    })
for p,q in zip(refinements[1:-1],refinements[2:]):
    q['observed_error_ratio_previous_over_current']=p['max_state_abs_difference']/q['max_state_abs_difference']

gas=s.Gas(1.,0.,.05,.03,0.)
shape0=s.State((s.Node(60.,0.,1.),),gas)
shape1=s.State((s.Node(40.,0.,.5),s.Node(80.,0.,.5)),gas)
shape_results=[]
for shape in (shape0,shape1):
    after,led=s.evolve(shape,4e9,1e-3)
    shape_results.append({'initial_N':shape.nphot,'initial_U_eV_per_H':shape.u_phot_ev,
                          'HeII_photoevents_per_H':led.photo_events[2],
                          'all_photoevents':list(led.photo_events),
                          'absorbed_energy_eV_per_H':led.absorbed_energy_ev,
                          'ledger_energy_residual':led.energy_residual_ev})

# Cross-check instantaneous directional redshift-work from the exact Killing E.
signed_case=[]
for b in (-.12,-.05,0.,.05,.12):
    after,ledger=s.evolve(x0,0.,1e-3,a_end=1.08,b_end=b)
    signed_case.append({'delta_b':b,'a_end':1.08,'work_eV_per_H':ledger.geometric_work_ev,
                        'relative_work_over_E0':ledger.geometric_work_ev/x0.u_phot_ev,
                        'energy_ledger_residual_eV_per_H':ledger.energy_residual_ev,
                        'photon_counts_preserved':after.nphot==x0.nphot})

report={
'schema':'rei.source_aware.photo_reaction.study.v1',
'run_platform':{'python':platform.python_version(),'numpy':np.__version__},
'science_scope':'conditional 3-species Verner photoionization, immutable photon-q nodes and analytic pair Strang composition; no production integration',
'metric_signature':'(-,+,+,+)','reference_epoch_a':1.,
'proper_dt_seconds':proper_dt_s,'n_h_proper_cm3':n_H_cm3,
'atomic_source':{'paper':'Verner et al. 1996 ApJ 465 487','doi':'10.1086/177435',
                'rei_PR152_commit':'bbbd18b5c16eff70bc32ba4296360dceb9060ec4',
                'full_donor_sha256':'a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389',
                'sourced_rows':3,'photo_fit_threshold_eV':[v[0] for v in s.VERNER_ROWS],
                'physical_binding_eV':list(s.CHI_EV)},
'original_state':{'photons':[asdict(p) for p in x0.photons],'gas':asdict(x0.gas)},
'reference_solver':{'method':'DOP853','rtol':2e-12,'atol':2e-14,'output':'all photon node and gas states'},
'refinements':refinements,
'spectrum_degeneracy':{'cases':shape_results,'difference_HeII_photoevents_per_H':shape_results[0]['HeII_photoevents_per_H']-shape_results[1]['HeII_photoevents_per_H'],
                       'meaning':'positive spectra with identical N/U differ in HeII absorption; no unique spectral recovery from two moments'},
'signed_background_geometry':signed_case,
'claim_limits':['No recombination/Thomson/CMB/stellar reservoir','Neutral opacity self-coupled only through H-He photoionization','Time-dependent geometry split first-order as currently arranged','No baryon momentum Euler owner','No cosmological full-History or local workstation/NCP execution']}
ROOT.joinpath('study_results.json').write_text(json.dumps(report,indent=2)+'\n')
print('REFINEMENT')
for v in refinements:print(v['reaction_substeps'],v['max_state_abs_difference'],v.get('observed_error_ratio_previous_over_current'),v['abs_energy_residual_eV_per_H'])
print('SPECTRAL_DIFFERENCE_HeII',report['spectrum_degeneracy']['difference_HeII_photoevents_per_H'])
print('SIGNED',signed_case)
