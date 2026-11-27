"""Focused manufactured exporter contracts; no original owner execution or ODE."""
import copy
from decimal import Decimal
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

import export_owner as ex


def manufactured_model():
    matrix = np.eye(5, dtype=np.float64)
    matrix[0] = [np.nextafter(0., 1.), -2., -1.e-16, 0., -0.]
    momentum = SimpleNamespace(
        radial_cells=24, angular_cells=12, gauss_order=3,
        _q=np.linspace(.1, 3., 72, dtype=np.float64)[:, None],
        _mu2=np.linspace(.01, .99, 36, dtype=np.float64)[None, :],
        _numbers=np.ones((72, 36), dtype=np.float64), mass=30.,
        reference_energy_norm=123.4, amplitude=-.1)
    momentum._numbers[-1] = 0.
    source = SimpleNamespace(h0=1.e-18, omega_m=.3, omega_r=.0001,
                             omega_lambda=.6999, aref=1./21., href=1.e-16,
                             rhocrit_j_m3=7.e-10)
    return SimpleNamespace(L=8, momentum=momentum, src=source,
                           mat=matrix, mpref=.1*.3/(1./21.)**3)


def manufactured_table():
    coefficients = ex.capture_coefficients(manufactured_model(), .1)
    return ex.seal({
        "schema": ex.SCHEMA, "encoding": ex.ENCODING,
        "fixture": "MANUFACTURED_EXPORT_CONTRACT_ONLY_NOT_AN_ACTUAL_OWNER_EXPORT",
        **coefficients,
        "provenance": {
            "loader_sha256": ex.LOADER_SHA256, "owner_lock_sha256": ex.LOCK_SHA256,
            "archive_sha256": ex.ARCHIVE_SHA256, "manifest_sha256": ex.MANIFEST_SHA256,
            "terminal_index_sha256": ex.INDEX_SHA256,
            "owner_files": copy.deepcopy(ex.OWNER_FILES),
            "case_identity": {"case_id": "manufactured",
                "npz_sha256": "0"*64, "receipt_sha256": "1"*64,
                "terminal_state_sha256": "2"*64,
                "amplitude_exact_decimal": coefficients["constants"]["amplitude"]}},
        "HH_R10": "OFF", "production_admission": "NOT_ISSUED"})


