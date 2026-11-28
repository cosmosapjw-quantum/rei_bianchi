"""Changed runtime seam: new state artifacts and the third pinned native library."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import validate_worker_artifacts,backend_identity

class StateIdentity(unittest.TestCase):
    def test_state_artifact_identity_and_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);(folder/'DATA.json').write_bytes(b'{}');(folder/'STATE.npz').write_bytes(b'state')
            result={'code_identity_sha256':'pinned','selected_backend':{'backend':'reference'},'evidence_file':'DATA.json','evidence_bytes':2,'evidence_sha256':hashlib.sha256(b'{}').hexdigest(),'state_file':'STATE.npz','state_bytes':5,'state_sha256':hashlib.sha256(b'state').hexdigest()}
            validate_worker_artifacts(result,folder,{'sha256':'pinned'},{'backend':'reference'})
            (folder/'STATE.npz').write_bytes(b'wrong')
            with self.assertRaisesRegex(RuntimeError,'STATE_ARTIFACT'):validate_worker_artifacts(result,folder,{'sha256':'pinned'},{'backend':'reference'})
    def test_three_native_libraries_are_pinned(self):
        info=backend_identity('native');self.assertEqual(set(info['libraries']),{'prolate','inner','element'})
        for library in info['libraries'].values():self.assertEqual(hashlib.sha256(Path(library['library']).read_bytes()).hexdigest(),library['library_sha256'])

if __name__=='__main__':unittest.main()
