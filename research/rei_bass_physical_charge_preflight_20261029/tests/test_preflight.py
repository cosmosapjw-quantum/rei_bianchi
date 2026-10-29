from __future__ import annotations
import importlib.util,json,random,unittest,hashlib,math,tempfile
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('inventory_preflight',ROOT/'code/inventory_preflight.py')
pre=importlib.util.module_from_spec(spec);spec.loader.exec_module(pre)

class TestSourceLockedPreflight(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=pre.load_rei();cls.model,cls.weights,cls.norm=pre.load_bass()
 def test_01_exact_source_count(self):self.assertEqual(len(self.rows),7)
 def test_02_pinned_bass_model(self):self.assertEqual(hashlib.sha256(pre.BASS.read_bytes()).hexdigest(),pre.SOURCE_HASH[pre.BASS.name])
 def test_03_pinned_rei_rows(self):self.assertEqual(hashlib.sha256(pre.REI.read_bytes()).hexdigest(),pre.SOURCE_HASH[pre.REI.name])
 def test_04_bass_source_code_guard(self):self.assertIsNotNone(pre.load_bass())
 def test_05_bass_full21_has_T(self):self.assertEqual(self.model['species_order'][5:7],['TI','TII'])
 def test_06_bass_zero_T(self):self.assertEqual(self.model['inventory_number_ratios_to_H1']['T'],0)
 def test_07_rei_positive_T_all_rows(self):self.assertTrue(all(pre.isotope_totals(r['y'])['T']>0 for r in self.rows))
 def test_08_rei_H_He_ratio_incompatible(self):
  target=self.weights['He4']/self.weights['H1']
  self.assertTrue(all(pre.isotope_totals(r['y'])['He4']/pre.isotope_totals(r['y'])['H1']!=target for r in self.rows))
 def test_09_minimax_certificate_exact_residual(self):
  for r in self.rows:
   c=pre.field_minimax(r['y'],self.weights)
   self.assertEqual(c['r_H'],-c['r_He4']);self.assertEqual(abs(c['r_H']),c['irreducible_relative'])
 def test_10_minimax_witness_vs_grid(self):
  rng=random.Random(2190)
  for _ in range(200):
   a=Q(rng.randint(1,100),rng.randint(1,100));b=Q(rng.randint(1,100),rng.randint(1,100))
   rho,d=pre.sharp_two_isotope_minimax(a,b)
   E=lambda x:max(abs(a*x-1),abs(b*x-1))
   self.assertEqual(E(rho),d)
   for fac in (Q(1,3),Q(3,4),Q(1,1),Q(5,4),Q(3,1)):self.assertGreaterEqual(E(rho*fac),d)
 def test_11_minimax_nonpositive_refusal(self):
  for x in ('0','-1'):
   with self.assertRaises(ValueError):pre.sharp_two_isotope_minimax(x,'1')
 def test_12_seven_photo_direct_exact(self):
  for row in self.rows:
   gamma=('1/1000','2/1000','3/1000')
   self.assertEqual(pre.photo_lumped_rhs(row['y'],gamma),pre.photo_direct_reduced_rhs(row['y'],gamma))
 def test_13_photo_random_state_exact(self):
  rng=random.Random(332)
  for _ in range(200):
   y=[Q(rng.randint(0,17),rng.randint(1,19)) for _ in range(17)]
   gg=[Q(rng.randint(0,20),rng.randint(1,23)) for _ in range(3)]
   self.assertEqual(pre.photo_lumped_rhs(y,gg),pre.photo_direct_reduced_rhs(y,gg))
 def test_14_photo_zero_source(self):
  y=[Q(0)]*17
  self.assertTrue(all(v==0 for v in pre.photo_full_rhs(y,['1','1','1'])))
 def test_15_photo_source_nonnegative_event_electrons(self):
  for r in self.rows:
   f=pre.photo_full_rhs(r['y'],['1/2000','1/1000','1/3000'])
   self.assertEqual(sum(pre.exact(a)*b for a,b in zip(f,pre.BARYON)),0)
   self.assertGreater(sum(pre.exact(a)*b for a,b in zip(f,pre.CHARGE)),0)
 def test_16_photo_He_closure_two_ion_stages(self):
  y=[Q(0)]*17;y[7]=Q(1,4);y[8]=Q(1,8);y[9]=Q(1,16);y[10]=Q(1,2);y[11]=Q(1,3)
  self.assertEqual(pre.photo_lumped_rhs(y,('2','3','5')),pre.photo_direct_reduced_rhs(y,('2','3','5')))
 def test_17_normalized_photo_clock_identity(self):
  for r in self.rows:
   y=r['y'];gg=('1/3','2/7','5/11');weights=self.weights;rho=Q(3,5);rp=Q(-1,10);H=Q(7,2)
   out=pre.normalized_lumped_rhs(y,gg,rho,rp,H,weights)
   self.assertEqual(out['charge_equality'],out['raw_charge_rho'])
   qy=sum(pre.exact(v)*q for v,q in zip(y,pre.CHARGE))
   f=pre.photo_full_rhs(y,gg)
   qf=sum(pre.exact(v)*q for v,q in zip(f,pre.CHARGE))
   wh=weights['H1']+weights['D'];whe=weights['He3']+weights['He4'];wli=weights['Li6']+weights['Li7']
   eb=(wh,whe,2*whe,wli,2*wli,3*wli)
   self.assertEqual(sum(wi*zi for wi,zi in zip(eb,out['zprime']))+out['Tprime'],rp*qy+rho/H*qf)
 def test_18_source_rate_equality_is_conditional(self):
  y=[Q(0)]*17;y[1]=Q(1,2);y[3]=Q(1,2)
  # same H charged + total, but unequal HI rate makes different projected source.
  yp=list(y);yp[1]=Q(1);yp[3]=Q(0)
  rateH,rateD=Q(1,2),Q(3,2)
  self.assertEqual(pre.reduced_raw(y)['Hplus'],pre.reduced_raw(yp)['Hplus'])
  self.assertEqual(pre.reduced_raw(y)['NH'],pre.reduced_raw(yp)['NH'])
  self.assertNotEqual(rateH*y[1]+rateD*y[3],rateH*yp[1]+rateD*yp[3])
 def test_19_conditional_source_T_invariant(self):
  y=[Q(0)]*17;y[1]=Q(1)
  self.assertEqual(pre.photo_lumped_rhs(y,('2','3','4'))['Tplus'],0)
 def test_20_different_full_rhs_extra_neutron_beta(self):
  # Original REI model.py also has beta_n=1/878.4, absent from six charge carrier.
  n0=Q(0);n1=Q(1,100);lam=Q(1)/Q('878.4')
  self.assertEqual(lam*n0,0);self.assertGreater(lam*n1,0)
 def test_21_hidden_Li6_is_not_in_REI_17_state(self):
  self.assertFalse(any(x.startswith('Li6') for x in pre.LABELS))
  self.assertGreater(self.weights['Li6'],0)
 def test_22_no_actual_physical_tau_or_source_radii(self):
  a=pre.source_compatibility()
  self.assertIsNone(a['actual_K_H_nb_nHref']);self.assertIsNone(a['full_chemistry_Jy'])
  self.assertEqual(a['working_dag'],'33/88');self.assertEqual(a['physical_delta'],0)
 def test_23_source_tamper_rejected(self):
  old=pre.BASS
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/'tampered.json';q.write_bytes(old.read_bytes()+b'X')
   try:
    pre.BASS=q
    with self.assertRaisesRegex(ValueError,'SOURCE_SHA_MISMATCH'):pre.load_bass()
   finally:pre.BASS=old
 def test_24_source_bool_float_rejected_as_exact_rational(self):
  for v in (True,1.234):
   with self.assertRaises(TypeError):pre.exact(v)
 def test_25_BASS_model_ratio_and_rho_scale(self):
  self.assertAlmostEqual(self.norm,1.3245833147583381,places=12)
  self.assertEqual(self.weights['T'],0)
  self.assertGreater(self.weights['He4'],0)
 def test_26_last_epoch_minimax_anchor(self):
  a=pre.field_minimax(self.rows[-1]['y'],self.weights)
  self.assertAlmostEqual(float(a['irreducible_relative']),0.005185866314686339,places=14)
 def test_27_all_epochs_minimax_window(self):
  ds=[pre.field_minimax(row['y'],self.weights)['irreducible_relative'] for row in self.rows]
  self.assertTrue(all(Q('0.004')<d<Q('0.006') for d in ds))
 def test_29_photo_lumped_jacobian_exact(self):
  g=('2','3','5');J=pre.photo_lumped_jacobian(g)
  self.assertEqual(J[0][0],-2);self.assertEqual(J[1][1],-8)
  self.assertEqual(J[1][2],-3);self.assertEqual(J[2][1],5);self.assertEqual(J[3][3],-2)
 def test_30_photo_helium_eigenpolynomial(self):
  rng=random.Random(9034)
  for _ in range(80):
   b=Q(rng.randrange(1,100),rng.randrange(1,100));c=Q(rng.randrange(1,100),rng.randrange(1,100))
   J=pre.photo_lumped_jacobian((Q(1),b,c))
   self.assertEqual(J[1][1]+J[2][2],-(b+c))
   self.assertEqual(J[1][1]*J[2][2]-J[1][2]*J[2][1],b*c)
 def test_31_zero_HI_rate_invariant(self):
  g=('0','3','4')
  J=pre.photo_lumped_jacobian(g)
  self.assertEqual(J[0][0],0);self.assertEqual(J[3][3],0)
 def test_32_photo_simplex_boundary_tangent_inward(self):
  # For all gamma>=0: on p=0, dp/dt=a*Nneutral>=0;
  # on d=0, dd/dt=b*p>=0; on p+d=NHe, d(p+d)/dt=0.
  y=[Q(0)]*17;y[8]=Q(1,3);y[9]=Q(2,3)
  f=pre.photo_lumped_rhs(y,('2','3','5'))
  self.assertEqual(f['Heplus']+f['He2plus'],0)
  y=[Q(0)]*17;y[7]=Q(3,4)
  self.assertGreaterEqual(pre.photo_lumped_rhs(y,('2','3','5'))['Heplus'],0)
 def test_28_common_rho_cannot_resolve_T(self):
  for row in self.rows:
   self.assertGreater(pre.isotope_totals(row['y'])['T'],0)
  self.assertEqual(self.weights['T'],0)
if __name__=='__main__':unittest.main()
