"""Independent Gaussian polynomial controls, not a replay of INTAKE01 tests."""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import finite_drift as fd


def fixture(*, power=-1, drift=0.04, ta=5000.0, tb=15000.0,
            ma=1.6e-27, mb=6.6e-27, na=2.0e6, nb=7.0e6):
    t = fd.PAIR.relative_temperature(ta, tb, ma, mb)
    mu = ma * mb / (ma + mb)
    s2 = fd.PAIR.KB_J_K * t / mu
    s = math.sqrt(s2)
    amplitude = 1.0e-16 if power == -1 else 1.0e-24
    # Direct gamma integral for sigma_1(g)=amplitude*g**power.
    q11 = amplitude * (math.sqrt(2.0) * s) ** power * math.gamma(3.0 + power / 2.0) / 2.0
    q12 = amplitude * (math.sqrt(2.0) * s) ** power * math.gamma(4.0 + power / 2.0) / 6.0
    kwargs = dict(
        T_H_K=ta, T_He_K=tb, n_H_m3=na, n_He_m3=nb,
        mass_H_kg=ma, mass_He_kg=mb,
        velocity_H_m_s=(drift * s, 0.0, 0.0), velocity_He_m_s=(0.0, 0.0, 0.0),
        q11_m2=q11, q12_m2=q12, q11_temperature_K=t, q12_temperature_K=t,
        q11_value_evidence="manufactured exact gamma integral",
        q12_value_evidence="manufactured exact gamma integral",
        mass_binding_evidence="synthetic masses; no isotope source claim",
        same_law_evidence=f"one manufactured sigma1=Lambda*g^{power}",
        maximum_drift_ratio=0.2,
        small_drift_contract="manufactured polynomial control; no physical remainder claim",
    )
    return kwargs, dict(mu=mu, s2=s2, amplitude=amplitude,
                        ca=ma/(ma+mb), cb=mb/(ma+mb), C=na*nb*mu,
                        beta=mu*(ta-tb)/((ma+mb)*t))


