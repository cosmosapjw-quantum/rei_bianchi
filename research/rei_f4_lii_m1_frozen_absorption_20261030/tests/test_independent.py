"""Independent high precision Verner formula and negative provenance checks."""
import sys,unittest
from pathlib import Path
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import m1_absorption as m
class IndependentSourceCheck(unittest.TestCase):
 def test_mpmath80_four_source_cross_sections(self):
  mp.mp.dps=80
  # Independently copied source-owned Verner 1996 row coefficients,
  # exact numeric fingerprints from original BASS blob 2eba600a9...
  params={
   'H1I':('0.4298','54750','32.88','2.963','0','0','0'),
   'He4I':('13.61','949.2','1.469','3.188','2.039','.4434','2.136'),
   'He4II':('1.72','13690','32.88','2.963','0','0','0')}
  arr,src,pr,cap=m.load_sources()
  for name,row in params.items():
   e0,s0,ya,p,yw,y0,y1=map(mp.mpf,row)
   e=mp.mpf(str(m.ENERGY)); x=e/e0-y0;y=mp.sqrt(x*x+y1*y1)
   mb=s0*((x-1)**2+yw*yw)*y**(p/mp.mpf(2)-mp.mpf('5.5'))*(1+mp.sqrt(y/ya))**(-p)
   physical_m2=float(mb*mp.mpf('1e-22'))
   got=float(src['sigma_m2'][src['names'].index(name)])
   self.assertLess(abs(physical_m2/got-1),1e-12,(name,physical_m2,got))
 def test_source_zip_hash_negative(self):
  saved=m.SHA_PR280
  try:
   m.SHA_PR280='0'*64
   with self.assertRaisesRegex(ValueError,'SOURCE_ZIP_SHA'):
    m.load_sources()
  finally:m.SHA_PR280=saved
 def test_frozen_crossing_bracket(self):
  rows,_,_=m.compute()
  for key,level,zhi,zlo in [('first_photoabsorption_He_II_fraction',.5,9.226077552875777,9.122960208701825),
                           ('tau_one_frozen_Hubble_length',1,2.09261538166547,2.0614301805891118)]:
   r=[x for x in rows if min(zlo,zhi)-1e-8<=x['z']<=max(zlo,zhi)+1e-8]
   self.assertEqual(len(r),2)
   self.assertLessEqual(min(x[key] for x in r),level)
   self.assertGreaterEqual(max(x[key] for x in r),level)
if __name__=='__main__':unittest.main()
