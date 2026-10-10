#!/usr/bin/env python3
"""PHYS23 spectral response: independent log-energy finite differences.

Only Python's standard library is required. Source f64 literals are interpreted
as exact real inputs to continuum formulas, not as native round-at-every-step
arithmetic. PHYS22 numerical J_np is read as a closed input; no old code imports
or old main/suite execution. The new check differentiates the original fit
directly with 9-point stencils and one Richardson extrapolation.
"""
from __future__ import annotations

import argparse
from decimal import Decimal as D, getcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import platform
import sys

getcontext().prec = 110
ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'inputs/PHYS22_INITIAL_COEFFICIENTS.json'
CONTRACT = ROOT / 'PHYSICS_CONTRACT.json'
INPUT_SHA = '6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79'
CONTRACT_SHA = '888eb11c8a53f828b0ed5d3a053d91dc4da671d727e49c519cb3110bb5b6d200'


def b(value):
    return D.from_float(float(value))


ZERO = D(0)
ONE = D(1)
C = b('29979245800')
NH = b('1e-4')
XH = b('0.9')
FHE = b('0.083')
H1 = b('0.3')
H2 = b('0.6')
TSTAR = b('50000')
KB = b('1.380649e-16')
EV = b('1.602176634e-12')
N0 = b('0.05')
SH = (b('1.01e-14') - b('0.99e-14')) / 2
Q = 2 * SH**2
ANCHOR_E = b('13.7')
CHI = b('13.598434599702')
CUT_HI = b('13.60')
CUT_HEI = b('24.59')
E0 = b('0.4298')
YA = b('32.88')
P = b('2.963')
SIG0 = b('5.475e4')
CM2 = b('1e-18')
PI = 1 + FHE + XH + FHE * (H1 + 2 * H2)
AT = 2 * EV / (3 * KB)
ETH = 3 * KB * TSTAR / (2 * EV)
KAPPA = C * NH * (1 - XH)
COMMON = Q * N0 * KAPPA / 45
FD_H = D('1e-5')
FD_TOL = D('1e-42')
ANCHOR_TOL = D('1e-70')
ALGEBRA_TOL = D('1e-95')
ROOT_WIDTH = D('1e-20')
CHECKS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(name, actual, expected, tol, scale=None):
    if scale is None:
        scale = max(abs(actual), abs(expected))
    error = abs(actual - expected) / scale if scale else abs(actual - expected)
    row = {'name': name, 'actual': actual, 'expected': expected,
           'scaled_error': error, 'tolerance': tol, 'pass': error <= tol}
    CHECKS.append(row)
    return row


def condition(name, passed, **evidence):
    CHECKS.append({'name': name, 'pass': bool(passed), **evidence})


def power(x, p):
    return (p * x.ln()).exp()


def sigma_original(e):
    """Original source formula specialized to the analytic open HI-only band."""
    if not CUT_HI < e < CUT_HEI:
        raise ValueError('derivative stencil must stay strictly within HI-only band')
    x = e / E0
    return SIG0 * (x - 1)**2 * power(x, P / 2 - b('5.5')) * power(
        1 + (x / YA).sqrt(), -P) * CM2


def analytic(e):
    """Analytic comparison expression; independent of the FD stencils."""
    s = sigma_original(e)
    x = e / E0
    v = (x / YA).sqrt()
    alpha = 2 * x / (x - 1) + P / 2 - b('5.5') - P * v / (2 * (1 + v))
    d_alpha = -2 * x / (x - 1)**2 - P * v / (4 * (1 + v)**2)
    zeta = alpha * (alpha + 3) + d_alpha
    cs = s * zeta
    ch = (e - CHI) * cs + e * s * (2 * alpha + 4)
    ct = ch - ETH * cs
    return {'sigma_cm2': s, 'alpha': alpha, 'D_alpha': d_alpha,
            'C_sigma_over_sigma': zeta, 'C_sigma_cm2': cs,
            'C_sigma_heat_eV_cm2': ch, 'C_sigma_thermal_eV_cm2': ct,
            'signed_curvature_ratio_eV': ch / cs}


# Exact, eighth-order centered first/second derivative stencils in z=log E.
OFFSETS = list(range(-4, 5))
W1 = [F(1, 280), F(-4, 105), F(1, 5), F(-4, 5), F(0),
      F(4, 5), F(-1, 5), F(4, 105), F(-1, 280)]
W2 = [F(-1, 560), F(8, 315), F(-1, 5), F(8, 5), F(-205, 72),
      F(8, 5), F(-1, 5), F(8, 315), F(-1, 560)]


def dec_fraction(f):
    return D(f.numerator) / D(f.denominator)


