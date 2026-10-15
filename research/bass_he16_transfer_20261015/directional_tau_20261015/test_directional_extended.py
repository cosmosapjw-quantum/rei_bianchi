import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np

from benchmark_directional import reference_scalar_roots
from directional_tau import (
    KAPPA, PREC, source_b_history, directional_moments,
    tau_between_source_and_observer, solve_directional_redshift,
)


class TestGeometryAndReference(unittest.TestCase):
    def reference(self,n=301,H=.1):
        t=np.linspace(0,10,n)
        a=np.exp(H*t)
        ne=np.full(n,.001)
        tau=KAPPA*PREC(".001")*t.astype(PREC)
        return {"a":a,"t_s":t,"ne_cm3":ne,"tau":tau}

    def test_constant_b_is_pure_coordinate_rescaling(self):
        src=self.reference()
        b=np.full(src["a"].shape,.5)
        mu=np.linspace(-1,1,89)
        col,info=tau_between_source_and_observer(src,b,.6,mu)
        self.assertLess(float(np.max(col)-np.min(col)),3e-21)
        self.assertLess(float(np.max(abs(col-(KAPPA*PREC(".001")*
            PREC(np.log1p(.6)/.1))))),1e-19)

    def test_z_relative_monotone_column(self):
        src=self.reference()
        b=.01*np.log(src["a"])
        mu=np.linspace(0,1,13)
        a,_=tau_between_source_and_observer(src,b,.2,mu)
        c,_=tau_between_source_and_observer(src,b,.5,mu)
        self.assertTrue(np.all(c>a))

    def test_scalar_math_bisection_same_as_vector(self):
        src=self.reference()
        u=np.log(src["a"])
        b=.012*u
        mu=np.linspace(-1,1,95)
        roots,_=solve_directional_redshift(u,b,mu,.4)
        serial=reference_scalar_roots(u,b,mu,.4)
        self.assertLess(float(np.max(abs(roots-serial))),3e-14)

    def test_geometry_column_matches_source_scale_nodes(self):
        src=self.reference(n=5)
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"history.csv"
            with f.open("w",newline="") as out:
                w=csv.writer(out)
                w.writerow(["case_id","q_ref","a","b"])
                for a in src["a"]:
                    w.writerow(["ZERO",0,format(a,".17g"),0])
            result=source_b_history(f,src["a"])
            self.assertTrue(np.array_equal(result,np.zeros(5)))

    def test_geometry_source_node_mismatch_fails(self):
        src=self.reference(n=5)
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"history.csv"
            with f.open("w",newline="") as out:
                w=csv.writer(out)
                w.writerow(["case_id","q_ref","a","b"])
                for i,a in enumerate(src["a"]):
                    w.writerow(["ZERO",0,format(a+(1e-4 if i==2 else 0),".17g"),0])
            with self.assertRaisesRegex(ValueError,"scale-factor node parity"):
                source_b_history(f,src["a"])


if __name__=="__main__":
    unittest.main()
