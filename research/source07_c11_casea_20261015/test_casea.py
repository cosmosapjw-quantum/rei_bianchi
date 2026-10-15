#!/usr/bin/env python3
"""C11 Case-A owner/collision-event/analytic/continuum-limit tests."""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np
from scipy.linalg import expm

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import casea as x
from rate_table import CaseARates,ConstantRates,RateDomainError


class C11CaseATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider=CaseARates()
        cls.model=x.C9.Scenario(x.ROOT)
        cls.gas=x.c10.Gas.initial(cls.model)

    def test_source_table_domain_and_positive(self):
        self.assertEqual(self.provider.values.shape,(129,8))
        self.assertLess(self.provider.exact_grid_parity(),1e-12)
        for t in (10000.01,11522.11,17001.7,23999.8):
            r=self.provider(t)
            self.assertTrue(np.all(np.isfinite(r)))
            self.assertTrue(np.all(r>0.))
        for t in (1.,9999.,24001.,1000000.,float("nan")):
            with self.assertRaises(RateDomainError):
                self.provider(t)

    def test_frozen_he_analytic_chain_matrix_exponential(self):
        for k2,k3 in ((1e-12,2e-12),(2e-12,1e-12),(1e-12,1e-12),
                      (1e-12,1e-12*(1.+1e-13)),(0.,3e-12),(3e-12,0.)):
            h0=.7;y0=.3;z0=.4
            dt=2e11
            h,y,z,events=x.rec_analytic(h0,y0,z0,1.5e-12,k2,k3,dt)
            Q=np.array([[0,k2,0],[0,-k2,k3],[0,0,-k3]])
            ref=expm(dt*Q)@np.array([1.5,y0,z0])
            self.assertAlmostEqual(y,ref[1],delta=1e-13)
            self.assertAlmostEqual(z,ref[2],delta=1e-13)
            self.assertTrue(np.all(events>=-1e-14))
            self.assertAlmostEqual(events[1],y0+z0-y-z,delta=1e-14)
            self.assertAlmostEqual(events[2],z0-z,delta=1e-14)
        self.assertAlmostEqual(x.stable_divided_exponential(2e-12,2e-12,1e11),
                               1e11*math.exp(-.2),delta=.0001)

    def test_manufactured_H_only_recombination_analytic_refinement(self):
        # ne = nHII; HII'=-alpha*nHII^2 has exact rational positive solution.
        alpha=3e-13;nh=.001;hii0=.0008;dt=5e14
        gas=x.c10.Gas(nh,0.,nh-hii0,0.,0.,
                     1.5*x.c10.KB_EV_K*12000.*(nh+hii0))
        provider=ConstantRates(rr=(alpha,0.,0.))
        exact=hii0/(1.+alpha*hii0*dt)
        errors=[]
        for n in (4,8,16,32,64,128,256):
            now=gas
            escaped=0.
            rec=0.
            for i in range(n):
                now,event=x.rec_step(now,dt/n,provider)
                escaped+=event["escape_eV_cm3"]
                rec+=sum(event["recomb_events_cm3"])
            errors.append(abs(now.nHII-exact))
            self.assertAlmostEqual(rec,hii0-now.nHII,delta=1e-16)
            self.assertLess(abs(now.binding_eV_cm3+now.thermal_eV_cm3+escaped-
                                gas.binding_eV_cm3-gas.thermal_eV_cm3),1e-14)
            self.assertAlmostEqual(now.nHI+now.nHII,nh,delta=1e-16)
            self.assertLess(abs(now.thermal_eV_cm3-gas.thermal_eV_cm3),1e-15)
        self.assertGreater(errors[0],errors[-1])
        self.assertLess(errors[-1],3e-12)
        self.assertGreater(errors[-2]/errors[-1],3.1)

    def test_casea_negative_temperature_guard_no_clamp(self):
        bad=x.c10.Gas(self.gas.nH,self.gas.nHe,self.gas.nHI,
                       self.gas.nHeI,self.gas.nHeII,self.gas.thermal_eV_cm3*.5)
        self.assertLess(bad.temperature_K,10000.)
        with self.assertRaises(x.c10.StepFailure):
            x.rec_step(bad,1e12,self.provider)

    def test_grackle_he_rec_photo_ledger(self):
        m=self.model
        for q,source in ((0.,"bb50k"),(.01,"hard")):
            run=x.one_run(q,source,nsteps=16,interval_s=1e12,
                          compress=False,provider=self.provider)
            r=run["final"]
            self.assertGreater(r["radiative_escape_eV_per_H"],0.)
            self.assertGreater(r["cumulative_recombination_electrons_per_H"],0.)
            self.assertLess(run["max_energy_residual_eV_per_H"],1e-10)
            self.assertLess(run["max_electron_photon_residual_per_H"],1e-10)
            self.assertTrue(all(np.isfinite(list(a.values())).all()
                                for a in run["history"]))
            self.assertTrue(all(0<=a["x_HII"]<=1 and
                                0<=a["x_HeII"]<=1 and
                                0<=a["x_HeIII"]<=1 and
                                a["x_HeII"]+a["x_HeIII"]<=1+1e-12
                                for a in run["history"]))

    def test_second_order_strang_self_convergence(self):
        runs=[x.one_run(0.,"bb50k",nsteps=n,interval_s=1e12,
                         compress=True,provider=self.provider)
              for n in (8,16,32,64)]
        for field in ("x_HII","Tgas_K"):
            vals=[a["final"][field] for a in runs]
            gaps=[abs(vals[i+1]-vals[i]) for i in range(len(vals)-1)]
            ratios=[gaps[i]/gaps[i+1] for i in range(2)]
            for ratio in ratios:
                self.assertGreater(ratio,3.3,msg=(field,gaps,ratios))
                self.assertLess(ratio,4.7,msg=(field,gaps,ratios))

    def test_positive_source_dependent_compression_vs_dense(self):
        for source in ("bb50k","hard"):
            base=x.one_run(0.,source,nsteps=24,compress=False,
                           provider=self.provider)
            light=x.one_run(0.,source,nsteps=24,compress=True,
                            provider=self.provider)
            self.assertLess(light["kept_age_nodes"],base["kept_age_nodes"])
            self.assertLess(light["max_energy_residual_eV_per_H"],1e-10)
            for field,tolerance in (("x_HII",1e-7),("x_HeII",1e-7),
                                    ("Tgas_K",.002),
                                    ("radiative_escape_eV_per_H",1e-6)):
                self.assertLess(abs(base["final"][field]-light["final"][field]),tolerance)

    def test_invalid_and_zero_recombination(self):
        z=ConstantRates()
        gas,receipt=x.rec_step(self.gas,1e12,z)
        # Scientific state equivalence, not byte-identical roundoff of nHe-y-z.
        for k in ("nHI","nHeI","nHeII","thermal_eV_cm3","ne","temperature_K"):
            self.assertAlmostEqual(getattr(gas,k),getattr(self.gas,k),delta=1e-14)
        self.assertEqual(receipt["escape_eV_cm3"],0.)
        with self.assertRaises(ValueError):
            x.rec_step(self.gas,-1,z)
        with self.assertRaises(ValueError):
            x.stable_divided_exponential(-1,0,10)


if __name__=="__main__":
    unittest.main(verbosity=2)
