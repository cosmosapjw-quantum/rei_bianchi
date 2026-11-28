"""Regression for independent review B10; synthetic exact input only."""
import unittest
from fractions import Fraction as F
from exact_gram.engine import sqrt_interval, round_binary64, Limits, ResourceLimit


class ResourceReviewTests(unittest.TestCase):
    def test_perfect_square_shortcut_obeys_work_bit_cap(self):
        with self.assertRaises(ResourceLimit):
            sqrt_interval(F(2**200),limits=Limits(max_work_bits=8))

    def test_small_perfect_square_with_sufficient_budget(self):
        result=sqrt_interval(F(4),limits=Limits(max_work_bits=8))
        self.assertEqual((result.lo,result.hi),(F(2),F(2)))

    def test_binary64_alignment_rejected_before_oversized_shift(self):
        for q in (F(2**200),F(1,2**200)):
            with self.subTest(q=q), self.assertRaisesRegex(ResourceLimit,'alignment'):
                round_binary64(q,limits=Limits(max_work_bits=8))


if __name__=='__main__':unittest.main()
