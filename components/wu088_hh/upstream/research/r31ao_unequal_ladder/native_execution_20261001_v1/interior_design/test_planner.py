import unittest
from fractions import Fraction as Q
import planner as p


class DomainTests(unittest.TestCase):
    def test_full_W3_exact_axis_coverage(self):
        axis=p.geometric_axis('1/256',str(1<<192))
        self.assertEqual(len(axis),200)
        self.assertEqual(sum((r-l for l,r in axis),Q(0)),Q(1<<192)-Q(1,256))
        self.assertTrue(all(axis[i][1]==axis[i+1][0] for i in range(len(axis)-1)))

    def test_final_partial_tile_and_caps(self):
        self.assertEqual(p.geometric_axis('1','5'),[(Q(1),Q(2)),(Q(2),Q(4)),(Q(4),Q(5))])
        for lo,hi in (('0','1'),('1','1'),('1/3','1')):
            with self.assertRaises(ValueError):p.geometric_axis(lo,hi)
        with self.assertRaises(ValueError):p.geometric_axis('1',str(1<<100),4)

    def test_inverse_bound_independent_exact_complex_samples(self):
        for a in (Q(1,500),Q(3)):
            for lo,hi,y in ((Q(1),Q(2),Q(1,4)),(Q(1,256),Q(1<<192),Q(1,1024))):
                lower=p.inverse_real_lower(a,lo,hi,y)
                self.assertGreater(lower,0)
                for x in (lo,(lo+hi)/2,hi):
                    for imaginary in (-y,Q(0),y):
                        real=(a+x)/((a+x)**2+imaginary**2)
                        self.assertGreaterEqual(real,lower)

    def test_padded_pilot_domains_remain_positive(self):
        for _,w in p.PILOTS:
            evidence=p.complex_domain(Q(1,500),Q(1,500),w)
            self.assertTrue(evidence['proved_domain_margin_sufficient_for_this_product'])

    def test_partition_area_additivity_without_endpoint_duplication(self):
        tx=p.geometric_axis('1/4','8');ux=p.geometric_axis('1/2','4')
        area=sum(((tr-tl)*(ur-ul) for tl,tr in tx for ul,ur in ux),Q(0))
        self.assertEqual(area,(8-Q(1,4))*(4-Q(1,2)))
        endpoint=Q(1,16)
        self.assertNotEqual(area+endpoint,area+len(tx)*len(ux)*endpoint)


if __name__=='__main__':unittest.main(verbosity=2)
