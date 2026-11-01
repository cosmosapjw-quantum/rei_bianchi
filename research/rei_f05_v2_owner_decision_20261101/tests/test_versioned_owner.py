from __future__ import annotations
import importlib.util
import csv
import gzip
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import sys
import json

import numpy as np

SOURCE=Path(__file__).resolve().parents[1]/"versioned_owner.py"
sp=importlib.util.spec_from_file_location("rei_f05_v2_scoped_owner",SOURCE)
v=importlib.util.module_from_spec(sp)
sys.modules[sp.name]=v
sp.loader.exec_module(v)
KEYS={
"H_nuclei","He_nuclei",
"stage_photon_identity","stage_total_energy",
"final_photon_identity","final_total_energy",
*(f"{phase}_group_{j}_photon" for phase in ("stage","final") for j in range(4))
}

def fake():
    duration=100000.
    t0=duration*(160/131072)
    t1=duration*(161/131072)
    mid=t0+.5*(t1-t0)
    return {"lane":v.LANES[0],"source_sha256":v.SOURCE,
       "state_array_sha256":v.STATE,"kernel_sha256":v.KERNEL,
       "original_lock_sha256":v.LOCK,"original_policy_sha256":v.POLICY,
       "original_accepted_tick":"160/131072",
       "shadow_v2_candidate_tick":"161/131072_NOT_OFFICIAL",
       "original_worker_modified":False,"official_tick161_accepted":False,
       "original_legacy_worker_gate":"FAIL_HISTORICAL_UNCHANGED",
       "original_policy_v2_post_map_validation":"PASS_SHADOW_ONLY",
       "original_14_ledger_pass":True,
       "original_table_event":{"any_event":False},
       "native_step_receipts":{"full":{},"half1":{},"half2":{}},
       "old_independent_endpoint_local_upper":
          {"x_HII":1e-6,"x_HeII":1e-6,"x_HeIII":1e-6,"log_T":2.1245e-4},
       "new_original_common_parent_local_upper":
          {k:5e-6 for k in v.FIELDS},
       "original_public_widths":{k:2e-4 for k in v.FIELDS},
       "original_native_raw_14_ledgers":{k:[-1.,1.] for k in KEYS},
       "clock_hex":{"t0":t0.hex(),"tm":mid.hex(),"t1":t1.hex(),
                    "duration":duration.hex()}}

class TestVersionedOwner(unittest.TestCase):
    def test_locked_true_shadow(self):
        v.version_gate(fake(),v.LANES[0],KEYS)
    def test_reject_mutated_historical_v1(self):
        r=fake()
        r["old_independent_endpoint_local_upper"]["log_T"]=1e-6
        with self.assertRaisesRegex(ValueError,"historical"):
            v.version_gate(r,v.LANES[0],KEYS)
    def test_reject_source_clock_and_ledger(self):
        for key in ("clock","ledger","source"):
            r=fake()
            if key=="clock":r["clock_hex"]["tm"]=float(999).hex()
            if key=="ledger":r["original_native_raw_14_ledgers"]["final_total_energy"]=[1.,2.]
            if key=="source":r["source_sha256"]="0"*64
            with self.subTest(key=key),self.assertRaises(ValueError):
                v.version_gate(r,v.LANES[0],KEYS)
    def test_zero_decision_not_official(self):
        r=fake();r["official_tick161_accepted"]=True
        with self.assertRaisesRegex(ValueError,"illicit_admission"):
            v.version_gate(r,v.LANES[0],KEYS)
    def test_electron_physics_and_no_tau(self):
        a=np.zeros((v.N,5),dtype=np.float64)
        a[:,0]=3.;a[:,1]=2.;a[:,2]=1.;a[:,3]=1.;a[:,4]=0.
        b=a.copy();b[:,0]=4.;b[:,1]=1.;b[:,2]=1.;b[:,3]=.5;b[:,4]=.5
        x={"source_parent_population_lower":a,"source_parent_population_upper":a,
           "population_lower":b,"population_upper":b}
        z=v.electron_science(x)
        self.assertEqual(z["delta_Ne_negative_cells"],v.N)
        self.assertEqual(z["delta_Ne_positive_cells"],0)
        self.assertEqual(z["delta_Ne_uncertain_cells"],0)
        self.assertAlmostEqual(z["delta_Ne_global_float64_interval"][0],-.5*v.N)
        self.assertIn("not_tau",z["physics"])
    def test_npz_accepted_parent_array_tampering(self):
        lo=np.ones((v.N,5));hi=lo+1e-8
        tlo=np.ones(v.N);thi=tlo+1e-8
        dec=SimpleNamespace(population_lower=lo,population_upper=hi,
              log_temperature_lower=tlo,log_temperature_upper=thi)
        arr={"population_lower":lo,"population_upper":hi,
             "log_temperature_lower":tlo,"log_temperature_upper":thi,
             "source_parent_population_lower":lo.copy(),
             "source_parent_population_upper":hi.copy(),
             "source_parent_logT_lower":tlo.copy(),
             "source_parent_logT_upper":thi.copy()}
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"state.npz"
            np.savez_compressed(p,**arr)
            v.read_candidate(p,{"candidate_state_sha256":v.digest(p)},dec)
            arr["source_parent_population_lower"][0,1]+=1e-9
            np.savez_compressed(p,**arr)
            with self.assertRaisesRegex(ValueError,"parent_array_parity"):
                v.read_candidate(p,{"candidate_state_sha256":v.digest(p)},dec)

    def test_correlated_increment_physically_signed(self):
        labels=[f"x_{s}_original_twohalf_increment_{b}"
                for s in ("HII","HeII","HeIII") for b in ("lower","upper")]
        names=["node"]+labels+[f"unused_{i}" for i in range(23)]
        self.assertEqual(len(names),30)
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"increment.csv.gz"
            with gzip.open(path,"wt",newline="") as f:
                w=csv.DictWriter(f,fieldnames=names)
                w.writeheader()
                for i in range(10):
                    r=dict.fromkeys(names,0)
                    r["node"]=i
                    for b in ("lower","upper"):
                        r[f"x_HII_original_twohalf_increment_{b}"]=-.1
                        r[f"x_HeII_original_twohalf_increment_{b}"]=.02
                        r[f"x_HeIII_original_twohalf_increment_{b}"]=0.
                    w.writerow(r)
            with patch.object(v,"N",10),patch.object(v,"INCREMENT_SHA",v.digest(path)):
                r=v.correlated_electron_science(path,np.full(10,10.0),np.full(10,2.0))
            self.assertEqual(r["negative_cells"],10)
            self.assertEqual(r["positive_cells"],0)
            self.assertAlmostEqual(r["global_delta_Ne_conditional_float64_interval"][0],-9.6,places=10)
            self.assertAlmostEqual(r["global_delta_Ne_conditional_float64_interval"][1],-9.6,places=10)

if __name__=="__main__":
    unittest.main()
