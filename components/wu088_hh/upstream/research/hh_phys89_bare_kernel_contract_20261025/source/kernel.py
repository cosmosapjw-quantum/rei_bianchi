"""PHYS89 finite interfaces. No integration, old map evaluation or PSD repair.

Exact Decimal/Fraction leaves describe the displayed ENDF table, not a physical
uncertainty guarantee. JointEvent and manufactured_fixture are bookkeeping only.
"""
from bisect import bisect_right
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import math
import re

SOURCE_SHA = '3024d8f0db604b074e33ed8b05027eb9f5a738614041ba44c83f048e0d0bc1af'


def endf_decimal(token):
    text = token.strip()
    if not text:
        raise ValueError('EMPTY_ENDF_NUMBER')
    if 'e' not in text.lower():
        text = re.sub(r'(?<=\d)([+-]\d+)$', r'E\1', text)
    value = Decimal(text)
    if not value.is_finite():
        raise ValueError('NONFINITE_ENDF_NUMBER')
    return value


def parse_mf33(path):
    raw = Path(path).read_bytes()
    if len(raw) != 671232 or hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('IMMUTABLE_SOURCE_IDENTITY_MISMATCH')
    records = [line for line in raw.decode('ascii').splitlines()
               if len(line) >= 75 and line[66:70].strip() == '125'
               and line[70:72].strip() == '33' and line[72:75].strip() == '102']
    fields = [[line[i:i+11] for i in range(0, 66, 11)] for line in records]
    if len(fields) < 4:
        raise ValueError('MISSING_MF33_SECTION')
    header = [endf_decimal(x) for x in fields[0]]
    sub = [endf_decimal(x) for x in fields[1]]
    control = [endf_decimal(x) for x in fields[2]]
    if header[5] != 1 or sub[2:] != [0, 102, 0, 1] or control[2:] != [1, 5, 11935, 154]:
        raise ValueError('MF33_FROZEN_STRUCTURE_MISMATCH')
    all_tokens = [x for row in fields[3:] for x in row]
    tokens = all_tokens[:11935]
    if len(tokens) != 11935 or any(endf_decimal(t) != 0 for t in all_tokens[11935:] if t.strip()):
        raise ValueError('MF33_LIST_LENGTH_OR_PADDING')
    values = [endf_decimal(x) for x in tokens]
    boundaries, packed = values[:154], values[154:]
    if len(packed) != 11781 or any(a >= b for a, b in zip(boundaries, boundaries[1:])):
        raise ValueError('MF33_BOUNDARIES_OR_PACKING')
    if (boundaries[0], boundaries[-1]) != (Decimal('0.000005'), Decimal('20250000')):
        raise ValueError('MF33_BOUNDARY_ENDPOINTS')
    matrix = [[Decimal(0)]*153 for _ in range(153)]
    k = 0
    for i in range(153):
        for j in range(i, 153):
            matrix[i][j] = matrix[j][i] = packed[k]
            k += 1
    return {'boundaries': boundaries, 'packed': packed, 'matrix': matrix,
            'raw_tokens': tokens, 'float_matrix': [[float(x) for x in row] for row in matrix]}


def native_bin(energy, boundaries, support=(Decimal('0.00001'), Decimal('20000000'))):
    """Classify canonical source energy once; no roundtrip/epsilon correction."""
    e = energy if isinstance(energy, Decimal) else Decimal(str(energy))
    if not e.is_finite() or not support[0] <= e <= support[1]:
        raise ValueError('OUTSIDE_NATIVE_SIGMA_SUPPORT')
    if e < boundaries[0] or e > boundaries[-1]:
        raise ValueError('OUTSIDE_COVARIANCE_SUPPORT')
    return min(bisect_right(boundaries, e)-1, len(boundaries)-2)


def mapped_bin(mapped_energy, forward_boundaries, mapped_support):
    """Use pre-supplied monotone forward boundaries, never evaluate an old map."""
    if any(a >= b for a, b in zip(forward_boundaries, forward_boundaries[1:])):
        raise ValueError('NONMONOTONE_FORWARD_BOUNDARIES')
    return native_bin(mapped_energy, forward_boundaries, mapped_support)


