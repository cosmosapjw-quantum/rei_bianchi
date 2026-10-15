import json
import tempfile
import unittest
from pathlib import Path

from ax08_crosscheck import crosscheck,CASES,SOURCE_SHA
from plot_signed_tau import render

class ExternalCrosscheckTests(unittest.TestCase):
    def fixture(self,root):
        ax={"schema":"rei.axbi.signed_prefix_parity.v1","scientific_admission":"NOT_ISSUED",
            "cases":{c:{"history_sha256":c+"hash","source_identity_sha256":SOURCE_SHA} for c in CASES},
            "metrics":{"J2_photon_u_eV_per_H":{
                "odd_at_q_0p01":{"endpoint":-2.0},
                "odd_at_q_0p005":{"endpoint":-1.0},
                "even_at_q_0p01":{"endpoint":0.0}}}}
        root=Path(root)
        for c in CASES:
            (root/(c+".json")).write_text(json.dumps({"history_sha256":c+"hash"}))
        (root/"SIGNED_RESPONSE.json").write_text(json.dumps({
            "even_half_q010":["-4.0"],"even_half_q005":["-1.0"],
            "even_ratio_q010_to_q005":["4.0"]}))
        return ax

    def test_crosscheck_reuses_existing_ax08(self):
        with tempfile.TemporaryDirectory() as p:
            ax=self.fixture(p)
            r=crosscheck(ax,Path(p))
            self.assertEqual(r["j2_odd_ratio"],2.0)
            self.assertEqual(r["tau_even_ratio"],"4.0")
            self.assertEqual(r["scientific_admission"],"NOT_ISSUED")

    def test_mismatched_history_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            ax=self.fixture(p)
            ax["cases"]["ZERO"]["history_sha256"]="different"
            with self.assertRaisesRegex(ValueError,"History input mismatch"):
                crosscheck(ax,Path(p))

    def test_svg_valid_xml(self):
        from xml.etree import ElementTree as ET
        x=[.055,.06,.07,.08,.08873654701704167]
        signed={"a_grid":x}
        clock={"mean_a_grid":x,"decompositions":{}}
        for q in ("0.005","0.01"):
            clock["decompositions"][q]={
                "even_mean_a":["-1e-8"]*5,
                "even_clock_residual":["-9e-9"]*5,
                "even_common_time":["-1e-9"]*5,
                "even_clock_fraction":["0.9"]*5
            }
        with tempfile.TemporaryDirectory() as p:
            out=render(signed,clock,Path(p)/"result.svg")
            self.assertIn("svg",ET.parse(out).getroot().tag)
            self.assertGreater(out.stat().st_size,2000)

if __name__=="__main__":unittest.main()
