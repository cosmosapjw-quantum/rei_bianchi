"""New APERTURE07 calculations, invoked inside its bounded validation process.

This script is not a plotter. It never calls an ANGULAR06/PHOTON05 kernel.
"""
import hashlib
import json
from pathlib import Path
import sys
from fractions import Fraction as Q

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.aperture import AngularMap, BernsteinDensity, aperture_integral, pair_response

SOURCE_SHA256 = '71812d18e39080ace31cfb0d0a5b418ea0dc291210b6d34c8b79c992d6376ff6'


def scalar(value):
    return {'rational': str(value), 'display_float': float(value)}


def bounds(value):
    return {k: scalar(getattr(value, k)) for k in
            ('lower', 'upper', 'width', 'uncertainty_length', 'width_bound')}


def build_payload():
    source_path = ROOT / 'sources/ANGULAR06_SAVED_PLOT_DATA.json'
    raw = source_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise RuntimeError('immutable ANGULAR06 saved input changed')
    source = json.loads(raw)
    if len(source['native']) != 12:
        raise RuntimeError('expected twelve saved native parameter rows')
    uniform = BernsteinDensity([Q(1, 2)])
    manufactured = BernsteinDensity([0, Q(3, 2), 0])
    folded = AngularMap(1, Q(5, 4))
    bins = []
    for exponent in range(2, 8):
        width = Q(1, 2**exponent)
        result = aperture_integral(folded, uniform, (Q(3, 5), Q(3, 5) + width), delta=Q(1, 2**40))
        bins.append({'lab_bin_width': scalar(width), 'mass': bounds(result['integral'])})
    convergence = []
    for exponent in (8, 16, 24, 40):
        delta = Q(1, 2**exponent)
        result = aperture_integral(folded, uniform, (Q(3, 5), Q(4, 5)), delta=delta)
        convergence.append({'bits': exponent, 'delta': scalar(delta),
                            'mass': bounds(result['integral'])})
    paired = pair_response(AngularMap(1, 0), uniform, (Q(1, 2), 1), (-1, -Q(1, 2)),
                           delta=Q(1, 2**40), energy0=3, energy1=1)
    counterexample = {name: bounds(paired[name]) for name in
                      ('coincidence', 'hit_a', 'hit_b', 'inclusive_a', 'inclusive_b',
                       'coincidence_daughters', 'pair_energy_MeV')}
    counterexample['product_of_marginal_hits'] = scalar(Q(1, 4))
    native = []
    for row in source['native']:
        # Deliberately read stored gamma/a only; no DCS/error/flux conversion.
        response = pair_response(AngularMap(row['gamma'], row['a']), manufactured,
                                 (Q(1, 2), 1), (-1, -Q(1, 2)), delta=Q(1, 2**40))
        native.append({'source_row': row['source_row'],
                       'gamma_stored_exact': scalar(Q.from_float(row['gamma'])),
                       'a_stored_exact': scalar(Q.from_float(row['a'])),
                       'synthetic_density': 'Bernstein [0,3/2,0]; sigma=1',
                       **{name: bounds(response[name]) for name in
                          ('coincidence', 'hit_a', 'hit_b', 'inclusive_a', 'inclusive_b')}})
    return {
        'schema': 'HE_APERTURE07_SAVED_DATA_V1',
        'source_angular06_saved_sha256': SOURCE_SHA256,
        'source_columns_used': ['source_row', 'gamma', 'a'],
        'fixed_stored_parameter_certificate_only': True,
        'scope': 'continuous even polar marginal; whole-azimuth annular windows',
        'empirical_DCS_used': False, 'old_scientific_kernels_called': False,
        'physical_event_rate_inferred': False,
        'fold_bin_mass': bins, 'convergence': convergence,
        'correlated_counterexample': counterexample, 'native_parameters': native,
    }


def save_payload(payload):
    target = ROOT / 'evidence/validation/SAVED_PLOT_DATA.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, indent=2) + '\n')
    temporary.replace(target)
    return target


if __name__ == '__main__':
    print(save_payload(build_payload()))
