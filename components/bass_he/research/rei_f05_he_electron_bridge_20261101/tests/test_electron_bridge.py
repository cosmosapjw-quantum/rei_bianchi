import gzip,hashlib,importlib.util,json,math,sys,tempfile,unittest
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("electron_bridge",ROOT/"electron_bridge.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def case(h=("-0.2","-0.1"),he2=("0.3","0.4"),he3=("-0.03","-0.02")):
 r={}
 for s,(lo,hi) in (("x_HII",h),("x_HeII",he2),("x_HeIII",he3)):
  for kind in m.KINDS:
   r[f"{s}_{kind}_lower"]=lo;r[f"{s}_{kind}_upper"]=hi
 return r
class TestElectronBridge(unittest.TestCase):
 def test_y_source(self):self.assertEqual(m.Y,Q(79,1000))
 def test_h_he_e(self):
  h,he,e=m.calc(case(),m.KINDS[0])
  self.assertEqual(e[0],h[0]+he[0]);self.assertEqual(e[1],h[1]+he[1])
  self.assertLess(e[1],0);self.assertGreater(he[0],0)
 def test_helium_conservation_dual(self):
  x=case()
  b=m.calc(x,m.KINDS[0])[1]
  for i,side in enumerate(("lower","upper")):
   he2=m.endpoint(x,"x_HeII",m.KINDS[0],side)
   he3=m.endpoint(x,"x_HeIII",m.KINDS[0],side)
   hei=-(he2+he3)
   self.assertEqual(b[i],m.Y*(-hei+he3))
 def test_negative_he_source(self):
  self.assertLess(m.calc(case(he2=("-0.4","-0.3")),m.KINDS[0])[1][1],0)
 def test_inverted_source_rejected(self):
  with self.assertRaises(ValueError):m.calc(case(h=("1","0")),m.KINDS[0])
 def test_nonfinite_rejected(self):
  with self.assertRaises(ValueError):m.calc(case(h=("nan","1")),m.KINDS[0])
 def test_outward_bound(self):
  for f in (Q(1,10**19),Q(-1,3),Q(2,7)):
   self.assertLessEqual(Q.from_float(float(m.out(f,False))),f)
   self.assertGreaterEqual(Q.from_float(float(m.out(f,True))),f)
 def test_published_46080_receipt(self):
  p=ROOT/"results/REI_F05_H_HE_ELECTRON_46080.csv.gz"
  j=json.loads((ROOT/"results/RESULT.json").read_text())
  self.assertEqual(m.digest(p),j["output_sha256"])
  with gzip.open(p,"rt") as f:
   import csv
   reader=csv.DictReader(f);n=0
   for r in reader:
    self.assertEqual(int(r["node"]),n)
    for x in ("H_full","He_full","e_full","He_twohalf","e_twohalf","He_defect","e_defect"):
     self.assertLessEqual(float(r[x+"_lower"]),float(r[x+"_upper"]))
    n+=1
  self.assertEqual(n,46080)
 def test_source_missing_fails(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):m.main(Path(t),Path(t)/"out")
if __name__=="__main__":unittest.main()
