"""PHYS87 source-native, finite-window n+atomic-H1 -> effective-D+gamma.

Equations and acceptance belong to CONTRACT revision2 and the theory note.
No continuum/tail/uncertainty certificate, stopping or network activation.
Numerical dependencies are imported inside called methods, never by resume.
"""
from bisect import bisect_right
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import numbers
import re

RAW_SHA256 = '3024d8f0db604b074e33ed8b05027eb9f5a738614041ba44c83f048e0d0bc1af'
TABLE_SHA256 = 'b14ad9b4a2379166ec2b2c04b2a77efb4c819498924682072d74a6b4e31c5014'
RAW_BYTES = 671232
EPS_N = 939565421.94  # displayed CODATA2022 parent neutron reference, eV
AWR = 0.9991673
EPS_H = AWR * EPS_N
Q = 2224648.0
M = EPS_N + EPS_H
EPS_D = M - Q
C_CM_S = 29979245800.0
KB_EV_K = 8.617333262145179e-5  # exact SI kB/eV quotient, evaluated in binary64
DOMAIN = (1e-5, 2e7)
TEMPERATURE_DOMAIN = (255.0, 101000000.0)
SOURCE_NATIVE = 'ENDF_SOURCE_NATIVE_ATOMIC_EQUIVALENT'
ROUTES = ('emissivity_handoff', 'immediate_escape')


class SourceError(ValueError):
    """Invalid source identity, format or literal transcription."""


class DomainError(ValueError):
    """Unavailable source or model domain; never clips or zero-extends."""


def require(condition, message, error=SourceError):
    if not condition:
        raise error(message)


def finite_scalar(value, label):
    require(isinstance(value, numbers.Real) and not isinstance(value, bool),
            label + ': REAL_NUMBER_REQUIRED', DomainError)
    result = float(value)
    require(math.isfinite(result), label + ': FINITE_REQUIRED', DomainError)
    return result


def require_convention(convention=SOURCE_NATIVE):
    require(convention == SOURCE_NATIVE, 'BARE_NETWORK_OR_OTHER_CONVENTION_UNAVAILABLE', DomainError)


def temperature(value):
    t = finite_scalar(value, 'T_K')
    require(TEMPERATURE_DOMAIN[0] <= t <= TEMPERATURE_DOMAIN[1],
            'T_OUTSIDE_FROZEN_NUMERICAL_DOMAIN', DomainError)
    theta = KB_EV_K * t
    require(all(math.isfinite(z) and z >= 1e5 for z in
                (EPS_N/theta, EPS_H/theta, EPS_D/theta, M/theta)),
            'ASYMPTOTIC_Z_DOMAIN', DomainError)
    return t, theta


def endf_decimal(field):
    raw = field.strip()
    require(bool(raw), 'BLANK_ENDF_NUMBER')
    if 'e' not in raw.lower():
        raw = re.sub(r'(?<=\d)([+-]\d+)$', r'e\1', raw)
    try:
        value = Decimal(raw)
    except Exception as exc:
        raise SourceError('INVALID_ENDF_NUMBER') from exc
    require(value.is_finite(), 'NONFINITE_ENDF_NUMBER')
    return value


def cont(line):
    require(len(line) >= 75, 'SHORT_ENDF_RECORD')
    fields = [line[i:i+11] for i in range(0, 66, 11)]
    values = [endf_decimal(x) if x.strip() else Decimal(0) for x in fields]
    return values


def integral(value, name):
    require(value == value.to_integral_value(), 'NONINTEGER_ENDF_' + name)
    return int(value)


