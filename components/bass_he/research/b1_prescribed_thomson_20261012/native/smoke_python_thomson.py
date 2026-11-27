"""One positive-depth affected-boundary check; no existing full suite replay."""
from __future__ import annotations

import json
from pathlib import Path
import time

import numpy as np
from python_thomson import PythonThomson


def main():
    mu, wg = np.polynomial.legendre.leggauss(8)
    phi = 2*np.pi*np.arange(8)/8
    mu = np.repeat(mu, len(phi))
    phi = np.tile(phi, len(wg))
    weights = np.repeat(wg, 8)*(2*np.pi/8)
    s = np.sqrt(1-mu*mu)
    e = np.stack([s*np.cos(phi), s*np.sin(phi), mu], axis=1)
    theta = np.stack([mu*np.cos(phi), mu*np.sin(phi), -s], axis=1)
    azimuth = np.stack([-np.sin(phi), np.cos(phi), np.zeros_like(phi)], axis=1)
    P = np.eye(3)[None] - e[:, :, None]*e[:, None, :]
    alpha, x = 0.4, 0.2
    intensity = np.stack([np.ones_like(mu), 1+alpha*(3*mu*mu-1)/2], axis=1)
    J = 0.5*intensity[:, :, None, None]*P[:, None, :, :]
    packed = np.zeros((len(e), 2, 9))
    for k, (a, b) in enumerate([(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]):
        packed[:, :, k] = J[:, :, a, b]
    kernel = PythonThomson(e, weights)
    start = time.perf_counter()
    out = kernel.collide(packed, x)
    elapsed = time.perf_counter() - start
    O = np.zeros_like(J)
    for k, (a,b) in enumerate([(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]):
        O[:, :, a, b] = out[:, :, k]
        O[:, :, b, a] = out[:, :, k]
    Q = (np.einsum("ai,aeij,aj->ae",theta,O,theta)
         -np.einsum("ai,aeij,aj->ae",azimuth,O,azimuth))
    c07 = np.exp(-x)*np.expm1(0.7*x)/0.7
    # Direct angular-tensor moment of I=1+alpha*P2 gives this Q in theta/phi basis.
    Q_expected = -3*alpha*c07*(1-mu*mu)/20
    number = np.einsum("a,ae->e",weights,np.trace(O,axis1=2,axis2=3))
    metrics = {
        "isotropic_tensor_max_abs": float(np.max(np.abs(O[:,0]-J[:,0]))),
        "integrated_intensity_rel": float(np.max(np.abs(number/(4*np.pi)-1))),
        "quadrupole_to_Q_max_abs": float(np.max(np.abs(Q[:,1]-Q_expected))),
        "anti_components_max_abs": float(np.max(np.abs(out[:,:,6:]))),
        "screen_leak_max_abs": float(np.max(np.abs(np.einsum('aeij,aj->aei',O,e)))),
        "grid_eigenvalue_max_abs": float(np.max(np.abs(kernel.eigenvalues()-[1,.7,.5]))),
    }
    result = {
        "test_id": "B1_PYTHON_THOMSON_AFFECTED_BOUNDARY_01",
        "backend": kernel.backend, "source": "unchanged bass polarization.py::collide",
        "status": "PASS" if max(metrics.values())<2e-14 else "FAIL",
        "tolerance_absolute_or_normalized": 2e-14, "metrics": metrics,
        "collision_stage_calls": kernel.calls,
        "upstream_energy_slice_calls": kernel.upstream_energy_slice_calls,
        "native_rust_invocations": 0, "x": x, "angles": len(e), "energy_slices": 2,
        "wall_s": elapsed,
        "scope": "packed interface and analytic monopole/quadrupole response only; not full B1",
    }
    path = Path(__file__).parent/'PYTHON_THOMSON_SMOKE.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if result['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
