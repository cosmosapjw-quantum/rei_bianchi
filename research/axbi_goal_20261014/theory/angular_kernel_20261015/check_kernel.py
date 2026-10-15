#!/usr/bin/env python3
"""Standalone axisymmetric Bianchi-I Liouville angular-kernel validation.

Dimensionless b; mu is conserved covariant momentum direction at b=0.
Not a chemistry/feedback solver. Numerical check and throughput benchmark.
"""
import json
import time
import numpy as np
from numpy.polynomial.legendre import leggauss


def kernel(b, mu):
    # Stable log-sum-exp of two nonnegative energy contributions.
    mu2 = np.asarray(mu, dtype=float)**2
    return np.sqrt((1.0-mu2)*np.exp(2*b)+mu2*np.exp(-4*b))


def drift(b, mu):
    mu2 = np.asarray(mu, dtype=float)**2
    positive = (1.0-mu2)*np.exp(2*b)
    axial = mu2*np.exp(-4*b)
    return (positive-2.0*axial)/(positive+axial)


def checks():
    mu, w = leggauss(128)
    b = 0.013
    h = 1.e-6
    numerical = (np.log(kernel(b+h, mu))-np.log(kernel(b-h, mu)))/(2*h)
    err = float(np.max(np.abs(numerical-drift(b, mu))))
    isotropy = float(np.dot(w, drift(0., mu))/2)
    odd = float(np.max(np.abs(kernel(b, mu)-kernel(b, -mu))))
    assert err < 2e-9, err
    assert abs(isotropy) < 1e-13, isotropy
    assert odd == 0, odd
    # No-angle first-order correction to total energy; second order is allowed.
    epsilon = 1e-4
    avg = lambda z: float(np.dot(w, kernel(z, mu))/2)
    derivative = (avg(epsilon)-avg(-epsilon))/(2*epsilon)
    assert abs(derivative) < 1e-7, derivative
    return {'finite_difference_max_error':err,'isotropic_drift_average':isotropy,'reflection_error':odd,'angular_energy_linear_coefficient':derivative}


def benchmark():
    mu = np.linspace(-1,1,200000, dtype=float)
    b = 0.013
    repeats=30
    t0=time.perf_counter()
    for _ in range(repeats):
        v = kernel(b,mu)
    vtime=time.perf_counter()-t0
    import math
    sample = mu[::100] # 2000 samples for a fair direct Python baseline.
    t0=time.perf_counter()
    for m in sample:
        u=float(m)
        scalar=math.sqrt((1.0-u*u)*math.exp(2*b)+u*u*math.exp(-4*b))
    scalar_per=(time.perf_counter()-t0)/len(sample)
    return {'array_length':len(mu),'repeats':repeats,'vector_seconds_per_element':vtime/(repeats*len(mu)),'scalar_seconds_per_element':scalar_per,'approx_scalar_to_vector_ratio':scalar_per/(vtime/(repeats*len(mu))),'checksum':float(v.sum())}

if __name__=='__main__':
    print(json.dumps({'checks':checks(),'benchmark':benchmark()},indent=2))
