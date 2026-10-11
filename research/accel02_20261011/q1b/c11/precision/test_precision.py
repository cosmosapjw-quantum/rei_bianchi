from pathlib import Path
import sys
import unittest
import numpy as np
import mpmath as mp
HERE=Path(__file__).resolve().parent
Q1B=HERE.parent.parent
sys.path[:0]=[str(HERE),str(Q1B),str(Q1B.parent/'n1')]
from provider import HistoryProvider
from source_cells import CellSource
from grid_cells import load_grid
from reference_mp import ray,cell_moments
from source_precision import StableCellSource,log_ray,ray_difference

class PrecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=HistoryProvider(r=0.)
        cls.s=CellSource(cls.p,load_grid(Q1B/'GRID_C2.json'))
        cls.stable=StableCellSource(cls.s)
        cls.born=int(np.flatnonzero(cls.s.edges[:-1]==50000.)[0])

    def test_stable_ray_difference_against_80digit_same_formula(self):
        with mp.workdps(80):
            for t0,t1 in [(0.,1e4),(1e15,1e15+1e5)]:
                ref=ray(self.p.background,t0)-ray(self.p.background,t1)
                got=ray_difference(self.p.background,t0,t1)
                self.assertLess(float(abs(mp.mpf(got)-ref)/ref),2e-15)

    def test_direct_birth_offset_preserves_information_lost_in_Q_minus_aN(self):
        with mp.workdps(80):
            got=self.stable.source(1e4)
            refs=cell_moments(self.s,1e4,self.born)
            for name,ref in zip(['N','Q_eV','D_eV'],refs):
                self.assertLess(float(abs(mp.mpf(got[name][0,self.born])-ref)/ref),1e-11)
            lossy=got['Q_eV'][0,self.born]-50000*got['N'][0,self.born]
            self.assertGreater(float(abs(mp.mpf(lossy)-refs[2])/refs[2]),1e-7)

    def test_nonflrw_is_refused_explicitly(self):
        class Other:pass
        other=Other();other.provider=Other();other.provider.r=.001
        with self.assertRaisesRegex(ValueError,'FLRW_ONLY'):
            StableCellSource(other)

if __name__=='__main__':unittest.main()
