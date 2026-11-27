import unittest,json,hashlib,subprocess
from pathlib import Path
O=Path(__file__).parent
class PacketTests(unittest.TestCase):
 def test_authority(self):
  x=json.loads((O/'AUTHORIZATION_AUDIT.json').read_text());self.assertIsNone(x['authorization_record']);self.assertEqual(x['dispatch_count'],0);self.assertTrue(x['old_registry_unchanged']);self.assertEqual(x['field_calls'],0)
 def test_budget_unchanged(self):
  a=json.loads((O/'original_TWO_CELL_NEW_SCOPE_PROPOSAL.json').read_text());b=json.loads((O/'TWO_CELL_NEW_SCOPE_PROPOSAL_V2.json').read_text())
  for key in ['cell_inputs','field_scope','unchanged_numeric_contract','proposed_budget']:self.assertEqual(a[key],b[key])
 def test_no_proof_inference(self):
  x=json.loads((O/'FULL_BOX_FEASIBILITY.json').read_text());self.assertFalse(x['whole_physical_boxes_inclusion']);self.assertFalse(x['sign_rank_admission']);self.assertEqual(x['coverage']['unbounded'],265)
 def test_real_binding_open(self):
  x=json.loads((O/'CGROUP_BINDING.json').read_text());self.assertEqual(x['status'],'OPEN');self.assertIsNone(x['live_science_binding'])
 def test_scalar_identity(self):
  p=O/'source/gap_closure_20261001_g0_g6_v1/validated_callback/finite_m.hpp';self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'7b06ed12be2afd191831676ed2f3eae4198ae39805434c09fac59b1581f34282')
 def test_sources_preserved(self):
  for r in json.loads((O/'SOURCE_BINDING.json').read_text())['inputs']:self.assertEqual(hashlib.sha256(Path(r['path']).read_bytes()).hexdigest(),r['sha256'])
 def test_identity_no_science(self):
  p=subprocess.run([str(O/'c1_candidate_integration_worker'),'--identity'],capture_output=True);self.assertEqual(p.returncode,0);self.assertIn(b'FLINT=3.4.0 GMP=6.3.0 MPFR=4.2.2',p.stdout)
 def test_dispatch_blocked(self):
  for args in [[],['--integrate'],['0','128'],['--identity','extra']]:
   p=subprocess.run([str(O/'c1_candidate_integration_worker'),*args],capture_output=True);self.assertEqual(p.returncode,77);self.assertIn(b'C1_DISPATCH_BLOCKED',p.stderr)
if __name__=='__main__':unittest.main()
