#!/usr/bin/env python3
"""Signed second-Volterra correction on immutable captured OFF segments.

The baseline first-variation quadrature is reused at its original N. Only the
causal prefix and signed correction are evaluated at M. Whole-cell rectangle
intervals are intentional; this is not a second-order quadrature claim.
"""
from decimal import Decimal as D
import time

import directed_interval as di
from directed_interval import IV, Jet2, value, response_j
from local_enclosure import Coefficients, SPECIES, lift
import path_enclosure as pe


def fields(c, x):
    """Return r and signed moment kernels; one original coefficient call."""
    E, q, rates = c(x)
    u, remaining = c.h * x, c.h * (1 - x)
    F = (-c.L * remaining).exp()
    K0 = response_j(c.L, remaining)
    KE = E * response_j(c.L + 1, remaining)
    Pf = c.f0 * (-c.L * u).exp() + c.qf * response_j(c.L, u)
    dl = [v - f for v, f in zip(rates, c.lf)]
    dL = sum(dl, Jet2(0) if isinstance(x, Jet2) else IV(0))
    r = q - c.qf - dL * Pf
    out = {'P1': -F * dL, 'Z_eV': -KE * dL,
           'QN': Jet2(0) if isinstance(x, Jet2) else IV(0),
           'QE_eV': Jet2(0) if isinstance(x, Jet2) else IV(0)}
    for i, sp in enumerate(SPECIES):
        out['A_' + sp] = dl[i] - c.lf[i] * K0 * dL
        out['B_' + sp + '_eV'] = E * dl[i] - c.lf[i] * KE * dL
        out['H_' + sp + '_eV'] = ((E - c.chi[i]) * dl[i]
            - c.lf[i] * (KE - c.chi[i] * K0) * dL)
    for p in ('A', 'B', 'H'):
        suffix = '_eV' if p != 'A' else ''
        out[p + '_total' + suffix] = sum((out[p + '_' + sp + suffix] for sp in SPECIES), 0)
    out['P1_energy_eV'] = c.endpoint_E * out['P1']
    return r, out


def prefix_and_correction(c, m, incoming_center):
    """Enclose delta1 prefixes and all integrals k*delta1 in O(M) cells.

    eta is excluded from delta1 and is carried in analytic remainder_bounds.
    x=u/h; a=h*Lambda_f. For each cell [l,b], the forcing integrand
    exp(-a*(b-x))*r(x) has second derivative exp(...)*(r''+2a*r'+a^2*r).
    """
    if not isinstance(m, int) or m <= 0 or m & (m - 1):
        raise ValueError('positive dyadic M required')
    if c.L.lo < 0 or c.h.lo <= 0:
        raise ValueError('nonnegative frozen opacity and positive h required')
    a, dx = c.h * c.L, IV(1) / m
    decay, midpoint_decay = (-a * dx).exp(), (-a * dx / 2).exp()
    span = IV(0, dx.hi)
    decay_span = (-a * span).exp()
    forcing_span = c.h * response_j(a, span)
    prefix = IV(incoming_center)
    corrections, cells = {}, []
    prefix_truncation_sum = IV(0)
    before = c.evaluations
    for j in range(m):
        left, right, mid = IV(j) / m, IV(j + 1) / m, IV(2 * j + 1) / (2 * m)
        cell = IV(left.lo, right.hi)
        rj, kernels = fields(c, Jet2.variable(cell))
        rm, _ = fields(c, mid)
        # The kernel in the variable-length cell prefix is nonnegative.
        # Integral r*kernel belongs to [r_lo,r_hi] times its integral.
        within = decay_span * prefix + forcing_span * rj.v
        contrib = {k: c.h * dx * value(v) * within for k, v in kernels.items()}
        for k, v in contrib.items():
            corrections[k] = corrections.get(k, IV(0)) + v
        kernel_second = decay_span * (rj.d2 + 2 * a * rj.d1 + a.square() * rj.v)
        local_radius = (c.h * dx * dx * dx * abs(kernel_second) / 24).hi
        forcing_midpoint = c.h * dx * midpoint_decay * value(rm)
        next_prefix = decay * prefix + forcing_midpoint + pe.symmetric(local_radius)
        prefix_truncation_sum += IV(local_radius)
        cells.append({'cell': j, 'x_left': left, 'x_right': right,
            'prefix_left': prefix, 'prefix_whole_cell': within,
            'r_whole_cell': rj.v, 'forcing_midpoint_integral': forcing_midpoint,
            'forcing_midpoint_truncation_radius': local_radius,
            'prefix_right': next_prefix,
            'photon_signed_cell_integral': contrib['P1'],
            'heat_total_signed_cell_integral_eV': contrib['H_total_eV']})
        prefix = next_prefix
    return {'method': 'stable_midpoint_prefix_and_signed_whole_cell_rectangles_v1',
        'M_second': m, 'prefix_initial': IV(incoming_center), 'prefix_endpoint': prefix,
        'signed': corrections, 'cells': cells,
        'prefix_local_truncation_radii_sum_upper': prefix_truncation_sum.hi,
        'new_coefficient_evaluations': c.evaluations - before,
        'firstvariation_quadrature_replays': 0,
        'rectangle_cells': m, 'prefix_midpoint_cells': m,
        'incoming_uncertainty_in_prefix': False}


