import sys, unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hh_f03_binding import evaluate

MODEL={'n_h_cm3':'1','n_he_cm3':'1','kb_erg_k':'1','chi_erg':'10'}
def state(T='10000',h='0.2',he1='0.3',he2='0.1'):
    P=F(2)+F(h)+F(he1)+2*F(he2)
    # Test fixtures below are terminating decimal rationals.
    from decimal import Decimal as D, localcontext
    with localcontext() as c:
        c.prec=120
        u=F(3,2)*P*F(T)
        us=str(D(u.numerator)/D(u.denominator))
    return [h,he1,he2,us,'1','2','3']
def contains(iv,x):return F(iv[0])<=F(x)<=F(iv[1])

class RedGreen(unittest.TestCase):
    def test_seven_coordinate_energy_and_no_photon(self):
        out=evaluate(MODEL,state(T='2000'),'LCS91')
        self.assertIn('rhs',out,'F03-coordinate atomic source is missing')
        self.assertTrue(contains(out['rhs'][0],F(64,100)*F('1e-20')))
        self.assertTrue(contains(out['rhs'][3],-F(64,100)*F('1e-19')))
        self.assertEqual(out['rhs'][4:],[['0','0']]*3)
        self.assertEqual(out['energy_null_coefficient'],'0')
    def test_composition_chain_includes_both_helium_charges(self):
        out=evaluate(MODEL,state(),'LCS91')
        self.assertIn('scalar_gradient',out,'Actual-temperature chain rule missing')
        g=out['scalar_gradient'];self.assertLess(F(g[1][1]),0)
        self.assertLess(F(g[2][1]),0);self.assertGreater(F(g[3][0]),0)
        # Twice the HeII derivative equals the HeIII derivative.
        self.assertLessEqual(2*F(g[1][0]),F(g[2][1]))
        self.assertGreaterEqual(2*F(g[1][1]),F(g[2][0]))
    def test_zero_neutral_has_zero_gradient_but_nonzero_hessian(self):
        out=evaluate(MODEL,state(h='1'),'LCS91')
        self.assertIn('scalar_hessian',out,'Boundary Hessian missing')
        self.assertEqual(out['scalar_gradient'],[['0','0']]*7)
        self.assertGreater(F(out['scalar_hessian'][0][0][0]),0)
    def test_exact_3000_boundary_preserves_value_and_refuses_smooth_jet(self):
        out=evaluate(MODEL,state(T='3000'),'LCS91')
        self.assertEqual(out.get('branch'),'NONSMOOTH_3000K')
        self.assertEqual(out['rate_cm3_s'],['1E-20','1E-20'])
        self.assertIsNone(out['scalar_gradient']);self.assertIsNone(out['scalar_hessian'])
    def test_HH_only_nonzero_eigenvalue_is_nonpositive(self):
        out=evaluate(MODEL,state(),'KS92_corrected_Glover15')
        self.assertIn('HH_only_eigenvalue_per_s',out,'Rank-one contraction missing')
        self.assertLess(F(out['HH_only_eigenvalue_per_s'][1]),0)
        self.assertFalse(out['consumer_admission'])

if __name__=='__main__':unittest.main()
