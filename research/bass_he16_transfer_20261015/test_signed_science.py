"""Manufactured tests for signed-q scalar response and clock decomposition."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from signed_prefix_tau import EXPECTED_Q, DEFAULT_GRID, combine, at_a, taucum, PREC
from clock_decompose_signed import response, tau_at_t, read_caches, digest, CASE_ORDER


class TestSignedScientificContract(unittest.TestCase):
    def reports(self, c0, c1, c2, c3, c4):
        rows=[]
        for name,q in EXPECTED_Q.items():
            taus=[c0+c1*q+c2*q*q+c3*q**3+c4*q**4 for _ in DEFAULT_GRID]
            rows.append({"case":name,"q_ref":q,"grid":list(DEFAULT_GRID),
                        "tau_at_a":[format(v,".20g") for v in taus],
                        "proper_seconds_at_a":["1"]*len(taus),
                        "history_sha256":"a"*64,
                        "electron_census_max_abs_over_nH":0.0})
        return rows

    def test_polynomial_stencil(self):
        result=combine(self.reports(.003,.02,-.007,.1,.3))
        self.assertAlmostEqual(float(result["quadratic_coefficient_q2"][0]),-.007,places=8)
        self.assertAlmostEqual(float(result["quartic_coefficient_q4"][0]),.3,places=7)
        self.assertAlmostEqual(float(result["linear_coefficient_q1"][0]),.02,places=9)
        self.assertAlmostEqual(float(result["cubic_coefficient_q3"][0]),.1,places=7)

    def test_zero_response_reports_null_ratio(self):
        r=combine(self.reports(.003,0,0,0,0))
        self.assertTrue(all(v is None for v in r["even_ratio_q010_to_q005"]))

    def test_exact_cell_partial_integral(self):
        t=np.asarray([0.,1.,2.]);ne=np.asarray([1.,2.,3.])
        tau,_=taucum(t,ne)
        target=tau_at_t(t,ne,tau,PREC(".5"))
        reference=(PREC(".5")+PREC(".125"))*PREC(6.6524587321e-29)*PREC(299792458)*PREC(1000000)
        self.assertLess(abs(target-reference)/reference,PREC("1e-15"))

    def test_exact_clock_split_synthetic(self):
        grid=np.linspace(.047619047619047616,.08873654701704167,41)
        sources={};cases={}
        for name,q in EXPECTED_Q.items():
            t=np.linspace(0,1000*(1+8*q*q),len(grid))
            n=np.full(len(grid),1+3*q*q)
            tau,_=taucum(t,n)
            cases[name]={"t_s":t,"a":grid,"ne_cm3":n,"tau":tau}
            src={"a":grid,"time_s":t,"ne_proper_cm3":n}
            samples=[at_a(src,tau,a) for a in DEFAULT_GRID]
            sources[name]={"tau_at_a":[format(v[1],".20g") for v in samples],
                           "history_sha256":"b"*64}
        r=response(cases,sources)
        for key in ("0.005","0.01"):
            p=r["decompositions"][key]
            for ea,et,ec in zip(p["even_mean_a"],p["even_common_time"],p["even_clock_residual"]):
                self.assertAlmostEqual(float(ea),float(et)+float(ec),places=19)
            self.assertTrue(all(abs(float(o))<1e-27 for o in p["odd_mean_a"]))

    def test_zero_effect_null_clock_fraction(self):
        grid=np.linspace(.047619047619047616,.08873654701704167,41)
        cases={};sources={}
        t=np.linspace(0,1000,len(grid));n=np.ones(len(t));tau,_=taucum(t,n)
        for name in EXPECTED_Q:
            cases[name]={"t_s":t,"a":grid,"ne_cm3":n,"tau":tau}
            src={"a":grid,"time_s":t,"ne_proper_cm3":n}
            sources[name]={"tau_at_a":[format(at_a(src,tau,a)[1],".20g") for a in DEFAULT_GRID],
                           "history_sha256":"c"*64}
        r=response(cases,sources)
        self.assertTrue(all(x is None for x in r["decompositions"]["0.005"]["even_clock_fraction"]))

    def test_cache_integrity_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            fake=folder/"SHEAR_MINUS.npz"
            fake.write_bytes(b"ABCD")
            goodhash=digest(fake)
            (folder/"MANIFEST.json").write_text(json.dumps({"cases":{
                "SHEAR_MINUS":{"cache_filename":fake.name,"cache_sha256":goodhash}
            }}))
            fake.write_bytes(b"ABCDX")
            with self.assertRaisesRegex(ValueError,"Cache SHA mismatch"):
                read_caches(folder)


if __name__=="__main__":unittest.main()
