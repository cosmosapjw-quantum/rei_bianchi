"""New restart harness checks only; do not replay old checkpoint tests."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import numpy as np
from cold_restart import verify_closure, compare_exact

class HarnessTests(unittest.TestCase):
    def test_dependency_mismatch_fails_before_simulation(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); p=root/'source.py';p.write_text('original')
            pins={'dependency:source.py':hashlib.sha256(p.read_bytes()).hexdigest()}
            self.assertEqual(verify_closure(root,pins),pins)
            p.write_text('changed')
            with self.assertRaisesRegex(ValueError,'DEPENDENCY_MISMATCH'):
                verify_closure(root,pins)
    def test_exact_array_comparison_keeps_even_one_ulp_difference(self):
        a=np.array([0.,1.,2.]);b=a.copy()
        self.assertTrue(compare_exact(a,b)['bitwise_equal'])
        b[1]=np.nextafter(b[1],np.inf)
        r=compare_exact(a,b)
        self.assertFalse(r['bitwise_equal']); self.assertEqual(r['different_entries'],1)
        self.assertGreater(r['max_absolute_difference'],0)
    def test_signed_zero_is_not_bitwise_equal(self):
        self.assertFalse(compare_exact(np.array([0.]),np.array([-0.]))['bitwise_equal'])

if __name__=='__main__':unittest.main()
