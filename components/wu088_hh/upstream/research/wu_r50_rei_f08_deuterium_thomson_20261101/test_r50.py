import csv, gzip, json, math, pathlib, shutil, tempfile, unittest
import r50_deuterium_observer_screen as m

ROOT=pathlib.Path(__file__).resolve().parent
RES=json.loads((ROOT/"results/R50_RESULTS.json").read_text())

class TestPhysicalScreen(unittest.TestCase):
    def test_positive_time_integral_and_zero_duration(self):
        self.assertEqual(m.h_integral(1e13,1e13,1e-14,1e-4),0)
        self.assertGreater(m.h_integral(0,1e13,1e-14,1e-4),0)
        self.assertAlmostEqual(m.h_integral(0,1e9,1e-14,1e-4),1e5,delta=3)

    def test_invalid_clock_and_fraction_rejected(self):
        for te,to,h,nh,eta in [(-1,1,1e-14,1e-4,1e-5),(2,1,1e-14,1e-4,1e-5),
                                (0,1,0,1e-4,1e-5),(0,1,1e-14,1e-4,-1e-5),
                                (0,1,1e-14,1e-4,1.5)]:
            with self.subTest(te=te,to=to,eta=eta):
                with self.assertRaises(ValueError):
                    m.analytic_cap(te,to,h,nh,eta)

    def test_invariance_at_zero_and_fraction_linearity(self):
        v=m.analytic_cap(3e12,1e13,1e-14,1e-4)
        self.assertEqual(m.analytic_cap(3e12,1e13,1e-14,1e-4,eta=0),0)
        self.assertEqual(m.analytic_cap(1e13,1e13,1e-14,1e-4),0)
        self.assertAlmostEqual(m.analytic_cap(3e12,1e13,1e-14,1e-4,eta=m.ETA_D/2),v/2,delta=v*1e-14)

    def test_genuine_source_sha(self):
        for name,dig in m.SOURCE_SHA.items():
            self.assertEqual(m.digest(m.SOURCE/name),dig)
        self.assertEqual(m.git_blob(m.SOURCE/"SOURCE_F08_THOMSON_SKY_SUMMARY_12.csv"),m.SOURCE_SUMMARY_GIT_BLOB)

    def test_original_source_has_two_16001_histories(self):
        self.assertEqual(RES["original_source_check"]["history_rows_BI"],16001)
        self.assertEqual(RES["original_source_check"]["history_rows_FLRW"],16001)
        self.assertLess(RES["original_source_check"]["max_recomputed_original_sky_tau_relative_error"],1e-11)

    def test_no_scientific_promotion_or_unmeasured_claim(self):
        self.assertEqual(RES["DAG"]["new_canonical_nodes"],0)
        self.assertEqual(RES["DAG"]["WU"],"34/49")
        self.assertEqual(RES["DAG"]["REI_central"],"28/88")
        self.assertTrue(RES["assumptions"]["original_F08_S0_prescribed_not_cosmic_history"])
        self.assertFalse(RES["assumptions"]["admitted_primordial_D_measurement"])

    def test_full_file_physical_bounds_all_rays(self):
        n=0
        path=ROOT/"results/R50_ORIGINAL_F08_S0_D_ELECTRON_THOMSON_CAP_10752.csv.gz"
        with gzip.open(path,"rt",newline="") as f:
            for r in csv.DictReader(f):
                n+=1
                cap=float(r["D_fullion_tau_cap"])
                tau=float(r["original_tau_BI"])
                rho=float(r["D_emitter_electron_fraction_cap"])
                g0=float(r["visibility_upper_bound_any_D_ionization"])/(1+rho)
                gl=float(r["visibility_lower_bound_any_D_ionization"])
                gu=float(r["visibility_upper_bound_any_D_ionization"])
                gf=float(r["fullion_visibility"])
                self.assertGreaterEqual(cap,0)
                self.assertLessEqual(cap/tau,2.5e-5)
                self.assertLessEqual(gl,gf*(1+1e-13))
                self.assertLessEqual(gf,gu*(1+1e-13))
                self.assertAlmostEqual(gl/g0,math.exp(-cap),delta=1e-12)
                self.assertAlmostEqual(float(r["tau_BI_with_fullion_D"]),cap+tau,delta=1e-15)
        self.assertEqual(n,10752)

    def test_all_12_observer_windows_and_rms_upper(self):
        self.assertEqual(RES["ray_rows"],10752)
        self.assertEqual(len(RES["per_window"]),12)
        self.assertLess(RES["observer_conclusion"]["max_bound_to_geometry_RMS"],.005)
        self.assertLess(RES["observer_conclusion"]["max_tau_fraction"],2.5e-5)
        for group in RES["per_window"]:
            self.assertEqual(group["ray_rows"],group["angular_nmu"]*group["angular_nphi"])
            self.assertGreater(group["original_Bianchi_geometry_RMS"],0)
            self.assertLess(abs(group["fullion_Qxx"]+group["fullion_Qyy"]+group["fullion_Qzz"]),1e-22)

    def test_output_checksums(self):
        for name,dig in RES["output_sha256"].items():
            self.assertEqual(m.digest(ROOT/"results"/name),dig)

    def test_source_tamper_detectable_without_modifying_original(self):
        with tempfile.TemporaryDirectory() as td:
            c=pathlib.Path(td)/"copied_scenario.json"
            shutil.copy2(m.SOURCE/"science_scenario_v1.json",c)
            c.write_bytes(c.read_bytes()+b" ")
            self.assertNotEqual(m.digest(c),m.SOURCE_SHA["science_scenario_v1.json"])

    def test_transmission_has_correct_sign(self):
        with gzip.open(ROOT/"results/R50_ORIGINAL_F08_S0_D_ELECTRON_THOMSON_CAP_10752.csv.gz","rt") as f:
            r=next(csv.DictReader(f))
            self.assertLess(float(r["fullion_transmission"]),math.exp(-float(r["original_tau_BI"])))

    def test_source_reference_linkage(self):
        self.assertEqual(RES["source_pair_id"],m.REI_SOURCE_PAIR_ID)
        self.assertEqual(RES["parent_WU_head"],"f5d09daf5e70baa964aadda2156cd61facf495c4")

if __name__=="__main__":
    unittest.main()
