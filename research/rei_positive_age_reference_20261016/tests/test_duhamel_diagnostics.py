"""Falsification-oriented research regression for prescribed-source/opacity C7-C8.
No test promotes the conditional model to native chemistry full-history truth.
"""
import json
import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from duhamel_diagnostics import (ManufacturedCase, duhamel_survivor,
    independent_reference, finite_slab_history, midpoint_impulse_hazard_reference,
    adaptive_positive)
from positive_reference import frozen_slab


class DuhamelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case=ManufacturedCase()
        cls.ref=independent_reference(cls.case)

    def test_exact_piecewise_optical_depth(self):
        c=self.case
        self.assertAlmostEqual(c.depth(1),c.hi_base+c.hei_base+0.5*(c.hi_growth+c.hei_growth)+c.heii_on*(1-c.event_x))
        h=1e-7
        for x in (0.15,0.60,0.80,0.92):
            self.assertAlmostEqual((c.depth(x+h)-c.depth(x-h))/(2*h),sum(c.rates(x)),delta=2e-7)

    def test_strict_event_is_applied_once(self):
        c=self.case
        self.assertEqual(c.rates(c.event_x-1e-9)[2],0)
        self.assertEqual(c.rates(c.event_x+1e-9)[2],c.heii_on)
        self.assertAlmostEqual(c.depth(c.event_x+1e-9)-c.depth(c.event_x-1e-9),
                               2e-9*sum(c.rates(c.event_x-1e-9))+1e-9*c.heii_on,delta=2e-12)

    def test_duhamel_initial_exact(self):
        self.assertEqual(duhamel_survivor(self.case,0),self.case.old)

    def test_duhamel_reference_positive(self):
        for x in (0,.1,.3,.7,.73,.731,.91,1):
            self.assertGreaterEqual(duhamel_survivor(self.case,x),0)

    def test_independent_species_mass_and_energy(self):
        r=self.ref
        self.assertLess(abs(r['photon_residual']),2e-12)
        self.assertLess(abs(r['energy_residual_ev']),5e-10)
        self.assertEqual(len(r['absorbed']),3)
        self.assertTrue(all(v>0 for v in r['absorbed']))
        self.assertGreater(r['heat_ev'],0)

    def test_exact_integrated_source(self):
        self.assertAlmostEqual(self.ref['emitted'],1.15,places=14)
        for n in (4,8,32,128):
            self.assertAlmostEqual(finite_slab_history(self.case,n)['emitted'],1.15,delta=1e-13)

    def test_event_split_converges_with_resolution(self):
        errs=[]
        for n in (8,16,32,64,128):
            a=finite_slab_history(self.case,n,True)
            errs.append(abs(a['survived']-self.ref['survived']))
        self.assertTrue(all(b<a for a,b in zip(errs,errs[1:])),errs)
        self.assertLess(errs[-1],7e-9)

    def test_event_split_improves_over_undivided_grid(self):
        for n in (8,16,32,64,128):
            a=finite_slab_history(self.case,n,True)
            b=finite_slab_history(self.case,n,False)
            self.assertLess(abs(a['survived']-self.ref['survived']),
                            abs(b['survived']-self.ref['survived']))

    def test_midpoint_impulse_stiff_bias(self):
        n=8
        impulse=midpoint_impulse_hazard_reference(self.case,n)
        phi=finite_slab_history(self.case,n,True)['survived']
        self.assertGreater(abs(impulse-self.ref['survived']),1e-3)
        self.assertLess(abs(phi-self.ref['survived']),1e-6)

    def test_species_event_heat_converges(self):
        for metric in ('heat_ev','binding_ev'):
            errs=[abs(finite_slab_history(self.case,n)[metric]-self.ref[metric]) for n in (16,32,64,128)]
            self.assertTrue(all(b<a for a,b in zip(errs,errs[1:])),(metric,errs))

    def test_finite_slab_ledgers(self):
        for n in (8,16,32,128):
            for split in (True,False):
                r=finite_slab_history(self.case,n,split)
                self.assertGreaterEqual(r['survived'],0)
                self.assertTrue(all(v>=0 for v in r['absorbed']))
                self.assertLess(abs(r['photon_residual']),3e-13)
                self.assertLess(abs(r['energy_residual_ev']),3e-11)

    def test_frozen_steady_limit(self):
        c=ManufacturedCase(source_growth=0.,hi_growth=0.,hei_growth=0.,heii_on=0.)
        ref=independent_reference(c)
        for n in (1,2,8,16):
            v=finite_slab_history(c,n)
            self.assertAlmostEqual(v['survived'],ref['survived'],delta=2e-14)

    def test_adaptive_refinement(self):
        errs=[]
        for tol in (1e-4,1e-6,1e-8):
            r=adaptive_positive(self.case,tol,max_leaf=20000)
            errs.append(abs(r['survived']-self.ref['survived']))
            self.assertGreaterEqual(r['survived'],0)
            self.assertLess(abs(r['photon_residual']),1e-11)
            self.assertLess(abs(r['energy_residual_ev']),1e-9)
        self.assertTrue(all(b<a for a,b in zip(errs,errs[1:])),errs)
        self.assertLess(errs[-1],1e-9)

    def test_adaptive_budget_reject(self):
        with self.assertRaises(RuntimeError):adaptive_positive(self.case,rtol=1e-10,max_leaf=5)

    def test_input_validation(self):
        with self.assertRaises(ValueError):ManufacturedCase(event_x=0)
        with self.assertRaises(ValueError):ManufacturedCase(energy_ev=40)
        with self.assertRaises(ValueError):ManufacturedCase(heii_on=-1)
        with self.assertRaises(ValueError):duhamel_survivor(self.case,2)
        with self.assertRaises(ValueError):finite_slab_history(self.case,0)
        with self.assertRaises(ValueError):adaptive_positive(self.case,rtol=0)

    def test_zero_source_needs_initial(self):
        c=ManufacturedCase(old=0.,source_level=0.)
        r=independent_reference(c)
        self.assertEqual(r['survived'],0)
        self.assertEqual(r['photon_residual'],0)
        self.assertEqual(r['energy_residual_ev'],0)

    def test_earlier_native_exposure_not_single_constant(self):
        p=ROOT/'results/native_age_summary.json'
        d=json.loads(p.read_text())['by_signed_s_over_H']['0']
        t1=d['effective_constant_opacity_depth_from_first_ratio']
        t2=d['effective_constant_opacity_depth_from_second_ratio']
        self.assertAlmostEqual(t1,150.09681238103187,delta=1e-9)
        self.assertAlmostEqual(t2,193.66043926495212,delta=1e-9)
        self.assertGreater(abs(t2-t1)/t1,0.25)


if __name__=='__main__':unittest.main()