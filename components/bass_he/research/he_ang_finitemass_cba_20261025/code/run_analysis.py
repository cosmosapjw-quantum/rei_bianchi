"""Execute only the frozen new finite-mass fixtures under run_bounded.py."""
import csv
import datetime
import io
import json
import math
from pathlib import Path
import traceback
import mpmath as mp
from numpy.polynomial.legendre import leggauss
import fm_cba as fm
from io_utils import atomic_bytes, atomic_json, cjson
from reference import mp_form_factor, mp_overlap, mp_parameters, mpjson, original_integral, scaled

UNIT = Path(__file__).resolve().parents[1]
PLAN = json.loads((UNIT/'FROZEN_CONTRACT.json').read_bytes().decode('utf-8'))['analysis']
RESULTS = UNIT/'results'
REPORT = {'schema': 'HEANG_FINITEMASS_CBA_V1', 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'model': fm.MODEL, 'generic': [], 'quadrature': [], 'tiny': [], 'kinematics_normalization': [],
          'fold': [], 'illustration': [], 'mass_trend': [], 'acceptance': PLAN,
          'old_suite_replay': 0, 'physical_provider_admitted': False,
          'scope': 'Frozen finite fixtures; no uniform/outward accuracy or physical-provider certificate'}


def save(name='ANALYSIS_PARTIAL.json'):
    atomic_json(RESULTS/name, REPORT)


def kernel_checks():
    cfg = PLAN['generic']
    for M in cfg['masses']:
        for geometry in cfg['geometries']:
            D, k = geometry['Delta'], geometry['k']
            plus, minus = fm.overlap_terms(M, D, k)
            F = fm.finite_form_factor(M, D, k)
            with mp.workdps(cfg['mp_digits'][0]): r50 = mp_form_factor(M, D, k)
            with mp.workdps(cfg['mp_digits'][1]):
                r80 = mp_form_factor(M, D, k)
                errors = [scaled(mp.mpc(x), y) for x, y in zip((F, plus, minus), r80)]
                precision = [scaled(x, y) for x, y in zip(r50, r80)]
                row = {'M': M, 'geometry': geometry, 'F_binary64': cjson(F),
                       'plus_binary64': cjson(plus), 'minus_binary64': cjson(minus),
                       'mp50_F_plus_minus': [mpjson(x) for x in r50],
                       'mp80_F_plus_minus': [mpjson(x) for x in r80],
                       'binary64_scaled_errors_F_plus_minus': list(map(float, errors)),
                       'mp50_vs80_scaled_errors': [mp.nstr(x, 45) for x in precision],
                       'omitted_second_phase_overlap_abs_DIAGNOSTIC_ONLY': abs(minus),
                       'pass': max(errors) <= cfg['binary64_scaled_tolerance']
                               and max(precision) <= cfg['mp_precision_scaled_tolerance']}
            REPORT['generic'].append(row); save()
    cfg = PLAN['quadrature']
    for case in cfg['cases']:
        with mp.workdps(cfg['digits']):
            mu, b = mp_parameters(case['M'])
            D, k = list(map(mp.mpf, case['Delta'])), list(map(mp.mpf, case['k']))
            results = []
            for label, s in [('aDelta', [mu*x for x in D]), ('minus_bDelta', [-b*x for x in D])]:
                value, parts = original_integral(mu, s, k)
                closed = mp_overlap(mu, s, k)
                error = scaled(value, closed)
                results.append({'term': label, 'shift': [mp.nstr(x, 55) for x in s],
                                'original_integral': mpjson(value), 'closed': mpjson(closed),
                                'raw_integral_parts': [mpjson(x) for x in parts],
                                'scaled_error': mp.nstr(error, 45), 'pass': error <= cfg['scaled_tolerance']})
            row = {'fixture': case, 'terms': results, 'method': cfg['method'],
                   'integration_segments': ['0..1', '1..4', '4..12', '12..infinity'],
                   'pass': all(x['pass'] for x in results)}
        REPORT['quadrature'].append(row); save()
    cfg = PLAN['tiny']
    for M in cfg['masses']:
        for direction, unit in [('parallel z', (0, 0, 1)), ('transverse x', (1, 0, 0))]:
            for t in cfg['t']:
                D = tuple(t*x for x in unit); F = fm.finite_form_factor(M, D, cfg['k'])
                with mp.workdps(cfg['reference_digits']):
                    ref = mp_form_factor(M, D, cfg['k'])[0]
                    error = abs(mp.mpc(F)-ref)/abs(ref) if ref else abs(F)
                    row = {'M': M, 'direction': direction, 't_binary64': t, 'Delta': D,
                           'F_binary64': cjson(F), 'F_mp80': mpjson(ref),
                           'true_relative_error': float(error),
                           'pass': error <= cfg['true_relative_tolerance']}
                REPORT['tiny'].append(row); save()


