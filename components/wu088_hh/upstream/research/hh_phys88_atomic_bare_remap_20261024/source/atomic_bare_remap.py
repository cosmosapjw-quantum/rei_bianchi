"""PHYS88 conditional kernel transport and separate relabel/bare event ledgers.

Authority: frozen CONTRACT revision3 and root theory. No physical charge-state
equivalence, uncertainty interval, tail, actual stopping or activation is issued.
Only NativeSource and ScaledBesselSix are reused from the unchanged vendor.
"""
from fractions import Fraction
import math
import numbers

from vendor.phys87_native_moments import NativeSource, ScaledBesselSix

MAPS = ('LAB_ANCHORED', 'FIXED_COM_K')
ROUTES = ('emissivity_handoff', 'immediate_escape')
FIELDS = ('kappa_cm3_per_s', 'mean_Kin_eV', 'mean_Egamma_eV', 'mean_Kd_eV')
NATIVE_SUPPORT = (1e-5, 2e7)
KB_EV_K = 8.617333262145179e-5
C_CM_S = 29979245800.0


class DomainError(ValueError):
    """Refused conditional model input; unavailable values are never clipped."""


def need(condition, message):
    if not condition:
        raise DomainError(message)


def real(value, name):
    need(isinstance(value, numbers.Real) and not isinstance(value, bool), name+':REAL_REQUIRED')
    value = float(value)
    need(math.isfinite(value), name+':FINITE_REQUIRED')
    return value


def activation(production=False):
    need(production is False, 'PRODUCTION_OR_NETWORK_ACTIVATION_NOT_ISSUED')


class MassConvention:
    def __init__(self, tokens):
        f = {k: Fraction(tokens[k]) for k in ('epsilon_n', 'epsilon_p', 'epsilon_d',
             'epsilon_e', 'AWR', 'Q_source', 'Q_bare', 'B_H', 'B_D')}
        need(all(x > 0 for x in f.values()), 'POSITIVE_NOMINAL_MASS_INPUTS_REQUIRED')
        a, b, d, e = (f[k] for k in ('epsilon_n', 'epsilon_p', 'epsilon_d', 'epsilon_e'))
        h = a*f['AWR']; D = a+h-f['Q_source']
        dh, dd = h-b, D-d
        rh, rd = h-(b+e-f['B_H']), D-(d+e-f['B_D'])
        exact = dict(f, epsilon_H_source=h, epsilon_D_source=D,
                     DeltaH=dh, DeltaD=dd, rhoH=rh, rhoD=rd,
                     binding_shift=f['B_D']-f['B_H'], convention_shift=rh-rd)
        self.exact = exact
        self.a, self.b, self.d, self.h, self.D = map(float, (a, b, d, h, D))
        self.Mb, self.Ms = float(a+b), float(a+h)
        self.Qb, self.Qs = float(f['Q_bare']), float(f['Q_source'])
        self.deltaH, self.deltaD = float(dh), float(dd)
        self.residuals = {'bare_Q': a+b-d-f['Q_bare'],
            'Q_difference_vs_shifts': f['Q_source']-f['Q_bare']-(dh-dd),
            'Q_difference_vs_binding_and_convention': f['Q_source']-f['Q_bare']-
                (f['B_D']-f['B_H']+rh-rd),
            'H_shift_decomposition': dh-(e-f['B_H']+rh),
            'D_shift_decomposition': dd-(e-f['B_D']+rd)}

    def record(self):
        return {'nominal_exact_rationals': {k: str(v) for k, v in self.exact.items()},
                'exact_residuals': {k: str(v) for k, v in self.residuals.items()},
                'physical_mass_exactness': False, 'physical_CI': False,
                'reservoir': 'Signed convention/internal accounting; not an on-shell electron or heat source'}


def temperature(value, masses):
    t = real(value, 'T_K')
    need(255 <= t <= 101000000, 'T_OUTSIDE_FROZEN_DOMAIN')
    theta = KB_EV_K*t
    need(min(masses.a, masses.b, masses.d, masses.Mb)/theta >= 1e5, 'BESSEL_Z_DOMAIN')
    return t, theta


