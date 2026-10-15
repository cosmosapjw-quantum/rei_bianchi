"""Native nine-run and pure-Rust semigroup evidence consistency regressions."""
import csv
import json
from pathlib import Path
import tempfile
import unittest


def interpret_remap_csv(path):
    with path.open(newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=48:
        raise ValueError("Expected 2 z x 3 energy bins x 8 projection subdivisions")
    samples={}
    for r in rows:
        z=r["z_end"];idx=r["energy_index"];n=int(r["steps"])
        if n not in (1,2,4,16,64,256,1024,4096):
            raise ValueError("Unexpected projection count")
        key=f"z{z}_bin{idx}"
        if key not in samples:samples[key]={}
        if n in samples[key]:raise ValueError("Duplicate semigroup check")
        samples[key][n]={k:float(v) for k,v in r.items() if k not in
                         ("z_end","energy_index","steps","occupied_bins")}
        samples[key][n]["occupied_bins"]=int(r["occupied_bins"])
    result={}
    for key,series in samples.items():
        if len(series)!=8:raise ValueError("Incomplete projection series")
        first=series[1];many=series[4096]
        relative_var=many["variance_eV2"]/first["variance_eV2"]-1
        if first["variance_eV2"]<=0 or relative_var<=0:
            raise ValueError("Source remap semigroup regression no longer reproduced")
        if abs(first["relative_mean_error"])>1e-10:
            raise ValueError("One-step freeflight energy moment no longer conserved")
        result[key]={
            "starting_energy_eV":first["start_energy_eV"],
            "exact_final_energy_eV":first["exact_end_eV"],
            "one_projection_variance_eV2":first["variance_eV2"],
            "repeated_projection_variance_eV2":many["variance_eV2"],
            "variance_relative_excess":relative_var,
            "one_projection_boundary_loss":first["boundary_loss"],
            "repeated_projection_boundary_loss":many["boundary_loss"],
            "repeated_occupied_bins":many["occupied_bins"],
            "count_plus_boundary_at_n4096":many["photon_number"]+many["boundary_loss"]
        }
    return result


class NativeScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).with_name("results")
        cls.r3=json.loads((cls.root/"THREE_LEVEL_GOAL_CONVERGENCE.json").read_text())
        cls.r1=json.loads((cls.root/"NATIVE_GOAL_ANALYSIS.json").read_text())
        cls.corr=json.loads((cls.root/"SIGNED_CORRELATED_ERROR.json").read_text())
        cls.remap=interpret_remap_csv(cls.root/"REMAP_SEMIGROUP_LEDGER.csv")


    def test_raw_provenance_manifest_frozen_native_identity(self):
        m=json.loads((self.root/"RAW_SOURCE_SHA256_MANIFEST.json").read_text())
        self.assertEqual(m["native_run_count"],9)
        self.assertEqual(m["file_count"],169)
        self.assertEqual(m["geometry_ledger_probes"],48)
        self.assertFalse(m["source_ode_error_certified"])
        self.assertEqual(m["scientific_admission"],"NOT_ISSUED")
        for case in ("ZERO","SHEAR_HALF_MINUS","SHEAR_HALF_PLUS"):
            rows={r["level"]:r["accepted"] for r in m["native_runs"]
                  if r["case"]==case}
            self.assertEqual(rows,{"baseline":972,"refined":1797,"ultra":3706})

    def test_three_native_levels_remain_non_certified(self):
        self.assertEqual(self.r3["scientific_admission"],"HOLD")
        self.assertEqual(self.r3["status"],
             "THREE_EXPLORATORY_NATIVE_LEVELS_COMPLETED_NO_CERTIFIED_GLOBAL_ERROR")

    def test_state_difference_does_not_contract(self):
        v=self.r3["per_case_state_endpoint_attentuation"]
        for case in ("ZERO","SHEAR_HALF_MINUS","SHEAR_HALF_PLUS"):
            self.assertGreater(v[case]["x_HII"]["endpoint_difference_ratio"],1)

    def test_goal_attenuation_is_non_uniform(self):
        v=self.r3["sampled_goal_difference_attenuation"]
        self.assertGreater(v[0]["odd_tau_quadrupole_abs_diff_attenuation_ratio"],1.)
        self.assertLess(v[-1]["odd_tau_quadrupole_abs_diff_attenuation_ratio"],1.)

    def test_exact_signed_clock_rows(self):
        for level in ("refined","ultra"):
            self.assertEqual(self.corr["exact_signed_grid_parity"][level]["time_s_abs_max"],0)
            self.assertEqual(self.corr["exact_signed_grid_parity"][level]["a_abs_max"],0)

    def test_native_source_error_is_even_dominated(self):
        r=self.corr["native_electron_error_common_odd"]
        self.assertLess(r["max_abs_odd_to_even_ratio"],1e-8)
        for row in self.corr["counterfactual"]:
            self.assertLess(abs(row["fraction_of_native_change_predicted_by_frozen_geometry_common_ne"]-1.),.01)

    def test_pure_remap_increases_variance_with_projection_count(self):
        for row in self.remap.values():
            self.assertGreater(row["variance_relative_excess"],0)
            self.assertAlmostEqual(row["count_plus_boundary_at_n4096"],1.0,places=8)

    def test_unphysical_boundary_leakage_has_no_absorption(self):
        row=self.remap["z19.8_bin5"]
        self.assertGreater(row["exact_final_energy_eV"],13.6)
        self.assertEqual(row["one_projection_boundary_loss"],0)
        self.assertGreater(row["repeated_projection_boundary_loss"],1e-6)
        self.assertGreater(row["variance_relative_excess"],.3)


    def test_native_original_ledger_is_conserved_in_each_freeflight_probe(self):
        import csv
        p=self.root/"REMAP_SEMIGROUP_LEDGER.csv"
        with p.open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),48)
        max_number=max(abs(float(x["number_ledger_residual"])) for x in rows)
        max_energy=max(abs(float(x["energy_ledger_residual"])) for x in rows)
        self.assertLess(max_number,4e-15)
        self.assertLess(max_energy,2e-13)

    def test_grid_mean_energy_can_be_biased_by_boundary_leakage(self):
        a=self.remap["z19.8_bin5"]
        self.assertGreater(a["repeated_projection_boundary_loss"],1e-6)
        self.assertAlmostEqual(a["count_plus_boundary_at_n4096"],1,places=12)
        self.assertGreater(a["exact_final_energy_eV"],13.6)
        self.assertGreater(a["variance_relative_excess"],.33)

    def test_short_remap_var_increases_at_fixed_grid(self):
        self.assertGreater(self.remap["z19.99_bin5"]["variance_relative_excess"],.01)

    def test_replay_control_is_byte_identical_until_final_step(self):
        for case,r in self.r1["original_baseline_prefix_identity"].items():
            self.assertEqual(r["matching_initial_csv_lines_including_header"],973)
            self.assertEqual(r["first_mismatch_line_zero_index"],973)


if __name__=="__main__": unittest.main()
