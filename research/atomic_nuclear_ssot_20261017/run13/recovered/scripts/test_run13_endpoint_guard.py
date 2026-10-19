"""Filesystem contract tests; manufactured receipts, no mocked integrator claims."""
import copy, hashlib, json, pathlib, tempfile, unittest
import numpy as np
from run13_endpoint_guard import load_complete,load_sealed_parent
class EndpointGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name)
        self.inputs=self.root/'inputs/spectral11';self.inputs.mkdir(parents=True)
        self.out=self.root/'evidence/joint11_sided_m2_3e-11';self.out.mkdir(parents=True)
        self.packet={'cohorts':[[0.25]*9,[0.25]*9]};self.p=self.inputs/'m2.json';self.p.write_text(json.dumps(self.packet))
        self.sha=hashlib.sha256(self.p.read_bytes()).hexdigest()
        self.events={'packet_sha256':self.sha,'points':[0.,.5,1.],'dimension':38}
        (self.inputs/'m2_events.json').write_text(json.dumps(self.events))
        self.y=np.zeros(38);self.y[1]=1.;self.y[13]=2.
        np.savez_compressed(self.out/'checkpoint_2.npz',state=self.y);np.savez_compressed(self.out/'endpoint.npz',state=self.y)
        self.record={'packet_sha256':self.sha,'rtol':3e-11,'status':'COMPLETE','next_segment':2,'segments':[[0.,.5,0,2,2],[.5,1.,1,2,2]],'state_file':'checkpoint_2.npz','state_sha256':hashlib.sha256((self.out/'checkpoint_2.npz').read_bytes()).hexdigest(),'dimension':38,'physical_cohorts':2,'observable':{'T_K':10000.}}
        self.save()
    def save(self):
        (self.out/'checkpoint.json').write_text(json.dumps(self.record));(self.out/'result.json').write_text(json.dumps(self.record))
    def test_complete_endpoint_is_accepted(self):
        result,state=load_complete(self.root,2,3e-11);self.assertEqual(result['status'],'COMPLETE');np.testing.assert_array_equal(state,self.y)
    def test_in_progress_cannot_become_endpoint(self):
        self.record['status']='IN_PROGRESS';self.save()
        with self.assertRaisesRegex(ValueError,'incomplete'):load_complete(self.root,2,3e-11)
    def test_final_segment_must_exist(self):
        self.record['next_segment']=1;self.record['segments']=self.record['segments'][:1];self.save()
        with self.assertRaisesRegex(ValueError,'incomplete'):load_complete(self.root,2,3e-11)
    def test_packet_mismatch_rejected(self):
        self.record['packet_sha256']='0'*64;self.save()
        with self.assertRaisesRegex(ValueError,'packet'):load_complete(self.root,2,3e-11)
    def test_state_corruption_rejected(self):
        with (self.out/'checkpoint_2.npz').open('ab') as f:f.write(b'changed')
        with self.assertRaisesRegex(ValueError,'state hash'):load_complete(self.root,2,3e-11)
    def test_endpoint_not_latest_state_rejected(self):
        other=self.y.copy();other[13]+=1;np.savez_compressed(self.out/'endpoint.npz',state=other)
        with self.assertRaisesRegex(ValueError,'endpoint'):load_complete(self.root,2,3e-11)
    def test_event_gap_rejected(self):
        self.record['segments'][1][0]=.6;self.save()
        with self.assertRaisesRegex(ValueError,'event'):load_complete(self.root,2,3e-11)
    def seal(self):
        manifest=self.root/'SEALED.sha256'
        paths=[self.out/'result.json',self.out/'endpoint.npz',self.p,self.inputs/'m2_events.json']
        manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(self.root).as_posix()+'\n' for p in paths))
        return manifest
    def test_sealed_parent_does_not_require_restart_metadata(self):
        manifest=self.seal();(self.out/'checkpoint.json').unlink()
        result,state=load_sealed_parent(self.root,2,3e-11,manifest)
        np.testing.assert_array_equal(state,self.y);self.assertEqual(result['status'],'COMPLETE')
    def test_sealed_parent_corruption_rejected(self):
        manifest=self.seal()
        with (self.out/'endpoint.npz').open('ab') as f:f.write(b'changed')
        with self.assertRaisesRegex(ValueError,'hash'):load_sealed_parent(self.root,2,3e-11,manifest)
    def test_seal_does_not_certify_incomplete_science(self):
        self.record['status']='IN_PROGRESS';self.save();manifest=self.seal()
        with self.assertRaisesRegex(ValueError,'incomplete'):load_sealed_parent(self.root,2,3e-11,manifest)
if __name__=='__main__':unittest.main()
