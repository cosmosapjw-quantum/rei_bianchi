import tempfile,unittest
from pathlib import Path
import numpy as np
from helpers import load
m=load('test_state_io_module','analysis/state_io.py')
class Tests(unittest.TestCase):
 def sample(self):
  lo=np.arange(15,dtype=float).reshape(3,5)+1;hi=np.nextafter(lo,np.inf);tl=np.log([1e4,1.2e4,1.4e4]);th=np.nextafter(tl,np.inf)
  return {'accepted_index':7,'endpoint_tick':448,'lane':'LOCAL_NEUTRAL_HAZARD_PRIMARY','parent_state_sha256':'0'*64},lo,hi,tl,th
 def test_deterministic_roundtrip(self):
  a=self.sample();self.assertEqual(m.encode_state(*a),m.encode_state(*a));d=m.decode_state(m.encode_state(*a));self.assertEqual(d.metadata,a[0]);np.testing.assert_array_equal(d.population_lower,a[1])
 def test_hash_corruption(self):
  with tempfile.TemporaryDirectory() as r:
   p=Path(r)/'s';h=m.write_state(p,*self.sample());m.read_state(p,expected_sha256=h);x=bytearray(p.read_bytes());x[-1]^=1;p.write_bytes(x)
   with self.assertRaisesRegex(ValueError,'SHA-256'):m.read_state(p,expected_sha256=h)
 def test_invalid_boxes_and_format(self):
  a=list(self.sample());a[2][0,0]=np.nan
  with self.assertRaises(ValueError):m.encode_state(*a)
  payload=m.encode_state(*self.sample())
  with self.assertRaises(ValueError):m.decode_state(payload+b'x')
if __name__=='__main__':unittest.main()