def packed(lines, cursor, count):
    values, literals = [], []
    for _ in range((count+5)//6):
        require(cursor < len(lines), 'TRUNCATED_ENDF_PACKED_VALUES')
        line = lines[cursor]
        for j in range(6):
            if len(values) == count:
                break
            token = line[j*11:(j+1)*11].strip()
            values.append(endf_decimal(token)); literals.append(token)
        cursor += 1
    return values, literals, cursor


def tab1(lines, cursor):
    h = cont(lines[cursor]); cursor += 1
    nr, np_ = integral(h[4], 'NR'), integral(h[5], 'NP')
    interp, _, cursor = packed(lines, cursor, 2*nr)
    data, literals, cursor = packed(lines, cursor, 2*np_)
    return {'header': h, 'interpolation': [(integral(interp[i], 'NBT'), integral(interp[i+1], 'INT'))
                                         for i in range(0, 2*nr, 2)],
            'x': data[::2], 'y': data[1::2], 'x_literal': literals[::2],
            'y_literal': literals[1::2]}, cursor


def tab2(lines, cursor):
    h = cont(lines[cursor]); cursor += 1
    nr = integral(h[4], 'NR')
    interpolation, _, cursor = packed(lines, cursor, 2*nr)
    return h, [(integral(interpolation[i], 'NBT'), integral(interpolation[i+1], 'INT'))
               for i in range(0, 2*nr, 2)], cursor


@dataclass(frozen=True)
class NativeRow:
    energy: Decimal
    sigma: Decimal
    a1: Decimal
    a2: Decimal
    literals: tuple


class NativeSource:
    """Parse canonical bytes and bind every MF3/MF6 row to literal source table."""
    def __init__(self, raw_path, table_path):
        raw = Path(raw_path).read_bytes(); table_bytes = Path(table_path).read_bytes()
        require(len(raw) == RAW_BYTES and hashlib.sha256(raw).hexdigest() == RAW_SHA256,
                'CANONICAL_RAW_BYTES_HASH_MISMATCH')
        require(hashlib.sha256(table_bytes).hexdigest() == TABLE_SHA256,
                'FROZEN_TABLE_HASH_MISMATCH')
        table = json.loads(table_bytes)
        require(table['source_sha256'] == RAW_SHA256 and table['source_bytes'] == RAW_BYTES,
                'TABLE_RAW_BINDING_MISMATCH')
        lines = raw.decode('ascii').splitlines()
        sections = {}
        for mf in (3, 6):
            sections[mf] = [line for line in lines if len(line) >= 75 and
                            line[66:70].strip() == '125' and
                            line[70:72].strip() == str(mf) and line[72:75].strip() == '102']
        require(len(sections[3]) == 54 and len(sections[6]) == 315, 'SECTION_RECORD_COUNT')
        mf3, mf6 = sections[3], sections[6]
        h3, h6 = cont(mf3[0]), cont(mf6[0])
        require(h3[:2] == h6[:2] == [Decimal('1001'), Decimal('0.9991673')],
                'ZA_OR_AWR_MISMATCH')
        cross, cursor3 = tab1(mf3, 1)
        require(cursor3 == len(mf3), 'TRAILING_MF3_RECORD')
        require(cross['header'][:2] == [Decimal('2224648')]*2 and
                cross['header'][2:4] == [Decimal(0)]*2 and
                cross['interpolation'] == [(33, 5), (153, 2)] and len(cross['x']) == 153,
                'MF3_HEADER_OR_INTERPOLATION')
        require(h6[2:] == [Decimal(0), Decimal(2), Decimal(2), Decimal(0)],
                'MF6_FRAME_OR_PRODUCTS')
        photon, cursor6 = tab1(mf6, 1)
        require(photon['header'][:4] == [Decimal(0), Decimal('2223300'), Decimal(0), Decimal(2)],
                'MF6_PHOTON_BRANCH')
        self._yield(photon)
        angular_header, angular_interp, cursor6 = tab2(mf6, cursor6)
        require(angular_header[:4] == [Decimal(0)]*4 and angular_header[5] == 153 and
                angular_interp == [(153, 2)], 'MF6_ANGULAR_TAB2')
        angular = []
        for _ in range(153):
            ah = cont(mf6[cursor6]); cursor6 += 1
            require(ah[0] == 0 and ah[2:4] == [Decimal(0)]*2 and ah[4:] == [Decimal(2)]*2,
                    'MF6_LANG_NL_OR_LIST')
            coeff, literal, cursor6 = packed(mf6, cursor6, 2)
            energy_literal = mf6[cursor6-2][11:22].strip()
            angular.append((ah[1], coeff, literal, energy_literal))
        recoil, cursor6 = tab1(mf6, cursor6)
        require(recoil['header'][:4] == [Decimal(1002), Decimal('1.996256'), Decimal(0), Decimal(4)],
                'MF6_RECOIL_BRANCH')
        self._yield(recoil)
        require(cursor6 == len(mf6), 'TRAILING_MF6_RECORD')
        require(len(table['rows']) == 153, 'TABLE_ROW_COUNT')
        rows = []
        for i, (energy, sigma) in enumerate(zip(cross['x'], cross['y'])):
            a_energy, coeff, literal, a_energy_literal = angular[i]
            saved = table['rows'][i]
            require(energy == a_energy and energy > 0 and sigma > 0, 'ENERGY_OR_SIGMA_SOURCE_DOMAIN')
            require(i == 0 or energy > rows[-1].energy, 'NONINCREASING_NATIVE_GRID')
            exact_tokens = (cross['x_literal'][i], cross['y_literal'][i], literal[0], literal[1])
            require(tuple(saved['raw_ENDF_fields'][k] for k in ('En', 'sigma', 'a1', 'a2')) == exact_tokens,
                    'RAW_LITERAL_ROW_MISMATCH')
            require(a_energy_literal == exact_tokens[0], 'MF3_MF6_ENERGY_LITERAL_MISMATCH')
            require(saved['index1'] == i+1 and
                    [Decimal(saved[k]) for k in ('En_eV', 'sigma_barn', 'a1', 'a2')] ==
                    [energy, sigma, *coeff], 'DECIMAL_TABLE_ROW_MISMATCH')
            rows.append(NativeRow(energy, sigma, coeff[0], coeff[1], exact_tokens))
        require(rows[0].energy == Decimal('1e-5') and rows[-1].energy == Decimal('2e7'),
                'NATIVE_SUPPORT_MISMATCH')
        # Table metadata is checked independently of the row values.
        require(table['MF3_MT102']['NP'] == 153 and table['MF6_MT102']['LCT'] == 2 and
                table['MF6_MT102']['photon']['LAW'] == 2 and
                table['MF6_MT102']['photon']['LANG'] == 0 and
                table['MF6_MT102']['photon']['NL'] == 2 and
                table['MF6_MT102']['recoil']['LAW'] == 4, 'TABLE_BRANCH_METADATA_MISMATCH')
        self.rows = tuple(rows)
        self.energies = tuple(float(row.energy) for row in rows)
        self.sigma_values = tuple(float(row.sigma) for row in rows)
        self.a1_values = tuple(float(row.a1) for row in rows)
        self.a2_values = tuple(float(row.a2) for row in rows)
        self.raw_sha256 = RAW_SHA256

    @staticmethod
    def _yield(record):
        require(record['interpolation'] == [(2, 2)] and
                record['x'] == [Decimal('1e-5'), Decimal('2e7')] and
                record['y'] == [Decimal(1), Decimal(1)], 'PRODUCT_YIELD_NOT_ONE')

    def evaluate(self, energies, convention=SOURCE_NATIVE):
        import numpy as np
        require_convention(convention)
        values = np.asarray(energies, dtype=float)
        require(np.isfinite(values).all() and ((values >= DOMAIN[0]) & (values <= DOMAIN[1])).all(),
                'ENERGY_OUTSIDE_SOURCE_SUPPORT_UNAVAILABLE', DomainError)
        flat = values.reshape(-1)
        grid = np.asarray(self.energies)
        idx = np.searchsorted(grid, flat, side='right')-1
        # Endpoint chooses the last native cell, not an out-of-domain clip.
        idx[flat == grid[-1]] = len(grid)-2
        lo, hi = grid[idx], grid[idx+1]
        sigma = np.asarray(self.sigma_values); a1 = np.asarray(self.a1_values); a2 = np.asarray(self.a2_values)
        fraction = (flat-lo)/(hi-lo)
        sig_lin = sigma[idx] + fraction*(sigma[idx+1]-sigma[idx])
        sig_log = np.exp(np.log(sigma[idx]) + np.log(flat/lo)/np.log(hi/lo)*
                         np.log(sigma[idx+1]/sigma[idx]))
        # NBT=33 means intervals with lower zero-based index0..31 use INT5.
        sig = np.where(idx < 32, sig_log, sig_lin)
        c1 = a1[idx] + fraction*(a1[idx+1]-a1[idx])
        c2 = a2[idx] + fraction*(a2[idx+1]-a2[idx])
        # Return literal source values at all exact represented knots.
        knot = np.searchsorted(grid, flat, side='left')
        hit = (knot < len(grid)) & (grid[knot] == flat)
        sig[hit] = sigma[knot[hit]]; c1[hit] = a1[knot[hit]]; c2[hit] = a2[knot[hit]]
        shape = values.shape
        return sig.reshape(shape), c1.reshape(shape), c2.reshape(shape)

    def angular_pdf(self, energy, mu, convention=SOURCE_NATIVE):
        mu = finite_scalar(mu, 'mu')
        require(-1 <= mu <= 1, 'MU_DOMAIN', DomainError)
        _, a1, a2 = self.evaluate([finite_scalar(energy, 'E_lab')], convention)
        return float((1+3*a1[0]*mu+5*a2[0]*(3*mu*mu-1)/2)/2)

    def positivity_witness(self):
        """Exact represented polynomial minima and whole-cell convex proof data."""
        knots, coefficients = [], []
        for i, row in enumerate(self.rows):
            a1, a2 = Fraction(row.a1), Fraction(row.a2)
            aa, bb, cc = 15*a2/4, 3*a1/2, Fraction(1, 2)-5*a2/4
            points = [Fraction(-1), Fraction(1)]
            if aa > 0 and -1 <= -bb/(2*aa) <= 1:
                points.append(-bb/(2*aa))
            values = [aa*x*x+bb*x+cc for x in points]
            minimum = min(values)
            require(minimum > 0, 'EXACT_ANGULAR_POSITIVITY_FAILED')
            coefficients.append((aa, bb, cc))
            knots.append({'index1': i+1, 'En_eV': str(row.energy),
                          'candidate_mu': [str(x) for x in points],
                          'candidate_f': [str(x) for x in values], 'minimum': str(minimum)})
        cells = []
        for i in range(152):
            left, right = coefficients[i], coefficients[i+1]
            cells.append({'left_index1': i+1, 'right_index1': i+2,
                          'coeff_constant': [str(x) for x in left],
                          'coeff_t': [str(right[j]-left[j]) for j in range(3)],
                          'interpolation': 'f(E,mu)=(1-t)f_left(mu)+t*f_right(mu); t=(E-E_left)/(E_right-E_left) in[0,1]',
                          'left_minimum': knots[i]['minimum'], 'right_minimum': knots[i+1]['minimum'],
                          'whole_cell_positive': True})
        return {'kind': 'EXACT_FRACTION_REPRESENTED_QUADRATIC_AND_CONVEX_COMBINATION',
                'knots': knots, 'cells': cells, 'physical_uncertainty_claim': False}


def poly_coeff(nu):
    require(nu in (1, 2), 'ONLY_BESSEL_ORDERS_1_2', DomainError)
    coefficients = [Fraction(1)]
    for j in range(1, 7):
        coefficients.append(coefficients[-1]*Fraction(4*nu*nu-(2*j-1)**2, 8*j))
    return coefficients


def poly_add(a, b):
    return [(a[i] if i < len(a) else Fraction(0)) +
            (b[i] if i < len(b) else Fraction(0)) for i in range(max(len(a), len(b)))]


def poly_multiply(a, b):
    result = [Fraction(0)]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] += x*y
    return result


