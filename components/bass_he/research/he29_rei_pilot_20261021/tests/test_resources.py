import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import shared_runner as r

class ResourceTests(unittest.TestCase):
    def snap(self, quota=None, available=16*r.GIB):
        return dict(affinity_cpu_ids=list(range(8))+[55], cpu_quota=quota,
                    memory_limit_bytes=16*r.GIB, memory_available_bytes=available,
                    cpu_busy={c:0. for c in list(range(8))+[55]})
    def test_quota_and_cpu55(self):
        cap=r.capacity(self.snap(quota=3.9),28)
        self.assertEqual(cap['new_workers'],2)
        self.assertNotIn(55,cap['cpu_ids'])
    def test_memory_limit(self):
        self.assertEqual(r.capacity(self.snap(available=2*r.GIB),28)['new_workers'],0)
    def test_pending_not_inflated(self):
        self.assertEqual(r.capacity(self.snap(),1)['new_workers'],1)
    def test_busy_unregistered_observed(self):
        s=self.snap(); s['cpu_busy']={c:1. for c in s['affinity_cpu_ids']}
        self.assertEqual(r.capacity(s,28)['new_workers'],0)
    def test_reserve_contract(self):
        for total, expected in ((128*r.GIB,16*r.GIB),(8*r.GIB,4*r.GIB)):
            snapshot=self.snap(available=total)
            snapshot["memory_limit_bytes"]=total
            self.assertEqual(r.capacity(snapshot,28)["memory_reserve_bytes"],expected)

    def test_occupied_lease_others_free(self):
        with tempfile.TemporaryDirectory() as d:
            lock=r.acquire_cpu(d,0)
            cpu, other=r.select_cpu(d,[0,1,55])
            self.assertEqual(cpu,1)
            lock.close(); other.close()
    def test_completed_exact_identity_validation(self):
        import pilot
        with patch.object(pilot,'completed_result',return_value=True) as check:
            self.assertTrue(r.reusable({'case_id':'exact'},Path('/tmp/example')))
            check.assert_called_once_with({'case_id':'exact'},Path('/tmp/example'))
        with patch.object(pilot,'completed_result',return_value=False):
            self.assertFalse(r.reusable({'case_id':'changed'},Path('/tmp/example')))

if __name__=='__main__': unittest.main()
