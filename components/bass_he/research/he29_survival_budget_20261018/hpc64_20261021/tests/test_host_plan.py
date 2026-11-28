"""New Linux host/proc/lease fixtures; no native jobs or host changes."""
import errno
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import host_plan as h


def host_fixture(directory):
    root = Path(directory)
    proc, system, mount = root / "proc", root / "sys", root / "cgroup"
    (proc / "self").mkdir(parents=True)
    leaf = mount / "parent/job"
    leaf.mkdir(parents=True)
    (proc / "self/cgroup").write_text("0::/parent/job\n")
    (proc / "self/mountinfo").write_text(f"1 0 0:1 / {mount} rw - cgroup2 cgroup rw\n")
    (proc / "meminfo").write_text(f"MemTotal: {128*h.GIB//1024} kB\nMemAvailable: {120*h.GIB//1024} kB\n")
    for path in (mount, mount / "parent", leaf):
        (path / "cpu.max").write_text("max 100000\n")
        (path / "memory.max").write_text("max\n")
        (path / "memory.current").write_text(str(h.GIB))
    for cpu in range(64):
        path = system / f"devices/system/cpu/cpu{cpu}/topology"
        path.mkdir(parents=True)
        (path / "physical_package_id").write_text("0")
        (path / "core_id").write_text(str(cpu % 32))
        (path / "thread_siblings_list").write_text(f"{cpu%32},{cpu%32+32}")
    return proc, system, mount


def observe_fixture(proc, system):
    return h.observe_host(proc_root=proc, sys_root=system, affinity=range(64))


def proc_entry(root, pid, tokens, ppid=1, state="S"):
    path = root / str(pid)
    path.mkdir(parents=True, exist_ok=True)
    (path / "cmdline").write_bytes(b"\0".join(x.encode() for x in tokens) + b"\0")
    (path / "stat").write_text(f"{pid} (fixture process with spaces) {state} {ppid} " + "0 "*17 + "12345 0\n")
    return path