def poly_subtract(a, b):
    return poly_add(a, [-x for x in b])


def horner(coefficients, t):
    result = 0.0
    for coefficient in reversed(coefficients):
        result = result*t+float(coefficient)
    return result


class ScaledBesselSix:
    """Terms0..6; exact cancellations happen before binary64 evaluation."""
    def __init__(self):
        self.p1 = poly_coeff(1); self.p2 = poly_coeff(2)
        self.p2_minus_p1 = poly_subtract(self.p2, self.p1)
        self.p1_minus_p2 = [-x for x in self.p2_minus_p1]
        p11 = poly_multiply(self.p1, self.p1)
        p21 = poly_multiply(self.p2, self.p1)
        p22 = poly_multiply(self.p2, self.p2)
        self.variance_numerator = poly_subtract(poly_add(p11, [Fraction(0)]+[3*x for x in p21]), p22)
        require(self.variance_numerator[:2] == [0, 0], 'EXACT_VARIANCE_CANCELLATION')

    @staticmethod
    def _z(z):
        import numpy as np
        z = np.asarray(z, dtype=float)
        require(np.isfinite(z).all() and (z >= 1e5).all(), 'ASYMPTOTIC_Z_DOMAIN', DomainError)
        return z

    def scaled(self, nu, z):
        import numpy as np
        z = self._z(z)
        return np.sqrt(np.pi/(2*z))*horner(self.p1 if nu == 1 else self.p2 if nu == 2 else poly_coeff(nu), 1/z)

    def boost(self, z):
        z = self._z(z); t = 1/z
        p1, p2 = horner(self.p1, t), horner(self.p2, t)
        gm1 = horner(self.p2_minus_p1, t)/p1
        variance = horner(self.variance_numerator, t)/(p1*p1)
        g = p2/p1
        require((variance > 0).all(), 'NONPOSITIVE_CONDITIONAL_GAMMA_VARIANCE')
        return g, gm1, variance

    def single_u(self, epsilon, theta):
        z = self._z(epsilon/theta); t = 1/z
        return float(epsilon*horner(self.p1_minus_p2, t)/horner(self.p2, t)+3*theta)

    def exact_coefficient_record(self):
        return {name: [str(c) for c in value] for name, value in
                [('P1', self.p1), ('P2', self.p2), ('P2_minus_P1', self.p2_minus_p1),
                 ('P1_minus_P2', self.p1_minus_p2), ('variance_numerator', self.variance_numerator)]}


