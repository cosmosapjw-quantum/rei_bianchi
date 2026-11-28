#!/usr/bin/env python3
"""E13C4 local validated enclosures, without any continuous ODE solve.

Coefficients are independently translated from the inherited E13C2 Decimal
definition. The original binary64 constants, captured freezing and masks are
kept. Interval inclusion follows expression composition; Jet2 supplies whole
cell second derivative ranges for validated signed midpoint integration.
"""
import argparse
from decimal import Decimal as D
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import sys
import time

import directed_interval as di
from directed_interval import IV, Jet2, value, response_j

SPECIES = ('HI', 'HeI', 'HeII')
PARAMS = ((.4298, 5.475e4, 32.88, 2.963, 0., 0., 0.),
          (13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
          (1.720, 1.369e4, 32.88, 2.963, 0., 0., 0.))
CHI = (13.598434599702, 24.587389011, 54.41776)
CUTOFF = (13.6, 24.59, 54.42)
KEYS = [('OFF', 1, 0, 0), ('OFF', 1, 1162, 0), ('OFF', 1, 1976, 0),
        ('GM', 2, 1727, 0), ('GM', 2, 2333, 0), ('OFF', 2, 700, 1)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def lift(v):
    return IV.from_binary64(v)


class Coefficients:
    def __init__(self, control):
        self.control = control
        row, stage = control['row'], control['stage']
        self.a, self.h, self.e0, self.f0 = [lift(row[k]) for k in ('a', 'h', 'e0', 'f0')]
        self.s0, self.s1 = [lift(stage[k]) for k in ('s0', 's1')]
        self.old = [lift(stage['old_' + k]) for k in ('x', 'y', 'z')]
        self.new = [lift(stage['new_' + k]) for k in ('x', 'y', 'z')]
        self.mask = [control['mask'][k] for k in SPECIES]
        assert self.mask == [float(row['e_mid']) >= x for x in CUTOFF]
        self.source_on = control['source_on']
        assert self.source_on == (float(row['source_on']) == 1.)
        assert float(row['outn']) == float(row['oute']) == 0.
        self.hubble0, self.omega_r, self.omega_m, self.omega_l = map(lift, (2.2e-18, 9e-5, .3, .69991))
        ob, he, grav, proton = map(lift, (.048, .24, 6.67430e-8, 1.67262192595e-24))
        rho = 3 * self.hubble0.square() / (8 * lift(math.pi) * grav)
        self.nh0 = (1 - he) * ob * rho / proton
        self.nhe0 = he * ob * rho / (4 * proton)
        self.c, self.rate, self.emin, self.emax = map(lift, (2.99792458e10, 1e-15, 13.7, 100.))
        self.params = [list(map(lift, row)) for row in PARAMS]
        self.log_norms = [(p[1].ln() + lift(1e-18).ln()) for p in self.params]
        self.chi = list(map(lift, CHI))
        self.qf = lift(row['q'])
        self.lf = [lift(row['lambda_' + k]) for k in SPECIES]
        self.L = sum(self.lf, IV(0))
        if self.h.lo <= 0 or self.s1.lo <= self.s0.hi or self.f0.lo < 0 or self.qf.lo < 0:
            raise ArithmeticError('invalid captured initial/frozen domain')
        if any(v.lo < 0 for v in self.lf):
            raise ArithmeticError('negative captured opacity')
        if any((not active) and (lam.lo != 0 or lam.hi != 0) for active, lam in zip(self.mask, self.lf)):
            raise ArithmeticError('inactive frozen opacity not exactly zero')
        self.endpoint_E = self.e0 * (-self.h).exp()
        self.evaluations = 0
        self.domain = {'gas_checked_evaluations': 0, 'positive_rate_evaluations': 0,
                       'active_heat_weight_min_eV': None, 'H_min': None,
                       'q_min': None, 'energy_min_eV': None, 'energy_max_eV': None,
                       'theta_min': None, 'theta_max': None}

    def sigma(self, i, energy):
        if not self.mask[i]:
            return Jet2(0) if isinstance(energy, Jet2) else IV(0)
        e0, sigma0, ya, power, yw, y0, y1 = self.params[i]
        x = energy / e0 - y0
        y = (x.square() + y1.square()).sqrt()
        log_sigma = (self.log_norms[i] + ((x - 1).square() + yw.square()).ln()
                     + (power / 2 - IV('5.5')) * y.ln()
                     - power * (1 + (y / ya).sqrt()).ln())
        return log_sigma.exp()

    def _min(self, name, x):
        self.domain[name] = x if self.domain[name] is None else min(self.domain[name], x)

    def _max(self, name, x):
        self.domain[name] = x if self.domain[name] is None else max(self.domain[name], x)

    def __call__(self, t):
        if value(t).lo < 0 or value(t).hi > 1:
            raise ArithmeticError('normalized time outside captured segment')
        du = self.h * t
        s = self.a + du
        energy = self.e0 * (-du).exp()
        theta = (self.a - self.s0 + du) / (self.s1 - self.s0)
        x, y, z = [a + (b - a) * theta for a, b in zip(self.old, self.new)]
        xv, yv, zv = value(x), value(y), value(z)
        if not (xv.lo >= 0 and xv.hi <= 1 and yv.lo >= 0 and zv.lo >= 0 and (yv + zv).hi <= 1):
            raise ArithmeticError('gas positivity domain not enclosed')
        self.domain['gas_checked_evaluations'] += 1
        self._min('theta_min', value(theta).lo); self._max('theta_max', value(theta).hi)
        exp3 = (-3 * s).exp()
        nh, nhe = self.nh0 * exp3, self.nhe0 * exp3
        hubble = self.hubble0 * (self.omega_r * (-4 * s).exp() + self.omega_m * exp3 + self.omega_l).sqrt()
        targets = (nh * (1 - x), nhe * (1 - y - z), nhe * y)
        rates = [self.c * target * self.sigma(i, energy) / hubble for i, target in enumerate(targets)]
        q = self.rate / ((1 / self.emin - 1 / self.emax) * energy * hubble) if self.source_on else (Jet2(0) if isinstance(t, Jet2) else IV(0))
        if value(hubble).lo <= 0 or value(q).lo < 0 or any(value(l).lo < 0 for l in rates):
            raise ArithmeticError('opacity/source/H positivity not enclosed')
        self.domain['positive_rate_evaluations'] += 1
        self._min('H_min', value(hubble).lo); self._min('q_min', value(q).lo)
        self._min('energy_min_eV', value(energy).lo); self._max('energy_max_eV', value(energy).hi)
        for active, chi in zip(self.mask, self.chi):
            if active:
                gap = value(energy) - chi
                if gap.lo < 0:
                    raise ArithmeticError('active heat weight positivity not enclosed')
                self._min('active_heat_weight_min_eV', gap.lo)
        self.evaluations += 1
        return energy, q, rates


def integrands(c, t):
    E, q, lambdas = c(t)
    du, width = c.h * t, c.h * (1 - t)
    W = (-c.L * width).exp()
    K0, KE = response_j(c.L, width), E * response_j(c.L + 1, width)
    Pf = c.f0 * (-c.L * du).exp() + c.qf * response_j(c.L, du)
    dq = q - c.qf
    dl = [l - lf for l, lf in zip(lambdas, c.lf)]
    dL = sum(dl, Jet2(0) if isinstance(t, Jet2) else IV(0))
    r = dq - dL * Pf
    out = {'P1': W * r, 'Z_eV': KE * r, 'QN': dq, 'QE_eV': E * dq}
    kq, weight = [], []
    for i, k in enumerate(SPECIES):
        weight.append(E - c.chi[i])
        kq.append(KE - c.chi[i] * K0)
        out['A_' + k] = dl[i] * Pf + c.lf[i] * K0 * r
        out['B_' + k + '_eV'] = E * dl[i] * Pf + c.lf[i] * KE * r
        out['H_' + k + '_eV'] = weight[i] * dl[i] * Pf + c.lf[i] * kq[i] * r
    out['A_total'] = sum((out['A_' + k] for k in SPECIES), 0)
    out['B_total_eV'] = sum((out['B_' + k + '_eV'] for k in SPECIES), 0)
    # Keep heat weights inside the integrand, before enclosure and summation.
    out['H_total_eV'] = sum((out['H_' + k + '_eV'] for k in SPECIES), 0)
    out['P1_energy_eV'] = c.endpoint_E * out['P1']
    aL, aq, pv, ev = abs(value(dL)), abs(value(dq)), value(Pf), value(E)
    if pv.lo < 0:
        raise ArithmeticError('frozen stock nonnegative enclosure failed')
    k0v, kev, wv = value(K0), value(KE), value(W)
    adl = [abs(value(l)) for l in dl]
    bv = {'D_L': aL, 'B_r': aq + aL * pv, 'H_h': wv * aL,
          'H_0': k0v * aL, 'H_E': kev * aL}
    total_direct_heat, total_kernel_heat = IV(0), IV(0)
    total_triangle_heat = IV(0)
    for i, k in enumerate(SPECIES):
        dv = value(dl[i]); wi = value(weight[i]); ki = value(kq[i])
        bv['V_' + k] = adl[i]; bv['VE_' + k] = ev * adl[i]
        bv['effective_A_' + k] = abs(dv - c.lf[i] * k0v * value(dL))
        bv['effective_B_' + k] = abs(ev * dv - c.lf[i] * kev * value(dL))
        bv['effective_H_' + k] = abs(wi * dv - c.lf[i] * ki * value(dL))
        bv['triangle_A_' + k] = adl[i] + c.lf[i] * k0v * aL
        bv['triangle_B_' + k] = ev * adl[i] + c.lf[i] * kev * aL
        if c.mask[i]:
            # E(u)>=chi for the entire segment implies K_Q>=0 analytically.
            kp = ki.intersect_nonnegative()
            hv = wi * adl[i] + c.lf[i] * kp * aL
        else:
            hv = IV(0)
        bv['triangle_H_' + k] = hv
        total_triangle_heat += hv
        total_direct_heat += wi * dv
        total_kernel_heat += c.lf[i] * ki
    bv['effective_H_total'] = abs(total_direct_heat - total_kernel_heat * value(dL))
    bv['triangle_H_total'] = total_triangle_heat
    bv['effective_B_total'] = abs(ev * value(dL) - c.L * kev * value(dL))
    return out, bv


def saved_point(v):
    return D.from_float(v) if isinstance(v, float) else D(v)


def flatten_saved(data, primary=False):
    if primary:
        out = {'P1': data['delta_P'], 'Z_eV': data['delta_redshift_eV'],
               'QN': data['delta_source_number'], 'QE_eV': data['delta_source_energy_eV'],
               'H_total_eV': data['delta_total_heat_eV']}
        groups = [('A', data['delta_A']), ('B', data['delta_B_eV']), ('H', data['delta_heat_eV'])]
    else:
        out = {k: data[k] for k in ('P1', 'Z_eV', 'QN', 'QE_eV', 'H_total_eV')}
        groups = [('A', data['A']), ('B', data['B_eV']), ('H', data['H_eV'])]
    for prefix, seq in groups:
        for k, v in zip(SPECIES, seq):
            out[prefix + '_' + k + ('_eV' if prefix != 'A' else '')] = v
    return {k: saved_point(v) for k, v in out.items()}


def solve_control(control, n):
    start = time.perf_counter()
    c = Coefficients(control)
    delta = IV(1) / n
    midpoint, radii, bound_integrals, max_d2 = {}, {}, {}, {}
    for j in range(n):
        a, b, m = IV(j) / n, IV(j + 1) / n, IV(2 * j + 1) / (2 * n)
        cell = IV(a.lo, b.hi)
        field, bounds = integrands(c, Jet2.variable(cell))
        center, _ = integrands(c, m)
        for k, jet in field.items():
            m2 = abs(jet.d2).hi
            midpoint[k] = midpoint.get(k, IV(0)) + c.h * delta * value(center[k])
            radii[k] = radii.get(k, IV(0)) + c.h * IV(m2) / (24 * n ** 3)
            max_d2[k] = max(max_d2.get(k, D(0)), m2)
        for k, item in bounds.items():
            bound_integrals[k] = bound_integrals.get(k, IV(0)) + c.h * delta * item
    certified = {k: val + IV(radii[k].hi.copy_negate(), radii[k].hi) for k, val in midpoint.items()}
    S = bound_integrals['B_r']
    trunc = {'P1': (S * bound_integrals['H_h']).hi,
             'Z_eV': (S * bound_integrals['H_E']).hi, 'QN': D(0), 'QE_eV': D(0)}
    alternatives = {}
    for i, k in enumerate(SPECIES):
        for prefix in ('A', 'B', 'H'):
            label = prefix + '_' + k + ('_eV' if prefix != 'A' else '')
            effective = (S * bound_integrals['effective_' + prefix + '_' + k]).hi
            triangle = (S * bound_integrals['triangle_' + prefix + '_' + k]).hi
            trunc[label] = min(effective, triangle)
            alternatives[label] = {'effective': str(effective), 'triangle': str(triangle)}
    trunc['A_total'] = trunc['P1']
    trunc['P1_energy_eV'] = (c.endpoint_E * IV(trunc['P1'])).hi
    trunc['B_total_eV'] = min((S * bound_integrals['effective_B_total']).hi,
                            (IV(trunc['P1_energy_eV']) + IV(trunc['Z_eV'])).hi)
    heff = (S * bound_integrals['effective_H_total']).hi
    htri = (S * bound_integrals['triangle_H_total']).hi
    trunc['H_total_eV'] = min(heff, htri)
    alternatives['H_total_eV'] = {'effective': str(heff), 'triangle': str(htri)}
    compare = {}
    reference = flatten_saved(control['saved_continuous_defect'])
    for name, candidate in [('saved_E13C3_primary_GL12', flatten_saved(control['saved_primary_GL12'], True)),
                            ('saved_E13C3_Decimal_GL20', flatten_saved(control['saved_decimal_firstvariation']))]:
        comparisons = {}
        for k, cand in candidate.items():
            firstvar_err = abs(certified[k] - IV(cand)).hi
            full_bound = (IV(firstvar_err) + IV(trunc[k])).hi
            ref = reference[k]
            observed = abs(IV(cand) - IV(ref))
            floor = D('1e-24') if 'eV' in k else D('1e-25')
            # Every reported ratio uses outward arithmetic too. Floors are
            # display rules, not acceptance tolerances or reference proofs.
            ref_big = ref.copy_abs() >= floor
            gap_big = observed.lo >= floor
            comparisons[k] = {
                'candidate_value': str(cand), 'saved_reference_value': str(ref),
                'candidate_inside_firstvariation_interval': certified[k].contains(cand),
                'certified_candidate_to_exact_firstvariation_upper': str(firstvar_err),
                'certified_truncation_upper': str(trunc[k]),
                'certified_candidate_to_true_defect_upper': str(full_bound),
                'observed_saved_reference_absolute_gap': observed.json(),
                'observed_gap_contained': observed.hi <= full_bound,
                'reference_value_inside_true_defect_interval': (certified[k] + IV(trunc[k].copy_negate(), trunc[k])).contains(ref),
                'full_bound_over_saved_defect_abs_upper': str((IV(full_bound) / IV(ref.copy_abs())).hi) if ref_big else None,
                'truncation_bound_over_observed_gap_upper': str((IV(trunc[k]) / observed).hi) if gap_big else None,
                'relative_defect_status': 'EVALUATED_DIAGNOSTIC' if ref_big else 'UNRESOLVED_BELOW_FLOOR',
                'sharpness_status': 'EVALUATED_DIAGNOSTIC' if gap_big else 'UNRESOLVED_BELOW_FLOOR',
                'reference_is_rigorous_enclosure': False}
        compare[name] = comparisons
    return {'key': control['key'], 'subdivisions': n, 'precision_digits': di.PRECISION,
            'cell_coverage': {'normalized_domain': ['0', '1'], 'equal_dyadic_cells': n,
                              'overlap_gaps': 'none by exact rational partition', 'coefficient_evaluations': c.evaluations,
                              'whole_cell_derivative_evaluations': n, 'midpoint_evaluations': n},
            'domain': {k: str(v) if isinstance(v, D) else v for k, v in c.domain.items()},
            'frozen': {'L': c.L.json(), 'h': c.h.json(), 'Lh': (c.L * c.h).json(),
                       'f0': c.f0.json(), 'qf': c.qf.json(), 'endpoint_E_eV': c.endpoint_E.json(),
                       'mask': c.mask, 'source_on': c.source_on, 'incoming_correction': '0'},
            'variation_integral_enclosures': {k: v.json() for k, v in bound_integrals.items()},
            'frozen_quadrature_midpoint_sum_enclosures': {k: v.json() for k, v in midpoint.items()},
            'validated_midpoint_truncation_radii': {k: str(v.hi) for k, v in radii.items()},
            'max_abs_second_t_derivative': {k: str(v) for k, v in max_d2.items()},
            'exact_firstvariation_integral_enclosures': {k: v.json() for k, v in certified.items()},
            'analytic_truncation_upper': {k: str(v) for k, v in trunc.items()},
            'truncation_alternatives': alternatives,
            'sup_photon_remainder_upper': str((S * bound_integrals['D_L']).hi),
            'saved_candidate_comparison': compare,
            'saved_reference_order_gap': control['saved_reference_order_gap'],
            'reference_order_gap_status': 'NUMERICAL_EVIDENCE_NOT_RIGOROUS_UNCERTAINTY',
            'elapsed_seconds': time.perf_counter() - start}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--subdivisions', type=int, required=True)
    ap.add_argument('--precision', type=int, default=60)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.subdivisions <= 0 or args.subdivisions & (args.subdivisions - 1):
        raise ValueError('subdivisions must be a positive power of two')
    if args.subdivisions > 2048:
        raise ValueError('bounded local implementation max2048; no automatic full-path extension')
    di.configure(args.precision)
    package = args.package.resolve()
    inputs_path = package / 'inputs/SIX_CONTROLS.json'
    data = json.loads(inputs_path.read_text())
    if [tuple(c['key']) for c in data['controls']] != KEYS:
        raise ValueError('six local identities changed')
    source_files = [Path(__file__), Path(di.__file__), package / 'PLAN.json', inputs_path]
    started = datetime.now(timezone.utc).isoformat()
    identity = {'started_utc': started, 'argv': sys.argv,
                'source_sha256_before_run': {str(p.relative_to(package)): sha(p) for p in source_files},
                'python': sys.version, 'platform': platform.platform(),
                'decimal_libmpdec_version': __import__('decimal').__libmpdec_version__,
                'precision_digits': args.precision, 'subdivisions': args.subdivisions,
                'native_runs': 0, 'gas_advances': 0, 'old_continuous_solves': 0}
    atomic_json(args.output.with_name(args.output.stem + '_START.json'), identity)
    started_perf = time.perf_counter()
    rows = []
    for control in data['controls']:
        result = solve_control(control, args.subdivisions)
        rows.append(result)
        atomic_json(args.output.with_name(args.output.stem + '_CHECKPOINT.json'), {'completed_controls': rows, 'identity': identity})
        print(json.dumps({'key': result['key'], 'seconds': result['elapsed_seconds'],
                          'heat_truncation_upper': result['analytic_truncation_upper']['H_total_eV'],
                          'primary_heat_full_bound_ratio': result['saved_candidate_comparison']['saved_E13C3_primary_GL12']['H_total_eV']['full_bound_over_saved_defect_abs_upper']}), flush=True)
    checks = []
    for row in rows:
        for lane, comp in row['saved_candidate_comparison'].items():
            for k, v in comp.items():
                checks.append({'key': row['key'], 'lane': lane, 'observable': k,
                               'compatible': v['observed_gap_contained'] and v['reference_value_inside_true_defect_interval'],
                               'saved_candidate_inside_firstvariation_interval': v['candidate_inside_firstvariation_interval']})
    unchanged = all(sha(package / name) == digest for name, digest in identity['source_sha256_before_run'].items())
    result = {'schema': 'bass-he-e13c4-local-enclosure-v1', 'identity': identity,
              'finished_utc': datetime.now(timezone.utc).isoformat(), 'controls': rows,
              'rounding_operation_counts': di.COUNTS, 'source_unchanged_during_run': unchanged,
              'saved_evidence_compatibility_checks': checks,
              'compatibility_failures': [x for x in checks if not x['compatible']],
              'saved_firstvariation_containment_failures': [x for x in checks if not x['saved_candidate_inside_firstvariation_interval']],
              'elapsed_seconds': time.perf_counter() - started_perf,
              'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'claim_ceiling': 'six inherited local controls; exact realification of captured inputs; rigorous arithmetic/analytic bounds subject to documented Decimal guarantees; no physical production or full-path claim',
              'physical': 'HOLD', 'production': 'HOLD', 'independent_decision': 'PENDING'}
    if not unchanged:
        raise RuntimeError('source changed while running')
    atomic_json(args.output, result)
    return 0 if not result['compatibility_failures'] and not result['saved_firstvariation_containment_failures'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
