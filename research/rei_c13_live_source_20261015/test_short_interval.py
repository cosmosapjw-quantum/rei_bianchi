#!/usr/bin/env python3
"""Executed finite-source, background, atomic, exact-source and stress tests."""
import hashlib,math,sys,unittest
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from short_interval import (
    Background,Family,NativeStellarSource,Scenario,PhotonCloud,
    SourceState,ROOT,START,STOP,run,initial_gas,drift_state,
    independent_scalar_killing, c10, EV_CM3_TO_PA)

class LiveC13(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=Scenario(ROOT)
        cls.sources={name:NativeStellarSource.load(
            cls.model,HERE/f"NATIVE_SOURCE_{name}.csv")
            for name in ("4X8","8X8","16X8","32X8","8X16")}
    def test_rust_native_md14_spectral_mu_and_perH_rate(self):
        for name,s in self.sources.items():
            self.assertEqual(s.source_id,"MD14_Z002_FESC_BB50K_13P6_100_V1")
            self.assertAlmostEqual(float(s.weights.sum()),1.,places=13)
            self.assertLess(s.normalization_relative_residual,1e-7)
            self.assertEqual(s.grid_rate.shape,(17,4))
            self.assertAlmostEqual(s.nh0,self.model.nh,delta=5e-20)
            self.assertLess(abs(np.dot(s.weights,s.mu)),1e-14)
            self.assertLess(abs(np.dot(s.weights,s.mu**2)-1/3),2e-14)
    def test_killing_scalar_independent_signed_shear_and_inverse(self):
        rng=np.random.default_rng(34)
        es=rng.uniform(13.6,100.,257)
        mu=rng.uniform(-.999,.999,257)
        n=rng.uniform(.001,1.,257)
        sky=PhotonCloud(es,mu,n)
        for dx,db in ((1e-6,3e-8),(.03,-.01),(.02,0.)):
            fast=sky.drift(dx,db)
            slow=np.array([independent_scalar_killing(float(e),float(m),dx,db)
                           for e,m in zip(es,mu)])
            np.testing.assert_allclose(fast.E,slow[:,0],rtol=9e-16,atol=0)
            np.testing.assert_allclose(fast.mu,slow[:,1],rtol=9e-16,atol=0)
            np.testing.assert_allclose(fast.drift(0.,-db).drift(0.,db).E,fast.E,rtol=3e-15)
            self.assertEqual(sky.number,fast.number)
            if db==0.:
                np.testing.assert_array_equal(fast.mu,mu)
                np.testing.assert_allclose(fast.E/es,math.exp(-dx),rtol=2e-15)
    def test_expansion_gas_thermal_a_minus_2_and_photon_N_per_H(self):
        a0=.1999;a1=.2;m=self.model
        g=initial_gas(m,a0)
        N=np.array([.5,.15])
        s=SourceState(a0,g,PhotonCloud(np.array([20.,80.]),np.array([-.3,.7]),N))
        oldT=g.temperature_K
        for q in (0.,-.01,.01):
            new=drift_state(s,a1,Background(Family(q)))
            self.assertAlmostEqual(new.gas.temperature_K/oldT,(a0/a1)**2,delta=4e-14)
            self.assertAlmostEqual(new.gas.nH/m.nh*a1**3,1.,delta=5e-14)
            self.assertEqual(new.photons.number,s.photons.number)
            self.assertLess(abs(new.energy_ledger()-s.energy_ledger()),1e-12)
            self.assertLess(abs(new.number_ledger()-s.number_ledger()),1e-12)
            self.assertGreaterEqual(new.geometry_work_eV_perH,0.)
    def test_zero_source_prevents_photon_birth(self):
        case=run(0.,self.sources["4X8"],nstep=12,source_scale=0.)
        self.assertEqual(case["end"]["source_N_perH"],0.)
        self.assertEqual(case["end"]["photon_N_perH"],0.)
        self.assertEqual(case["end"]["Pi_ion_Pa"],0.)
        self.assertEqual(case["source_midpoint_relative_error"],0.)
        self.assertLess(case["end"]["x_HII"],.4)
        self.assertLess(case["max_energy_eV_perH_residual"],2e-11)
    def test_born_photons_coupled_H_He_and_exact_number_energy(self):
        for q in (0.,-.005,.005,-.01,.01):
            result=run(q,self.sources["8X8"],nstep=16)
            final=result["end"]
            self.assertGreater(final["x_HII"],.4)
            self.assertGreater(final["x_HeII"],.5)
            self.assertGreater(final["Tgas_K"],12000.)
            self.assertGreater(final["photon_N_perH"],0.)
            self.assertGreater(final["source_N_perH"],final["photon_N_perH"])
            self.assertGreater(final["geometry_work_eV_perH"],0.)
            self.assertGreater(final["escape_E_eV_perH"],0.)
            self.assertGreater(final["thomson_tau"],0.)
            self.assertLess(result["max_number_abs_residual"],3e-13)
            self.assertLess(result["max_energy_eV_perH_residual"],3e-11)
            self.assertLess(result["source_midpoint_relative_error"],2e-9)
            self.assertEqual(final["packet_count"],16*2*192)
    def test_time_refinement_observed_second_order(self):
        xs=[run(0.,self.sources["8X8"],nstep=n) for n in (16,32,64)]
        for field in ("x_HII","Tgas_K","photon_N_perH"):
            gaps=[abs(a["end"][field]-b["end"][field]) for a,b in zip(xs,xs[1:])]
            self.assertGreater(gaps[0]/gaps[1],2.9)
            self.assertLess(gaps[0]/gaps[1],4.5)
    def test_native_spectral_source_refinement_second_order(self):
        results=[run(0.,self.sources[name],nstep=64) for name in ("8X8","16X8","32X8")]
        for key in ("x_HII","Tgas_K","photon_N_perH"):
            old=abs(results[0]["end"][key]-results[1]["end"][key])
            new=abs(results[1]["end"][key]-results[2]["end"][key])
            self.assertGreater(old/new,3.5)
            self.assertLess(old/new,4.5)

    def test_Pi_ion_actual_new_source_and_sourced_CMB_stress_separate(self):
        q0=run(0.,self.sources["8X8"],nstep=16)["end"]
        pos=run(.01,self.sources["8X8"],nstep=16)["end"]
        neg=run(-.01,self.sources["8X8"],nstep=16)["end"]
        self.assertEqual(q0["shear_orientation"],0)
        self.assertLess(abs(q0["Pi_ion_Pa"]),1e-30)
        self.assertEqual(pos["shear_orientation"],1)
        self.assertEqual(neg["shear_orientation"],-1)
        self.assertGreater(pos["Sigma"],0)
        self.assertAlmostEqual(pos["Sigma"],neg["Sigma"],places=14)
        self.assertLess(pos["Pi_ion_Pa"],0)
        self.assertGreater(neg["Pi_ion_Pa"],0)
        self.assertLess(pos["Pi_CMB_source_Pa"],0)
        self.assertGreater(neg["Pi_CMB_source_Pa"],0)
        self.assertLess(abs(pos["Pi_ion_Pa"]/pos["Pi_CMB_source_Pa"]),1e-10)
        self.assertLess(abs(neg["Pi_ion_Pa"]/neg["Pi_CMB_source_Pa"]),1e-10)
    def test_invalid_sources_and_no_extrapolation(self):
        s=self.sources["8X8"]
        with self.assertRaises(ValueError):s.birth(-1.)
        with self.assertRaises(ValueError):run(0.4,s,nstep=3)
        with self.assertRaises(ValueError):run(0.,s,nstep=0)
        with self.assertRaises(ValueError):run(0.,s,nstep=4,a_start=.2,a_end=.2)
        with self.assertRaises(ValueError):run(0.,s,nstep=4,source_scale=-1.)
        with self.assertRaises(ValueError):run(0.,s,nstep=4,a_start=.04,a_end=.2)

if __name__=="__main__":unittest.main(verbosity=2)
