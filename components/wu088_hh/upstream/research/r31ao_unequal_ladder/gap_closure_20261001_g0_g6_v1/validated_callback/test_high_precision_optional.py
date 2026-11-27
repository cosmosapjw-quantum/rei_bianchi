"""Independent point checks only; they never certify a ball enclosure.

Not run in the authoring environment because mpmath is unavailable.
"""
import unittest
try:
    import mpmath as mp
except ImportError:
    mp=None


@unittest.skipIf(mp is None,'mpmath unavailable; not an acquired verification result')
class HighPrecisionSynthetic(unittest.TestCase):
    def setUp(self):
        mp.mp.dps=80

    def moment(self,k,sigma,s,r=0):
        h=mp.mpf(k)/2
        return ((2*sigma)**h*mp.gamma(h+mp.mpf('1.5'))/mp.gamma(mp.mpf('1.5'))
                *mp.rf(-h,r)/mp.rf(mp.mpf('1.5'),r)*(-1/(2*sigma))**r
                *mp.hyp1f1(-h+r,mp.mpf('1.5')+r,-s/(2*sigma)))

    def test_real_defining_integral(self):
        sigma,s=mp.mpf('0.5'),mp.mpf(1)/3
        d=mp.sqrt(s)
        for k in (1,3,5):
            f=lambda r:r**(k+1)*(mp.exp(-(r-d)**2/(2*sigma))-mp.exp(-(r+d)**2/(2*sigma)))
            independent=mp.sqrt(2/mp.pi)/(2*mp.sqrt(sigma)*d)*mp.quad(f,[0,1,3,mp.inf])
            self.assertLess(abs(independent-self.moment(k,sigma,s)),mp.mpf('1e-60'))

    def test_low_k_closed_form(self):
        sigma,s=mp.mpf('0.5'),mp.mpf(2)/3
        closed=mp.sqrt(2*sigma/mp.pi)*mp.exp(-s/(2*sigma))+(mp.sqrt(s)+sigma/mp.sqrt(s))*mp.erf(mp.sqrt(s/(2*sigma)))
        self.assertLess(abs(closed-self.moment(1,sigma,s)),mp.mpf('1e-65'))

    def test_complex_derivative(self):
        sigma=mp.mpc(1,mp.mpf(1)/4)
        s=mp.mpc(mp.mpf(1)/3,mp.mpf(2)/5)
        for k in (1,3,5,7):
            for r in (1,2):
                derivative=mp.diff(lambda z:self.moment(k,sigma,z),s,r)
                self.assertLess(abs(derivative-self.moment(k,sigma,s,r)),mp.mpf('1e-60'))


if __name__=='__main__': unittest.main(verbosity=2)
