#!/usr/bin/env python3
"""Minimal tests of original parent composition/energy path, not full all-X certificate."""
import importlib.util,sys,unittest,numpy as np
from pathlib import Path
here=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('material_parent_for_test',here/'material_parent_probe.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def state(self):
        n=7;H=np.ones(n);He=np.full(n,.079)
        p=np.zeros((n,5))
        p[:,1]=.80;p[:,0]=.20;p[:,3]=.055;p[:,4]=.011;p[:,2]=.013
        radius=np.zeros_like(p)
        radius[:,1]=.0002;radius[:,0]=.0002
        radius[:,2]=.00003;radius[:,3]=.00002;radius[:,4]=.00001
        return p-radius,p+radius,np.full(n,np.log(1e4)-.0002),np.full(n,np.log(1e4)+.0002),H,He
    def test_exact_material(self):
        lo,hi,l,h,H,He=self.state()
        samples,receipt=m.correlated_points(lo,hi,l,h,H,He)
        self.assertEqual(set(samples),{'CHEM_MINUS','CHEM_PLUS'})
        self.assertLess(receipt['material_relative_error_max'],4e-15)
        for x,lt in samples.values():
            self.assertTrue(np.all(x>=lo-1e-14))
            self.assertTrue(np.all(x<=hi+1e-14))
            self.assertTrue(np.all(np.exp(lt)>=np.exp(l)*(1-1e-14)))
            self.assertTrue(np.all(np.exp(lt)<=np.exp(h)*(1+1e-14)))
            self.assertLess(float(np.max(abs(x[:,0]+x[:,1]-H))),1e-14)
            self.assertLess(float(np.max(abs(np.sum(x[:,2:5],axis=1)-He))),1e-14)
    def test_direction(self):
        lo,hi,l,h,H,He=self.state()
        s,_=m.correlated_points(lo,hi,l,h,H,He)
        self.assertTrue(np.all(s['CHEM_PLUS'][0][:,1]>s['CHEM_MINUS'][0][:,1]))
        self.assertTrue(np.all(s['CHEM_PLUS'][1]<s['CHEM_MINUS'][1]))
    def test_original_gate_not_promoted(self):
        self.assertEqual(m.GATE,2e-4)
        self.assertEqual(m.EXPECTED_SOURCE_BODY_SHA,'cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01')
    def test_wrong_shape_fails(self):
        lo,hi,l,h,H,He=self.state()
        with self.assertRaisesRegex(ValueError,'shape'):m.correlated_points(lo[:,:4],hi[:,:4],l,h,H,He)
    def test_failed_helium_conservation(self):
        lo,hi,l,h,H,He=self.state()
        with self.assertRaises(ValueError):m.correlated_points(lo,hi,l,h,H,He*.4)
if __name__=='__main__':unittest.main()
