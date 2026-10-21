"""Thin pilot adapter: exact vendored physical RHS; setup-only caches."""
import os
for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_key] = '1'
import hashlib
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss, legvander

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))
import lrs_boltzmann as lb
import species_hierarchy as sh
import canonical_fv as fv

SOURCE = json.loads((ROOT / 'SOURCE_MANIFEST.json').read_text())
SIGMAS = [0., .0003, .001, .003, .01, .03, .1]
PIS = [0., .00001, .00003, .0001, .0003, .0006, .001]
SOLVER = dict(method='DOP853', rtol=3e-11, atol=3e-13, epochs=121)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def verify_source():
    for name, expected in SOURCE['files'].items():
        if hashlib.sha256((ROOT/'vendor'/name).read_bytes()).hexdigest() != expected:
            raise ValueError('SOURCE_IDENTITY_MISMATCH:' + name)


@lru_cache(maxsize=1)
def cosmology():
    lock = json.loads((ROOT/'vendor'/'REI_BACKGROUND_FAMILY_LOCK.json').read_text())
    c, t = lock['cosmology'], lock['clock']
    return lb.SourceLock(c['H0_per_s'], c['Omega_m'], c['Omega_r'],
                         c['Omega_lambda'], t['a_ref'], t['a_end']), c['Tcmb0_K']


_original_matrix = lb.legendre_matrix


@lru_cache(maxsize=64)
def cached_matrix(lmax, order=None, power=4):
    result = _original_matrix(lmax, order, power)
    result.flags.writeable = False
    return result


# SpeciesHierarchy resolves this function through its own imported global.
# Cache keys include every argument; source matrices and arithmetic unchanged.
sh.legendre_matrix = cached_matrix
lb.legendre_matrix = cached_matrix


_original_momentum = fv.CanonicalMomentumFV


@lru_cache(maxsize=8)
def momentum(mass_over_Tref=30., amplitude=0., radial_cells=24,
             angular_cells=12, gauss_order=3):
    return _original_momentum(mass_over_Tref, amplitude, radial_cells,
                              angular_cells, gauss_order)


fv.CanonicalMomentumFV = momentum


def calibration(sigma_f, pi_signed):
    if not all(map(math.isfinite, (sigma_f, pi_signed))) or not 0 <= sigma_f <= .1:
        raise ValueError('INVALID_INITIAL_NORM')
    src, _ = cosmology()
    hi2 = src.href**2/(1-sigma_f**2/6)
    k = 5*src.aref**4*hi2*pi_signed/(math.sqrt(6)*src.h0**2*src.omega_r)
    if abs(k) > .5:
        raise ValueError('INITIAL_RADIATION_AMPLITUDE_OUTSIDE_CONTRACT')
    return {'H_i_squared': hi2, 'k_gamma': k, 'k_nu': k,
            'Sigma_half_i': sigma_f/math.sqrt(2),
            'shear_orientation': 1 if sigma_f else 0,
            'Pi_F_signed_target': pi_signed}


def config(sigma_f, pi_signed, guard=False):
    return {'Sigma_F_i': sigma_f, 'Pi_F_signed_i': pi_signed,
            'stress_sign': int(np.sign(pi_signed)),
            'relative_alignment': int(np.sign(pi_signed)) if sigma_f and pi_signed else None,
            'ellmax': 12 if guard else 8, 'radial_cells': 48 if guard else 24,
            'angular_cells': 24 if guard else 12, 'subcell_gauss_order': 3,
            'mass_fraction': .1, 'mass_over_Tref': 30., 'massive_A': 0.,
            'ne_source': None, 'guard': guard, 'solver': SOLVER,
            'source_commit': SOURCE['source_commit'], 'source_sha256': SOURCE['files'],
            'calibration': calibration(sigma_f, pi_signed)}


def cases():
    nominal = [config(s, p*sign) for s in SIGMAS for p in PIS
               for sign in ((1,) if not p else (1, -1))]
    guards = [config(s, p, True) for s, p in ((.1, .001), (.1, -.001), (0., .001))]
    return [{'id': digest(c), 'config': c} for c in nominal+guards]


