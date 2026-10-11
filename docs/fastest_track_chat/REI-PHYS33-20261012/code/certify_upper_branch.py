#!/usr/bin/env python3
"""PHYS33 fixed-source upper-branch finite-width certificate.

Exactly one first run and one restored-path replay are owned by the frozen
protocol. No old scientific module, numerical quadrature, trajectory, root
iteration, or physical-parameter sweep is used.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
from fractions import Fraction as Q
import hashlib
import json
from math import comb, factorial
import os
from pathlib import Path
import platform
import resource
import time
import traceback

from outward_decimal import Arithmetic, Interval, EnergyJet
from rational_kernel import (build_kernel_representations,
    bernstein_coefficients, polynomial_value, derivative_numerator,
    polynomial_derivative, polynomial_multiply, polynomial_add)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumpable(value):
    if isinstance(value, Interval):
        return value.as_json()
    if isinstance(value, (Decimal, Q)):
        return str(value)
    if isinstance(value, dict):
        return {str(k): dumpable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [dumpable(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', choices=('first', 'replay'), required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--ledger', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    contract = json.loads((root/'PHYSICS_CONTRACT.json').read_text())
    protocol = json.loads((root/'EXECUTION_PROTOCOL.json').read_text())
    frozen = json.loads((root/'evidence/PREEXECUTION_FREEZE.json').read_text())
    for path, expected in frozen['sha256'].items():
        if sha(root/path) != expected:
            raise RuntimeError('PREEXECUTION_IDENTITY_MISMATCH: '+path)
    ledger = Path(args.ledger)
    ledger.mkdir(parents=True, exist_ok=True)
    marker = ledger/(args.role+'.started.json')
    if args.role == 'replay' and not (ledger/'first.finished.json').exists():
        raise RuntimeError('Replay requires a completed first receipt')
    fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump({'role': args.role, 'source_hash': frozen['sha256'],
                   'root': str(root), 'started_ns': time.time_ns()}, f, indent=2)
    resource.setrlimit(resource.RLIMIT_CPU, (40, 41))
    resource.setrlimit(resource.RLIMIT_AS, (384*1024**2, 384*1024**2))
    wall0, cpu0 = time.monotonic(), time.process_time()
    counts = {'main_this_process': 1, 'bernstein_boxes': 0,
        'transcendental_prefactor_boxes': 0, 'independent_joint_jets': 0,
        'point_root_residual_evaluations': 0, 'physical_root_searches': 0,
        'finite_width_quadrature': 0, 'old_scientific_imports_mains_suites': 0,
        'native_runs': 0, 'gas_IVP_runs': 0, 'NCP_runs': 0}
    checks, certificate = [], {}
    ar = Arithmetic(protocol['precision_digits'])
    I = ar.interval

    def tick():
        if time.monotonic()-wall0 > 45 or time.process_time()-cpu0 > 40:
            raise RuntimeError('FROZEN_TIME_CAP_EXHAUSTED')
        if counts['bernstein_boxes'] > 512 or counts['transcendental_prefactor_boxes'] > 512:
            raise RuntimeError('FROZEN_BOX_CAP_EXHAUSTED')
        if counts['independent_joint_jets'] > 4:
            raise RuntimeError('FROZEN_JET_CAP_EXHAUSTED')

    def check(name, passed, **evidence):
        checks.append({'name': name, 'passed': bool(passed), **dumpable(evidence)})
        if not passed:
            raise AssertionError(name)

    result_path = Path(args.output)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    status, failure = 'FAIL', None
    try:
        raw = json.loads((root/'inputs/PHYS29_SECOND_ORDER_FIRST.json').read_text())
        jraw = json.loads((root/'inputs/PHYS22_INITIAL_COEFFICIENTS.json').read_text())
        check('pinned_source_identities',
              sha(root/'inputs/PHYS29_SECOND_ORDER_FIRST.json') == contract['inputs']['primary_json_sha256']
              and sha(root/'inputs/PHYS22_INITIAL_COEFFICIENTS.json') == contract['inputs']['J_json_sha256'])
        source_literals = ['0.05', '1.01e-14', '0.99e-14', '29979245800',
            '1e-4', '0.9', '13.598434599702', '0.4298', '32.88',
            '2.963', '5.475e4', '1e-18', '13.60', '24.59']
        f64 = {s: Q.from_float(float(s)) for s in source_literals}
        jx = Q(jraw['results']['baseline_local']['J_nonphoto'][2][0])
        jw = Q(jraw['results']['baseline_local']['J_nonphoto'][2][3])
        check('frozen_J_strings', jx == Q(raw['constants']['J_h2_x'])
              and jw == Q(raw['constants']['J_h2_w']))
        A = Q(raw['second_order']['jet_chain']['upper_root']['response_s-4'])
        check('same_exact_nonzero_A', A != 0 and A == Q(contract['geometry']['common_level_exact_s4']),
              A=A, key=contract['geometry']['common_level_key'])
        what = Q(raw['constants']['stored_PHYS26_root_strings']['upper_root'])
        a, b, mean, R = Q('13.61'), Q('24.58'), Q(18), Q('4.39')
        d, eta, mu2 = Q('0.001'), Q('0.25'), Q(1, 3)
        E0, ya, P, chi = (f64[s] for s in ('0.4298', '32.88', '2.963', '13.598434599702'))
        B = E0*ya
        shear = (f64['1.01e-14']-f64['0.99e-14'])/2
        q_shear = 2*shear**2
        kappa_opacity = f64['29979245800']*f64['1e-4']*(1-f64['0.9'])
        prefactor = q_shear*f64['0.05']*kappa_opacity/180
        constant = I(prefactor*f64['5.475e4']*f64['1e-18'])*I(ya).real_power(P/2-Q(11, 2))
        check('positive_common_prefactor', constant.lo > 0)

        # Generic exact/rational checks discriminate conversion and rounding bugs.
        check('directed_fraction_and_arithmetic',
              I(Q(1, 3)).contains_rational(Q(1, 3))
              and (I(Q(2, 7))/I(Q(-3, 11))).contains_rational(Q(-22, 21))
              and (I(-2, 3)**2).contains_rational(0)
              and (I(-2, 3)**2).contains_rational(9))
        rejected = False
        try:
            I(1)/I(-1, 1)
        except ZeroDivisionError:
            rejected = True
        check('zero_denominator_is_rejected', rejected)
        check('expanded_elementary_identities',
              I(0).exp().contains_rational(1)
              and I(1).ln().contains_rational(0)
              and I(4).sqrt().contains_rational(2)
              and I(9).real_power(Q(1, 2)).contains_rational(3))
        poly = [Q(1), Q(-3), Q(2), Q(5)]
        beta = bernstein_coefficients(poly, Q(-2), Q(3))
        counts['bernstein_boxes'] += 1
        # Reconstruct the whole polynomial, not just values at sample points.
        power = [Q(0) for _ in range(4)]
        for i, bi in enumerate(beta):
            for j in range(3-i+1):
                power[i+j] += bi*comb(3, i)*comb(3-i, j)*(-1)**j
        direct_power = [sum((poly[j]*comb(j,k)*Q(-2)**(j-k)*Q(5)**k
                             for j in range(k,4)), Q(0)) for k in range(4)]
        check('exact_Bernstein_polynomial_identity', power == direct_power,
              power=power, bernstein=beta)
        check('degenerate_Bernstein_interval',
              all(v == polynomial_value(poly, Q(2)) for v in
                  bernstein_coefficients(poly, Q(2), Q(2))))
        counts['bernstein_boxes'] += 1
        # Source-free product rule, evaluated with integer exponents and a
        # polynomial expansion independent of T's implementation.
        toyQ, aa, bb = [Q(3), Q(-2), Q(1)], 2, 3
        whole = polynomial_multiply([Q(0), Q(0), Q(1)],
                  polynomial_multiply([Q(1), Q(3), Q(3), Q(1)], toyQ))
        lhs = polynomial_derivative(whole)
        rhs = polynomial_multiply([Q(0), Q(1)],
                  polynomial_multiply([Q(1), Q(2), Q(1)],
                    derivative_numerator(toyQ, Q(aa), Q(bb))))
        check('exact_factored_derivative_product_rule', lhs == rhs)

        representations = build_kernel_representations(P, ya, B, jx, jw, chi)
        check('representation_degree_cap',
              max(len(rep['polynomial'])-1 for rep in representations.values()) <= 16)
        certificate['representations'] = representations
        certificate['source_constants'] = {
            s: {'binary64_hex': float(s).hex(), 'exact_rational': v}
            for s, v in f64.items()}
        certificate['Jx'] = jx
        certificate['Jw'] = jw
        certificate['A'] = A
        certificate['stored_W'] = what
        certificate['prefactor_exact_rational'] = prefactor
        certificate['common_prefactor_interval'] = constant

        def bound_z(order, left, right, label):
            counts['bernstein_boxes'] += 1
            counts['transcendental_prefactor_boxes'] += 1
            tick()
            rep = representations[order]
            coeff = bernstein_coefficients(rep['polynomial'], left, right)
            pmin, pmax = min(coeff), max(coeff)
            Z = I(left, right)
            factor = (constant*I(rep['rational_multiplier'])
                      * Z.real_power(rep['exponent_z'])
                      * (1+Z).real_power(rep['exponent_one_plus_z']))
            enclosure = factor*I(pmin, pmax)
            return enclosure, {'label': label, 'order': order,
                'z_interval': Z, 'polynomial_range_exact': [pmin, pmax],
                'all_Bernstein_positive': all(v > 0 for v in coeff),
                'positive_factor': factor, 'enclosure': enclosure,
                'coefficient_sha256': hashlib.sha256(json.dumps(
                    [str(v) for v in coeff], separators=(',', ':')).encode()).hexdigest()}

        def bound_energy(order, left, right, label):
            Z = (I(left, right)/I(B)).sqrt()
            return bound_z(order, Q(Z.lo), Q(Z.hi), label)

        # The actual grid encloses [a,22] rather than using the wider rational
        # containing interval itself as a physical evaluation domain.
        zdomain = (I(a, Q(22))/I(B)).sqrt()
        zl, zu = Q(zdomain.lo), Q(zdomain.hi)
        check('complete_grid_domain_and_cutoff_containment',
              Q(49,50) <= zl <= zu <= Q(5,4)
              and zl*zl*B <= a and zu*zu*B >= 22
              and zl*zl*B > f64['13.60'] and zu*zu*B < f64['24.59'],
              z_domain=zdomain, extended_energy_domain=[zl*zl*B, zu*zu*B])
        grid, ranges = [], {}
        ncell = protocol['z_cells']
        for order in range(5):
            boxes = []
            for i in range(ncell):
                lo = zl+(zu-zl)*Q(i,ncell)
                hi = zl+(zu-zl)*Q(i+1,ncell)
                val, rec = bound_z(order,lo,hi,'slope_domain_cell_'+str(i))
                grid.append(rec)
                boxes.append(val)
            ranges[order] = Interval(ar, min(v.lo for v in boxes), max(v.hi for v in boxes))
        certificate['covering'] = {'cells_per_order':ncell,'energy_domain_eV':[a,Q(22)],
            'z_domain': zdomain, 'records': grid, 'derivative_ranges': ranges}
        check('continuous_positive_k_second', ranges[2].lo > 0,
              bound=ranges[2], scope='whole interpolation domain, not sampled points')
        check('continuous_positive_k_fourth', ranges[4].lo > 0,
              bound=ranges[4], scope='containing interval for both packets')

        # Certify support for ALL delta in [0,d] and W in [what-eta,what+eta].
        wlo, whi = what-eta, what+eta
        rd = R-d
        interior_lo = mean+(wlo-mu2*d*d)/R-d
        interior_hi = mean+whi/rd+d
        endpoint_lo, endpoint_hi = a, a+2*d
        check('full_tube_feasibility',
              d < min(R,b-mean) and mu2*d*d < wlo
              and whi < (R-d)*(b-mean-d),
              W_tube=[wlo,whi], delta=[Q(0),d])
        check('packet_and_slope_domain_coverage',
              a <= endpoint_lo <= endpoint_hi <= 22
              and a <= interior_lo <= interior_hi <= 22,
              endpoint_packet=[endpoint_lo,endpoint_hi], interior_packet=[interior_lo,interior_hi])

        # Root residual is evaluated at the entire exact stored decimal W,
        # not at its rounded retained node and not at a redefined level A.
        x0 = mean+what/R
        p0, q0 = what/(R*R+what), R*R/(R*R+what)
        ke, ke_rec = bound_energy(0,a,a,'exact_anchor')
        kc, kc_rec = bound_energy(0,x0,x0,'exact_reconstructed_center')
        counts['point_root_residual_evaluations'] += 1
        residual = I(p0)*ke+I(q0)*kc-I(A)
        eps = residual.abs_upper()
        certificate['zero_width_residual'] = {'ke':ke_rec,'kc':kc_rec,
            'exact_geometry':{'x0_eV':x0,'p0':p0,'q0':q0},
            'residual_s-4':residual,'epsilon_r_s-4':eps}

        M1, M2 = ranges[1].abs_upper(), ranges[2].hi
        kappa = I(ranges[2].lo)/2
        Kupper = I(ranges[2].hi)/2
        check('profile_probability_monotonicity', what-mu2*d*R > 0)
        vd = what-mu2*d*d
        pd = vd/(rd*rd+vd)
        dx = what*d/(R*rd)+mu2*d*d/rd
        response_B = (I(pd-p0)*I((ke-kc).abs_upper())
            + I(M1)*(I(pd*d)+I(q0*dx)) + I(mu2*d*d/2)*I(M2))
        total_residual_bound = response_B+I(eps)
        tube_margin = kappa*I(eta)-total_residual_bound
        root_error = I(eps)/kappa
        rho = total_residual_bound/kappa
        check('uniform_common_level_root_existence', tube_margin.lo > 0,
              displacement_bound=rho, eta=eta, margin_s4=tube_margin)
        check('zero_width_exact_level_root_enclosure', root_error.hi < I(eta).lo,
              error_eV2=root_error, A=A)
        # Positive order follows from the exact PHYS32 Peano identity and
        # the slope/packet bounds. These positive constants give the magnitude:
        # -C_large*delta^4 <= Wp-Wu <= -C_small*delta^4 < 0.
        Csmall = I(ranges[4].lo)/(I(945)*Kupper)
        Clarge = I(ranges[4].hi)/(I(945)*kappa)
        check('strict_positive_width_root_order_constants',
              Csmall.lo > 0 and Clarge.hi >= Csmall.lo,
              C_small_eV_minus2=Csmall,C_large_eV_minus2=Clarge)
        certificate['root_tube'] = {'delta_interval_eV':[Q(0),d],
            'W_tube_eV2':[wlo,whi],'packet_end_eV':[endpoint_lo,endpoint_hi],
            'packet_interior_eV':[interior_lo,interior_hi],
            'M1':M1,'M2':M2,'kappa_s-4_eV-2':kappa,'slope_upper_s-4_eV-2':Kupper,
            'B_s-4':response_B,'epsilon_r_s-4':eps,'margin_s-4':tube_margin,
            'root_error_at_zero_eV2':root_error,'rho_all_widths_eV2':rho,
            'C_small_eV-2':Csmall,'C_large_eV-2':Clarge,
            'root_order':'Wp(delta) < Wu(delta) for every 0<delta<=0.001 eV',
            'difference_enclosure_at_d_eV2':[-I(Clarge.hi)*I(d**4),-I(Csmall.lo)*I(d**4)]}

        def independent_jet(E):
            counts['independent_joint_jets'] += 1
            tick()
            Ej = EnergyJet(ar, [I(E),1])
            Xj = Ej/I(E0)
            sigma = ((Xj-1)*(Xj-1)*Xj.power(P/2-Q(11,2))
                *(1+(Xj/I(ya)).power(Q(1,2))).power(-P)*I(f64['5.475e4']*f64['1e-18']))
            phi = sigma*((Ej-I(chi))*I(jw)+I(jx))
            out = {}
            for n in (0,1,2,4):
                # d^n [E² phi'' + 4E phi']:
                out[n] = I(prefactor)*(I(E)**2*factorial(n+2)*phi.c[n+2]
                    + I(E)*(2*n+4)*factorial(n+1)*phi.c[n+1]
                    + n*(n+3)*factorial(n)*phi.c[n])
            return out

        comparisons = []
        # Four inherited EXACT ENERGY STRINGS; this is an expression
        # cross-check, not a sample-based proof of a global sign.
        for name in protocol['independent_nodes']:
            E = Q(raw['energy_nodes_eV'][name])
            jet = independent_jet(E)
            for order, value in jet.items():
                primary, rec = bound_energy(order,E,E,'crosscheck_'+name)
                check('independent_interval_expression_'+name+'_'+str(order),
                      primary.overlaps(value), primary=primary, independent=value)
                comparisons.append({'node':name,'energy_eV':E,'order':order,
                    'primary':primary,'independent':value,'primary_record':rec})
        certificate['independent_expression_comparisons'] = comparisons
        tick()
        check('frozen_call_caps', counts['point_root_residual_evaluations'] == 1
              and counts['independent_joint_jets'] == len(protocol['independent_nodes'])
              and counts['bernstein_boxes'] <= 512)
        status = 'PASS_SCOPED'
    except Exception as exc:
        failure = {'type':type(exc).__name__,'message':str(exc),
                   'traceback':traceback.format_exc()}
        status = 'FAIL'
    elapsed = time.monotonic()-wall0
    cpu = time.process_time()-cpu0
    usage = resource.getrusage(resource.RUSAGE_SELF)
    scientific = {'task':contract['task'],'status':status,'claim_ceiling':contract['claims'],
        'source_commit':contract['source']['commit'],'contract_sha256':sha(root/'PHYSICS_CONTRACT.json'),
        'protocol_sha256':sha(root/'EXECUTION_PROTOCOL.json'),
        'precision_digits':ar.digits,'certificate':certificate,'checks':checks,
        'counts':counts,'elementary_endpoint_calls':ar.elementary_endpoint_calls,'failure':failure}
    result_path.write_text(json.dumps(dumpable(scientific),ensure_ascii=False,indent=2)+'\n')
    receipt = {'role':args.role,'status':status,'output':str(result_path),
        'raw_sha256':sha(result_path),'raw_bytes':result_path.stat().st_size,
        'wall_seconds':elapsed,'cpu_seconds':cpu,'maxrss_KiB':usage.ru_maxrss,
        'python':platform.python_version(),'source_root':str(root),
        'counts':counts,'checks_passed':sum(c['passed'] for c in checks),
        'checks_total':len(checks),'failure':failure}
    (ledger/(args.role+'.finished.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
    return 0 if status == 'PASS_SCOPED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
