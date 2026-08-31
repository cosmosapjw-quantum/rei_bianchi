from __future__ import annotations

import importlib.util
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[3]
STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load_bridge():
    path = STAGE / "analysis/rust_source_bound_thermal.py"
    spec = importlib.util.spec_from_file_location("rei_rust_backend_tests", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RustSourceBoundThermalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bridge = _load_bridge()

    def test_authenticated_runtime_identities_are_exact_and_path_free(self) -> None:
        identity = self.bridge.authenticate_runtime(stage_dir=STAGE)
        self.assertEqual(identity["precision_bits"], 256)
        self.assertEqual(identity["mpfr_version"], "4.2.1")
        self.assertEqual(identity["gmp_version"], "6.3.0")
        self.assertEqual(
            identity["mpfr_sha256"],
            "2156351fa3dedd04a7381c6ac7a8a26efa2d6fb08b80f8a2d644ccdd653710ae",
        )
        self.assertEqual(
            identity["gmp_sha256"],
            "0ccdfb6d6f5c039465f6d002cf7e4c072d48ac6a2cffc8dd6c748dec31592804",
        )
        self.assertEqual(identity["rustc_commit"], "e408947bfd200af42db322daf0fadfe7e26d3bd1")
        self.assertEqual(identity["rustc_host"], "x86_64-unknown-linux-gnu")
        self.assertEqual(identity["pointer_width_bits"], 64)
        self.assertEqual(identity["mpfr_raw_size"], 32)
        self.assertEqual(identity["mpfr_raw_align"], 8)
        self.assertEqual(identity["limb_bits"], 64)
        self.assertFalse(any(key.endswith("_path") for key in identity))

    def test_rustc_locator_relocation_does_not_change_identity(self) -> None:
        expected = self.bridge.authenticate_runtime(stage_dir=STAGE)
        parent = Path("/mnt/data") if Path("/mnt/data").is_dir() else Path(tempfile.gettempdir())
        with tempfile.TemporaryDirectory(prefix="rei-rustc-relocation-", dir=parent) as directory:
            relocated = Path(directory) / "relocated-rustc"
            relocated.symlink_to(self.bridge.resolve_rustc_locator())
            with mock.patch.dict(
                os.environ, {"REI_RUSTC_1_94_1": str(relocated)}, clear=False
            ):
                observed = self.bridge.authenticate_runtime(stage_dir=STAGE)
        self.assertEqual(observed, expected)

    def test_interval_division_rejects_zero_before_a_result_is_returned(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-divide-") as directory:
            backend = self.bridge.build_authenticated_backend(
                stage_dir=STAGE, output_dir=Path(directory)
            )
            with self.assertRaisesRegex(self.bridge.RustBackendError, "ZERO_DIVISOR_INTERVAL"):
                self.bridge.interval_divide((1.0, 1.0), (-1.0, 1.0), backend=backend)

    def test_build_output_inside_any_git_worktree_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            self.bridge.RustBackendError, "BUILD_OUTPUT_INSIDE_GIT_WORKTREE"
        ):
            self.bridge.build_authenticated_backend(
                stage_dir=STAGE, output_dir=STAGE / "forbidden-build"
            )

    def test_two_external_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-build-a-") as first, tempfile.TemporaryDirectory(
            prefix="rei-build-b-"
        ) as second:
            one = self.bridge.build_authenticated_backend(
                stage_dir=STAGE, output_dir=Path(first)
            )
            two = self.bridge.build_authenticated_backend(
                stage_dir=STAGE, output_dir=Path(second)
            )
            self.assertEqual(one.receipt.artifact_sha256, two.receipt.artifact_sha256)
            self.assertEqual(one.receipt.canonical_bytes(), two.receipt.canonical_bytes())
            self.assertEqual(one.artifact_path.read_bytes(), two.artifact_path.read_bytes())
            self.assertFalse(any(key.endswith("_path") for key in one.receipt.to_mapping()))

    def test_public_api_cannot_construct_or_retarget_a_capability(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-capability-") as directory:
            backend = self.bridge.build_authenticated_backend(
                stage_dir=STAGE, output_dir=Path(directory)
            )
            with self.assertRaisesRegex(
                self.bridge.RustBackendError, "BACKEND_CAPABILITY_FACTORY_REQUIRED"
            ):
                self.bridge.AuthenticatedBackend(backend.artifact_path, backend.receipt)

            # Replace the directory entry atomically.  Truncating an already
            # dlopen'ed inode can SIGBUS at interpreter teardown and would test
            # the loader's mmap lifetime rather than our hash guard.
            replacement = backend.artifact_path.with_name("replacement.so")
            replacement.write_bytes(b"not an ELF artifact")
            os.replace(replacement, backend.artifact_path)
            with self.assertRaisesRegex(
                self.bridge.RustBackendError, "BACKEND_ARTIFACT_HASH_MISMATCH"
            ):
                self.bridge.interval_divide((1.0, 1.0), (2.0, 2.0), backend=backend)

    def test_process_boundary_claim_is_explicitly_not_overstated(self) -> None:
        self.assertEqual(
            self.bridge.PROCESS_BOUNDARY_BLOCKER,
            "RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING",
        )
        self.assertEqual(
            self.bridge.PRESTART_RUNTIME_BLOCKER,
            "BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED",
        )
        self.assertIn("not a hostile same-process boundary", self.bridge.__doc__)

    def test_native_linkage_is_mpfr_gmp_and_not_python(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-linkage-") as directory:
            backend = self.bridge.build_authenticated_backend(
                stage_dir=STAGE, output_dir=Path(directory)
            )
            completed = subprocess.run(
                ("ldd", str(backend.artifact_path)),
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("libmpfr.so.6", completed.stdout)
        self.assertIn("libgmp.so.10", completed.stdout)
        self.assertNotIn("libpython", completed.stdout.lower())

    def test_python_layer_contains_no_jax_or_numerical_fallback(self) -> None:
        bridge_source = (STAGE / "analysis/rust_source_bound_thermal.py").read_text(
            encoding="utf-8"
        )
        model_source = (REPO / "src/rei_bianchi/joint_implicit_remainder.py").read_text(
            encoding="utf-8"
        )
        rust_source = (STAGE / "rust/source_bound_thermal.rs").read_text(encoding="utf-8")
        for forbidden in ("import numpy", "import jax", "decimal", "Fraction", "linalg"):
            self.assertNotIn(forbidden, bridge_source)
            self.assertNotIn(forbidden, model_source)
        self.assertNotIn("f64::exp", rust_source)
        self.assertNotIn("f64::ln", rust_source)
        self.assertIn("MPFR_RNDD", rust_source)
        self.assertIn("MPFR_RNDU", rust_source)

    def test_rustc_is_hash_admitted_before_it_can_execute(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-hostile-rustc-") as directory:
            root = Path(directory)
            marker = root / "executed"
            hostile = root / "rustc"
            hostile.write_text(
                f"#!/bin/sh\nprintf executed > {marker}\nprintf 'release: 1.94.1\\ncommit-hash: fake\\nhost: x86_64-unknown-linux-gnu\\n'\n",
                encoding="utf-8",
            )
            hostile.chmod(0o755)
            with mock.patch.dict(
                os.environ, {"REI_RUSTC_1_94_1": str(hostile)}, clear=False
            ):
                with self.assertRaisesRegex(
                    self.bridge.RustBackendError,
                    "PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED",
                ):
                    self.bridge.authenticate_runtime(stage_dir=STAGE)
            self.assertFalse(marker.exists(), "untrusted compiler ran before hash admission")

    def test_mpfr_hash_is_admitted_before_any_dynamic_load(self) -> None:
        real_sha256 = self.bridge._sha256

        def drifting_sha(path: Path) -> str:
            if Path(path).resolve() == self.bridge.MPFR.resolve():
                return "0" * 64
            return real_sha256(Path(path))

        with mock.patch.object(self.bridge, "_sha256", side_effect=drifting_sha), mock.patch.object(
            self.bridge,
            "_runtime_versions",
            side_effect=AssertionError("MPFR was loaded before identity admission"),
        ):
            with self.assertRaisesRegex(
                self.bridge.RustBackendError,
                "PREAUTH_DYNAMIC_LIBRARY_IDENTITY_NOT_ESTABLISHED",
            ):
                self.bridge.authenticate_runtime(stage_dir=STAGE)

    def test_mpfr_transitive_closure_is_admitted_before_any_dynamic_load(self) -> None:
        real_sha256 = self.bridge._sha256
        libc = self.bridge._RUNTIME_ELF_PATHS["libc.so.6"]

        def drifting_sha(path: Path) -> str:
            if Path(path).resolve() == libc:
                return "0" * 64
            return real_sha256(Path(path))

        with mock.patch.object(self.bridge, "_sha256", side_effect=drifting_sha), mock.patch.object(
            self.bridge,
            "_runtime_versions",
            side_effect=AssertionError("native closure loaded before identity admission"),
        ):
            with self.assertRaisesRegex(
                self.bridge.RustBackendError,
                "PREAUTH_DYNAMIC_LIBRARY_DEPENDENCY_IDENTITY_NOT_ESTABLISHED",
            ):
                self.bridge.authenticate_runtime(stage_dir=STAGE)

    def test_artifact_runtime_closure_binds_transitive_libs_and_interpreter(self) -> None:
        artifact = Path(
            "/workspace/scratch/6f83d977af18/build/rei-source-bound-rust-a/"
            "librei_source_bound_thermal.so"
        )
        if not artifact.is_file() or hashlib.sha256(artifact.read_bytes()).hexdigest() != (
            "a563eec77de3e0bfa55df454b4ec4cfdc317a1feb4cf2074385719ebdcca32ef"
        ):
            self.skipTest("authoritative external artifact is unavailable")
        closure = dict(self.bridge._artifact_dependencies(artifact))
        self.assertEqual(
            set(closure),
            {
                "ELF_INTERPRETER",
                "libc.so.6",
                "libgcc_s.so.1",
                "libgmp.so.10",
                "libmpfr.so.6",
            },
        )
        self.assertEqual(
            closure["ELF_INTERPRETER"],
            "6222a16be7f2d458d6870efe6e715fc0c8d45766fb79cf7dcc3125538d703e28",
        )

    def test_transitive_dependency_drift_is_rejected_before_native_load(self) -> None:
        artifact = Path(
            "/workspace/scratch/6f83d977af18/build/rei-source-bound-rust-a/"
            "librei_source_bound_thermal.so"
        )
        if not artifact.is_file() or hashlib.sha256(artifact.read_bytes()).hexdigest() != (
            "a563eec77de3e0bfa55df454b4ec4cfdc317a1feb4cf2074385719ebdcca32ef"
        ):
            self.skipTest("authoritative external artifact is unavailable")
        real_sha256 = self.bridge._sha256
        libc = self.bridge._RUNTIME_ELF_PATHS["libc.so.6"]

        def drifting_sha(path: Path) -> str:
            if Path(path).resolve() == libc:
                return "0" * 64
            return real_sha256(Path(path))

        with mock.patch.object(self.bridge, "_sha256", side_effect=drifting_sha), mock.patch.object(
            self.bridge.ctypes,
            "CDLL",
            side_effect=AssertionError("native object loaded before closure admission"),
        ):
            with self.assertRaisesRegex(
                self.bridge.RustBackendError,
                "BACKEND_DEPENDENCY_HASH_MISMATCH: libc.so.6",
            ):
                self.bridge._load_library(artifact)

    def test_fixed_tool_is_hash_admitted_before_subprocess_launch(self) -> None:
        real_sha256 = self.bridge._sha256

        def drifting_sha(path: Path) -> str:
            if Path(path).resolve() == self.bridge.GIT.resolve():
                return "0" * 64
            return real_sha256(Path(path))

        with mock.patch.object(self.bridge, "_sha256", side_effect=drifting_sha), mock.patch.object(
            self.bridge.subprocess, "run", side_effect=AssertionError("tool executed")
        ):
            with self.assertRaisesRegex(
                self.bridge.RustBackendError,
                "PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED",
            ):
                self.bridge._run((str(self.bridge.GIT), "--version"))

    def test_load_bearing_factory_cannot_run_without_runtime_observer(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rei-observer-required-") as directory, mock.patch.object(
            self.bridge,
            "_prepare_runtime_authority",
            side_effect=self.bridge.RuntimeClosureError(
                "RUNTIME_OBSERVATION_CAPABILITY_REQUIRED"
            ),
        ), mock.patch.object(
            self.bridge,
            "authenticate_runtime",
            side_effect=AssertionError("unaudited production path reached"),
        ):
            with self.assertRaisesRegex(
                self.bridge.RuntimeClosureError,
                "RUNTIME_OBSERVATION_CAPABILITY_REQUIRED",
            ):
                self.bridge.build_authenticated_backend(
                    stage_dir=STAGE,
                    output_dir=Path(directory),
                )


if __name__ == "__main__":
    unittest.main()
