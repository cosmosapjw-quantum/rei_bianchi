"""Small independent donor/receiver checks; no parameter sweep or benchmark."""
from __future__ import annotations

import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import argparse
from dataclasses import FrozenInstanceError
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
from scipy.integrate import solve_ivp

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT/"src"))
from electron_donor import ElectronDonor, GAMMA_PER_NE
from prepare_donor import write_bundle
from receiver import make_model, augmented_rhs, DEFAULT_NUMERICS, selected_donor

MEASUREMENTS = {}


def fixture(*, unit="cm^-3", frame="proper", zero=False):
    a = np.geomspace(1/21., 1/3., 9)
    volume = a**-3 if frame == "proper" else np.ones_like(a)
    unit_factor = 1 if unit == "cm^-3" else 1e6
    h = np.zeros_like(a) if zero else np.full_like(a, .6)
    he2 = np.zeros_like(a) if zero else np.full_like(a, .2)
    he3 = np.zeros_like(a) if zero else np.full_like(a, .3)
    columns = dict(a=a, nH=2e-7*volume*unit_factor, nHe=1.6e-8*volume*unit_factor,
                   xHII=h, xHeII=he2, xHeIII=he3)
    provenance = dict(kind="manufactured_control", closure="constant ionic fractions for algebraic control",
                      source_sha256=hashlib.sha256(b"HE31_MANUFACTURED_CONSTANT_FRACTIONS").hexdigest())
    return columns, dict(density_unit=unit, density_frame=frame, provenance=provenance)