class ExportContracts(unittest.TestCase):
    def test_exact_binary64_capture_preserves_source_and_signed_matrix(self):
        model = manufactured_model()
        arrays = [model.momentum._q, model.momentum._mu2, model.momentum._numbers, model.mat]
        before = [a.tobytes() for a in arrays]
        for array in arrays:
            array.flags.writeable = False
        table = ex.capture_coefficients(model, .1)
        self.assertEqual(before, [a.tobytes() for a in arrays])
        self.assertEqual(table["arrays"]["q"][0], str(Decimal.from_float(.1)))
        self.assertNotEqual(table["arrays"]["q"][0], str(Decimal.from_float(.1**2)))
        self.assertEqual(table["arrays"]["M"][0][0], str(Decimal.from_float(np.nextafter(0., 1.))))
        self.assertLess(Decimal(table["arrays"]["M"][0][2]), 0)
        self.assertEqual(table["arrays"]["M"][0][4], "-0")
        for name, array in zip(("q", "mu2", "numbers", "M"), arrays):
            recovered = np.asarray(table["arrays"][name], dtype="<f8")
            self.assertEqual(recovered.tobytes(), np.asarray(array, dtype="<f8").tobytes())
        table["profile"]["packet_shape"][0] = 0
        table["array_metadata"]["q"]["shape"][0] = 0
        self.assertEqual(ex.PROFILE["packet_shape"], [72, 36])
        self.assertEqual(ex.SHAPES["q"], [72])

    def test_wrong_profile_shapes_dtypes_and_nonfinite_rejected(self):
        mutations = (
            lambda m: setattr(m, "L", 10),
            lambda m: setattr(m.momentum, "_q", m.momentum._q[:, 0]),
            lambda m: setattr(m.momentum, "_numbers", m.momentum._numbers.astype(np.float32)),
            lambda m: setattr(m, "mat", m.mat.astype(complex)),
            lambda m: m.momentum._numbers.__setitem__((0, 0), np.nan),
            lambda m: setattr(m.src, "h0", np.inf))
        for mutation in mutations:
            with self.subTest(mutation=repr(mutation)):
                model = manufactured_model()
                mutation(model)
                with self.assertRaises(ValueError):
                    ex.capture_coefficients(model, .1)

    def test_nonpositive_constants_and_kinetic_domain_rejected(self):
        mutations = (
            lambda m: setattr(m.momentum, "reference_energy_norm", 0.),
            lambda m: setattr(m.momentum, "mass", -30.),
            lambda m: setattr(m.momentum, "amplitude", 2.1),
            lambda m: m.momentum._q.__setitem__((0, 0), -.1),
            lambda m: m.momentum._mu2.__setitem__((0, 0), 1.1),
            lambda m: m.momentum._numbers.__setitem__((0, 0), -.01),
            lambda m: m.momentum._numbers.fill(0.))
        for mutation in mutations:
            with self.subTest(mutation=repr(mutation)):
                model = manufactured_model()
                mutation(model)
                with self.assertRaises(ValueError):
                    ex.capture_coefficients(model, .1)

    def test_rounded_or_malformed_decimal_strings_rejected(self):
        for invalid in ("0.1", "NaN", "Infinity", "1e1000", "-0.0", 1., complex(1)):
            with self.subTest(value=repr(invalid)), self.assertRaises(ValueError):
                ex._binary64_decimal(invalid)
        self.assertEqual(ex._binary64_decimal("-0").as_tuple().sign, 1)

    def test_outer_array_and_raw_byte_hashes_are_all_checked(self):
        table = manufactured_table()
        table["arrays"]["q"][0] = "1"
        with self.assertRaisesRegex(ValueError, "TABLE_HASH"):
            ex.validate_table(table)
        with self.assertRaisesRegex(ValueError, "DECIMAL_ARRAY_HASH"):
            ex.validate_table(ex.seal(table))
        table["array_metadata"]["q"]["exact_decimal_json_sha256"] = hashlib.sha256(
            ex.canonical(table["arrays"]["q"])).hexdigest()
        with self.assertRaisesRegex(ValueError, "BINARY64_ARRAY_HASH"):
            ex.validate_table(ex.seal(table))

    def test_stale_provenance_and_case_binding_fail_closed(self):
        mutations = (
            lambda t: t["provenance"].__setitem__("loader_sha256", "0"*64),
            lambda t: t["provenance"]["owner_files"].__setitem__("pilot.py", "0"*64),
            lambda t: t["provenance"]["case_identity"].__setitem__("case_id", "../outside"),
            lambda t: t["provenance"]["case_identity"].__setitem__("case_id", ".."),
            lambda t: t["provenance"]["case_identity"].__setitem__("npz_sha256", "missing"),
            lambda t: t["provenance"]["case_identity"].__setitem__("amplitude_exact_decimal", "0"),
            lambda t: t.__setitem__("HH_R10", "ON"),
            lambda t: t.__setitem__("production_admission", "ISSUED"))
        valid = manufactured_table()
        self.assertTrue(ex.validate_table(valid))
        for mutation in mutations:
            with self.subTest(mutation=repr(mutation)):
                table = copy.deepcopy(valid)
                mutation(table)
                with self.assertRaises(ValueError):
                    ex.validate_table(ex.seal(table))

    def test_stale_loader_rejected_before_import_and_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            loader = Path(tmp) / ex.LOADER_REL
            loader.parent.mkdir(parents=True)
            loader.write_text("raise RuntimeError('MUST_NEVER_EXECUTE')\n")
            with self.assertRaisesRegex(ValueError, "SOURCE_SHA256_MISMATCH"):
                ex._load_pinned_loader(tmp)
            link = Path(tmp) / "loader_link.py"
            link.symlink_to(loader)
            with self.assertRaisesRegex(ValueError, "SYMLINK_SOURCE_REJECTED"):
                ex._checked_file(link, ex.sha256(loader))

    def test_create_only_write_and_exact_readback(self):
        table = manufactured_table()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "table.json"
            receipt = ex.write_export(path, table)
            self.assertEqual(ex.load_export(path), table)
            self.assertEqual(receipt["file_sha256"], ex.sha256(path))
            with self.assertRaises(FileExistsError):
                ex.write_export(path, table)

    def test_request_uses_exact_original_initial_state_and_existing_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "manufactured.npz"
            x = np.linspace(0., 1., 65)
            state = np.arange(8*65, dtype=np.float64).reshape(8, 65) / 10.
            np.savez(raw, x=x, state=state)
            table = manufactured_table()
            case = table["provenance"]["case_identity"]
            case["npz_path"], case["npz_sha256"] = raw.name, ex.sha256(raw)
            table = ex.seal(table)
            request = ex.prepare_request(table, tmp)
            self.assertEqual(request["initial"]["x"], "0")
            self.assertEqual(request["initial"]["state"], request["predictor"]["state"][0])
            self.assertEqual(request["predictor"]["state"][1][3], ex.exact_decimal(state[3, 1]))
            self.assertEqual(len(request["predictor"]["x"]), 2)
            self.assertEqual(len(ex.prepare_request(table, tmp, 65)["predictor"]["x"]), 65)
            receipt = ex.write_request(Path(tmp) / "request.json", request)
            self.assertEqual(receipt["predictor_nodes"], 2)
            for count in (0, 1, 66, True, 2.5):
                with self.subTest(count=count), self.assertRaises(ValueError):
                    ex.prepare_request(table, tmp, count)
            np.savez(raw, x=x+.1, state=state)
            with self.assertRaisesRegex(ValueError, "SOURCE_SHA256_MISMATCH"):
                ex.prepare_request(table, tmp)
            table["provenance"]["case_identity"]["npz_sha256"] = ex.sha256(raw)
            with self.assertRaisesRegex(ValueError, "EXACT_ORIGINAL_INITIAL_STATE"):
                ex.prepare_request(ex.seal(table), tmp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
