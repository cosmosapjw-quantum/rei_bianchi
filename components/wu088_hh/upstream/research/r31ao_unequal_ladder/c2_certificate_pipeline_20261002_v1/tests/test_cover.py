import unittest
from c2_support import ContractError, complete_indices

class ExactCover(unittest.TestCase):
    def test_missing_is_not_zero(self):
        with self.assertRaisesRegex(ContractError, 'missing'):
            complete_indices(list(range(288)), 289)
    def test_duplicate_is_not_coverage(self):
        with self.assertRaisesRegex(ContractError, 'duplicate'):
            complete_indices(list(range(288)) + [287], 289)
    def test_boolean_index_is_not_integer(self):
        with self.assertRaisesRegex(ContractError, 'index'):
            complete_indices([False], 1)
    def test_bounded_single_pass_iterable(self):
        with self.assertRaisesRegex(ContractError, 'count|duplicate'):
            complete_indices((i for i in range(300)), 289)
    def test_exact_cover_accepts_order_independently(self):
        self.assertEqual(complete_indices([2, 0, 1], 3), (0,1,2))