def stencil(e, h):
    # All three observables use the original cross section at shifted energies.
    values = []
    for j in OFFSETS:
        ej = e * (D(j) * h).exp()
        sj = sigma_original(ej)
        values.append([sj, sj * (ej - CHI), sj * (ej - CHI - ETH)])
    cvals = []
    for k in range(3):
        first = sum((dec_fraction(w) * y[k] for w, y in zip(W1, values)), ZERO) / h
        second = sum((dec_fraction(w) * y[k] for w, y in zip(W2, values)), ZERO) / h**2
        cvals.append(second + 3 * first)
    return cvals


def fd_curvatures(e):
    coarse = stencil(e, FD_H)
    fine = stencil(e, FD_H / 2)
    extrap = [(256 * f - c) / 255 for c, f in zip(coarse, fine)]
    return {'coarse': coarse, 'fine': fine, 'richardson': extrap}


def response(e, jac):
    spec = analytic(e)
    ax = COMMON * spec['C_sigma_cm2']
    aw = COMMON * spec['C_sigma_heat_eV_cm2']
    tt = COMMON * AT / PI * spec['C_sigma_thermal_eV_cm2']
    he2 = (jac[1][0] * ax + jac[1][3] * aw) / 4
    he3 = (jac[2][0] * ax + jac[2][3] * aw) / 4
    return {'energy_eV': e, **spec,
            'HII_t3_s-3': ax, 'w_t3_eV_H-1_s-3': aw,
            'T_t3_K_s-3': tt, 'HeII_t4_s-4': he2, 'HeIII_t4_s-4': he3,
            'T_t3_thermal_part_K_s-3': AT / PI * aw,
            'T_t3_particle_part_K_s-3': -TSTAR / PI * ax}


def checked_response(label, e, jac):
    ans = response(e, jac)
    fd = fd_curvatures(e)
    for name, idx in [('C_sigma_cm2', 0), ('C_sigma_heat_eV_cm2', 1),
                      ('C_sigma_thermal_eV_cm2', 2)]:
        close(label + '__' + name, fd['richardson'][idx], ans[name], FD_TOL)
    close(label + '__temperature_particle_identity', ans['T_t3_K_s-3'],
          ans['T_t3_thermal_part_K_s-3'] + ans['T_t3_particle_part_K_s-3'], ALGEBRA_TOL)
    ans['direct_log_energy_FD'] = fd
    return ans


COEFF_KEYS = ['HII_t3_s-3', 'w_t3_eV_H-1_s-3', 'T_t3_K_s-3',
              'HeII_t4_s-4', 'HeIII_t4_s-4']


def mixture(number_weights, energies, jac):
    assert len(number_weights) == len(energies)
    nsum = sum(number_weights, ZERO)
    energy = sum((n * e for n, e in zip(number_weights, energies)), ZERO)
    responses = [response(e, jac) for e in energies]
    vals = {key: sum((n / N0 * r[key] for n, r in zip(number_weights, responses)), ZERO)
            for key in COEFF_KEYS}
    return {'energies_eV': energies, 'photon_number_weights_per_H': number_weights,
            'total_photon_number_per_H': nsum, 'total_energy_eV_per_H': energy,
            'mean_energy_eV': energy / nsum, **vals}


def comparison(mix, jac):
    mono = mixture([mix['total_photon_number_per_H']], [mix['mean_energy_eV']], jac)
    return {'mixture': mix, 'same_N_and_U_mean_energy_monoenergetic': mono,
            'mixture_over_mono_minus_one': {key: mix[key] / mono[key] - 1 for key in COEFF_KEYS}}


