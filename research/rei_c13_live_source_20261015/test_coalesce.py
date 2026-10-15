#!/usr/bin/env python3
"""Positive age-cohort compression, moment parity, guards, future-orbit comparator."""
import sys,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from short_interval import (ROOT,Scenario,NativeStellarSource,PhotonCloud,
                            initial_gas,run)
from coalesce import reduce_age_cohorts,moments

class Coalescence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=Scenario(ROOT)
        cls.source=NativeStellarSource.load(cls.model,HERE/"NATIVE_SOURCE_8X8.csv")
        cls.gas=initial_gas(cls.model,.2)

    def test_supported_two_node_moments_and_frozen_response(self):
        s=self.source;w=.002
        sky=PhotonCloud(np.concatenate((s.energy,s.energy*.9999,s.energy*.9998)),
                        np.concatenate((s.mu,s.mu,s.mu)),
                        np.concatenate((s.weights*w,s.weights*w,s.weights*w)))
        new,r=reduce_age_cohorts(sky,len(s.energy),self.gas,1e12,
                                 event_budget=1e-12,heat_budget=1e-11)
        self.assertTrue(r["admitted"])
        self.assertTrue(r["merged"])
        self.assertEqual(len(new.E),len(s.energy)*2)
        np.testing.assert_allclose(moments(new),moments(sky),rtol=5e-14,atol=1e-22)
        self.assertLessEqual(r["max_event_abs_perH"],1e-12)
        self.assertLessEqual(r["max_heat_abs_eV_perH"],1e-11)

    def test_adversarial_threshold_crossing_is_hold(self):
        cloud=PhotonCloud(np.array([13.6,50.,99.]),
                          np.array([.3,.3,.3]),
                          np.array([.4,.2,.4]))
        after,receipt=reduce_age_cohorts(cloud,1,self.gas,1e12,
                        event_budget=1e-15,heat_budget=1e-13)
        self.assertFalse(receipt["admitted"])
        self.assertEqual(after.packet_count,cloud.packet_count)
        self.assertGreater(receipt["max_event_abs_perH"],1e-15)

    def test_real_evolving_source_all_signs_dense_vs_admitted_coalescence(self):
        for q in (0.,-.01,.01):
            full=run(q,self.source,nstep=64)
            thin=run(q,self.source,nstep=64,coalescence_budget=(1e-12,1e-11))
            self.assertEqual(thin["coalescence_holds"],0)
            self.assertEqual(thin["coalescence_admitted_count"],63)
            self.assertEqual(thin["end"]["packet_count"],384)
            self.assertEqual(full["end"]["packet_count"],24576)
            self.assertLess(abs(full["end"]["x_HII"]-thin["end"]["x_HII"]),1e-9)
            self.assertLess(abs(full["end"]["Tgas_K"]-thin["end"]["Tgas_K"]),.0001)
            self.assertLess(abs(full["end"]["Pi_ion_Pa"]-thin["end"]["Pi_ion_Pa"]),1e-25)
            self.assertLess(thin["max_energy_eV_perH_residual"],3e-11)
            self.assertLess(thin["max_number_abs_residual"],3e-13)

if __name__=="__main__":unittest.main(verbosity=2)
