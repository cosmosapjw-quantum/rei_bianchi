"""Bounded real-expression diagnostics for the source-bound FLRW remap.

This computes one operator column and free-emission energy moments. It does
not advance a physical gas/photon trajectory or solve any BE root. Every
numerical input is an exact binary64 leaf from the sealed selected record or
the immutable owner source. Arb balls enclose the real expressions, not the
rounding of each native Rust operation.
"""
from pathlib import Path
from decimal import Decimal, Context, ROUND_FLOOR, ROUND_CEILING
import argparse
import hashlib
import json
import platform

import flint
from flint import arb, ctx
import mpmath as mp
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
SELECTED = ROOT / 'inputs/phys02/inputs/SELECTED_SOURCE.json'
SELECTED_SHA = '26a340065a9a99d02903bf0cc008baaf6ade00d2e845beb9d2b0b7d801316494'


def leaf(x):
    a, b = float(x).as_integer_ratio()
    return arb(a) / b


def mp_leaf(x):
    a, b = float(x).as_integer_ratio()
    return mp.mpf(a) / b


def endpoint(v, rounding):
    """Serialize the exact dyadic endpoint and a directed decimal envelope."""
    assert v.is_exact() and v.is_finite()
    m, e = (int(a) for a in v.man_exp())
    numerator = m * (1 << e) if e >= 0 else m
    denominator = 1 if e >= 0 else 1 << (-e)
    value = Context(prec=42, rounding=rounding).divide(
        Decimal(numerator), Decimal(denominator))
    return str(value), {'mantissa': str(m), 'exponent_2': e}


def dump_ball(v):
    assert v.is_finite()
    lo, exact_lo = endpoint(v.lower(), ROUND_FLOOR)
    hi, exact_hi = endpoint(v.upper(), ROUND_CEILING)
    return {'ball': v.str(40), 'lower': lo, 'upper': hi,
            'exact_lower': exact_lo, 'exact_upper': exact_hi,
            'finite': True}


def inside_exact_ball(value, interval):
    def dyadic(d):
        return mp.mpf(d['mantissa']) * mp.power(2, d['exponent_2'])
    return bool(dyadic(interval['exact_lower']) <= value
                <= dyadic(interval['exact_upper']))