def pullback(sigma_source, sigma_source_prime, canonical_bin, canonical_bin_prime, matrix):
    if not (0 <= canonical_bin < len(matrix) and 0 <= canonical_bin_prime < len(matrix)):
        raise ValueError('INVALID_CANONICAL_BIN')
    if not all(math.isfinite(float(x)) and x >= 0 for x in (sigma_source, sigma_source_prime)):
        raise ValueError('INVALID_CROSS_SECTION')
    return sigma_source*sigma_source_prime*matrix[canonical_bin][canonical_bin_prime]


def finite(values):
    if not all(math.isfinite(float(x)) for x in values):
        raise ValueError('NONFINITE_INPUT')


def dot(a, b):
    if len(a) != len(b):
        raise ValueError('DIMENSION_MISMATCH')
    return sum((x*y for x, y in zip(a, b)), 0)


def covariance(rows, matrix):
    n = len(matrix)
    if any(len(row) != n for row in matrix) or any(len(row) != n for row in rows):
        raise ValueError('DIMENSION_MISMATCH')
    finite([x for row in [*rows, *matrix] for x in row])
    return [[sum((a[i]*matrix[i][j]*b[j] for i in range(n) for j in range(n)), 0)
             for b in rows] for a in rows]


def normalized(r, rewards, matrix):
    finite([*r, *(x for row in rewards for x in row)])
    z = sum(r)
    if any(x < 0 for x in r) or z <= 0 or any(len(a) != len(r) for a in rewards):
        raise ValueError('INVALID_FINITE_FUNCTIONAL')
    means = [sum(a)/z for a in rewards]
    sensitivity = [[(x-m*y)/z for x, y in zip(a, r)] for a, m in zip(rewards, means)]
    return {'Z': z, 'A': [sum(a) for a in rewards], 'M': means, 'B': sensitivity,
            'linear_covariance': covariance([r, *rewards], matrix),
            'delta_covariance': covariance(sensitivity, matrix)}


def ratio_change(r, reward, eta, rho):
    finite([*r, *reward, *eta, rho])
    z = sum(r)
    if z <= 0 or any(x < 0 for x in r) or not 0 <= rho < 1:
        raise ValueError('INVALID_RATIO_DOMAIN')
    m = sum(reward)/z
    dz, da = dot(r, eta), dot(reward, eta)
    if z+dz <= 0 or abs(dz) > rho*z:
        raise ValueError('DENOMINATOR_OR_REMAINDER_DOMAIN')
    linear = (da-m*dz)/z
    exact = (da-m*dz)/(z+dz)
    return {'deltaZ': dz, 'deltaA': da, 'linear': linear, 'exact': exact,
            'remainder': exact-linear, 'bound': rho/(1-rho)*abs(linear)}


@dataclass(frozen=True)
class JointEvent:
    Kin_eV: object
    Qb_eV: object
    Kd_eV: object
    Egamma_eV: object
    h: object
    r_gamma: object
    incoming_neutron_thermal: bool = True
    incoming_proton_thermal: bool = True

    def __post_init__(self):
        finite(self.__dict__.values())
        if min(self.Kin_eV, self.Qb_eV, self.Kd_eV, self.Egamma_eV) < 0:
            raise ValueError('NEGATIVE_UNSIGNED_EVENT_ENERGY')
        if not 0 <= self.h <= 1 or not 0 <= self.r_gamma <= 1:
            raise ValueError('EVENT_PARTITION_OUTSIDE_UNIT_INTERVAL')
        if self.Kin_eV+self.Qb_eV != self.Kd_eV+self.Egamma_eV:
            raise ValueError('EVENT_ENERGY_DOES_NOT_CLOSE')

    def signed_energy(self):
        self._caloric_ownership()
        return [self.h*self.Kd_eV-self.Kin_eV, (1-self.h)*self.Kd_eV,
                -self.Qb_eV, 0*self.Qb_eV, self.r_gamma*self.Egamma_eV, (1-self.r_gamma)*self.Egamma_eV]

    def counts(self):
        self._caloric_ownership()
        return {'thermal': self.h-2, 'fast': 1-self.h, 'electron': 0}

    def caloric(self, u_n, u_p, u_d):
        self._caloric_ownership()
        finite([u_n, u_p, u_d])
        return -self.Kin_eV+u_n+u_p+self.h*(self.Kd_eV-u_d)

    def _caloric_ownership(self):
        if self.incoming_neutron_thermal is not True or self.incoming_proton_thermal is not True:
            raise ValueError('BOTH_INCOMING_THERMAL_OWNERS_REQUIRED')


