#!/usr/bin/env python3
"""Point-only checks of the actual Coulomb Dirichlet Green kernel.

No radial integration, angular quadrature, inherited panel replay, or original
source solve is performed. Numerical point checks support implementation and
normalization only; the all-j inequalities have separate analytic proofs.

Radial derivatives use NIST DLMF 33.4.4, with d/dr = k d/d(rho):
X'_rho = ((ell+1)/rho + eta/(ell+1)) X_ell
         - sqrt(1 + eta**2/(ell+1)**2) X_(ell+1).
Primary source inspected 2026-10-20: https://dlmf.nist.gov/33.4#E4
"""
from functools import lru_cache
import json
import mpmath as mp
import sys

mp.mp.dps = 60
B = mp.mpf(27)
k = mp.mpf(7) / 10
eta_c = -mp.mpf(10) / 7
ells = (0, 20, 64, 128)
radii = (27, 28, 29)
tolerance = mp.mpf('1e-45')


def out(x):
    return mp.nstr(x, 62)


def out_complex(z):
    return {'real': out(mp.re(z)), 'imag': out(mp.im(z))}


@lru_cache(maxsize=None)
def fg(ell, r):
    rho = k * r
    return mp.coulombf(ell, eta_c, rho), mp.coulombg(ell, eta_c, rho)


@lru_cache(maxsize=None)
def point(ell, r):
    f, g = fg(ell, r)
    f_next, g_next = fg(ell + 1, r)
    order = mp.mpf(ell + 1)
    s = order / (k * r) + eta_c / order
    factor = mp.sqrt(1 + (eta_c / order) ** 2)
    fp = k * (s * f - factor * f_next)
    gp = k * (s * g - factor * g_next)
    return f, g, fp, gp


def phi_and_derivative(ell, r):
    fb, gb, _, _ = point(ell, 27)
    f, g, fp, gp = point(ell, r)
    return (f * gb - g * fb) / k, (fp * gb - gp * fb) / k


def h_and_derivative(ell, r):
    f, g, fp, gp = point(ell, r)
    return mp.mpc(g, f), mp.mpc(gp, fp)


def green(ell, r, s):
    lo, hi = min(r, s), max(r, s)
    phi, _ = phi_and_derivative(ell, lo)
    h, _ = h_and_derivative(ell, hi)
    hb, _ = h_and_derivative(ell, 27)
    return phi * h / hb


points = []
channels = []
failures = []
for ell in ells:
    for r in radii:
        h, hp = h_and_derivative(ell, r)
        flux = mp.im(mp.conj(h) * hp)
        residual = abs(flux - k)
        points.append({'ell': ell, 'r': r, 'rho': out(k * r),
                       'H_plus': out_complex(h),
                       'H_prime_radial': out_complex(hp),
                       'wronskian_flux': out(flux),
                       'wronskian_abs_residual': out(residual)})
        if residual > tolerance:
            failures.append(f'wronskian_ell{ell}_r{r}')
    phi_b, phip_b = phi_and_derivative(ell, 27)
    hb, _ = h_and_derivative(ell, 27)
    values = []
    for r, s in ((27, 29), (28, 29)):
        z = green(ell, r, s)
        z_swapped = green(ell, s, r)
        upper = mp.mpf(45) * min(r, s) ** 3
        symmetry = abs(z - z_swapped)
        ratio = abs(z) / upper
        values.append({'r': r, 's': s, 'green': out_complex(z),
                       'symmetry_abs_residual': out(symmetry),
                       'pointwise_upper_45_min_cubed': out(upper),
                       'abs_green_over_pointwise_upper': out(ratio)})
        if symmetry > tolerance or ratio > 1:
            failures.append(f'kernel_ell{ell}_r{r}_s{s}')
    jumps = []
    for s in (28, 29):
        phi, phip = phi_and_derivative(ell, s)
        h, hp = h_and_derivative(ell, s)
        jump = (phi * hp - phip * h) / hb
        error = abs(jump + 1)
        jumps.append({'s': s, 'right_minus_left_derivative_jump': out_complex(jump),
                      'jump_plus_one_abs_residual': out(error)})
        if error > tolerance:
            failures.append(f'jump_ell{ell}_s{s}')
    if abs(phi_b) > tolerance or abs(phip_b - 1) > tolerance:
        failures.append(f'boundary_ell{ell}')
    channels.append({'ell': ell, 'phi_B': out(phi_b),
                     'phi_prime_B': out(phip_b),
                     'boundary_derivative_abs_residual': out(abs(phip_b - 1)),
                     'kernels': values, 'jumps': jumps})

result = {
    'schema': 'PHYS72_ACTUAL_COULOMB_GREEN_POINT_CHECK_V1',
    'status': 'PASS_SCOPED_POINT_CHECKS' if not failures else 'FAIL_POINT_CHECKS',
    'scope': 'Actual Coulomb functions and exact Green formula at 12 requested channel/radius points; not an all-j or continuum numerical certificate.',
    'B': '27', 'k': '7/10', 'E_hartree': '49/200', 'eta_C': '-10/7',
    'outgoing': 'H_plus=G+iF_C', 'operator': '-d_r^2+ell(ell+1)/r^2-2/r-k^2',
    'normalization': 'phi(B)=0; phi_prime(B)=1; Green derivative jump=-1',
    'precision_decimal_digits': mp.mp.dps, 'mpmath_version': mp.__version__,
    'tolerance': out(tolerance),
    'derivative_primary_source': 'https://dlmf.nist.gov/33.4#E4',
    'derivative_source_checked_date_utc': '2026-10-20',
    'requested_channel_radius_points': len(points),
    'actual_FG_channel_radius_pairs_including_derivative_auxiliary': fg.cache_info().currsize,
    'scalar_Coulomb_function_evaluations': 2 * fg.cache_info().currsize,
    'radial_integrations': 0, 'angular_quadratures': 0,
    'inherited_panel_or_profile_integrations': 0,
    'frozen_NPZ_used': False, 'HH_R10': 'OFF',
    'max_wronskian_abs_residual': out(max(mp.mpf(p['wronskian_abs_residual']) for p in points)),
    'max_boundary_derivative_abs_residual': out(max(mp.mpf(c['boundary_derivative_abs_residual']) for c in channels)),
    'max_jump_plus_one_abs_residual': out(max(mp.mpf(j['jump_plus_one_abs_residual']) for c in channels for j in c['jumps'])),
    'max_symmetry_abs_residual': out(max(mp.mpf(g['symmetry_abs_residual']) for c in channels for g in c['kernels'])),
    'max_abs_green_over_pointwise_upper': out(max(mp.mpf(g['abs_green_over_pointwise_upper']) for c in channels for g in c['kernels'])),
    'points': points, 'channels': channels, 'failures': failures,
}
print(json.dumps(result, indent=2))
raise SystemExit(0 if not failures else 1)
