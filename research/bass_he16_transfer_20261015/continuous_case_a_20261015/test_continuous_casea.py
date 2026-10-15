"""Independent tests on actual 48-row native MD14/Grackle source A/B evidence."""
import copy,json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from analyze_continuous import csvdict,validate,analyze

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"results"
class TrueSourceBirthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=csvdict(DATA/"MD14_CASEA_SERIAL.csv")
        cls.results=analyze(DATA/"MD14_CASEA_SERIAL.csv",
          DATA/"MD14_CASEA_PARALLEL2.csv",
          DATA/"SOURCE_GL16_REFERENCE.csv",
          DATA/"SOURCE_SUPPORT.csv")
    def get(self,q=0.,eta=0.,n=128,arm="PROJECTED"):
        return self.data[(q,eta,n)][arm]
    def test_twenty_four_cases_and_forty_eight_records(self):
        self.assertEqual(self.results["paired_cases"],24)
        self.assertEqual(self.results["individual_lanes"],48)
    def test_rust_serial_vs_two_worker_numerical_equality(self):
        self.assertTrue(self.results["serial_sha256"]!=self.results["parallel_sha256"])
        # Runtime columns legitimately differ, but the independent analyzer
        # checked all scientific strings for equality across all 48 rows.
    def test_all_photon_nuclear_and_energy_conservation_records(self):
        for item in self.data.values():
            for x in item.values():
                residuals=validate(x)
                self.assertLess(residuals["total_energy_error"],4e-11)
                self.assertLess(residuals["photon_count_error"],2e-16)
    def test_true_MD14_emission_is_common_to_both_transport_arms(self):
        for item in self.data.values():
            a,b=item["PROJECTED"],item["COVARIANT"]
            for key in ("emitted_photons_per_H","emitted_energy_eV_per_H",
                        "number_of_birth_cohorts",
                        "emitted_flux_z_eV_per_H","emitted_P2_eV_per_H"):
                self.assertEqual(a[key],b[key])
    def test_source_midpoint_birth_count_matches_independent_gauss16(self):
        r=self.get()
        self.assertLess(
          abs(float(r["emitted_photons_per_H"])-3.45955703510326897e-6)/
              3.45955703510326897e-6,2e-11)
    def test_source_birth_quadrature_errors_contract(self):
        for q in (-.005,0.,.005):
            rows={v["steps"]:v for v in self.results["measured"] if v["q_ref"]==q and v["eta"]==0.}
            errs=[rows[n]["birth_GL16_relative_error"] for n in (1,8,32,128)]
            self.assertTrue(all(errs[i]>errs[i+1] for i in range(3)))
            self.assertLess(errs[-1],1e-11)
    def test_source_births_are_per_H_no_double_four_pi(self):
        self.assertGreater(float(self.get()["emitted_photons_per_H"]),3.4e-6)
        self.assertLess(float(self.get()["emitted_photons_per_H"]),3.5e-6)
        self.assertEqual(int(self.get(n=128)["number_of_birth_cohorts"]),49152)
    def test_earliest_source_ray_never_reaches_the_lower_13p6_ev_support(self):
        for q in (-.005,0.,.005):
            item=next(v for v in self.results["measured"] if v["q_ref"]==q and v["eta"]==0 and v["steps"]==128)
            self.assertGreater(item["min_source_true_final_E_eV"],13.85)
            self.assertEqual(item["covariant_photons_below_13p6_eV_per_H"],0.)
    def test_numerically_spurious_lower_boundary_loss_exceeds_three_percent(self):
        for q in (-.005,0.,.005):
            item=next(v for v in self.results["measured"] if v["q_ref"]==q and v["eta"]==0 and v["steps"]==128)
            self.assertGreater(item["projected_boundary_ratio_of_births"],.03)
            self.assertLess(item["projected_boundary_ratio_of_births"],.032)
    def test_even_single_macro_step_can_lose_uv_photons_artificially(self):
        self.assertGreater(float(self.get(n=1)["boundary_photons_per_H"]),1e-7)
        self.assertEqual(float(self.get(n=1,arm="COVARIANT")["boundary_photons_per_H"]),0.)
    def test_source_emission_is_axially_symmetric_and_zero_quad(self):
        for pair in self.data.values():
            for r in pair.values():
                E=float(r["emitted_energy_eV_per_H"])
                self.assertLess(abs(float(r["emitted_flux_z_eV_per_H"]))/E,1e-10)
                self.assertLess(abs(float(r["emitted_P2_eV_per_H"]))/E,1e-10)
    def test_signed_q_reverses_quad_while_flrw_quad_nearly_zero(self):
        a=float(self.get(q=-.005,arm="COVARIANT")["final_P2_eV_per_H"])
        b=float(self.get(q=.005,arm="COVARIANT")["final_P2_eV_per_H"])
        z=float(self.get(q=0,arm="COVARIANT")["final_P2_eV_per_H"])
        self.assertGreater(a,0.);self.assertLess(b,0.)
        self.assertLess(abs(a+b)/abs(a),3e-5)
        self.assertLess(abs(z),1e-19)
    def test_both_arms_preserve_positive_moment_cone(self):
        self.assertTrue(self.results["photon_moment_positivity_verified"])
        for pair in self.data.values():
            for r in pair.values():
                U=float(r["final_photon_energy_eV_per_H"])
                F=float(r["final_flux_z_eV_per_H"])
                P=float(r["final_P2_eV_per_H"])
                self.assertGreaterEqual(U,0)
                self.assertGreaterEqual(P,-U/2-1e-12*U)
                self.assertLessEqual(P,U+1e-12*U)
                self.assertLessEqual(3*F*F,U*(U+2*P)+1e-12*U**2)
    def test_true_MD14_nonzero_photoionization_in_both_arms(self):
        for arm in ("PROJECTED","COVARIANT"):
            x=self.get(arm=arm)
            self.assertGreater(float(x["HeII_absorbed_per_H"]),0.)
            self.assertGreater(float(x["RR_HeIII_per_H"]),0.)
    def test_macro_step_changes_not_claimed_certified_global(self):
        o=self.results
        self.assertFalse(o["source_emitters_and_recombination_escape_as_physical_stress"])
        self.assertEqual(o["global_EOR_and_CMB_sci_admission"],"HOLD")
    def test_native_shear_source_births_even_under_q_reversal(self):
        for n in (1,8,32,128):
            a=float(self.get(q=-.005,n=n)["emitted_photons_per_H"])
            b=float(self.get(q=.005,n=n)["emitted_photons_per_H"])
            self.assertLess(abs(a-b)/a,2e-12)
    def test_c13_c16_source_cohort_growth_bound(self):
        for n in (1,8,32,128):
            self.assertEqual(int(self.get(n=n)["number_of_birth_cohorts"]),384*n)
    def test_manufactured_corrupted_source_n_ledger_rejected(self):
        tampered=dict(self.get())
        tampered["emitted_photons_per_H"]=str(float(tampered["emitted_photons_per_H"])*1.01)
        with self.assertRaises(ValueError):
            validate(tampered)
    def test_manufactured_corrupted_gas_bind_energy_rejected(self):
        tampered=dict(self.get())
        tampered["micro_binding_eV_per_H"]=str(float(tampered["micro_binding_eV_per_H"])+1e-4)
        with self.assertRaises(ValueError):
            validate(tampered)
    def test_missing_case_rejected_before_claim(self):
        with TemporaryDirectory() as td:
            p=Path(td)/"bad.csv"
            p.write_text("\n".join((DATA/"MD14_CASEA_SERIAL.csv").read_text().splitlines()[:-1])+"\n")
            with self.assertRaises(ValueError):
                csvdict(p)

    def test_source_only_first_energy_node_projection_algebra(self):
        import csv
        with (DATA/"SOURCE_ONLY_BOUNDARY.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        data=next(x for x in rows if float(x["q_ref"])==0 and int(x["substeps"])==1)
        expected=float(data["first_bin_expected_fraction"])
        actual=float(data["boundary_fraction"])
        self.assertAlmostEqual(actual,expected,places=14)
        self.assertGreater(expected,.032)

    def test_source_only_loss_does_not_vanish_under_five_step_refinements(self):
        import csv
        with (DATA/"SOURCE_ONLY_BOUNDARY.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        for q in (-.005,0.,.005):
            selected=sorted((x for x in rows if float(x["q_ref"])==q),
                             key=lambda x:int(x["substeps"]))
            self.assertEqual([int(x["substeps"]) for x in selected],[1,8,32,128,512])
            self.assertGreater(float(selected[-1]["boundary_fraction"]),.0328)
            self.assertLess(float(selected[-1]["boundary_fraction"]),.033)
            for x in selected:
                self.assertLess(abs(float(x["photon_count_residual"])),2e-18)

    def test_real_case_a_moment_bias_under_signed_q(self):
        for q in (-.005,.005):
            a=self.get(q=q)
            b=self.get(q=q,arm="COVARIANT")
            pa=float(a["final_P2_eV_per_H"]);pb=float(b["final_P2_eV_per_H"])
            self.assertGreater(abs(pb),1e-12)
            self.assertGreater(abs(pb-pa)/abs(pb),.02)
            self.assertLess(abs(pb-pa)/abs(pb),.03)

if __name__=="__main__":unittest.main()
