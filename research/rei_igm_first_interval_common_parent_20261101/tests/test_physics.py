import hashlib,io,json,struct,sys,tarfile,tempfile,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
import paired_defect as p, physical_probe as f

class PhysicsTests(unittest.TestCase):
 def test_positive_H_chemistry(self):
  for x in (0.,.1,.6,1.):
   for h in (0.,1e8,1e10,1e11):
    y=p.backward_euler(x,1e-12,2e-13,h)
    self.assertTrue(0.<=y<=1.)
 def test_common_parent_exact(self):
  for x in (0.,.2,.5,.833333333333,1.):
   h=1e10
   a=p.backward_euler(x,1e-12,2e-13,h)
   b=p.backward_euler(p.backward_euler(x,1e-12,2e-13,h/2),1e-12,2e-13,h/2)
   self.assertAlmostEqual(a-b,p.same_parent_defect(x,1e-12,2e-13,h),delta=1e-15)
 def test_limit_zero(self):
  self.assertEqual(p.same_parent_defect(.5,0.,0.,1e10),0.)
  self.assertEqual(p.same_parent_defect(.5,1e-12,1e-13,0.),0.)
 def test_independent_gap_false_floor(self):
  a=p.compare_box(.2,.8,1e-12,2e-13,1e9)
  self.assertGreater(a.independent_box_gap,.5)
  self.assertLess(a.common_parent_gap,1e-5)
 def test_second_order_scaling(self):
  a=p.compare_box(.2,.8,1e-12,2e-13,1e10)
  b=p.compare_box(.2,.8,1e-12,2e-13,5e9)
  self.assertTrue(3.7<a.common_parent_gap/b.common_parent_gap<4.2)
 def test_authentic_failure_not_promoted(self):
  self.assertEqual(p.ACCEPTED_TICK,160)
  self.assertLess(p.ACCEPTED_TICK,p.TOTAL_TICKS)
  self.assertGreater(p.ORIGINAL_OBSERVED[1],p.LIMIT)
 def test_source_state_layout(self):
  n=f.N
  a=np.ones((n,5),dtype="<f8");a[:,1]=2;a[:,3]=3;a[:,4]=4
  logt=np.full(n,np.log(1e4),dtype="<f8")
  header=dict(population_shape=[n,5],log_temperature_shape=[n],
    array_order=["population_lower","population_upper","log_temperature_lower","log_temperature_upper"],metadata={"accepted_tick":160})
  b=json.dumps(header).encode("ascii")
  raw=f.MAGIC+struct.pack("<Q",len(b))+b+a.tobytes()*2+logt.tobytes()*2
  result=f.inspect_state(raw,"accepted.bin")
  self.assertEqual(result["nodes"],n)
  self.assertAlmostEqual(result["x_HII"]["min"],2/3)
  self.assertAlmostEqual(result["x_HeIII"]["max"],4/8)
  self.assertAlmostEqual(result["T_K"]["max"],1e4)
  self.assertGreater(result["U_thermal_erg_per_H"]["max"],0)
 def test_source_state_invalid(self):
  self.assertIsNone(f.inspect_state(b"not-a-state","test.bin"))
if __name__=="__main__":unittest.main()
