"""Independent claim-quarantine seam checks; fixtures only, no campaign mutation."""
import copy,importlib.util,json,os,pathlib,tempfile,unittest
HERE=pathlib.Path(__file__).resolve().parent
P=HERE.parent/'tile_runner/reconcile_claims.py'
s=importlib.util.spec_from_file_location('review_claim_reconciler',P);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class ReconcileReview(unittest.TestCase):
 def test_noreplace_preserves_existing_destination_and_source(self):
  with tempfile.TemporaryDirectory() as td:
   a=pathlib.Path(td)/'source';b=pathlib.Path(td)/'archive';a.write_bytes(b'original');b.write_bytes(b'old evidence')
   with self.assertRaises(FileExistsError):c.atomic_archive(a,b)
   self.assertEqual(a.read_bytes(),b'original');self.assertEqual(b.read_bytes(),b'old evidence')
 def test_atomic_move_preserves_claim_bytes_and_mtime(self):
  with tempfile.TemporaryDirectory() as td:
   a=pathlib.Path(td)/'source';b=pathlib.Path(td)/'archive';a.write_bytes(b'123');old=a.stat().st_mtime_ns;c.atomic_archive(a,b)
   self.assertFalse(a.exists());self.assertEqual(b.read_bytes(),b'123');self.assertEqual(b.stat().st_mtime_ns,old)
 def test_symlink_claim_refused(self):
  with tempfile.TemporaryDirectory() as td:
   a=pathlib.Path(td)/'source';b=pathlib.Path(td)/'link';a.write_bytes(b'123');b.symlink_to(a)
   with self.assertRaises(ValueError):c.regular(b)
 def test_unknown_claim_and_changed_bytes_refused(self):
  o=json.loads(c.OBSERVATION.read_bytes())
  with tempfile.TemporaryDirectory() as td:
   base=pathlib.Path(td);raw=base/'runtime/W1_CAMPAIGN/raw';raw.mkdir(parents=True)
   for q in o['claims']:
    p=base/q['path'];p.write_bytes(q['data'].encode());os.utime(p,ns=(q['mtime_ns'],q['mtime_ns']))
   self.assertEqual(len(c.claim_entries(o,base,base/'quarantine')),6)
   extra=raw/'01.json.claim';extra.write_bytes(b'new unrecognized owner')
   with self.assertRaisesRegex(ValueError,'claim set'):c.claim_entries(o,base,base/'quarantine')
   extra.unlink();changed=raw/'02.json.claim';changed.write_bytes(b'999')
   with self.assertRaisesRegex(ValueError,'claim bytes'):c.claim_entries(o,base,base/'quarantine')
if __name__=='__main__':unittest.main(verbosity=2)
