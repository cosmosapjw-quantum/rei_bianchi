#!/usr/bin/env python3
"""C16 exact positive angular cone, original native C11 Qmu and C15 real escrow."""
from __future__ import annotations
import math, sys, unittest
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import qmu as q


class QmuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cos=q.c13.Scenario(q.c13.ROOT)
        cls.source=q.c13.NativeStellarSource.load(
            cls.cos,q.ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
        cls.gas=q.c13.initial_gas(cls.cos,.1999)

    def test_arbitrary_positive_three_atom_construction(self):
        rng=np.random.default_rng(1012)
        for _ in range(300):
            u=float(rng.uniform(.001,120))
            m=float(rng.uniform(-.99,.99))
            v=m*m+(1-m*m)*float(rng.uniform(0,1))
            original=q.Moment(u,m*u,.5*(3*v-1)*u)
            self.assertTrue(original.positive_cone())
            photon=q.positive_three_atom(original,energy_eV=40.)
            after=q.Moment.from_sky(photon)
            self.assertAlmostEqual(after.U,original.U,delta=3e-12*u)
            self.assertAlmostEqual(after.cPz,original.cPz,delta=3e-12*u)
            self.assertAlmostEqual(after.Pi,original.Pi,delta=3e-12*u)
            self.assertAlmostEqual(photon.number,u/40,delta=3e-12*u/40)

    def test_sharp_nonidentifiability_even_with_exact_number_and_flux(self):
        U=.002134217081027237
        choices=(q.Moment(U,0.,U),q.Moment(U,0.,-U/2),
                 q.Moment(U,0.,0.))
        clouds=[q.positive_three_atom(z,energy_eV=30) for z in choices]
        self.assertTrue(all(abs(s.number-U/30)<1e-15 for s in clouds))
        self.assertTrue(all(abs(q.Moment.from_sky(s).cPz)<1e-16 for s in clouds))
        self.assertAlmostEqual(q.Moment.from_sky(clouds[0]).Pi,U,delta=1e-16)
        self.assertAlmostEqual(q.Moment.from_sky(clouds[1]).Pi,-U/2,delta=1e-16)
        self.assertAlmostEqual(q.Moment.from_sky(clouds[2]).Pi,0.,delta=1e-16)
        # This is an information-theoretic counterexample, not a spectrum
        # proposal: original Case A knows Uesc, not even photon number.
        self.assertGreater(choices[0].Pi-choices[1].Pi,0.)

    def test_reject_unphysical_moment_sources(self):
        for bad in (q.Moment(-1,0,0),q.Moment(1,0,1.001),
                    q.Moment(1,0,-.501),q.Moment(1,1.1,.2),
                    q.Moment(1,.8,-.4),q.Moment(0,.1,0),
                    q.Moment(float("nan"),0,0)):
            self.assertFalse(bad.positive_cone())
            with self.assertRaises(ValueError):q.positive_three_atom(bad)
        self.assertTrue(q.Moment(0.,0.,0.).positive_cone())
        self.assertEqual(q.positive_three_atom(q.Moment(0.,0.,0.)).packet_count,0)

    def test_symmetry_C11_real_source_photo_local_Q0_Qz(self):
        sky=self.source.birth(.02)
        record=q.native_C11_Qmu(self.gas,sky,dt=1e10)
        self.assertGreater(record["photo_absorbed_energy_eV_perH"],0.)
        self.assertGreater(record["true_CaseA_scalar_escape_eV_perH"],0.)
        self.assertLess(abs(record["required_baryon_recoil_cPz_eV_perH"]),1e-12)
        self.assertLess(abs(record["energy_exchange_residual_eV_perH"]),1e-11)
        self.assertLess(abs(record["electron_photon_ledger_residual_perH"]),1e-11)
        self.assertEqual(record["CaseA_escape_Qz_and_Pi"],
                         "NOT_DETERMINED_BY_ORIGINAL_OWNER")
        for rec in (record["first_photo"],record["last_photo"]):
            self.assertEqual(len(rec["species_energy_eV_cm3"]),3)
            self.assertEqual(len(rec["species_cPz_eV_cm3"]),3)
            self.assertGreater(rec["Q0_to_gas_eV_cm3"],0.)

    def test_real_MD14_directed_source_requires_material_momentum_impulse(self):
        native=self.source.birth(.02)
        weights=native.NperH*(1+.8*native.mu)
        altered=q.c13.PhotonCloud(native.E,native.mu,weights)
        before=q.Moment.from_sky(altered)
        self.assertAlmostEqual(altered.number,native.number,delta=1e-15)
        self.assertGreater(before.cPz,.05)
        result=q.native_C11_Qmu(self.gas,altered,1e10)
        self.assertGreater(result["required_baryon_recoil_cPz_eV_perH"],.001)
        self.assertLess(result["required_baryon_recoil_cPz_eV_perH"],.002)
        self.assertLess(abs(result["energy_exchange_residual_eV_perH"]),1e-11)
        self.assertEqual(result["baryon_velocity_recoil"],
                         "NOT_EVOLVED_BY_C11_CASEA")

    def test_C15_live_UV_photon_cone_and_stellar_reservoir(self):
        for sig,ori in ((0.,0),(.002,1),(.002,-1)):
            r=q.C15_escrow_and_escape_bound(
                q.c15.Parameters(sig,ori,.2,.2,.1,.5),nsteps=32)
            self.assertLess(r["max_real_photochemical_energy_ledger_eV_perH"],1e-11)
            self.assertLess(r["max_real_photochemical_number_ledger_perH"],1e-11)
            self.assertLess(r["max_reflection_symmetric_UV_flux_abs_eV_perH"],1e-12)
            self.assertGreater(r["CaseA_escape_cumulative_energy_eV_perH"],0.)
            self.assertTrue(all(z["positive_radiation_moment_cone"]
                                for z in r["history"]))
            self.assertTrue(all(z["emitted_MD14_energy_this_step_eV_perH"]>=0
                                for z in r["history"]))
            self.assertGreater(r["linearized_omitted_escape_stress_absolute_delta_Sigma_bound"],0)
            self.assertLess(r["linearized_omitted_escape_stress_absolute_delta_Sigma_bound"],1e-12)
            self.assertEqual(r["physics_gate"],"CASEA_SPECTRUM_ANGULAR_MOMENTS_NOT_ADMITTED")

    def test_linearized_escape_bound_short_interval_grid_stability(self):
        p=q.c15.Parameters(0.,0,.2,.2,.1,.5)
        vals=[q.C15_escrow_and_escape_bound(p,nsteps=n) for n in (16,32,64)]
        self.assertTrue(all(v["linearized_omitted_escape_stress_absolute_delta_Sigma_bound"]<1e-12
                            for v in vals))
        self.assertLess(abs(vals[0]["linearized_omitted_escape_stress_absolute_delta_Sigma_bound"]-
                            vals[-1]["linearized_omitted_escape_stress_absolute_delta_Sigma_bound"]),
                        1e-18)

if __name__=="__main__":unittest.main(verbosity=2)