class Contracts(unittest.TestCase):
    def test_units_comoving_and_helium_census(self):
        query = np.geomspace(1/21., 1/3., 37)
        expected = (2e-7*.6 + 1.6e-8*(.2+2*.3))/query**3
        errors = []
        for unit in ("cm^-3", "m^-3"):
            for frame in ("proper", "comoving_a3"):
                columns, kwargs = fixture(unit=unit, frame=frame)
                d = ElectronDonor.from_arrays(**columns, **kwargs)
                actual = d.density(query)
                error = float(np.max(abs(actual/expected-1)))
                errors.append(error)
                np.testing.assert_allclose(actual, expected, rtol=3e-15, atol=0)
        MEASUREMENTS["units_and_dilution_max_relative_error"] = max(errors)

    def test_zero_neutral_and_endpoint_support(self):
        columns, kwargs = fixture(zero=True)
        d = ElectronDonor.from_arrays(**columns, **kwargs)
        self.assertTrue(np.all(d.density(columns["a"]) == 0))
        self.assertEqual(d.density(columns["a"][0]), 0.)
        self.assertEqual(d.density(np.nextafter(columns["a"][-1], math.inf)), 0.)
        for query in (0., float("nan"), 1/3.+1e-10, 1/21.-1e-10):
            with self.assertRaises(ValueError):
                d.density(query)
        MEASUREMENTS["exact_zero_preserved"] = True

    def test_fraction_and_nucleus_rejection(self):
        columns, kwargs = fixture()
        for key, value in (("xHII", -1e-4), ("xHeIII", .9), ("nH", 0.)):
            changed = {k:v.copy() for k,v in columns.items()}
            changed[key][3] = value
            with self.assertRaises(ValueError):
                ElectronDonor.from_arrays(**changed, **kwargs)
        changed = {k:v.copy() for k,v in columns.items()}
        changed["nH"][3] *= 1.01
        with self.assertRaises(ValueError):
            ElectronDonor.from_arrays(**changed, **kwargs)
        with self.assertRaises(ValueError):
            ElectronDonor.from_arrays(**columns, **dict(kwargs, density_unit="auto"))

    def test_bundle_hash_identity_and_immutable_state(self):
        columns, kwargs = fixture()
        d = ElectronDonor.from_arrays(**columns, **kwargs)
        with self.assertRaises(FrozenInstanceError):
            d._nH0 = 4.
        for arr in (d._a, d._x, d._c, d._comoving_ne):
            with self.assertRaises(ValueError):
                arr.flags.writeable = True
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/"donor"
            write_bundle(p, columns, **kwargs)
            restored = ElectronDonor.load(p/"manifest.json")
            self.assertEqual(restored.identity, d.identity)
            with (p/"history.npz").open("ab") as stream:
                stream.write(b"tamper")
            with self.assertRaises(ValueError):
                ElectronDonor.load(p/"manifest.json")

    def test_fast_path_uses_actual_interval(self):
        a = np.exp(np.array([-3., -2., -1., 0.]) + np.array([0., 8e-11, 0., 0.]))
        columns, kwargs = fixture()
        columns = dict(a=a, nH=2e-7/a**3, nHe=1.6e-8/a**3,
                       xHII=np.array([0., 1., .1, .8]), xHeII=np.zeros(4), xHeIII=np.zeros(4))
        d = ElectronDonor.from_arrays(**columns, **kwargs)
        queries = np.exp(np.array([-2.-2e-11, -2.+4e-11, -1.+1e-11]))
        scalar = np.array([d.density(float(a)) for a in queries])
        vector = d.density(queries)
        np.testing.assert_allclose(scalar, vector, rtol=3e-15, atol=0)
        self.assertTrue(np.all(scalar >= 0))

    def test_actual_donor_roundtrip_and_z2_rejection(self):
        d = ElectronDonor.load(UNIT/"inputs/r15_flrw/manifest.json")
        with np.load(UNIT/"inputs/r15_flrw/history.npz", allow_pickle=False) as raw:
            got = d.density(raw["a"])
            scale = np.maximum(raw["ne_reference"], 1e-30)
            error = float(np.max(abs(got-raw["ne_reference"])/scale))
        self.assertLess(error, 3e-14)
        self.assertEqual(got[0], 0.)
        with self.assertRaises(ValueError):
            d.require_support(1/21., 1/3.)
        MEASUREMENTS["actual_donor_knot_relative_error"] = error
        MEASUREMENTS["actual_donor_z2_extrapolation_rejected"] = True

    def test_collision_only_analytic_optical_depth(self):
        columns, kwargs = fixture()
        d = ElectronDonor.from_arrays(**columns, **kwargs)
        H = 2e-17
        a0, a1 = d.support
        k = GAMMA_PER_NE*(2e-7*.6+1.6e-8*(.2+2*.3))/(H*a0**3)
        xmax = math.log(a1/a0)
        tau = k*(-math.expm1(-3*xmax))/3
        def rhs(x,y):
            g = d.rate(a0*math.exp(x))/H
            return [-.9*g*y[0], g]
        sol = solve_ivp(rhs,(0,xmax),[1.,0.],method="DOP853",rtol=3e-12,atol=1e-14)
        self.assertTrue(sol.success)
        error = float(np.max(abs(sol.y[:,-1]-[math.exp(-.9*tau),tau])))
        self.assertLess(error, 3e-11)
        MEASUREMENTS["collision_only_max_abs_error"] = error
        MEASUREMENTS["collision_only_diagnostic_tau"] = tau

    def test_gamma_only_rhs_and_target_clock(self):
        manifest = UNIT/"inputs/r15_flrw/manifest.json"
        common = dict(case_id="contract", Sigma_F=.003, P_m=.0003, P_r=-.001,
                      z_end=4., backend="reference", donor_manifest=str(manifest),
                      donor_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                      numerics=dict(DEFAULT_NUMERICS))
        on, donor, _ = make_model(dict(common, opacity="on"))
        off, _, _ = make_model(dict(common, opacity="off"))
        y = on.initial_state()
        x = .6
        expected_field = on.fields(x,y)
        g = expected_field["GammaT"]/expected_field["H"]
        delta = on.rhs(x,y)-off.rhs(x,y)
        n = on.n
        expected = np.zeros_like(y)
        expected[4:4+n] = -g*on.thomson*y[4:4+n]
        expected[4+n:4+2*n] = -g*on.thomson*y[4+n:4+2*n]
        np.testing.assert_allclose(delta, expected, rtol=0., atol=2e-18)
        calls = [0]
        original = on.momentum.moments
        def counted(eta,b):
            calls[0] += 1
            return original(eta,b)
        on.momentum.moments = counted
        derivative = augmented_rhs(on, donor)(x,np.r_[y,0.])
        self.assertEqual(calls[0],1)
        # Three elementary binary64 operations reconstruct Gamma/H from
        # the original Href/H derivative. Bound this rounding path, not an
        # unrelated absolute tolerance on an opacity of arbitrary size.
        self.assertLessEqual(abs(derivative[-1]-g),4*np.finfo(float).eps*abs(g))
        MEASUREMENTS["gamma_only_rhs_max_abs_error"] = float(np.max(abs(delta-expected)))
        MEASUREMENTS["fv_moment_calls_per_augmented_rhs"] = calls[0]
        MEASUREMENTS["diagnostic_tau_rhs_relative_error"] = abs(float(derivative[-1]/g-1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--only", help="run one affected contract after a correction")
    args = parser.parse_args()
    suite = (unittest.TestSuite([Contracts(args.only)]) if args.only else
             unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = dict(status="PASS_SCOPED" if result.wasSuccessful() else "FAIL",
        tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        measurements=MEASUREMENTS, scope="donor contracts, analytic scalar collision and same-state full40 RHS",
        physical_sweep_runs=0, benchmark_runs=0,
        implementation_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((UNIT/"src").glob("*.py"))},
        test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        python=sys.version, numpy=np.__version__)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt["measurements"],indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
