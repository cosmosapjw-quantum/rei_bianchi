import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import unittest,json,copy,subprocess,numpy as np
from retarded_integrator import *
class RetardedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packet=json.loads((ROOT/'inputs/FINITE_BIRTH_PACKET.json').read_text())
 def reduced(self):
  f=copy.deepcopy(self.packet);f['cohorts']=f['cohorts'][:8];return RetardedModel(f)
 def test_exact_reflection_support(self):
  f=coalesce_reflections(self.packet);self.assertEqual(len(f['cohorts'])*2,len(self.packet['cohorts']))
  m=RetardedModel(self.packet);r=RetardedModel(f);self.assertAlmostEqual(m.B.sum(),r.B.sum(),places=17)
  for z in [.2,.7,1.]:
   ef=m.rays(z,m.m)[0];er=r.rays(z,r.m)[0]
   for j,(a,b) in enumerate(f['reflection_mapping']):self.assertEqual(ef[a],ef[b]);self.assertEqual(ef[a],er[j])
 def test_missing_pair_rejected(self):
  f=copy.deepcopy(self.packet);f['cohorts']=f['cohorts'][:-1]
  with self.assertRaises(ValueError):coalesce_reflections(f)
 def test_adiabatic_and_dark_limit(self):
  m=self.reduced()
  with GasServer() as srv:
   m.server=srv;y=m.y0.copy();d=m.raw_rhs(0.4,y,0,'photo');self.assertTrue(np.all(d==0))
  self.assertEqual(len(m.events()[0]),3)
 def test_all_four_threshold_guards(self):
  m=self.reduced();edges=np.maximum(m.chi,[13.6,24.59,54.42,13.6])
  for j,e in enumerate(edges):
   s=sigma_native_formula([np.nextafter(e,0),np.nextafter(e,np.inf)],m.chi)
   self.assertEqual(s[0,j],0);self.assertGreater(s[1,j],0)
 def test_interior_threshold_birth_restart(self):
  f=copy.deepcopy(self.packet);f['cohorts']=f['cohorts'][:2]
  for row in f['cohorts']:row[4]=13.604
  m=RetardedModel(f);events,count=m.events();self.assertEqual(count,4)
  self.assertGreater(len(events),3)
  for j in range(2):
   self.assertGreater(m.rays(m.birth[j],2)[0][j],m.chi[3]);self.assertLess(m.rays(1.,2)[0][j],13.6)
 def test_analytic_jacobian_directional_check(self):
  m=self.reduced();y=m.y0.copy();y[27:m.p]=.7;v=np.zeros(m.dim);v[[1,2,3,4,10,11,12,13]]=[.01,-.01,2e-6,-2e-6,.005,-.003,-.002,.01];v[27:m.p]=np.linspace(-.1,.2,m.m)
  with GasServer() as srv:
   m.server=srv;j=analytic_jacobian(m,.5,y,m.m);eps=1e-4
   fd=(m.raw_rhs(.5,y+eps*v,m.m)-m.raw_rhs(.5,y-eps*v,m.m))/(2*eps)
  err=max(abs(j@v-fd));self.assertLess(err,2e-7*max(abs(fd)))
 def test_physical_energy_rhs_identity(self):
  m=self.reduced();y=m.y0.copy();y[27:m.p]=.1
  with GasServer() as srv:
   m.server=srv;q=m.raw_rhs(.4,y,m.m)
  e,de,_,_=m.rays(.4,m.m);P=m.B*np.exp(-y[27:m.p]);res=q[13]+q[14]+q[15]+q[:13]@m.bind+sum(q[m.p+8:m.p+10])+np.dot(P,m.dx*de-e*q[27:m.p])
  self.assertLess(abs(res),2e-13*(abs(q[13])+sum(abs(q[m.p+8:m.p+10]))))
 def test_source_no_renormalization(self):
  full=RetardedModel(self.packet);small=self.reduced();self.assertLess(small.B.sum(),full.B.sum());self.assertEqual(small.B[0],full.B[0])
if __name__=='__main__':unittest.main(verbosity=2)
