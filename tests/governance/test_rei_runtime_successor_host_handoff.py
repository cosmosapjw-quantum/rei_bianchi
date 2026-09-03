from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import urllib.error

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "handoff" / "rei_runtime_bridge_successor_host_20260903"
RUNNER = PACKAGE / "successor_runtime_runner.py"
CONTRACT = PACKAGE / "CONTRACT.json"
WORKFLOW = ROOT / ".github" / "workflows" / "rei-runtime-bridge-successor-host-handoff.yml"

SEMANTIC_LOCK = "a3da50241ed6423212ab40c79f7810b5eaad042acdff29eb40f330aa39d2d4fa"
PR41_HEAD = "ad4b3854cb52bc735b28fc828c09de1a3302bb0a"
PR41_TREE = "ed11f66ff25e1fa132644cad97594838a2f02044"
PR38_HEAD = "3169d1b0554193ababfb568406764d53df29649d"
PR38_TREE = "1fa2da1a818bb311bf6cec42f76ff05693ed0903"
LEASE_REF = "refs/heads/attempt-ledger/rei-runtime-bridge-ntpath-rebind-20260903-attempt-3"


def load_runner():
    spec = importlib.util.spec_from_file_location("rei_successor_runner_test", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("runner import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


class FakeResponse:
    def __init__(self, status: int, body: dict):
        self.status = status
        self._body = json.dumps(body).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class SuccessorHostHandoffContractTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = {
            "CONTRACT.json",
            "GLOBAL_ATTEMPT_LEASE_PROTOCOL_V2.json",
            "successor_runtime_runner.py",
            "verify_successor_handoff.py",
            "README.md",
            "LOCAL_CODEX_RUNTIME_PROMPT.md",
            "SCISPACE_LITERATURE_LOCK.md",
            "WOLFRAM_DAG_RECEIPT.json",
            "PHYS_MATH_AUDIT.md",
            "PHYS_MATH_CODE_AUDIT.md",
            "HANDOFF_STATE.csv",
            "HANDOFF_STATE.svg",
            "render_handoff_state.py",
            "TDD_RED_RECEIPT.json",
            "PACKAGE_INDEX.json",
        }
        self.assertEqual(sorted(name for name in required if not (PACKAGE / name).is_file()), [])

    def test_contract_pins_governance_and_scientific_lineage(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["immutable_governance_predecessor"]["commit"], PR41_HEAD)
        self.assertEqual(contract["immutable_governance_predecessor"]["tree"], PR41_TREE)
        self.assertEqual(contract["source_handoff"]["commit"], PR38_HEAD)
        self.assertEqual(contract["source_handoff"]["tree"], PR38_TREE)
        self.assertEqual(contract["successor_section0"]["semantic_toolchain_lock_sha256"], SEMANTIC_LOCK)
        self.assertEqual(contract["attempt_budget"]["remaining_native_attempts"], 1)
        self.assertEqual(contract["attempt_budget"]["retries_after_outcome"], 0)
        self.assertEqual(contract["attempt_budget"]["global_lease_ref"], LEASE_REF)

    def test_historical_section0_receipt_is_rejected(self) -> None:
        runner = load_runner()
        contract = runner.load_contract(CONTRACT)
        with tempfile.TemporaryDirectory() as tmp:
            receipt = Path(tmp) / "historical.json"
            write_json(receipt, {
                "status": "PASS_IMMUTABLE_SECTION_0",
                "semantic_toolchain_lock_sha256": SEMANTIC_LOCK,
            })
            with self.assertRaisesRegex(runner.SuccessorHandoffError, "SUCCESSOR_SECTION0_STATUS_MISMATCH"):
                runner.load_successor_section0_receipt(receipt, contract)

    def test_successor_section0_requires_exact_semantic_lock(self) -> None:
        runner = load_runner()
        contract = runner.load_contract(CONTRACT)
        with tempfile.TemporaryDirectory() as tmp:
            receipt = Path(tmp) / "successor.json"
            write_json(receipt, {
                "schema": "rei-successor-section0-receipt/v1",
                "status": "PASS_EQUIVALENT_SECTION_0_SUCCESSOR",
                "semantic_toolchain_lock_sha256": "0" * 64,
                "observed_toolchain": {},
            })
            with self.assertRaisesRegex(runner.SuccessorHandoffError, "SUCCESSOR_SECTION0_LOCK_MISMATCH"):
                runner.load_successor_section0_receipt(receipt, contract)

    def test_successor_section0_accepts_exact_lock_and_fields(self) -> None:
        runner = load_runner()
        contract = runner.load_contract(CONTRACT)
        lock = contract["successor_section0"]["semantic_toolchain_lock"]
        with tempfile.TemporaryDirectory() as tmp:
            receipt = Path(tmp) / "successor.json"
            write_json(receipt, {
                "schema": "rei-successor-section0-receipt/v1",
                "status": "PASS_EQUIVALENT_SECTION_0_SUCCESSOR",
                "semantic_toolchain_lock_sha256": SEMANTIC_LOCK,
                "observed_toolchain": lock,
                "claim_boundary": "HOST_REATTESTATION_ONLY_NATIVE_RUNTIME_NOT_RUN",
            })
            loaded = runner.load_successor_section0_receipt(receipt, contract)
            self.assertEqual(loaded["observed_toolchain"], lock)

    def test_global_lease_201_targets_exact_executable_release(self) -> None:
        runner = load_runner()
        contract = runner.load_contract(CONTRACT)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "global.json"
            expected_head = "1" * 40
            events = []

            def opener(request, timeout):
                events.append(json.loads(request.data.decode("ascii")))
                return FakeResponse(201, {
                    "ref": LEASE_REF,
                    "object": {"sha": expected_head},
                })

            record = runner.acquire_global_lease(
                contract=contract,
                successor_receipt_sha256="2" * 64,
                expected_release_head=expected_head,
                token="token",
                output=out,
                api_base="https://example.invalid",
                opener=opener,
            )
            self.assertEqual(events, [{"ref": LEASE_REF, "sha": expected_head}])
            self.assertEqual(record["target_commit"], expected_head)
            self.assertTrue(out.is_file())

    def test_global_lease_422_fails_without_receipt(self) -> None:
        runner = load_runner()
        contract = runner.load_contract(CONTRACT)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "global.json"

            def opener(request, timeout):
                raise urllib.error.HTTPError(request.full_url, 422, "exists", {}, None)

            with self.assertRaisesRegex(runner.SuccessorHandoffError, "STOP_ATTEMPT_ALREADY_RESERVED"):
                runner.acquire_global_lease(
                    contract=contract,
                    successor_receipt_sha256="2" * 64,
                    expected_release_head="1" * 40,
                    token="token",
                    output=out,
                    api_base="https://example.invalid",
                    opener=opener,
                )
            self.assertFalse(out.exists())

    def test_global_lease_response_mismatch_fails_closed(self) -> None:
        runner = load_runner()
        contract = runner.load_contract(CONTRACT)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "global.json"

            def opener(request, timeout):
                return FakeResponse(201, {
                    "ref": LEASE_REF,
                    "object": {"sha": "f" * 40},
                })

            with self.assertRaisesRegex(runner.SuccessorHandoffError, "STOP_REMOTE_LEASE_RESPONSE_MISMATCH"):
                runner.acquire_global_lease(
                    contract=contract,
                    successor_receipt_sha256="2" * 64,
                    expected_release_head="1" * 40,
                    token="token",
                    output=out,
                    api_base="https://example.invalid",
                    opener=opener,
                )
            self.assertFalse(out.exists())

    def test_local_lease_is_persistent_o_excl_and_not_tmp(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory(dir="/mnt/data") as tmp:
            root = Path(tmp)
            lease = root / "attempt-3.local-lease.json"
            payload = {"schema": "x", "status": "LOCAL_ATTEMPT_RESERVED"}
            runner.create_persistent_local_lease(lease, payload, forbidden_roots=())
            self.assertTrue(lease.is_file())
            with self.assertRaisesRegex(runner.SuccessorHandoffError, "STOP_LOCAL_ATTEMPT_ALREADY_RESERVED"):
                runner.create_persistent_local_lease(lease, payload, forbidden_roots=())
        with self.assertRaisesRegex(runner.SuccessorHandoffError, "LOCAL_LEASE_UNDER_TMP_FORBIDDEN"):
            runner.validate_local_lease_path(Path("/tmp/attempt.json"), forbidden_roots=())

    def test_release_identity_uses_exact_head_and_tree(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory(dir="/mnt/data") as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "test"], check=True)
            (repo / "x.txt").write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "x.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "x"], check=True)
            head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            tree = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD^{tree}"], text=True).strip()
            observed = runner.verify_exact_release_identity(repo, head, tree)
            self.assertEqual(observed, (head, tree))
            with self.assertRaisesRegex(runner.SuccessorHandoffError, "EXECUTABLE_RELEASE_HEAD_MISMATCH"):
                runner.verify_exact_release_identity(repo, "0" * 40, tree)

    def test_order_is_global_then_local_then_native_exactly_once(self) -> None:
        runner = load_runner()
        events = []
        with tempfile.TemporaryDirectory(dir="/mnt/data") as tmp:
            root = Path(tmp)
            global_receipt = root / "global.json"
            local_lease = root / "local.json"

            def global_acquire():
                events.append("global")
                write_json(global_receipt, {"status": "GLOBAL_ATTEMPT_RESERVED"})
                return {"status": "GLOBAL_ATTEMPT_RESERVED"}

            def native_dispatch():
                self.assertTrue(global_receipt.is_file())
                self.assertTrue(local_lease.is_file())
                events.append("native")
                return {"status": "RUNTIME_BRIDGE_PASS_WITH_PRESTART_PROCESS_BOUNDARY_RESIDUAL"}

            result = runner.reserve_then_dispatch(
                global_acquire=global_acquire,
                local_lease_path=local_lease,
                local_lease_payload={"status": "LOCAL_ATTEMPT_RESERVED"},
                forbidden_local_roots=(),
                native_dispatch=native_dispatch,
            )
            self.assertEqual(events, ["global", "native"])
            self.assertEqual(result["status"], "RUNTIME_BRIDGE_PASS_WITH_PRESTART_PROCESS_BOUNDARY_RESIDUAL")

    def test_native_failure_is_not_retried(self) -> None:
        runner = load_runner()
        calls = []
        with tempfile.TemporaryDirectory(dir="/mnt/data") as tmp:
            root = Path(tmp)

            def global_acquire():
                return {"status": "GLOBAL_ATTEMPT_RESERVED"}

            def native_dispatch():
                calls.append(1)
                raise runner.SuccessorHandoffError("FIRST_NATIVE_BLOCKER")

            with self.assertRaisesRegex(runner.SuccessorHandoffError, "FIRST_NATIVE_BLOCKER"):
                runner.reserve_then_dispatch(
                    global_acquire=global_acquire,
                    local_lease_path=root / "local.json",
                    local_lease_payload={"status": "LOCAL_ATTEMPT_RESERVED"},
                    forbidden_local_roots=(),
                    native_dispatch=native_dispatch,
                )
            self.assertEqual(calls, [1])

    def test_workflow_is_read_only_and_never_invokes_native_runner(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("contents: read", text)
        self.assertIn("REI_NATIVE_DISPATCH_FORBIDDEN: \"1\"", text)
        self.assertNotIn("cargo ", text)
        self.assertNotIn("rustc ", text)
        self.assertNotIn("successor_runtime_runner.py --repo", text)

    def test_claim_ceiling_is_unchanged(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        ceiling = contract["claim_ceiling"]
        self.assertEqual(ceiling["native_runtime"], "NOT_RUN")
        self.assertEqual(ceiling["first_interval"], "NO_PASS_FIRST_CANONICAL_INTERVAL")
        self.assertEqual(ceiling["provider_export"], "NOT_AUTHORIZED")
        self.assertEqual(ceiling["scientific_pass"], "NOT_CLAIMED")

    def test_package_index_has_no_self_hash_cycle(self) -> None:
        index_path = PACKAGE / "PACKAGE_INDEX.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        names = [row["path"] for row in index["entries"]]
        self.assertNotIn("PACKAGE_INDEX.json", names)
        self.assertEqual(len(names), len(set(names)))
        for row in index["entries"]:
            path = PACKAGE / row["path"]
            payload = path.read_bytes()
            blob = hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()
            self.assertEqual(blob, row["blob_sha"])


if __name__ == "__main__":
    unittest.main()
