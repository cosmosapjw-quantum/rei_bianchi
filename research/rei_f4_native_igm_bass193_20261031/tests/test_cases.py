import csv,hashlib,pathlib,unittest,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
class TestSourceCases(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with (ROOT/'data/native_rei_igm_193_cases.csv').open() as f:cls.rows=list(csv.DictReader(f))
 def test_193_origins(self):
  self.assertEqual(len(self.rows),193)
  self.assertEqual([int(row['epoch']) for row in self.rows],list(range(193)))
 def test_clock(self):
  for i in range(1,193):
   lo,hi=self.rows[i-1:i+1]
   dt=float(hi['proper_elapsed_s'])-float(lo['proper_elapsed_s']);dx=float(hi['x'])-float(lo['x']);h=(float(lo['H_s'])+float(hi['H_s']))/2
   self.assertLess(abs(dt*h/dx-1),5e-5)
 def test_source_nonaddition(self):
  for r in self.rows:
   assert float(r['nHref_cm3'])>0
   for v in ('Gamma_HI_s','Gamma_HeI_s','Gamma_HeII_s'):self.assertGreaterEqual(float(r[v]),0)
 def test_he_complement(self):
  for r in self.rows:
   a=float(r['x_HeII']);b=float(r['x_HeIII']);self.assertGreaterEqual(a,0);self.assertGreaterEqual(b,0);self.assertLessEqual(a+b,1)
 def test_photo_admission(self):
  chi=[13.598434599702,24.587389011,54.41776]
  for r in self.rows:
   nh=float(r['nHref_cm3']);nhe=float(r['nHe4_cm3']);xh=float(r['x_HII']);xhe=float(r['x_HeII']);xhei=float(r['x_HeIII'])
   n=[nh*(1-xh),nhe*(1-xhe-xhei),nhe*xhe]
   g=[float(r[x]) for x in ('Gamma_HI_s','Gamma_HeI_s','Gamma_HeII_s')]
   heat=[float(r[x]) for x in ('heat_HI_erg_per_absorber_s','heat_HeI_erg_per_absorber_s','heat_HeII_erg_per_absorber_s')]
   total=sum(ni*(gi*ei*1.602176634e-12+wi) for ni,gi,ei,wi in zip(n,g,chi,heat))
   target=float(r['expected_photo_input_erg_cm3_s'])
   self.assertLess(abs(total-target),5e-8*max(abs(total),abs(target),1e-60))
 def test_thermal_energy_identity_in_saved_source(self):
  for r in self.rows:
   f=lambda k:float(r[k]);res=f('expected_thermal_erg_cm3_s')+f('expected_binding_erg_cm3_s')+f('expected_escape_erg_cm3_s')-f('expected_photo_input_erg_cm3_s')-f('expected_CMB_erg_cm3_s')
   self.assertLess(abs(res),2e-43)
if __name__=='__main__': unittest.main()
