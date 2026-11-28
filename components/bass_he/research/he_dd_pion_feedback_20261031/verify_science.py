#!/usr/bin/env python3
"""Data-only independently constructed scientific evidence checks, no imports from model src."""
from pathlib import Path
import csv,json,math
BASE=Path(__file__).resolve().parent/'data'

def load(name):
    with (BASE/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

a=load('COUPLED_NUCLEAR_PI0_GREEN_RESPONSE_36.csv')
events=load('REACTION_17_RESPONSES_612.csv')
nuclides=load('NUCLIDE_9_SIGNED_RESPONSE_324.csv')
spectra=load('THREE_SPECIES_NUCLEAR_OPACITY_SPECTRA.csv')
sens=load('PI0_RETURN_GRID_SENSITIVITY_5.csv')
anchors=load('SOURCE_MEASURED_INCLUSIVE_OPACITY_ANCHORS_4.csv')
assert (len(a),len(events),len(nuclides),len(spectra),len(sens),len(anchors))==(36,612,324,3048,5,4)
assert len({(r['E_primary_MeV'],r['z'],r['scenario_id']) for r in a})==36
assert all(float(r['D_net_per_initial_pi0'])>0 for r in a)
assert all(float(r['pion_fraction_inclusive'])<1 for r in anchors)
assert all(float(r['measured_minus_pi0_minus_four_alpha_model_micro_b'])>0 for r in anchors)
assert all(float(r['gamma_spectrum'])>=0 and float(r['electron_spectrum'])>=0 and float(r['positron_spectrum'])>=0 for r in spectra)
assert all(float(r['max_pi_kernel_count_norm_abs_err'])<1e-10 for r in a)
assert all(abs(float(r['known_channels_baryon_residual']))<1e-12 for r in a)
assert all(abs(float(r['known_channels_charge_residual']))<1e-12 for r in a)
for r in a:
    key=(r['E_primary_MeV'],r['z'],r['scenario_id'])
    ev={int(t['reaction_id']):float(t['event_response_per_pi0']) for t in events if (t['E_primary_MeV'],t['z'],t['scenario'])==key}
    nu={int(t['nuclide_index']):float(t['signed_delta_Y_per_pi0']) for t in nuclides if (t['E_primary_MeV'],t['z'],t['scenario'])==key}
    assert len(ev)==17 and len(nu)==9
    d=ev[2]+ev[4]+2*ev[8]+ev[9]-ev[1]
    assert abs(d-float(r['D_net_per_initial_pi0']))<1e-13
    assert abs(d-nu[2])<1e-13
    assert abs(ev[11]-float(r['unassigned_inclusive_Li6_gamma_X_events']))<1e-13
for z in ('10000.0','100000.0','1000000.0'):
    for E in ('206','216','229','241'):
        sub={x['scenario_id']:float(x['D_net_per_initial_pi0']) for x in a if x['z']==z and x['E_primary_MeV']==E}
        assert sub['nuclear_loss']<sub['em_only']
        assert sub['measured_pi_gain']>=sub['nuclear_loss']-1e-16
        if E in ('206','216'):assert abs(sub['measured_pi_gain']-sub['nuclear_loss'])<1e-15
print('SOURCE_CONDITIONAL_DATA_AUDIT_PASS',len(a),len(events),len(nuclides),len(spectra),len(sens),len(anchors))