class ConditionalMap:
    """Compose source-native interpolation with a monotone named map."""
    def __init__(self, source, masses, map_token=None, *, conditional_transport=False,
                 production=False):
        activation(production)
        need(map_token in MAPS, 'EXPLICIT_SUPPORTED_MAP_TOKEN_REQUIRED')
        need(conditional_transport is True, 'EXPLICIT_CONDITIONAL_TRANSPORT_OPT_IN_REQUIRED')
        self.source, self.masses, self.map = source, masses, map_token

    def _native(self, energies):
        import numpy as np
        need(not isinstance(energies, bool), 'NATIVE_ENERGY_REAL_REQUIRED')
        raw = np.asarray(energies)
        need(raw.dtype.kind in 'iuf' and raw.dtype.kind != 'b', 'NATIVE_ENERGY_REAL_REQUIRED')
        e = raw.astype(float)
        need(np.isfinite(e).all() and ((e >= NATIVE_SUPPORT[0]) &
             (e <= NATIVE_SUPPORT[1])).all(), 'NATIVE_ENERGY_OUTSIDE_SUPPORT_UNAVAILABLE')
        return e

    def kinematics(self, native_Es, *, production=False):
        import numpy as np
        activation(production)
        e = self._native(native_Es); m = self.masses
        target, pair = (m.b, m.Mb) if self.map == MAPS[0] else (m.h, m.Ms)
        root = np.sqrt(pair*pair+2*target*e)
        k = 2*target*e/(root+pair)
        jac = target*e/(pair+k)
        w = m.Mb+k
        eb = e if self.map == MAPS[0] else k*(2*m.Mb+k)/(2*m.b)
        available = m.Qb+k
        recoil = available*available/(2*w)
        photon = available*(2*w-available)/(2*w)
        lam = k*(2*m.Mb+k)*(4*m.a*m.b+2*m.Mb*k+k*k)
        return {'Es_eV': e, 'Eb_eV': eb, 'K_eV': k, 'W_eV': w,
                'eStar_eV': photon, 'kStar_eV': recoil,
                'daughterStar_eV': m.d+recoil, 'lambda_eV4': lam,
                'dK_dlogEs_eV': jac}

    def bare_support(self):
        return [float(v) for v in self.kinematics(NATIVE_SUPPORT)['Eb_eV']]

    def native_from_bare(self, bare_Eb, *, production=False):
        import numpy as np
        activation(production)
        raw = np.asarray(bare_Eb)
        need(raw.dtype.kind in 'iuf' and raw.dtype.kind != 'b', 'BARE_ENERGY_REAL_REQUIRED')
        eb = raw.astype(float); low, high = self.bare_support()
        need(np.isfinite(eb).all() and ((eb >= low) & (eb <= high)).all(),
             'BARE_ENERGY_OUTSIDE_MAPPED_SUPPORT_UNAVAILABLE')
        if self.map == MAPS[0]:
            return eb
        m = self.masses
        k = 2*m.b*eb/(np.sqrt(m.Mb*m.Mb+2*m.b*eb)+m.Mb)
        es = k*(2*m.Ms+k)/(2*m.h)
        # Exact represented endpoint labels, not clipping an outside input.
        es = np.where(eb == low, NATIVE_SUPPORT[0], es)
        return np.where(eb == high, NATIVE_SUPPORT[1], es)

    def evaluate_native(self, native_Es, *, production=False):
        activation(production)
        return self.source.evaluate(self._native(native_Es))

    def evaluate_bare(self, bare_Eb, *, production=False):
        return self.evaluate_native(self.native_from_bare(bare_Eb, production=production),
                                    production=production)


