import unittest,numpy as np
from inventory import *
class T(unittest.TestCase):
 def test_eos(self):
  f=np.array([1.,0.,1.]);Y=.08
  self.assertAlmostEqual(cv(f,Y)/(1.5*KB),2.24)
  self.assertAlmostEqual(binding(f,Y),CHI[0]+Y*(CHI[1]+CHI[2]))
 def test_conservation(self):
  f0=[.1,.1,0.];f1=[.2,.2,.1];Y=.08;w0=cv(f0,Y)*100.;B0=binding(f0,Y);B1=binding(f1,Y)
  Qrad=.001;Qext=B1-B0;T=(thermal_pred(w0,.1,.11)-Qrad)/cv(f1,Y)
  self.assertLess(abs(gas_residual(T,cv(f1,Y),w0,B0,B1,.1,.11,Qext,Qrad)),1e-14)
 def test_nested(self):
  e=nested_edges();f=nested_edges(cut=1e-6);np.testing.assert_array_equal(e[-len(f):],f)
 def test_fixed_composition(self):
  f=[.1,.1,0];Y=.08;C=cv(f,Y);B=binding(f,Y)
  self.assertLess(abs(gas_residual(100*(.1/.11)**2,C,100*C,B,B,.1,.11,0,0)),1e-14)
if __name__=='__main__':unittest.main()
