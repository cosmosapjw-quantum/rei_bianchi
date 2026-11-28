"""M1/M2 build contract checks; no scientific pair computation."""
import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "ncp_build.py"


def module():
    spec = importlib.util.spec_from_file_location("ncp_build", SCRIPT)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_rejects_ambiguous_probe_before_build():
    m = module()
    report = {"schema": "WU088_NCP_READ_ONLY_PROBE_V1", "status": "PROBE_REQUIRES_CGROUP_INSPECTION",
              "warnings": ["unresolved"], "allowed_logical_cpus": list(range(64)),
              "planning_cpu_budget": 64, "cgroup": {"quota_cpu_equivalents": None}}
    with pytest.raises(ValueError, match="cgroup|probe"):
        m.validate_probe(report)


def test_rejects_budget_above_allowed_affinity():
    m = module()
    report = {"schema": "WU088_NCP_READ_ONLY_PROBE_V1", "status": "PROBED_NOT_BENCHMARKED",
              "warnings": [], "allowed_logical_cpus": [0, 1],
              "planning_cpu_budget": 64, "cgroup": {"quota_cpu_equivalents": None}}
    with pytest.raises(ValueError, match="budget"):
        m.validate_probe(report)


def test_native_build_environment_drops_loader_injection():
    m = module()
    env = m.trusted_env({"PATH": "/usr/bin", "LD_PRELOAD": "/tmp/inject.so",
                         "LD_LIBRARY_PATH": "/tmp", "OMP_NUM_THREADS": "64"})
    assert env["PATH"] == "/usr/bin"
    assert "LD_PRELOAD" not in env and "LD_LIBRARY_PATH" not in env
    assert env["OMP_NUM_THREADS"] == "1"


def test_build_flags_preserve_strict_precision():
    m = module()
    assert "-fno-fast-math" in m.FLAGS
    assert "-ffp-contract=off" in m.FLAGS
    assert "-ffast-math" not in m.FLAGS