def source_kinematics(energies, convention=SOURCE_NATIVE):
    import numpy as np
    require_convention(convention)
    e = np.asarray(energies, dtype=float)
    require(np.isfinite(e).all() and ((e >= DOMAIN[0]) & (e <= DOMAIN[1])).all(),
            'ENERGY_OUTSIDE_SOURCE_SUPPORT_UNAVAILABLE', DomainError)
    w = np.sqrt(M*M+2*EPS_H*e)
    k = 2*EPS_H*e/(w+M)
    w = M+k
    q = Q+k
    kstar = q*q/(2*w)
    estar = q-kstar
    edstar = EPS_D+kstar
    lam = k*(2*M+k)*(4*EPS_N*EPS_H+2*M*k+k*k)
    return w, k, estar, edstar, kstar, lam


def owner_row(moments, h, route, convention=SOURCE_NATIVE):
    require_convention(convention)
    require(type(h) is int and h in (0, 1), 'OWNER_MEMBERSHIP_DOMAIN', DomainError)
    require(route in ROUTES, 'RADIATION_ROUTE_DOMAIN', DomainError)
    kin, kd, eg = (moments[k] for k in ('mean_Kin_eV', 'mean_Kd_eV', 'mean_Egamma_eV'))
    six = [h*kd-kin, (1-h)*kd, -Q, 0.0,
           eg if route == 'emissivity_handoff' else 0.0,
           eg if route == 'immediate_escape' else 0.0]
    forcing = -kin+moments['u_n_eV']+moments['u_H_eV']+h*(kd-moments['u_D_eV'])
    return {'T_K': moments['T_K'], 'order': moments['order'], 'h': h, 'radiation_route': route,
            'count_columns': {'thermal': h-2, 'fast': 1-h, 'nuclear_total': -1, 'free_electron': 0},
            'energy_columns_eV': dict(zip(('thermal', 'fast', 'nuclear_rest', 'atomic_binding',
                                          'radiation_injected', 'radiation_escape'), six)),
            'energy_closure_eV': math.fsum(six),
            'Cv_Tdot_over_R_eV': forcing,
            'h1_interpretation': 'EXPLICIT_INSTANTANEOUS_CALORIC_BIRTH_NOT_STOPPING',
            'network_activation': False}


