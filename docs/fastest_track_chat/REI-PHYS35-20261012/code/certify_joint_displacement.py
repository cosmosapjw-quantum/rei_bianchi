#!/usr/bin/env python3
"""PHYS35: exact rational recombination of accepted PHYS33/34 enclosures.

No physical kernel, polynomial, transcendental, jet, root, quadrature or old
scientific module is evaluated. Fractions are authoritative; Decimal is used
only to render exact results outward. Importing this module does no science.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
import traceback


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exact(value):
    if isinstance(value, (float, bool)):
        raise TypeError('No float or Boolean scientific operands')
    return Q(value)


def pair(record):
    lo, hi = exact(record['lower']), exact(record['upper'])
    if lo > hi:
        raise ValueError('Reversed inherited enclosure')
    return lo, hi


def field(record, path):
    for part in path.split('.'):
        record = record[part]
    return record


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
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
    frozen_path = root/'evidence/PREEXECUTION_FREEZE.json'
    frozen = json.loads(frozen_path.read_text())
    for relative, expected in frozen['sha256'].items():
        if sha(root/relative) != expected:
            raise RuntimeError('PREEXECUTION_IDENTITY_MISMATCH: '+relative)
    output = Path(args.output).resolve()
    if output.exists():
        raise FileExistsError('Refuse output overwrite')
    ledger = Path(args.ledger).resolve()
    ledger.mkdir(parents=True, exist_ok=True)
    if args.role == 'replay':
        first = ledger/'first.finished.json'
        if not first.exists() or json.loads(first.read_text())['status'] != 'PASS_SCOPED':
            raise RuntimeError('Replay requires a completed passing first run')
    with (ledger/(args.role+'.started.json')).open('x') as file:
        json.dump({'role': args.role, 'started_utc': datetime.now(timezone.utc).isoformat(),
                   'source_root': str(root), 'preexecution_freeze_sha256': sha(frozen_path)}, file, indent=2)
        file.write('\n')
    caps = protocol['caps']
    sys.set_int_max_str_digits(caps['int_to_string_decimal_digits'])
    resource.setrlimit(resource.RLIMIT_CPU, (caps['cpu_seconds'], caps['cpu_seconds']+1))
    memory = caps['memory_MiB']*1024**2
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    wall0, cpu0 = time.monotonic(), time.process_time()
    counts = {key: 0 for key in protocol['anticipated_counts_per_main']}
    counts['main_this_process'] = 1
    checks, certificate = [], {}
    down = Context(prec=protocol['display_digits'], rounding=ROUND_FLOOR)
    up = Context(prec=protocol['display_digits'], rounding=ROUND_CEILING)
    display_count = 0

    def tick():
        if time.monotonic()-wall0 > caps['wall_seconds'] or time.process_time()-cpu0 > caps['cpu_seconds']:
            raise RuntimeError('FROZEN_TIME_CAP_EXHAUSTED')
        for key, val in counts.items():
            if val > protocol['anticipated_counts_per_main'][key]:
                raise RuntimeError('FROZEN_CALL_CAP_EXHAUSTED: '+key)

    def check(name, passed, **evidence):
        checks.append({'name': name, 'passed': bool(passed), **encode(evidence)})
        if not passed:
            raise AssertionError(name)

    def outward(lo, hi=None):
        nonlocal display_count
        lo, hi = exact(lo), exact(lo if hi is None else hi)
        if lo > hi:
            raise ValueError('Reversed new interval')
        dl = down.divide(Decimal(lo.numerator), Decimal(lo.denominator))
        du = up.divide(Decimal(hi.numerator), Decimal(hi.denominator))
        if not dl.is_finite() or not du.is_finite() or Q(dl) > lo or Q(du) < hi:
            raise AssertionError('Outward rendering failed exact rational comparison')
        display_count += 1
        return {'lower': str(dl), 'upper': str(du)}

    def bound(lo, hi, unit):
        return {'exact_rational': {'lower': str(lo), 'upper': str(hi)},
                'decimal_outward_90': outward(lo, hi), 'unit': unit}

    status, failure = 'FAIL', None
    try:
        manifest = json.loads((root/'SOURCE_MANIFEST.json').read_text())
        check('all_pinned_inputs_byte_identical', all(sha(root/r['path']) == r['sha256'] for r in manifest['inputs']))
        primary = json.loads((root/'inputs/PHYS29_SECOND_ORDER_FIRST.json').read_text())
        jraw = json.loads((root/'inputs/PHYS22_INITIAL_COEFFICIENTS.json').read_text())
        jx = exact(jraw['results']['baseline_local']['J_nonphoto'][2][0])
        jw = exact(jraw['results']['baseline_local']['J_nonphoto'][2][3])
        check('primary_and_J_source_identity',
              sha(root/'inputs/PHYS29_SECOND_ORDER_FIRST.json') == contract['inputs']['primary_json_sha256']
              and sha(root/'inputs/PHYS22_INITIAL_COEFFICIENTS.json') == contract['inputs']['J_json_sha256']
              and jx == exact(primary['constants']['J_h2_x'])
              and jw == exact(primary['constants']['J_h2_w']))
        geometry = contract['geometry']
        a, b, mean = (exact(geometry[k]) for k in ('a_eV', 'b_eV', 'm_eV'))
        d, eta, mu2 = exact(geometry['delta_eV'][1]), exact(geometry['tube_radius_eV2']), exact(geometry['mu2'])
        check('fixed_common_geometry', (a, b, mean, d, eta, mu2) ==
              (Q('13.61'), Q('24.58'), Q(18), Q('0.001'), Q('0.25'), Q(1, 3))
              and exact(geometry['delta_eV'][0]) == 0)
        prior_data, branch_data, coefficients = {}, {}, {}
        shared_constants = shared_representations = None
        for name in protocol['branch_order']:
            tick()
            cfg = geometry['branches'][name]
            prior = cfg['prior']
            folder = root/'inputs'/prior
            raw_path = folder/'evidence/CERTIFICATE_FIRST.json'
            raw = json.loads(raw_path.read_text())
            counts['prior_certificate_reads'] += 1
            old = raw['certificate']
            oldcontract = json.loads((folder/'PHYSICS_CONTRACT.json').read_text())
            decision_path = folder/'independent/DECISION_REVIEW.json'
            decision = json.loads(decision_path.read_text())
            closeout = json.loads((folder/'state/CLOSEOUT.json').read_text())
            check(name+'_inherited_accepted_certificate',
                  sha(raw_path) == contract['inputs']['prior_raw'][prior]
                  and sha(decision_path) == contract['inputs']['prior_decisions'][prior]
                  and raw['status'] == 'PASS_SCOPED'
                  and all(c['passed'] is True for c in raw['checks'])
                  and decision['decision'] == 'PROMOTE_SCOPED' and decision['fatal_count'] == 0
                  and closeout['decision'] == 'PROMOTE_SCOPED'
                  and sha(folder/'PHYSICS_CONTRACT.json') == raw['contract_sha256']
                  and sha(folder/'EXECUTION_PROTOCOL.json') == raw['protocol_sha256'],
                  inherited_task=raw['task'], inherited_checks=len(raw['checks']), rerun_count=0)
            prior_data[name] = old
            if shared_constants is None:
                shared_constants = old['source_constants']
                shared_representations = old['representations']
            check(name+'_same_fixed_kernel', old['source_constants'] == shared_constants
                  and old['representations'] == shared_representations
                  and exact(old['Jx']) == jx and exact(old['Jw']) == jw)
            A = exact(field(primary, cfg['A_key']))
            what_string = field(primary, cfg['W_key'])
            what = exact(what_string)
            s, R, anchor = cfg['s'], exact(cfg['R_eV']), exact(cfg['anchor_eV'])
            Elo, Ehi = map(exact, cfg['slope_domain_eV'])
            oldg = oldcontract['geometry']
            check(name+'_exact_levels_W_and_original_domain', A != 0
                  and A == exact(cfg['A_exact_s-4']) == exact(old['A'])
                  and what == exact(old['stored_W'])
                  and oldg['common_level_key'] == cfg['A_key']
                  and exact(oldg['common_level_exact_s4']) == A
                  and oldg['delta_eV'] == geometry['delta_eV']
                  and exact(oldg['tube_radius_eV2']) == eta
                  and oldg['slope_energy_domain_eV'] == cfg['slope_domain_eV']
                  and exact(oldg['R_eV']) == R
                  and ((s == 1 and anchor == a and R == mean-a)
                       or (s == -1 and anchor == b and R == b-mean)),
                  A_exact_s4=A, W_string=what_string, W_key=cfg['W_key'], A_key=cfg['A_key'])
            wlo, whi, rd = what-eta, what+eta, R-d
            vmin, vmax = wlo-mu2*d*d, whi
            check(name+'_inherited_tube_geometry', 0 < d < R and vmin > 0
                  and [wlo, whi] == list(map(exact, old['root_tube']['W_tube_eV2'])))
            if s == 1:
                centers = (mean+vmin/R, mean+vmax/rd)
                endpoint = (a, a+2*d)
            else:
                centers = (mean-vmax/rd, mean-vmin/R)
                endpoint = (b-2*d, b)
            interior = (centers[0]-d, centers[1]+d)
            check(name+'_whole_packet_geometry_matches_prior',
                  list(endpoint) == list(map(exact, old['root_tube']['packet_end_eV']))
                  and list(interior) == list(map(exact, old['root_tube']['packet_interior_eV']))
                  and Elo <= endpoint[0] <= endpoint[1] <= Ehi
                  and Elo <= interior[0] <= interior[1] <= Ehi)
            xref = exact(primary['energy_nodes_eV'][cfg['reference_node']])
            Dref = xref-anchor
            check(name+'_reference_path_and_orientation',
                  Elo <= xref <= Ehi and Elo <= anchor <= Ehi and s*Dref > 0)

            def point(node, order, energy):
                records = [r for r in old['independent_expression_comparisons']
                           if r['node'] == node and r['order'] == order]
                if len(records) != 1 or exact(records[0]['energy_eV']) != energy:
                    raise AssertionError('Inherited point label/energy mismatch')
                return pair(records[0]['primary'])

            ke = point(cfg['endpoint_node'], 0, anchor)
            kc = point(cfg['reference_node'], 0, xref)
            k1c = point(cfg['reference_node'], 1, xref)
            Hc = max(abs(centers[0]-xref), abs(centers[1]-xref))
            M3 = max(abs(v) for v in pair(old['covering']['derivative_ranges']['3']))
            M4 = max(abs(v) for v in pair(old['covering']['derivative_ranges']['4']))
            Cref_lo = (ke[0]-kc[1]+min(Dref*k1c[0], Dref*k1c[1]))/(Dref*Dref)
            Cref_hi = (ke[1]-kc[0]+max(Dref*k1c[0], Dref*k1c[1]))/(Dref*Dref)
            geometry_error = M3*(d/6+Hc/3)
            smoothing_error = mu2*M4*d*d/4
            Cerr = geometry_error+smoothing_error
            Clo, Chi = Cref_lo-Cerr, Cref_hi+Cerr
            check(name+'_positive_uniform_slope', 0 < Clo <= Chi,
                  slope=bound(Clo, Chi, 's^-4 eV^-2'))

            # The exact old cell grid is reconstructed from declared grid endpoints.
            # Rounded per-row z_interval values are checked to CONTAIN each exact cell;
            # their outer slivers are never asserted to have the cell polynomial bound.
            covering = old['covering']
            n = covering['cells_per_order']
            check(name+'_unchanged_grid_count', n == protocol['read_only_prior_z_cells'])
            zl, zu = pair(covering['z_domain'])
            B = exact(old['source_constants']['0.4298']['exact_rational'])*exact(old['source_constants']['32.88']['exact_rational'])
            hi_cut = exact(old['source_constants']['24.59']['exact_rational'])
            lo_cut = exact(old['source_constants']['13.60']['exact_rational'])
            check(name+'_old_grid_whole_domain_and_cutoffs', 0 < zl < zu
                  and lo_cut < B*zl*zl <= Elo and Ehi <= B*zu*zu < hi_cut)
            rows = [r for r in covering['records'] if r['order'] == 4]
            check(name+'_old_k4_record_count', len(rows) == n)
            cells = []
            for i, row in enumerate(rows):
                counts['existing_k4_records_inspected'] += 1
                z0, z1 = zl+(zu-zl)*Q(i, n), zl+(zu-zl)*Q(i+1, n)
                declared_lo, declared_hi = pair(row['z_interval'])
                if row['label'] != 'slope_domain_cell_'+str(i) or not (declared_lo <= z0 < z1 <= declared_hi):
                    raise AssertionError('Cell identity or outward prefactor interval mismatch')
                if 'exact_rational_cell' in row and list(map(exact, row['exact_rational_cell'])) != [z0, z1]:
                    raise AssertionError('Stored exact rational cell mismatch')
                if prior == 'PHYS34' and 'exact_rational_cell' not in row:
                    raise AssertionError('PHYS34 exact rational cell missing')
                value = pair(row['enclosure'])
                if value[0] <= 0 or row['all_Bernstein_positive'] is not True:
                    raise AssertionError('Inherited k4 positivity unavailable')
                cells.append({'index': i, 'energy': (B*z0*z0, B*z1*z1),
                              'z_exact': (z0, z1), 'bounds': value,
                              'coefficient_sha256': row['coefficient_sha256']})
            check(name+'_old_exact_grid_contiguous', all(cells[i]['energy'][1] == cells[i+1]['energy'][0] for i in range(n-1)))

            def packet_range(support, label):
                counts['packet_cover_queries'] += 1
                selected = [c for c in cells if c['energy'][0] <= support[1] and c['energy'][1] >= support[0]]
                if not selected:
                    raise AssertionError('No old cells cover packet')
                check(name+'_'+label+'_continuous_cell_cover',
                      selected[0]['energy'][0] <= support[0] <= support[1] <= selected[-1]['energy'][1]
                      and all(selected[i]['energy'][1] == selected[i+1]['energy'][0] for i in range(len(selected)-1)))
                lo = min(c['bounds'][0] for c in selected)
                hi = max(c['bounds'][1] for c in selected)
                return (lo, hi), {'packet_support_eV': bound(*support, 'eV'),
                    'selected_cell_indices': [c['index'] for c in selected],
                    'selected_cells': selected, 'k4': bound(lo, hi, 's^-4 eV^-4')}

            ek4, erec = packet_range(endpoint, 'endpoint')
            xk4, xrec = packet_range(interior, 'interior')
            pmin, pmax = vmin/(R*R+vmin), vmax/(rd*rd+vmax)
            check(name+'_probability_range', 0 < pmin <= pmax < 1)
            affine_low = [p*ek4[0]+(1-p)*xk4[0] for p in (pmin, pmax)]
            affine_high = [p*ek4[1]+(1-p)*xk4[1] for p in (pmin, pmax)]
            Slo, Shi = min(affine_low), max(affine_high)
            L, U = Slo/(945*Chi), Shi/(945*Clo)
            check(name+'_positive_profile_coefficient', 0 < Slo <= Shi and 0 < L <= U)
            counts['branch_bound_assemblies'] += 1
            coefficients[name] = (L, U)
            branch_data[name] = {
                'prior_certificate_path': str(raw_path.relative_to(root)),
                'prior_raw_sha256': sha(raw_path), 'A_exact_s4': A, 'stored_W_exact_eV2': what,
                'reference': {'anchor_eV': anchor, 'xref_eV': xref, 'Dref_eV': Dref,
                    'xref_equals_exact_reconstructed_center': xref == mean+s*what/R,
                    'k_anchor': bound(*ke, 's^-4'), 'k_reference': bound(*kc, 's^-4'),
                    'kprime_reference': bound(*k1c, 's^-4 eV^-1'),
                    'Cref': bound(Cref_lo, Cref_hi, 's^-4 eV^-2')},
                'root_tube_eV2': bound(wlo, whi, 'eV^2'),
                'center_interval_eV': bound(*centers, 'eV'),
                'Hc_upper_eV': bound(Hc, Hc, 'eV'),
                'M3_inherited': M3, 'M4_inherited': M4,
                'slope_geometry_error_upper': bound(geometry_error, geometry_error, 's^-4 eV^-2'),
                'slope_smoothing_error_upper': bound(smoothing_error, smoothing_error, 's^-4 eV^-2'),
                'slope_total_error_upper': bound(Cerr, Cerr, 's^-4 eV^-2'),
                'uniform_slope': bound(Clo, Chi, 's^-4 eV^-2'),
                'endpoint_packet': erec, 'interior_packet': xrec,
                'p_interval': bound(pmin, pmax, '1'),
                'S_interval': bound(Slo, Shi, 's^-4 eV^-4'),
                'quartic_magnitude_coefficient': bound(L, U, 'eV^-2'),
                'root_shift_at_d': bound(-U*d**4, -L*d**4, 'eV^2'),
                'meaning': 'For every positive delta, DeltaW=-delta^4*c(delta); c lies in this uniform interval.'}
            tick()
        certificate['branches'] = branch_data
        check('distinct_levels_preserved', branch_data['upper']['A_exact_s4'] != branch_data['lower']['A_exact_s4'])
        Lplus, Uplus = coefficients['upper']
        Lminus, Uminus = coefficients['lower']
        gap_lo, gap_hi = Lplus-Uminus, Uplus-Lminus
        counts['joint_bound_assemblies'] += 1
        coarse_lo = exact(prior_data['upper']['root_tube']['C_small_eV-2']['lower'])-exact(prior_data['lower']['root_tube']['C_large_eV-2']['upper'])
        coarse_hi = exact(prior_data['upper']['root_tube']['C_large_eV-2']['upper'])-exact(prior_data['lower']['root_tube']['C_small_eV-2']['lower'])
        counts['coarse_bound_diagnostics'] += 1
        direction = 'WIDENS' if gap_lo > 0 else ('NARROWS' if gap_hi < 0 else 'UNRESOLVED_BOUND_OVERLAP')
        certificate['joint'] = {
            'observable': contract['observable'],
            'coarse_inherited_coefficient_difference': bound(coarse_lo, coarse_hi, 'eV^-2'),
            'new_gap_coefficient': bound(gap_lo, gap_hi, 'eV^-2'),
            'gap_change_at_d': bound(gap_lo*d**4, gap_hi*d**4, 'eV^2'),
            'gap_change_at_zero': '0 exactly; profiles coincide, so both within-branch root shifts vanish.',
            'positive_width_domain_eV': ['0 < delta', str(d)],
            'direction': direction,
            'claim_scope': 'Two fixed levels A_minus != A_plus; fixed source-real kernel only; no common-A or physical-admission claim.'}
        check('coarse_bound_previously_overlapped_zero', coarse_lo < 0 < coarse_hi)
        check('new_coefficient_interval_is_ordered', gap_lo <= gap_hi)
        # A valid overlapping bound is retained as an unresolved scientific result.
        signed = gap_lo > 0 or gap_hi < 0
        checks.append({'name': 'uniform_joint_sign_separation', 'passed': signed,
                       'direction': direction, 'negative_result_policy': 'HOLD_BOUND_OVERLAP if not separated'})
        check('frozen_call_caps_and_zero_new_kernel_work', counts == protocol['anticipated_counts_per_main'])
        check('all_decimal_renderings_contain_exact_rationals', display_count > 0,
              rendering_count=display_count, scientific_rounding_operations=0)
        tick()
        status = 'PASS_SCOPED' if signed else 'HOLD_BOUND_OVERLAP'
    except Exception as exc:
        failure = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
        status = 'FAIL'
    science = {'task': contract['task'], 'status': status,
        'claim_ceiling_snapshot': contract['claims'], 'source_commit': contract['source']['commit'],
        'contract_sha256': sha(root/'PHYSICS_CONTRACT.json'),
        'protocol_sha256': sha(root/'EXECUTION_PROTOCOL.json'),
        'arithmetic': 'Exact rational science; 90-digit outward decimal rendering only',
        'certificate': certificate, 'checks': checks, 'counts': counts,
        'outward_rendering_count': display_count, 'failure': failure}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as file:
        json.dump(encode(science), file, ensure_ascii=False, indent=2)
        file.write('\n')
    usage = resource.getrusage(resource.RUSAGE_SELF)
    receipt = {'task': contract['task'], 'role': args.role, 'status': status,
        'source_root': str(root), 'output': str(output), 'raw_sha256': sha(output),
        'raw_bytes': output.stat().st_size, 'wall_seconds': time.monotonic()-wall0,
        'cpu_seconds': time.process_time()-cpu0, 'maxrss_KiB': usage.ru_maxrss,
        'python': platform.python_version(), 'counts': counts,
        'checks_passed': sum(c['passed'] for c in checks), 'checks_total': len(checks),
        'failure': failure}
    with (ledger/(args.role+'.finished.json')).open('x') as file:
        json.dump(receipt, file, indent=2)
        file.write('\n')
    print(json.dumps(receipt, indent=2), flush=True)
    return 0 if status == 'PASS_SCOPED' else 2 if status == 'HOLD_BOUND_OVERLAP' else 1


if __name__ == '__main__':
    raise SystemExit(main())