def model(c):
    src, temperature = cosmology()
    a = c['calibration']
    obj = fv.CanonicalFVSpecies(src, temperature, c['ellmax'],
        Sigma_ref=a['Sigma_half_i'], orientation=a['shear_orientation'],
        kappa_gamma=a['k_gamma'], kappa_nu=a['k_nu'], ne_source=None,
        mass_fraction=c['mass_fraction'], massive_A=c['massive_A'],
        mass_over_Tref=c['mass_over_Tref'], radial_cells=c['radial_cells'],
        angular_cells=c['angular_cells'], subcell_gauss_order=c['subcell_gauss_order'])
    # The source constructor resolves its packet setup through the cached
    # factory above. No field or RHS formula is changed.
    return obj


def observables(obj, sol):
    fields = [obj.fields(float(x), sol.y[:, i]) for i, x in enumerate(sol.t)]
    out = {name: np.array([d[name] for d in fields]) for name in
           ('a', 'b', 'H', 's', 'Sigma', 'Pi_gamma_J_m3', 'Pi_nu_J_m3',
            'Pi_matter_J_m3', 'rad_energy_norm', 'dust_energy_norm',
            'massive_energy_norm', 'massive_min_cell_population')}
    out['Sigma_half'] = out.pop('Sigma')
    out['Sigma_F'] = math.sqrt(2)*out['Sigma_half']
    out['elapsed_proper_s'] = sol.y[0]/obj.source.href
    kt = 8*math.pi*fv.G_SI/fv.C_SI**2
    for species in ('gamma', 'nu', 'matter'):
        out['Pi_F_signed_'+species] = math.sqrt(6)*kt*out['Pi_'+species+'_J_m3']/out['H']**2
    out['Pi_F_signed'] = sum(out['Pi_F_signed_'+s] for s in ('gamma', 'nu', 'matter'))
    out['Pi_F'] = np.abs(out['Pi_F_signed'])
    out['pi_s_J_m3'] = sum(out['Pi_'+s+'_J_m3'] for s in ('gamma', 'nu', 'matter'))
    out['sigma_squared_s2'] = 6*out['s']**2
    out['pi_squared_J2_m6'] = 6*out['pi_s_J_m3']**2
    out['sigma_pi_J_m3_s'] = 6*out['s']*out['pi_s_J_m3']
    out['gamma_N0'] = np.array([d['N_gamma'][0] for d in fields])
    out['nu_N0'] = np.array([d['N_nu'][0] for d in fields])
    for species in ('gamma', 'nu'):
        moments = np.array([d['E_'+species] for d in fields])
        mu, _ = leggauss(64)
        pol = legvander(mu, obj.ellmax).T*(2*np.arange(obj.n)+1)[:, None]
        out['minimum_brightness_'+species] = (moments @ pol).min(axis=1)
    out['Hamiltonian_construction_residual'] = np.array([
        abs(d['Einstein_H2']/d['H']**2-1) for d in fields])
    return out


def validate(c, sol, out):
    checks = {
        'solver_success': bool(sol.success),
        'finite_solution': bool(np.isfinite(sol.y).all()),
        'finite_observables': all(np.isfinite(v).all() for v in out.values()),
        'epochs_121': len(sol.t) == 121,
        'reached_a_end': bool(len(sol.t) and sol.t[-1] == cosmology()[0].xmax
                              and abs(out['a'][-1]-.2) <= 2e-16),
        'positive_H': bool(np.all(out['H'] > 0)),
        'canonical_nonnegative': bool(np.all(out['massive_min_cell_population'] >= 0)),
        'gamma_number': bool(np.max(abs(out['gamma_N0']-1)) <= 5e-11),
        'nu_number': bool(np.max(abs(out['nu_N0']-1)) <= 5e-11),
        'initial_Sigma': bool(abs(out['Sigma_F'][0]-c['Sigma_F_i']) <= 5e-12),
        'initial_Pi': bool(abs(out['Pi_F_signed'][0]-c['Pi_F_signed_i']) <= 5e-12),
        'positive_energy': bool(np.all(out['rad_energy_norm'] > 0) and
            np.all(out['dust_energy_norm'] > 0) and np.all(out['massive_energy_norm'] > 0)),
        'gamma_brightness_sample': bool(np.min(out['minimum_brightness_gamma']) >= -1e-10),
        'nu_brightness_sample': bool(np.min(out['minimum_brightness_nu']) >= -1e-10)}
    if c['Sigma_F_i'] == 0 and c['Pi_F_signed_i'] == 0:
        checks['isotropic_grid_control'] = bool(np.max(abs(out['Sigma_F'])) < 5e-12
                                              and np.max(abs(out['Pi_F_signed'])) < 5e-12)
    return checks