class DriftTests(unittest.TestCase):
    def close(self, actual, expected, rel=4.0e-13, scale=None):
        norm = abs(expected) if scale is None else scale
        self.assertLessEqual(abs(actual-expected), rel*norm if norm else 0.0,
                             (actual, expected, norm))

    def test_constant_rate_exact_gaussian_integral(self):
        args, w = fixture(power=-1)
        out = fd.conditional_h_he_drift(**args)
        u = args['velocity_H_m_s'][0]
        # A=Lambda U and div A=3 Lambda, integrated before Taylor expansion.
        heat_a = w['C'] * w['amplitude'] * (w['cb']*u*u - 3*w['beta']*w['s2'])
        heat_b = w['C'] * w['amplitude'] * (w['ca']*u*u + 3*w['beta']*w['s2'])
        self.close(out.centered_heat_H_W_m3, heat_a)
        self.close(out.centered_heat_He_W_m3, heat_b)
        self.close(out.force_H_N_m3[0], -w['C']*w['amplitude']*u)

    def test_growing_rate_exact_remainders_and_scaling(self):
        residuals = []
        for drift in (0.12, 0.06):
            args, w = fixture(power=1, drift=drift)
            out = fd.conditional_h_he_drift(**args)
            u = args['velocity_H_m_s'][0]
            a_dot_u = w['amplitude'] * (u*u + 5*w['s2']) * u*u
            div_a = w['amplitude'] * (5*u*u + 15*w['s2'])
            exact_a = w['C'] * (w['cb']*a_dot_u - w['beta']*w['s2']*div_a)
            exact_b = w['C'] * (w['ca']*a_dot_u + w['beta']*w['s2']*div_a)
            exact_force = -w['C']*w['amplitude']*(u*u+5*w['s2'])*u
            da = exact_a-out.centered_heat_H_W_m3
            db = exact_b-out.centered_heat_He_W_m3
            dr = exact_force-out.force_H_N_m3[0]
            self.close(da, w['C']*w['amplitude']*w['cb']*u**4, rel=2e-8)
            self.close(db, w['C']*w['amplitude']*w['ca']*u**4, rel=2e-8)
            self.close(dr, -w['C']*w['amplitude']*u**3, rel=2e-10)
            residuals.append((da, db, dr))
        self.close(residuals[1][0]/residuals[0][0], 1/16, rel=3e-8)
        self.close(residuals[1][1]/residuals[0][1], 1/16, rel=3e-8)
        self.close(residuals[1][2]/residuals[0][2], 1/8, rel=3e-10)

    def test_equal_temperature_mass_partition_and_energy(self):
        args, w = fixture(ta=10000.0, tb=10000.0)
        out = fd.conditional_h_he_drift(**args)
        self.assertEqual(out.heat_exchange_H_W_m3, 0.0)
        self.close(out.quadratic_heat_H_W_m3, w['cb']*out.drift_dissipation_W_m3)
        self.close(out.quadratic_heat_He_W_m3, w['ca']*out.drift_dissipation_W_m3)
        self.close(out.centered_heat_H_W_m3+out.centered_heat_He_W_m3,
                   out.drift_dissipation_W_m3)
        self.close(out.bulk_power_W_m3, -out.drift_dissipation_W_m3)
        self.close(out.energy_balance_residual_W_m3, 0.0, scale=out.drift_dissipation_W_m3)

    def test_unequal_temperature_signed_quadratic_correction(self):
        args, w = fixture(power=1, ta=20000.0, tb=100.0, ma=1e-27, mb=4e-27)
        # r=3 is supplied by the positive same-law sigma1(g) proportional to g^12.
        args['q12_m2'] = 3.0*args['q11_m2']
        args['same_law_evidence'] = "manufactured g^12 law normalized to supplied Q11"
        out = fd.conditional_h_he_drift(**args)
        self.assertLess(out.quadratic_heat_H_W_m3, 0.0)
        self.close(out.quadratic_heat_H_W_m3+out.quadratic_heat_He_W_m3,
                   out.drift_dissipation_W_m3)

    def test_galilean_invariance_and_raw_energy_transform(self):
        args, _ = fixture(power=1)
        first = fd.conditional_h_he_drift(**args)
        boost = (100.0, -40.0, 25.0)
        shifted = dict(args)
        shifted['velocity_H_m_s'] = tuple(x-w for x,w in zip(args['velocity_H_m_s'], boost))
        shifted['velocity_He_m_s'] = tuple(x-w for x,w in zip(args['velocity_He_m_s'], boost))
        second = fd.conditional_h_he_drift(**shifted)
        self.close(first.centered_heat_H_W_m3, second.centered_heat_H_W_m3)
        self.close(first.centered_heat_He_W_m3, second.centered_heat_He_W_m3)
        self.close(second.raw_kinetic_H_W_m3,
                   first.raw_kinetic_H_W_m3-math.fsum(x*w for x,w in zip(first.force_H_N_m3,boost)))

    def test_reversal_even_heat_odd_force(self):
        args, _ = fixture(power=1)
        first = fd.conditional_h_he_drift(**args)
        args['velocity_H_m_s'] = tuple(-x for x in args['velocity_H_m_s'])
        second = fd.conditional_h_he_drift(**args)
        self.assertEqual(first.centered_heat_H_W_m3, second.centered_heat_H_W_m3)
        self.assertEqual(first.force_H_N_m3, tuple(-x for x in second.force_H_N_m3))

    def test_species_interchange(self):
        args, _ = fixture(power=1)
        first = fd.conditional_h_he_drift(**args)
        other = dict(args)
        for a,b in [('T_H_K','T_He_K'),('n_H_m3','n_He_m3'),('mass_H_kg','mass_He_kg'),
                    ('velocity_H_m_s','velocity_He_m_s')]:
            other[a],other[b] = args[b],args[a]
        second = fd.conditional_h_he_drift(**other)
        self.close(first.centered_heat_H_W_m3, second.centered_heat_He_W_m3)
        self.close(first.quadratic_heat_H_W_m3, second.quadratic_heat_He_W_m3)
        self.close(first.force_H_N_m3[0], second.force_He_N_m3[0])

    def test_zero_drift_reuses_existing_pair_result(self):
        args,_ = fixture(drift=0.0)
        out = fd.conditional_h_he_drift(**args)
        self.assertEqual(out.centered_heat_H_W_m3, out.heat_exchange_H_W_m3)
        self.assertEqual(out.centered_heat_He_W_m3, -out.heat_exchange_H_W_m3)
        self.assertEqual(out.quadratic_heat_H_W_m3, 0.0)
        self.assertEqual(out.force_H_N_m3, (0.0,0.0,0.0))

    def test_caloric_adapter_and_count_ownership(self):
        args,_ = fixture(ta=10000.0, tb=10000.0)
        out = fd.conditional_h_he_drift(**args)
        self.close(1.5*args['n_H_m3']*fd.PAIR.KB_J_K*out.temperature_rate_H_K_s,
                   out.centered_heat_H_W_m3)
        self.close(1.5*args['n_He_m3']*fd.PAIR.KB_J_K*out.temperature_rate_He_K_s,
                   out.centered_heat_He_W_m3)
        self.assertEqual(out.particle_source_H_m3_s+out.particle_source_He_m3_s,0.0)
        self.assertEqual(out.binding_energy_source_W_m3,0.0)
        self.assertEqual(out.nonthermal_energy_source_W_m3,0.0)
        self.assertFalse(out.physical_provider_admitted)
        self.assertFalse(out.remainder_bound_certified)
        json.dumps(out.to_dict(), allow_nan=False)

    def test_absent_species_has_no_temperature_rhs(self):
        args,_ = fixture(na=0.0)
        out = fd.conditional_h_he_drift(**args)
        self.assertIsNone(out.temperature_rate_H_K_s)
        self.assertEqual(out.temperature_rate_He_K_s, 0.0)
        self.assertEqual(out.drift_dissipation_W_m3, 0.0)

    def test_invalid_evidence_temperatures_and_numbers(self):
        args,_ = fixture()
        bad_values = {
            'q12_m2':[True,0.0,-1.0,float('nan'),float('inf'),'1'],
            'q12_temperature_K':[args['q12_temperature_K']+1.0],
            'q12_value_evidence':['',None], 'same_law_evidence':['',True],
            'small_drift_contract':[''], 'maximum_drift_ratio':[0.0,1.0,float('inf'),True],
            'mass_H_kg':[10**400], 'T_H_K':[10**400], 'n_H_m3':[10**400],
            'velocity_H_m_s':[(1.0,2.0),(1.0,2.0,float('nan')),(True,0.0,0.0)],
        }
        for key, values in bad_values.items():
            for value in values:
                with self.subTest(key=key,value=value), self.assertRaises(ValueError):
                    fd.conditional_h_he_drift(**dict(args, **{key:value}))

    def test_declared_small_drift_domain_is_enforced(self):
        args,_ = fixture(drift=0.3)
        with self.assertRaises(ValueError):
            fd.conditional_h_he_drift(**args)

    def test_underflow_and_overflow_are_rejected(self):
        args,_ = fixture()
        with self.assertRaises(ValueError):
            fd.conditional_h_he_drift(**dict(args,velocity_H_m_s=(1e-200,0.0,0.0)))
        with self.assertRaisesRegex(ValueError, "dissipation underflowed"):
            fd.conditional_h_he_drift(**dict(args,velocity_H_m_s=(1e-150,0.0,0.0)))
        with self.assertRaises(ValueError):
            fd.conditional_h_he_drift(**dict(args,velocity_H_m_s=(1e308,1e308,0.0)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
