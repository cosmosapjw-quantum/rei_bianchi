"""Read-only saved-state diagnostics. No IVP or new state interpolation."""
from pathlib import Path
import json
import sys
import time
import resource
import numpy as np

START = time.monotonic()
BASE = Path('/workspace/scratch/d5baa30c266d/rei_isotope/research/rei_angular_thermochemistry_20261023')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'code'))
from angular_model import Reduced, CT, NN, VGRAD

report = {'scope': 'saved NPZ/JSON only; no IVP; nearest saved states, no state interpolation',
          'targets_eta': [.1, .2, .4, .45, .7, 1.], 'cases': {}}
with np.load(BASE / 'inputs/background/grid044_history.npz', allow_pickle=False) as bg:
    back = {'fields': {k: {'shape': list(bg[k].shape), 'dtype': str(bg[k].dtype)} for k in bg.files}}
    for key in ['b', 'n', 's', 'H', 'nH_ref_cm3']:
        if key in bg:
            a = bg[key]
            back[key] = {'min': float(a.min()), 'max': float(a.max()), 'max_abs': float(abs(a).max())}
    for key in ['n', 's', 'nH_ref_cm3']:
        if key in bg:
            a = abs(bg[key] / bg['H'])
            i = int(a.argmax())
            back[f'max_abs_{key}_over_H'] = {'value': float(a[i]), 'eta': float(bg['eta'][i])}
    report['background_saved_nodes'] = back

for M in [4, 8, 16]:
    name = f'grid044_M{M}_tight'
    meta = json.loads((BASE / 'results' / (name + '.json')).read_text())
    model = Reduced(M=M)
    case = {'json_status': meta['status'], 'json_keys': list(meta),
            'json_accepted_nodes_total': meta.get('accepted_nodes_total'),
            'json_segment_count': len(meta.get('segments', [])),
            'state_layout': {'fractions': [0, 9], 'optical_depths': [9, 9 + 6*M], 'U': model.iu},
            'reconstruction': {'photons': 'g0 * exp(-saved optical depth)',
                               'T_K': 'saved U / (CT * (NN + VGRAD @ saved fractions))',
                               'ne_cm-3': 'n0*exp(-3*saved eta) * (VGRAD @ saved fractions)',
                               'Li_fraction_order': ['LiI', 'LiII', 'LiIII', 'LiIV'],
                               'cohort_order_initial_energy_eV': [10, 20, 40, 60, 100, 150],
                               'initial_cohorts_at_least_20eV_label': 'sum of initial 20,40,60,100,150 eV cohorts; not a current-energy cut'}}
    with np.load(BASE / 'results' / (name + '.npz'), allow_pickle=False) as d:
        case['fields'] = {k: {'shape': list(d[k].shape), 'dtype': str(d[k].dtype)} for k in d.files}
        for label, tk, yk in [('reported', 'eta', 'Y'), ('accepted', 'accepted_eta', 'accepted_Y')]:
            if tk not in d or yk not in d:
                case[label] = {'available': False}
                continue
            t, Y = d[tk], d[yk]
            f = Y[:9]
            v = VGRAD @ f
            T = Y[model.iu] / (CT * (NN + v))
            ne = model.bg.n0 * np.exp(-3*t) * v
            tau = Y[model.gx]
            g = model.g0[:, None] * np.exp(-tau)
            cohorts = g.reshape(6, M, len(t)).sum(axis=1)
            ten = tau[:M]
            hist = {'available': True, 'count': len(t), 'unique_eta_count': len(np.unique(t)),
                    'eta_range': [float(t.min()), float(t.max())],
                    'T_K_range': [float(T.min()), float(T.max())],
                    'electron_per_Href_range': [float(v.min()), float(v.max())],
                    'ne_cm-3_range': [float(ne.min()), float(ne.max())],
                    'ten_eV_optical_depth_global_range': [float(ten.min()), float(ten.max())],
                    'ten_eV_envelope_by_saved_eta': {'eta': t.tolist(), 'min': ten.min(axis=0).tolist(), 'max': ten.max(axis=0).tolist()},
                    'nearest_saved_samples': []}
            if label == 'reported':
                hist['reconstructed_T_max_abs_difference_from_saved_K'] = float(abs(T-d['temperature_K']).max())
                hist['reconstructed_electron_per_Href_max_abs_difference'] = float(abs(v-d['electron_per_Href']).max())
                hist['reconstructed_photon_groups_max_abs_difference'] = float(abs(g-d['photon_groups']).max())
                hist['saved_nHref_times_electron_per_Href_max_abs_difference_cm-3'] = float(abs(ne-d['nHref']*d['electron_per_Href']).max())
            for target in report['targets_eta']:
                i = int(abs(t-target).argmin())
                h, n, b, bp = model.bg.fields(float(t[i]))
                hist['nearest_saved_samples'].append({'target_eta': target, 'saved_index': i, 'eta_used': float(t[i]),
                    'delta_eta': float(t[i]-target), 'T_K': float(T[i]), 'ne_cm-3': float(ne[i]),
                    'electron_per_Href': float(v[i]), 'ten_eV_optical_depth_min': float(ten[:, i].min()),
                    'ten_eV_optical_depth_max': float(ten[:, i].max()),
                    'remaining_photons_per_Href_by_initial_cohort': cohorts[:, i].tolist(),
                    'remaining_initial_cohorts_at_least_20eV_per_Href': float(cohorts[1:, i].sum()),
                    'Li_charge_state_fractions': f[5:9, i].tolist(), 'b': b, 'bprime': bp})
            case[label] = hist
    report['cases'][name] = case

report['execution'] = {'wall_s': time.monotonic()-START, 'cpu_s': time.process_time(),
                       'maxrss_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       'new_IVPs': 0, 'state_interpolations': 0}
(OUT / 'saved_diagnostics.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
brief = {**report, 'cases': {}}
for name, case in report['cases'].items():
    brief['cases'][name] = {**case}
    for label in ['accepted', 'reported']:
        brief['cases'][name][label] = {k: v for k, v in case[label].items() if k != 'ten_eV_envelope_by_saved_eta'}
print(json.dumps(brief, indent=2, allow_nan=False))
