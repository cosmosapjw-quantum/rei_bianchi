#!/usr/bin/env python3
"""Original HH screened source multipoles from a positive Yukawa formula.

The formula is exact; SciPy binary64 evaluation remains noncertifying.
DLMF10.60.3 uses k_l=sqrt(pi/(2z))*K_(l+1/2); our kbar=(2/pi)*k_l.
For r>=27>a=.7, V=2(Y_kappa-d_kappa Y_kappa)|kappa=2, Y=e^-kappa*d/d.

Integral_-1^1 V P_l dmu
 =4*kappa*((i_l-a*i_(l+1))*kbar_l + r*i_l*kbar_(l-1)).

At l=0, kbar_-1=kbar_0. Since i_(l+1)/i_l <= (kappa*a)/(2*l+3),
i_l-a*i_(l+1) >= (101/150)*i_l in this fixed HH model. All terms in
the displayed formula are positive. No angular quadrature is performed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import scipy
from scipy.special import spherical_in, spherical_kn

OFFSET = 7.0 / 10.0
KAPPA = 2.0  # Screening exponent, distinct from scattering k=7/10 and eta_C.
PRIMARY_SOURCES = [
    "https://dlmf.nist.gov/10.60.E3",
    "https://dlmf.nist.gov/10.47.E7",
    "https://dlmf.nist.gov/10.47.E9",
    "https://dlmf.nist.gov/10.51.E5",
    "https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.spherical_in.html",
    "https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.spherical_kn.html",
]


def backend_metadata():
    return {
        "method": "analytic_positive_Yukawa_multipoles",
        "offset": "7/10", "screening_kappa": "2", "scattering_k": "7/10",
        "eta_C": "-10/7", "numpy": np.__version__, "scipy": scipy.__version__,
        "precision": "binary64", "angular_quadrature_used": False,
        "certified": False, "primary_sources": PRIMARY_SOURCES,
        "domain": {"lmax": [0, 128], "radii": [27, 65], "max_radial_points": 4097},
    }


def _domain(radii, lmax):
    if type(lmax) is not int or not 0 <= lmax <= 128:
        raise ValueError("lmax must be an integer in 0..128")
    raw = np.asarray(radii)
    if np.iscomplexobj(raw):
        raise ValueError("real radii required")
    r = np.asarray(raw, dtype=np.float64)
    if r.ndim != 1 or not 1 <= len(r) <= 4097:
        raise ValueError("radii must be a nonempty one-dimensional array of at most4097 points")
    if not np.isfinite(r).all() or np.any(r < 27.0) or np.any(r > 65.0):
        raise ValueError("all radii must lie in the fixed interval[27,65]")
    return r, np.arange(lmax + 1)[:, None]


def _positive_normal(value, label):
    if not np.isfinite(value).all() or np.any(value <= 0):
        raise ArithmeticError(label + ": nonfinite, nonpositive, or underflow-to-zero value")
    if np.any(value < np.finfo(np.float64).tiny):
        raise ArithmeticError(label + ": subnormal value outside the binary64 preparation contract")
    return value


def screen_legendre_integrals(radii, lmax):
    """Return integral V(r,mu)P_l(mu)dmu, shape(lmax+1,len(radii))."""
    r, ell = _domain(radii, lmax)
    with np.errstate(over="raise", under="raise", divide="raise", invalid="raise"):
        i = _positive_normal(spherical_in(ell, KAPPA * OFFSET), "i_l")
        ip = _positive_normal(spherical_in(ell + 1, KAPPA * OFFSET), "i_(l+1)")
        k = _positive_normal((2.0 / np.pi) * spherical_kn(ell, KAPPA * r[None, :]), "kbar_l")
        # kbar_-1=kbar_0 follows from K_-1/2=K_1/2.
        km = _positive_normal((2.0 / np.pi) * spherical_kn(np.maximum(ell - 1, 0), KAPPA * r[None, :]), "kbar_(l-1)")
        positive_difference = _positive_normal(i - OFFSET * ip, "i_l-a*i_(l+1)")
        if np.any(positive_difference < 0.67 * i):
            # Exact lower factor101/150>0.6733; this loose guard only detects gross arithmetic/library failures.
            raise ArithmeticError("positive difference violates the fixed-model separation guard")
        result = 4.0 * KAPPA * (positive_difference * k + r[None, :] * i * km)
    return _positive_normal(result, "screen multipoles")


def angular_forcing(radii, lmax):
    """Reduced m=0 source for phi=e^-r/sqrt(pi), before radial quadrature weights."""
    r, ell = _domain(radii, lmax)
    with np.errstate(over="raise", under="raise", divide="raise", invalid="raise"):
        source = (r * np.exp(-r))[None, :] * np.sqrt(2 * ell + 1) * screen_legendre_integrals(r, lmax)
    return _positive_normal(source, "original reduced source")


def derivative_reference(radii, lmax):
    """Algebraically distinct SciPy derivative evaluation, for diagnostics only."""
    r, ell = _domain(radii, lmax)
    with np.errstate(over="raise", under="raise", divide="raise", invalid="raise"):
        i = spherical_in(ell, KAPPA * OFFSET)
        di = spherical_in(ell, KAPPA * OFFSET, derivative=True)
        k = (2.0 / np.pi) * spherical_kn(ell, KAPPA * r[None, :])
        dk = (2.0 / np.pi) * spherical_kn(ell, KAPPA * r[None, :], derivative=True)
        c = KAPPA * i * k
        dc = i * k + KAPPA * OFFSET * di * k + KAPPA * r[None, :] * i * dk
        result = 4.0 * (c - dc)
    return _positive_normal(result, "derivative reference")


def verify():
    """Four independent high-precision angular integrals plus a high-j reference."""
    import mpmath as mp
    started = time.perf_counter()
    records = []
    # High-j64 quad needs enough absolute precision to resolve its tiny moment.
    with mp.workdps(180):
        a, kap = mp.mpf(7) / 10, mp.mpf(2)

        def bessel_coefficient(l, r, z):
            il = mp.sqrt(mp.pi / (2 * z * a)) * mp.besseli(l + mp.mpf(".5"), z * a)
            kl = mp.sqrt(2 / (mp.pi * z * r)) * mp.besselk(l + mp.mpf(".5"), z * r)
            return z * il * kl

        for l, radius in [(0, 27), (1, 28), (16, 44), (64, 27), (128, 65)]:
            r = mp.mpf(radius)
            coefficient = lambda z: bessel_coefficient(l, r, z)
            reference = 4 * (coefficient(kap) - mp.diff(coefficient, kap))
            value = float(screen_legendre_integrals([radius], l)[l, 0])
            relative = abs(mp.mpf(value) / reference - 1)
            if relative >= mp.mpf("5e-12"):
                raise ArithmeticError("binary64 multipole disagrees with high-precision reference")
            record = {"ell": l, "r": radius, "binary64_moment": value,
                      "high_precision_moment": mp.nstr(reference, 80),
                      "relative_difference": mp.nstr(relative, 20)}
            if l != 128:
                def integrand(mu):
                    distance = mp.sqrt(r * r + a * a - 2 * r * a * mu)
                    return 2 * (1 + 1 / distance) * mp.exp(-2 * distance) * mp.legendre(l, mu)
                direct = mp.quad(integrand, [-1, 1])
                direct_relative = abs(direct / reference - 1)
                if direct_relative >= mp.mpf("1e-45"):
                    raise ArithmeticError("direct angular integral disagrees with Yukawa identity")
                record["direct_angular_integral"] = mp.nstr(direct, 80)
                record["direct_integral_relative_difference"] = mp.nstr(direct_relative, 20)
            records.append(record)

    selected_radii = [27, 44, 65]
    positive = screen_legendre_integrals(selected_radii, 128)
    derivative = derivative_reference(selected_radii, 128)
    derivative_difference = float(np.max(np.abs(positive / derivative - 1)))
    if derivative_difference >= 5e-12:
        raise ArithmeticError("positive/derivative formula regression failed")
    full_source = angular_forcing(selected_radii, 128)

    # Quantify the reason the former binary64 quadrature cannot define high-j source input.
    mu, w = np.polynomial.legendre.leggauss(128)
    d = np.sqrt(27.0**2 + OFFSET**2 - 2 * 27.0 * OFFSET * mu)
    v = 2 * (1 + 1 / d) * np.exp(-2 * d)
    p64 = np.polynomial.legendre.legval(mu, np.r_[np.zeros(64), 1.0])
    gauss64 = float(np.sum(w * v * p64))
    actual64 = float(positive[64, 0])

    rejected = 0
    for radii, lmax in [([], 0), ([26], 0), ([66], 0), ([float("nan")], 0),
                         ([27 + 1j], 0), ([27], -1), ([27], 129), ([27], True)]:
        try:
            angular_forcing(radii, lmax)
        except (ValueError, ArithmeticError):
            rejected += 1
        else:
            raise AssertionError("invalid domain accepted")
    return {"schema": "PHYS73_ANALYTIC_SCREEN_CHECK_V1", "backend": backend_metadata(),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "mpmath_version": mp.__version__, "mpmath_dps": 180,
            "direct_angular_integrals": 4, "high_precision_bessel_references": 5,
            "reference_points": records, "selected_grid_values": int(full_source.size),
            "selected_grid_min_source": float(full_source.min()),
            "selected_grid_max_positive_derivative_relative_difference": derivative_difference,
            "invalid_domain_rejections": rejected,
            "gauss128_ell64_r27": {"quadrature_value": gauss64, "positive_formula_value": actual64,
                                  "absolute_difference": abs(gauss64 - actual64),
                                  "quadrature_over_true_magnitude": abs(gauss64 / actual64),
                                  "accepted_as_production_input": False},
            "elapsed_seconds": time.perf_counter() - started,
            "old_panel_integrations": 0, "old_profile_integrations": 0,
            "Coulomb_evaluations": 0, "certified": False,
            "scope": "selected numerical checks of the exact source formula; no uniform floating-point certificate"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("output exists; use a new path")
    record = verify()
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k: v for k, v in record.items() if k != "reference_points"}, indent=2))


if __name__ == "__main__":
    main()
