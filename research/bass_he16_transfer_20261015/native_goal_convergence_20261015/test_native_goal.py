"""Red/green scientific contracts for independent native convergence analysis."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from native_probe import conf,CASE_Q,TARGETS
from native_goal_analysis import (sha,original_prefix_replay,
                                  compare_native_levels,linearly_predicted_tau2)


class NativeProbeTests(unittest.TestCase):
    def test_config_same_physics_except_q_and_target(self):
        c1=dict(line.split("=",1) for line in conf(0.,1e-5).splitlines() if line)
        c2=dict(line.split("=",1) for line in conf(0.,3e-6).splitlines() if line)
        self.assertEqual(c1["end_zbar"],"19.99")
        self.assertEqual(c1["energy_subdivisions"],"16")
        self.assertEqual(c1["n_mu"],"8")
        self.assertEqual(c1["same_h"],"false")
        self.assertEqual(c1["initial_temperature_k"],"8.098143045064857")
        self.assertEqual(set(k for k in c1 if c1[k]!=c2[k]),{"local_target"})
        self.assertEqual(c1["output_budget_mib"],"256")

    def test_signed_pair_physics_symmetric(self):
        a=dict(line.split("=",1) for line in conf(-.005,1e-5).splitlines() if line)
        b=dict(line.split("=",1) for line in conf(.005,1e-5).splitlines() if line)
        self.assertEqual(set(k for k in a if a[k]!=b[k]),{"q_ref"})
        self.assertEqual(float(a["q_ref"]),-float(b["q_ref"]))

    def test_manufactured_exact_level_agreement(self):
        a=np.array([.04,.041,.043])
        d={key:np.array([1.,2.,3.]) for key in
           ("time_s","b","H_per_s","x_HII","x_HeII","x_HeIII",
           "nH_proper_cm3","ne_proper_cm3","temperature_K",
           "J2_photon_u_eV_per_H")}
        d["a"]=a
        r=compare_native_levels(d,d)
        self.assertTrue(all(v["abs_diff_max_101_lna_samples"]==0 for v in r.values()))

    def test_manufactured_endpoint_interpolation(self):
        a=np.array([.047,.05,.052])
        d={key:np.array([1.,2.,3.]) for key in
           ("time_s","b","H_per_s","x_HII","x_HeII","x_HeIII",
            "nH_proper_cm3","ne_proper_cm3","temperature_K","J2_photon_u_eV_per_H")}
        d["a"]=a
        modified={k:(v+.1 if k=="x_HII" else v.copy()) for k,v in d.items()}
        r=compare_native_levels(d,modified)
        self.assertAlmostEqual(r["x_HII"]["abs_diff_endpoint"],.1)
        self.assertAlmostEqual(r["x_HII"]["abs_diff_max_101_lna_samples"],.1,places=14)

    def test_linear_odd_quad_sign_and_symmetry(self):
        a=np.array([.04,.045,.05])
        h=1e-12
        zero={"a":a,"ne_proper_cm3":np.ones(3)*.001,"H_per_s":np.ones(3)*h}
        s=.02
        plus={"a":a,"b":s*np.log(a/a[-1])}
        minus={"a":a,"b":-s*np.log(a/a[-1])}
        result=linearly_predicted_tau2(.1,zero,plus,minus)
        self.assertLess(result["predicted_odd"],0)
        self.assertAlmostEqual(result["predicted_plus"],-result["predicted_minus"],places=18)

    def test_original_byte_prefix_holds(self):
        with tempfile.TemporaryDirectory() as temp:
            original=Path(temp)/"source.csv"
            new=Path(temp)/"new.csv"
            original.write_bytes(b"head\n1\n2\n3\n4\n")
            new.write_bytes(b"head\n1\n2\nq\n")
            r=original_prefix_replay(new,original,sha(original))
            self.assertEqual(r["matching_initial_csv_lines_including_header"],3)
            self.assertEqual(r["first_mismatch_line_zero_index"],3)

    def test_unexpected_original_identity_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            original=Path(temp)/"source.csv";new=Path(temp)/"new.csv"
            original.write_bytes(b"HEAD\n");new.write_bytes(b"HEAD\n")
            with self.assertRaisesRegex(ValueError,"Original science source CSV changed"):
                original_prefix_replay(new,original,"0"*64)


if __name__=="__main__":
    unittest.main()