def jsonable(value):
    if isinstance(value, D):
        return str(value)
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('refusing to overwrite prior evidence: ' + str(args.output))
    if sha(INPUT) != INPUT_SHA or sha(CONTRACT) != CONTRACT_SHA:
        raise ValueError('closed input or contract identity mismatch')
    old = json.loads(INPUT.read_text())['results']
    jac = [[D(x) for x in row] for row in old['baseline_local']['J_nonphoto']]
    # One finite exact stencil-moment validation; no scientific old-suite replay.
    moment_checks = []
    for order, weights in [(1, W1), (2, W2)]:
        for degree in range(9):
            moment = sum((w * F(j)**degree for w, j in zip(weights, OFFSETS)), F(0))
            expected = F(1 if order == 1 else 2) if degree == order else F(0)
            moment_checks.append(moment == expected)
    condition('new_stencil_exact_moments_degrees_0_to_8', all(moment_checks),
              count=len(moment_checks))

    energies = [('13.61', D('13.61')), ('13.7_f64_anchor', ANCHOR_E),
                ('14', D(14)), ('16', D(16)), ('18', D(18)), ('20', D(20)),
                ('22', D(22)), ('24', D(24)), ('24.58', D('24.58'))]
    rows = [checked_response(label, e, jac) for label, e in energies]
    anchor = rows[1]
    old_actual = old['actual_shear_time_coefficients']
    for key, val in [('HII_t3_s-3', old_actual['state_t3'][0]),
                     ('w_t3_eV_H-1_s-3', old_actual['state_t3'][3]),
                     ('T_t3_K_s-3', old_actual['temperature_t3_K_s3']),
                     ('HeII_t4_s-4', old_actual['state_t4'][1]),
                     ('HeIII_t4_s-4', old_actual['state_t4'][2])]:
        close('single_PHYS22_anchor__' + key, anchor[key], D(val), ANCHOR_TOL)

    # Find only brackets suggested by the declared finite representative set.
    brackets = [(left['energy_eV'], right['energy_eV'])
                for left, right in zip(rows[:-1], rows[1:])
                if left['HeIII_t4_s-4'] * right['HeIII_t4_s-4'] < 0]
    roots = []
    for initial_left, initial_right in brackets:
        left, right = initial_left, initial_right
        fl = response(left, jac)['HeIII_t4_s-4']
        fr = response(right, jac)['HeIII_t4_s-4']
        niter = 0
        while right - left > ROOT_WIDTH:
            midpoint = (left + right) / 2
            fm = response(midpoint, jac)['HeIII_t4_s-4']
            if fm == 0:
                raise ArithmeticError('exact computed midpoint zero; preserve and revise bracket rule')
            if fl * fm < 0:
                right, fr = midpoint, fm
            else:
                left, fl = midpoint, fm
            niter += 1
            if niter > 100:
                raise ArithmeticError('bisection iteration ceiling exceeded')
        mid = (left + right) / 2
        rm = response(mid, jac)
        root = {'initial_bracket_eV': [initial_left, initial_right],
                'final_bracket_eV': [left, right], 'width_eV': right - left,
                'midpoint_eV': mid, 'endpoint_HeIII_t4_s-4': [fl, fr],
                'midpoint_HeIII_t4_s-4': rm['HeIII_t4_s-4'], 'iterations': niter,
                'claim_level': 'numerical bracket conditional on inherited numerical J_np; not a rigorous interval proof'}
        condition('HeIII_numerical_bracket_endpoint_signs', fl * fr < 0 and right - left <= ROOT_WIDTH,
                  bracket=root['final_bracket_eV'], width_eV=right-left)
        for side, ee, ff in [('left', left, fl), ('right', right, fr)]:
            curv = fd_curvatures(ee)['richardson']
            hefd = COMMON / 4 * (jac[2][0] * curv[0] + jac[2][3] * curv[1])
            natural = abs(COMMON / 4 * jac[2][0] * curv[0]) + abs(COMMON / 4 * jac[2][3] * curv[1])
            close('HeIII_bracket_direct_FD_' + side, hefd, ff, FD_TOL, natural)
            condition('HeIII_bracket_FD_sign_' + side, hefd * ff > 0,
                      direct_FD=hefd, analytic=ff)
        roots.append(root)

    equal_number = comparison(mixture([N0/2, N0/2], [D(14), D(24)], jac), jac)
    equal_number['normalization'] = 'N0 fixed, equal photon numbers at 14 and 24 eV; same N and U as mono 19 eV'
    _ = checked_response('mean_energy_19', D(19), jac)
    close('equal_number_mixture_N', equal_number['mixture']['total_photon_number_per_H'], N0, ALGEBRA_TOL)
    close('equal_number_mixture_mean', equal_number['mixture']['mean_energy_eV'], D(19), ALGEBRA_TOL)
    for key in COEFF_KEYS:
        expected = (response(D(14), jac)[key] + response(D(24), jac)[key]) / 2
        close('mixture_linearity__' + key, equal_number['mixture'][key], expected, ALGEBRA_TOL)

    # Fixed energy and equal energy fractions are a distinct measure convention.
    uref = N0 * ANCHOR_E
    equal_energy = comparison(mixture([uref/(2*D(14)), uref/(2*D(24))], [D(14), D(24)], jac), jac)
    equal_energy['normalization'] = 'fixed U=N0*13.7_f64 eV/H, half of U at each line; number weights unequal'
    close('equal_energy_total_U', equal_energy['mixture']['total_energy_eV_per_H'], uref, ALGEBRA_TOL)

    counterexample = None
    # A bounded constructive example, if the two-line and mean-energy zero
    # fractions differ. It does not search over a large family or integrate gas.
    if len(roots) == 1 and D(14) < roots[0]['midpoint_eV'] < D(24):
        g14 = response(D(14), jac)['HeIII_t4_s-4']
        g24 = response(D(24), jac)['HeIII_t4_s-4']
        p_mix_zero = -g24 / (g14 - g24)
        p_mono_zero = (D(24) - roots[0]['midpoint_eV']) / 10
        p_example = (p_mix_zero + p_mono_zero) / 2
        if not ZERO < p_example < ONE:
            raise ArithmeticError('constructed positive-mixture fraction lies outside (0,1)')
        counterexample = comparison(mixture([N0*p_example, N0*(1-p_example)], [D(14), D(24)], jac), jac)
        counterexample['construction'] = {'p_14_zero_of_mixture_HeIII': p_mix_zero,
                                         'p_14_zero_of_mean_energy_mono_HeIII': p_mono_zero,
                                         'p_14_example_midpoint': p_example,
                                         'normalization': 'fixed N0 and matched total energy U for mixture and mono'}
        checked_response('counterexample_mean', counterexample['mixture']['mean_energy_eV'], jac)
        condition('same_mean_spectrum_can_reverse_HeIII_sign',
                  counterexample['mixture']['HeIII_t4_s-4'] * counterexample['same_N_and_U_mean_energy_monoenergetic']['HeIII_t4_s-4'] < 0)
        condition('counterexample_H_and_T_remain_negative',
                  all(obj[key] < 0 for obj in [counterexample['mixture'], counterexample['same_N_and_U_mean_energy_monoenergetic']]
                      for key in ['HII_t3_s-3', 'T_t3_K_s-3']))

    result = {
        'task': 'REI-PHYS23', 'contribution': 'independent finite-difference spectral numerics',
        'evidence_state': ['numerically checked', 'implementation-verified'],
        'contract_sha256': CONTRACT_SHA, 'inherited_PHYS22_JSON_sha256': INPUT_SHA,
        'script_sha256': sha(Path(__file__)), 'python': platform.python_version(),
        'decimal_precision': getcontext().prec,
        'arithmetic': 'exact-real binary64 source constants; diagnostic energies exact decimals except 13.7 f64 anchor; inherited J_np serialized Decimal80 numerical input',
        'coefficient_convention': '[epsilon^2] coefficient with physical q=2 shear^2 included; no extra time factorial',
        'operator': 'C=D^2+3D, D=d/d(log E), gas T and state held fixed',
        'constants': {'c_cm_s': C, 'kB_erg_K': KB, 'eV_erg': EV, 'nH_cm-3': NH,
                      'N0_per_H': N0, 'shear_s-1': SH, 'q_s-2': Q, 'Pi': PI,
                      'Tstar_K': TSTAR, 'e_th_eV': ETH, 'HI_chi_eV': CHI,
                      'HI_cutoff_eV': CUT_HI, 'HeI_cutoff_eV': CUT_HEI},
        'inherited_Jnp_HeII_row': jac[1], 'inherited_Jnp_HeIII_row': jac[2],
        'HeIII_signed_ratio_critical_eV': -jac[2][0] / jac[2][3],
        'finite_difference': {'coordinate': 'z=log(E/evaluation_energy)',
                              'offsets': OFFSETS, 'order': 8, 'coarse_h': FD_H,
                              'fine_h': FD_H/2, 'Richardson_factor': 256,
                              'relative_or_natural_scale_tolerance': FD_TOL,
                              'status': 'high-precision numerical comparison; not a rigorous derivative-error enclosure'},
        'representative_samples': rows,
        'finite_sample_sign_observation': 'HII, w, T, HeII negative at the declared sample set; no root-absence or uniqueness certificate is claimed here',
        'HeIII_numerical_roots': roots,
        'equal_number_two_line_vs_mean': equal_number,
        'equal_energy_two_line_vs_mean': equal_energy,
        'same_mean_HeIII_sign_counterexample': counterexample,
        'checks': CHECKS,
        'summary': {'passed': sum(row['pass'] for row in CHECKS), 'total': len(CHECKS),
                    'failures': sum(not row['pass'] for row in CHECKS)},
        'native_runs': 0, 'gas_IVP_runs': 0, 'old_suite_or_main_replays': 0,
        'source_changes': 0, 'physical_admission': 'HOLD',
        'limits': ['No finite-time gas history or Taylor remainder bound',
                   'No threshold-crossing differentiation',
                   'HeIII root conditional on inherited numerical Jnp, not a rigorous exact-data certificate',
                   'Signed curvature ratio is not heat deposited per absorption event']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(jsonable(result), indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'output': str(args.output), **result['summary']}))
    return int(result['summary']['failures'] != 0)


if __name__ == '__main__':
    sys.exit(main())
