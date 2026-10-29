"""Bounded independent-target tests; real source/trajectory, no new IVP."""
from __future__ import annotations
import csv, math, sys, unittest, numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import quasi_eq as q

class NativeEquilibrium(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a,cls.net=q.source();cls.d={str(k):cls.a['diagnostics'][:,i] for i,k in enumerate(cls.a['diagnostic_names'])}
  with (ROOT/'results/EQUILIBRIUM_193x6.csv').open(newline='') as f:cls.rows=list(csv.DictReader(f))
  with (ROOT/'results/ELECTRON_FEEDBACK_193.csv').open(newline='') as f:cls.epochs=list(csv.DictReader(f))
 def test_01_authoritative_sha_and_grain(self):
  self.assertEqual(self.a['Y'].shape,(193,21));self.assertEqual(len(self.rows),1158);self.assertEqual(len(self.epochs),193)
  self.assertAlmostEqual(float(self.a['z'][0]),20);self.assertAlmostEqual(float(self.a['z'][-1]),2)
 def test_02_source_ne_nb_and_baryon(self):
  for i in [0,13,55,80,119,192]:
   y=self.a['Y'][i]; self.assertAlmostEqual(float(self.net.q@y),float(self.d['ne_m3'][i]/self.d['nb_m3'][i]),delta=5e-14)
   self.assertAlmostEqual(float(self.net.A@y),1.,delta=4e-10)
 def test_03_exact_2state_closed_form(self):
  for ne in [0.01,1.,7e5]:
   up=np.array([2.3]);down=np.array([0.45]);pi,m,var=q.stationary(up,down,ne)
   self.assertAlmostEqual(pi[1],2.3/(2.3+0.45*ne),delta=1e-15)
   self.assertAlmostEqual(var,pi[0]*pi[1],delta=1e-14)
 def test_04_log_ne_derivative_equals_minus_variance(self):
  up=np.array([1.2,3.1,0.7]);down=np.array([0.25,0.81,2.1]); ne=0.65;h=1e-5
  c=q.stationary(up,down,ne)[2]
  xp=q.stationary(up,down,ne*np.exp(h))[1]
  xm=q.stationary(up,down,ne*np.exp(-h))[1]
  self.assertLess(abs((xp-xm)/(2*h)+c),1e-9)
 def test_05_nonnegative_stationary_and_generator(self):
  for i in [0,24,55,90,160,192]:
   ne=float(self.d['ne_m3'][i]); rates=self.net.rates(float(self.d['T_K'][i]),float(self.d['uv_scale'][i]))
   for g in q.GROUPS:
    idx,up,down=q.group_rates(self.net,rates,g);pi,mean,var=q.stationary(up,down,ne)
    M=q.local_generator(up,down,ne)
    self.assertTrue(np.all(pi>=0));self.assertAlmostEqual(float(pi.sum()),1.,delta=1e-14)
    self.assertLess(np.max(np.abs(M@pi)),2e-25);self.assertLess(np.max(np.abs(M.sum(axis=0))),1e-24)
 def test_06_source_family_isotopic_equality(self):
  for i in [0,40,80,140,192]:
   T=float(self.d['T_K'][i]);UV=float(self.d['uv_scale'][i]);rate=self.net.rates(T,UV)
   for a,b in [('H1','D'),('He3','He4'),('Li6','Li7')]:
    _,x,y=q.group_rates(self.net,rate,a);_,u,v=q.group_rates(self.net,rate,b)
    self.assertTrue(np.array_equal(x,u));self.assertTrue(np.array_equal(y,v))
 def test_07_root_satisfies_fixedpoint(self):
  for i in [0,40,80,122,192]:
   rate=self.net.rates(float(self.d['T_K'][i]),float(self.d['uv_scale'][i]))
   ni={g:float(np.sum(self.net.initial_Y[list(self.net.isotope_groups[g])])) for g in q.GROUPS}
   xe,params,rerr,limit=q.root_for_rates(self.net,rate,float(self.d['nb_m3'][i]),ni)
   self.assertLess(rerr,2e-14);self.assertLess(xe,limit);self.assertGreater(xe,0)
 def test_08_self_consistent_eq_actual_native_rhs(self):
  for i in [0,40,80,122,192]:
   rate=self.net.rates(float(self.d['T_K'][i]),float(self.d['uv_scale'][i]));nb=float(self.d['nb_m3'][i]);ni={g:float(np.sum(self.net.initial_Y[list(self.net.isotope_groups[g])])) for g in q.GROUPS}
   xe,par,_,_=q.root_for_rates(self.net,rate,nb,ni);ystar=np.zeros(21)
   for g,(idx,up,down) in par.items():ystar[idx]=ni[g]*q.stationary(up,down,nb*xe)[0]
   f=self.net.evaluate(ystar,float(self.d['T_K'][i]),float(self.d['uv_scale'][i]),nb)['dY_dt']
   self.assertLess(float(np.max(np.abs(f))),1e-23)
 def test_09_output_consistency_charge_and_source(self):
  row=self.epochs[0];self.assertLess(float(row['xe_star']),float(row['xe_saved']))
  row=self.epochs[-1];self.assertLess(abs(float(row['xe_star'])-float(row['xe_saved'])),2e-8)
  for t in self.epochs:
   a=float(t['xe_star_minus_saved']);b=float(t['xe_star'])-float(t['xe_saved']);self.assertLess(abs(a-b),2e-15)
 def test_10_each_isotope_probability_TV(self):
  for r in self.rows:
   tv=float(r['TV_distance']);self.assertTrue(0<=tv<=1.+1e-12)
   self.assertTrue(float(r['gap_over_H'])>0.)
 def test_11_negative_domain(self):
  with self.assertRaises(ValueError):q.stationary(np.array([1.]),np.array([1.]),0.)
  with self.assertRaises(ValueError):q.stationary(np.array([1.]),np.array([1.]),-1.)
  with self.assertRaises(ValueError):q.root_for_rates(self.net,self.net.rates(100.,1.),-1.,{g:1 for g in q.GROUPS})
 def test_12_diagnostic_no_hidden_IVP(self):
  import inspect
  code=inspect.getsource(q)
  self.assertNotIn('solve_ivp',code);self.assertNotIn('odeint',code)
  self.assertEqual(len(set(r['group'] for r in self.rows)),6)

if __name__=='__main__':unittest.main()
