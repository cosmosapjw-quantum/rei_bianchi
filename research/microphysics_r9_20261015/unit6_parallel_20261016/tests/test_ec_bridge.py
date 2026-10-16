"""One bounded EC contract suite; records raw numerical outputs for review."""
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time
import unittest

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("ec_bridge",ROOT/"code/ec_bridge.py")
ec=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ec)
START=time.perf_counter()
OBS=[]
RESULT=None


class ECTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=json.loads((ROOT/"spec/EC_CONTRACT.json").read_text())
        cls.report=ec.conditional_donor_report()
        cls.inventory=cls.report["inventory"]

    def tearDown(self):
        global RESULT
        RESULT=self._outcome.result

    def close(self,actual,expected,donor=False):
        floor=1e-25 if donor else 5e-14
        rel=1e-12 if donor else 0.
        self.assertLessEqual(abs(actual-expected),floor+rel*abs(expected),(actual,expected))

    def event_checks(self,result,scale,channel):
        Cb=result["total_bound_count"];Cc=result["total_continuum_count"]
        count=Cb+Cc
        expected={"free_electrons":-Cc,"bound_electrons":-Cb,"nuclear_charge":-count,
                  "ionic_charge":-Cc,"nuclei":0.,"baryons":0.,"net_charge":0.}
        for key,value in expected.items():
            self.close(result["signed_rewards"][key],value,donor=scale<1.)
            # A large absolute background cannot resolve donor-relative deltas.
            initial=result["ledgers_before"][key]
            final=result["ledgers_after"][key]
            tolerance=(1e-25+1e-12*max(abs(initial),abs(value))) if key in ("nuclei","baryons","nuclear_charge","bound_electrons","ionic_charge") else 5e-14*max(1.,abs(initial))
            self.assertLessEqual(abs(final-(initial+value)),tolerance,(key,initial,final,value))
        self.close(result["emitted_neutrinos"],count,donor=scale<1.)
        self.close(result["delta_free"],-Cc,donor=scale<1.)
        self.close(result["delta_bound"],-Cb,donor=scale<1.)
        before=result["ledgers_before"]["baryons"]
        after=result["ledgers_after"]["baryons"]
        if before:self.assertLessEqual(abs(after-before)/before,1e-12)
        self.assertGreaterEqual(float(result["be"].min()),-5e-14)
        self.assertGreaterEqual(float(result["li"].min()),-5e-14)
        self.assertIsNone(result["heat"])
        self.assertEqual(result["heat_status"],"NEEDS_ENERGY_PARTITION")

    def cross_method(self,name,be,li,b,c,dt,free,donor=False):
        exact=ec.frozen_hazard_step(be,li,free,b,c,dt)
        uniform,diagnostics=ec.uniformization_step(be,li,b,c,dt)
        analytic=np.concatenate((exact["be"],exact["li"]))
        floor=1e-25 if donor else 1e-15
        allowed=floor+1e-12*np.abs(analytic)
        self.assertTrue(np.all(np.abs(uniform-analytic)<=allowed),(name,uniform,analytic,allowed))
        self.assertLessEqual(diagnostics["omitted_tail_bound"],1e-14)
        self.assertGreaterEqual(float(uniform.min()),-5e-14)
        G=ec.build_generator(b,c)
        self.assertLessEqual(float(np.abs(G.sum(axis=0)).max()),5e-14)
        off=G.copy();np.fill_diagonal(off,0)
        self.assertGreaterEqual(float(off.min()),0.)
        scipy_error=None
        try:
            from scipy.linalg import expm
            reference=expm(dt*G)@np.concatenate((be,li))
            self.assertTrue(np.all(np.abs(reference-analytic)<=allowed))
            scipy_error=float(np.max(np.abs(reference-analytic)))
        except ImportError:
            pass
        OBS.append({"name":name,"analytic":exact,"uniformization":uniform,"uniformization_diagnostics":diagnostics,
                    "max_cross_method_error":float(np.max(np.abs(uniform-analytic))),"scipy_expm_max_error":scipy_error,
                    "generator":G,"generator_off_diagonal_min":float(off.min())})
        return exact

    def test_01_all_eight_single_channels_unit_and_donor(self):
        for scale in (1.,self.inventory["original_Y_final"]["Be7"]):
            for channel,q in [("bound",q) for q in range(4)]+[("continuum",q) for q in range(1,5)]:
                be=np.zeros(5);be[q]=scale
                b=np.zeros(5);c=np.zeros(5)
                (b if channel=="bound" else c)[q]=1.
                result=self.cross_method(f"single_{channel}_q{q}_{'unit' if scale==1 else 'donor'}",be,np.zeros(4),b,c,math.log(2),2.,scale<1)
                expected_be=be.copy();expected_be[q]=scale/2
                daughter=q if channel=="bound" else q-1
                expected_li=np.zeros(4);expected_li[daughter]=scale/2
                for actual,expected in zip(result["be"],expected_be):self.close(actual,expected,scale<1)
                for actual,expected in zip(result["li"],expected_li):self.close(actual,expected,scale<1)
                self.close(result["total_bound_count"],scale/2 if channel=="bound" else 0,scale<1)
                self.close(result["total_continuum_count"],scale/2 if channel=="continuum" else 0,scale<1)
                self.event_checks(result,scale,channel)

    def test_02_zero_competing_and_split_uniformization(self):
        zero=self.contract["fixtures"][0]
        result=ec.frozen_hazard_step(zero["be"],zero["li"],zero["free"],zero["b"],zero["c"],zero["dt"])
        np.testing.assert_array_equal(result["be"],zero["be"])
        np.testing.assert_array_equal(result["li"],zero["li"])
        self.assertEqual(result["electron_ledger"],zero["free"])
        self.assertTrue(all(value==0 for value in result["ledger_residuals"].values()))
        uniform,diagnostics=ec.uniformization_step(zero["be"],zero["li"],zero["b"],zero["c"],zero["dt"])
        np.testing.assert_array_equal(uniform,np.r_[zero["be"],zero["li"]])
        self.assertEqual(diagnostics["omitted_tail_bound"],0)
        OBS.append({"name":"zero_hazard_exact","result":result,"uniformization_diagnostics":diagnostics})
        for q in (1,2,3):
            be=np.zeros(5);be[q]=1.
            b=np.zeros(5);c=np.zeros(5);b[q]=.6;c[q]=.4
            result=self.cross_method(f"competition_q{q}",be,np.zeros(4),b,c,math.log(2),2.)
            self.close(result["be"][q],.5)
            self.close(result["li"][q],.3)
            self.close(result["li"][q-1],.2)
            self.close(result["delta_free"],-.2)
            self.close(result["delta_bound"],-.3)
            self.event_checks(result,1.,"competition")
        b=np.array([.2,.4,.6,.8,0.]);c=np.array([0.,.1,.2,.3,1.])
        self.cross_method("mixed_split_exposure25",np.array([.1,.2,.3,.4,.5]),np.array([.6,.7,.8,.9]),b,c,25.,2.)

    def test_03_invalid_budget_forbidden_and_finite_inputs(self):
        be=np.zeros(5);be[4]=1.
        b=np.zeros(5);c=np.zeros(5);c[4]=1.
        errors=[]
        with self.assertRaisesRegex(ValueError,"ELECTRON_BUDGET_EXCEEDED"):
            ec.frozen_hazard_step(be,np.zeros(4),.1,b,c,math.log(2))
        errors.append("ELECTRON_BUDGET_EXCEEDED")
        for channel,q,message in (("bound",4,"NO_BOUND_ELECTRON"),("continuum",0,"EXCLUDED_CHANNEL_LI_MINUS")):
            bad_b=np.zeros(5);bad_c=np.zeros(5)
            (bad_b if channel=="bound" else bad_c)[q]=1.
            with self.assertRaisesRegex(ValueError,message):ec.frozen_hazard_step(be,np.zeros(4),2.,bad_b,bad_c,1.)
            errors.append(message)
        for bad_be,bad_li,free,dt in (([-1.,0.,0.,0.,0.],np.zeros(4),2.,1.),(np.zeros(4),np.zeros(4),2.,1.),
                                      (np.full(5,np.nan),np.zeros(4),2.,1.),(be,np.zeros(4),-1.,1.),
                                      (be,np.zeros(4),np.inf,1.),(be,np.zeros(4),2.,np.inf),(be,np.zeros(4),2.,-1.)):
            with self.assertRaises(ValueError):ec.frozen_hazard_step(bad_be,bad_li,free,np.zeros(5),np.zeros(5),dt)
        for bad_hazard in (np.array([0.,-1.,0.,0.,0.]),np.array([0.,np.inf,0.,0.,0.])):
            with self.assertRaises(ValueError):ec.frozen_hazard_step(be,np.zeros(4),2.,bad_hazard,np.zeros(5),1.)
        counts=np.zeros(5);counts[4]=.5000000000001
        # The signed reward and raw tiny deficit are retained, with no clipping.
        tiny=ec.apply_event_counts(be,np.zeros(4),.5,np.zeros(5),counts)
        self.assertLess(tiny["electron_ledger"],0)
        self.assertEqual(tiny["electron_ledger"],.5-counts[4])
        self.assertEqual(tiny["delta_free"],-counts[4])
        over=np.zeros(5);over[4]=1.01
        with self.assertRaisesRegex(ValueError,"PARENT_BUDGET_EXCEEDED"):ec.apply_event_counts(be,np.zeros(4),2.,np.zeros(5),over)
        OBS.append({"name":"rejections_and_roundoff_negative","expected_errors":errors,"tiny_negative_result":tiny,"clipped":False})

    def test_04_actual_donor_inventory_and_bare_default(self):
        inv=self.inventory
        self.assertEqual(inv["identity"]["sha256"],self.contract["donor"]["sha256"])
        self.assertEqual(len(inv["tracked22"]),22)
        self.assertFalse(inv["native17_claim"])
        self.assertEqual(inv["Be_move_count"],1)
        self.assertNotIn("Be7",inv["excluded_after_Be_move"])
        self.assertIn("Be7",inv["old_excluded"])
        self.assertEqual(inv["excluded_after_Be_move"],{k:v for k,v in inv["old_excluded"].items() if k!="Be7"})
        self.assertLessEqual(abs(inv["baryon_map_residual"]),5e-14)
        self.assertLessEqual(abs(inv["tracked_electron_closure_residual"]),5e-14)
        self.assertEqual(inv["normalization_defect_unrepaired"],inv["full_baryons"]-1.)
        self.assertNotEqual(inv["normalization_defect_unrepaired"],0.)
        for key in ("Be7","Li7","p"):
            self.assertEqual(inv["original_Y_final"][key],self.contract["donor"][key])
        np.testing.assert_array_equal(inv["be"],self.contract["donor"]["initial_Be_default"])
        np.testing.assert_array_equal(inv["li"],self.contract["donor"]["initial_Li_default"])
        b=np.array([1.,1.,1.,1.,0.])
        result=ec.frozen_hazard_step(inv["be"],inv["li"],inv["tracked_free_electrons"],b,np.zeros(5),10.)
        np.testing.assert_array_equal(result["be"],inv["be"])
        np.testing.assert_array_equal(result["li"],inv["li"])
        self.assertEqual(result["delta_free"],0.)
        OBS.append({"name":"actual_bare_donor_no_bound_capture","result":result})

    def test_05_donor_exposure_families_complete_limit_and_clocks(self):
        B=self.inventory["original_Y_final"]["Be7"]
        L=self.inventory["original_Y_final"]["Li7"]
        for family in self.report["exposure_families"]:
            u=family["exposure"];result=family["result"]
            survival=B*math.exp(-u);count=B*(-math.expm1(-u))
            self.close(float(sum(result["be"])),survival,True)
            self.close(float(sum(result["li"])),L+count,True)
            self.close(result["li"][3],count,True)
            self.close(result["delta_free"],-count if family["channel"]=="continuum" else 0.,True)
            self.assertLessEqual(abs(result["electron_ledger"]-(1.+result["delta_free"])),5e-14)
            self.event_checks(result,B,family["channel"])
            be=np.zeros(5);be[family["prepared_q"]]=B
            b=np.zeros(5);c=np.zeros(5)
            (b if family["channel"]=="bound" else c)[family["prepared_q"]]=1.
            self.cross_method(f"actual_donor_{family['channel']}_u{u}",be,self.inventory["li"],b,c,u,1.,True)
        complete=next(f for f in self.contract["fixtures"] if f["id"]=="actual_donor_complete_limit")
        for key in ("Be_total","Li_total","mass7_baryons","Li_total_over_donor_p"):
            self.close(self.report["analytic_complete_limit"][key],complete[key],True)
        expected_clock=next(f for f in self.contract["fixtures"] if f["id"]=="conditional_hydrogenic_clock")
        self.close(self.report["hydrogenic_clock"]["anchors"][0]["lambda_b3_s-1"],expected_clock["lambda_b3_s-1"],True)
        for anchor,expected in zip(self.report["hydrogenic_clock"]["anchors"],expected_clock["anchors"]):
            result=anchor["result"]
            self.assertEqual(anchor["elapsed_days"],expected["elapsed_days"])
            self.close(result["be"][3],expected["Be3"],True)
            self.close(result["li"][3],expected["Li3_increment"],True)
            self.close(sum(result["li"]),expected["Li_total"],True)
            self.assertEqual(result["delta_free"],0.)

    def test_06_prescribed_density_and_energy_only_synthetic(self):
        kappa=np.array([0.,1.,2.,3.,4.])*1e-15
        c,metadata=ec.prescribed_continuum_hazard(kappa,1e6)
        np.testing.assert_allclose(c,kappa*1e6,rtol=0,atol=0)
        self.assertIn("prescribed",metadata["closure"])
        with self.assertRaises(ValueError):ec.prescribed_continuum_hazard([1.,0.,0.,0.,0.],1.)
        energy=self.report["synthetic_energy"]
        self.assertFalse(energy["physical_input"])
        self.assertEqual(energy["outgoing_identity_residual_eV"],0.)
        self.assertEqual(energy["complete_identity_residual_eV"],0.)
        self.assertIsNone(self.report["heat"])
        self.assertEqual(self.report["heat_status"],"NEEDS_ENERGY_PARTITION")
        OBS.append({"name":"prescribed_density_and_synthetic_energy","continuum_hazard_s-1":c,"density_metadata":metadata,"synthetic_energy":energy})


def tearDownModule():
    report=ECTests.report
    report["validation"]={"tests_run":RESULT.testsRun if RESULT else None,"failures":len(RESULT.failures) if RESULT else None,
                          "errors":len(RESULT.errors) if RESULT else None,"wall_s":time.perf_counter()-START,
                          "observations":OBS,"raw_log":"evidence/EC_TEST_LOG.txt",
                          "thread_environment":{name:os.environ.get(name) for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS")},
                          "command":"env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 timeout 29s python -m unittest discover -s tests -p test_ec_bridge.py -v",
                          "physical_H_actions":0,"NCP_actions":0,"no_optional_test_expansion":True}
    (ROOT/"evidence/EC_RESULTS.json").write_text(json.dumps(ec.json_ready(report),indent=2)+"\n")


if __name__=="__main__":unittest.main(verbosity=2)
