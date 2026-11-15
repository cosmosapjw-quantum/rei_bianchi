"""Consume an admitted complete +0.01 history; never evolve or replay four cases.

The four-case approximation summary and PR374 sample products remain immutable.
All output is provisional until an independent review consumes the actual data.
"""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_simpson

from background_stress import C, G, KB, H0, OM, OR, OL, OGAMMA, AI, angular_moments, background
from full_history_diagnostic import COUPLING, EV_J, integrate, sha

FOUR_SHA = '7d37d82d0dd090c63097770827e429ae09b0f0d5d4651eea206ed2841cb2c8ef'
DONOR_SHA = {
    'physics_consumer.py': '36ab1556010cd182790e924b1042227b36496c7a17d6d55ddfbff5935a58cfb8',
    'results/comparison_zbar.csv.gz': '09707da49b7d0b7d8cf4839d83fed8d8acdc78eb7a362c9ba6fd08ef11ae01fa',
    'results/comparison_time.csv.gz': '92080417a743fd10794107c26e1e51e69b77e36d593e5c94c57a5e0c183445bd',
    'results/milestones.csv': '27df2c04cd6a278efaffb3cccb797055c49500693c68ac7f0290fcc44cece638',
    'results/abundances.csv.gz': 'a568581b7aabbbe3d052d494b283992a90f6ac91ef4e8d289c17632ed99cd3c9',
}
FHE = .2454 / (4 * (1 - .2454))
EXTRA = ['J0_photon_u_eV_per_H', 'J1_photon_u_eV_per_H', 'J2_photon_u_eV_per_H', 'photon_u_eV_per_H',
         'photon_n_per_H','Gamma_HI_per_s','Gamma_HeI_per_s','Gamma_HeII_per_s']


def require(ok, code):
    if not bool(ok):
        raise ValueError(code)


def admit(manifest, history):
    """Fail closed on incomplete, wrong-identity, or uncomposed history."""
    m = json.loads(manifest.read_text())
    require(m.get('schema') == 'rei.axbi.plus_complete_composition.v1', 'COMPOSITION_SCHEMA')
    a = m.get('admission', {})
    require(a.get('status') == 'COMPLETE_COMPOSED_HISTORY', 'ENDPOINT_NOT_ADMITTED')
    require(a.get('case_id') == 'SHEAR_PLUS' and a.get('q_ref') == .01, 'WRONG_CASE')
    require(a.get('zbar_start') == 20 and a.get('zbar_end') == 4, 'WRONG_DOMAIN')
    require(all(a.get(k) is True for k in ['boundary_checks_passed', 'terminal_checkpoint_matches',
                                         'original_physics_identity_verified']), 'COMPOSITION_CHECKS')
    require(isinstance(a.get('rows'), int) and a['rows'] >= 3, 'ROW_COUNT_MISSING')
    require(a.get('native_terminal_accepted') == a['rows'] - 1, 'ACCEPTED_ROWS_MISMATCH')
    require(history.stat().st_size == a.get('bytes'), 'SOURCE_SIZE')
    require(sha(history) == a.get('sha256'), 'SOURCE_SHA')
    return a


