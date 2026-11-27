"""Synthetic controller boundary tests; never imports numerical dependencies."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE=Path(__file__).with_name('pilot_runner.py')
spec=importlib.util.spec_from_file_location('_strip_runner_unit',SOURCE)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class FakeProcess:
    def __init__(self,code=0,delay=0):self.code=code;self.delay=delay;self.killed=False
    def poll(self):
        if self.delay:self.delay-=1;return None
        return self.code
    def kill(self):self.killed=True;self.code=-9;self.delay=0
    def wait(self,timeout=None):return self.code

class ControllerTests(unittest.TestCase):
    def test_complete_all_once_at_most_two_live(self):
        events=[];live=set();peak=[0]
        def launch(i):
            self.assertNotIn(i,events);events.append(i);live.add(i);peak[0]=max(peak[0],len(live))
            return {'process':FakeProcess(),'start':r.time.monotonic_ns(),'timed_out':False}
        def done(i,h,code):live.remove(i);return {'cell_id':i,'accepted':code==0,'status':'PASS'}
        dispatched,results=r.run_queue(r.IDS,launch,done)
        self.assertEqual(dispatched,list(r.IDS));self.assertEqual(peak[0],2);self.assertEqual(len(results),4)
    def test_observed_failure_drains_inflight_without_new_launch(self):
        launched=[]
        def launch(i):
            launched.append(i);return {'process':FakeProcess(code=2 if i==20 else 0),'start':r.time.monotonic_ns(),'timed_out':False}
        def done(i,h,code):return {'cell_id':i,'accepted':code==0,'status':'FAIL'if code else'PASS'}
        d,rs=r.run_queue(r.IDS,launch,done)
        self.assertEqual(d,[20,52]);self.assertEqual(len(rs),2);self.assertEqual(sum(x['accepted']for x in rs),1)
    def test_launch_failure_preserves_prior_inflight(self):
        def launch(i):
            if i==52:raise OSError('synthetic launch failure')
            return {'process':FakeProcess(),'start':r.time.monotonic_ns(),'timed_out':False}
        def done(i,h,code):return {'cell_id':i,'accepted':True,'status':'PASS'}
        d,rs=r.run_queue(r.IDS,launch,done)
        self.assertEqual(d,[20,52]);self.assertEqual({x['status']for x in rs},{'PASS','WORKER_LAUNCH_FAILED'})
    def test_timeout_kills_waits_and_stops_dispatch(self):
        p=FakeProcess(delay=20)
        def launch(i):return {'process':p,'start':r.time.monotonic_ns()-2*10**9,'timed_out':False}
        def done(i,h,code):return {'cell_id':i,'accepted':False,'timed_out':h['timed_out']}
        d,rs=r.run_queue(r.IDS,launch,done,concurrency=1,wall_seconds=1)
        self.assertEqual(d,[20]);self.assertTrue(p.killed);self.assertTrue(rs[0]['timed_out'])
    def test_create_only_evidence_is_not_overwritten(self):
        with tempfile.TemporaryDirectory()as t:
            p=Path(t)/'claim.json';r.write(p,{'first':True})
            with self.assertRaises(FileExistsError):r.write(p,{'first':False})
            self.assertEqual(r.read(p),{'first':True})

if __name__=='__main__':unittest.main(verbosity=2)
