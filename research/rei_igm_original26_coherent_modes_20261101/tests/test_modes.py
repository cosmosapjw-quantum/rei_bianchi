import importlib.util,sys,unittest,tempfile
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[1]/"science.py"
spec=importlib.util.spec_from_file_location("rei_source_physical_modes",P)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class PhysicalModes(unittest.TestCase):
    def setUp(self):
        self.p=np.array([[.6,.4,.2,.3,.5],[.5,.5,.15,.35,.5]])
        self.lo=self.p-.01;self.hi=self.p+.01
        self.x=np.log([10000.,7000.]);self.xlo=self.x-.001;self.xhi=self.x+.001
        self.nh=self.p[:,:2].sum(axis=1);self.nhe=self.p[:,2:].sum(axis=1)
    def test_mode_names(self):self.assertEqual(set(m.modes(self.p,self.lo,self.hi,self.x,self.xlo,self.xhi)),set(m.MODES))
    def test_nuclear_inventory(self):
        for v,w,a in m.modes(self.p,self.lo,self.hi,self.x,self.xlo,self.xhi).values():
            self.assertTrue(np.all(a>=0))
            self.assertLess(np.max(abs(v[:,:2].sum(axis=1))),1e-15)
            self.assertLess(np.max(abs(v[:,2:].sum(axis=1))),1e-15)
    def test_all_curve_points_inside(self):
        for v,w,a in m.modes(self.p,self.lo,self.hi,self.x,self.xlo,self.xhi).values():
            for k in (-1.,-.3,0.,.4,1.):
                self.assertTrue(m.validate_point(self.p+k*v,self.x+k*w,self.p,self.x,self.lo,self.hi,self.xlo,self.xhi,self.nh,self.nhe))
    def test_invalid_inventory(self):
        p=self.p.copy();p[0,1]+=.5
        with self.assertRaises(ValueError):m.validate_point(p,self.x,self.p,self.x,self.lo,self.hi,self.xlo,self.xhi,self.nh,self.nhe)
    def test_nonfinite(self):
        p=self.p.copy();p[0,0]=float("nan")
        with self.assertRaises(ValueError):m.validate_point(p,self.x,self.p,self.x,self.lo,self.hi,self.xlo,self.xhi,self.nh,self.nhe)
    def test_original_gate(self):self.assertEqual(m.GATE,0.0002)
    def test_serial_zip_identity(self):
        with tempfile.TemporaryDirectory() as f:
            q=Path(f);records=[(1,"A",2),(2,"B",3)]
            self.assertEqual(m.write_gzip(q/"a.gz",["i","m","v"],records),m.write_gzip(q/"b.gz",["i","m","v"],records))
    def test_zero_margin(self):
        self.lo[0,0]=self.p[0,0]
        v,w,a=m.modes(self.p,self.lo,self.hi,self.x,self.xlo,self.xhi)["H_ION"]
        self.assertEqual(a[0],0.)
    def test_frozen_parent(self):self.assertIn("rei_igm_original26_commonparent_20261101",str(m.PARENT))
    def test_scope(self):self.assertEqual((m.CENTRAL,m.WORKING,m.FAST),("28/88","33/88","4/7"))
if __name__=="__main__":unittest.main(verbosity=2)
