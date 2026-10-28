"""Actual saved GRID044 endpoint consumer; no quadrature, IVP, or fitted rate.

The reused REC response is already per reference nucleus per proper second.
Only new normalization algebra and bindings are implemented here. Thermal
heating, finite-mass stopping, angular absorption and geometry feedback remain
unsupplied. The 25 response outputs are not a 25-state evolution system.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'reused'))
import chem_ledger as wu
import opacity_response as rec
from source_ledger import reaction_event_ledger

EV_TO_J = 1.602176634e-19
C_M_S = 299792458.0
FRAME = 'normal_tetrad_stationary_ground_state'
REFERENCE = 'fixed_comoving_bookkeeping_number'
SOURCE_NAMES = ('stellar', 'external_IGM')
SUPPORT_EV = (5.0, 150.0)
SOURCE_ID = 'GRID044_CONTINUOUS_OPACITY_RESPONSE_20261025'


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def check_input_identity():
    manifest = json.loads((ROOT / 'SOURCE_MANIFEST.json').read_text())
    checked = []
    for row in manifest['files']:
        data = (ROOT / row['path']).read_bytes()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('IMMUTABLE_INPUT_IDENTITY:' + row['path'])
        checked.append(row['path'])
    return checked


def normalize_source_directional(x, source, reference, *, reference_source=0.0,
                                 dx=None, dsource=None, dreference=0.0,
                                 dreference_source=0.0):
    """Return F=(S-xR)/r and its tangent in the caller's actual coordinates.

    dsource already includes the caller's physical-to-state composition. This
    function never differentiates a provider implicitly or interprets dsource
    as a derivative with respect to physical n. r>0; all base/tangent data finite.
    """
    x = np.asarray(x)
    source = np.asarray(source)
    dx = np.zeros_like(x) if dx is None else np.asarray(dx)
    dsource = np.zeros_like(source) if dsource is None else np.asarray(dsource)
    if x.ndim != 1 or source.shape != x.shape or dx.shape != x.shape or dsource.shape != x.shape:
        raise ValueError('NORMALIZATION_SHAPE')
    scalar = np.asarray([reference, reference_source, dreference, dreference_source])
    if np.iscomplexobj(scalar) or not np.all(np.isfinite(scalar)) or reference <= 0:
        raise ValueError('POSITIVE_FINITE_REFERENCE_REQUIRED')
    if any(not np.all(np.isfinite(v)) for v in (x, source, dx, dsource)):
        raise ValueError('FINITE_NORMALIZATION_DATA_REQUIRED')
    f = (source - x * reference_source) / reference
    df = (dsource - reference_source * dx - x * dreference_source) / reference
    df -= f * dreference / reference
    return f, df


def load_inputs():
    check_input_identity()
    payload = json.loads((ROOT / 'inputs/AGGREGATE_PAYLOAD.json').read_text())
    config = json.loads((ROOT / 'inputs/MODEL_CONFIG.json').read_text())
    contract = json.loads((ROOT / 'inputs/GRID044_IMPLEMENTATION_CONTRACT.json').read_text())
    with np.load(ROOT / 'inputs/grid044_history.npz', allow_pickle=False) as archive:
        labels = archive['atomic_state_labels'].tolist()
        if len(labels) != 21 or len(set(labels)) != 21 or set(labels) != set(rec.SPECIES):
            raise ValueError('DONOR_SPECIES_LABEL_MISMATCH')
        ix = [labels.index(label) for label in rec.SPECIES]
        x_saved = archive['atomic_abundance_per_Href'][:, -1]
        x = x_saved[ix]
        endpoint = {}
        for key in archive.files:
            arr = archive[key]
            if arr.ndim == 1 and arr.shape[0] == archive['eta'].shape[0]:
                endpoint[key] = arr[-1].item()
            elif arr.ndim == 2 and arr.shape[0] == archive['eta'].shape[0]:
                endpoint[key] = arr[-1].tolist()
            elif arr.ndim == 0:
                endpoint[key] = arr.item()
        endpoint['Y_all_62_endpoint'] = archive['Y'][:, -1].tolist()
    rates = np.asarray(payload['rates_per_source_target'], dtype=float)
    r = float(payload['nHref_m3'])
    a = float(endpoint['a'])
    binding = {
        'donor_state_sha256': 'ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b',
        'selection': 'last stored time column, index 200; no interpolation or trajectory replay',
        'donor_species_order': labels,
        'consumer_species_order': list(rec.SPECIES),
        'consumer_to_donor_indices': ix,
        'donor_atomic_abundance_per_Href': x_saved.tolist(),
        'actual_abundance_per_ref': x.tolist(),
        'actual_zero_labels': [label for label, value in zip(rec.SPECIES, x) if value == 0],
        'endpoint': endpoint,
        'reference': {'mode': REFERENCE, 'r_m3': r, 'a': a, 'a_today': 1.0,
                      'n_ref0_m3': r * a**3, 'coordinate_volume_today_m3': 1.0,
                      'N_ref_in_selected_coordinate_volume': r * a**3,
                      'S_ref_m3_s': 0.0, 'independent_of_actual_nuclear_or_H_counts': True,
                      'donor_nH_ref_cm3_to_m3': endpoint['nH_ref_cm3'] * 1e6},
        'time': {'proper_seconds': endpoint['proper_elapsed_s'], 'client_local_t_star_s': 0.0,
                 'eta_log_a_over_a_initial': payload['eta'], 'redshift': payload['redshift']},
        'frame': FRAME,
        'temperature_role': 'saved background only; no thermal rate, recombination fit or heating used',
        'state_source_relation': 'instantaneous counterfactual: actual saved donor target paired with independently prescribed continua; not a new trajectory',
        'old_donor_photo_rates_role': 'saved context only; not used as selected source moments',
    }
    validate_binding(x, rates, SOURCE_NAMES, (1.0, 1.0), rec.SPECIES, r, FRAME,
                     SUPPORT_EV, REFERENCE, SOURCE_ID)
    if payload['unit'] != SOURCE_ID or tuple(payload['sources']) != SOURCE_NAMES:
        raise ValueError('SAVED_SOURCE_IDENTITY_MISMATCH')
    if tuple(config['birth_energy_support_eV']) != SUPPORT_EV:
        raise ValueError('SAVED_SOURCE_SUPPORT_MISMATCH')
    if tuple(contract['sources']['birth_support_eV']) != SUPPORT_EV:
        raise ValueError('CONTINUUM_CONTRACT_SUPPORT_MISMATCH')
    return x, rates, binding, payload, config, contract


def validate_binding(x, rates, source_names, amplitudes, labels, reference,
                     frame, support, reference_mode, source_id):
    if tuple(labels) != rec.SPECIES:
        raise ValueError('ORDERED_SPECIES_LABEL_MISMATCH')
    if rates is None or source_names is None or tuple(source_names) != SOURCE_NAMES:
        raise ValueError('MISSING_OR_WRONG_REQUIRED_SOURCE')
    if source_id != SOURCE_ID:
        raise ValueError('SPECTRAL_PROVIDER_SUBSTITUTION_REJECTED')
    if frame != FRAME or reference_mode != REFERENCE:
        raise ValueError('FRAME_OR_REFERENCE_MODE_MISMATCH')
    if tuple(support) != SUPPORT_EV:
        raise ValueError('SOURCE_BIRTH_SUPPORT_MISMATCH')
    frozen_r = 5.151254745827818
    if not math.isfinite(reference) or reference <= 0 or abs(reference / frozen_r - 1) > 1e-14:
        raise ValueError('REFERENCE_DENSITY_MISMATCH')
    for name, arr, shape in [('state', x, (21,)), ('rates', rates, (2, 6, 3)), ('amplitudes', amplitudes, (2,))]:
        arr = np.asarray(arr)
        if arr.shape != shape or np.iscomplexobj(arr) or not np.all(np.isfinite(arr)) or np.any(arr < 0):
            raise ValueError('INVALID_PHYSICAL_' + name.upper())


def species_records():
    nuclei = {'n': (0, 1), 'H1': (1, 1), 'D': (1, 2), 'T': (1, 3),
              'He3': (2, 3), 'He4': (2, 4), 'Li6': (3, 6), 'Li7': (3, 7)}
    rows = {}
    for label in rec.SPECIES:
        isotope, charge = ('n', 0) if label == 'n' else (label.rsplit('_', 1)[0], int(label.rsplit('_', 1)[1]))
        z, a = nuclei[isotope]
        rows[label] = {'composition': [{'Z': z, 'A': a, 'isomer': 'ground', 'count': 1}],
                       'charge': charge, 'state': 'ground', 'pool': 'material'}
    rows['e_fast'] = {'composition': [], 'charge': -1, 'state': 'continuum_unresolved_spectrum', 'pool': 'electron_fast'}
    return rows


def reactions():
    return [{'event_id': 'photo:' + rec.SPECIES[lower] + '->' + rec.SPECIES[upper],
             'reactants': [[rec.SPECIES[lower], 1]],
             'products': [[rec.SPECIES[upper], 1], ['e_fast', 1]],
             'kind': 'chemical', 'normalization': wu.NORMALIZATION,
             'provider': 'REC_GRID044_saved_continuum_moments',
             'provider_domain': 'z=2; birth support 5..150 eV; inherited valence electronic channel',
             'frame': FRAME, 'process': 'ground_state_single_photoionization',
             'direction': 'lower_charge_to_next_charge', 'state_resolution': 'ground_isotope_charge_plus_fast_electron',
             'ownership_slot': 'physical_extent', 'activation': 'active',
             'energy_partition': 'REC:P,chi*Gamma,K; CR:generic_event_ledger; HE:unqualified_degradation',
             'channel_index': ch, 'lower_index': lower, 'upper_index': upper}
            for lower, upper, ch in rec.EDGES]


def canonical_physical_key(reaction, species):
    """Independent of provider-domain prose: one physical event, one extent."""
    if reaction['process'] != 'ground_state_single_photoionization' or reaction['frame'] != FRAME:
        raise ValueError('UNSELECTED_EVENT_PROCESS_OR_FRAME')
    return (wu.side_signature(reaction['reactants'], species),
            wu.side_signature(reaction['products'], species),
            reaction['process'], reaction['frame'])


def check_extent_owners(event_rows, species):
    active = {}
    for reaction in event_rows:
        if reaction.get('activation', 'active') != 'active':
            continue
        key = canonical_physical_key(reaction, species)
        if key in active:
            raise ValueError('DUPLICATE_PHYSICAL_EXTENT_OWNER:' + reaction['event_id'])
        active[key] = reaction['provider']
    return active


def evaluate_endpoint():
    x, rates, binding, payload, config, contract = load_inputs()
    r = binding['reference']['r_m3']
    f, jac, total_events = rec.target_response(x, rates, (1.0, 1.0))
    records = species_records()
    species = wu.catalog(records)
    event_rows = reactions()
    wu.register_ownership(event_rows, species)
    check_extent_owners(event_rows, species)
    material = {label: Fraction(0) for label in records}
    source_scales = np.zeros(22)
    matrix = np.zeros((21, 21))
    contributions = []
    for reaction in event_rows:
        nu = wu.conservation(reaction, species)['nu']
        lower, ch = reaction['lower_index'], reaction['channel_index']
        for si, source_name in enumerate(SOURCE_NAMES):
            gamma, power, primary = rates[si, ch]
            extent = Fraction(str(float(x[lower]))) * Fraction(str(float(gamma)))
            output = wu.source(reaction, species, extent)
            for label, value in output.items():
                material[label] += value
                i = 21 if label == 'e_fast' else rec.SPECIES.index(label)
                source_scales[i] += abs(float(value))
            for label, stoich in nu.items():
                if label != 'e_fast':
                    matrix[rec.SPECIES.index(label), lower] += stoich * gamma
            ledger = reaction_event_ledger(imported_photon_ev=float(power/gamma),
                                          primary_binding_ev=float(rec.CHI_EV[ch]),
                                          electron_kinetic_ev=float(primary/gamma),
                                          recoil_ev=0.0, escaping_other_ev=0.0)
            energy = x[lower] * np.asarray([-power, rec.CHI_EV[ch]*gamma, primary])
            contributions.append({'event_id': reaction['event_id'], 'source': source_name,
                                  'channel': rec.CHANNEL_NAMES[ch], 'lower': rec.SPECIES[lower],
                                  'upper': rec.SPECIES[reaction['upper_index']],
                                  'target_abundance_per_ref': float(x[lower]),
                                  'Gamma_s_inverse': float(gamma), 'P_eV_s_per_target': float(power),
                                  'K_eV_s_per_target': float(primary), 'chi_eV': float(rec.CHI_EV[ch]),
                                  'event_rate_per_ref_s': float(extent),
                                  'event_rate_m3_s': r*float(extent),
                                  'species_and_fast_electron_source_per_ref_s': {k: float(v) for k,v in output.items()},
                                  'energy_order': ['radiation_loss_signed','binding_gain','primary_electron_gain'],
                                  'energy_eV_per_ref_s': energy.tolist(),
                                  'energy_J_m3_s': (energy*r*EV_TO_J).tolist(),
                                  'CR_generic_event_ledger_eV': ledger,
                                  'recoil_model': 'stationary target, original no-recoil approximation',
                                  'extent_owner': reaction['provider']})
    assembled = np.asarray([float(material[label]) for label in list(rec.SPECIES)+['e_fast']])
    residuals = wu.source_residuals(material, species)
    conservation = {'isotopes': {str(k): str(v) for k,v in residuals['isotopes'].items()},
                    'charge': str(residuals['charge']), 'baryon': str(residuals['baryon']),
                    'arithmetic': 'Fraction of decimal representations of supplied floating values; not exact physical rates'}
    upper = np.zeros(21)
    for block in rec.BLOCKS:
        upper[list(block)] = float(np.sum(x[list(block)]))
    result = {'unit': 'REI-GRID044-ENDPOINT-BINDING-01',
              'scope': 'actual saved target, instantaneous frozen prescribed-source photo-only response',
              'input_identity_checked': check_input_identity(), 'species': list(rec.SPECIES),
              'x': x.tolist(), 'reference_density_m3': r,
              'saved_rates_per_source_target': rates.tolist(),
              'rec_output_25': f.tolist(), 'rec_jacobian_25_by_23': jac.tolist(),
              'wu_source_22': assembled.tolist(), 'source_row_scales_22': source_scales.tolist(),
              'wu_coefficient_matrix_21_by_21': matrix.tolist(),
              'physical_species_and_e_fast_source_m3_s': (r*assembled).tolist(),
              'signed_energy_source_eV_per_ref_s': f[22:25].tolist(),
              'signed_energy_source_J_m3_s': (r*EV_TO_J*f[22:25]).tolist(),
              'exact_decimal_representation_conservation': conservation,
              'events_total_13_per_ref_s': total_events.tolist(),
              'thermal_heating_J_m3_s': None, 'thermal_heating_status': 'UNQUALIFIED',
              'new_IVPs': 0, 'new_opacity_integrals': 0, 'historical_test_replays': 0,
              'new83_runs': 0, 'NCP_runs': 0, 'L4_ready': False,
              'global_physical_completion': None,
              'client_box': {'t_s': [0.0,0.0], 'lower': [0.0]*21, 'upper': upper.tolist(),
                             'meaning': 'finite callback envelope; isotope-sum/simplex and complete physical-domain certification separate'}}
    return result, binding, records, event_rows, contributions


def write_endpoint_files(result, binding, records, events, contributions):
    write_json(ROOT/'ACTUAL_STATE_BINDING.json', binding)
    write_json(ROOT/'SPECIES_CATALOG.json', records)
    write_json(ROOT/'SOURCE_ABSORBER_MATRIX.json', {'events': events,
                 'source_contributions': contributions, 'event_count': 13,
                 'additive_source_contribution_count': 26,
                 'owner_rule': 'one physical extent per event; source templates are additive contributions'})
    write_json(ROOT/'HE_RECEIVER_INPUT.json', {
        'status': 'RECEIVER_INPUT_PREPARED', 'electron_pool': 'e_fast',
        'primary_number_m3_s': result['physical_species_and_e_fast_source_m3_s'][21],
        'primary_kinetic_energy_J_m3_s': result['signed_energy_source_J_m3_s'][2],
        'event_contributions': [{'event_id':r['event_id'], 'source':r['source'],
                                'event_rate_m3_s':r['event_rate_m3_s'],
                                'mean_primary_electron_eV':r['CR_generic_event_ledger_eV']['electron_kinetic_ev']}
                               for r in contributions],
        'spectral_measure': None, 'angular_measure': None,
        'mean_energy_interpretation': 'first moments only; not a monoenergetic electron spectrum or an angular law',
        'degradation_status': 'UNQUALIFIED', 'thermal_heating': None,
        'HE101_C8': 'OPEN', 'existing_exhausted_reservation': 'PRESERVED',
        'meaning': 'number and energy moments only; no spectrum or stopping provider invented'})
    write_json(ROOT/'BASS_INPUT_JOIN.json', {
        'status': 'INPUT_REUSED', 'frame': FRAME,
        'endpoint': binding['endpoint'],
        'new_absorption_angular_measure': None,
        'new_absorption_stress_tensor': None,
        'geometry_feedback': 'OPEN',
        'meaning': 'prescribed donor geometry and signed stress retained; no scalar-to-isotropic angular replacement'})
    write_json(ROOT/'VIGILODE_CLIENT_CONTRACT.json', {
        'client': 'actual21_frozen_endpoint_photo_operator',
        'RHS': 'A*x; A assembled from exact reused WU incidence and saved REC Gamma',
        'Jacobian': 'A; full write of all21x21 coefficients',
        'clock': 'local proper seconds with t_star=0 at saved donor proper_elapsed_s',
        'donor_proper_elapsed_s': binding['time']['proper_seconds'],
        'domain': result['client_box'], 'full_physical_domain': 'OPEN',
        'trajectory_error_control': 'OPEN', 'native_norm': 'REUSED_REFERENCE_ONLY',
        'old_D1_D5_suites': 'NOT_REPLAYED',
        'witness': 'caller assertion epoch=1,environment_ok=true; no native FP certification',
        'gateway_sha256': 'c4ae170271fdae67bab2edfddb16ea149bccfc77f60f59e161347cbcfee697ee'})


if __name__ == '__main__':
    data = evaluate_endpoint()
    write_endpoint_files(*data)
    write_json(ROOT/'endpoint_raw.json', data[0])
    print(json.dumps({'outputs':25,'Jacobian':[25,23],'events':13,'source_contributions':26,'new_IVPs':0}))
