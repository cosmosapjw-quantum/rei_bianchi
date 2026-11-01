import random, unittest, sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from finite_remainder import finite_source_certificate, exact_delta, exact_remainder, f

class ExactGlobalSourceTest(unittest.TestCase):
    def test_photon_normalization(self):
        q=finite_source_certificate([3,2,4,1],[2,1,3,1],[4,3,5,2]);self.assertEqual(q['p0_sum'],1)
    def test_vanish_at_point(self):
        a=[1,2,3,4];r=finite_source_certificate(a,a,a)
        for p in r['rows']:
            self.assertEqual(p['delta_abs_bound'],0);self.assertEqual(p['remainder_abs_bound'],0)
    def test_zeros_are_exact(self):
        q=finite_source_certificate([0,3,0,10],[0,2,0,9],[0,4,0,11])
        for j in (0,2):
            self.assertEqual(q['rows'][j]['p0'],0)
            self.assertEqual(q['rows'][j]['delta_abs_bound'],0)
            self.assertEqual(q['rows'][j]['remainder_abs_bound'],0)
    def test_bad_denominator_refuses(self):
        with self.assertRaises(ValueError):finite_source_certificate([1,0,0,0],[0,0,0,0],[2,0,0,0])
    def test_out_of_box_refuses(self):
        with self.assertRaises(ValueError):finite_source_certificate([1,2,3,4],[2,2,3,4],[3,3,4,5])
    def test_exact_photon_conservation(self):
        for k in range(25):
            a=[F(k+1+j,3+j) for j in range(4)]
            b=[a[j]*F(50+k+j,50+k+2*j+1) for j in range(4)]
            self.assertEqual(sum(exact_delta(a,b)),0)
            self.assertEqual(sum(exact_remainder(a,b)),0)
    def test_entire_box_rational_corner_bound(self):
        rng=random.Random(42)
        for _ in range(20):
            lo=[F(rng.randint(1,8),11) for _ in range(4)]
            hi=[x+F(rng.randint(1,8),23) for x in lo]
            mid=[(x+y)/2 for x,y in zip(lo,hi)]
            q=finite_source_certificate(mid,lo,hi)
            for m in range(16):
                b=[hi[j] if (m>>j)&1 else lo[j] for j in range(4)]
                dd=exact_delta(mid,b); rr=exact_remainder(mid,b)
                for j,row in enumerate(q['rows']):
                    self.assertLessEqual(abs(dd[j]),row['delta_abs_bound'])
                    self.assertLessEqual(abs(rr[j]),row['remainder_abs_bound'])
                    self.assertLessEqual(row['pmin'],mid[j]/sum(mid)+dd[j]);self.assertLessEqual(mid[j]/sum(mid)+dd[j],row['pmax'])
    def test_random_interior_bound(self):
        lo=[F(1,2),F(3,2),F(1,7),F(1,13)];hi=[F(2),F(5),F(1,2),F(1,3)]
        mid=[(a+b)/2 for a,b in zip(lo,hi)]
        q=finite_source_certificate(mid,lo,hi)
        for n in range(100):
            t=F(n,99);b=[a+t*(c-a) for a,c in zip(lo,hi)]
            for j,rr in enumerate(exact_remainder(mid,b)):
                self.assertLessEqual(abs(rr),q['rows'][j]['remainder_abs_bound'])
    def test_structural_external_zero(self):
        q=finite_source_certificate([4,5,6,0],[3,4,5,0],[6,7,8,0]);self.assertEqual(q['rows'][3]['p0'],0)
    def test_dimensionless_scaling(self):
        a=[1,2,3,4];lo=[.9,1.8,2.7,3.6];hi=[1.1,2.2,3.3,4.4]
        x=finite_source_certificate(a,lo,hi);y=finite_source_certificate([v*1e20 for v in a],[v*1e20 for v in lo],[v*1e20 for v in hi]);
        # Floating-point source bytes are not representation-invariant; check with exact rationals.
        a=list(map(F,[1,2,3,4]));lo=[v*F(9,10) for v in a];hi=[v*F(11,10) for v in a]
        x=finite_source_certificate(a,lo,hi);y=finite_source_certificate([v*10**20 for v in a],[v*10**20 for v in lo],[v*10**20 for v in hi]);
        self.assertEqual(x['rows'][0]['remainder_abs_bound'],y['rows'][0]['remainder_abs_bound'])

if __name__=='__main__':unittest.main()
