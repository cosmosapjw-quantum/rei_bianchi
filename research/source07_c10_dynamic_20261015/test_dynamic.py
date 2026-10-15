#!/usr/bin/env python3
"""Physical invariants, independent analytic one-channel limit, and C9 parity."""
import math
import sys
import unittest
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import dynamic as d


class PhotonChemistryTests(unittest.TestCase):
    def test_exact_single_hydrogen_species_analytic_limit(self):
        """Closed photon/H scheme N'=-k*N*(nHI0-N0+N), independent of C9."""
        nH,nHe,nHI,nHeI,nHeII=0.001,0.0001,0.0008,0.0001,0.
        ne=nH-nHI
        u=1.5*d.KB_EV_K*10000.*(nH+nHe+ne)
        gas=d.Gas(nH,nHe,nHI,nHeI,nHeII,u)
        N0=.0002
        energy=np.array([20.])
        cross=np.array([[2e-18,0.,0.]])
        packet=d.Packets(energy,cross,cross*np.maximum(energy[:,None]-d.c9.BIND[None,:],0.),
                         np.array([N0]))
        dt=1e10
        k=d.c9.C_CGS*cross[0,0]
        excess=nHI-N0
        exact=(excess*N0*math.exp(-k*excess*dt)/
               (excess+N0*(1.-math.exp(-k*excess*dt))))
        errors=[]
        for n in (4,8,16,32,64):
            ans=d.propagate(packet,gas,nsteps=n,interval=dt)
            recovered=ans["final"]["photon_N_per_H"]*nH
            errors.append(abs(recovered-exact))
            self.assertLess(ans["max_total_energy_rel_residual"],1e-12)
            self.assertLess(ans["max_photon_plus_electron_rel_residual"],1e-12)
        self.assertGreater(errors[0],errors[-1])
        self.assertLess(errors[-1],2e-10)
        self.assertGreater(errors[-2]/errors[-1],3.2)
        self.assertLess(errors[-2]/errors[-1],4.8)

    def test_scalar_vector_independent_event_parity(self):
        model=d.c9.Scenario(d.ROOT)
        spectrum=d.c9.Spectrum()
        ages=np.array([model.ar,.2])
        gas=d.Gas.initial(model)
        for q in (-.01,0.,.01):
            two=d.c9.build_packets(model,spectrum,ages,q)
            E,weights,sigma,sig_heat=two[1]
            pop=weights*gas.nH*.4
            for dt in (0.1,1e8,1e10):
                ev,heat,eng,remain,absorbed=d.reactions_vector(
                    pop,E,sigma,sig_heat,gas.neutral,dt)
                sev,sheat,seng,scount=d.reactions_scalar(
                    pop,E,sigma,gas.neutral,dt)
                np.testing.assert_allclose(ev,sev,rtol=1e-11,atol=1e-21)
                np.testing.assert_allclose((heat,eng,absorbed),
                                           (sheat,seng,scount),
                                           rtol=1e-10,atol=1e-21)
                self.assertLess(abs(pop.sum()-remain.sum()-absorbed),1e-12*gas.nH)

    def test_case_BB_and_hard_dynamic_ledgers(self):
        for source in ("bb50k","hard"):
            r=d.one_run(0.,source,nsteps=12,
                        photons_per_H=1.,interval_s=1e12)
            for obj in (r["dense"], *(x["simulation"] for x in r["alternatives"].values())):
                self.assertLess(obj["max_total_energy_rel_residual"],1e-12)
                self.assertLess(obj["max_photon_plus_electron_rel_residual"],1e-12)
                self.assertGreater(obj["final"]["Tgas_K"],12000.)
                self.assertGreater(obj["final"]["x_HII"],.40)
                self.assertTrue(all(0<=h["x_HII"]<=1 and 0<=h["x_HeII"]<=1
                                    and 0<=h["x_HeIII"]<=1 for h in obj["history"]))
                self.assertTrue(all(h["x_HeII"]+h["x_HeIII"]<=1+1e-12
                                    for h in obj["history"]))
            five=r["alternatives"]["frozen_train_5"]["dynamic_disagreement"]
            one=r["alternatives"]["frozen_train_1"]["dynamic_disagreement"]
            self.assertLess(five["x_HII"]["max_abs"],one["x_HII"]["max_abs"])
            self.assertLess(five["Tgas_K"]["max_abs"],one["Tgas_K"]["max_abs"])
            self.assertLess(five["Tgas_K"]["max_abs"],.1)

    def test_Helium_first_and_second_photoionization_from_zero_HeII(self):
        nH,nHe=0.001,0.0001
        nHI=0.
        ne=nH
        u=1.5*d.KB_EV_K*9000.*(nH+nHe+ne)
        gas=d.Gas(nH,nHe,nHI,nHe,0.,u)
        energy=np.array([80.])
        cross=np.array([[0.,1e-17,1e-17]])
        packet=d.Packets(energy,cross,cross*np.maximum(energy[:,None]-d.c9.BIND[None,:],0.),
                         np.array([.0002]))
        g,p,r=d.midpoint_step(gas,packet,1e10)
        self.assertLess(g.nHeI,gas.nHeI)
        self.assertGreater(g.nHeII,0.)
        self.assertGreater(g.nHeIII,0.)
        self.assertAlmostEqual(g.nHeI+g.nHeII+g.nHeIII,nHe,delta=1e-15)
        self.assertLess(abs(p.n+g.ne-(packet.n+gas.ne)),5e-14)
        self.assertLess(abs(p.u+g.thermal_eV_cm3+g.binding_eV_cm3
                            -(packet.u+gas.thermal_eV_cm3+gas.binding_eV_cm3)),1e-12)

    def test_invalid_inputs(self):
        gas=d.Gas(1e-3,1e-4,-1e-5,1e-4,0.,.01)
        with self.assertRaises(d.StepFailure):
            gas.check()
        packet=d.Packets(np.array([30.]),np.array([[1e-18,0.,0.]]),
                         np.array([[1e-17,0.,0.]]),np.array([1e-5]))
        with self.assertRaises(ValueError):
            d.propagate(packet,d.Gas(1e-3,1e-4,.0005,.0001,0.,.01),nsteps=0)
        with self.assertRaises(ValueError):
            d.midpoint_step(d.Gas(1e-3,1e-4,.0005,.0001,0.,.01),packet,-1)


if __name__=="__main__":
    unittest.main(verbosity=2)
