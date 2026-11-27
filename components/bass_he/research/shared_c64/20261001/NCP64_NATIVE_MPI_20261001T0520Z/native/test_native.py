#!/usr/bin/env python3
"""Kernel indexing, arithmetic, input contract, and thread determinism tests.

These tests do not solve a physical eigenproblem or assert NCP speedup.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from native_backend import element_blocks, native_info, prepare_element_kernel


def fixture(nq=7, na=4, nk=11, nl=6):
    rng = np.random.default_rng(591602)
    B = rng.normal(size=(nq, na))
    gaunt = rng.normal(size=(nk, nl, nl))  # deliberately not symmetric
    gaunt[rng.random(gaunt.shape) < .45] = 0.
    vl = rng.normal(size=(nq, nk))
    weights = rng.normal(size=nq)  # negative weights are algebraically valid
    kin = rng.normal(size=(na, na))
    cent = rng.normal(size=(na, na))
    ls = np.arange(nl, dtype=np.int64)*2
    return B, gaunt, vl, weights, kin, cent, ls


def reference(inputs):
    B, gaunt, vl, weights, kin, cent, ls = inputs
    vll = np.einsum("qk,kij->qij", vl, gaunt, optimize=True)
    blocks = np.einsum("qa,qij,qb,q->iajb", B, vll, B, weights, optimize=True)
    for i, l in enumerate(ls):
        blocks[i, :, i, :] += kin + l*(l+1)*cent
    return blocks


class NativeTests(unittest.TestCase):
    def test_nonsymmetric_indexing_and_tiny_shapes(self):
        for shape in [(1, 1, 1, 1), (7, 4, 11, 6), (14, 5, 193, 97)]:
            inputs = fixture(*shape)
            actual = element_blocks(*inputs)
            expected = reference(inputs)
            scale = max(1., float(np.max(np.abs(expected))))
            self.assertLess(float(np.max(np.abs(actual-expected)))/scale, 2e-14)
            self.assertEqual(actual.shape, expected.shape)
            self.assertTrue(actual.flags.c_contiguous)

    def test_noncontiguous_valid_inputs(self):
        inputs = fixture()
        views = []
        for arr in inputs:
            enlarged = np.empty(tuple(n*2 for n in arr.shape), dtype=arr.dtype)
            view = enlarged[tuple(slice(None, None, 2) for _ in arr.shape)]
            view[...] = arr
            views.append(view)
        np.testing.assert_array_equal(element_blocks(*views), element_blocks(*inputs))

    def test_prepared_inputs_are_owned_and_reused(self):
        B, gaunt, vl, weights, kin, cent, ls = fixture()
        expected = element_blocks(B, gaunt, vl, weights, kin, cent, ls)
        prepared = prepare_element_kernel(B, gaunt, ls)
        B[:] = np.nan
        gaunt[:] = np.nan
        ls[:] = -1
        np.testing.assert_array_equal(prepared.blocks(vl, weights, kin, cent), expected)
        np.testing.assert_array_equal(prepared.blocks(vl, weights, kin, cent), expected)

    def test_reject_invalid_inputs(self):
        baseline = fixture()
        invalid = []
        x = list(baseline); x[0] = x[0].astype(np.float32); invalid.append((x, TypeError))
        x = list(baseline); x[1] = x[1].copy(); x[1][0,0,0] = np.nan; invalid.append((x, ValueError))
        x = list(baseline); x[2] = x[2][:-1]; invalid.append((x, ValueError))
        x = list(baseline); x[6] = x[6].astype(np.int32); invalid.append((x, TypeError))
        x = list(baseline); x[6] = x[6][::-1]; invalid.append((x, ValueError))
        x = list(baseline); x[0] = x[0][:0]; invalid.append((x, ValueError))
        for values, exception in invalid:
            with self.assertRaises(exception):
                element_blocks(*values)

    def test_thread_count_bitwise_determinism(self):
        identities = []
        for threads in (1, 2, 4):
            environment = {**os.environ, "OMP_NUM_THREADS": str(threads), "OMP_DYNAMIC": "FALSE",
                           "OPENBLAS_NUM_THREADS": "1"}
            completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--fingerprint"],
                                       env=environment, capture_output=True, text=True, check=True)
            result = json.loads(completed.stdout)
            self.assertEqual(result["threads"], threads)
            identities.append(result["sha256"])
        self.assertEqual(len(set(identities)), 1)

    def test_library_sha_rejection(self):
        environment = {**os.environ, "BASS_NATIVE_EXPECTED_SHA256": "0"*64}
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--fingerprint"],
                                   env=environment, capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("SHA-256 differs", completed.stderr)

    def test_missing_build_manifest_rejected(self):
        with tempfile.TemporaryDirectory(prefix="bass-test-missing-manifest-") as temporary:
            library = Path(temporary) / "libbass_element.so"
            shutil.copyfile(native_info()["library_path"], library)
            environment = {**os.environ, "BASS_NATIVE_LIBRARY": str(library)}
            environment.pop("BASS_NATIVE_EXPECTED_SHA256", None)
            completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--fingerprint"],
                                       env=environment, capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("required native build manifest is absent", completed.stderr)


if __name__ == "__main__":
    if "--fingerprint" in sys.argv:
        result = element_blocks(*fixture())
        print(json.dumps({"sha256": hashlib.sha256(result.tobytes()).hexdigest(),
                          "threads": native_info()["openmp_max_threads"]}))
    else:
        print(json.dumps({"native": native_info()}), flush=True)
        unittest.main(verbosity=2)
