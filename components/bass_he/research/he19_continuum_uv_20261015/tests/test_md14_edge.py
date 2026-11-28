"""Focused regression and scientific limits for BASS_HE HE19 source split."""
import csv
import math
import os
import unittest
from md14_edge_flux import audit, source_cells, split_cell, partition, independent_reference

FIXTURE=os.environ.get("HE19_NATIVE_C8_CSV","")

class EdgeTests(unittest.TestCase):
    def test_original_native_c8_lower_node(self):
        self.assertTrue(os.path.isfile(FIXTURE), FIXTURE)
        with open(FIXTURE,newline="") as f:
            data=list(csv.DictReader(f))
        self.assertEqual(len(data),20)
        for row in data:
            if int(row["substeps"])!=1:continue
            m=int(row["cells_per_segment"])
            result=audit(m,0.)
            self.assertAlmostEqual(result["native_first_node_ghost_fraction"],
                float(row["predicted_first_node_fraction"]),delta=5e-12)
            self.assertAlmostEqual(result["native_first_node_ghost_fraction"],
                float(row["boundary_n_fraction"]),delta=5e-12)
            self.assertGreater(result["native_first_node_ghost_fraction"],0.)
            self.assertEqual(result["physical_below13p6_fraction"],0.)

    def test_parent_moments_and_child_support(self):
        for m in (4,8,16,32,64,128):
            for c in source_cells(m):
                for cut in (c.lo, (c.lo+c.hi)/2, c.hi):
                    p,a=split_cell(c,cut)
                    ns=sum(v.n for v in (p,a) if v is not None)
                    us=sum(v.u for v in (p,a) if v is not None)
                    self.assertAlmostEqual(ns,c.n,delta=1e-12*max(c.n,1e-20))
                    self.assertAlmostEqual(us,c.u,delta=1e-12*max(c.u,1e-20))
                    for v in (p,a):
                        if v is not None:
                            self.assertGreater(v.n,0)
                            self.assertLessEqual(v.lo-1e-11,v.u/v.n)
                            self.assertLessEqual(v.u/v.n,v.hi+1e-11)

    def test_independent_continuum_and_ledger(self):
        h=math.log(21/20.998)
        reference=independent_reference(h)
        for m in (4,8,16,32,64,128):
            result=audit(m,h)
            self.assertAlmostEqual(result["physical_below13p6_fraction"],
                reference,delta=3e-10)
            self.assertLess(abs(result["N_residual"]),1e-12*result["emitted_n"])
            self.assertLess(abs(result["U_residual_eV"]),1e-12*result["emitted_u_eV"])
            f=result["species_below_cut_fractions"]
            self.assertTrue(0<=f["HI"]<=f["HeI"]<=f["HeII"]<=1)

    def test_invalid_inputs(self):
        for m in (0,-1,1025,4.5,True):
            with self.assertRaises(ValueError):source_cells(m)
        for h in (-0.1,float("nan"),float("inf")):
            with self.assertRaises(ValueError):audit(8,h)
        with self.assertRaises(ValueError):partition(source_cells(4),0.,13.6)

    def test_no_spurious_loss_at_zero_expansion(self):
        for m in (4,8,16,32,64):
            z=audit(m,0.)
            self.assertEqual(z["passive_n"],0.)
            self.assertGreater(z["native_first_node_ghost_fraction"],0.)

    def test_positive_work_and_not_discard_passive(self):
        z=audit(32,math.log(21/20.0))
        self.assertGreater(z["passive_n"],0)
        self.assertGreater(z["passive_u_eV"],0)
        self.assertLess(abs(z["U_residual_eV"]),1e-12*z["emitted_u_eV"])
        # Incorrect passivation by deleting photons demonstrably loses energy.
        wrong=z["emitted_u_eV"]-z["active_u_eV"]-z["redshift_work_eV"]
        self.assertAlmostEqual(wrong,z["passive_u_eV"],delta=1e-11)

if __name__=="__main__":unittest.main()