def load_donor(owner):
    for name, digest in DONOR_SHA.items():
        require(sha(owner / name) == digest, 'DONOR_SHA:' + name)
    spec = importlib.util.spec_from_file_location('frozen_pr374_consumer', owner / 'physics_consumer.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_fifth(history, admission, donor):
    d = pd.read_csv(history, usecols=list(dict.fromkeys(donor.COLS + EXTRA)), float_precision='round_trip')
    checks = donor.validate_frame(d, {'id': 'SHEAR_PLUS', 'q_ref': .01, 'rows': admission['rows']})
    require(np.isfinite(d[EXTRA].to_numpy()).all(), 'NONFINITE_RADIATION')
    d['ln_a'] = np.log(d.a)
    d['xe_per_H'] = d.ne_proper_cm3 / d.nH_proper_cm3
    for suffix in ['HI', 'HII']:
        d['Y_' + suffix] = d['x_' + suffix] / (1 + 4 * FHE)
    for suffix in ['HeI', 'HeII', 'HeIII']:
        d['Y_' + suffix] = FHE * d['x_' + suffix] / (1 + 4 * FHE)
    d['Y_e'] = d.xe_per_H / (1 + 4 * FHE)
    checks['baryon_number_Y'] = float(np.max(abs(d.Y_HI+d.Y_HII+4*(d.Y_HeI+d.Y_HeII+d.Y_HeIII)-1)))
    require(checks['baryon_number_Y'] <= 1e-12, 'BARYON_Y_NORMALIZATION')
    return d, checks


def diagnostic(d, digest):
    """Same physical reduction as the reviewed four-case implementation."""
    a, b, H, s, t = (d[k].to_numpy() for k in ['a', 'b', 'H_per_s', 's_per_s', 'time_s'])
    locked_H, locked_s = background(a, .01)
    herr = float(np.max(abs(H / locked_H - 1)))
    serr = float(np.max(abs(s / locked_s - 1)))
    require(herr <= 1e-12 and serr <= 1e-12, 'LOCKED_BACKGROUND_MISMATCH')
    M, F = angular_moments(b, 16)
    nH, ne = d.nH_proper_cm3.to_numpy() * 1e6, d.ne_proper_cm3.to_numpy() * 1e6
    uion = nH * d.J0_photon_u_eV_per_H.to_numpy() * EV_J
    pion = nH * d.J2_photon_u_eV_per_H.to_numpy() * EV_J
    uref = H0**2 * OR / (COUPLING * a**4)
    prad = uref * F
    uth = 1.5 * KB * d.temperature_K.to_numpy() * (nH * (1 + FHE) + ne)
    total_energy = H**2 / COUPLING
    dsrad, dsion, dstotal = (integrate(a, H, p) for p in [prad, pion, prad + pion])
    dstime = cumulative_simpson(a**3 * COUPLING * (prad + pion), x=t, initial=0) / (a**3 * H)
    hf2 = H0**2 * (OR/a**4 + OM/a**3 + OL)
    extra = (uion + uth + abs(uref * (M - 1))) / (hf2 / COUPLING)
    extra_total = extra * hf2 / H**2
    imax, emax = int(np.argmax(abs(dstotal))), int(np.argmax(extra))
    M32, F32 = angular_moments(b[::311], 32)
    r = {
        'rows': len(d), 'input_sha256': digest, 'q_ref': .01,
        'max_abs_total_delta_s_over_H': float(np.max(abs(dstotal))),
        'signed_total_delta_s_over_H_at_peak': float(dstotal[imax]),
        'stress_peak_zbar': float(1/a[imax] - 1),
        'max_abs_background_delta_s_over_H': float(np.max(abs(dsrad))),
        'max_abs_CMB_delta_s_over_H': float(np.max(abs(dsrad)) * OGAMMA/OR),
        'max_abs_ionizing_delta_s_over_H': float(np.max(abs(dsion))),
        'max_abs_total_delta_s_over_s': float(np.max(abs(dstotal * H/s))),
        'max_extra_energy_over_FLRW_background_source_comparator': float(extra[emax]),
        'max_extra_energy_over_total': float(np.max(extra_total)),
        'energy_peak_zbar': float(1/a[emax] - 1),
        'max_ionizing_plus_thermal_over_total': float(np.max((uion+uth)/total_energy)),
        'max_ionizing_over_total': float(np.max(uion/total_energy)),
        'max_thermal_over_total': float(np.max(uth/total_energy)),
        'max_background_energy_correction_over_total': float(np.max(abs(uref*(M-1))/total_energy)),
        'max_Thomson_cooling_coefficient_fractional_change': float(np.max(abs(M-1))),
        'total_shear_check_original_target': 1e-4, 'total_energy_check_original_target': 1e-4,
        'total_shear_status': 'BELOW_TARGET' if np.max(abs(dstotal)) < 1e-4 else 'EXCEEDS_TARGET',
        'total_energy_status': 'BELOW_TARGET' if np.max(extra) < 1e-4 else 'EXCEEDS_TARGET',
        'source_H_locked_background_max_relative_error': herr,
        'source_s_locked_background_max_relative_error': serr,
        'quadrature_GL16_vs_GL32_sample_error': float(max(np.max(abs(M32-M[::311])), np.max(abs(F32-F[::311])))),
        'separate_vs_joint_integral_max_abs': float(np.max(abs(dstotal-dsrad-dsion))),
        'proper_time_vs_lna_integral_max_abs': float(np.max(abs(dstotal-dstime))),
        'source_J0_vs_photon_u_max_eV_per_H': float(np.max(abs(d.J0_photon_u_eV_per_H-d.photon_u_eV_per_H))),
        'original_evolution_error_bound': None,
        'physical_scope': 'perturbative forcing on original saved metric; no coupled feedback',
    }
    ids = np.unique(np.r_[np.linspace(0,len(d)-1,1001).astype(int), imax, emax])
    sample = pd.DataFrame({'original_row': ids, 'a': a[ids], 'zbar': 1/a[ids]-1,
        'background_delta_s_over_H': dsrad[ids], 'ionizing_delta_s_over_H': dsion[ids],
        'total_delta_s_over_H': dstotal[ids], 'extra_energy_over_FLRW_background': extra[ids]})
    return r, sample


def extrema(values, coordinate):
    i = int(np.argmax(abs(values)))
    return {'max_abs': float(abs(values[i])), 'signed_at_peak': float(values[i]),
            'coordinate_at_peak': float(coordinate[i])}


def parity(plus, minus, zero):
    return (plus-minus)/2, (plus+minus)/2-zero


def responses(d, donor, owner):
    zold = pd.read_csv(owner/'results/comparison_zbar.csv.gz', float_precision='round_trip')
    told = pd.read_csv(owner/'results/comparison_time.csv.gz', float_precision='round_trip')
    modes, summaries = {}, {}
    # The exact published sample coordinates and reference values are reused.
    for mode, old in [('fixed_a', zold), ('fixed_t', told)]:
        oldminus = old[old['case']=='SHEAR_MINUS'].reset_index(drop=True)
        if mode == 'fixed_a':
            grid = np.linspace(np.log(AI), np.log(.2), len(oldminus))
            require(np.max(abs(np.exp(grid)-oldminus.a)) <= 2e-16, 'CANONICAL_GRID')
            coordinate = oldminus.zbar.to_numpy()
            query = grid
        else:
            coordinate = oldminus.elapsed_time_s.to_numpy()
            query = donor.interp(coordinate, d.time_s, d.ln_a)
        frame = pd.DataFrame({'coordinate': coordinate})
        if mode == 'fixed_a':
            frame['zbar'] = coordinate
            frame['candidate_zbar'] = coordinate
            frame['reference_zbar'] = coordinate
            frame['candidate_time_s'] = donor.field_at(d,query,'time_s')
            frame['reference_time_s'] = oldminus.reference_time_s.to_numpy()
        else:
            frame['elapsed_time_s'] = coordinate
            frame['candidate_time_s'] = coordinate
            frame['reference_time_s'] = coordinate
            frame['candidate_zbar'] = np.exp(-query)-1
            frame['reference_zbar'] = oldminus.reference_zbar.to_numpy()
        metrics = {}
        for field in donor.OBS:
            plus = donor.field_at(d, query, field)
            minus = oldminus[field+'_candidate'].to_numpy()
            zero = oldminus[field+'_reference'].to_numpy()
            for oldcase in ['SHEAR_HALF_PLUS','SHEAR_HALF_MINUS']:
                require(np.array_equal(old[old['case']==oldcase][field+'_reference'].to_numpy(),zero),
                        'DONOR_REFERENCE_MISMATCH')
            odd, even = parity(plus, minus, zero)
            hp = old[old['case']=='SHEAR_HALF_PLUS'][field+'_candidate'].to_numpy()
            hm = old[old['case']=='SHEAR_HALF_MINUS'][field+'_candidate'].to_numpy()
            ho, he = parity(hp, hm, zero)
            for label, values in [('plus',plus), ('minus',minus), ('zero',zero),
                    ('plus_response',plus-zero), ('odd_q001',odd), ('even_q001',even),
                    ('odd_q0005',ho), ('even_q0005',he),
                    ('odd_linear_scaling_residual',odd-2*ho),
                    ('even_quadratic_scaling_residual',even-4*he)]:
                frame[field+'_'+label] = values
            metrics[field] = {k: extrema(v,coordinate) for k,v in [
                ('plus_response',plus-zero), ('odd_q001',odd), ('even_q001',even),
                ('odd_q0005',ho), ('even_q0005',he),
                ('odd_linear_scaling_residual',odd-2*ho), ('even_quadratic_scaling_residual',even-4*he)]}
            floor = .01 if field=='temperature_K' else (1+3*FHE)*1e-7 if field=='xe_per_H' else 1e-7
            metrics[field]['original_response_floor'] = floor
            metrics[field]['above_floor_is_not_resolution'] = True
            metrics[field]['scientific_resolution'] = 'UNRESOLVED_AX11'
        modes[mode] = frame
        summaries[mode] = metrics
    # Milestones use the actual native + history and inherited native brackets.
    mil = pd.DataFrame([donor.milestone(d, {'id':'SHEAR_PLUS','q_ref':.01}, lev) for lev in [.1,.5,.9]])
    oldmil = pd.read_csv(owner/'results/milestones.csv',float_precision='round_trip')
    for refcase in ['ZERO','SHEAR_MINUS']:
        ref = oldmil[oldmil['case']==refcase].set_index('x_HII_level')
        for field in ['time_s','zbar','pchip_time_s']:
            if field not in mil:mil[field]=np.nan
            mil['delta_'+field+'_from_'+refcase] = mil[field]-mil.x_HII_level.map(ref[field])
    return modes, summaries, mil


def cohort_diagnostic(d, metrics):
    """Instantaneous saved absorption residence estimate, never a response bound."""
    absorbed=(1-d.x_HII)*d.Gamma_HI_per_s+FHE*(d.x_HeI*d.Gamma_HeI_per_s+d.x_HeII*d.Gamma_HeII_per_s)
    n=d.photon_n_per_H.to_numpy()
    lam=np.full(len(d),np.nan)
    np.divide(absorbed.to_numpy(),n,out=lam,where=n>0)
    valid=(lam>0)&np.isfinite(lam)
    chi=np.full(len(d),np.nan)
    np.divide(abs(d.s_per_s.to_numpy()),lam,out=chi,where=valid)
    peaks={}
    for field in ['x_HII','x_HeII','temperature_K']:
        peaks[field]={}
        for component in ['plus_response','odd_q001','even_q001']:
            z=metrics['fixed_a'][field][component]['coordinate_at_peak']
            u=np.log(1/(1+z));i=int(np.argmin(abs(d.ln_a.to_numpy()-u)))
            peaks[field][component]={'response_sample_zbar':z,'nearest_native_row':i,
                'native_zbar':float(d.zbar.iloc[i]),'absorption_rate_per_H_s_inv':float(absorbed.iloc[i]),
                'photon_n_per_H':float(n[i]),'lambda_abs_s_inv':float(lam[i]) if valid[i] else None,
                'chi_abs_s_over_lambda':float(chi[i]) if valid[i] else None,
                'chi_cubed':float(chi[i]**3) if valid[i] else None}
    return {'schema':'rei.axbi.saved-cohort-residence-diagnostic.v1',
        'definition':'lambda_abs=[(1-xHII)*GammaHI+fHe*(xHeI*GammaHeI+xHeII*GammaHeII)]/N_gamma_per_H; chi=abs(s)/lambda_abs',
        'represented_native_rows':len(d),'valid_rows':int(np.sum(valid)),
        'max_chi_over_valid_saved_nodes':float(np.max(chi[valid])) if np.any(valid) else None,
        'at_response_peaks':peaks,
        'interpretation':'Under a quasi-stationary absorption-dominated residence model only, delta_b~s/lambda_abs and odd scalar angular moments may start cubic.',
        'limits':['Source evolution, redshift escape, energy-dependent lifetimes and nonlocal residence-time distributions are not replaced by this instantaneous ratio.',
                  'chi_cubed is not an abundance coefficient, error estimate, or bound; numerical suppression still requires AX11 discrimination.'],
        'new_IVPs':0}


def run(args):
    started = time.perf_counter()
    require(not args.out.exists(), 'OUTPUT_EXISTS')
    require(not args.full_abundance_out.exists(), 'FULL_ABUNDANCE_OUTPUT_EXISTS')
    admission = admit(args.composition, args.history)
    require(sha(args.four_summary)==FOUR_SHA, 'FOUR_RESULT_SHA')
    four = json.loads(args.four_summary.read_text())
    donor = load_donor(args.owner)
    d, checks = load_fifth(args.history, admission, donor)
    fifth, diagnostic_sample = diagnostic(d, admission['sha256'])
    modes, metrics, milestones = responses(d, donor, args.owner)
    cohort=cohort_diagnostic(d,metrics)
    # Complete native normalized rows are a private source product. The public
    # package contains their hash/row/column contract and an inspection sample.
    full_columns=['case_id','q_ref','a','zbar','time_s','b','H_per_s','s_per_s']+donor.OBS+donor.YS+['nH_proper_cm3','ne_proper_cm3']
    full=d[full_columns].copy()
    full['normalization_registry']='X:element_fraction;Y:n_species/(nH+4nHe);xe:ne/nH;Y_e:ne/(nH+4nHe)'
    args.full_abundance_out.parent.mkdir(parents=True,exist_ok=True)
    temporary=args.full_abundance_out.with_name(args.full_abundance_out.name+'.partial')
    full.to_csv(temporary,index=False,float_format='%.17g',compression={'method':'gzip','compresslevel':1,'mtime':0})
    temporary.replace(args.full_abundance_out)
    full_manifest={'filename':args.full_abundance_out.name,'sha256':sha(args.full_abundance_out),
        'bytes':args.full_abundance_out.stat().st_size,'rows':len(full),'columns':list(full.columns),
        'scope':'complete time-ordered normalized native +0.01 history; no resampling',
        'source_history_sha256':admission['sha256'],'source_composition_sha256':sha(args.composition),
        'normalization_checks':checks}
    args.out.mkdir(parents=True)
    dump = lambda name,data: (args.out/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    dump('FIFTH_DIAGNOSTIC.json',fifth)
    dump('FIFTH_FULL_ABUNDANCE_MANIFEST.json',full_manifest)
    dump('COHORT_RESIDENCE_DIAGNOSTIC.json',cohort)
    donor.write_csv(diagnostic_sample,args.out/'fifth_diagnostic_sample.csv.gz')
    for name,frame in modes.items():donor.write_csv(frame,args.out/('responses_'+name+'.csv.gz'))
    donor.write_csv(milestones,args.out/'fifth_milestones.csv')
    grid=np.linspace(np.log(AI),np.log(.2),1001)
    abundance=pd.DataFrame({'case':'SHEAR_PLUS','q_ref':.01,'a':np.exp(grid),
                           'zbar':np.exp(-grid)-1,'time_s':donor.field_at(d,grid,'time_s')})
    for field in donor.OBS+donor.YS+['nH_proper_cm3','ne_proper_cm3','b']:
        abundance[field]=donor.field_at(d,grid,field)
    donor.write_csv(abundance,args.out/'fifth_abundances.csv.gz')
    old_abundance=pd.read_csv(args.owner/'results/abundances.csv.gz',float_precision='round_trip')
    donor.write_csv(pd.concat([old_abundance,abundance],ignore_index=True),args.out/'five_case_abundances.csv.gz')
    merged = {**four, 'schema':'rei.axbi.five-history-incremental-diagnostic.v1',
        'cases': {**four['cases'],'SHEAR_PLUS':fifth},
        'source_origin':'Original four PR374 cases plus separately admitted native checkpoint continuation',
        'runtime_wall_s':time.perf_counter()-started,
        'rows_consumed':len(d), 'rows_reused_without_reduction':four['rows_consumed'],
        'represented_rows':len(d)+four['rows_consumed'],
        'four_case_summary_sha256':FOUR_SHA,
        'composition_manifest_sha256':sha(args.composition),
        'status':'FIVE_REPRESENTED_CASES_FORCED_FIXED_BACKGROUND_DIAGNOSTICS_PENDING_REVIEW',
        'full_goal_scientific_admission':'UNRESOLVED_AX11_AX12',
        'AX08_admission':'PENDING_OWNER_AND_ACTUAL_FIFTH_CASE_REVIEW',
        'canonical_DAG_delta':0, 'new_IVPs':0,
        'IVP_count_scope':'This consumer starts zero IVPs; its new source is the separately authorized native checkpoint continuation executed by the geometry owner.'}
    merged.pop('canonical_parent_status',None)
    dump('FIVE_CASE_APPROXIMATION_SUMMARY.json',merged)
    response_summary={'schema':'rei.axbi.fifth-native-response.v1',
        'status':'SAVED_HISTORY_ESTIMATES_PENDING_REVIEW_AND_AX11_RESOLUTION',
        'sample_scope':'1001 original PR374 coordinates per mode; not continuous extrema',
        'parity_definitions':{'odd':'(X(+q)-X(-q))/2','even':'(X(+q)+X(-q))/2-X(0)'},
        'scaling_residuals':'O(.01)-2*O(.005); E(.01)-4*E(.005); diagnostic only, no Taylor-order proof',
        'coordinate_modes':{'fixed_a':'same a / zbar','fixed_t':'same elapsed proper seconds since each model zbar20'},
        'responses':metrics,'checks':checks,'donor_sha256':DONOR_SHA,
        'new_IVPs':0,'original_four_reprocessed':False,
        'abundance_error_bound':None,'AX11':'UNRESOLVED','AX12':'UNRESOLVED',
        'output_sha256':{p.name:sha(p) for p in args.out.iterdir() if p.is_file()},
        'runtime_wall_s':time.perf_counter()-started}
    dump('FIFTH_RESPONSE_SUMMARY.json',response_summary)
    return {'rows_new':len(d),'rows_reused':four['rows_consumed'],
            'status':response_summary['status'],'wall_s':time.perf_counter()-started}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for flag in ['history','composition','owner','four-summary','out','full-abundance-out']:
        p.add_argument('--'+flag,type=Path,required=True)
    print(json.dumps(run(p.parse_args()),indent=2))
