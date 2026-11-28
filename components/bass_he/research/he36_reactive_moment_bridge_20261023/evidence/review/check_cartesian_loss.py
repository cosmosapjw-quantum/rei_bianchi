"""Independent raw incoming-loss Gaussian oracle. No derived source coefficient used."""
from pathlib import Path
import sys
import importlib.util
import json
import hashlib
import math
import platform
import time
import resource
from datetime import datetime, timezone

import numpy as np
from numpy.polynomial.hermite import hermgauss

ROOT = Path(__file__).parent
TARGET = Path('/tmp/he36_pair_implementation/reactive_moments.py')
spec = importlib.util.spec_from_file_location('review_target_reactive_moments', TARGET)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
RawMoments = module.RawMoments
binary_loss = module.binary_loss

KB = 1.380649e-23
MU = 1.66053906892e-27
GATE = 2e-11
start = time.perf_counter()
started_utc = datetime.now(timezone.utc).isoformat()

nodes, weights = hermgauss(5)
meshes = np.meshgrid(*([nodes] * 6), indexing='ij')
coordinates = np.stack([arr.ravel() for arr in meshes], axis=1)
weight_meshes = np.meshgrid(*([weights] * 6), indexing='ij')
joint_weight = np.prod(np.stack([arr.ravel() for arr in weight_meshes], axis=1), axis=1) / math.pi**3

ZA = np.array([[0.12,0.04,-0.02],[0.04,-0.03,0.01],[-0.02,0.01,-0.09]])
ZB = np.array([[-0.07,-0.03,0.01],[-0.03,0.10,0.02],[0.01,0.02,-0.03]])

def rising_three_halves(order):
    result = 1.0
    for j in range(order):
        result *= 1.5 + j
    return result

def stf(tensor):
    return tensor - np.eye(3) * np.trace(tensor) / 3

def relative_error(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    denominator = max(float(np.max(np.abs(actual))), float(np.max(np.abs(expected))), np.finfo(float).tiny)
    return float(np.max(np.abs(actual - expected))) / denominator

rows = []
for case, (ma, mb, na, nb, temperature) in enumerate([
    (1.0*MU,4.0*MU,1.3e6,0.7e6,8000.0),
    (7.0*MU,0.2*MU,0.4e6,2.1e6,23000.0),
]):
    theta = KB * temperature
    reduced_mass = ma * mb / (ma + mb)
    v = coordinates[:,:3] * math.sqrt(2 * theta / ma)
    w = coordinates[:,3:] * math.sqrt(2 * theta / mb)
    relative_velocity = v - w
    relative_energy = 0.5 * reduced_mass * np.sum(relative_velocity**2, axis=1)
    x = relative_energy / theta
    pi_a = na * theta * ZA
    pi_b = nb * theta * ZB
    score_a = ma / (2 * na * theta**2) * np.einsum('ni,ij,nj->n', v, pi_a, v)
    score_b = mb / (2 * nb * theta**2) * np.einsum('ni,ij,nj->n', w, pi_b, w)
    score = score_a + score_b
    k0 = 2.4e-15
    for q in [0, 1, 2]:
        kernel = k0 * x**q
        weighted_kernel = joint_weight * kernel
        number_rate = -na * nb * np.sum(weighted_kernel)
        raw_a_0 = -na * nb * ma * np.einsum('n,ni,nj->ij', weighted_kernel, v, v)
        raw_b_0 = -na * nb * mb * np.einsum('n,ni,nj->ij', weighted_kernel, w, w)
        raw_a_1 = -na * nb * ma * np.einsum('n,ni,nj->ij', weighted_kernel * score, v, v)
        raw_b_1 = -na * nb * mb * np.einsum('n,ni,nj->ij', weighted_kernel * score, w, w)
        reference_ja = stf(raw_a_1)
        reference_jb = stf(raw_b_1)
        moments = RawMoments(k0 * rising_three_halves(q),
            theta * k0 * rising_three_halves(q+1),
            theta**2 * k0 * rising_three_halves(q+2),
            provenance='independent-polynomial-Gaussian-control',
            interpretation='supplied_moments')
        actual = binary_loss(na,nb,ma,mb,temperature,pi_a,pi_b,moments,linear_response=True)
        errors = {
            'Rn_a': relative_error(actual.Rn_a, number_rate),
            'Rn_b': relative_error(actual.Rn_b, number_rate),
            'Q_a': relative_error(actual.Q_a, 0.5*np.trace(raw_a_0)),
            'Q_b': relative_error(actual.Q_b, 0.5*np.trace(raw_b_0)),
            'J_a': relative_error(actual.J_a, reference_ja),
            'J_b': relative_error(actual.J_b, reference_jb),
            'S_a': relative_error(actual.S_a, raw_a_0+raw_a_1),
            'S_b': relative_error(actual.S_b, raw_b_0+raw_b_1),
        }
        # First-order STF perturbations have no scalar number or energy moment.
        scalar_variation_residuals = {
            'number': float(abs(np.sum(weighted_kernel*score)) / np.sum(weighted_kernel)),
            'Q_a': float(abs(np.trace(raw_a_1)) / abs(np.trace(raw_a_0))),
            'Q_b': float(abs(np.trace(raw_b_1)) / abs(np.trace(raw_b_0))),
        }
        passed = max([*errors.values(),*scalar_variation_residuals.values()]) <= GATE
        rows.append(dict(case=case,power=q,input=dict(ma=ma,mb=mb,na=na,nb=nb,T=temperature),
            errors=errors,scalar_first_variation=scalar_variation_residuals,
            max_error=max(errors.values()),pass_gate=passed,
            oracle_Q=[float(0.5*np.trace(raw_a_0)),float(0.5*np.trace(raw_b_0))],
            oracle_J_A=reference_ja.tolist(),oracle_J_B=reference_jb.tolist()))

report = dict(status='PASS' if all(r['pass_gate'] for r in rows) else 'FAIL',
    started_utc=started_utc,finished_utc=datetime.now(timezone.utc).isoformat(),
    gate_relative=GATE,controls=6,quadrature_nodes_per_control=len(joint_weight),
    total_joint_nodes=6*len(joint_weight),
    source_sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    max_relative_error=max(r['max_error'] for r in rows),
    max_scalar_first_variation=max(max(r['scalar_first_variation'].values()) for r in rows),
    wall_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    environment=dict(python=platform.python_version(),numpy=np.__version__,threads='1 requested by parent command'),
    rows=rows,prior_suite_replay_count=0,new_ivps=0,new_renders=0,new_empirical_admissions=0,
    interpretation='Independent instantaneous incoming-loss Grad first variation; product/gain and physical isotope/nuclear rates remain unspecified.')
ROOT.joinpath('CARTESIAN_LOSS_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','controls','quadrature_nodes_per_control','max_relative_error','max_scalar_first_variation','wall_seconds','peak_rss_kib','source_sha256']},indent=2))
if report['status'] != 'PASS':
    raise SystemExit(1)