def kinematic_normalization_checks():
    for M in PLAN['generic']['masses']:
        x = fm.jacobi_tdcs(250/27.2, 5/27.2, M, (.1, .03, 1), (.4, -.1, 1))
        state = fm.shell.shell_state(x['E0'], x['binding'], M, x['p_A'], x['p_B'])
        delta2 = fm.cba._dot(x['Delta'], x['Delta'])
        Tdelta = (4*math.pi/delta2)/(2*math.pi)**3*x['F']
        delta_W = (2*math.pi)**4/x['incident_speed']*abs(Tdelta)**2
        independent_J = 4*x['mu']*x['nu']**2*math.hypot(*x['q'])*math.hypot(*x['k'])/x['qi']*abs(x['F'])**2/delta2**2
        map_errors = [abs(x['Delta'][i]-(x['P'][i]-x['p_A'][i])) for i in range(3)]
        lab = fm.lab_tdcs(x['E0'], M, x['p_A'], x['p_B'])
        branch_errors = [abs(b['shell_residual']) for b in lab['branches']]
        norm_errors = [abs(x['W']-delta_W)/max(1., abs(delta_W)),
                       abs(x['tdcs_au']-independent_J)/max(1., abs(independent_J))]
        kin_errors = map_errors+[abs(state['F']), abs(state['energy_identity_residual'])]+branch_errors
        row = {'M': M, 'Er': x['Er'], 'binding': x['binding'], 'shell_residual': state['F'],
               'energy_identity_residual': state['energy_identity_residual'], 'Delta_mapping_errors': map_errors,
               'W': x['W'], 'delta_state_W': delta_W, 'Jacobi_tdcs_au': x['tdcs_au'],
               'independent_coefficient_J': independent_J, 'normalization_scaled_errors': norm_errors,
               'lab_status': lab['status'], 'positive_lab_branches': len(lab['branches']),
               'lab_branch_shell_errors': branch_errors, 'lab_density': lab['density'],
               'pass': max(kin_errors) <= PLAN['kinematics_scaled_tolerance']
                       and max(norm_errors) <= PLAN['normalization_scaled_tolerance']
                       and lab['density'] is not None}
        REPORT['kinematics_normalization'].append(row); save()


def fold_checks():
    cfg = PLAN['fold']; M, E0 = cfg['M'], cfg['E0']
    P = math.sqrt(2*E0); pA = (0., 0., P/10)
    z = fm.finite_mass_parameters(M)
    sphere = fm.shell.conditional_sphere(E0, z['binding'], M, pA)
    rho, c = sphere['radius'], sphere['center'][2]
    if not (sphere['status'] == 'SPHERE' and c > rho > 0):
        raise RuntimeError('frozen weighted-fold fixture lost two-root geometry')
    for order in cfg['gauss_orders']:
        nodes, weights = leggauss(order)
        regular_terms, folded_terms = [], []
        for u, weight in zip(nodes, weights):
            u, weight = float(u), float(weight)
            k = (rho*math.sqrt(1-u*u), 0., rho*u)
            pB = (k[0], 0., c+k[2])
            regular_terms.append(weight*fm.invariant_weight(E0, M, pA, pB)['W'])
        sphere_value = 2*math.pi*z['mu']*rho*math.fsum(regular_terms)
        branch_rows = []
        for x, weight in zip(nodes, weights):
            h = rho*(float(x)+1)/2; dh_weight = rho*float(weight)/2
            root_sqrt = math.sqrt(h*h+c*c-rho*rho)
            t = root_sqrt/c
            transverse = math.sqrt(1-t*t)
            plus, minus = c*t+h, c*t-h
            values = []
            for p in (plus, minus):
                if p <= 0: raise RuntimeError('frozen fold branch is not positive')
                pB = (p*transverse, 0., p*t)
                W = fm.invariant_weight(E0, M, pA, pB)['W']
                values.append(p*p*W)
            contribution = dh_weight*sum(values)/(sphere['alpha']*c*root_sqrt)
            folded_terms.append(contribution)
            branch_rows.append({'h': h, 'p_plus': plus, 'p_minus': minus,
                                'p2W_plus': values[0], 'p2W_minus': values[1]})
        folded_value = 2*math.pi*math.fsum(folded_terms)
        chart_error = abs(folded_value-sphere_value)/abs(sphere_value)
        row = {'order': order, 'M': M, 'E0': E0, 'p_A': pA, 'binding': z['binding'],
               'rho_squared': sphere['radius_squared'], 'center': sphere['center'],
               'sphere_integral': sphere_value, 'two_root_h_integral': folded_value,
               'chart_relative_error': chart_error, 'two_root_samples': branch_rows,
               'units': 'a0^2/p0^3, conditional slice; not total event sigma'}
        REPORT['fold'].append(row); save()
    fine, previous = REPORT['fold'][-1], REPORT['fold'][-2]
    refinement = max(abs(fine[key]-previous[key])/abs(fine[key])
                     for key in ['sphere_integral', 'two_root_h_integral'])
    REPORT['fold_acceptance'] = {'fine_chart_relative_error': fine['chart_relative_error'],
        'fine_refinement_relative_error': refinement,
        'pass': fine['chart_relative_error'] <= cfg['fine_chart_relative_tolerance']
                and refinement <= cfg['fine_refinement_relative_tolerance']}
    save()


