#!/usr/bin/env python3
"""E13C10 first-integral replacement with unchanged E13C9 Volterra method.

Segment/output assembly and path stitching are copied from the pinned E13C9
source; only the first integral and its provenance are changed. The original
signed_volterra prefix and finite remainder functions are imported unchanged.
"""
from decimal import Decimal as D
import time
import directed_interval as di
from directed_interval import IV
from local_enclosure import Coefficients, SPECIES, lift
import path_enclosure as pe
import signed_volterra as sv
from first_midpoint import integrate_signed


def segment(control, cached_segment, baseline_n, n, m, incoming_center, incoming_radius):
    c = Coefficients(control)
    old_local = cached_segment['local']
    if control['key'] != cached_segment['key'] or old_local['cell_coverage']['dyadic_cells'] != baseline_n:
        raise ValueError('cached segment key/resolution mismatch')
    cached_midpoint = None
    if n == baseline_n:
        cached_midpoint = {k:pe.iv(v) for k,v in old_local['midpoint'].items()}
    local = integrate_signed(c, n, cached_midpoint=cached_midpoint)
    signed = local['signed']
    bounds = {k: pe.iv(v) for k, v in old_local['bounds'].items()}
    frozen, gains = pe.frozen_outputs_and_gains(c)
    captured = pe.captured_outputs(control, c.chi)
    correction = sv.prefix_and_correction(c, m, incoming_center)
    if set(correction['signed']) != set(signed):
        raise ValueError('second/first variation quantity mismatch')
    first = {k: v + gains[k] * IV(incoming_center) for k, v in signed.items()}
    prefix_box, terminal_box = correction['prefix_endpoint'], first['P1']
    prefix_overlap = max(prefix_box.lo, terminal_box.lo) <= min(prefix_box.hi, terminal_box.hi)
    if not prefix_overlap:
        raise ArithmeticError('prefix/new first-integral endpoint non-overlap')
    remainder = sv.remainder_bounds(c, bounds, gains, incoming_center, incoming_radius)
    # Preserve the inherited cancellation grouping. Source second corrections
    # remain exactly zero; their NEW first-integral enclosures can differ.
    representation = {k: frozen[k] - captured[k] for k in first}
    represented = {k: first[k] + correction['signed'][k] + representation[k] for k in first}
    outputs = {}
    for k, v in represented.items():
        center = pe.center(v)
        numerical = pe.radius_about(v, center)
        radius = (IV(numerical) + IV(remainder['total_before_numerical_upper'][k])).hi
        corr = IV(center) + pe.symmetric(radius)
        outputs[k] = {'candidate': center, 'radius': radius,
            'numerical_and_representation_radius': numerical,
            'centered_secondvariation_plus_representation_interval': v,
            'true_minus_captured_interval': corr,
            'true_absolute_interval': captured[k] + corr}
    second = correction['signed']
    ledgers = {
        'frozen_number': frozen['P1'] - c.f0 + frozen['A_total'] - frozen['QN'],
        'frozen_energy_eV': frozen['P1_energy_eV'] - c.e0*c.f0 + frozen['B_total_eV'] + frozen['Z_eV'] - frozen['QE_eV'],
        'firstvariation_number': first['P1'] - IV(incoming_center) + first['A_total'] - first['QN'],
        'firstvariation_energy_eV': first['P1_energy_eV'] - c.e0*IV(incoming_center) + first['B_total_eV'] + first['Z_eV'] - first['QE_eV'],
        'secondvariation_number': second['P1'] + second['A_total'],
        'secondvariation_energy_eV': second['P1_energy_eV'] + second['B_total_eV'] + second['Z_eV']}
    for i, sp in enumerate(SPECIES):
        for name, seq in [('firstvariation', first), ('secondvariation', second)]:
            ledgers[name + '_heat_' + sp] = seq['H_'+sp+'_eV'] - seq['B_'+sp+'_eV'] + c.chi[i]*seq['A_'+sp]
    if any(not v.contains(D(0)) for v in ledgers.values()):
        raise ArithmeticError('segment ledger does not contain zero')
    local['bounds'] = bounds
    local['bounds_origin'] = 'REUSED_BYTE_AND_INPUT_MATCHED_FINE_GRID_E13C7'
    local['N_bounds'] = baseline_n
    local['old_first_midpoint_radius_for_diagnostic_only'] = old_local['midpoint_radius']
    return c, {'key': control['key'],
        'incoming': {'center': incoming_center, 'radius': incoming_radius,
            'interval': IV(incoming_center)+pe.symmetric(incoming_radius)},
        'local': local, 'second_correction': correction,
        'new_coefficient_domain': c.domain,
        'frozen': frozen, 'gains': gains, 'captured': captured,
        'firstvariation_with_candidate_incoming': first,
        'prefix_and_new_first_endpoint_overlap': prefix_overlap,
        'remainder': remainder, 'outputs': outputs, 'ledger_enclosures': ledgers,
        'endpoint_energy_eV': c.endpoint_E, 'initial_energy_eV': c.e0,
        'native_energy_stock_minus_Eh_n_eV': captured['P1_energy_eV'] - c.endpoint_E*captured['P1'],
        'frozen_Lh': c.L*c.h}


