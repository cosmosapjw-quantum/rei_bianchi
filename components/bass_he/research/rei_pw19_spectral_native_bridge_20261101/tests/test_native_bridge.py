#!/usr/bin/env python3
"""Focused deterministic science tests; assertions survive python -O."""
import json, math, sys, unittest
from pathlib import Path
DIR=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(DIR))
import spectral_native_bridge as m

class NativeSpectralBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=m.compute()
    def test_exact_source_identity(self):
        self.assertEqual(m.spectra.sha(m.spectra.ZIP.read_bytes()),m.spectra.ZIP_SHA)
        self.assertEqual(self.a["native_source_array_sha256"],m.SOURCE_STATE)
    def test_source_member_rows_and_zero(self):
        s=m.spectra.read_source()
        self.assertEqual(len(s[m.spectra.Z0]["E"]),626)
        self.assertEqual(len(s[m.spectra.Z1]["E"]),626)
        for z in (m.spectra.Z0,m.spectra.Z1):
            zeros=[i for i,v in enumerate(s[z]["I"]) if v==0]
            self.assertEqual(zeros,[290])
            self.assertEqual(s[z]["E"][290],48.355849560166504)
    def test_verified_verner_parameters(self):
        self.assertEqual(m.spectra.VERNER["HI"],(13.60,5.0e4,.4298,5.475e4,32.88,2.963,0.,0.,0.))
        self.assertEqual(m.spectra.VERNER["HeI"],(24.59,5.0e4,13.61,949.2,1.469,3.188,2.039,.4434,2.136))
        self.assertEqual(m.spectra.VERNER["HeII"],(54.42,5.0e4,1.720,1.369e4,32.88,2.963,0.,0.,0.))
    def test_thresholds_and_fit_upper(self):
        for k,(e,_,*_) in m.spectra.VERNER.items():
            self.assertEqual(m.spectra.cross(e*.999,k),0.0)
            self.assertGreater(m.spectra.cross(e,k),0)
            self.assertEqual(m.spectra.cross(50001,k),0)
    def test_three_band_photon_support(self):
        for s in m.SCENARIOS:
            rows=self.a["source_scenarios"][s]["bands"]
            self.assertEqual(len(rows),3)
            self.assertEqual(rows[0]["source_photoionizations_per_s"]["HeI"],0.0)
            self.assertEqual(rows[0]["source_photoionizations_per_s"]["HeII"],0.0)
            self.assertEqual(rows[1]["source_photoionizations_per_s"]["HeII"],0.0)
            self.assertGreater(rows[2]["source_photoionizations_per_s"]["HeII"],0)
    def test_hydrogen_low_band_dominance(self):
        a=self.a["source_scenarios"]["z5p95_log"]
        frac=a["bands"][0]["source_photoionizations_per_s"]["HI"]/a["species"]["HI"]["photoionizations_per_s"]
        self.assertGreater(frac,.93)
        self.assertLess(frac,.94)
    def test_three_species_native_frozen_counts(self):
        for s,v in self.a["neutral_counts"].items():
            self.assertGreater(v,0)
        self.assertEqual(self.a["native_cells_reused"],46080)
        self.assertAlmostEqual(self.a["native_frozen_z"],5.95,places=12)
    def test_energy_ownership_closure(self):
        for s in m.SCENARIOS:
            row=self.a["source_scenarios"][s]
            x=row["global"]
            self.assertTrue(math.isclose(x["excess_heat_erg_s"]+x["binding_energy_storage_rate_erg_s"],
                          x["absorbed_photon_power_erg_s"],rel_tol=3e-15))
            for v in row["species"].values():
                self.assertTrue(math.isclose(v["photo_excess_heat_erg_s"]+
                     v["ionization_binding_energy_storage_erg_s"],v["absorbed_photon_power_erg_s"],rel_tol=3e-15))
    def test_photon_density_cgs_conversion(self):
        for s in m.SCENARIOS:
            for b in self.a["source_scenarios"][s]["bands"]:
                self.assertTrue(math.isclose(b["isotropic_photon_number_density_cm3"]*m.C_CGS,
                                 b["exposure_photon_cm2_s"],rel_tol=2e-15))
    def test_native_cone_infeasibility(self):
        for s in m.SCENARIOS:
            w=self.a["source_scenarios"][s]["fixed_native_current_only_photon_cone"]
            self.assertLess(w["spectral_HeI_over_HI_events"],.031)
            self.assertGreater(w["native_min_HeI_over_HI_events"],.69)
            self.assertGreater(w["rate_pair_minimax_lower_bound"],.90)
            self.assertFalse(w["current_only_adapter_feasible"])
    def test_no_promoted_ivp(self):
        self.assertEqual(self.a["central_DAG"],"28/88_REPORTED")
        self.assertEqual(self.a["BASS_HE_physical_DAG"],"14/18_REPORTED")
        self.assertEqual(self.a["canonical_delta"],0)
        self.assertEqual(self.a["source_ownership"]["RUX04"],"NOT_ADMITTED")
        self.assertTrue(self.a["no_new_ionization_ivp"])
    def test_spectral_donor_csv_18_physical_rows(self):
        import csv
        f=m.write_group_donor_csv(self.a)
        with f.open() as stream:rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),18)
        for row in rows:
            n=float(row["photon_n_cm3"])
            sigma=float(row["effective_sigma_cm2"])
            gamma=float(row["photo_gamma_per_s"])
            self.assertTrue(math.isclose(gamma,m.C_CGS*n*sigma,rel_tol=4e-15,abs_tol=1e-30))
            if gamma:
                ex=float(row["photo_excess_eV_per_event"])
                ab=float(row["photo_absorbed_eV_per_event"])
                self.assertGreaterEqual(ex,0)
                self.assertGreater(ab,ex)
            self.assertEqual(row["claim_scope"],"EXPLORATORY_NONAUTHORITATIVE_NO_LOCAL_REI_PHOTON_OWNER")
    def test_bad_result_sha_rejected(self):
        good=m.SOURCE_REPORT_SHA
        try:
            m.SOURCE_REPORT_SHA="0"*64
            with self.assertRaises(ValueError):m.load_inputs()
        finally:m.SOURCE_REPORT_SHA=good
    def test_bad_native_ratio_rejected(self):
        fun=m.native_cone.compute
        try:
            m.native_cone.compute=lambda root:dict(fun(root),r_min_HeI_per_HI=0.1)
            with self.assertRaises(ValueError):m.load_inputs()
        finally:m.native_cone.compute=fun

if __name__=="__main__":unittest.main(verbosity=2)