def remainder_bounds(c, bounds, gains, incoming_center, incoming_radius):
    """Finite Volterra remainder, using NEW carry and original valid bounds."""
    if D(incoming_radius) < 0:
        raise ArithmeticError('negative incoming radius')
    # Inherited function selects the established effective/triangle T bounds.
    original = pe.remainder_bounds(c, bounds, gains, incoming_center, incoming_radius)
    S, norm = IV(original['S_upper']), IV(bounds['D_L'].hi)
    if norm.lo < 0:
        raise ArithmeticError('negative whole-segment operator norm bound')
    eta = IV(incoming_radius)
    incoming = {k: (abs(gains[k]) * eta).hi for k in original['T_upper']}
    incoming_coupling = {k: (IV(t) * eta).hi for k, t in original['T_upper'].items()}
    remainder = {k: (IV(t) * norm * S).hi for k, t in original['T_upper'].items()}
    total = {k: (IV(incoming[k]) + IV(incoming_coupling[k]) + IV(remainder[k])).hi for k in incoming}
    return {'S_upper': S.hi, 'D_upper': norm.hi, 'T_upper': original['T_upper'],
        'incoming_upper': incoming, 'incoming_coupling_upper': incoming_coupling,
        'second_volterra_remainder_upper': remainder,
        'total_before_numerical_upper': total,
        'old_firstorder_coupling_upper_for_diagnostic_only': original['nonlinear_upper']}


def segment(control, cached_segment, baseline_n, m, incoming_center, incoming_radius):
    c = Coefficients(control)
    old_local = cached_segment['local']
    if control['key'] != cached_segment['key'] or old_local['cell_coverage']['dyadic_cells'] != baseline_n:
        raise ValueError('cached segment key/resolution mismatch')
    cached_signed = {k: pe.iv(v) for k, v in old_local['signed'].items()}
    bounds = {k: pe.iv(v) for k, v in old_local['bounds'].items()}
    frozen, gains = pe.frozen_outputs_and_gains(c)
    captured = pe.captured_outputs(control, c.chi)
    correction = prefix_and_correction(c, m, incoming_center)
    if set(correction['signed']) != set(cached_signed):
        raise ValueError('second/first variation quantity mismatch')
    first = {k: v + gains[k] * IV(incoming_center) for k, v in cached_signed.items()}
    prefix_box, terminal_box = correction['prefix_endpoint'], first['P1']
    prefix_overlap = max(prefix_box.lo, terminal_box.lo) <= min(prefix_box.hi, terminal_box.hi)
    if not prefix_overlap:
        raise ArithmeticError('independent first-prefix/cached endpoint non-overlap')
    remainder = remainder_bounds(c, bounds, gains, incoming_center, incoming_radius)
    represented = {k: first[k] + correction['signed'][k] + frozen[k] - captured[k] for k in first}
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
    local = {'origin': 'REUSED_BYTE_AND_INPUT_MATCHED_E13C8_BASELINE_FIRST_VARIATION',
        'N_base': baseline_n, 'signed': cached_signed, 'bounds': bounds,
        'midpoint_radius': old_local['midpoint_radius'],
        'firstvariation_quadrature_replays': 0, 'new_coefficient_evaluations': 0}
    return c, {'key': control['key'],
        'incoming': {'center': incoming_center, 'radius': incoming_radius,
            'interval': IV(incoming_center)+pe.symmetric(incoming_radius)},
        'local': local, 'second_correction': correction,
        'new_coefficient_domain': c.domain,
        'frozen': frozen, 'gains': gains, 'captured': captured,
        'firstvariation_with_candidate_incoming': first,
        'prefix_and_cached_endpoint_overlap': prefix_overlap,
        'remainder': remainder, 'outputs': outputs, 'ledger_enclosures': ledgers,
        'endpoint_energy_eV': c.endpoint_E, 'initial_energy_eV': c.e0,
        'native_energy_stock_minus_Eh_n_eV': captured['P1_energy_eV'] - c.endpoint_E*captured['P1'],
        'frozen_Lh': c.L*c.h}


def run_track(controls, cached_track, baseline_n, m, checkpoint):
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
        c, result = segment(control, old, baseline_n, m, incoming_center, incoming_radius)
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
