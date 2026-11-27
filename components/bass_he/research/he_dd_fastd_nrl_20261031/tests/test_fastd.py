import csv,math,pathlib,unittest,sys
from scipy import constants as c
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from fastd import *
ROOT=pathlib.Path(__file__).resolve().parents[1]
class StoppingPhysicsTests(unittest.TestCase):
 def test_charge_neutrality(self):
  for z in REDSHIFTS:
   p=plasma(z)
   self.assertAlmostEqual(p.n_e_m3,p.n_p_m3+2*p.n_a_m3,delta=1e-12*p.n_e_m3)
 def test_redshift_scaling(self):
  a=plasma(1e4);b=plasma(1e5)
  self.assertAlmostEqual(b.n_b_m3/a.n_b_m3,((1e5+1)/(1e4+1))**3,places=12)
 def test_source_identity_pr131(self):
  self.assertEqual(NB0_CM3,2.515e-7);self.assertEqual(Y_HE,.2448);self.assertEqual(T0_K,2.7255)
 def test_psi_analytic(self):
  for x in [1e-4,.2,1,10,100]:
   s,d=psi(x)
   self.assertAlmostEqual(s,math.erf(math.sqrt(x))-2/math.sqrt(math.pi)*math.sqrt(x)*math.exp(-x),delta=1e-12)
   self.assertGreaterEqual(d,0.)
  self.assertAlmostEqual(psi(1e-6)[0]/(1e-9),4/(3*math.sqrt(math.pi)),delta=5e-6)
 def test_electron_low_velocity_heating(self):
  p=plasma(1e5);q=spitzer_species(.2*p.kBT_MeV,p,'electron')
  self.assertLess(q['loss_MeV_s'],0.)
 def test_electron_fast_limit(self):
  p=plasma(1e5);q=spitzer_species(20.,p,'electron')
  self.assertAlmostEqual(q['psi'],1.,delta=1e-12);self.assertLess(q['dpsi'],1e-10)
 def test_validity_lambda_weak(self):
  for z in REDSHIFTS:
   p=plasma(z)
   for E in [.1,1,10,100]:
    for sp in ['electron','proton','alpha']:
     q=spitzer_species(E,p,sp)
     self.assertGreater(q['lnLambda'],9.)
     self.assertGreater(q['bmax_cm'],q['bmin_cm'])
 def test_positive_rates_above_cut(self):
  for z in REDSHIFTS:
   p=plasma(z)
   for E in [terminal(p),.1,1,10,30]:
    for v in ('electron','proton','alpha'):
     self.assertGreater(spitzer_species(E,p,v)['loss_MeV_s'],0.)
 def test_helium_removed(self):
  p=plasma(1e5,y_he=0.)
  self.assertEqual(p.n_a_m3,0)
  self.assertEqual(spitzer_species(1.,p,'alpha')['loss_MeV_s'],0.)
 def test_representative_stop(self):
  p=plasma(1e5);x=integrate(1.,p)
  self.assertAlmostEqual(x['Q_e_MeV'],.9972050324390451,delta=5e-9)
  self.assertAlmostEqual(x['t_stop_s'],430.08105168206123,delta=2e-5)
 def test_conservation_on_50_states(self):
  with (ROOT/'data/FASTD_INTEGRATED_50.csv').open() as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),50)
  for r in rows:
   gap=sum(float(r[k]) for k in ['Q_e_MeV','Q_p_MeV','Q_alpha_MeV'])-float(r['deltaK_MeV'])
   self.assertLess(abs(gap),1e-8)
   self.assertLess(float(r['stop_over_Hubble']),.002)
 def test_exposure_dimensions(self):
  p=plasma(1e5);r=integrate(1.,p)
  self.assertAlmostEqual(r['exposure_p_cm2'],r['L_path_m']*p.n_p_m3*1e-4,delta=1e5)
 def test_nuclear_1mb_reference_not_actual(self):
  r=integrate(1.,plasma(1e5))
  self.assertAlmostEqual(r['tau_reference_p_1mb'],r['exposure_p_cm2']*1e-27,delta=1e-14)
 def test_quadrature_resolution(self):
  for k in [.1,1.,10.,30.]:
   p=plasma(1e5)
   a=integrate(k,p,order=160);b=integrate(k,p,order=320)
   self.assertLess(abs(a['t_stop_s']-b['t_stop_s'])/b['t_stop_s'],1e-5)
 def test_high_energies_tagged(self):
  self.assertEqual(integrate(50.,plasma(1e5))['source_scope'],'EXPLORATORY_NONREL')
 def test_no_heatrate(self):
  r=integrate(1.,plasma(1e5));self.assertNotIn('heat_rate',r);self.assertNotIn('R_event',r)
if __name__=='__main__': unittest.main()
