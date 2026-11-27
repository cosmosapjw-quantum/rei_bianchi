import unittest,tempfile,json,os
from pathlib import Path
from unittest.mock import patch
from resources import LeasePool,slots,GIB
class ResourcesTests(unittest.TestCase):
 def test_busy_peers_reduce_not_forbid(self):
  self.assertEqual(slots(64,20,100,125,16,1,12,12),44)
 def test_memory_and_quota_bound(self):
  self.assertEqual(slots(64,0,19,125,16,2,0,0),1)
  self.assertEqual(slots(8,2,100,125,16,1,7,7),1)
  self.assertEqual(slots(64,64,100,125,16,1,0,0),0)
 def test_small_session_shares_larger_allocation(self):
  with tempfile.TemporaryDirectory() as d,patch('resources.cpu_limit',return_value=8),patch('resources.busy_cores',return_value=3),patch('resources.os.sched_getaffinity',return_value=set(range(8))),patch('resources.memory_available',return_value=(20*GIB,20*GIB)):
   a=LeasePool(d,max_cpus=2,memory_gib=20,reserve_gib=1)
   key,_=a.acquire('small-concurrent-session');self.assertIsNotNone(key);a.release(key)
 def test_live_lease_not_overwritten(self):
  with tempfile.TemporaryDirectory() as d,patch('resources.cpu_limit',return_value=2),patch('resources.busy_cores',return_value=0),patch('resources.memory_available',return_value=(8*GIB,8*GIB)):
   a=LeasePool(d,max_cpus=2,memory_gib=8,reserve_gib=1);b=LeasePool(d,max_cpus=2,memory_gib=8,reserve_gib=1)
   k,_=a.acquire('case-a');h,_=b.acquire('case-b');self.assertIsNotNone(k);self.assertIsNotNone(h)
   q,_=b.acquire('case-c');self.assertIsNone(q)
   with self.assertRaises(RuntimeError):b.release(k)
   a.release(k);q,_=b.acquire('case-c');self.assertIsNotNone(q)
   b.release(h);b.release(q);self.assertFalse(list(Path(d).glob('lease-*.json')))
if __name__=='__main__':unittest.main()