def run_track(controls, cached_track, baseline_n, n, m, checkpoint):
    """Use inherited exact captured stitch and signed seam without alteration."""
    start = time.perf_counter()
    incoming_center, incoming_radius = D(0), D(0)
    if [c['key'] for c in controls] != [s['key'] for s in cached_track['segments']]:
        raise ValueError('cached ordered segment identity mismatch')
    rows, seams = [], []
    cumulative = {k: {'candidate': D(0), 'radius': D(0), 'interval': IV(0)} for k in pe.MOMENTS}
    captured_sum = {k: IV(0) for k in pe.MOMENTS}
    anchor_sum = IV(0)
    initial_P, initial_E = lift(controls[0]['row']['f0']), lift(controls[0]['row']['e0'])
    for j, (control, old) in enumerate(zip(controls, cached_track['segments'])):
        c, result = segment(control, old, baseline_n, n, m, incoming_center, incoming_radius)
        for k in pe.MOMENTS:
            cumulative[k] = pe.accumulate(cumulative[k], result['outputs'][k])
            captured_sum[k] += result['captured'][k]
        result['cumulative_moment_corrections'] = {k: dict(v) for k, v in cumulative.items()}
        result['cumulative_captured_moments'] = dict(captured_sum)
        rows.append(result)
        if j+1 < len(controls):
            join, incoming_center, incoming_radius = pe.seam(control, controls[j+1], result)
            seams.append(join)
            anchor_sum += join['true_anchor_eV']
        checkpoint(rows, seams)
    moments = {k: captured_sum[k] + cumulative[k]['interval'] for k in pe.MOMENTS}
    final = rows[-1]['outputs']
    ledgers = {
        'number': final['P1']['true_absolute_interval']-initial_P+moments['A_total']-moments['QN'],
        'energy_eV_with_anchor_subtracted': final['P1_energy_eV']['true_absolute_interval']-initial_E*initial_P+moments['B_total_eV']+moments['Z_eV']-moments['QE_eV']-anchor_sum}
    for i, sp in enumerate(SPECIES):
        ledgers['heat_'+sp] = moments['H_'+sp+'_eV']-moments['B_'+sp+'_eV']+c.chi[i]*moments['A_'+sp]
    if any(not v.contains(D(0)) for v in ledgers.values()):
        raise ArithmeticError('stitched number/energy/heat ledger does not contain zero')
    return {'track': {'mode':'OFF','node':controls[0]['key'][2]}, 'segments':rows,'seams':seams,
        'final_photon':final['P1'],'final_energy_stock_eV':final['P1_energy_eV'],
        'cumulative_moment_corrections':cumulative,'cumulative_captured_moments':captured_sum,
        'true_moment_enclosures':moments,'summed_true_anchor_eV':anchor_sum,
        'global_ledger_enclosures':ledgers,'elapsed_seconds':time.perf_counter()-start}