def angle_direction(degrees):
    theta = math.radians(degrees)
    return (math.sin(theta), 0., math.cos(theta))


def illustrations():
    cfg = PLAN['illustration']; E0, Er, U = 250/27.2, 5/27.2, 27.2
    nq = angle_direction(cfg['q_direction_degrees'])
    for angle in range(-180, 181, 5):
        nk = angle_direction(angle)
        row = {'oriented_k_angle_degree': angle, 'Er': Er, 'energy_label': 'Er relative pair, not lab EB',
               'units': 'a0^2/(eV sr^2), nominal27.2eV/E_h'}
        for label, M in [('M2_synthetic', 2.), ('proton', 1836.152673426)]:
            x = fm.jacobi_tdcs(E0, Er, M, nq, nk)
            row[label+'_tdcs_au'] = x['tdcs_au']; row[label+'_per_eV'] = x['tdcs_au']/U
        parent = fm.cba.direct_tdcs(E0, Er, (0, 0, 1), nq, nk)
        row['infinite_parent100_tdcs_au'] = parent['tdcs_au']
        row['infinite_parent100_per_eV'] = parent['tdcs_au']/U
        REPORT['illustration'].append(row)
    nk = angle_direction(cfg['trend_k_angle_degrees'])
    reference = fm.cba.direct_tdcs(E0, Er, (0, 0, 1), nq, nk)['tdcs_au']
    for M in cfg['mass_trend']:
        value = fm.jacobi_tdcs(E0, Er, M, nq, nk)['tdcs_au']
        REPORT['mass_trend'].append({'M': M, 'k_angle_degree': cfg['trend_k_angle_degrees'],
            'finite_tdcs_au': value, 'infinite_tdcs_au': reference,
            'absolute_difference_au': abs(value-reference),
            'absolute_difference_per_eV': abs(value-reference)/U,
            'units': 'a0^2/(eV sr^2), absolute finite-M difference'})
    stream = io.StringIO(newline='')
    fields = ['oriented_k_angle_degree', 'M2_synthetic_per_eV', 'proton_per_eV', 'infinite_parent100_per_eV']
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader(); writer.writerows({k: row[k] for k in fields} for row in REPORT['illustration'])
    atomic_bytes(RESULTS/'ILLUSTRATION.csv', stream.getvalue().encode('utf-8'))
    save()


def run():
    kernel_checks(); kinematic_normalization_checks(); fold_checks(); illustrations()
    categories = ['generic', 'quadrature', 'tiny', 'kinematics_normalization']
    REPORT['checks_by_category'] = {name: {'rows': len(REPORT[name]), 'passed': sum(row['pass'] for row in REPORT[name])}
                                   for name in categories}
    REPORT['pass'] = all(row['pass'] for name in categories for row in REPORT[name]) and REPORT['fold_acceptance']['pass']
    REPORT['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save('ANALYSIS.json')
    print(json.dumps({'pass': REPORT['pass'], 'checks': REPORT['checks_by_category'], 'fold': REPORT['fold_acceptance']}))
    return 0 if REPORT['pass'] else 1


if __name__ == '__main__':
    try: raise SystemExit(run())
    except Exception as exc:
        REPORT['exception'] = {'class': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
        save('ANALYSIS_FAILURE.json')
        raise
