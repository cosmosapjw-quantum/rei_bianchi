import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import unittest,json,pathlib,numpy as np
from spectral_joint11 import SpectralModel,coalesce_reflections,R
class NativeSpectral(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packets=[json.loads((R/f'inputs/spectral11/m{k}.json').read_text()) for k in range(3)]
 def test_unchanged_47_cells_and_clocks(self):
  a=np.array(self.packets[0]['cohorts']);ref=a[a[:,7]!=0]
  for p in self.packets[1:]:
   b=np.array(p['cohorts']);self.assertEqual(ref.tobytes(),b[b[:,7]!=0].tobytes());np.testing.assert_array_equal(np.unique(a[:,1]),np.unique(b[:,1]))
 def test_masks_match_native_interior(self):
  from retarded_integrator import sigma_native_formula
  m=SpectralModel(coalesce_reflections(self.packets[1]));ed=json.loads((R/'inputs/spectral11/m1_events.json').read_text());pts=ed['points']
  for k in [10,100,1000,2000]:
   left,right=pts[k:k+2];ac=np.searchsorted(m.birth,left,side='right');mid=.5*(left+right);m.set_interval(left,right,ac)
   e=m.rays(mid,ac)[0];np.testing.assert_allclose(m.section_sigma(e),sigma_native_formula(e,m.chi),rtol=2e-15,atol=0)
 def test_sided_threshold_extension(self):
  m=SpectralModel(coalesce_reflections(self.packets[1]));ed=json.loads((R/'inputs/spectral11/m1_events.json').read_text());z,j,sp,_=ed['roots'][0]
  k=np.searchsorted(ed['points'],z);left=ed['points'][k-1];m.set_interval(left,z,np.searchsorted(m.birth,left,side='right'))
  e=m.rays(z,m.section_active)[0];e[j]=np.nextafter(13.6,0.);self.assertGreater(m.section_sigma(e)[j,0],0.)
  right=ed['points'][k+1];m.set_interval(z,right,np.searchsorted(m.birth,z,side='right'));e=m.rays(z,m.section_active)[0];self.assertEqual(m.section_sigma(e)[j,0],0.)
if __name__=='__main__':unittest.main()
