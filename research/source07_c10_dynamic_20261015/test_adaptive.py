#!/usr/bin/env python3
"""Independent adaptive acceptance and analytically solvable sink checks."""
import math
import sys
import unittest
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import adaptive as a
import dynamic as d


class AdaptiveTests(unittest.TestCase):
    def test_cold_one_species_analytic_reference_and_ledger(self):
        nh=.001
        ne_initial=.0002
        gas=d.Gas(nh,.0001,.0008,.0001,0.,
                  1.5*d.KB_EV_K*10000.*(nh+.0001+ne_initial))
        sigma=np.array([[2e-18,0,0]])
        E=np.array([20.])
        packets=d.Packets(E,sigma,sigma*np.maximum(E[:,None]-d.c9.BIND[None,:],0.),
                          np.array([.0002]))
        dt=1e10
        before=packets.n
        excess=gas.nHI-before
        k=d.c9.C_CGS*sigma[0,0]
        expected=excess*before*math.exp(-k*excess*dt)/(
                 excess+before*(1.-math.exp(-k*excess*dt)))
        tolerance=np.array([2e-8,1e-8,1e-8,.01,2e-8,1e-5])
        x=a.propagate_adaptive(packets,gas,interval_s=dt,initial_step_s=dt,
                               tolerance=tolerance)
        y=d.propagate(packets,gas,nsteps=256,interval=dt)
        self.assertGreater(x["accepted"],2)
        self.assertLess(x["max_total_energy_relative_residual"],1e-12)
        self.assertLess(x["max_photon_electron_relative_residual"],1e-12)
        self.assertLess(abs(x["final"]["photon_N_per_H"]*nh-expected),2e-9)
        self.assertLess(abs(x["final"]["x_HII"]-y["final"]["x_HII"]),1e-5)

    def test_full_and_reduced_hhe_adaptive(self):
        for source in ("bb50k","hard"):
            r=a.test_case(source)
            self.assertIn("dense36",r["cases"])
            self.assertIn("compressed",r["cases"])
            left=r["cases"]["dense36"];right=r["cases"]["compressed"]
            for v in (left,right):
                adap=v["adaptive"]
                self.assertGreater(adap["accepted"],0)
                self.assertEqual(adap["history"][-1]["time_s"],1e12)
                self.assertLess(adap["max_total_energy_relative_residual"],1e-12)
                self.assertLess(adap["max_photon_electron_relative_residual"],1e-12)
                self.assertLess(v["ref_delta"]["x_HII"],1e-5)
                self.assertLess(v["ref_delta"]["Tgas_K"],.1)
                self.assertLessEqual(adap["max_local_estimator_over_tolerance"],1.+1e-12)
            self.assertLess(abs(left["adaptive"]["final"]["Tgas_K"]-
                                right["adaptive"]["final"]["Tgas_K"]),.01)
            self.assertLess(abs(left["adaptive"]["final"]["x_HeII"]-
                                right["adaptive"]["final"]["x_HeII"]),1e-7)

    def test_invalid_inputs(self):
        m=d.c9.Scenario(d.ROOT)
        gas=d.Gas.initial(m)
        packet=d.Packets(np.array([20.]),np.array([[0.,0.,0.]]),
                         np.array([[0.,0.,0.]]),np.array([.0001]))
        with self.assertRaises(ValueError):
            a.propagate_adaptive(packet,gas,interval_s=-1)
        with self.assertRaises(ValueError):
            a.propagate_adaptive(packet,gas,tolerance=[1,0,1,1,1,1])


if __name__=="__main__":
    unittest.main(verbosity=2)
