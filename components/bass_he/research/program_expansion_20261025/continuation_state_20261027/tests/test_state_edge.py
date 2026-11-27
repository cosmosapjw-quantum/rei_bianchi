import json,math,sys,unittest
from decimal import Decimal,localcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import state_edge as m
P=ROOT.parent/'continuation_event_20261027/sources/raw_wu_r4/sources/MOLECULAR_SOURCE_PACKET.json'
def ref(T,rate):
 with localcontext() as c:
  c.prec=80;D=Decimal;delta=D('100')*D('6.62607015e-34')*D('299792458')*D('89.227900');r=D(3)*(-delta/(D('1.380649e-23')*D(str(T)))).exp();return delta,D(rate)*D('1e-6'),r,D(rate)*D('1e-6')*r
class Controls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=m.parse()
 def test_01_structure(self):
  d=self.d;self.assertEqual((len(d['levels']),len(d['radiative']),len(d['collisions']),len(d['temperatures'])),(52,368,171,25));self.assertEqual(len({int(x) for row in d['collisions'] for x in row[1:3]}),19);self.assertEqual(d['temperatures'][-1],'3005.0')
 def test_02_rates(self):
  self.assertEqual(sum(len(r[3:]) for r in self.d['collisions']),4275);self.assertTrue(all(math.isfinite(float(x)) and float(x)>=0 for r in self.d['collisions'] for x in r[3:]));self.assertEqual(self.d['radiative'][0][3],'5.443e-08')
 def test_03_bindings(self):
  self.assertEqual(self.d['levels'][0][:3],['1','0.000000','1.0']);self.assertEqual(self.d['levels'][1][:3],['2','89.227900','3.0']);self.assertEqual(m.native(self.d,1005)['printed_cm3_s'],'2.48e-10')
 def test_04_units(self):
  p=m.pair(self.d,1005,m.CLOSURE);delta,down,_,_=ref(1005,'2.48e-10');self.assertAlmostEqual(p['delta_j']/float(delta),1,delta=5e-13);self.assertAlmostEqual(p['down_m3_s']/float(down),1,delta=5e-13)
 def test_05_selector_rejections(self):
  for T in (1000,0,-1,3005,3001,float('nan'),float('inf'),True):
   with self.subTest(T=T),self.assertRaises(m.ContractError):m.native(self.d,T)
 def test_06_all_24_reciprocity(self):
  for T in self.d['temperatures'][:-1]:
   p=m.pair(self.d,float(T),m.CLOSURE);_,_,r,up=ref(T,p['printed_cm3_s']);self.assertAlmostEqual(p['up_m3_s']/float(up),1,delta=5e-13);self.assertAlmostEqual(p['equilibrium_ratio']/float(r),1,delta=5e-13)
 def test_07_explicit_closure(self):
  for x in (None,'',True,'LTE'):
   with self.assertRaises(m.ContractError):m.pair(self.d,1005,x)
 def test_08_equilibrium_signs(self):
  r=m.pair(self.d,1005,m.CLOSURE)['equilibrium_ratio'];cases=[m.source(self.d,1005,1e6,2e6,2e6*r*x,m.CLOSURE) for x in (0.5,1,2)];self.assertGreater(cases[0]['Gamma_upper'],0);self.assertLess(cases[2]['Gamma_upper'],0);self.assertLessEqual(abs(cases[1]['Gamma_upper']),64*sys.float_info.epsilon*(cases[1]['j_up']+cases[1]['j_down']))
 def test_09_particle_conservation(self):
  s=m.source(self.d,1005,1e6,2e6,1e6,m.CLOSURE);self.assertEqual(s['Gamma_lower']+s['Gamma_upper'],0);self.assertEqual(s['Gamma_Hplus'],0)
 def test_10_energy(self):
  s=m.source(self.d,1005,1e6,2e6,1e6,m.CLOSURE);self.assertEqual(s['population_internal_witness_W_m3']+s['material_kinetic_compensation_W_m3'],0)
  with localcontext() as c:
   c.prec=80;delta,down,_,up=ref(1005,'2.48e-10');J=Decimal('1e6')*(Decimal('2e6')*up-Decimal('1e6')*down);self.assertAlmostEqual(s['Gamma_upper']/float(J),1,delta=5e-13);self.assertAlmostEqual(s['population_internal_witness_W_m3']/float(delta*J),1,delta=5e-13)
 def test_11_offset(self):
  with localcontext() as c:
   c.prec=80;D=Decimal;offset=D('12345');self.assertEqual((offset+D('89.227900'))-(offset+D('0.000000')),D('89.227900'))
 def test_12_zero_and_invalid(self):
  z=m.source(self.d,1005,0,1,1,m.CLOSURE);self.assertEqual(z['Gamma_upper'],0);self.assertIsNone(z['entropy_production_over_kB']);self.assertEqual(z['zero_flux_log_diagnostic'],'UNDEFINED_OR_LIMIT')
  for x in (-1,True,float('nan'),float('inf')):
   with self.assertRaises(m.ContractError):m.source(self.d,1005,x,1,1,m.CLOSURE)
  for x in (-1,True,float('nan'),float('inf')):
   for lower,upper in ((x,1),(1,x)):
    with self.assertRaises(m.ContractError):m.source(self.d,1005,0,lower,upper,m.CLOSURE)
 def test_13_range(self):
  for values in ((1e308,1e308,1),(5e-324,5e-324,1)):
   with self.assertRaises(m.ContractError):m.source(self.d,1005,*values,m.CLOSURE)
 def test_14_entropy(self):
  for lower,upper in ((2e6,1e5),(2e6,1e6),(2e6,1e7),(1e200,1e-200)):
   s=m.source(self.d,1005,1e6,lower,upper,m.CLOSURE);actual=s['entropy_production_over_kB'];self.assertTrue(math.isfinite(actual));self.assertGreaterEqual(actual,0)
   with localcontext() as c:
    c.prec=80;_,down,_,up=ref(1005,'2.48e-10');a=Decimal('1e6')*Decimal(str(lower))*up;b=Decimal('1e6')*Decimal(str(upper))*down;expected=(a-b)*(a.ln()-b.ln());self.assertAlmostEqual(actual/float(expected),1,delta=5e-13);self.assertLessEqual(-m.KB*1005*actual,0)
 def test_15_ownership(self):
  s=m.source(self.d,1005,1e6,2e6,1e6,m.CLOSURE);self.assertTrue(all(s[k] is None for k in ('species_heat','species_momentum','species_stress','independent_internal_rhs')));self.assertEqual(s['birth_pool'],'UNASSIGNED');self.assertFalse(s['physical_global_consumer_admitted'])
 def test_16_radiation(self):
  self.assertEqual(self.d['radiative'][0][3],'5.443e-08');self.assertFalse(m.source(self.d,1005,1,1,1,m.CLOSURE)['radiative_photon_emitted'])
 def test_17_correction(self):
  p=m.lih_select('BENNETT2008_CORRECTED');rows=dict(p['rows']);self.assertEqual((len(rows),rows['1000.0'],rows['3000.0']),(27,'3.19','1.80'));self.assertFalse(p['additive']);self.assertEqual(rows['50.0'],'3.86');self.assertEqual(rows['10000.0'],'0.55')
  with self.assertRaises(m.ContractError):m.lih_select('BENNETT2003')
 def test_18_source_boundaries(self):
  p=m.lih_select('BENNETT2008_CORRECTED');self.assertIsNone(p['physical_covariance']);self.assertFalse(p['RA_state_binding']);self.assertFalse(p['fit_evaluated']);self.assertEqual(self.d['temperatures'][-1],'3005.0')
 def test_19_saved_data(self):
  hd=[m.pair(self.d,float(T),m.CLOSURE) for T in self.d['temperatures'][:-1]];r=hd[20]['equilibrium_ratio'];samples=[m.source(self.d,1005,1e6,2e6,2e6*r*f,m.CLOSURE) for f in (0,0.5,1,2)];packet=json.loads(P.read_text());old=next(x for x in packet['rows'] if x['id']=='BENNETT2003_LIH_SPONTANEOUS_RA_TABLE3')['native_rows'];new=m.lih_select('BENNETT2008_CORRECTED')['rows'];self.assertEqual(len(old),27);self.assertEqual([x['T'] for x in old],[x[0] for x in new]);self.assertEqual([(x['k_mantissa']) for x in old if x['T'] in ('1000.0','3000.0')],['17.7','51.2']);data={'hd':hd,'hd_3005_native_hold':self.d['collisions'][0][-1],'samples':samples,'lih_old':[[x['T'],x['k_mantissa']] for x in old],'lih_corrected':new,'scope':'synthetic examples and source printed values; no physical global admission'};path=ROOT/'evidence/validation/SAVED_PLOT_DATA.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+'\n')