class TestHostPlan(unittest.TestCase):
    def test_64cpu_128g_plan_protects_cpu55_and_prefers_physical_cores(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, _ = host_fixture(directory)
            observed = observe_fixture(proc, system)
            plan = h.choose_resources(observed)
            self.assertTrue(plan["execution_allowed"])
            self.assertEqual((plan["table_workers"], plan["build_jobs"]), (48, 8))
            self.assertNotIn(55, plan["cpu_ids"])
            self.assertEqual(plan["protected_cpu_ids"], [55])
            self.assertEqual(plan["cpu_ids"][:32], list(range(32)))
            self.assertEqual(plan["effective_cpu_capacity"], 63)
            self.assertGreaterEqual(plan["reserved_memory_bytes"], 128*h.GIB/5)
            self.assertFalse(plan["rss_bound_measured"])

    def test_parent_quota8_overrides_leaf64_and_reserve_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, mount = host_fixture(directory)
            (mount / "parent/cpu.max").write_text("800000 100000")
            (mount / "parent/job/cpu.max").write_text("6400000 100000")
            observed = observe_fixture(proc, system)
            held = h.choose_resources(observed)
            self.assertFalse(held["execution_allowed"])
            self.assertIn("CPU_CAPACITY_EXHAUSTED_AFTER_RESERVE", held["hold_reasons"])
            reduced = h.choose_resources(observed, reserve_cpus=2)
            self.assertTrue(reduced["execution_allowed"])
            self.assertEqual(reduced["ancestor_min_cpu_quota_fraction"], "8")
            self.assertEqual((reduced["table_workers"], reduced["build_jobs"]), (6, 6))
            self.assertEqual(len(observed["cgroup_v2"]["ancestors"]), 3)

    def test_parent_memory8g_and_current_headroom_override_host128g(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, mount = host_fixture(directory)
            (mount / "parent/memory.max").write_text(str(8*h.GIB))
            (mount / "parent/memory.current").write_text(str(h.GIB))
            (mount / "parent/job/memory.max").write_text(str(128*h.GIB))
            observed = observe_fixture(proc, system)
            held = h.choose_resources(observed)
            self.assertFalse(held["execution_allowed"])
            self.assertEqual(held["effective_memory_capacity_bytes"], 8*h.GIB)
            self.assertEqual(held["effective_memory_available_bytes"], 7*h.GIB)
            reduced = h.choose_resources(observed, reserve_memory_gib=0)
            self.assertTrue(reduced["execution_allowed"])
            self.assertEqual((reduced["table_workers"], reduced["build_jobs"]), (3, 1))
            self.assertGreaterEqual(reduced["reserved_memory_bytes"], 8*h.GIB/5)

    def test_fractional_quota_is_floored_and_unobserved_limit_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, mount = host_fixture(directory)
            (mount / "parent/cpu.max").write_text("350000 100000")
            plan = h.choose_resources(observe_fixture(proc, system), reserve_cpus=1)
            self.assertEqual((plan["table_workers"], plan["build_jobs"]), (2, 2))
            (mount / "cpu.max").unlink()
            unknown = h.choose_resources(observe_fixture(proc, system), reserve_cpus=1)
            self.assertFalse(unknown["execution_allowed"])
            self.assertTrue(any(x.startswith("CPU_QUOTA_UNOBSERVED") for x in unknown["hold_reasons"]))
            self.assertEqual(unknown["cpu_ids"], [])

    def test_missing_memory_current_or_memavailable_holds(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, mount = host_fixture(directory)
            (mount / "parent/memory.max").write_text(str(64*h.GIB))
            (mount / "parent/memory.current").unlink()
            plan = h.choose_resources(observe_fixture(proc, system))
            self.assertFalse(plan["execution_allowed"])
            self.assertTrue(any(x.startswith("MEMORY_LIMIT_OR_HEADROOM") for x in plan["hold_reasons"]))
            (proc / "meminfo").write_text(f"MemTotal: {128*h.GIB//1024} kB\n")
            self.assertIn("MEMTOTAL_OR_MEMAVAILABLE_UNOBSERVED",
                          h.choose_resources(observe_fixture(proc, system))["hold_reasons"])

    def test_actual_global_root_missing_max_files_preserves_descendant_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, mount = host_fixture(directory)
            (mount / "cgroup.controllers").write_text("cpu memory\n")
            (mount / "cpu.max").unlink()
            (mount / "memory.max").unlink()
            (mount / "parent/cpu.max").write_text("800000 100000")
            (mount / "parent/memory.max").write_text(str(64*h.GIB))
            (mount / "parent/memory.current").write_text(str(8*h.GIB))
            observed = observe_fixture(proc, system)
            plan = h.choose_resources(observed, reserve_cpus=2)
            self.assertTrue(plan["execution_allowed"])
            self.assertEqual(plan["mount_root_classification"], "ACTUAL_GLOBAL_ROOT_SIGNATURE")
            self.assertEqual(plan["ancestor_min_cpu_quota_fraction"], "8")
            self.assertEqual(plan["effective_memory_available_bytes"], 56*h.GIB)
            self.assertEqual((plan["table_workers"], plan["build_jobs"]), (6, 6))

    def test_namespace_root_missing_controls_is_not_global_unlimited(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, mount = host_fixture(directory)
            (mount / "cgroup.controllers").write_text("cpu memory")
            (mount / "cgroup.type").write_text("domain")
            (mount / "cpu.max").unlink()
            (mount / "memory.max").unlink()
            observed = observe_fixture(proc, system)
            plan = h.choose_resources(observed)
            self.assertFalse(plan["execution_allowed"])
            self.assertEqual(plan["mount_root_classification"], "ACTUAL_NONROOT_NAMESPACE_OR_SUBTREE_MOUNT")
            self.assertTrue(any(x.startswith("CPU_QUOTA_UNOBSERVED") for x in plan["hold_reasons"]))

    def test_root_permission_denied_never_becomes_not_found_or_unlimited(self):
        for denied_name in ("cgroup.type", "cpu.max", "cgroup.controllers"):
            with self.subTest(denied_name=denied_name), tempfile.TemporaryDirectory() as directory:
                proc, system, mount = host_fixture(directory)
                (mount / "cgroup.controllers").write_text("cpu memory")
                (mount / "cpu.max").unlink()
                (mount / "memory.max").unlink()
                original = Path.read_text
                def read(path, *args, **kwargs):
                    if path == mount / denied_name:
                        raise PermissionError(errno.EACCES, "fixture root denied", str(path))
                    return original(path, *args, **kwargs)
                with mock.patch.object(Path, "read_text", read):
                    observed = observe_fixture(proc, system)
                plan = h.choose_resources(observed)
                self.assertFalse(plan["execution_allowed"])
                self.assertEqual(plan["mount_root_classification"], "ROOT_KIND_UNPROVEN")

    def test_missing_core_root_signature_does_not_bypass_unknown_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, mount = host_fixture(directory)
            (mount / "cpu.max").unlink()
            (mount / "memory.max").unlink()
            observed = observe_fixture(proc, system)
            plan = h.choose_resources(observed)
            self.assertFalse(plan["execution_allowed"])
            self.assertEqual(plan["mount_root_classification"], "ROOT_KIND_UNPROVEN")

    def test_proc_duplicates_other_namespaces_and_self_ancestors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "owner"
            binary.write_bytes(b"fixture not executable")
            proc_entry(root, os.getpid(), ["python3", "batch_entry.py"], ppid=91001)
            proc_entry(root, 91001, ["python3", "hpc_canary.py"], ppid=0)
            proc_entry(root, 91011, ["python3", "/work/BASS_HE/reference_runner.py", "case"])
            owner = proc_entry(root, 91012, ["owner"])
            (owner / "exe").symlink_to(binary)
            proc_entry(root, 91013, ["python3", "/work/VigilODE/campaign.py"])
            proc_entry(root, 91014, ["git", "-C", "/work/REI", "status"])
            proc_entry(root, 91015, ["python3", "run_packed.py"], state="Z")
            result = h.active_he29_processes(binary, proc_root=root)
            self.assertEqual({x["pid"] for x in result["matches"]}, {91011, 91012})
            self.assertEqual([x["pid"] for x in result["other_scientific_matches"]], [91013])
            self.assertIn(91001, result["excluded_pids"])
            self.assertIn(os.getpid(), result["excluded_pids"])
            self.assertEqual(result["zombie_pids_ignored"], [91015])
            self.assertFalse(result["execution_allowed"])
            self.assertEqual(result["kill_or_signal_calls"], 0)

    def test_permission_denied_is_not_pid_vanishing_or_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            denied = proc_entry(root, 91021, ["python3", "run_packed.py"]) / "cmdline"
            gone = proc_entry(root, 91022, ["python3", "run_packed.py"]) / "cmdline"
            gone.unlink()
            original = Path.read_bytes
            def read(path):
                if path == denied:
                    raise PermissionError(errno.EACCES, "fixture access denied", str(path))
                return original(path)
            with mock.patch.object(Path, "read_bytes", read):
                result = h.active_he29_processes(None, proc_root=root)
            self.assertEqual([x["pid"] for x in result["permission_denied"]], [91021])
            self.assertEqual(result["vanished_pids"], [91022])
            self.assertIn("PROC_VISIBILITY_INCOMPLETE", result["hold_reasons"])
            self.assertFalse(result["execution_allowed"])

    def test_empty_visible_process_scope_is_allowed_but_not_global_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            proc_entry(root, 91031, ["git", "-C", "/work/BASS_HE", "status"])
            proc_entry(root, 91032, [])
            result = h.active_he29_processes(None, proc_root=root)
            self.assertTrue(result["execution_allowed"])
            self.assertEqual(result["matches"], [])
            self.assertIn("observable local", result["scope"])

    def test_relative_scientific_command_uses_cwd_and_specific_namespace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for pid, folder_name in ((91041, "BASS_HE83"), (91042, "bass_cr")):
                working = root / folder_name
                working.mkdir()
                process = proc_entry(root, pid, ["python3", "campaign.py"])
                (process / "cwd").symlink_to(working, target_is_directory=True)
            result = h.active_he29_processes(None, proc_root=root)
            self.assertFalse(result["execution_allowed"])
            self.assertEqual([x["namespaces"] for x in result["other_scientific_matches"]],
                             [["BASS_HE"], ["bass_cr"]])
            self.assertTrue(all(x["matched_namespace_tokens"] == []
                                for x in result["other_scientific_matches"]))
            self.assertTrue(all(x["namespace_from_cwd"] is not None
                                for x in result["other_scientific_matches"]))

    def test_unreadable_cwd_for_relative_command_is_visibility_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = proc_entry(root, 91043, ["python3", "campaign.py"]) / "cwd"
            original = os.readlink
            def readlink(target):
                if Path(target) == path:
                    raise PermissionError(errno.EACCES, "fixture cwd denied", str(path))
                return original(target)
            with mock.patch.object(os, "readlink", side_effect=readlink):
                result = h.active_he29_processes(None, proc_root=root)
            self.assertFalse(result["execution_allowed"])
            self.assertEqual([x["pid"] for x in result["permission_denied"]], [91043])
            self.assertIn("PROC_VISIBILITY_INCOMPLETE", result["hold_reasons"])

    def test_supplied_busy_process_observation_blocks_resource_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            proc, system, _ = host_fixture(directory)
            observed = observe_fixture(proc, system)
            observed["process_observation"] = {"execution_allowed": False,
                                               "hold_reasons": ["OTHER_SCIENTIFIC_PROCESS_OBSERVED"]}
            result = h.choose_resources(observed)
            self.assertFalse(result["execution_allowed"])
            self.assertEqual(result["table_workers"], 0)

    def test_lease_collision_does_not_truncate_and_inode_survives_release(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lease.lock"
            path.write_bytes(b"previous metadata")
            inode = path.stat().st_ino
            with h.host_execution_lease(path) as lease:
                self.assertEqual(lease["pid"], os.getpid())
                active_bytes = path.read_bytes()
                with self.assertRaisesRegex(RuntimeError, "LEASE_BUSY"):
                    with h.host_execution_lease(path):
                        self.fail("second holder entered")
                self.assertEqual(path.read_bytes(), active_bytes)
            self.assertEqual(path.stat().st_ino, inode)
            self.assertEqual(json.loads(path.read_text())["state"], "RELEASED")
            with h.host_execution_lease(path):
                self.assertEqual(path.stat().st_ino, inode)
            self.assertTrue(path.is_file())

    def test_lease_rejects_symlink_and_linked_inode_without_changing_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.write_bytes(b"preserved")
            link = root / "lease"
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "SYMLINK"):
                with h.host_execution_lease(link):
                    pass
            link.unlink()
            os.link(target, link)
            with self.assertRaisesRegex(ValueError, "SINGLE_REGULAR_INODE"):
                with h.host_execution_lease(link):
                    pass
            self.assertEqual(target.read_bytes(), b"preserved")

    def test_exception_releases_lock_and_preserves_failed_body_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lease"
            with self.assertRaisesRegex(ValueError, "fixture body failure"):
                with h.host_execution_lease(path):
                    raise ValueError("fixture body failure")
            record = json.loads(path.read_text())
            self.assertTrue(record["body_failed"])
            self.assertEqual(record["state"], "RELEASED")
            with h.host_execution_lease(path):
                pass


if __name__ == "__main__":
    unittest.main()
