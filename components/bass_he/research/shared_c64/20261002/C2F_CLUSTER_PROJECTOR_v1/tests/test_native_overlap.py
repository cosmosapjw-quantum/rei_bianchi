"""Manufactured native-kernel tests; no physical Hamiltonian or prior suite."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from native_overlap import NativeOverlapError, identity, overlap

STRICT = ROOT / "native" / "build-v2b" / "libbass_overlap.so"
DEBUG = ROOT / "native" / "build-debug-v2b" / "libbass_overlap.so"


def scalar_fsum_reference(u, v, w):
    """Independent scalar real arithmetic + math.fsum; no native call/BLAS."""
    result = np.empty((u.shape[1], v.shape[1]), dtype=np.complex128)
    for a in range(u.shape[1]):
        for b in range(v.shape[1]):
            re, im = [], []
            for i in range(u.shape[0]):
                ar, ai = float(u[i,a].real), float(u[i,a].imag)
                br, bi = float(v[i,b].real), float(v[i,b].imag)
                re.append((ar*br + ai*bi) * float(w[i]))
                im.append((ar*bi - ai*br) * float(w[i]))
            result[a,b] = complex(math.fsum(re), math.fsum(im))
    return result


class NativeOverlapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["OMP_NUM_THREADS"] = "1"
        os.environ["OMP_DYNAMIC"] = "FALSE"
        for library in (STRICT, DEBUG):
            if not library.is_file():
                raise RuntimeError("strict and debug native builds are required before tests")

    def setUp(self):
        self.u = np.array([[1+2j, 0], [2-1j, 1j], [-1+0.5j, 2]], dtype=np.complex128)
        self.v = np.array([[3-1j], [1+4j], [-2j]], dtype=np.complex128)
        self.w = np.array([0.5, 2, 1.25], dtype=np.float64)

    def test_identity_matches_compiled_source_and_binary(self):
        for library in (STRICT, DEBUG):
            info = identity(library)
            self.assertEqual(info["abi"], 1)
            self.assertEqual(info["verified_library_sha256"], hashlib.sha256(library.read_bytes()).hexdigest())
            self.assertEqual(info["verified_source_sha256"], hashlib.sha256((ROOT / "native/weighted_overlap.f90").read_bytes()).hexdigest())
            self.assertFalse(info["runtime_dynamic"])
            self.assertIn("-ffp-contract=off", info["flags"])

    def test_analytic_complex_nonuniform_metric(self):
        # Hand-evaluated dyadic products: exact in binary64.
        expected = np.array([[-4.75+17.0j], [8.0-7.0j]], dtype=np.complex128)
        for library in (STRICT, DEBUG):
            np.testing.assert_array_equal(overlap(self.u,self.v,self.w,library=library), expected)

    def test_cancellation_across_tiles(self):
        v = np.tile(np.array([1e16+1e16j, 1+2j, -1e16-1e16j], dtype=np.complex128), 342).reshape(-1,1)
        u = np.ones_like(v)
        w = np.ones(len(v), dtype=np.float64)
        expected = np.array([[342+684j]], dtype=np.complex128)
        for library in (STRICT, DEBUG):
            np.testing.assert_array_equal(overlap(u,v,w,library=library), expected)

    def test_lane_compensations_are_not_prerounded(self):
        # Lane 1 holds 1e16+1, lane 2 holds -1e16. Merging only rounded
        # lane totals would produce zero, while separate corrections give one.
        v = np.zeros((16,1),dtype=np.complex128)
        v[0,0] = 1e16+1e16j; v[1,0] = -1e16-1e16j; v[8,0] = 1+2j
        for library in (STRICT,DEBUG):
            np.testing.assert_array_equal(overlap(np.ones_like(v),v,np.ones(16,dtype=np.float64),library=library),
                                          np.array([[1+2j]],dtype=np.complex128))

    def test_adversarial_mixed_exponent_fsum(self):
        rng = np.random.default_rng(65537)
        re = np.ldexp(rng.choice([-1.,1.],size=(2053,3)),rng.integers(-35,35,size=(2053,3)))
        im = np.ldexp(rng.choice([-1.,1.],size=(2053,3)),rng.integers(-35,35,size=(2053,3)))
        v = (re+1j*im).astype(np.complex128)
        # Cancel the large partial totals exactly and retain sub-unit tails.
        v = np.concatenate([v,-v[::-1],np.array([[.5+.25j,1+2j,-.25+.5j]],dtype=np.complex128)])
        u = np.ones((len(v),1),dtype=np.complex128); w = np.ones(len(v),dtype=np.float64)
        expected = scalar_fsum_reference(u,v,w)
        for library in (STRICT,DEBUG):
            np.testing.assert_array_equal(overlap(u,v,w,library=library),expected)

    def test_random_complex_fsum_parity(self):
        rng = np.random.default_rng(1729)
        u = (rng.normal(size=(517,3)) + 1j*rng.normal(size=(517,3))).astype(np.complex128)
        v = (rng.normal(size=(517,4)) + 1j*rng.normal(size=(517,4))).astype(np.complex128)
        w = np.exp(rng.uniform(-3,3,size=517)).astype(np.float64)
        expected = scalar_fsum_reference(u,v,w)
        results = [overlap(u,v,w,library=library) for library in (STRICT, DEBUG)]
        for result in results:
            np.testing.assert_allclose(result, expected, rtol=2e-15, atol=2e-13)
        np.testing.assert_array_equal(results[0], results[1])

    def test_hermitian_swap_and_gram(self):
        uv = overlap(self.u,self.v,self.w,library=STRICT)
        vu = overlap(self.v,self.u,self.w,library=STRICT)
        np.testing.assert_array_equal(uv, vu.conj().T)
        gram = overlap(self.u,self.u,self.w,library=STRICT)
        np.testing.assert_array_equal(gram, gram.conj().T)
        self.assertTrue(np.all(np.linalg.eigvalsh(gram) > 0))

    def test_noncontiguous_frames_and_weights(self):
        # Reversed rows and strided weights preserve the same weighted sum.
        wbig = np.zeros(6, dtype=np.float64)
        wbig[::2] = self.w
        expected = scalar_fsum_reference(self.u,self.v,self.w)
        np.testing.assert_array_equal(overlap(self.u[::-1],self.v[::-1],wbig[::2][::-1],library=STRICT), expected)

    def test_input_precision_is_explicit(self):
        for u,v,w in ((self.u.astype(np.complex64),self.v,self.w),
                      (self.u,self.v.astype(np.complex64),self.w),
                      (self.u,self.v,self.w.astype(np.float32)),
                      (self.u.real,self.v,self.w), (self.u.tolist(),self.v,self.w)):
            with self.assertRaises(TypeError):
                overlap(u,v,w,library=STRICT)

    def test_invalid_shapes_and_empty_ranks(self):
        for u,v,w in ((self.u.ravel(),self.v,self.w), (self.u,self.v[:2],self.w),
                      (self.u,self.v,self.w[:,None]), (self.u,self.v,self.w[:2]),
                      (self.u[:,:0],self.v,self.w), (self.u[:0],self.v[:0],self.w[:0])):
            with self.assertRaises(ValueError):
                overlap(u,v,w,library=STRICT)

    def test_finite_and_positive_metric_required(self):
        for bad in (0.0, -1.0, np.nan, np.inf):
            w = self.w.copy(); w[1] = bad
            with self.assertRaises(ValueError):
                overlap(self.u,self.v,w,library=STRICT)
        for bad in (complex(np.nan,0), complex(0,np.inf)):
            u = self.u.copy(); u[0,0] = bad
            with self.assertRaises(ValueError):
                overlap(u,self.v,self.w,library=STRICT)

    def test_missing_or_unsupported_thread_settings_fail_closed(self):
        cases = ({"OMP_NUM_THREADS":"", "OMP_DYNAMIC":"FALSE"},
                 {"OMP_NUM_THREADS":"1,4", "OMP_DYNAMIC":"FALSE"},
                 {"OMP_NUM_THREADS":"0", "OMP_DYNAMIC":"FALSE"},
                 {"OMP_NUM_THREADS":"1", "OMP_DYNAMIC":"TRUE"},
                 {"OMP_NUM_THREADS":"1", "OMP_DYNAMIC":""})
        for values in cases:
            with patch.dict(os.environ,values):
                with self.assertRaises(NativeOverlapError):
                    overlap(self.u,self.v,self.w,library=STRICT)

    def test_missing_library_has_no_fallback(self):
        with self.assertRaises(NativeOverlapError):
            overlap(self.u,self.v,self.w,library=None)
        with self.assertRaises(NativeOverlapError):
            overlap(self.u,self.v,self.w,library=ROOT/"native/this-library-does-not-exist.so")

    def test_finite_input_overflow_is_explicit_failure(self):
        u = np.array([[1e308+0j]], dtype=np.complex128)
        v = np.array([[2+0j]], dtype=np.complex128)
        with self.assertRaises(FloatingPointError):
            overlap(u,v,np.ones(1,dtype=np.float64),library=STRICT)

    def test_binary_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            lib = Path(temp) / "libbass_overlap.so"
            shutil.copy2(STRICT,lib)
            shutil.copy2(STRICT.with_suffix(".build.json"),lib.with_suffix(".build.json"))
            with lib.open("ab") as handle:
                handle.write(b"tampered")
            with self.assertRaisesRegex(NativeOverlapError,"identity mismatch"):
                identity(lib)

    def test_flag_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            lib = Path(temp) / "libbass_overlap.so"
            shutil.copy2(STRICT,lib)
            meta = json.loads(STRICT.with_suffix(".build.json").read_text())
            meta["flags"].append("-ffast-math")
            lib.with_suffix(".build.json").write_text(json.dumps(meta))
            with self.assertRaisesRegex(NativeOverlapError,"flags violate"):
                identity(lib)

    def test_one_vs_four_threads_bitwise(self):
        script = r'''import hashlib, numpy as np, sys
from native_overlap import overlap
rng=np.random.default_rng(104729)
u=(rng.normal(size=(1031,5))+1j*rng.normal(size=(1031,5))).astype(np.complex128)
v=(rng.normal(size=(1031,6))+1j*rng.normal(size=(1031,6))).astype(np.complex128)
w=np.exp(rng.uniform(-5,5,size=1031)).astype(np.float64)
print(hashlib.sha256(overlap(u,v,w,library=sys.argv[1]).tobytes(order="C")).hexdigest())
'''
        hashes=[]
        for threads in (1,4):
            env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_DYNAMIC="FALSE",
                       OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONPATH=str(ROOT/"code"))
            hashes.append(subprocess.check_output([sys.executable,"-c",script,str(STRICT)], env=env, text=True).strip())
        self.assertEqual(hashes[0],hashes[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