def capture_temperature_derivative(caloric_source_eV_m3_s, species_n_m3, species_du_dT_eV_K):
    """Capture contribution only; expansion/work and other processes are separate."""
    finite([caloric_source_eV_m3_s, *species_n_m3, *species_du_dT_eV_K])
    if any(n < 0 for n in species_n_m3):
        raise ValueError('NEGATIVE_SPECIES_DENSITY')
    cv = dot(species_n_m3, species_du_dT_eV_K)
    if cv <= 0:
        raise ValueError('NONPOSITIVE_HEAT_CAPACITY')
    return caloric_source_eV_m3_s/cv


@dataclass(frozen=True)
class ClockDensity:
    nHref_m3: object
    theta_per_s: object
    dnHref_per_m3_s: object
    lapse: object

    def __post_init__(self):
        finite(self.__dict__.values())
        if self.nHref_m3 <= 0 or self.lapse <= 0:
            raise ValueError('INVALID_DENSITY_OR_LAPSE')

    def yield_proper(self, source_per_m3_s, Y, conserved=False):
        finite([source_per_m3_s, Y])
        drift = self.theta_per_s+self.dnHref_per_m3_s/self.nHref_m3
        if conserved and drift != 0:
            raise ValueError('REFERENCE_NOT_EXACTLY_CONSERVED')
        return source_per_m3_s/self.nHref_m3-Y*drift

    def coordinate_from_proper(self, derivative):
        finite([derivative])
        return self.lapse*derivative

    def packet(self, rate_per_m3_s, delta_tau_s):
        finite([rate_per_m3_s, delta_tau_s])
        if rate_per_m3_s < 0 or delta_tau_s < 0:
            raise ValueError('NEGATIVE_PACKET_RATE_OR_DURATION')
        return rate_per_m3_s*delta_tau_s/self.nHref_m3

    def energy_density_SI(self, energy_eV_per_Href):
        finite([energy_eV_per_Href])
        return energy_eV_per_Href*self.nHref_m3*Q('1.602176634e-19')


def density_cm3_to_m3(value):
    finite([value])
    if value <= 0:
        raise ValueError('NONPOSITIVE_DENSITY')
    return value*1000000


def manufactured_fixture():
    """Explicitly manufactured rational three-group PSD covariance, not source F."""
    r = list(map(Q, [2, 3, 5]))
    # Gram matrix of rows (1/10,0,0), (1/20,1/10,0), (0,1/20,1/10).
    f = [[Q(1,100), Q(1,200), Q(0)], [Q(1,200), Q(1,80), Q(1,200)],
         [Q(0), Q(1,200), Q(1,80)]]
    events = [JointEvent(Q(k), Q(4), Q(k,2), Q(4)+Q(k,2), h, h)
              for k, h in zip([1, 2, 3], [Q(0), Q(1,2), Q(1)])]
    energies = [e.signed_energy() for e in events]
    rewards = [[r[g]*energies[g][a] for g in range(3)] for a in range(6)]
    stats = normalized(r, rewards, f)
    clock = ClockDensity(Q(2000000), Q(3), Q(-6000000), Q(2,3))
    return {'label': 'MANUFACTURED_NOT_SOURCE_OR_PHYSICAL_RATE', 'r': r, 'F': f,
            'energy_per_event': energies, 'reward_rows': rewards, 'statistics': stats,
            'counts': [e.counts() for e in events],
            'caloric': [e.caloric(Q(3,2), Q(3,2), Q(3,2)) for e in events],
            'ratio': ratio_change(r, rewards[0], [Q(1,100), Q(-1,200), Q(1,300)], Q(1,10)),
            'clock': {'Y_proper': clock.yield_proper(Q(12), Q(1,3), conserved=True),
                      'Y_coordinate': clock.coordinate_from_proper(clock.yield_proper(Q(12), Q(1,3), conserved=True)),
                      'packet': clock.packet(Q(12), Q(5)), 'energy_density_J_m3': clock.energy_density_SI(Q(7)),
                      'density_m3': density_cm3_to_m3(Q(2))}}
