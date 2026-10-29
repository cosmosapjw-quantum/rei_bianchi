"""Targeted no-IVP source and observability checks for BASS193 charge-blind jets."""
from __future__ import annotations
import unittest,sys,io,zipfile,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import charge_jets as cj

class ChargeJets(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.saved=cj.load_original();cls.net=cj.src.new_native_network();cls.result=cj.calculate()

 def test_01_source_hash_and_saved_shape(self):
  self.assertEqual(self.saved['Y'].shape,(193,21));self.assertEqual(len(self.result['saved_193']),193)
  self.assertEqual(self.saved['z'][0],20.0)
  self.assertAlmostEqual(self.saved['z'][-1],2,places=13)

 def test_02_baryon_density_source_clock(self):
  idx=list(map(str,self.saved['diagnostic_names'])).index('nb_m3')
  nb=self.saved['diagnostics'][:,idx]
  np.testing.assert_allclose(nb/nb[0],np.exp(-3*self.saved['x']),rtol=2e-14,atol=0)

 def test_03_mass_charge_blind_basis(self):
  np.testing.assert_array_equal(np.sum(cj.V,axis=0),np.zeros(2))
  np.testing.assert_array_equal(cj.Q4@cj.V,np.zeros(2))
  self.assertEqual(int(np.linalg.matrix_rank(cj.V)),2)

 def test_04_native_event_replay_and_full_j(self):
  d=np.load(ROOT/'source/PR275_FJ_193.npz',allow_pickle=False)
  for i in [0,37,65,100,150,192]:
   Y=self.saved['Y'][i];di={str(k):j for j,k in enumerate(self.saved['diagnostic_names'])};diag=self.saved['diagnostics'][i]
   native=self.net.evaluate(Y,float(diag[di['T_K']]),float(diag[di['uv_scale']]),float(diag[di['nb_m3']]))
   self.assertLess(np.max(abs(native['dY_dt']-d['F_21'][i])),2e-31)
   self.assertLess(np.max(abs(native['jac']-d['J_21x21'][i])),2e-29)

 def test_05_analytic_recomb_temperature_derivative(self):
  for i in [65,75,100,150,192]:
   point,_=cj.source_point(self.net,self.saved,i);T=point['T_K'];dT=min(0.0002*T,0.1*T)
   approx=(self.net.rates(T+dT,0)['Gne']-self.net.rates(T-dT,0)['Gne'])/(2*dT)
   true=cj.recombination_T_derivative(self.net,T)
   relative=np.max(abs(approx-true))/max(np.max(abs(true)),1e-100)
   self.assertLess(relative,3e-7)

 def test_06_real_bath_and_nonnegative_perturbation(self):
  for i in [0,27,65,90,125,150,192]:
   row,_=cj.source_point(self.net,self.saved,i)
   self.assertLess(row['derivative_bath_consistency'],3e-11)
   eps=row['perturb_epsilon_per_baryon'];base=self.saved['Y'][i,13:17]
   self.assertTrue(np.all(base+eps*cj.V[:,1]>=0))
   self.assertLess(abs(row['perturb_charge_sum']),max(1e-40,2e-15*eps))

 def test_07_jacobian_electron_invisible_direction(self):
  for i in [70,100,150,192]:
   row,(M,Mdot,full,rr,y,perturb)=cj.source_point(self.net,self.saved,i)
   d=np.zeros(21);d[13:17]=perturb
   self.assertLess(abs(self.net.q@d),max(1e-40,2e-15*max(abs(perturb))))
   
   # Exact 21x21 J includes outer(Gne Y,q), which annihilates q-blind tangent.
   diff=full['jac']@d
   ref=M@perturb
   self.assertLess(np.max(abs(diff[13:17]-ref)),max(1e-60,8e-16*np.max(abs(ref))))
   self.assertLess(np.max(abs(diff[cj.P_KEEP])),max(1e-45,5e-15*np.max(abs(ref))))

 def test_08_independent_event_charge_current(self):
  for i in [0,70,100,192]:
   row,(M,Mdot,full,rr,y,perturb)=cj.source_point(self.net,self.saved,i)
   charge_M=cj.Q4@M
   ne=row['ne_m3'];up=rr['photo_s'][13:16]
   dn=ne*(rr['rr_m3_s']+rr['dr_m3_s'])[14:17]
   charge_event=np.array([up[0],up[1]-dn[0],up[2]-dn[1],-dn[2]])
   self.assertLess(np.max(abs(charge_M-charge_event)),max(1e-38,1e-14*np.max(abs(charge_M))))

 def test_09_nonautonomous_and_frozen_differ(self):
  row,_=cj.source_point(self.net,self.saved,45)
  self.assertGreater(abs(row['det_nonautonomous']-row['det_frozen']),0.1)

 def test_10_verified_sign_brackets(self):
  self.assertEqual(len(self.result['sign_brackets']['frozen']),3)
  self.assertEqual(len(self.result['sign_brackets']['nonautonomous']),5)
  for kind in ['frozen','nonautonomous']:
   for bracket in self.result['sign_brackets'][kind]:
    self.assertLess(bracket['det_left']*bracket['det_right'],0.)
    self.assertGreater(bracket['z_high'],bracket['z_low'])

 def test_11_nonautonomous_local_electron_jets(self):
  row,(M,Mdot,full,rr,y,p)=cj.source_point(self.net,self.saved,192)
  # Evolving source linearized observability is q (Mdot + M^2), not q M^2.
  self.assertAlmostEqual(row['jet1_v2_s'],float(cj.Q4@M@cj.V[:,1]),delta=1e-27)
  self.assertAlmostEqual(row['jet2_v2_s2'],float(cj.Q4@(Mdot+M@M)@cj.V[:,1]),delta=1e-39)
  self.assertGreater(abs(row['delta_electron_source_per_baryon_s']),1e-32)
  self.assertGreater(row['delta_retained_second_l1_per_baryon_s2'],0.)

 def test_12_source_fixed_finite_derivative_of_M(self):
  # Single-step differentiability check in input space, NOT an ODE step.
  for i in [60,90,120,160]:
   row,(M,Mdot,full,rr,y,p)=cj.source_point(self.net,self.saved,i)
   x=row['x']; H=row['H_s'];nb=row['nb_m3'];zz=row['z'];ee=1e-5
   ne=row['ne_m3'];ne_x=-3*ne+nb*(self.net.q@full['dY_dt'])/H
   def evaluate_at_x(shift):
    z_new=21.*math.exp(-(x+shift))-1.
    T,uv=cj.src.original_bass_bath_at_z(z_new)
    n_new=ne+shift*ne_x
    r=self.net.rates(T,uv)
    return r['G0'][13:17,13:17]+n_new*r['Gne'][13:17,13:17]
   mx=(evaluate_at_x(ee)-evaluate_at_x(-ee))/(2*ee)
   denom=max(np.max(abs(Mdot/H)),1e-99)
   self.assertLess(np.max(abs(mx-Mdot/H))/denom,2e-6)

 def test_13_no_IVP_and_positive_model(self):
  import inspect
  s=inspect.getsource(cj)
  self.assertNotIn('solve_ivp',s)
  self.assertEqual(self.result['new_ivp'],0)
  self.assertTrue(np.isfinite([r['det_nonautonomous'] for r in self.result['saved_193']]).all())

if __name__=='__main__':unittest.main()
