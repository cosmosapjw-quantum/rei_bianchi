# SPDX-License-Identifier: GPL-3.0-only
"""Proper-frame cosmic-ray source and frozen AXBI thin-target diagnostics.

The PHYS02 saved electron source and the AXBI primary collision experiment
are separate systems. Each has its own gas state, proper clock and energy ledger.
The companion Rudd notice and GPL text are in ``cr_sources``.
"""
from __future__ import annotations

from importlib.resources import files
import hashlib
import io
import json
import math

import numpy as np

from .cr_sources import injection, ports, rudd

DATA = files(__package__ + '.cr_sources')
PAYLOAD_SHA = '7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc'
ENERGY_SHA = '6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292'
ARRAY_SHA = '07dd0fa81154f5aecaf262b00c2adfada21ebc9b2a2dba59703e03e3f5dab609'
PHYS02_REV = 'ec463db0c7e5c7fb5070796071c926caa4db6445'
STATE = 'PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED'
FRAME = 'prescribed_gas_rest_frame_scalar'
MAPPING = 'CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4'
END_S = 1.0e10
# AXBI HHeModel::controlled_fixture thresholds for the elemental ion reservoir.
OWNER_THRESHOLD_EV = {'H': 13.598434599702, 'He': 24.587389011}


def integrate_phys02(start_s=0.0, stop_s=END_S, *, population='selected_total', include_spectrum=False):
    """Integrate stored PHYS02 birth atoms on a finite fixed proper volume.

    ``number_m3`` counts directly ejected electrons. ``coordinate_energy_J_m3``
    is their kinetic energy density. The fixed PHYS02 100 K gas need not equal
    a REI recipient. ``ports.claim_injection`` detects overlapping claims when
    combining populations from this same source family.
    """
    raw = DATA.joinpath('SPECTRUM_fullBED_9600.npz').read_bytes()
    if hashlib.sha256(raw).hexdigest() != PAYLOAD_SHA:
        raise ValueError('PHYS02 spectrum checksum mismatch')
    with np.load(io.BytesIO(raw), allow_pickle=False) as f:
        energies, vectors = f['energy_eV'], f['source_vectors']
        scale = float(f['physical_energy_scale_eV_m3'])
        times = f['time_s'].tolist()
    if (energies.shape != (9600,) or vectors.shape != (9611, 2) or
            hashlib.sha256(energies.tobytes()).hexdigest() != ENERGY_SHA or
            hashlib.sha256(vectors.tobytes()).hexdigest() != ARRAY_SHA or
            times != [0.0, END_S] or scale != 1.1242596728743301e-13):
        raise ValueError('PHYS02 saved array or physical scale mismatch')
    bands = {'direct_0p1_10': (0, [0.1,10.0]), 'direct_10_900': (1,[10.0,900.0]),
             'selected_total': (None,[0.1,900.0])}
    if population not in bands:
        raise ValueError('unknown PHYS02 birth partition')
    col, support = bands[population]
    weights = [float(row[col]) if col is not None else math.fsum(row) for row in vectors]
    conv = scale / END_S**2
    atoms = [{'energy_eV':float(e), 'number_coefficients':[0.0,conv*w/float(e)],
              'stored_node_index':i} for i,(e,w) in enumerate(zip(energies,weights)) if w]
    # Two entries are the number and kinetic energy of the same boundary atom.
    cutoff_n, cutoff_e = weights[9608], weights[9605]
    if not math.isclose(0.1*cutoff_n, cutoff_e, rel_tol=2e-13, abs_tol=0.0):
        raise ValueError('PHYS02 boundary energy and number disagree')
    if cutoff_n:
        atoms.append({'energy_eV':0.1, 'number_coefficients':[0.0,conv*cutoff_n],
                      'stored_node_index':'cutoff_boundary'})
    number_coeff = math.fsum(atom['number_coefficients'][1] for atom in atoms)
    energy_coeff = conv*math.fsum(weights[:9600]+[cutoff_e])
    definition = {'source_model':'PHYS02_Qe_tA_leading_local','state':STATE,'frame':FRAME,
                  'mapping':MAPPING,'energy_scale_eV_m3':scale,'known_time_s':times,
                  'native_secondary_eV':[0.1,900.0],'proton_collision_eV':[1e6,4e6],
                  'normalization':'proper_volume_clock_target_angle_already_included'}
    event = ports.build_source_event(physical_definition_sha256=ports.digest(definition),
                energy_array_sha256=ENERGY_SHA, source_array_sha256=ARRAY_SHA,
                family_native_birth_support_eV=[0.1,900.0], native_birth_support_eV=support,
                clock_origin_s=0.0)
    source = {'schema':'CR_PROPER_SOURCE_V1',
        'source':{'repository':'cosmosapjw-quantum/bass_cr','revision':PHYS02_REV,
                  'payload_sha256':PAYLOAD_SHA,'evidence_kind':'stored_physical'},
        'particle':{'kind':'electron','isotope':'e-','state':'PHYS02_direct_secondary_birth',
                    'energy_coordinate':'kinetic_eV'},
        'medium':{'state_id':STATE,'frame':FRAME,'temperature_K':100.0,
                  'proper_volume_mode':'fixed','proper_volume_m3':None},
        'isotope_mapping':MAPPING,'support_eV':support,'source_event':event,
        'representation':'atomic_bins','history_boundary':'unknown_outside_recorded_segments',
        'normalization':{'clock_measure':'proper_s','volume_measure':'proper_m3',
            'd_native_clock_d_proper_s':1.0,'d_native_volume_d_proper_m3':1.0,
            'target_density_mode':'already_included','target_density_m3':None,'applied_tokens':[]},
        'history':[{'start_s':0.0,'stop_s':END_S,'number_coefficients':[0.0,number_coeff],
                    'energy_coefficients_eV':[0.0,energy_coeff],'bins':atoms}]}
    result = ports.integrate_history(source,[start_s,stop_s])
    result['population'] = population
    result['integrated_spectrum_atoms'] = len(result['spectrum'])
    if not include_spectrum:
        result.pop('spectrum')
    return result