def diagnostics():
    ctx.prec = 256
    mp.mp.dps = 110
    payload = SELECTED.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == SELECTED_SHA
    s = json.loads(payload)
    i = 16
    e_left, e_cut = map(leaf, s['energies_ev'][i-1:i+1])
    sigma = leaf(s['sigma_cm2'][i][0])
    hubble, delta = leaf(s['h_mean_per_s']), leaf(s['dt_s'])
    assert s['energies_ev'][i] == 13.60
    assert s['sigma_cm2'][i-1][0] == 0.0
    assert s['h_mean_per_s'] == 1e-14 and s['dt_s'] == 625000000.0
    assert sigma > 0 and hubble > 0 and delta > 0
    macro = 2 * delta
    gap = e_cut - e_left
    r = (-hubble * delta).exp()
    moved_half, moved_full = e_cut * r, e_cut * r*r
    assert e_left < moved_full and moved_full < moved_half and moved_half < e_cut
    w_half = (moved_half - e_left) / gap
    w_full = (moved_full - e_left) / gap
    w_two = w_half*w_half
    k = e_cut/gap
    excess = w_two - w_full
    positive_identity = k*(k-1)*(1-r)*(1-r)
    assert 0 < w_full and w_full < w_two and w_two < w_half and w_half < 1
    assert excess > 0 and (excess-positive_identity).contains(0)
    crossing = (e_cut/e_left).log()/hubble
    assert macro < crossing

    # Under redshift an old lower node cannot return to the higher active node.
    # Both one-step columns preserve number and the transported first energy
    # moment while their active threshold weights differ.
    n_half = (1-w_half) + w_half
    e_half = e_left*(1-w_half) + e_cut*w_half
    e_full = e_left*(1-w_full) + e_cut*w_full
    e_two = r*e_half
    assert (n_half-1).contains(0)
    assert (e_half-moved_half).contains(0)
    assert (e_full-moved_full).contains(0)
    assert (e_two-moved_full).contains(0)

    # Exact symbolic identities are independent of finite-precision arithmetic.
    K, R = sp.symbols('K R')
    symbolic_excess = sp.expand((1-K*(1-R))**2 - (1-K*(1-R**2))
                               - K*(K-1)*(1-R)**2)
    assert symbolic_excess == 0
    E0, E1, W = sp.symbols('E0 E1 W')
    assert sp.expand(E0*(1-W)+E1*W-(E0+(E1-E0)*W)) == 0

    # Free propagation only: compare uniform emission with endpoint schedules.
    # S and birth energy are exact source-code binary64 leaves, not fitted data.
    source, birth_energy = leaf(5e-15), leaf(13.7)
    photons = source*macro
    energy_endpoint = photons*birth_energy
    energy_continuous = source*birth_energy*(1-r*r)/hubble
    energy_twohalf = energy_endpoint*(1+r)/2
    assert energy_continuous < energy_twohalf and energy_twohalf < energy_endpoint
    values = {
        'gap_ev': gap, 'half_redshift_ratio': r,
        'characteristic_energy_half_ev': moved_half,
        'characteristic_energy_full_ev': moved_full,
        'active_weight_one_half': w_half,
        'active_weight_one_full': w_full,
        'active_weight_two_half': w_two,
        'two_half_minus_full_active_weight': excess,
        'positive_factorized_weight_defect': positive_identity,
        'effective_sigma_one_half_cm2': sigma*w_half,
        'effective_sigma_one_full_cm2': sigma*w_full,
        'effective_sigma_two_half_cm2': sigma*w_two,
        'two_half_minus_full_effective_sigma_cm2': sigma*excess,
        'time_to_inactive_left_node_s': crossing,
        'photons_born_per_h': photons,
        'free_energy_continuous_ev_per_h': energy_continuous,
        'free_energy_one_endpoint_ev_per_h': energy_endpoint,
        'free_energy_two_endpoint_ev_per_h': energy_twohalf,
        'endpoint_relative_energy_excess': energy_endpoint/energy_continuous-1,
        'two_endpoint_relative_energy_excess': energy_twohalf/energy_continuous-1,
    }
    balls = {name: dump_ball(v) for name, v in values.items()}
    # Independent high-precision scalar arithmetic, without using Arb results.
    ml, mc = map(mp_leaf, s['energies_ev'][i-1:i+1])
    mh, md = mp_leaf(s['h_mean_per_s']), mp_leaf(s['dt_s'])
    ms = mp_leaf(s['sigma_cm2'][i][0])
    mr = mp.exp(-mh*md)
    mwh, mwf = (mc*mr-ml)/(mc-ml), (mc*mr**2-ml)/(mc-ml)
    checks = {
        'half_redshift_ratio': mr,
        'active_weight_one_half': mwh,
        'active_weight_one_full': mwf,
        'active_weight_two_half': mwh**2,
        'two_half_minus_full_active_weight': mwh**2-mwf,
        'two_half_minus_full_effective_sigma_cm2': ms*(mwh**2-mwf),
        'time_to_inactive_left_node_s': mp.log(mc/ml)/mh,
        'free_energy_continuous_ev_per_h':
            mp_leaf(5e-15)*mp_leaf(13.7)*(1-mr**2)/mh,
        'free_energy_two_endpoint_ev_per_h':
            mp_leaf(5e-15)*2*md*mp_leaf(13.7)*(1+mr)/2,
    }
    mp_checks = {name: {'value': mp.nstr(v,90),
                        'inside_exact_arb_endpoints': inside_exact_ball(v,balls[name])}
                 for name,v in checks.items()}
    assert all(v['inside_exact_arb_endpoints'] for v in mp_checks.values())
    return {
        'schema': 'HH-PHYS03-CHRONOLOGY-1',
        'scope': 'source-bound remap operator column and free-emission moments only',
        'arithmetic': 'Arb 256-bit real expressions over exact binary64 leaves',
        'native_operation_rounding_certificate': False,
        'selected_input_sha256': SELECTED_SHA,
        'owner_commit': '569b04cd71e45756e0fd476aef6643bd9434f4fa',
        'source_binding_file': 'inputs/source_survey/SOURCE_LINE_BINDINGS.json',
        'record': {'member': 1, 'scheme': 'FLRW half1 preBE',
                   't0_s': 160000000000, 't1_s': s['time_s'],
                   'half_step_s': s['dt_s'], 'full_step_s': 2*s['dt_s'],
                   'diagnostic_input': 'one unit basis packet at fixed node index 16',
                   'basis_packet_is_actual_history': False,
                   'provider_cutoff_ev': 13.60,
                   'atomic_binding_energy_ev': 13.598434599702,
                   'left_node_ev': s['energies_ev'][i-1],
                   'threshold_node_ev': s['energies_ev'][i],
                   'threshold_node_sigma_cm2': s['sigma_cm2'][i][0]},
        'results': balls,
        'characteristic_provider_sigma_after_half_and_full': 0,
        'exact_identities': {'non_semigroup_positive_factorization': str(symbolic_excess),
                             'number_and_first_energy_moment_preserved_interior': True},
        'independent_mpmath_110_dps': mp_checks,
        'proof_status': {
            'cell_membership_strict_arb': True,
            'active_weight_order_strict_arb': True,
            'energy_schedule_order_strict_arb': True,
            'provider_relative_opacity_leakage': True,
            'actual_gas_error_or_mixed_sign_bound': False,
            'true_atomic_cross_section_claim': False,
            'trajectory_steps': 0, 'native_dispatches': 0, 'nonlinear_be_solves': 0},
        'environment': {'python': platform.python_version(),
                        'python_flint': flint.__version__, 'sympy': sp.__version__,
                        'mpmath': mp.__version__}}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', type=Path,
                        default=ROOT/'results/CHRONOLOGY_256.json')
    args=parser.parse_args()
    result=diagnostics()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as out:
        json.dump(result,out,ensure_ascii=False,indent=2)
        out.write('\n')
    print(json.dumps({'status':'PASS','output':str(args.output),
                      'independent_checks':len(result['independent_mpmath_110_dps']),
                      'active_weight_one_full':result['results']['active_weight_one_full'],
                      'active_weight_two_half':result['results']['active_weight_two_half']},
                     ensure_ascii=False))


if __name__=='__main__':
    main()
