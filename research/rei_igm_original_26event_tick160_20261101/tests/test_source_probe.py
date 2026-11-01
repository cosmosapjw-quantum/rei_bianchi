"""Tests of the read-only 26-event source-probe's invariants and fail-closed guards."""
import importlib.util
from pathlib import Path
import struct, hashlib, json, tempfile, unittest
import numpy as np

P = Path(__file__).resolve().parents[1] / "source_26events.py"
spec = importlib.util.spec_from_file_location("source_26events", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class SourceProbeTests(unittest.TestCase):
    def test_stoichiometric_nuclei(self):
        f = np.zeros((3, 5, 5))
        f[:,1,0] = [2.0, 0.0, 1.0]
        f[:,3,2] = 4.0
        f[:,4,3] = 5.0
        dot = m.stoich_flux(f)
        self.assertTrue(np.array_equal(dot[:,:2].sum(axis=1), np.zeros(3)))
        self.assertTrue(np.array_equal(dot[:,2:].sum(axis=1), np.zeros(3)))
        self.assertEqual(float(dot[0,1]+dot[0,3]+2*dot[0,4]),11.0)

    def test_positive_nuclei_representative(self):
        lo = np.asarray([[.25,.25,.1,.1,.1]],float)
        hi = np.asarray([[.45,.45,.3,.3,.3]],float)
        out = m.representative(lo,hi,np.asarray([.8]),np.asarray([.6]))
        self.assertTrue(np.all(out >= lo-1e-12))
        self.assertTrue(np.all(out <= hi+1e-12))
        self.assertAlmostEqual(float(out[0,:2].sum()),.8)
        self.assertAlmostEqual(float(out[0,2:].sum()),.6)

    def test_infeasible_nuclei_rejected(self):
        lo = np.full((1,5),.2)
        hi = np.full((1,5),.25)
        with self.assertRaises(ValueError):
            m.representative(lo,hi,np.asarray([1.0]),np.asarray([.6]))

    def test_state_magic_nonmatch_is_not_a_state(self):
        self.assertIsNone(m.unpack_state(b"not a source state"))

    def test_original_archive_hash_fail_closed(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"wrong history");f.flush()
            with self.assertRaises(ValueError):
                m.archived_tick160(f.name)

    def test_model_data_not_claimed_as_canonical(self):
        self.assertEqual(m.TICK,160)
        self.assertEqual(m.TOTAL,131072)
        self.assertEqual(m.NODE_COUNT,46080)
        self.assertEqual(len(m.LANES),3)

    def test_percentiles_moment(self):
        got=m.percentile(np.asarray([1.,2.,3.]))
        self.assertEqual(got["50"],2.)
        with self.assertRaises(ValueError):
            m.percentile(np.asarray([float("nan")]))

if __name__ == "__main__":
    unittest.main()