class BareThermalIntegrator:
    """New bare integrals; no call to the parent thermal integrator."""
    def __init__(self, mapped):
        self.mapped = mapped
        self.bessel = ScaledBesselSix()
        self.integration_calls = []
        self.rules = {}

    def integrate(self, T_K, order, *, rate_only=False, production=False):
        import numpy as np
        activation(production)
        m = self.mapped.masses
        t, theta = temperature(T_K, m)
        need(type(order) is int and order in (16, 32), 'GL_ORDER_DOMAIN')
        need(type(rate_only) is bool, 'RATE_ONLY_FLAG_DOMAIN')
        self.integration_calls.append({'map': self.mapped.map, 'T_K': t,
                                       'order': order, 'rate_only': rate_only})
        if order not in self.rules:
            self.rules[order] = np.polynomial.legendre.leggauss(order)
        nodes, weights = self.rules[order]
        need((weights > 0).all(), 'POSITIVE_GL_WEIGHTS_REQUIRED')
        logknots = np.log(np.asarray(self.mapped.source.energies))
        half = (logknots[1:]-logknots[:-1])/2
        center = (logknots[1:]+logknots[:-1])/2
        es = np.exp(center[:, None]+half[:, None]*nodes[None, :])
        sigma, _, _ = self.mapped.evaluate_native(es)
        kin = self.mapped.kinematics(es)
        k, w, eg, kdstar, ed = (kin[key] for key in
            ('K_eV', 'W_eV', 'eStar_eV', 'kStar_eV', 'daughterStar_eV'))
        z = w/theta
        with np.errstate(under='ignore'):
            boltzmann = np.exp(-k/theta)
        mass = (half[:, None]*weights[None, :])*(sigma*1e-24)*kin['lambda_eV4']*\
            self.bessel.scaled(1, z)*boltzmann*kin['dK_dlogEs_eV']
        need(np.isfinite(mass).all() and (mass >= 0).all(), 'INVALID_POSITIVE_NATIVE_CELL_WEIGHTS')
        total = math.fsum(mass.reshape(-1))
        need(total > 0 and math.isfinite(total), 'ZERO_OR_NONFINITE_WINDOW_NORMALIZER')
        prefactor = C_CM_S/(4*m.a**2*m.b**2*theta*float(self.bessel.scaled(2, m.a/theta))*
                            float(self.bessel.scaled(2, m.b/theta)))
        rate = prefactor*total
        need(math.isfinite(rate) and rate > 0, 'INVALID_FINITE_WINDOW_RATE')
        result = {'map': self.mapped.map, 'T_K': t, 'order': order, 'rate_only': rate_only,
            'kappa_cm3_per_s': rate, 'native_intervals': len(half), 'quadrature_points': mass.size,
            'native_Es_support_eV': list(NATIVE_SUPPORT), 'bare_Eb_support_eV': self.mapped.bare_support(),
            'source_interpolation_coordinate': 'ORIGINAL_NATIVE_Es',
            'conditional_transport': True, 'support_policy': 'FINITE_WINDOW_ONLY_OUTSIDE_UNAVAILABLE',
            'underflowed_boltzmann_points': int(np.count_nonzero(boltzmann == 0)),
            'all_underflow_intervals': int(np.count_nonzero(np.all(boltzmann == 0, axis=1))),
            'minimum_pair_z': float(np.min(z))}
        if rate_only:
            return result
        probability = mass/total
        def average(v): return math.fsum((probability*v).reshape(-1))
        g, gm1, vg = self.bessel.boost(z)
        means = (k+w*gm1, eg*g, kdstar+ed*gm1)
        angular_variance = eg*eg*g/z
        within_variances = (w*w*vg, eg*eg*vg+angular_variance, ed*ed*vg+angular_variance)
        averages = [average(v) for v in means]
        variances = [average(within_variances[j]+(means[j]-averages[j])**2) for j in range(3)]
        pairs = ((0, 1), (0, 2), (1, 2))
        within_covariances = (w*eg*vg, w*ed*vg, eg*ed*vg-angular_variance)
        covariances = [average(within_covariances[j]+(means[a]-averages[a])*(means[b]-averages[b]))
                       for j, (a, b) in enumerate(pairs)]
        result.update(dict(zip(FIELDS[1:], averages)))
        result.update(dict(zip(('variance_Kin_eV2', 'variance_Egamma_eV2', 'variance_Kd_eV2'), variances)))
        result.update(dict(zip(('cov_Kin_Egamma_eV2', 'cov_Kin_Kd_eV2', 'cov_Egamma_Kd_eV2'), covariances)))
        un, up, ud = (self.bessel.single_u(eps, theta) for eps in (m.a, m.b, m.d))
        result.update(u_n_eV=un, u_p_eV=up, u_d_eV=ud,
            selected_log_rate_slope=(averages[0]-un-up)/theta,
            energy_identity_residual_eV=math.fsum([averages[0], m.Qb, -averages[1], -averages[2]]),
            conditional_gamma_variance_min=float(np.min(vg)))
        need(all(math.isfinite(v) and v >= 0 for v in variances), 'NONFINITE_OR_NEGATIVE_CENTERED_VARIANCE')
        return result


