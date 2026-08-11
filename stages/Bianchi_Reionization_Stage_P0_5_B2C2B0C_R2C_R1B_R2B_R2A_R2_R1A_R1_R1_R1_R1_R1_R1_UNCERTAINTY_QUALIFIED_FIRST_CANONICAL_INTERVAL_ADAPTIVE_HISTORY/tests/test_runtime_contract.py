import unittest
from unittest import mock

from helpers import STAGE, load


runtime_contract = load("runtime_contract_dependency_tests", "analysis/runtime_contract.py")
REPO = STAGE.parents[1]

PRODUCTION_DEPENDENCIES = {
    "numpy": "2.3.5",
    "scipy": "1.17.0",
    "pandas": "2.2.3",
    "python-dateutil": "2.9.0.post0",
    "pytz": "2026.3.post1",
    "tzdata": "2026.3",
    "six": "1.17.0",
}


def numeric_fingerprint(*, numpy_version="2.3.5"):
    return {
        "numpy": numpy_version,
        "numpy_configuration_sha256": "0" * 64,
        "numpy_runtime_sha256": "1" * 64,
        "pandas": "2.2.3",
        "scipy": "1.17.0",
    }


class RuntimeDependencyPolicyTests(unittest.TestCase):
    def build_with(self, versions, *, jax_spec=None, fingerprint=None):
        with (
            mock.patch.object(
                runtime_contract.importlib.metadata,
                "version",
                side_effect=lambda name: versions[name],
            ),
            mock.patch.object(
                runtime_contract.importlib.util,
                "find_spec",
                return_value=jax_spec,
            ),
        ):
            return runtime_contract.build(
                REPO,
                STAGE,
                numeric_fingerprint=fingerprint or numeric_fingerprint(),
                require_clean=False,
            )

    def test_rejects_wrong_direct_dependency_version(self):
        versions = dict(PRODUCTION_DEPENDENCIES, numpy="9.9.9")
        with self.assertRaisesRegex(
            RuntimeError,
            r"numpy.*expected 2\.3\.5.*observed 9\.9\.9",
        ):
            self.build_with(
                versions,
                fingerprint=numeric_fingerprint(numpy_version="9.9.9"),
            )

    def test_rejects_wrong_transitive_dependency_version(self):
        versions = dict(PRODUCTION_DEPENDENCIES)
        versions["python-dateutil"] = "0.0.0"
        with self.assertRaisesRegex(
            RuntimeError,
            r"python-dateutil.*expected 2\.9\.0\.post0.*observed 0\.0\.0",
        ):
            self.build_with(versions)

    def test_rejects_jax_when_installed(self):
        with self.assertRaisesRegex(RuntimeError, r"JAX must be absent"):
            self.build_with(PRODUCTION_DEPENDENCIES, jax_spec=object())

    def test_accepts_only_exact_production_closure_without_jax(self):
        value = self.build_with(PRODUCTION_DEPENDENCIES)
        self.assertEqual(value["dependencies"], PRODUCTION_DEPENDENCIES)
        self.assertFalse(value["jax_installed"])


if __name__ == "__main__":
    unittest.main()
