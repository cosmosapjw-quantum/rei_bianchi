"""RED-first tests of independently assembled E12 accepted-step ledger balances."""
import csv
import json
import math
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
from accepted_step_balance import analyze, reconstruct_step, preflight, BalanceError, exact_f64

ROOT = Path(__file__).resolve().parents[1]/"parent"/"full"

class TestBalance(unittest.TestCase):
    def setUp(self):
        self.off=ROOT/"OFF"
        def load(name):
            with (self.off/name).open(newline="") as handle:
                return list(csv.DictReader(handle))
        self.native=load("OWNER_NATIVE_41.csv")
        self.internal=load("OWNER_INTERNAL_5.csv")
        self.rct=load("OWNER_SELECTED_RCT.csv")
        self.steps=load("STEPS.csv")

    def test_exact_round_trip(self):
        self.assertEqual(float(exact_f64("1.00000000000000000e0")),1.0)
        self.assertEqual(exact_f64("-0.0"),0)
        with self.assertRaises(BalanceError): exact_f64("NaN")

    def test_one_step_gas_and_thermal(self):
        ratios=reconstruct_step(self.native,self.internal,self.rct,self.steps,1)
        self.assertEqual(len(ratios),4)
        self.assertTrue(all(0<=float(r)<=1 for r in ratios))

    def test_all_modes_all_steps(self):
        out=analyze(ROOT)
        self.assertEqual(out["accepted_steps"],1152)
        self.assertEqual(set(out["per_mode"]),{"OFF","KF","GM"})
        self.assertEqual(out["failures"],[])
        self.assertEqual(sum(x["tested_scalar_residuals"] for x in out["per_mode"].values()),4608)

    def test_double_RCT_must_fail(self):
        ratios=reconstruct_step(self.native,self.internal,self.rct,self.steps,7,rct_multiplier=2)
        # OFF RCT zero; the explicit KF/GM fixture detects double counting.
        other=ROOT/"GM"
        data=[]
        for fname in ["OWNER_NATIVE_41.csv","OWNER_INTERNAL_5.csv","OWNER_SELECTED_RCT.csv","STEPS.csv"]:
            with (other/fname).open(newline="") as handle:
                data.append(list(csv.DictReader(handle)))
        changed=reconstruct_step(*data,7,rct_multiplier=2)
        self.assertTrue(any(float(r)>1 for r in changed[:3]))

    def test_wrong_helium_ratio_rejected(self):
        with self.assertRaises(BalanceError):
            reconstruct_step(self.native,self.internal,self.rct,self.steps,1,helium_mass_fraction=0.25)

    def test_wrong_threshold_in_energy(self):
        v=reconstruct_step(self.native,self.internal,self.rct,self.steps,100,thresholds=(13.6,24.59,54.42))
        self.assertGreater(float(v[3]),1)

    def test_thermal_omission(self):
        v=reconstruct_step(self.native,self.internal,self.rct,self.steps,1,include_thermal=False)
        self.assertGreater(float(v[3]),1)

    def test_duplicate_and_disordered_step_rejected(self):
        rows=[dict(x) for x in self.native]
        rows[2]["ln_a"]=rows[1]["ln_a"]
        with self.assertRaises(BalanceError):preflight(rows,self.internal,self.rct,self.steps)

    def test_missing_column_rejected(self):
        rows=[dict(x) for x in self.native]
        del rows[2]["abs_HI"]
        with self.assertRaises(BalanceError):preflight(rows,self.internal,self.rct,self.steps)

    def test_negative_gate_preservation(self):
        r=analyze(ROOT)
        self.assertFalse(r["stage_independent_evaluator_executed"])
        self.assertFalse(r["true_error_enclosure"])
        self.assertEqual(r["protected_status"]["physical"],"HOLD")
        self.assertLess(r["per_mode"]["GM"]["max_ratio"],1)
        self.assertGreater(r["per_mode"]["GM"]["max_ratio"],.99)

if __name__ == "__main__": unittest.main()