class NativeThermalIntegrator:
    def __init__(self, source):
        self.source = source
        self.bessel = ScaledBesselSix()
        self.integration_calls = []
        self._rules = {}

    def integrate(self, t_kelvin, order, *, rate_only=False, convention=SOURCE_NATIVE):
        import numpy as np
        require_convention(convention)
        t_kelvin, theta = temperature(t_kelvin)
        require(type(order) is int and order in (16, 32), 'QUADRATURE_ORDER_DOMAIN', DomainError)
        require(type(rate_only) is bool, 'RATE_ONLY_FLAG_DOMAIN', DomainError)
        self.integration_calls.append({'T_K': t_kelvin, 'order': order, 'rate_only': rate_only})
        if order not in self._rules:
            x, weights = np.polynomial.legendre.leggauss(order)
            require((weights > 0).all(), 'NONPOSITIVE_GAUSS_WEIGHTS')
            self._rules[order] = x, weights
        x, weights = self._rules[order]
        logs = np.log(np.asarray(self.source.energies))
        half = (logs[1:]-logs[:-1])/2
        center = (logs[1:]+logs[:-1])/2
        log_e = center[:, None]+half[:, None]*x[None, :]
        e = np.exp(log_e)
        sigma, _, _ = self.source.evaluate(e, convention)
        w, k, estar, edstar, kstar, lam = source_kinematics(e, convention)
        z = w/theta
        with np.errstate(under='ignore'):
            boltzmann = np.exp(-k/theta)
        b1 = self.bessel.scaled(1, z)
        jacobian = EPS_H*e/w
        mass = (half[:, None]*weights[None, :])*(sigma*1e-24)*lam*b1*jacobian*boltzmann
        require(np.isfinite(mass).all() and (mass >= 0).all(), 'INVALID_POSITIVE_NATIVE_WEIGHTS')
        total = math.fsum(mass.reshape(-1))
        require(total > 0 and math.isfinite(total), 'FINITE_WINDOW_ZERO_OR_NONFINITE_NORMALIZER')
        prefactor = C_CM_S/(4*EPS_N**2*EPS_H**2*theta*
                                    float(self.bessel.scaled(2, EPS_N/theta))*
                                    float(self.bessel.scaled(2, EPS_H/theta)))
        rate = prefactor*total
        require(math.isfinite(rate) and rate > 0, 'INVALID_FINITE_WINDOW_RATE')
        record = {'T_K': t_kelvin, 'order': order, 'rate_only': rate_only,
                  'kappa_cm3_per_s': rate, 'native_intervals': len(half),
                  'quadrature_points': mass.size,
                  'underflowed_boltzmann_points': int(np.count_nonzero(boltzmann == 0)),
                  'all_boltzmann_underflow_intervals': int(np.count_nonzero(np.all(boltzmann == 0, axis=1))),
                  'minimum_pair_z': float(np.min(z)),
                  'source_support_eV': list(DOMAIN),
                  'support_policy': 'FINITE_WINDOW_ONLY; OUTSIDE_UNAVAILABLE; NO_ZERO_EXTENSION_OR_TAIL_BOUND'}
        if rate_only:
            return record
        normalized = mass/total
        def average(value):
            return math.fsum((normalized*value).reshape(-1))
        g, gm1, var_g = self.bessel.boost(z)
        means = (k+w*gm1, estar*g, kstar+edstar*gm1)
        var_k = w*w*var_g
        angular_variance = estar*estar*g/z
        variances = (var_k, estar*estar*var_g+angular_variance,
                     edstar*edstar*var_g+angular_variance)
        means_total = [average(v) for v in means]
        variances_total = [average(variances[j]+(means[j]-means_total[j])**2) for j in range(3)]
        within_cov = (w*estar*var_g, w*edstar*var_g, estar*edstar*var_g-angular_variance)
        covariances = [average(within_cov[j]+(means[a]-means_total[a])*(means[b]-means_total[b]))
                       for j, (a, b) in enumerate(((0, 1), (0, 2), (1, 2)))]
        un, uh, ud = (self.bessel.single_u(eps, theta) for eps in (EPS_N, EPS_H, EPS_D))
        record.update(dict(zip(('mean_Kin_eV', 'mean_Egamma_eV', 'mean_Kd_eV'), means_total)))
        record.update(dict(zip(('variance_Kin_eV2', 'variance_Egamma_eV2', 'variance_Kd_eV2'), variances_total)))
        record.update(dict(zip(('cov_Kin_Egamma_eV2', 'cov_Kin_Kd_eV2', 'cov_Egamma_Kd_eV2'), covariances)))
        record.update(u_n_eV=un, u_H_eV=uh, u_D_eV=ud,
                      selected_log_rate_slope=(means_total[0]-un-uh)/theta,
                      energy_identity_residual_eV=math.fsum([means_total[0], Q, -means_total[1], -means_total[2]]),
                      conditional_gamma_variance_min=float(np.min(var_g)))
        require(all(v > 0 and math.isfinite(v) for v in variances_total), 'NONPOSITIVE_TOTAL_VARIANCE')
        return record


