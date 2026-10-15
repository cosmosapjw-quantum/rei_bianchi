#!/usr/bin/env python3
"""Saved-complement finite-space T4 diagnostic. No SCF/FCI eigensolve.

summarize uses NumPy only; run supervises one local PySCF reconstruction/Krylov
worker. It never resumes or retries; valid checkpoints are retained for reuse.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time
import traceback
import numpy as np

UNIT = 'R9-T4-SAVED-COMPLEMENT-SPECTRUM-v1'
T4_CONTRACT_SHA256 = 'f870d006f3220a85c017813cbde21df7263f8c277435f438b9e01c2f172efb36'
IDENTITIES = {
    'data': '7aa230b66d500e7637161589533eef4f3f4efdc13f4beafb7e28fd275ab82c5d',
    'receipt': '3ae0c54716df1a7cfc1586a2641e1b461dffd3a721ed77daa4ca676bb0c0c3c8',
    'v6_source': '31cdd14df59ffc6208561cb3c61ff4bd114240c380693ff5789e14441e7c091c',
    'input': '289520d8aed460cdee460f5497762b0c613f003bd6ba43bb505416d945995097',
    'v6_contract': 'cf7b06ad72815513e799be253539bdfecfb9102c1fc586589003e8b6fd364e4d',
}
CASE_ID = 'quench_Li_Be_union_aug_TZ_occ_list_v6'
GRID = np.linspace(0., 20., 2001)
ETAS = (.05, .1, .2)
MILESTONES = (16, 32, 64, 128)
SCOPE = 'finite saved-complement projected Be+ spectral measure; no exclusive continuum, electron capture, or basis-closure claim'


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    tmp.replace(path)


def save_npz(path, **arrays):
    path = Path(path)
    tmp = path.with_name(path.stem + '.tmp.npz')
    np.savez(tmp, **arrays)
    tmp.replace(path)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def runtime():
    versions = {}
    for name in ('numpy', 'scipy', 'pyscf'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {'utc': utc(), 'python': sys.version, 'executable': sys.executable,
            'platform': platform.platform(), 'versions': versions,
            'cpu_count': os.cpu_count(), 'load_average': list(os.getloadavg())}


def project(vector, ground):
    return vector - ground * np.vdot(ground, vector)


def prepare_arrays(receipt, arrays, fixed_dimensions=True):
    keys = ('CI_parent', 'CI_daughter_ground', 'CI_complement', 'common_orbital_matrix',
            'AO_overlap_eigenvalues', 'rdm1_parent', 'rdm1_daughter')
    require(all(k in arrays for k in keys), 'missing required saved array')
    n, ao = receipt['retained_ao_rank'], receipt['ao_rank']
    require(isinstance(n, int) and isinstance(ao, int) and ao >= n > 0, 'invalid ranks')
    if fixed_dimensions:
        require(n == 92 and ao == 92, 'frozen T4 requires n=ao_rank=92')
    shape = (n * (n - 1) // 2, n)
    for key in keys:
        a = arrays[key]
        wanted = (shape if key.startswith('CI_') else (ao, n) if key == 'common_orbital_matrix'
                  else (ao,) if key == 'AO_overlap_eigenvalues' else (n, n))
        require(a.shape == wanted, 'saved shape mismatch: ' + key)
        require(np.all(np.isfinite(a)), 'nonfinite saved array: ' + key)
    ci, cg, saved_q = [arrays[k].reshape(-1) for k in keys[:3]]
    ni, ng = float(np.linalg.norm(ci)), float(np.linalg.norm(cg))
    require(abs(ni * ni - 1) <= 1e-10 and abs(ng * ng - 1) <= 1e-10, 'saved CI norm gate failed')
    raw_A = np.vdot(cg, ci)
    raw_q = ci - raw_A * cg
    q_error = float(np.linalg.norm(saved_q - raw_q))
    require(q_error <= 1e-10, 'saved complement identity failed')
    raw_p, raw_w = float(abs(raw_A)**2), float(np.vdot(saved_q, saved_q).real)
    require(abs(raw_p + raw_w - 1) <= 1e-10, 'saved closure failed')
    require(abs(raw_p - receipt['P_ground']) <= 1e-10, 'receipt probability mismatch')
    require(abs(raw_w - receipt['unresolved_excitation_including_bound_probability']) <= 1e-10,
            'receipt complement mismatch')
    traces = {role: float(np.trace(arrays['rdm1_' + role]).real) for role in ('parent', 'daughter')}
    require(all(abs(t - 3) <= 1e-8 for t in traces.values()), 'RDM trace failed')
    i, g = ci / ni, cg / ng
    A = np.vdot(g, i)
    q = project(i, g)
    W = float(np.vdot(q, q).real)
    require(W > 0, 'zero saved complement has no conditional diagnostic')
    u = q / math.sqrt(W)
    info = {'raw_parent_norm': ni, 'raw_daughter_norm': ng,
            'working_parent_scale': 1 / ni, 'working_daughter_scale': 1 / ng,
            'normalization': 'working copies only; raw arrays immutable; receipt parent moments scale by 1/raw_parent_norm^2',
            'saved_q_identity_l2': q_error, 'raw_P': raw_p, 'raw_W': raw_w,
            'raw_closure_error': abs(raw_p + raw_w - 1), 'rdm_traces': traces,
            'A_real': float(A.real), 'A_imag': float(A.imag), 'P': float(abs(A)**2), 'W': W,
            'working_closure_error': abs(float(abs(A)**2) + W - 1),
            'working_ground_complement_overlap': float(abs(np.vdot(g, q))),
            'norb': n, 'ao_rank': ao, 'ci_shape': list(shape)}
    return i, g, u, info


def load_saved(receipt_path, data_path):
    require(sha(receipt_path) == IDENTITIES['receipt'], 'receipt byte identity mismatch')
    require(sha(data_path) == IDENTITIES['data'], 'data byte identity mismatch')
    receipt = json.loads(Path(receipt_path).read_text())
    require(receipt['case']['id'] == CASE_ID, 'wrong case')
    require(receipt['input_sha256'] == IDENTITIES['input'], 'saved input identity mismatch')
    require(receipt['case']['contract_sha256'] == IDENTITIES['v6_contract'], 'saved V6 contract identity mismatch')
    require(receipt['runtime']['source_sha256'] == IDENTITIES['v6_source'], 'runtime source identity mismatch')
    require(receipt['status'] == 'finite_model_computed' and receipt['exit_code'] == 0,
            'input is not a successful finite-model receipt')
    require(receipt['finite_model_numerics_passed'] is True, 'top-level numerical gate failed')
    for role in ('parent', 'daughter'):
        state = receipt[role]
        require(state['finite_model_numerics_passed'] is True and state['nelec'] == [2, 1]
                and state['norb'] == 92, role + ' state identity/numerics failed')
    with Path(data_path).open('rb') as f, np.load(f, allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in archive.files}
    i, g, u, info = prepare_arrays(receipt, arrays)
    return receipt, arrays, i, g, u, info


def scalar_bounds(P, W, E0, mean, second, epsilon, cuts=(5., 10., 20.)):
    require(0 <= P <= 1 + 1e-10 and W > 0 and epsilon >= 0, 'invalid scalar bound inputs')
    require(all(math.isfinite(x) for x in (P, W, E0, mean, second, epsilon)), 'nonfinite scalar inputs')
    d, s = mean - E0, second - 2 * E0 * mean + E0**2
    require(s >= 0, 'inconsistent negative shifted second moment')
    delta = epsilon * (P + 2 * math.sqrt(P * W))
    a, b = (d - delta) / W, (d + delta) / W
    L = max(0., math.sqrt(s) - math.sqrt(P) * epsilon) / math.sqrt(W)
    U = (math.sqrt(s) + math.sqrt(P) * epsilon) / math.sqrt(W)
    c, e = max(0., L**2 - epsilon**2), U**2
    min_square = 0. if a <= 0 <= b else min(a*a, b*b)
    variance = [max(0., c - max(a*a, b*b)), e - min_square]
    require(variance[1] >= 0, 'inconsistent negative variance upper bound')
    cantelli = []
    for cut in cuts:
        bound = W * variance[1] / (variance[1] + (cut - b)**2) if cut > b else None
        cantelli.append({'cut_Eh': cut, 'unconditional_upper_probability': bound,
                         'condition_cut_above_mean_upper': cut > b})
    return {'shifted_first_d_Eh': d, 'shifted_second_s_Eh2': s,
            'epsilon_Eh': epsilon, 'conditional_mean_interval_Eh': [a, b],
            'conditional_second_interval_Eh2': [c, e], 'conditional_variance_interval_Eh2': variance,
            'exact_ground_limit_estimates': {'conditional_mean_Eh': d / W,
                 'conditional_second_Eh2': s / W, 'conditional_variance_Eh2': s / W - (d / W)**2},
            'cantelli': cantelli,
            'assumptions': 'conditional on archived H moments and daughter residual, up to rounding; finite projected measure only; cuts do not identify ionization channels'}


def make_summary(receipt_path, data_path, aug_dz_receipt=None):
    r, arrays, i, g, u, info = load_saved(receipt_path, data_path)
    E0 = r['daughter']['E_BO_Eh']
    bounds = scalar_bounds(info['P'], info['W'], E0,
                r['daughter_energy_mean_Eh'] / info['raw_parent_norm']**2,
                r['daughter_energy_second_moment_Eh2'] / info['raw_parent_norm']**2,
                r['daughter']['checks']['original_H_residual_Eh'] / info['raw_daughter_norm'])
    summary = {'unit': UNIT, 'scope': SCOPE, 'input_sha256': {'receipt': sha(receipt_path), 'data': sha(data_path)},
               'array_checks': info, 'recorded_E0_Eh': E0,
               'recorded_moments': {k: r[k] for k in ('daughter_energy_mean_Eh', 'daughter_energy_second_moment_Eh2', 'daughter_energy_variance_Eh2')},
               'residual_aware_scalar_diagnostic': bounds, 'runtime': runtime(),
               'NCP_execution_status': 'not_run_remote_unavailable',
               'original_H_residual': 'archived solver bound, not independently recomputed by summarize'}
    if aug_dz_receipt:
        old = json.loads(Path(aug_dz_receipt).read_text())
        require(old['case']['id'] == 'quench_Li_Be_union_aug_DZ', 'wrong comparison receipt')
        summary['basis_sensitivity'] = {'aug_DZ_P': old['P_ground'], 'aug_TZ_P': info['P'],
            'aug_TZ_minus_aug_DZ': info['P'] - old['P_ground'], 'receipt_sha256': sha(aug_dz_receipt),
            'claim': 'one measured basis sensitivity; not an error bound or basis-closure decision'}
    return summary


class Deferred(RuntimeError):
    pass


def available_gib():
    lines = Path('/proc/meminfo').read_text().splitlines()
    return next(int(line.split()[1]) for line in lines if line.startswith('MemAvailable:')) / 1024**2


class ActionBudget:
    def __init__(self, deadline, maximum=160, headroom_gib=20):
        self.deadline, self.maximum, self.headroom_gib = deadline, maximum, headroom_gib
        self.actions = 0

    def check(self):
        if time.monotonic() >= self.deadline:
            raise Deferred('cumulative_wall_limit')
        if self.headroom_gib and available_gib() < self.headroom_gib:
            raise Deferred('host_headroom_below_20GiB')

    def apply(self, action, vector):
        self.check()
        if self.actions >= self.maximum:
            raise Deferred('Hamiltonian_action_limit')
        self.actions += 1
        value = np.asarray(action(vector))
        self.check()
        require(value.shape == vector.shape and np.all(np.isfinite(value)), 'invalid Hamiltonian action')
        return value


def reconstruction_checks(action, i, g, u, E0, mean, second, metric_error):
    hi, hg, hu = action(i), action(g), action(u)
    gates = []
    def gate(name, measured, limit):
        gates.append({'name': name, 'measured': float(measured), 'limit': float(limit),
                      'pass': bool(np.isfinite(measured) and measured <= limit)})
    gate('orbital_metric_inf', metric_error, 1e-8)
    gate('daughter_norm_error', abs(np.vdot(g, g) - 1), 1e-10)
    gate('ground_energy_difference_Eh', abs(np.vdot(g, hg) - E0), 1e-8)
    gate('ground_residual_Eh', np.linalg.norm(hg - E0*g), 1e-7)
    gate('parent_mean_difference_Eh', abs(np.vdot(i, hi) - mean), 1e-8)
    gate('parent_second_difference_Eh2', abs(np.vdot(hi, hi) - second), 1e-8 * max(1., abs(second)))
    values, actions = {'i': i, 'g': g, 'u': u}, {'i': hi, 'g': hg, 'u': hu}
    for a, b in (('i', 'g'), ('i', 'u'), ('g', 'u')):
        left, right = np.vdot(values[a], actions[b]), np.vdot(actions[a], values[b])
        gate('hermiticity_' + a + '_' + b, abs(left-right), 1e-9 * max(1., abs(left), abs(right)))
    return {'passed': all(x['pass'] for x in gates), 'gates': gates,
            'direct_ground_energy_Eh': float(np.vdot(g, hg).real),
            'direct_parent_mean_Eh': float(np.vdot(i, hi).real),
            'direct_parent_second_Eh2': float(np.vdot(hi, hi).real)}


def lorentzian_spectra(nodes, weights, grid=GRID, etas=ETAS):
    delta = grid[:, None] - nodes[None, :]
    spectra, cdfs, masses = [], [], []
    W = float(sum(weights))
    for eta in etas:
        spectra.append(np.sum(weights[None, :] * eta / (math.pi * (delta**2 + eta**2)), axis=1))
        cdf = np.sum(weights[None, :] * (.5 + np.arctan(delta / eta) / math.pi), axis=1)
        cdfs.append(cdf)
        masses.append({'eta_Eh': eta, 'below_0': float(cdf[0]),
                       'inside_0_20': float(cdf[-1] - cdf[0]), 'above_20': float(W - cdf[-1])})
    return {'grid': np.asarray(grid), 'etas': np.asarray(etas), 'spectra': np.asarray(spectra),
            'cdfs': np.asarray(cdfs), 'masses': masses}


def refinement(previous, current, W):
    rows = []
    trapezoid = getattr(np, 'trapezoid', None)
    if trapezoid is None:
        trapezoid = np.trapz
    for index, eta in enumerate(current['etas']):
        l1 = float(trapezoid(abs(current['spectra'][index] - previous['spectra'][index]), current['grid']) / W)
        cdf = float(np.max(abs(current['cdfs'][index] - previous['cdfs'][index])) / W)
        window = abs(current['masses'][index]['inside_0_20'] - previous['masses'][index]['inside_0_20']) / W
        rows.append({'eta_Eh': float(eta), 'spectrum_L1_over_W': l1,
                     'max_CDF_change_over_W': cdf, 'window_mass_change_over_W': window,
                     'pass': l1 <= 1e-3 and cdf <= 1e-3 and window <= 1e-3})
    return {'passed': all(row['pass'] for row in rows), 'metrics': rows, 'tolerance': 1e-3}


def compressed_measure(V, KV, ground, W, direct_moments, remainder, corrections, happy):
    m = V.shape[1]
    C = V.conj().T @ KV
    J = (C + C.conj().T) * .5
    nodes, Y = np.linalg.eigh(J)
    weights = W * abs(Y[0])**2
    normC, normJ = np.linalg.norm(C, np.inf), np.linalg.norm(J, np.inf)
    offtri = C.copy()
    offtri[np.abs(np.arange(m)[:, None] - np.arange(m)[None, :]) <= 1] = 0
    moments = [float(np.sum(weights * nodes**k)) for k in range(3)]
    gates = []
    def gate(name, measured, limit):
        gates.append({'name': name, 'measured': float(measured), 'limit': float(limit),
                      'pass': bool(np.isfinite(measured) and measured <= limit)})
    finite = all(np.all(np.isfinite(x)) for x in (V, KV, C, nodes, weights))
    gates.append({'name': 'finite_vectors_matrix_nodes_weights', 'measured': bool(finite), 'pass': bool(finite)})
    gate('basis_gram_inf', np.linalg.norm(V.conj().T @ V - np.eye(m), np.inf), 1e-9)
    gate('ground_leakage', np.max(abs(ground.conj() @ V)), 1e-10)
    gate('antihermitian_inf', np.linalg.norm(C - C.conj().T, np.inf), 1e-10 * max(1., normC))
    gate('eigensystem_inf', np.linalg.norm(J@Y - Y*nodes, np.inf), 1e-10 * max(1., normJ))
    gate('mass_error', abs(sum(weights) - W), 1e-10)
    for k, (actual, target) in enumerate(zip(moments, direct_moments)):
        gate('direct_moment_' + str(k) + '_difference', abs(actual-target), 1e-8 * max(1., abs(target)))
    ritz = []
    for index in np.argsort(weights)[-min(6, m):][::-1]:
        y = Y[:, index]
        rv = V @ y
        ritz.append({'node_Eh': float(nodes[index]), 'weight': float(weights[index]),
                     'residual_Eh': float(np.linalg.norm(KV@y - nodes[index]*rv)),
                     'ground_leakage': float(abs(np.vdot(ground, rv)))})
    diag = {'length': m, 'passed': all(g['pass'] for g in gates), 'gates': gates,
            'compressed_off_tridiagonal_inf': float(np.linalg.norm(offtri, np.inf)),
            'unconditional_moments': moments,
            'conditional_mean_Eh': moments[1] / W, 'conditional_second_Eh2': moments[2] / W,
            'conditional_variance_Eh2': moments[2] / W - (moments[1]/W)**2,
            'weighted_central_second_moment_Eh2': moments[2] - moments[1]**2 / W,
            'ritz_largest_weights': ritz, 'actual_remainder_norm_Eh': remainder,
            'reorthogonalization_correction_norms_Eh': corrections,
            'happy_breakdown': bool(happy),
            'invariant_subspace_certificate': bool(happy and all(g['pass'] for g in gates)),
            'negative_node_interpretation_flag': bool(np.any(nodes < -1e-7)),
            'minimum_raw_node_Eh': float(min(nodes)),
            'direct_moments': list(direct_moments)}
    if happy:
        # This direct cached-action evidence supplements the recurrence's small
        # last remainder. It changes no acceptance threshold or Hamiltonian.
        diag['invariant_subspace_max_column_residual_Eh'] = max(
            float(np.linalg.norm(KV[:, k] - V@C[:, k])) for k in range(m))
    broad = lorentzian_spectra(nodes, weights)
    diag['lorentzian_masses'] = broad['masses']
    return diag, {'nodes': nodes, 'weights': weights, 'compressed_C': C, 'compressed_J': J,
                  **{k: broad[k] for k in ('grid', 'etas', 'spectra', 'cdfs')}}, broad


def krylov_chain(action, ground, u, W, out=None, budget=None, identities=None, max_length=128):
    """Nested two-pass MGS Lanczos; optional disk checkpoint at each milestone."""
    require(max_length <= 128 and max_length >= 1, 'invalid Krylov cap')
    dimension = len(u)
    V = np.empty((dimension, max_length), dtype=np.result_type(u, ground), order='F')
    KV = np.empty_like(V, order='F')
    v = u.copy()
    previous_beta = 0.
    corrections = []
    records, prior_broad, prior_m = [], None, None
    direct, spectral = None, None
    termination = 'maximum_length'
    refine_met = False
    for j in range(max_length):
        if budget:
            budget.check()
        V[:, j] = v
        kv = action(v)
        KV[:, j] = kv
        if j == 0:
            direct = [W, W*float(np.vdot(u, kv).real), W*float(np.vdot(kv, kv).real)]
        alpha = np.vdot(v, kv)
        residual = kv - alpha*v
        if j:
            residual -= previous_beta * V[:, j-1]
        raw_residual = residual.copy()
        residual = project(residual, ground)
        for _ in range(2):
            for index in range(j+1):
                residual -= V[:, index] * np.vdot(V[:, index], residual)
        residual = project(residual, ground)
        correction = float(np.linalg.norm(raw_residual-residual))
        corrections.append(correction)
        beta = float(np.linalg.norm(residual))
        threshold = 1e-12 * max(1., float(np.linalg.norm(kv)))
        happy = beta <= threshold
        length = j+1
        if length in MILESTONES or happy or length == max_length:
            diag, spectral, broad = compressed_measure(V[:, :length], KV[:, :length], ground, W,
                                                        direct, beta, corrections.copy(), happy)
            diag['breakdown_threshold_Eh'] = threshold
            diag['refinement'] = refinement(prior_broad, broad, W) if prior_broad else None
            diag['refinement_pair'] = [prior_m, length] if prior_m else None
            if out:
                out = Path(out)
                dump(out / ('milestone_%03d.json' % length), diag)
                save_npz(out / ('milestone_%03d.npz' % length), **spectral)
            records.append(diag)
            if not diag['passed']:
                raise ValueError('Krylov milestone numerical gate failed at ' + str(length))
            if out:
                metadata = {'unit': UNIT, 'identities': identities, 'length': length,
                            'Hamiltonian_actions': budget.actions if budget else None,
                            'cumulative_remaining_wall_s': budget.deadline-time.monotonic() if budget else None,
                            'direct_moments': direct, 'next_beta': beta,
                            'resume_implemented': False, 'saved_utc': utc()}
                save_npz(out / 'checkpoint.npz', V=V[:, :length], KV=KV[:, :length], ground=ground,
                         u=u, next_vector=residual/beta if not happy else np.zeros_like(residual),
                         metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)))
                save_npz(out / 'spectra.npz', **spectral)
                dump(out / 'progress.json', {**metadata, 'latest_milestone': diag})
            if diag['negative_node_interpretation_flag']:
                termination = 'negative_node_requires_Astra_interpretation'
                break
            if happy:
                termination = 'certified_invariant_subspace'
                break
            if length in (64, 128) and prior_m == length//2 and diag['refinement']['passed']:
                refine_met, termination = True, 'declared_broadening_refinement_met'
                break
            prior_m, prior_broad = length, broad
        v, previous_beta = residual / beta, beta
    return {'milestones': records, 'termination': termination, 'refinement_met': refine_met,
            'invariant_subspace': termination == 'certified_invariant_subspace',
            'direct_moments': direct, 'last_length': records[-1]['length'] if records else 0,
            'scope': SCOPE}, spectral


def reconstruct(receipt, arrays, i, g, u, info, source_path, budget):
    require(sha(source_path) == IDENTITIES['v6_source'], 'immutable V6 source byte mismatch')
    spec = importlib.util.spec_from_file_location('frozen_v6', source_path)
    v6 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v6)
    from pyscf import gto, ao2mo
    budget.check()
    mol = gto.M(atom=[('Be', (0., 0., 0.))], basis={'Be': receipt['common_expanded_basis']},
                charge=1, spin=1, unit='Bohr', cart=False, symmetry=False,
                verbose=0, max_memory=int(24*1024*.70))
    X = arrays['common_orbital_matrix']
    require(mol.nelec == (2, 1) and mol.nao_nr() == 92 and X.shape == (92, 92), 'reconstruction sector/dimension mismatch')
    estimate = v6.estimate(92, (2, 1), 24., extra_vectors=256)
    S = mol.intor('int1e_ovlp')
    metric = float(np.linalg.norm(X.conj().T@S@X - np.eye(92), np.inf))
    # Metric must pass before transforming the expensive ERI.
    if metric > 1e-8 or not np.isfinite(metric):
        return {'passed': False, 'gates': [{'name': 'orbital_metric_inf',
                'measured': metric if np.isfinite(metric) else str(metric), 'limit': 1e-8, 'pass': False}],
                'stage': 'before_ERI', 'integrals_included': False}, None
    h = X.conj().T @ (mol.intor('int1e_kin') + mol.intor('int1e_nuc')) @ X
    budget.check()
    eri = ao2mo.kernel(mol, X)
    budget.check()
    native = v6.raw_action(h, eri, 92, (2, 1))
    shape = arrays['CI_parent'].shape
    def H(vector):
        return budget.apply(lambda x: native(x.reshape(shape)).reshape(-1), vector)
    E0 = receipt['daughter']['E_BO_Eh']
    checks = reconstruction_checks(H, i, g, u, E0,
                receipt['daughter_energy_mean_Eh'] / info['raw_parent_norm']**2,
                receipt['daughter_energy_second_moment_Eh2'] / info['raw_parent_norm']**2, metric)
    checks.update(resource_estimate=estimate, integrals_included=False,
                  integral_policy='h/ERI reconstructed once in memory; not included in checkpoint',
                  frozen_raw_action_sha256=sha(source_path), nelec=list(mol.nelec), norb=92)
    def K(vector):
        qv = project(vector, g)
        return project(H(qv) - E0*qv, g)
    return checks, K


def worker(config_path):
    config = json.loads(Path(config_path).read_text())
    out = Path(config['out'])
    resource.setrlimit(resource.RLIMIT_AS, (24*1024**3, 24*1024**3))
    started = config['started_monotonic']
    budget = ActionBudget(started + 7200.)
    receipt = {'unit': UNIT, 'scope': SCOPE, 'started_utc': utc(), 'runtime': runtime(),
               'status': 'failure', 'numerical_passed': False, 'NCP_execution_status': 'executed',
               'resume_implemented': False, 'integrals_included': False}
    try:
        budget.check()
        r, arrays, i, g, u, info = load_saved(config['receipt'], config['data'])
        summary = make_summary(config['receipt'], config['data'])
        summary['NCP_execution_status'] = 'executed_reconstruction_pending'
        dump(out / 'summary.json', summary)
        checks, K = reconstruct(r, arrays, i, g, u, info, config['v6_source'], budget)
        dump(out / 'reconstruction.json', checks)
        require(checks['passed'], 'reconstruction gates failed; no basis extension')
        identities = {'receipt': sha(config['receipt']), 'data': sha(config['data']),
                      'v6_source': sha(config['v6_source']), 'runner': sha(__file__)}
        result, spectra = krylov_chain(K, g, u, info['W'], out, budget, identities)
        dump(out / 'chain.json', result)
        with (out / 'milestones.csv').open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['length', 'passed', 'conditional_mean_Eh', 'conditional_second_Eh2', 'conditional_variance_Eh2', 'remainder_Eh', 'refinement_met'])
            for m in result['milestones']:
                writer.writerow([m['length'], m['passed'], m['conditional_mean_Eh'], m['conditional_second_Eh2'],
                                 m['conditional_variance_Eh2'], m['actual_remainder_norm_Eh'],
                                 m['refinement']['passed'] if m['refinement'] else None])
        success = result['refinement_met'] or result['invariant_subspace']
        receipt.update(status='success' if success else 'partial', numerical_passed=success,
                       refinement_met=result['refinement_met'], invariant_subspace=result['invariant_subspace'],
                       termination=result['termination'], last_length=result['last_length'],
                       input_identities=identities,
                       direct_K_moments=result['direct_moments'],
                       direct_moment_policy='measured reconstructed K moments supersede archived scalar estimates for this operator')
    except Deferred as e:
        receipt.update(status='partial' if (out/'checkpoint.npz').exists() else 'deferred', reason=str(e))
    except Exception as e:
        receipt.update(status='failure', reason=str(e), traceback=traceback.format_exc())
        print(receipt['traceback'], file=sys.stderr)
    receipt.update(completed_utc=utc(), wall_s=time.monotonic()-started,
                   Hamiltonian_actions=budget.actions,
                   peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   checkpoint_exists=(out/'checkpoint.npz').exists())
    dump(out / 'receipt.json', receipt)
    print(json.dumps({'status': receipt['status'], 'Hamiltonian_actions': budget.actions}))
    return 0 if receipt['status'] in ('success', 'partial') else 3 if receipt['status'] == 'deferred' else 1


def supervise(command, out, wall_s, memory_gib, env=None, headroom_gib=20., started=None):
    """Supervise only the new child process group; useful for cheap test fixtures."""
    out, started = Path(out), time.monotonic() if started is None else started
    require(not (out/'receipt.json').exists(), 'existing terminal output cannot be rerun')
    launch = {'command': command, 'wall_s': wall_s, 'memory_gib': memory_gib,
              'headroom_gib': headroom_gib, 'host_before': runtime(),
              'host_available_gib_before': available_gib(), 'started_utc': utc()}
    dump(out / 'launch.json', launch)
    reason, peak = None, 0
    if headroom_gib and available_gib() < headroom_gib:
        result = {'unit': UNIT, 'status': 'deferred', 'reason': 'host_headroom_before_launch',
                  'numerical_passed': False, 'child_started': False, 'scope': SCOPE}
        dump(out/'receipt.json', result)
        return result
    with (out/'stdout.log').open('w') as stdout, (out/'stderr.log').open('w') as stderr:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
        while child.poll() is None:
            try:
                lines = Path('/proc/%d/status' % child.pid).read_text().splitlines()
                rss = next((int(line.split()[1]) for line in lines if line.startswith('VmRSS:')), 0)
            except FileNotFoundError:
                rss = 0
            peak = max(peak, rss)
            if time.monotonic()-started >= wall_s:
                reason = 'wall_limit'
            elif rss > memory_gib*1024**2:
                reason = 'RSS_limit'
            elif headroom_gib and available_gib() < headroom_gib:
                reason = 'host_headroom_limit'
            if reason:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                break
            time.sleep(.05)
        code = child.wait()
    result = json.loads((out/'receipt.json').read_text()) if (out/'receipt.json').exists() else {
        'unit': UNIT, 'status': 'partial' if (out/'checkpoint.npz').exists() else 'deferred' if reason else 'failure',
        'numerical_passed': False, 'reason': reason or 'worker_exited_without_receipt', 'scope': SCOPE}
    if reason:
        result.update(status='partial' if (out/'checkpoint.npz').exists() else 'deferred',
                      numerical_passed=False, reason=reason)
    elif code != 0 and result.get('status') == 'success':
        result.update(status='failure', numerical_passed=False, reason='nonzero_worker_exit')
    result.update(supervisor_exit_code=code, supervisor_stop_reason=reason,
                  supervisor_wall_s=time.monotonic()-started, supervisor_peak_rss_kib=peak,
                  host_available_gib_after=available_gib(), completed_utc=utc(),
                  checkpoint_exists=(out/'checkpoint.npz').exists())
    dump(out/'receipt.json', result)
    return result


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode', required=True)
    for mode in ('summarize', 'run'):
        q = sub.add_parser(mode)
        q.add_argument('--receipt', type=Path, required=True)
        q.add_argument('--data', type=Path, required=True)
        q.add_argument('--out', type=Path, required=True)
        q.add_argument('--contract', type=Path)
        if mode == 'summarize':
            q.add_argument('--aug-dz-receipt', type=Path)
        else:
            q.add_argument('--v6-source', type=Path, required=True)
            q.add_argument('--threads', type=int, default=12, choices=[12])
            q.add_argument('--memory-gib', type=float, default=24., choices=[24.])
            q.add_argument('--wall-s', type=float, default=7200., choices=[7200.])
    q = sub.add_parser('__worker', help=argparse.SUPPRESS)
    q.add_argument('--config', required=True, type=Path)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    if args.mode == '__worker':
        return worker(args.config)
    created = False
    try:
        args.out.mkdir(parents=True, exist_ok=False)
        created = True
        if args.contract:
            contract = json.loads(args.contract.read_text())
            require(contract['unit_id'] == UNIT, 'wrong T4 contract')
            require(sha(args.contract) == T4_CONTRACT_SHA256, 'frozen T4 contract byte identity mismatch')
            dump(args.out/'contract_identity.json', {'path': str(args.contract.resolve()), 'sha256': sha(args.contract)})
        if args.mode == 'summarize':
            summary = make_summary(args.receipt, args.data, args.aug_dz_receipt)
            dump(args.out/'summary.json', summary)
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0
        started = time.monotonic()
        require(os.cpu_count() >= 12, 'fewer than 12 host CPUs available')
        require(sha(args.v6_source) == IDENTITIES['v6_source'], 'immutable V6 source mismatch')
        config = {k: str(getattr(args, k).resolve()) for k in ('receipt', 'data', 'v6_source', 'out')}
        config.update(started_monotonic=started, threads=12, memory_gib=24., wall_s=7200.)
        dump(args.out/'worker_config.json', config)
        env = os.environ | {'OMP_NUM_THREADS': '12', 'OPENBLAS_NUM_THREADS': '1',
                            'MKL_NUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1'}
        command = [sys.executable, str(Path(__file__).resolve()), '__worker', '--config', str((args.out/'worker_config.json').resolve())]
        result = supervise(command, args.out, 7200., 24., env=env, started=started)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result['status'] in ('success', 'partial') else 3 if result['status'] == 'deferred' else 1
    except Exception as e:
        print(str(e), file=sys.stderr)
        if created and not (args.out/'receipt.json').exists():
            dump(args.out/'command_failure.json', {'status': 'failure', 'reason': str(e), 'utc': utc()})
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
