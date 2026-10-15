#!/usr/bin/env python3
"""True source-qualified angular CaseA escape transport and Green bound tests."""
from __future__ import annotations
import hashlib
import math
from pathlib import Path
import sys
import unittest

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from escape_transport import (
  CaseABirthRecorder, EscapeBirth, Config, Scenario, NativeStellarSource,
  sharp_per_event, radiation_cloud, angular_moments_fast,
  run_escape_response, get_actual_source, endpoint_source_pressure,
  response_mode, evolved_moments, FixedSourceGeometry, E_QUADRATURE_EV
)
from positive_source_pr144 import Moment,positive_three_atom

class EscapeSourceShear(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p,cls.geom,cls.births=run_escape_response(q_signed=.005,nstep=16,kappa=.2,order=16)
        cls.mn,cls.geom_minus,cls.births_minus=run_escape_response(q_signed=-.005,nstep=16,kappa=.2,order=16)
    def test_original_PR144_actual_sha_exact_source_class(self):
        original=HERE/"suppliers/PR144_qmu_immutable.py"
        src=original.read_text()
        start=src.index("@dataclass(frozen=True)")
        end=src.index("def photon_species_event")
        expected=hashlib.sha256(src[start:end].encode()).hexdigest()
        assert expected=="504ada593d3ad3c7e17bc790da9640d3cd45526d315a74160ede3b05665c2079"
        adapter=(HERE/"positive_source_pr144.py").read_text()
        self.assertIn(src[start:end],adapter)
    def test_source_energy_births_are_real_and_positive(self):
        for p,births in ((self.p,self.births),(self.mn,self.births_minus)):
            self.assertEqual(len(births),16)
            self.assertTrue(all(z.energy_eV_perH>=0 for z in births))
            self.assertTrue(all(z.a<.2 for z in births))
            self.assertAlmostEqual(
              sum(z.energy_eV_perH for z in births),
              p["original_actual_CaseA_emitted_U_eV_perH"],delta=5e-14)
    def test_sharp_cone_analytic_all_metric_signs(self):
        for U in (1.e-12,1e-5,.002134):
            for delta in (-.2,-.025,0.,.025,.2):
                birth=EscapeBirth(.1999,0.,U,0.,"manufactured angular limit, not emission owner")
                final_a=.2
                values=[]
                for kind in ("transverse","axial","PR144_zeroPi","isotropic"):
                    photon=evolved_moments(U,0.,.1999,delta,final_a,kind)
                    self.assertTrue(photon.positive_cone())
                    self.assertLess(abs(photon.cPz),2e-13*U)
                    values.append((kind,photon))
                lo,hi=sharp_per_event(birth,np.array([final_a]),np.array([delta]))
                self.assertAlmostEqual(values[0][1].Pi,float(lo[0]),delta=3e-13*U)
                self.assertAlmostEqual(values[1][1].Pi,float(hi[0]),delta=3e-13*U)
                for _,photon in values:
                    self.assertLessEqual(float(lo[0])-3e-13*U,photon.Pi)
                    self.assertGreaterEqual(float(hi[0])+3e-13*U,photon.Pi)
    def test_extremal_positive_three_atoms_not_signed_negative_flux(self):
        U=2.13e-3
        for kind,Pi in (("transverse",-.5*U),("axial",U),("PR144_zeroPi",0.)):
            src=radiation_cloud(U,kind)
            self.assertTrue(np.all(src.NperH>=0))
            m=Moment.from_sky(src)
            self.assertLess(abs(m.Pi-Pi),3e-13*U)
            self.assertLess(abs(m.cPz),2e-14*U)
        with self.assertRaises(ValueError): positive_three_atom(Moment(U,0,1.001*U))
        with self.assertRaises(ValueError): positive_three_atom(Moment(U,0,-.501*U))
    def test_native_photon_cloud_drift_matches_vectorized_Killing(self):
        for birth in self.births[::3]:
            for x in (.19997,.2):
                if x<birth.a:continue
                for kind in ("transverse","PR144_zeroPi","isotropic","axial"):
                    photon=evolved_moments(
                       birth.energy_eV_perH,birth.b,birth.a,
                       float(self.geom.b_interp(math.log(x))),x,kind)
                    e,p=angular_moments_fast(
                       birth,np.array([x]),np.array([float(self.geom.b_interp(math.log(x)))]),kind)
                    self.assertAlmostEqual(photon.U,float(e[0]),delta=3e-13*birth.energy_eV_perH)
                    self.assertAlmostEqual(photon.Pi,float(p[0]),delta=3e-13*birth.energy_eV_perH)
    def test_endpoint_full_angular_pressure_sharply_bounded(self):
        for _,g,births in ((self.p,self.geom,self.births),(self.mn,self.geom_minus,self.births_minus)):
            lows=endpoint_source_pressure(births,g,"transverse")
            highs=endpoint_source_pressure(births,g,"axial")
            middle=endpoint_source_pressure(births,g,"PR144_zeroPi")
            iso=endpoint_source_pressure(births,g,"isotropic")
            self.assertLess(lows[1],middle[1])
            self.assertLess(middle[1],highs[1])
            self.assertLess(lows[1],iso[1])
            self.assertLess(iso[1],highs[1])
            self.assertLess(abs(lows[1]+lows[0]/2),3e-13)
            self.assertLess(abs(highs[1]-highs[0]),3e-13)
    def test_actual_linear_ode_green_pressure_bounds(self):
        for p in (self.p,self.mn):
            lo=p["source_sharp_lower_shear_signed_per_s"]
            hi=p["source_sharp_upper_shear_signed_per_s"]
            self.assertLess(lo,0)
            self.assertGreater(hi,0)
            for x in p["response_shear_signed_per_s"].values():
                self.assertLessEqual(lo-3e-30,x)
                self.assertGreaterEqual(hi+3e-30,x)
            self.assertTrue(p["conditional_angular_realizations_reproduce_extrema"])
            self.assertEqual(p["scientific_admission"],
                "SCOPED_FIXED_C16_BACKGROUND_SHARP_LINEAR_SOURCE_PRESSURE_RESPONSE_ONLY")
    def test_einstein_angular_total_energy_not_from_unlicensed_escape_spectrum(self):
        for r in (self.p,self.mn):
            self.assertEqual(r["star_emitter_mass_energy_and_escaped_recombination_physical_EOS"],
                             "NOT_ASSIGNED")
            self.assertEqual(r["fully_nonlinear_Einstein_chemistry_backreaction"],
                             "NOT_SOLVED")
            self.assertTrue(r["separately_green_source_and_escaped_radiation_energy_dilution"])
    def test_density_geometry_input_is_positive_real_source(self):
        for g in (self.geom,self.geom_minus):
            a,b,H=g.geometry(np.linspace(g.x[0],g.x[-1],61))
            self.assertTrue(np.all(H>0))
            self.assertTrue(np.all(np.isfinite(b)))
            self.assertTrue(np.all(g.hydrogen_density_cm3(a)>0))
            with self.assertRaises(RuntimeError):g.geometry([g.x[-1]+.1])
    def test_reference_positive_source_to_current_einstein_thermal_unchanged(self):
        for p in (self.p,self.mn):
            self.assertGreater(p["original_actual_CaseA_emitted_U_eV_perH"],.002)
            self.assertLess(p["original_actual_CaseA_emitted_U_eV_perH"],.003)
            self.assertTrue(0<=p["Sigma_base_end"]<.002)

if __name__=="__main__":
    unittest.main(verbosity=2)