def conditional_angular_case(source, energy, beta, c_axis):
    """Compare actual positive4x8 angular rule with analytic polynomial moments."""
    import numpy as np
    energy = finite_scalar(energy, 'E_lab'); beta = finite_scalar(beta, 'boost_beta')
    c_axis = finite_scalar(c_axis, 'c_axis')
    require(0 <= beta < 1 and -1 <= c_axis <= 1, 'CONDITIONAL_BOOST_DOMAIN', DomainError)
    _, a1, a2 = source.evaluate([energy]);a1, a2 = float(a1[0]), float(a2[0])
    w, k, estar, edstar, kstar, _ = [float(v[0]) for v in source_kinematics([energy])]
    gamma = 1/math.sqrt((1-beta)*(1+beta))
    # Stable gamma-1; no subtraction of two near-one values.
    gm1 = beta*beta*gamma*gamma/(gamma+1)
    kin = k+w*gm1
    mu, glw = np.polynomial.legendre.leggauss(4)
    phi = np.arange(8)*(2*math.pi/8)
    nu = c_axis*mu[:, None]+math.sqrt(1-c_axis*c_axis)*np.sqrt(1-mu[:, None]**2)*np.cos(phi)[None, :]
    f = (1+3*a1*mu+5*a2*(3*mu*mu-1)/2)/2
    weights = glw[:, None]*f[:, None]*np.ones((1, 8))/8
    require((weights > 0).all(), 'NONPOSITIVE_ANGULAR_RULE_WEIGHT')
    def avg(x):return math.fsum((weights*x).reshape(-1))
    norm = math.fsum(weights.reshape(-1))
    eg = gamma*estar*(1+beta*nu)
    kd = kstar+gm1*edstar-gamma*beta*estar*nu
    mean_nu = a1*c_axis
    second_nu = (1-a2+3*a2*c_axis*c_axis)/3
    eg_expected = gamma*estar*(1+beta*mean_nu)
    kd_expected = kstar+gm1*edstar-gamma*beta*estar*mean_nu
    var_expected = (gamma*beta*estar)**2*(second_nu-mean_nu*mean_nu)
    eg_mean, kd_mean = avg(eg), avg(kd)
    raw = {'normalization': norm-1, 'mean_nu': avg(nu)-mean_nu,
           'second_nu': avg(nu*nu)-second_nu,
           'mean_Egamma_eV': eg_mean-eg_expected, 'mean_Kd_eV': kd_mean-kd_expected,
           'variance_Egamma_eV2': avg((eg-eg_mean)**2)-var_expected,
           'variance_Kd_eV2': avg((kd-kd_mean)**2)-var_expected}
    scaled = {key: abs(value)/max(1.0, abs({'normalization': 1.0, 'mean_nu': mean_nu,
              'second_nu': second_nu, 'mean_Egamma_eV': eg_expected, 'mean_Kd_eV': kd_expected,
              'variance_Egamma_eV2': var_expected, 'variance_Kd_eV2': var_expected}[key])) for key, value in raw.items()}
    closure = np.abs(kin+Q-kd-eg)
    return {'E_lab_eV': energy, 'boost_beta': beta, 'c_axis': c_axis,
            'a1': a1, 'a2': a2, 'mu_points': 4, 'azimuth_points': 8,
            'positive_weight_min': float(np.min(weights)), 'mean_nu': avg(nu), 'second_nu': avg(nu*nu),
            'mean_Egamma_eV': eg_mean, 'mean_Kd_eV': kd_mean,
            'variance_Egamma_eV2': avg((eg-eg_mean)**2),
            'raw_residuals': raw, 'relative_or_scaled_residuals': scaled,
            'maximum_scaled_residual': max(scaled.values()),
            'maximum_event_closure_abs_eV': float(np.max(closure)),
            'degree_argument': 'Normalized degree2 f; nu moments through degree2. Four-point GL integrates mu-polynomial degree<=7; eight azimuth nodes integrate Fourier modes through2 exactly in exact arithmetic.'}
