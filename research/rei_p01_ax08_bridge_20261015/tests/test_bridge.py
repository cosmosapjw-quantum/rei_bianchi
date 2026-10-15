#!/usr/bin/env python3
"""Focused actual-input and adversarial fixture tests for P01/AX08 bridge."""
import csv
from decimal import Decimal,localcontext
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
import numpy as np

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import certified16 as w
import ax08_early_tau as c

class Warm16(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.status=w.source_rows()
    def test_actual_source_and_contiguous_16_cells(self):
        self.assertEqual(len(self.rows),16)
        self.assertEqual(w.sha(w.CSV_PATH),w.CSV_SHA)
        self.assertEqual([r["proper_s"] for r in self.rows],
                         [(i+1)*int(w.DT) for i in range(16)])
    def test_positive_poisson_normalization_and_tail(self):
        for s in ("0","1e-40","1e-9","1.6e-7"):
            x=Decimal(s)
            p=w.probabilities(x)
            self.assertTrue(all(value>=0 for value in p.values()))
            self.assertLess(abs(sum(p.values())-1),Decimal("1e-85"))
            self.assertLessEqual(p["ge3"],x**3/6)
    def test_once_is_not_one_or_more(self):
        p=w.probabilities(Decimal(self.rows[-1]["source_tau_lower"]))
        self.assertGreater(p["p2"],Decimal("8e-15"))
        with localcontext() as context:
            context.prec=90
            self.assertLess(abs((1-p["p0"])-p["p1"]-p["p2"]-p["ge3"]),Decimal("1e-85"))
    def test_positive_increment_brackets(self):
        lo=hi=Decimal(0)
        for r in self.rows:
            l=Decimal(r["source_tau_lower"])
            u=Decimal(r["source_tau_upper"])
            self.assertGreater(l,hi)
            self.assertEqual(Decimal(r["slab_tau_lower"]),l-hi)
            self.assertEqual(Decimal(r["slab_tau_upper"]),u-lo)
            lo,hi=l,u
    def test_modified_source_csv_rejected(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"source.csv"
            path.write_bytes(w.CSV_PATH.read_bytes()+b"\n")
            with self.assertRaisesRegex(ValueError,"BYTE_IDENTITY_FAILURE"):
                w.source_rows(path=path)
    def test_bad_model_status_rejected(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"STATUS.json"
            payload=json.loads(w.STATUS_PATH.read_text())
            payload["scientific_status"]="APPROVED_FULL_EOR"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError,"BASS_HE_SCIENCE_SCOPE_CHANGED"):
                w.source_rows(status_path=path)
    def test_noncontiguous_time_rejected(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"source.csv"
            lines=w.CSV_PATH.read_text().splitlines()
            lines[4]=lines[4].replace("25000000000","25000000001",1)
            path.write_text("\n".join(lines)+"\n")
            with self.assertRaisesRegex(ValueError,"NONCONTIGUOUS_PROPER_CLOCK"):
                w.source_rows(path=path,check_sha=False)
    def test_large_or_negative_poisson_domain_rejected(self):
        for x in (Decimal("-1e-10"),Decimal("1")):
            with self.assertRaisesRegex(ValueError,"POISSON_TAU_OUT_OF_SUPPORTED_RANGE"):
                w.positive_poisson_tail(x)

class FiniteWindowLastScattering(unittest.TestCase):
    def test_actual_sixteen_cell_telescoping_and_positive_bounds(self):
        import finite_visibility as fv
        rows,_=w.source_rows()
        r=fv.build(rows)
        self.assertEqual(r["status"],"PASSED_16_SCOPED_POSITIVE_EVENT_WEIGHTS")
        self.assertEqual(len(r["result"]),16)
        self.assertEqual(Decimal(r["sum_mid"]),Decimal(r["total_probability_mid"]))
        for cell in r["result"]:
            lo=Decimal(cell["source_window_last_scatter_lower"])
            mid=Decimal(cell["source_window_last_scatter_mid"])
            up=Decimal(cell["source_window_last_scatter_upper"])
            self.assertTrue(Decimal(0)<lo<=mid<=up)
    def test_published_at_least_one_display_precision(self):
        rows,status=w.source_rows()
        tau=(Decimal(rows[-1]["source_tau_lower"])+
             Decimal(rows[-1]["source_tau_upper"]))/2
        with localcontext() as ctx:
            ctx.prec=90
            cumulative=1-(-tau).exp()
            displayed=Decimal(status["first_collision_mid_display"])
            self.assertLess(abs(cumulative-displayed),Decimal("1e-23"))
            self.assertNotEqual(cumulative,w.probabilities(tau)["p1"])

class RealAX08(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owner=Path.home()/"Dropbox/bianchi/rei_bianchi"
        cls.zero=c.load_case(cls.owner,"ZERO")
    def test_real_electron_density(self):
        arr=self.zero["arrays"]
        self.assertGreater(self.zero["prefix_rows"],100)
        self.assertEqual(arr["t"][0],0)
        self.assertGreater(arr["t"][-1],c.DURATION)
        self.assertAlmostEqual(arr["ne"][0],3.515843170412521e-7,delta=1e-18)
    def test_compensated_reference_parity(self):
        a=self.zero["arrays"]
        v=c.optical_history(a["t"],a["ne"],c.BOUNDARIES)
        scalar=c.kahan_tau(a["t"],a["ne"],c.DURATION)
        # Binary64 independent summation differences are O(1e-16*tau).
        self.assertAlmostEqual(v[-1],scalar,delta=1e-24)
        self.assertTrue(np.all(np.diff(v)>0))
        self.assertTrue(6e-10<v[-1]<8e-10)
    def test_downsample_is_diagnostic_not_claim(self):
        a=self.zero["arrays"]
        fine=c.optical_history(a["t"],a["ne"],c.BOUNDARIES)
        coarse=c.subsampled_history(a["t"],a["ne"],2,c.BOUNDARIES)
        self.assertLess(float(np.max(abs(fine-coarse))),1e-16)
    def test_negative_or_duplicate_data_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_MONOTONE_HISTORY"):
            c.optical_history(np.array([0.,10.,10.]),np.ones(3),np.array([5.]))
        with self.assertRaisesRegex(ValueError,"INVALID_MONOTONE_HISTORY"):
            c.optical_history(np.array([0.,10.,20.]),np.array([1.,-1.,1.]),np.array([5.]))
    def test_case_validation_and_all_five_original_sources(self):
        with self.assertRaises(ValueError): c.load_case(self.owner,"UNKNOWN")
        for case in c.CASE_REL:
            self.assertEqual(c.load_case(self.owner,case)["source_identity_sha256"],
                             c.OWNER_SOURCE_ID)

if __name__=="__main__":
    unittest.main(verbosity=2)
