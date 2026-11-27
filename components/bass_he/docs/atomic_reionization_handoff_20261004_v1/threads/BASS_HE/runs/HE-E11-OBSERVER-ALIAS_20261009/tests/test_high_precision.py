import unittest
from fractions import Fraction as F
from decimal import Decimal, localcontext
from e11.high_precision import decimal_photo, fraction_to_decimal

class HighPrecisionCheck(unittest.TestCase):
    def test_double_vs_exact_decimal(self):
        weights=(F(2,3),F(1,9),F(2,9))
        gamma=(F(7),F(11),F(13))
        exact=sum((a*b for a,b in zip(weights,gamma)),F(0))
        with localcontext() as c:
            c.prec=110
            rounded=sum((fraction_to_decimal(a,110)*fraction_to_decimal(b,110) for a,b in zip(weights,gamma)), Decimal(0))
            self.assertLess(abs(rounded-fraction_to_decimal(exact,110)),Decimal('1e-90'))
    def test_zero_rate(self):
        row={'x':'0.1','y':'0.05','z':'0.9','nH':'1e-4','nHe':'1e-5'}
        gamma=['0','0','0']
        self.assertEqual(decimal_photo(row,gamma,110),Decimal(0))
if __name__=='__main__': unittest.main()
