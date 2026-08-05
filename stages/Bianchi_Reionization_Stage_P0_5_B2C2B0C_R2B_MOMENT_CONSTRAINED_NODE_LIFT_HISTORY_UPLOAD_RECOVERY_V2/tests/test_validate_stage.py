from __future__ import annotations
import csv,gzip,json,sys,tempfile,unittest
from pathlib import Path
import pandas as pd
SRC=Path(__file__).resolve().parents[1]/'tests'
sys.path.insert(0,str(SRC))
from validate_stage import stream_validate_node_outputs, files_identical, resolve_logical_file

class IndependentStreamValidatorTest(unittest.TestCase):


 def test_resolves_split_logical_file_with_hash_verification(self):
  import hashlib,json
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); logical=root/"large.bin"; parts=root/"large.bin.parts"; parts.mkdir()
   payload=b"abcdefghij"
   chunks=[payload[:4],payload[4:8],payload[8:]]
   entries=[]
   for i,chunk in enumerate(chunks,1):
    name=f"part-{i:04d}.bin"; (parts/name).write_bytes(chunk)
    entries.append({"name":name,"size_bytes":len(chunk),"sha256":hashlib.sha256(chunk).hexdigest()})
   (parts/"parts_manifest.json").write_text(json.dumps({"original_name":"large.bin","size_bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest(),"parts":entries}))
   work=root/"work"; work.mkdir()
   resolved=resolve_logical_file(logical,work)
   self.assertEqual(resolved.read_bytes(),payload)

 def test_file_identity_is_byte_exact(self):
  with tempfile.TemporaryDirectory() as td:
   a=Path(td)/"a"; b=Path(td)/"b"
   a.write_bytes(b"1.0000000000000000\n"); b.write_bytes(b"1.0000000000000000\n")
   self.assertTrue(files_identical(a,b))
   b.write_bytes(b"1.0\n")
   self.assertFalse(files_identical(a,b))

 def test_lockstep_stream_reconstructs_macro_and_capacity_moments(self):
  with tempfile.TemporaryDirectory() as td:
   data=Path(td)
   state_cols=['shape_lane','interval_index','substep','z_mid','macro_index','micro_index','w_micro','M_sink_H_node_cMpc3','p_mass_conditional','xHII_prior','xHII_lift','T_prior_K','T_lift_K','nH_node_cm3','cycling_capacity_node_s_inv_cMpc3','mass_transfer_positive_H_s_inv_cMpc3','mass_transfer_negative_H_s_inv_cMpc3','mass_transfer_net_H_s_inv_cMpc3']
   group_cols=['shape_lane','interval_index','substep','z_mid','macro_index','micro_index','group','q_prior_conditional','J_sink_node_s_inv_cMpc3','kappa_sink_node_cMpc_inv','Phi_current_Gamma_s_inv_cMpc2','capacity_slack_after_all_groups_s_inv_cMpc3']
   state_rows=[
    ['L',0,1,5.95,0,0,.4,4,.4,.1,.25,100,150,1,7,1,0,1],
    ['L',0,1,5.95,0,1,.6,6,.6,.2,.75,200,250,2,8,2,0,2],
   ]
   group_rows=[
    ['L',0,1,5.95,0,0,'G1',.5,3,1,3,2],
    ['L',0,1,5.95,0,0,'G2a',.5,2,1,2,2],
    ['L',0,1,5.95,0,1,'G1',.5,3,1,3,3],
    ['L',0,1,5.95,0,1,'G2a',.5,2,1,2,3],
   ]
   with gzip.open(data/'node_state_lift.csv.gz','wt',newline='') as f:
    w=csv.writer(f);w.writerow(state_cols);w.writerows(state_rows)
   with gzip.open(data/'node_group_lift.csv.gz','wt',newline='') as f:
    w=csv.writer(f);w.writerow(group_cols);w.writerows(group_rows)
   out=stream_validate_node_outputs(data/'node_state_lift.csv.gz',data/'node_group_lift.csv.gz')
   self.assertEqual(out['state_rows'],2)
   self.assertEqual(out['group_rows'],4)
   self.assertEqual(out['macro_count'],1)
   m=next(iter(out['macro'].values()))
   self.assertAlmostEqual(m['mass'],10)
   self.assertAlmostEqual(m['mass_x'],5.5)
   self.assertAlmostEqual(m['mass_T'],2100)
   self.assertAlmostEqual(m['capacity'],15)
   self.assertAlmostEqual(m['transfer'],3)
   self.assertAlmostEqual(m['J_G1'],6)
   self.assertAlmostEqual(m['J_G2a'],4)
   self.assertAlmostEqual(m['kappa_G1'],2)
   self.assertAlmostEqual(m['kappa_G2a'],2)
   self.assertLess(out['max_capacity_relative_violation'],1e-15)
   self.assertLess(out['max_current_gamma_relative_residual'],1e-15)

if __name__=='__main__': unittest.main()
