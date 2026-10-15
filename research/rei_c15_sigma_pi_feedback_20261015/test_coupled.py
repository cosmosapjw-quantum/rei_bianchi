#!/usr/bin/env python3
"""Physical tests: dynamic Sigma orientation, PR140 kinetic massive source,
PR137 photon/neutrino Boltzmann, C13 stellar HHe and Einstein constraints.
"""
from __future__ import annotations
import math
import sys
import unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import coupled as c


class C15EinsteinSourceTests(unittest.TestCase):
    def test_original_BASS_radial_and_PSTF_sha_locked(self):
        info=c.source_identity()
        self.assertEqual(info["PR137_BASS_photon_blob"],
                         "e15e1875fba7fcc4a42e257e291c54d9b540a3f0")
        self.assertEqual(info["PR140_original_massive_blobs"]["vendor_pr140_massive_radial.py"],
                         "0eec2880c9d0d5675938ad516e00039b994ba18a")

    def test_Sigma_input_not_q_and_legacy_only_adapter(self):
        p=c.Parameters(.002,1)
        self.assertEqual(p.Sigma_initial,.002)
        self.assertEqual(p.orientation,1)
        for sigma,ori in ((-.001,1),(.01,0),(0.,1),(.01,-1.5)):
            with self.assertRaises(ValueError):c.Parameters(sigma,ori)
        self.assertEqual(c.EinsteinBoltzmann.legacy_reference_adapter(0.),(0.,0))
        sigma,ori=c.EinsteinBoltzmann.legacy_reference_adapter(-.01)
        self.assertEqual(ori,-1)
        self.assertAlmostEqual(sigma,math.sqrt(3)*.01/math.hypot(1.,.01))

    def test_massive_initial_velocity_kinetic_stress_positive(self):
        p=c.Parameters(0.,0,0.,0.,.1,.5)
        m=c.EinsteinBoltzmann(p)
        source=m.massive.moments(0.,0.,A=.5,imax=2)
        self.assertAlmostEqual(source.j0[0],1.,delta=3e-13)
        self.assertGreater(source.j0[1],0.)
        self.assertGreater(source.j2[0],0.)
        self.assertLess(abs(source.j2[0]),source.j0[1])
        self.assertAlmostEqual(source.j2[0]/source.j0[1],.5/5,delta=8e-13)
        source2=m.massive.moments(0.,0.,A=-.5,imax=2)
        self.assertLess(source2.j2[0],0.)
        with self.assertRaises(ValueError):c.EinsteinBoltzmann(c.Parameters(0.,0,massive_fraction=.8))

    def test_exact_independent_massive_Liouville_energy_stress_identity(self):
        p=c.Parameters(0.,0,.2,.2,.1,.5)
        model=c.EinsteinBoltzmann(p)
        fd=model.massive
        d=1e-6
        # PR140 momentum provider admits x>=0; central differences need x>h.
        for x in (.005,.01,.03):
            for b in (-.001,0.,.001):
                m=fd.moments(x,b,A=.5,imax=2)
                dx=(fd.moments(x+d,b,A=.5,imax=2).j0[0]-
                    fd.moments(x-d,b,A=.5,imax=2).j0[0])/(2*d)
                db=(fd.moments(x,b+d,A=.5,imax=2).j0[0]-
                    fd.moments(x,b-d,A=.5,imax=2).j0[0])/(2*d)
                self.assertLess(abs(dx+3*m.j0[0]+m.j0[1]),2e-8)
                self.assertLess(abs(db+2*m.j2[0]),2e-8)

    def test_closed_Einstein_Vlasov_Raychaudhuri(self):
        p=c.Parameters(0.,0,.2,.2,.1,.5)
        model=c.EinsteinBoltzmann(p)
        src=model.initial()
        proxy=c.Proxy(0.,0.,0.,0.,0.,0.,0.,0.)
        x=.00015;b=2e-8;v=.002
        J=src.moments.copy()
        J[0,2]=.041;J[2,2]=.038
        y=np.r_[b,v,0.,J.ravel()]
        f=model._physical(x,b,v,J,proxy,.5)
        dy=model.rhs(x,y,proxy,0.,.001)
        delta=2e-5
        plus=y+delta*dy;minus=y-delta*dy
        Hp=model._physical(x+delta,plus[0],plus[1],
                            plus[3:].reshape(4,p.L+1),proxy,.5)["H"]
        Hm=model._physical(x-delta,minus[0],minus[1],
                            minus[3:].reshape(4,p.L+1),proxy,.5)["H"]
        lhs=f["H"]*(Hp-Hm)/(2*delta)
        m=model.massive.moments(x,b,A=p.massive_quadrupole,imax=2)
        pbar=model.mass_ref_density*m.j0[1]/3
        dust=model.Ecrit*model.Om*(1-p.massive_fraction)/f["a"]**3
        expected=-c.KAPPA/2*(3*dust+4*(f["E_gamma"]+f["E_nu"])+
                            3*(f["E_massive"]+pbar))-3*f["s"]**2
        self.assertLess(abs(lhs-expected)/abs(expected),2e-7)

    def test_true_radiation_and_matter_stress_generate_shear_from_zero(self):
        source=c.Parameters(0.,0,.2,.2,.1,.5)
        on=c.EinsteinBoltzmann(source).run(nsteps=16)
        f=on["final"]
        self.assertGreater(f["Sigma"],1e-7)
        self.assertEqual(f["orientation"],1)
        self.assertGreater(f["Pi_gamma"],0.)
        self.assertGreater(f["Pi_massive"],0.)
        self.assertGreater(f["s_inv_s"],0.)
        # The gravitational-source-off lane is an intentionally unphysical
        # diagnostic, not asserted to satisfy Vlasov Raychaudhuri identities.
        off=c.EinsteinBoltzmann(c.Parameters(
            0.,0,.2,.2,.1,.5,enable_primordial_pi=False,
            enable_matter_pi=False,enable_ionizing_pi=False)).run(nsteps=16)
        self.assertLess(off["final"]["Sigma"],1e-17)
        self.assertGreater(f["Sigma"]-off["final"]["Sigma"],1e-7)

    def test_independent_primordial_and_BASS_massive_sources(self):
        radiation=c.EinsteinBoltzmann(
             c.Parameters(0.,0,.2,.2,0.,0.)).run(16)
        mass=c.EinsteinBoltzmann(
             c.Parameters(0.,0,0.,0.,.1,.5)).run(16)
        combo=c.EinsteinBoltzmann(
             c.Parameters(0.,0,.2,.2,.1,.5)).run(16)
        self.assertGreater(radiation["final"]["Sigma"],1e-8)
        self.assertGreater(mass["final"]["Sigma"],1e-8)
        self.assertGreater(combo["final"]["Sigma"],mass["final"]["Sigma"])
        self.assertGreater(combo["final"]["Sigma"],radiation["final"]["Sigma"])

    def test_signed_Sigma_orientation_and_normalized_stress(self):
        positive=c.EinsteinBoltzmann(c.Parameters(.002,1,.2,.2,.1,.5)).run(16)
        negative=c.EinsteinBoltzmann(c.Parameters(.002,-1,.2,.2,.1,.5)).run(16)
        self.assertGreater(positive["final"]["s_inv_s"],0.)
        self.assertLess(negative["final"]["s_inv_s"],0.)
        self.assertEqual(positive["final"]["orientation"],1)
        self.assertEqual(negative["final"]["orientation"],-1)
        self.assertGreater(positive["final"]["Sigma"],0)
        self.assertGreater(negative["final"]["Sigma"],0)
        self.assertLess(abs(positive["final"]["Sigma"]-.002),1e-5)
        self.assertLess(abs(negative["final"]["Sigma"]-.002),1e-5)

    def test_actual_native_photo_CaseA_reaction_feedback_and_ledgers(self):
        for sig,ori in ((0.,0),(.002,1),(.002,-1)):
            res=c.EinsteinBoltzmann(c.Parameters(sig,ori,.2,.2,.1,.5)).run(32)
            for name,val in res["errors"].items():
                self.assertLess(val,6e-11,(name,val))
            final=res["final"]
            self.assertGreater(final["source_photons_perH"],0.)
            self.assertGreater(final["remaining_UV_photons_perH"],0.)
            self.assertGreater(final["x_HII"],.4)
            self.assertGreater(final["x_HeII"],.5)
            self.assertGreater(final["Tgas_K"],12000)
            self.assertLessEqual(final["x_HeII"],1)
            self.assertTrue(abs(final["Pi_UV"])>0.)
            self.assertGreater(final["collision_tau"],0.)
            self.assertEqual(final["gamma_number_N0"],1.)
            self.assertEqual(final["nu_number_N0"],1.)

    def test_true_source_off_control_and_compression_source_exact(self):
        p=c.Parameters(0.,0,0.,0.,0.,0.,native_md14_source=False)
        res=c.EinsteinBoltzmann(p).run(16)
        self.assertEqual(res["final"]["source_photons_perH"],0.)
        self.assertEqual(res["final"]["remaining_UV_photons_perH"],0.)
        self.assertEqual(res["final"]["Pi_UV"],0.)
        self.assertLess(res["errors"]["photochemical_number_abs_max"],1e-10)
        p2=c.Parameters(0.,0,.2,.2,.1,.5)
        a=c.EinsteinBoltzmann(p2).run(32,compress=False)
        b=c.EinsteinBoltzmann(p2).run(32,compress=True)
        self.assertLess(abs(a["final"]["Sigma"]-b["final"]["Sigma"]),1e-12)
        self.assertLess(abs(a["final"]["x_HII"]-b["final"]["x_HII"]),1e-8)
        self.assertLess(abs(a["final"]["Tgas_K"]-b["final"]["Tgas_K"]),.001)
        self.assertGreater(a["final"]["UV_packets"],b["final"]["UV_packets"])

    def test_fast_BASS_3moment_vectorized_owner_parity(self):
        p=c.Parameters(0.,0,.2,.2,.1,.5)
        fast=c.EinsteinBoltzmann(p,fast_massive=True)
        original=c.EinsteinBoltzmann(p,fast_massive=False)
        for x in (.00001,.0001,.0003):
            for b in (-.001,0.,.001):
                a=np.asarray(fast.massive_source_3moments(x,b))
                z=np.asarray(original.massive_source_3moments(x,b))
                np.testing.assert_allclose(a,z,rtol=8e-15,atol=2e-15)
        a=fast.run(nsteps=16)
        z=original.run(nsteps=16)
        self.assertLess(abs(a["final"]["Sigma"]-z["final"]["Sigma"]),1e-13)
        self.assertLess(abs(a["final"]["Tgas_K"]-z["final"]["Tgas_K"]),1e-8)

    def test_native_spectral_threshold_source_resolution_in_Einstein(self):
        p=c.Parameters(0.,0,.2,.2,.1,.5)
        values=[c.EinsteinBoltzmann(p,source_grid=g).run(nsteps=32)
                for g in ("4X8","8X8","16X8")]
        for label in ("Tgas_K","x_HII","Sigma"):
            self.assertTrue(all(math.isfinite(r["final"][label]) for r in values))
        # Original Rust source refinement matters to reactive temperature,
        # even while Einstein Sigma source changes remain negligible here.
        self.assertGreater(abs(values[0]["final"]["Tgas_K"]-
                               values[1]["final"]["Tgas_K"]),.001)
        self.assertLess(abs(values[1]["final"]["Tgas_K"]-
                            values[2]["final"]["Tgas_K"]),.1)

    def test_isotropic_shear_direction_numerically_unresolved(self):
        case=c.EinsteinBoltzmann(c.Parameters(0.,0,0.,0.,0.,0.)).run(16)
        end=case["final"]
        self.assertLess(end["Sigma"],1e-13)
        self.assertEqual(end["orientation"],0)
        self.assertEqual(end["orientation_status"],
                         "NUMERICALLY_UNRESOLVED_BELOW_SIGMA_3E-13")

    def test_resolved_stress_shear_constraint_hamiltonian(self):
        model=c.EinsteinBoltzmann(c.Parameters(0.,0,.2,.2,.1,.5))
        st=model.initial()
        proxy=c.Proxy.from_states(st.gas_and_UV,st.gas_and_UV)
        f=model._physical(0.,st.b,st.s/model.H0_ref,st.moments,proxy,0.)
        recon=(model.cosmo.hf(st.a)**2+st.s**2+
               c.KAPPA*(f["delta_radiation"]+f["delta_massive"]+
                         f["E_UV"]+f["E_gas"]))
        self.assertLess(abs(recon-st.H**2)/st.H**2,3e-14)
        self.assertAlmostEqual(f["Sigma"],0.,places=14)

if __name__=="__main__":unittest.main(verbosity=2)
