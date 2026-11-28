"""Synthetic claim mismatch and atomic archive tests; no real claim mutation."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('tested_claim_reconciler',Path(__file__).with_name('reconcile_claims.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class ClaimTests(unittest.TestCase):
    def make(self,base):
        raw=base/'runtime/W1_CAMPAIGN/raw';raw.mkdir(parents=True)
        claims=[]
        for i in r.TILES:
            p=raw/('%02d.json.claim'%i);data=str(i).encode();p.write_bytes(data)
            claims.append({'path':str(p.relative_to(base)),'data':data.decode(),'sha256':r.sha(data),'mtime_ns':p.stat().st_mtime_ns})
        return {'claims':claims}
    def test_exact_six_preserved_in_plan(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);o=self.make(base);records=r.claim_entries(o,base,base/'quarantine')
            self.assertEqual([v['tile_id'] for v in records],list(r.TILES))
            self.assertEqual(len(list((base/'runtime/W1_CAMPAIGN/raw').glob('*.claim'))),6)
    def test_changed_bytes_refused(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);o=self.make(base);(base/o['claims'][0]['path']).write_text('changed')
            with self.assertRaisesRegex(ValueError,'bytes differ'):r.claim_entries(o,base,base/'q')
    def test_resealed_unknown_claim_refused(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);o=self.make(base);(base/'runtime/W1_CAMPAIGN/raw/03.json.claim').write_text('unresolved')
            with self.assertRaisesRegex(ValueError,'unknown'):r.claim_entries(o,base,base/'q')
    def test_observation_path_and_digest_tamper_refused(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);o=self.make(base)
            for key,value in [('path','../escape'),('sha256','0'*64),('mtime_ns',0)]:
                bad=copy.deepcopy(o);bad['claims'][0][key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):r.claim_entries(bad,base,base/'q')
    def test_claim_symlink_refused(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);o=self.make(base);p=base/o['claims'][0]['path'];data=p.read_bytes();p.unlink();target=base/'data';target.write_bytes(data);p.symlink_to(target)
            with self.assertRaisesRegex(ValueError,'nonsymlink'):r.claim_entries(o,base,base/'q')
    def test_atomic_move_preserves_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);source=base/'source';destination=base/'dest';source.write_bytes(b'original');destination.write_bytes(b'preserve')
            with self.assertRaises(FileExistsError):r.atomic_archive(source,destination)
            self.assertEqual(source.read_bytes(),b'original');self.assertEqual(destination.read_bytes(),b'preserve')
            target=base/'new';r.atomic_archive(source,target);self.assertFalse(source.exists());self.assertEqual(target.read_bytes(),b'original')

if __name__=='__main__':unittest.main(verbosity=2)
