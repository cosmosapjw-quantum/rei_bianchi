"""Affected integration-output boundary; no physical evaluation."""
from pathlib import Path
import json,sys,tempfile,unittest,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import validate_worker_artifacts,read_manifest,code_identity
class Checks(unittest.TestCase):
 def test_evidence_identity_and_library_failure(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'DATA.json';p.write_bytes(b'{"value":1}\n');backend={'backend':'native','libraries':{'pin':'good'}};result={'code_identity_sha256':'pinned','evidence_file':'DATA.json','evidence_bytes':p.stat().st_size,'evidence_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'selected_backend':backend}
   validate_worker_artifacts(result,d,{'sha256':'pinned'},backend)
   with self.assertRaises(RuntimeError):validate_worker_artifacts(result,d,{'sha256':'different'},backend)
   with self.assertRaises(RuntimeError):validate_worker_artifacts(result,d,{'sha256':'pinned'},{'backend':'native','libraries':{'pin':'bad'}})
   p.write_bytes(b'{"value":2}\n')
   with self.assertRaises(RuntimeError):validate_worker_artifacts(result,d,{'sha256':'pinned'},backend)
 def test_manifest_and_contract_binding(self):
  m,_,_=read_manifest(ROOT/'inputs/MAIN_TASKS.json');self.assertEqual(len(m['tasks']),55);ids=code_identity()['files'];self.assertIn('CONTRACT.json',ids);self.assertIn('inputs/FROZEN_IDENTITY.json',ids)
 def test_duplicate_ids_fail(self):
  from mpi_batch import validate_manifest
  t={'task_id':'one','parameters':{}}
  with self.assertRaises(ValueError):validate_manifest({'schema':1,'tasks':[t,t],'limits':{'per_worker_memory_gib':1,'task_wall_seconds':1}})
if __name__=='__main__':unittest.main()