def owner_row(row, masses, h, route, *, production=False):
    activation(production)
    need(type(h) is int and h in (0, 1), 'OWNER_MEMBERSHIP_DOMAIN')
    need(route in ROUTES, 'EXCLUSIVE_PHOTON_ROUTE_REQUIRED')
    need(row.get('map') in MAPS and row.get('conditional_transport') is True, 'CONDITIONAL_ROW_REQUIRED')
    kin, eg, kd, un, up, ud = [real(row[key], key) for key in
        ('mean_Kin_eV', 'mean_Egamma_eV', 'mean_Kd_eV', 'u_n_eV', 'u_p_eV', 'u_d_eV')]
    columns = [h*kd-kin, (1-h)*kd, -masses.Qb, 0.0,
               eg if route == ROUTES[0] else 0.0, eg if route == ROUTES[1] else 0.0]
    return {'map': row['map'], 'T_K': row['T_K'], 'order': row['order'], 'h': h, 'radiation_route': route,
        'count_columns': {'thermal': h-2, 'fast': 1-h, 'nuclear_total': -1, 'free_electron': 0},
        'energy_columns_eV': dict(zip(('thermal', 'fast', 'nuclear_rest', 'atomic_binding',
                                      'radiation_injected', 'radiation_escape'), columns)),
        'energy_closure_eV': math.fsum(columns),
        'Cv_Tdot_over_R_eV': math.fsum([-kin, un, up, h*(kd-ud)]),
        'interpretation': 'CONDITIONAL_BARE_CAPTURE; h1_INSTANTANEOUS_CALORIC_BIRTH_NOT_STOPPING',
        'network_activation': False}


def boost_z(q, gamma, gamma_beta):
    return [math.fsum([gamma*q[0], gamma_beta*q[3]]), q[1], q[2],
            math.fsum([gamma_beta*q[0], gamma*q[3]])]


def shell_record(q, epsilon):
    squares = [x*x for x in q]
    residual = math.fsum([-squares[0], *squares[1:], epsilon*epsilon])
    scale = math.fsum([*squares, epsilon*epsilon])
    need(scale > 0, 'POSITIVE_SHELL_SCALE_REQUIRED')
    return {'mass_eV': epsilon, 'residual_eV2': residual, 'scale_eV2': scale,
            'scaled_residual': abs(residual)/scale}


def four_vector_record(incoming, outgoing):
    residual = [math.fsum([*(v[j] for v in outgoing), *(-v[j] for v in incoming)]) for j in range(4)]
    scale = math.fsum(abs(v[0]) for v in incoming+outgoing)
    need(scale > 0, 'POSITIVE_FOUR_VECTOR_SCALE_REQUIRED')
    return {'residual_eV': residual, 'S4_eV': scale, 'scaled_residual': max(map(abs, residual))/scale}


def event_vectors(a, target, daughter, Q, E_lab, beta, mu):
    """Fresh target-rest incoming pair followed by the same normal z boost."""
    e, beta, mu = real(E_lab, 'E_lab'), real(beta, 'beta'), real(mu, 'mu')
    need(e > 0 and 0 <= beta < 1 and -1 <= mu <= 1, 'POSITIVE_ENERGY_SUBLUMINAL_BOOST_MU_DOMAIN')
    pair = a+target
    k = 2*target*e/(math.sqrt(pair*pair+2*target*e)+pair)
    w = pair+k
    p = math.sqrt(e*(2*a+e))
    gb_pair = p/w; gamma_pair = (pair+e)/w
    available = Q+k
    photon = available*(2*w-available)/(2*w)
    recoil = available*available/(2*w)
    transverse = photon*math.sqrt((1-mu)*(1+mu))
    photon_com = [photon, transverse, 0.0, photon*mu]
    daughter_com = [daughter+recoil, -transverse, 0.0, -photon*mu]
    gamma = 1/math.sqrt((1-beta)*(1+beta)); gb = gamma*beta
    normal = lambda q: boost_z(q, gamma, gb)
    neutron = normal([a+e, 0.0, 0.0, p])
    target_q = normal([target, 0.0, 0.0, 0.0])
    photon_q = normal(boost_z(photon_com, gamma_pair, gb_pair))
    daughter_q = normal(boost_z(daughter_com, gamma_pair, gb_pair))
    return neutron, target_q, daughter_q, photon_q, {'K_eV': k, 'W_eV': w,
        'pair_four_velocity_normal': [(neutron[j]+target_q[j])/w for j in range(4)]}


