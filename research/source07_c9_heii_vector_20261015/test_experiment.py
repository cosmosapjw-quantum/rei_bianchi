#!/usr/bin/env python3
"""Independent scalar oracle and physics/positivity tests for C9."""
import sys
import unittest
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import experiment as c9

# Reproduce C8 scalar method from its original pre-driver section, not C9 math.
reference=HERE.parent/"source07_c8_age_compression_20261015/experiment.py"
ns={"__file__":str(reference),"__name__":"c8_reference"}
reference_source=reference.read_text().split("\nresults=[]\n")[0]
assert "def vector(a,q,gas):" in reference_source
exec(compile(reference_source,str(reference),"exec"),ns)
scalar=ns["vector"]


class FrozenReceiverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=c9.Scenario(c9.ROOT)
        cls.spectrum=c9.Spectrum()
        cls.ages=np.geomspace(cls.model.ar,.2,c9.AGE_COUNT)
        cls.train,cls.hold=c9.gas_states(cls.model)

    def test_scalar_C8_oracle_including_nonzero_helium_II(self):
        """C8 heat includes HeII despite omitting it as a separate output."""
        heii_active_in_any_above_threshold_packet = False
        for q in (-.01,0.,.01):
            for age in (self.ages[0],self.ages[17],self.ages[-1]):
                packets=c9.build_packets(self.model,self.spectrum,np.array([age]),q)
                for state in (self.train[0],self.train[2]):
                    fast=c9.evaluate_packets(packets,state[None,:])[0,0]
                    slow=scalar(float(age),q,tuple(state))
                    indexes=(0,1,2,3,5)
                    for i,j in enumerate(indexes):
                        self.assertAlmostEqual(
                            fast[j],slow[i],delta=1e-10*max(abs(slow[i]),1e-15),
                            msg=f"q={q} age={age} state={state} j={j}")
                    self.assertGreaterEqual(fast[4],0.,"HeII absorption must be nonnegative")
                    heii_active_in_any_above_threshold_packet |= bool(fast[4] > 0.)
        self.assertTrue(heii_active_in_any_above_threshold_packet,
                        "the above-threshold recent cohort must absorb HeII photons")

    def test_boundaries_and_batch_input(self):
        edges=np.array([13.59,13.6,24.58,24.59,54.41,54.42,80.])
        rates=c9.cross_sections(edges)
        self.assertTrue(np.all(rates[:1]==0.))
        self.assertTrue(np.all(rates[:3,2]==0.))
        self.assertTrue(np.all(rates[:4,2]==0.))
        self.assertTrue(np.all(rates[4,2]==0.))
        self.assertGreater(rates[5,2],0.)
        self.assertEqual(rates[2,1],0.)
        self.assertGreater(rates[3,1],0.)
        with self.assertRaises(ValueError):
            c9.evaluate_packets([],np.array([[-1.,1.,0.]]))
        with self.assertRaises(ValueError):
            c9.evaluate_packets([],self.train,dt=-1.)

    def test_independent_number_energy_escape_and_zero_opacity(self):
        for q in (-.01,0.,.01):
            packets=c9.build_packets(self.model,self.spectrum,
                                      self.ages[[0,12,35]],q)
            response=c9.evaluate_packets(packets,np.vstack(
                (np.zeros(3),self.train,self.hold[::13])))
            ledger=c9.physics_ledger(response)
            self.assertLess(ledger["max_photon_residual"],1e-12)
            self.assertLess(ledger["max_energy_residual"],1e-12)
            self.assertEqual(ledger["max_negative_absorption"],0)
            self.assertEqual(ledger["max_negative_escape"],0)
            np.testing.assert_array_equal(response[0,:,2:6],0.)
            np.testing.assert_allclose(response[0,:,0],response[0,:,6],rtol=2e-15)
            np.testing.assert_allclose(response[0,:,1],response[0,:,7],rtol=2e-15)

    def test_positive_age_weights_and_He_simplex(self):
        ages=self.ages
        for q in (-.01,0.,.01):
            weight=c9.source_age_weights(self.model,ages,q)
            self.assertTrue(np.all(weight>0.))
            self.assertAlmostEqual(float(weight.sum()),1.,places=14)
        train,hold=self.train,self.hold
        self.assertTrue(np.all(np.concatenate((train,hold),axis=0)>=0.))
        # HeI+HeII <= fixed primordial He, preserving nonnegative HeIII.
        baseline_He=self.model.nh * 5**3 * .2454/(4*(1.-.2454))
        self.assertTrue(np.all(train[:,1]+train[:,2]<=baseline_He*(1+1e-14)))
        self.assertTrue(np.all(hold[:,1]+hold[:,2]<=baseline_He*(1+1e-14)))

    def test_lp_holdout_and_multishear(self):
        serial=[c9.one_q(q) for q in (-.01,0.,.01)]
        self.assertTrue(all(item["designs"]["5"]["status"]=="SOLVED"
                            for item in serial))
        for item in serial:
            self.assertLess(item["designs"]["5"]["training_max_rel_error"],1e-8)
            self.assertLess(item["designs"]["5"]["holdout_max_rel_error"],1e-8)
            self.assertLess(item["ledger"]["max_energy_residual"],1e-12)
            self.assertGreater(item["designs"]["1"]["holdout_max_rel_error"],1e-5)
        # Different q values must not change a result by a nonfinite value.
        self.assertTrue(np.all(np.isfinite([i["designs"]["5"]["holdout_max_rel_error"]
                                            for i in serial])))


if __name__=="__main__":
    unittest.main(verbosity=2)
