#!/usr/bin/env python3
"""Safe public checks only: original 460800-row source execution is off GitHub."""
import copy,json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(d):
    if d["schema"]!="REI_F05_ORIGINAL_26EVENT_10SITE_CONTINUUM_RESIDUAL_V1":raise ValueError("WRONG_SCHEMA")
    if d["actual_source_cell_site_rows"]!=460800 or d["original_source_point_evaluations"]!=10:raise ValueError("NOT_ORIGINAL_TEN_SOURCE_POINTS")
    if d["official_tick161"] or d["official_tick162"] or d["DAG"]["central"]!="28/88" or d["production"]!="HOLD":raise ValueError("FALSE_CANONICAL_ADMISSION")
    if d["path_residual_status"]!="NUMERICALLY_EVALUATED_SAMPLES_NOT_CONTINUUM_SUP_ENCLOSURE":raise ValueError("FALSE_CONTINUUM_CERTIFICATION")
    if len(d["epochs"])!=2:return False
    for epoch,interval in zip(d["epochs"],((160,161),(161,162))):
        if tuple(epoch["original_tick_interval"])!=interval or len(epoch["source_samples"])!=5:raise ValueError("WRONG_REAL_SOURCE_EPOCH")
        if not epoch["sampled_simpson_not_rigorous_integration"]:raise ValueError("FALSE_SIMPSON_PROOF")
        if len(epoch["sampled_simpson_max_abs_residual_by_coord"])!=4:raise ValueError("WRONG_RESIDUAL_COORDINATES")
    return True
class PublicReadback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=json.loads((ROOT/"results/SCIENCE_RESULT.json").read_text())
        cls.q=json.loads((ROOT/"results/QUADRATURE_AND_MOMENT.json").read_text())
        cls.audit=json.loads((ROOT/"results/INDEPENDENT_AUDIT.json").read_text())
    def test_native_source_record_count(self):
        self.assertTrue(validate(self.s))
        self.assertEqual(self.s["original_source_point_evaluations"],10)
        self.assertEqual(self.s["actual_source_cell_site_rows"],460800)
    def test_independent_audit_typed(self):
        self.assertEqual(self.audit["status"],"PASS_NUMERIC_SAMPLED_ORIGINAL_SOURCE_ONLY")
        self.assertFalse(self.audit["sampled_residual_is_proven_supremum"])
        self.assertFalse(self.audit["source_continuum_truncation_error_certified"])
    def test_original_26event_source_clock_join(self):
        a=self.s["epochs"][0]["source_samples"][-1]
        b=self.s["epochs"][1]["source_samples"][0]
        for v in ("global_B_erg","global_U_gas_erg","global_N_e","global_original_Bdot_erg_s","global_original_Udot_erg_s"):
            self.assertAlmostEqual(a[v]/b[v],1.,places=12)
    def test_global_original_rates_are_actual_trends(self):
        a=self.s["epochs"][0]["source_samples"]
        b=self.s["epochs"][1]["source_samples"]
        self.assertTrue(all(z["global_original_Bdot_erg_s"]<a[i+1]["global_original_Bdot_erg_s"] for i,z in enumerate(a[:-1])))
        self.assertTrue(all(z["global_original_Udot_erg_s"]>a[i+1]["global_original_Udot_erg_s"] for i,z in enumerate(a[:-1])))
        self.assertGreater(b[-1]["global_original_Bdot_erg_s"],a[-1]["global_original_Bdot_erg_s"])
    def test_three_moment_and_quadrature_not_proof(self):
        self.assertEqual(len(self.q["segments"]),2)
        self.assertTrue(all(not x["sample_quadrature_is_certified_continuum_error"] for x in (self.q,)))
        self.assertTrue(all(0<x["fixed_external_forcing_exact_Dg_log_change_upper_conditional"]<.01 for x in self.q["segments"]))
        self.assertTrue(all(0<max(z["three_minus_five_max_abs"] for z in seg["discrete_sampled_residual_quadrature"])<1e-14 for seg in self.q["segments"]))
    def test_forged_official_tick_rejected(self):
        f=copy.deepcopy(self.s);f["official_tick161"]=True
        with self.assertRaisesRegex(ValueError,"FALSE_CANONICAL_ADMISSION"):validate(f)
    def test_forged_continuum_certification_rejected(self):
        f=copy.deepcopy(self.s);f["path_residual_status"]="PROVEN_CONTINUUM"
        with self.assertRaisesRegex(ValueError,"FALSE_CONTINUUM_CERTIFICATION"):validate(f)
if __name__=="__main__":unittest.main()
