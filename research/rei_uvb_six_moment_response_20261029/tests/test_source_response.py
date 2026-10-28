"""New finite source-rate response tests; no old IVP/GLS campaigns rerun."""
import itertools,math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from source_response import *

class SourceResponseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d,cls.p,cls.rows=load();cls.geo=geometry(cls.d)
  cls.z=3.6;cls.a=cls.geo['a0']
 def test_01_source_sha_and_template(self):
  self.assertEqual(len(self.rows),13)
  x=np.array(self.d['z']);m=np.interp(x,self.rows[:,0],np.log10(self.rows[:,1]/1e-12))
  self.assertLess(np.max(np.abs(m-np.array(self.d['template_dex']))),1e-12)
 def test_02_full_covariance_projection(self):
  g=self.geo
  np.testing.assert_allclose(g['A']@g['X'],np.eye(2),rtol=0,atol=2e-13)
  np.testing.assert_allclose(g['A']@g['C']@g['A'].T,g['V'],rtol=0,atol=2e-13)
  self.assertGreater(np.min(np.linalg.eigvalsh(g['C'])),0)
 def test_03_independent_qr(self):
  g=self.geo;L=np.linalg.cholesky(g['C']);Q,R=np.linalg.qr(np.linalg.solve(L,g['X']))
  B=np.linalg.solve(R,Q.T@np.linalg.solve(L,np.eye(7)))
  np.testing.assert_allclose(B,g['A'],rtol=0,atol=1e-13)
 def test_04_six_units_positive(self):
  r=rate_response(self.z,self.a,self.rows)
  self.assertEqual(len(r['moments']),6);self.assertTrue(np.all(r['moments']>0))
  self.assertEqual(len(FIELDS),6)
 def test_05_nominal_pivot(self):
  r=rate_response(self.z,self.a,self.rows)
  self.assertAlmostEqual(r['factor'],10**self.a[0],places=14)
  self.assertEqual(r['jac'][0,1],0)
 def test_06_q0_exact_corner_extrema(self):
  g=self.geo
  for z in (2.4,3.6,4.75):
   t=tvec(z);arr=[]
   for th in (-1,1):
    for bits in itertools.product((0,1),repeat=7):
     j=np.where(bits,g['high'],g['low'])
     arr.append(float(t@(g['a0']+g['A']@(th*g['v']+j))))
   lo,hi=logfactor_support(z,0,g)
   self.assertAlmostEqual(lo,min(arr),places=13)
   self.assertAlmostEqual(hi,max(arr),places=13)
 def test_07_gaussian_ellipsoid_witness(self):
  g=self.geo;q=Q_JOINT2_95;t=tvec(4.0)
  nu=g['center']+g['G']@np.sign(g['G'].T@t)
  dv=math.sqrt(q)*g['V']@t/math.sqrt(float(t@g['V']@t))
  self.assertAlmostEqual(float(dv@np.linalg.solve(g['V'],dv)),q,places=11)
  self.assertAlmostEqual(float(t@(nu+dv)),logfactor_support(4.0,q,g)[1],places=12)
 def test_08_scalar_and_joint_coverage_labels(self):
  g=self.geo
  for z in (2.4,3.6,4.75):
   d=logfactor_support(z,0,g);s=logfactor_support(z,Q_SCALAR95,g);j=logfactor_support(z,Q_JOINT2_95,g)
   self.assertLess(j[0],s[0]);self.assertLess(s[0],d[0]);self.assertGreater(j[1],s[1]);self.assertGreater(s[1],d[1])
 def test_09_jacobian_finite_difference(self):
  z=4.0;a=self.a;resp=rate_response(z,a,self.rows);h=1e-6
  for k in range(2):
   e=np.eye(2)[k]*h
   fd=(rate_response(z,a+e,self.rows)['moments']-rate_response(z,a-e,self.rows)['moments'])/(2*h)
   np.testing.assert_allclose(fd,resp['jac'][:,k],rtol=2e-10,atol=1e-25)
 def test_10_hessian_finite_difference(self):
  z=4.0;a=self.a;resp=rate_response(z,a,self.rows);h=1e-5
  for k in range(2):
   e=np.eye(2)[k]*h
   fd=(rate_response(z,a+e,self.rows)['jac']-rate_response(z,a-e,self.rows)['jac'])/(2*h)
   np.testing.assert_allclose(fd,resp['hess'][:,:,k],rtol=3e-10,atol=1e-24)
 def test_11_six_common_factor_and_envelope(self):
  z=3.6;r=rate_response(z,self.a,self.rows)
  np.testing.assert_allclose(r['moments']/r['p19'],r['factor'],rtol=1e-15)
  en=pointwise_envelope(z,Q_JOINT2_95,self.geo,self.rows)
  np.testing.assert_allclose(en['moments_min']/r['p19'],en['factor'][0],rtol=1e-15)
 def test_12_fixed_population_ports(self):
  r=rate_response(3.6,self.a,self.rows);f={'HI':0.2,'HeI':0.1,'HeII':0.3}
  p=fixed_population_ports(r,f)
  self.assertTrue(p['fixed_population_only'])
  self.assertAlmostEqual(p['events_per_Href_s'][0],0.2*r['moments'][0],places=24)
  self.assertAlmostEqual(p['heat_eV_per_Href_s'][1],0.1*r['moments'][3],places=24)
  np.testing.assert_allclose(p['jac_heat'][2],0.3*r['jac'][5],rtol=0,atol=1e-25)
 def test_12b_photon_energy_ledger(self):
  r=rate_response(3.6,self.a,self.rows)
  p=fixed_population_ports(r,{'HI':0.2,'HeI':0.1,'HeII':0.3})
  # Manufactured positive thresholds, NOT an adopted atomic source constant.
  E={'HI':13.0,'HeI':24.0,'HeII':54.0}
  L=photon_energy_ledger(p,E)
  np.testing.assert_allclose(L['absorbed_photon_eV_per_Href_s'],L['ionization_storage_eV_per_Href_s']+L['photoheat_eV_per_Href_s'],rtol=0,atol=0)
  np.testing.assert_allclose(L['jac_absorbed_photon'],p['jac_heat']+np.array([13.,24.,54.])[:,None]*p['jac_events'],rtol=0,atol=0)
  with self.assertRaises(ValueError):photon_energy_ledger(p,{'HI':13.,'HeI':24.})
 def test_13_missing_target_fails(self):
  r=rate_response(3.6,self.a,self.rows)
  for f in ({},{'HI':0.1},{'HI':0.1,'HeI':-1,'HeII':0.2}):
   with self.assertRaises(ValueError):fixed_population_ports(r,f)
 def test_14_domain_and_prehistory(self):
  for z in (2.0,4.9,15.0,20.0):
   with self.assertRaises(ValueError):rate_response(z,self.a,self.rows)
  with self.assertRaisesRegex(ValueError,'MISSING_PREHISTORY'):rate_response(20.0,self.a,self.rows)
 def test_15_knot_one_sided(self):
  with self.assertRaisesRegex(ValueError,'ONE_SIDED'):p19_log_slopes(3.64,self.rows)
  np.testing.assert_allclose(p19_moments(3.64,self.rows),self.rows[7,1:],rtol=3e-14)
 def test_16_mean_clock_finite_difference(self):
  # The first binary64 central difference at h=1e-6 failed at 1.63e-9
  # relative due to cancellation; retain that failure and use MP80 source-level FD.
  import mpmath as mp
  mp.mp.dps=80
  z=3.6;H=1e-17;dx=mp.mpf('1e-16')
  result=mean_clock_response(z,H,self.a,self.rows)
  def mp_rate(zmp):
   i=next(i for i in range(len(self.rows)-1) if mp.mpf(repr(float(self.rows[i,0])))<zmp<mp.mpf(repr(float(self.rows[i+1,0]))))
   zl=mp.mpf(repr(float(self.rows[i,0])));zr=mp.mpf(repr(float(self.rows[i+1,0])))
   w=(zmp-zl)/(zr-zl)
   a0=mp.mpf(repr(float(self.a[0])));a1=mp.mpf(repr(float(self.a[1])))
   factor=mp.power(10,a0+a1*(zmp-mp.mpf('3.6')))
   return [mp.exp((1-w)*mp.log(mp.mpf(repr(float(self.rows[i,k]))))+w*mp.log(mp.mpf(repr(float(self.rows[i+1,k])))))*factor for k in range(1,7)]
  zp=mp.mpf('4.6')*mp.exp(-dx)-1;zm=mp.mpf('4.6')*mp.exp(dx)-1
  p=mp_rate(zp);m=mp_rate(zm)
  fd=np.array([float((u-v)/(2*dx)) for u,v in zip(p,m)])
  np.testing.assert_allclose(fd,result['d_moments_dx'],rtol=2e-12,atol=1e-26)
  np.testing.assert_allclose(result['d_moments_dt'],H*result['d_moments_dx'],rtol=0,atol=0)
 def test_17_tau_tangent_manufactured(self):
  K=1.;ne=.3;H=2.;dne=.2;dH=-.4;h=1e-6
  f,t=tau_rhs_and_tangent(K,ne,H,dne,dH)
  fd=(tau_rhs_and_tangent(K,ne+h*dne,H+h*dH,0,0)[0]-tau_rhs_and_tangent(K,ne-h*dne,H-h*dH,0,0)[0])/(2*h)
  self.assertAlmostEqual(f,.15,places=15);self.assertAlmostEqual(t,fd,places=10)
 def test_18_taylor_positive_remainder(self):
  rate=rate_response(4.0,self.a,self.rows)['moments'][0]
  for da in ([.05,-.01],[-.04,.02],[0.,0.]):
   rem,upper=taylor_remainder(rate,4.0,da)
   self.assertGreaterEqual(rem,-1e-27);self.assertLessEqual(rem,upper+1e-27)
 def test_19_negative_q(self):
  with self.assertRaises(ValueError):logfactor_support(3.6,-1,self.geo)
 def test_20_zero_H_and_missing_chemistry(self):
  with self.assertRaises(ValueError):mean_clock_response(3.6,0,self.a,self.rows)
  with self.assertRaises(ValueError):tau_rhs_and_tangent(1,1,0,0,0)
if __name__=='__main__':unittest.main(verbosity=2)