def relabel_event(masses, Es, beta, mu):
    Es = real(Es, 'Es')
    need(NATIVE_SUPPORT[0] <= Es <= NATIVE_SUPPORT[1], 'SOURCE_RELABEL_SUPPORT')
    m = masses
    n, H, D, photon, pair = event_vectors(m.a, m.h, m.D, m.Qs, Es, beta, mu)
    UH = [x/m.h for x in H]; UD = [x/m.D for x in D]
    bare_p = [m.b*x for x in UH]; bare_d = [m.d*x for x in UD]
    carrier = [math.fsum([m.deltaH*UH[j], -m.deltaD*UD[j]]) for j in range(4)]
    reservoir = [-x for x in carrier]
    residual = [math.fsum([bare_d[j], photon[j], -n[j], -bare_p[j], -carrier[j]]) for j in range(4)]
    return {'native_Es_eV': Es, 'normal_boost_beta': beta, 'COM_photon_mu': mu,
        'phi_rad': 0, 'kind': 'SAME_SOURCE_EVENT_RELABEL_SIGNED_CARRIER',
        'source_q_n': n, 'source_q_H': H, 'source_q_D': D, 'q_gamma': photon,
        'U_H': UH, 'U_D': UD, 'bare_label_q_p': bare_p, 'bare_label_q_d': bare_d,
        'C_eV': carrier, 'reservoir_delta_eV': reservoir,
        'relabel_residual_eV': residual, 'relabel_max_abs_eV': max(map(abs, residual)),
        'source_four_vector': four_vector_record([n, H], [D, photon]),
        'mass_shells': {'n': shell_record(n, m.a), 'p_label': shell_record(bare_p, m.b),
                        'd_label': shell_record(bare_d, m.d), 'gamma': shell_record(photon, 0.0)},
        'carrier_is_physical_electron_or_heat': False, 'fresh_bare_event': False, **pair}


def bare_event(mapped, Es, beta, mu, *, production=False):
    activation(production)
    k = mapped.kinematics([Es]); eb = float(k['Eb_eV'][0]); m = mapped.masses
    n, p, d, photon, pair = event_vectors(m.a, m.b, m.d, m.Qb, eb, beta, mu)
    sigma, a1, a2 = mapped.evaluate_native([Es])
    pdf = float((1+3*a1[0]*mu+5*a2[0]*(3*mu*mu-1)/2)/2)
    need(pdf >= 0, 'NEGATIVE_TRANSPORTED_ANGULAR_DENSITY')
    return {'map': mapped.map, 'native_Es_eV': Es, 'bare_Eb_eV': eb,
        'normal_boost_beta': beta, 'COM_photon_mu': mu, 'phi_rad': 0,
        'kind': 'FRESH_CLOSED_BARE_EVENT_NO_CARRIER', 'incoming_q_n': n, 'incoming_q_p': p,
        'outgoing_q_d': d, 'q_gamma': photon, 'carrier_added': False,
        'sigma_barn_at_native_Es': float(sigma[0]), 'a1': float(a1[0]), 'a2': float(a2[0]),
        'angular_pdf_per_mu': pdf, 'four_vector': four_vector_record([n, p], [d, photon]),
        'mass_shells': {'n': shell_record(n, m.a), 'p': shell_record(p, m.b),
                        'd': shell_record(d, m.d), 'gamma': shell_record(photon, 0.0)}, **pair}
