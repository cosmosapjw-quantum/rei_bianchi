#!/usr/bin/env python3
"""Actual saved AXBI abundance/clock/REC consumer. No new ODE evolution."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np
import pandas as pd
import scipy
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
YEAR_S = 31557600.0
FHE = 0.2454 / (4.0 * (1.0 - 0.2454))
# Exact values consumed from REC PR199's native source-law implementation.
C_CM_S = 29979245800.0
SIGMA_T_CM2 = 6.6524587051e-25
H0_S = 67.4e5 / 3.0856775814913673e24
A_INITIAL = 1.0 / 21.0
OMEGA_R, OMEGA_M = 9.2e-5, 0.315
OMEGA_L = 1.0 - OMEGA_R - OMEGA_M
OBS = ['x_HI', 'x_HII', 'x_HeI', 'x_HeII', 'x_HeIII', 'xe_per_H', 'temperature_K']
YS = ['Y_HI', 'Y_HII', 'Y_HeI', 'Y_HeII', 'Y_HeIII', 'Y_e']
COLS = ['case_id', 'q_ref', 'time_s', 'a', 'zbar', 'b', 'H_per_s', 's_per_s',
        'x_HI', 'x_HII', 'x_HeI', 'x_HeII', 'x_HeIII', 'nH_proper_cm3',
        'ne_proper_cm3', 'temperature_K']


def require(condition, code):
    if not bool(condition):
        raise ValueError(code)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def interp(x, xp, fp):
    """No extrapolation. Only <=8-ulp endpoint roundoff may be clipped."""
    x = np.asarray(x, dtype=float)
    require(np.isfinite(x).all(), 'NONFINITE_COORDINATE')
    require(np.all(np.diff(xp) > 0), 'NONMONOTONE_INTERPOLATION_AXIS')
    tol = 8 * np.finfo(float).eps * max(1.0, abs(xp[0]), abs(xp[-1]))
    require(np.all(x >= xp[0]-tol) and np.all(x <= xp[-1]+tol), 'COORDINATE_EXTRAPOLATION')
    return np.interp(np.clip(x, xp[0], xp[-1]), xp, fp)


def validate_frame(d, spec):
    require(len(d) == spec['rows'], 'ROW_COUNT')
    require(set(d.case_id) == {spec['id']}, 'CASE_ID')
    require(np.isfinite(d[COLS[1:]].to_numpy()).all(), 'NONFINITE_STATE')
    require(np.all(d.q_ref.to_numpy() == spec['q_ref']), 'WRONG_SHEAR')
    require(np.all(np.diff(d.time_s) > 0), 'NONMONOTONE_PROPER_TIME')
    require(np.all(np.diff(d.a) > 0), 'NONMONOTONE_SCALE')
    require(d.time_s.iloc[0] == 0, 'WRONG_TIME_ORIGIN')
    require(d.zbar.iloc[0] == 20 and d.zbar.iloc[-1] == 4, 'INCOMPLETE_SOURCE_DOMAIN')
    require(np.max(abs(d.zbar-(1/d.a-1))) < 1e-12, 'REDSHIFT_SCALE_MISMATCH')
    require(np.min(d[OBS[:5]].to_numpy()) >= 0, 'NEGATIVE_FRACTION')
    require(np.max(d[OBS[:5]].to_numpy()) <= 1, 'FRACTION_ABOVE_ONE')
    require(np.min(d.nH_proper_cm3) > 0 and np.min(d.temperature_K) > 0, 'NONPOSITIVE_GAS')
    e = d.x_HII + FHE*(d.x_HeII + 2*d.x_HeIII)
    residuals = {
        'hydrogen_sum': float(np.max(abs(d.x_HI+d.x_HII-1))),
        'helium_sum': float(np.max(abs(d.x_HeI+d.x_HeII+d.x_HeIII-1))),
        'electron_charge_per_H': float(np.max(abs(d.ne_proper_cm3/d.nH_proper_cm3-e))),
        'comoving_hydrogen_relative': float(np.max(abs(d.nH_proper_cm3*d.a**3 /
                                                    (d.nH_proper_cm3.iloc[0]*d.a.iloc[0]**3)-1)))
    }
    require(max(residuals.values()) <= 1e-12, 'CHARGE_NUCLEI_OR_DENSITY')
    return residuals


def load_case(root, spec):
    p = Path(root)/spec['relative_input']
    require(p.is_file(), 'MISSING_HISTORY')
    require(p.stat().st_size == spec['bytes'], 'SOURCE_SIZE')
    require(sha(p) == spec['sha256'], 'SOURCE_HASH')
    d = pd.read_csv(p, usecols=COLS, float_precision='round_trip')
    checks = validate_frame(d, spec)
    d['ln_a'] = np.log(d.a)
    d['xe_per_H'] = d.ne_proper_cm3/d.nH_proper_cm3
    denom = 1+4*FHE
    for suffix in ['HI', 'HII']:
        d['Y_'+suffix] = d['x_'+suffix]/denom
    for suffix in ['HeI', 'HeII', 'HeIII']:
        d['Y_'+suffix] = FHE*d['x_'+suffix]/denom
    d['Y_e'] = d.xe_per_H/denom
    checks['baryon_number_Y'] = float(np.max(abs(d.Y_HI+d.Y_HII+4*(d.Y_HeI+d.Y_HeII+d.Y_HeIII)-1)))
    require(checks['baryon_number_Y'] <= 1e-12, 'BARYON_Y_NORMALIZATION')
    return d, checks


def field_at(d, ln_a, field):
    return interp(ln_a, d.ln_a.to_numpy(), d[field].to_numpy())


def write_csv(d, path):
    path = Path(path)
    content = d.to_csv(index=False, float_format='%.17g').encode()
    if path.suffix == '.gz':
        with path.open('wb') as f:
            with gzip.GzipFile(filename='', mode='wb', fileobj=f, mtime=0) as z:
                z.write(content)
    else:
        path.write_bytes(content)


def milestone(d, spec, level):
    x = d.x_HII.to_numpy()
    cross = np.flatnonzero((x[:-1] < level) & (x[1:] >= level))
    base = {'case': spec['id'], 'q_ref': spec['q_ref'], 'x_HII_level': level,
            'coordinate': 'FIRST_UPWARD_SAVED_ROWS_LINEAR_LNA',
            'evolution_uncertainty': 'UNKNOWN_AX11'}
    if not len(cross):
        return {**base, 'status': 'NOT_REACHED'}
    i = int(cross[0]); f = float((level-x[i])/(x[i+1]-x[i]))
    lo, hi = d.iloc[i], d.iloc[i+1]
    ln_a = (1-f)*lo.ln_a+f*hi.ln_a
    t = (1-f)*lo.time_s+f*hi.time_s
    # Independent interpolation family on four nearby points. Diagnostic only.
    left, right = max(0, i-1), min(len(d), i+3)
    pchip = PchipInterpolator(d.ln_a.iloc[left:right], x[left:right])
    root = brentq(lambda a: float(pchip(a))-level, lo.ln_a, hi.ln_a,
                  xtol=5e-15, rtol=1e-14)
    t_alt = float(field_at(d, root, 'time_s'))
    return {**base, 'status': 'REACHED', 'lower_row': i, 'upper_row': i+1,
            'lower_x_HII': float(lo.x_HII), 'upper_x_HII': float(hi.x_HII),
            'lower_time_s': float(lo.time_s), 'upper_time_s': float(hi.time_s),
            'lower_zbar': float(lo.zbar), 'upper_zbar': float(hi.zbar),
            'bracket_width_years': float((hi.time_s-lo.time_s)/YEAR_S),
            'zbar': float(np.exp(-ln_a)-1), 'time_s': float(t),
            'elapsed_Myr': float(t/YEAR_S/1e6),
            'temperature_K': float((1-f)*lo.temperature_K+f*hi.temperature_K),
            'pchip_zbar': float(np.exp(-root)-1),
            'pchip_time_s': t_alt,
            'pchip_minus_linear_years': float((t_alt-t)/YEAR_S)}


def hf(a):
    return H0_S*np.sqrt(OMEGA_R/a**4+OMEGA_M/a**3+OMEGA_L)


def clock_offset(q, a):
    def stable(u):
        aa = math.exp(u)
        h = float(hf(aa)); s = q*float(hf(A_INITIAL))*(A_INITIAL/aa)**3
        r = s/h; v = math.sqrt(1+r*r)
        return -r*r/(h*v*(v+1))
    return quad(stable, math.log(A_INITIAL), math.log(a), epsabs=1e-4,
                epsrel=2e-12, limit=100)


def thomson(d, grid, case):
    t = d.time_s.to_numpy(); ne = d.ne_proper_cm3.to_numpy()
    inc = C_CM_S*SIGMA_T_CM2*0.5*(ne[1:]+ne[:-1])*np.diff(t)
    require(np.all(inc >= 0) and np.isfinite(inc).all(), 'THOMSON_INCREMENT')
    tail = np.concatenate([np.cumsum(inc[::-1])[::-1], [0.]])
    total = math.fsum(float(v) for v in inc)
    # Probability of one or more collisions in a cell, surviving its future tail.
    masses = np.exp(-tail[1:])*(-np.expm1(-inc))
    mass = math.fsum(float(v) for v in masses)
    p = -math.expm1(-total)
    require(abs(mass-p) <= 3e-14, 'CONDITIONAL_VISIBILITY_MASS')
    frame = pd.DataFrame({'case': case, 'a': np.exp(grid), 'zbar': np.exp(-grid)-1,
                          'time_s': field_at(d, grid, 'time_s'),
                          'proper_ne_cm3': field_at(d, grid, 'ne_proper_cm3'),
                          'xe_per_H': field_at(d, grid, 'xe_per_H'),
                          'tau_to_conditional_z4_receiver': interp(grid, d.ln_a, tail)})
    frame['Gamma_T_s_inv'] = C_CM_S*SIGMA_T_CM2*frame.proper_ne_cm3
    frame['g_conditional_per_s'] = frame.Gamma_T_s_inv*np.exp(-frame.tau_to_conditional_z4_receiver)
    # Native-time trapezoid vs native-ln(a) trapezoid is a method sensitivity,
    # not a rigorous error bar on the coupled history.
    ln_integrand = C_CM_S*SIGMA_T_CM2*ne/d.H_per_s.to_numpy()
    tau_lna = float(np.trapezoid(ln_integrand, d.ln_a.to_numpy()))
    return frame, {'tau_z20_to_z4': total, 'tau_lna_trapezoid': tau_lna,
                   'time_minus_lna_quadrature': total-tau_lna,
                   'conditional_scattering_probability': p,
                   'conditional_visibility_mass': mass,
                   'visibility_mass_residual': mass-p,
                   'observer_tail_tau': None, 'observer_total_tau': None,
                   'proper_electron_rows_consumed': len(d),
                   'scope': 'NON_TILTED_TIME_SURFACES_CONDITIONAL_Z4_RECEIVER',
                   'evolution_and_quadrature_error_bound': None}


def run(inputs, output):
    start = time.monotonic(); cpu = time.process_time()
    output = Path(output)
    require(not output.exists(), 'OUTPUT_EXISTS')
    output.mkdir(parents=True)
    manifest = json.loads((HERE/'INPUT_MANIFEST.json').read_text())
    specs = manifest['cases']; data = {}; checks = {}
    for spec in specs:
        data[spec['id']], checks[spec['id']] = load_case(inputs, spec)
    ref = data['ZERO']
    grid = np.linspace(ref.ln_a.iloc[0], ref.ln_a.iloc[-1], 1001)
    common_end = min(d.time_s.iloc[-1] for d in data.values())
    ref_end = float(interp(common_end, ref.time_s.to_numpy(), ref.ln_a.to_numpy()))
    ref_time_grid_lna = np.linspace(ref.ln_a.iloc[0], ref_end, 1001)
    times = field_at(ref, ref_time_grid_lna, 'time_s')
    abundance, zcomp, tcomp, optical, clocks = [], [], [], [], []
    milestones, metrics, optical_summary = [], {}, {}
    for spec in specs:
        case, q = spec['id'], spec['q_ref']; d = data[case]
        frame = pd.DataFrame({'case': case, 'q_ref': q, 'a': np.exp(grid),
                              'zbar': np.exp(-grid)-1,
                              'time_s': field_at(d, grid, 'time_s')})
        for field in OBS+YS+['nH_proper_cm3', 'ne_proper_cm3', 'b']:
            frame[field] = field_at(d, grid, field)
        abundance.append(frame)
        for level in [.1, .5, .9]:
            milestones.append(milestone(d, spec, level))
        vis, optical_summary[case] = thomson(d, grid, case)
        optical.append(vis)
        for u in grid[::40]:
            aa = float(np.exp(u)); analytic, err = clock_offset(q, aa)
            saved = float(field_at(d, u, 'time_s')-field_at(ref, u, 'time_s'))
            clocks.append({'case': case, 'q_ref': q, 'a': aa, 'zbar': 1/aa-1,
                           'saved_offset_s': saved, 'independent_offset_s': analytic,
                           'saved_minus_independent_s': saved-analytic,
                           'quadrature_error_estimate_s': err})
        if case == 'ZERO':
            continue
        zframe = pd.DataFrame({'case': case, 'q_ref': q, 'a': np.exp(grid),
                              'zbar': np.exp(-grid)-1,
                              'candidate_time_s': field_at(d, grid, 'time_s'),
                              'reference_time_s': field_at(ref, grid, 'time_s')})
        candidate_lna = interp(times, d.time_s.to_numpy(), d.ln_a.to_numpy())
        tframe = pd.DataFrame({'case': case, 'q_ref': q, 'elapsed_time_s': times,
                              'candidate_a': np.exp(candidate_lna),
                              'reference_a': np.exp(ref_time_grid_lna),
                              'candidate_zbar': np.exp(-candidate_lna)-1,
                              'reference_zbar': np.exp(-ref_time_grid_lna)-1})
        metrics[case] = {}
        for field in OBS:
            xq, x0 = field_at(d, grid, field), field_at(ref, grid, field)
            zframe[field+'_candidate'] = xq; zframe[field+'_reference'] = x0
            zframe[field+'_delta_at_fixed_a'] = xq-x0
            xc = field_at(d, candidate_lna, field)
            xr = field_at(ref, ref_time_grid_lna, field)
            xr_at_c = field_at(ref, candidate_lna, field)
            delta, da, clock = xc-xr, xc-xr_at_c, xr_at_c-xr
            residue = delta-da-clock
            tol = 2e-8 if field == 'temperature_K' else 2e-12
            require(np.max(abs(residue)) <= tol, 'COORDINATE_DECOMPOSITION')
            for suffix, values in [('candidate', xc), ('reference', xr),
                                   ('delta_at_fixed_t', delta),
                                   ('fixed_a_at_candidate_a', da), ('clock_displacement', clock)]:
                tframe[field+'_'+suffix] = values
            iz, it = int(np.argmax(abs(xq-x0))), int(np.argmax(abs(delta)))
            metrics[case][field] = {
                'fixed_a_sampled_max_abs': float(abs(xq[iz]-x0[iz])),
                'fixed_a_signed_at_max': float(xq[iz]-x0[iz]),
                'fixed_a_zbar_at_max': float(np.exp(-grid[iz])-1),
                'fixed_t_sampled_max_abs': float(abs(delta[it])),
                'fixed_t_signed_at_max': float(delta[it]),
                'fixed_t_elapsed_Myr_at_max': float(times[it]/YEAR_S/1e6),
                'fixed_a_term_at_fixed_t_peak': float(da[it]),
                'clock_term_at_fixed_t_peak': float(clock[it]),
                'decomposition_max_abs_residual': float(np.max(abs(residue))),
                'norm_scope': '1001_SAMPLE_MAX_NOT_CONTINUOUS_SUPREMUM',
                'evolution_refinement_uncertainty': 'UNKNOWN_AX11'}
        zcomp.append(zframe); tcomp.append(tframe)
    mil = pd.DataFrame(milestones)
    for field, outname in [('time_s', 'delta_time_s_from_ZERO'), ('zbar', 'delta_zbar_from_ZERO'),
                           ('pchip_time_s', 'delta_pchip_time_s_from_ZERO')]:
        reference = mil[mil['case']=='ZERO'].set_index('x_HII_level')[field]
        mil[outname] = mil[field]-mil.x_HII_level.map(reference)
    mil['delta_time_years_from_ZERO'] = mil.delta_time_s_from_ZERO/YEAR_S
    mil['paired_interpolation_sensitivity_years'] = (
        mil.delta_pchip_time_s_from_ZERO-mil.delta_time_s_from_ZERO)/YEAR_S
    outputs = {'abundances.csv.gz': pd.concat(abundance, ignore_index=True),
               'comparison_zbar.csv.gz': pd.concat(zcomp, ignore_index=True),
               'comparison_time.csv.gz': pd.concat(tcomp, ignore_index=True),
               'milestones.csv': mil,
               'thomson_segment.csv.gz': pd.concat(optical, ignore_index=True),
               'clock_check.csv': pd.DataFrame(clocks)}
    for name, frame in outputs.items():
        write_csv(frame, output/name)
    endpoint = {case: {'elapsed_Myr': float(d.time_s.iloc[-1]/YEAR_S/1e6),
                       **{f: float(d[f].iloc[-1]) for f in OBS+YS}}
                for case, d in data.items()}
    summary = {'schema': 'rei.axbi.actual-history-consumption.v1',
               'status': 'SAVED_CONDITIONAL_MODEL_PHYSICAL_DATA_GENERATED',
               'central_completed': 28, 'central_total': 88, 'canonical_delta': 0,
               'original_rows_consumed': sum(len(d) for d in data.values()),
               'new_ode_trajectories': 0, 'represented_domain_zbar': [20., 4.],
               'proper_time_common_end_s': float(common_end),
               'time_origin': 'ELAPSED_SINCE_EACH_MODELS_ZBAR20_NOT_COSMIC_AGE',
               'input_hashes_verified': {s['id']: s['sha256'] for s in specs},
               'source_checks': checks, 'responses': metrics, 'endpoints': endpoint,
               'rec_segment_consumer': optical_summary,
               'max_saved_clock_offset_disagreement_s': max(abs(x['saved_minus_independent_s']) for x in clocks),
               'sigma_T_cm2_source_pinned': SIGMA_T_CM2, 'c_cm_s': C_CM_S,
               'output_rows': {name: len(frame) for name, frame in outputs.items()},
               'output_sha256': {name: sha(output/name) for name in outputs},
               'consumer_code_sha256': sha(__file__),
               'physical_accuracy_admission': 'UNRESOLVED_AX11_AX12',
               'all_five_signed_cases_complete': False,
               'source_IC_geometry_error_budget': 'NOT_ESTABLISHED_BY_POSTPROCESSING',
               'private_source_arrays_published': False}
    (output/'SUMMARY.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    runtime = {'wall_s': time.monotonic()-start, 'cpu_s': time.process_time()-cpu,
               'python': platform.python_version(), 'numpy': np.__version__,
               'pandas': pd.__version__, 'scipy': scipy.__version__,
               'optimized_python': not __debug__, 'exit_status': 0}
    (output/'RUNTIME.json').write_text(json.dumps(runtime, indent=2)+'\n')
    print(json.dumps({'status': summary['status'], 'rows_consumed': summary['original_rows_consumed'],
                      'output_rows': summary['output_rows'], 'runtime': runtime}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--inputs', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    run(args.inputs, args.output)
