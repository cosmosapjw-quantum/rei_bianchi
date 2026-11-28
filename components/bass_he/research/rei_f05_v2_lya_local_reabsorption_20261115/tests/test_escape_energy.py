"""Regression for dimensionally consistent escaped photons -> erg checks."""
import csv
import gzip
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

D = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_ots_capture', D / 'capture_original_local_ots.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def box(lo, hi):
    return SimpleNamespace(lo=np.asarray(lo, dtype=float), hi=np.asarray(hi, dtype=float))

class EscapeEnergyCheck(unittest.TestCase):
    def test_converts_photons_to_erg(self):
        factor = m.E_ALPHA_EV * m.EV_ERG
        self.assertTrue(m.escaped_photon_energy_matches(box([2], [3]), box([2*factor], [3*factor])))

    def test_zero_source(self):
        self.assertTrue(m.escaped_photon_energy_matches(box([0], [0]), box([0], [0])))

    def test_dimension_error_with_shared_zero_lower_is_rejected(self):
        photons = box([0], [1e57])
        wrong_erg = box([0], [1e57])
        self.assertTrue(m.overlapping(photons, wrong_erg))
        self.assertFalse(m.escaped_photon_energy_matches(photons, wrong_erg))

    def test_wrong_scale_with_shared_zero_lower_is_rejected(self):
        photons = box([0], [1e57])
        wrong_erg = box([0], [2e57*m.E_ALPHA_EV*m.EV_ERG])
        self.assertTrue(m.overlapping(photons, wrong_erg))
        self.assertFalse(m.escaped_photon_energy_matches(photons, wrong_erg))

    def test_nonfinite_is_rejected(self):
        with self.assertRaises(ArithmeticError):
            m.escaped_photon_energy_matches(box([0], [np.inf]), box([0], [1]))

    def test_actual_original_92160_rows_changed_representation_check(self):
        p = D / 'results/REI_ORIGINAL_V2_LYA_LOCAL_H_HEI_FEEDBACK_92160.csv.gz'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),
                         '6acd17f0612738fa2954f3285b92b53d1444d8a4cc020375731d0557c0ba80ae')
        with gzip.open(p, 'rt', newline='') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 92160)
        n = box([float(r['escaped_lo']) for r in rows], [float(r['escaped_hi']) for r in rows])
        e = box([float(r['escape_original_lo']) for r in rows], [float(r['escape_original_hi']) for r in rows])
        self.assertTrue(m.escaped_photon_energy_matches(n, e))
        max_relative = max(float(np.max(np.abs(nv*m.E_ALPHA_EV*m.EV_ERG-ev) /
                                      np.maximum(np.abs(ev), 1e-280)))
                           for nv, ev in ((n.lo, e.lo), (n.hi, e.hi)))
        print(json.dumps({'changed_check_original_rows': len(rows),
                          'max_scaled_photon_energy_representation_error': max_relative,
                          'full_native_source_solver_rerun': False}, sort_keys=True))

if __name__ == '__main__':
    unittest.main()