def axbi_snapshots():
    """Return source-identified five-case gas rows and the quadrature selection."""
    return json.loads(DATA.joinpath('axbi_rows.json').read_text())


def snapshot_primary_ionization(snapshot, proper_exposure_s=END_S, *, enabled=True,
                                energy_order=48, age_order=8, mu_order=8):
    """End-of-window, proper-volume collision rates in the frozen AXBI gas.

    Start with empty CR inventory. The input comes from a matched AXBI scale
    slice. A separate hypothetical CR source fills it over ``proper_exposure_s``.
    H and shear stay constant during this conditional window. Model protons in
    the 1..4 MeV band ionize H I and He I in the optically thin approximation.
    Number densities outside that band retain their kinetic inventory.
    """
    if isinstance(snapshot, str):
        snapshot = axbi_snapshots()['rows'][snapshot]
    a, z, q = (float(snapshot[k]) for k in ('a','zbar','q_ref'))
    n_h = float(snapshot['nH_proper_cm3'])*1e6
    frac_h, frac_he = float(snapshot['x_HI']), float(snapshot['x_HeI'])
    if not (math.isfinite(a) and a > 0 and math.isclose(1/a-1,z,rel_tol=2e-12,abs_tol=2e-14)
            and math.isfinite(q) and math.isfinite(n_h) and n_h > 0
            and 0 <= frac_h <= 1 and 0 <= frac_he <= 1):
        raise ValueError('invalid AXBI snapshot redshift, density, or neutral fraction')
    # axbi_driver.rs owns q=s(ai)/HF(ai) and the helium mass fraction.
    def h_flrw(scale):
        h0 = 67.4e5 / 3.0856775814913673e24
        return h0 * math.sqrt(0.315/scale**3 + 9.2e-5/scale**4 + 1-0.315-9.2e-5)
    a_ref = 1/21
    s = q*h_flrw(a_ref)*(a_ref/a)**3
    h = math.hypot(h_flrw(a),s)
    n_he = n_h*0.2454/(4*(1-0.2454))
    model = injection.InjectionModel(z_snapshot=z, enabled=enabled)
    pop = injection.transport_population(model,proper_exposure_s,h,s,
                    energy_order=energy_order, age_order=age_order, mu_order=mu_order)
    k = pop['nodes']['kinetic_eV']
    weights = pop['nodes']['number_density_m3']
    speed = rudd.proton_speed_m_s(k)
    rates, binding, kinetic, loss, offset, thin = {}, {}, {}, {}, {}, []
    # R(t)=integral_0^t K(u)du for stationary injection. Interchanging two
    # integrals gives (T-u) for the time integral of a local volume rate.
    # Final proper density in an expanding comoving cell instead weighs births
    # at t by exp[-3 H (T-t)], giving -expm1[-3H(T-u)]/(3H).
    remaining = proper_exposure_s-pop['nodes']['age_s']
    time_weights = {'window':remaining,
                    'comoving_window_final_volume':-np.expm1(-3*h*remaining)/(3*h)}
    integral = {key:{channel:{} for channel in ('primary_ions_m3','projectile_debit_J_m3',
                'fast_birth_J_m3','threshold_offset_J_m3','owner_binding_J_m3')}
                for key in time_weights}
    for target, density in [('H',n_h*frac_h),('He',n_he*frac_he)]:
        moments = rudd.cross_section_moments(k,target)
        flux = density * speed * weights
        rates[target] = float(np.sum(flux*moments['sigma_m2']))
        binding[target] = rates[target]*OWNER_THRESHOLD_EV[target]*rudd.EV_J
        offset[target] = rates[target]*(rudd.TARGETS[target]['I_eV']-OWNER_THRESHOLD_EV[target])*rudd.EV_J
        kinetic[target] = float(np.sum(flux*moments['secondary_eV_m2']))*rudd.EV_J
        loss[target] = float(np.sum(flux*moments['loss_eV_m2']))*rudd.EV_J
        for measure, time_weight in time_weights.items():
            weighted = flux*time_weight
            ions = float(np.sum(weighted*moments['sigma_m2']))
            values = integral[measure]
            values['primary_ions_m3'][target] = ions
            values['owner_binding_J_m3'][target] = ions*OWNER_THRESHOLD_EV[target]*rudd.EV_J
            values['threshold_offset_J_m3'][target] = ions*(rudd.TARGETS[target]['I_eV']-OWNER_THRESHOLD_EV[target])*rudd.EV_J
            values['fast_birth_J_m3'][target] = float(np.sum(weighted*moments['secondary_eV_m2']))*rudd.EV_J
            values['projectile_debit_J_m3'][target] = float(np.sum(weighted*moments['loss_eV_m2']))*rudd.EV_J
        thin.append(float(np.max(speed*density*moments['loss_eV_m2']/k))*proper_exposure_s if k.size else 0.0)
    thin_diagnostic = math.fsum(thin)
    if thin_diagnostic > 1e-3:
        raise ValueError('thin-target sampled loss fraction exceeds the donor validity criterion')
    totals = [math.fsum(values.values()) for values in (binding,kinetic,offset,loss)]
    residual = math.fsum([*totals[:3],-totals[3]])
    window = {f'{measure}_{channel}_by_target':values for measure,channels in integral.items()
              for channel,values in channels.items()}
    return {**window, 'case':snapshot.get('case'),'a':a,'zbar':z,'H_s_inv':h,'shear_s_inv':s,
       'enabled':enabled,'proper_exposure_s':proper_exposure_s,'frame':'gas_rest_nontilted',
       'nHI_m3':n_h*frac_h,'nHeI_m3':n_he*frac_he,'primary_ion_rates_m3_s':rates,
       'fast_electron_births_m3_s':math.fsum(rates.values()),
       'fast_birth_J_m3_s_by_target':kinetic, 'threshold_offset_J_m3_s_by_target':offset,
       'owner_binding_J_m3_s_by_target':binding, 'projectile_debit_J_m3_s_by_target':loss,
       'thermal_electron_source_m3_s':None, 'prompt_gas_heat_J_m3_s':None,
       'binding_power_J_m3_s':totals[0], 'fast_electron_birth_power_J_m3_s':totals[1],
       'threshold_model_offset_J_m3_s':totals[2],'modeled_proton_loss_J_m3_s':totals[3],
       'partition_residual_J_m3_s':residual,'sampled_thin_loss_fraction':thin_diagnostic,
       'sampled_thin_loss_scope':'endpoint quadrature maximum times age for each target',
       'full_injection_power_J_m3_s':model.power_proper_J_m3_s(),
       'storage':pop['budgets'],'quadrature_orders':[energy_order,age_order,mu_order],
       'actual_owner_state_evolved':False}


def axbi_source_experiment():
    """Run the frozen one-window calculation on every matched gas snapshot."""
    data = axbi_snapshots()
    results = {name:snapshot_primary_ionization(row) for name,row in data['rows'].items()}
    coarse = {name:snapshot_primary_ionization(row, energy_order=24, age_order=4, mu_order=4)
              for name,row in data['rows'].items()}
    def precision(name):
        return max(abs(coarse[name]['primary_ion_rates_m3_s'][k]/result-1)
                   for k,result in results[name]['primary_ion_rates_m3_s'].items())
    return {'source_blob':data['git_blob'],'source_gzip_sha256':data['gzip_sha256'],
            'experiment':'optional CR switch, frozen AXBI snapshots and constant geometry over proper exposure',
            'cases':results, 'coarse_to_fine_max_primary_rate_relative_change':{key:precision(key) for key in results},
            'cr_off':snapshot_primary_ionization(data['rows']['SHEAR_PLUS'],enabled=False)}
