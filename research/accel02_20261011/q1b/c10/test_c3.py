"""Targeted acceptance of the new nested grid; no old campaigns execute."""
from pathlib import Path
import copy
import tempfile
import unittest
import numpy as np
from c3_grid import build_c3, freeze_c3

HERE = Path(__file__).resolve().parent
Q1B = HERE.parent

class C3GridTests(unittest.TestCase):
    def test_exact_nested_grid_and_physical_edges(self):
        import json
        c2 = json.loads((Q1B/'GRID_C2.json').read_text())
        c3 = build_c3(c2)
        e2, e3 = np.array(c2['q_edges_eV']), np.array(c3['q_edges_eV'])
        self.assertEqual((c3['energy_cells'], c3['angular_ordinates'], c3['total_cells']), (348,2,696))
        np.testing.assert_array_equal(e3[::2], e2)
        np.testing.assert_array_equal(e3[1::2], np.exp(.5*(np.log(e2[:-1])+np.log(e2[1:]))))
        self.assertTrue(np.all(np.diff(e3)>0))
        self.assertEqual(c3['initial_mu'], c2['initial_mu'])
        self.assertEqual(c3['angular_weights'], c2['angular_weights'])
        for edge in [13.60,24.59,54.42,50000.,*c2['initial_UVB_unequal_jump_edges_eV']]:
            self.assertEqual(np.count_nonzero(e3==edge), 1)

    def test_identity_and_member_mismatch_are_rejected(self):
        import json
        c2 = json.loads((Q1B/'GRID_C2.json').read_text())
        altered = copy.deepcopy(c2)
        altered['q_edges_eV'][1] *= 1.0001
        with self.assertRaisesRegex(ValueError, 'IDENTITY'):
            build_c3(altered)
        altered = copy.deepcopy(c2)
        altered['member'] = 'C1'
        with self.assertRaisesRegex(ValueError, 'BASELINE'):
            build_c3(altered)

    def test_freeze_is_create_only_and_roundtrips(self):
        import json
        import sys
        sys.path.insert(0, str(Q1B))
        from grid_cells import load_grid
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)/'GRID_C3.json'
            freeze_c3(Q1B/'GRID_C2.json', dest)
            frozen = dest.read_bytes()
            grid = load_grid(dest)
            self.assertEqual(grid['member'],'C3')
            with self.assertRaises(FileExistsError):
                freeze_c3(Q1B/'GRID_C2.json', dest)
            self.assertEqual(dest.read_bytes(),frozen)

if __name__=='__main__': unittest.main(verbosity=2)
