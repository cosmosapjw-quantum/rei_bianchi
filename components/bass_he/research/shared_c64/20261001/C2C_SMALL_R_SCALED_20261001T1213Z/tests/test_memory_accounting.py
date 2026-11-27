"""Accounting and fail-closed launch tests; no physics or MPI workload."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import host_probe
import launch_ncp

GIB = 2**30


def stat_text(**updates):
    data = dict(file=7*GIB, active_file=6*GIB, inactive_file=GIB,
                shmem=0, file_mapped=0, file_dirty=0, file_writeback=0,
                unevictable=0, anon=GIB//4, kernel=GIB//4,
                slab_reclaimable=GIB//4)
    data.update(updates)
    return "\n".join(f"{k} {v}" for k, v in data.items())


def budget(stats=None, current=8*GIB, limit=8*GIB, low="0", minimum="0",
           policy="clean-file-half-v1"):
    return host_probe.cgroup_memory_budget(limit, current,
           stat_text() if stats is None else stats, minimum, low, policy)


class MemoryAccountingTests(unittest.TestCase):
    def test_raw_is_default_and_never_credits_cache(self):
        result = host_probe.cgroup_memory_budget(8*GIB, 8*GIB, stat_text(), "0", "0")
        self.assertEqual(result["policy"], "raw-headroom")
        self.assertEqual(result["credited_bytes"], 0)
        self.assertEqual(result["available_estimate_bytes"], 0)

    def test_half_clean_file_credits_both_lru_lists(self):
        result = budget()
        self.assertEqual(result["credited_bytes"], 7*GIB//2)
        self.assertEqual(result["raw_headroom_bytes"], 0)
        self.assertEqual(result["memory.stat"]["slab_reclaimable"], GIB//4)
        # Slab is preserved in evidence but does not add any credit.
        self.assertEqual(result["available_estimate_bytes"], 7*GIB//2)

    def test_all_excluded_categories_subtracted_conservatively(self):
        result = budget(stat_text(shmem=GIB, file_mapped=GIB, file_dirty=GIB,
                        file_writeback=GIB, unevictable=GIB))
        self.assertEqual(result["clean_file_candidate_bytes"], 2*GIB)
        self.assertEqual(result["credited_bytes"], GIB)
        self.assertEqual(budget(stat_text(shmem=8*GIB))["credited_bytes"], 0)

    def test_dirty_cache_without_clean_pages_cannot_unblock(self):
        result = budget(stat_text(file_dirty=7*GIB))
        self.assertEqual(result["available_estimate_bytes"], 0)

    def test_missing_invalid_duplicate_stats_fail_to_zero_credit(self):
        for text in ("", "file 100", stat_text()+"\nfile 12", stat_text(file=-1),
                     stat_text(file="NaN"), "unparseable"):
            with self.subTest(text=text):
                result = budget(text)
                self.assertEqual(result["credited_bytes"], 0)
                self.assertIsNotNone(result["memory.stat.error"])

    def test_protection_unreadable_nonzero_disables_credit(self):
        for value in (None, "max", "1", "-1", "bad"):
            self.assertEqual(budget(low=value)["credited_bytes"], 0)
            self.assertEqual(budget(minimum=value)["credited_bytes"], 0)

    def test_credit_bounded_by_current_and_signed_overage_retained(self):
        result = budget(current=GIB, limit=8*GIB)
        self.assertEqual(result["credited_bytes"], GIB//2)
        self.assertLessEqual(result["available_estimate_bytes"], 8*GIB)
        over = budget(current=9*GIB, limit=8*GIB)
        self.assertEqual(over["available_estimate_bytes"], 5*GIB//2)
        self.assertEqual(over["raw_headroom_bytes"], 0)

    def test_unknown_policy_and_invalid_usage_rejected(self):
        for kwargs in (dict(policy="aggressive"), dict(current=-1), dict(limit=-1), dict(current=True)):
            with self.assertRaises(ValueError):
                budget(**kwargs)

    def fake_read(self, path):
        path = str(path)
        values = {"/proc/meminfo": "MemTotal: 12000000 kB\nMemAvailable: 4000000 kB\n"}
        for folder, limit, current in (("/cg/leaf", 8*GIB, 7*GIB), ("/cg", 6*GIB, 6*GIB)):
            values.update({folder+"/memory.max": str(limit), folder+"/memory.current": str(current),
                           folder+"/memory.stat": stat_text(), folder+"/memory.min": "0",
                           folder+"/memory.low": "0", folder+"/cpu.max": "800000 100000"})
        if path.endswith("physical_package_id"):
            return "0"
        if path.endswith("core_id"):
            return path.split("/cpu")[-1].split("/")[0]
        return values.get(path)

    def test_all_ancestors_and_host_cap_apply(self):
        with patch.object(host_probe, "_cgroup_paths", return_value=[Path("/cg/leaf"), Path("/cg")]), \
             patch.object(host_probe, "_read", side_effect=self.fake_read), \
             patch.object(host_probe.os, "sched_getaffinity", return_value={0, 1}):
            result = host_probe.probe_host("clean-file-half-v1")
            self.assertEqual(result["memory_available_budget_bytes"], 3*GIB)
            self.assertEqual(result["memory_raw_headroom_budget_bytes"], 0)
            self.assertEqual(len(result["cgroup_v2"]), 2)
            original_read = self.fake_read
            with patch.object(host_probe, "_read", side_effect=lambda p:
                       "MemAvailable: 1024 kB\n" if str(p)=="/proc/meminfo" else original_read(p)):
                self.assertEqual(host_probe.probe_host("clean-file-half-v1")["memory_available_budget_bytes"], 1024**2)

    def test_missing_host_estimate_rejects_cache_accounting(self):
        with patch.object(host_probe, "_cgroup_paths", return_value=[Path("/cg")]), \
             patch.object(host_probe, "_read", side_effect=lambda p:
                        None if str(p)=="/proc/meminfo" else self.fake_read(p)), \
             patch.object(host_probe.os, "sched_getaffinity", return_value={0}):
            with self.assertRaisesRegex(RuntimeError, "MemAvailable"):
                host_probe.probe_host("clean-file-half-v1")

    def test_binding_default_and_explicit_exception(self):
        args = ("mpirun", sys.executable, "tasks.json", "new_output", "native", 2, 1)
        default = launch_ncp.build_command(*args)
        explicit = launch_ncp.build_command(*args, bind_to="none")
        self.assertEqual(default[default.index("--bind-to")+1], "core")
        self.assertEqual(explicit[explicit.index("--bind-to")+1], "none")
        self.assertIn("--nooversubscribe", explicit)
        with self.assertRaises(ValueError):
            launch_ncp.build_command(*args, bind_to="socket")

    def test_execution_preflight_failure_never_calls_subprocess(self):
        host = {"core_binding_cpu_budget": 8, "memory_available_budget_bytes": 0,
                "cgroup_status": "V2_VISIBLE_ANCESTRY_INSPECTED"}
        with patch.object(launch_ncp, "read_manifest", return_value=({"limits": {"per_worker_memory_gib": 1.5}}, "sha", None)), \
             patch.object(launch_ncp, "probe_host", return_value=host), \
             patch.object(launch_ncp.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                launch_ncp.main(["--manifest", "unused", "--output-dir", "unused", "--backend", "native",
                                 "--ranks", "2", "--execute", "--bind-to", "none",
                                 "--memory-accounting", "clean-file-half-v1"])
            run.assert_not_called()

    def test_twenty_percent_reserve_and_envelopes_unchanged(self):
        host = {"core_binding_cpu_budget": 8, "memory_available_budget_bytes": 4*GIB,
                "cgroup_status": "V2_VISIBLE_ANCESTRY_INSPECTED"}
        result = launch_ncp.validate_layout(host, 2, 1, 1.5)
        self.assertEqual(result["maximum_workers_from_memory"], 1)
        self.assertEqual(result["per_worker_memory_bytes"], 3*GIB//2)
        self.assertEqual(result["controller_memory_budget_bytes"], GIB//2)
        self.assertEqual(result["memory_headroom_fraction"], 0.2)
        with self.assertRaises(ValueError):
            launch_ncp.validate_layout(host, 3, 1, 1.5)
        with self.assertRaises(ValueError):
            launch_ncp.validate_layout(host, 2, 1, 1.5, reserve_fraction=0.19)


if __name__ == "__main__":
    unittest.main()
