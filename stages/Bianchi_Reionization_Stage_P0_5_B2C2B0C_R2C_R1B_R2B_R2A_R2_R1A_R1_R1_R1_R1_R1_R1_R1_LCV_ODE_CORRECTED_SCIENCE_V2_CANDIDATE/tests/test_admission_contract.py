from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import sys
import unittest


ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
sys.path.insert(0, str(ANALYSIS))

try:
    import admission_contract as admission
except ModuleNotFoundError:
    admission = None


# This literal is the external admission contract.  It deliberately does not
# derive the required gates or authorities from the implementation.
EXPECTED_GATES = (
    ("FINITE_STATE", "CONTROLLER"),
    ("PHYSICAL_DOMAIN", "CONTROLLER"),
    ("RESIDUAL", "INDEPENDENT"),
    ("ENCLOSURE", "INDEPENDENT"),
    ("EXPECTED_TERMINAL", "CONTROLLER"),
    ("EVENT_COMPLETENESS", "INDEPENDENT"),
    ("PHYSICAL_INVARIANTS", "INDEPENDENT"),
    ("DIAGNOSTICS_COMPLETE", "CONTROLLER"),
    ("EXECUTION_IDENTITY", "CONTROLLER"),
    ("CORRECTED_LINEAGE", "CONTROLLER"),
)


class AdmissionContractTests(unittest.TestCase):
    def require_module(self):
        self.assertIsNotNone(admission, "admission_contract.py is not implemented")
        return admission

    def passing_evidence(self):
        module = self.require_module()
        return tuple(
            module.GateEvidence(
                gate=module.RequiredGate[gate_name],
                verdict=module.GateVerdict.PASS,
                authority=module.EvidenceAuthority[authority_name],
                evidence_sha256=hashlib.sha256(
                    ("external-evidence:" + gate_name).encode("ascii")
                ).hexdigest(),
            )
            for gate_name, authority_name in EXPECTED_GATES
        )

    def test_closed_required_gate_and_authority_contract(self) -> None:
        module = self.require_module()
        self.assertEqual(
            {gate.name for gate in module.RequiredGate},
            {name for name, _ in EXPECTED_GATES},
        )
        self.assertEqual(
            {
                gate.name: module.REQUIRED_AUTHORITY[gate].name
                for gate in module.RequiredGate
            },
            dict(EXPECTED_GATES),
        )
        self.assertEqual(
            {item.name for item in module.SolverOutcome},
            {"SOLVED", "FAILED", "UNRESOLVED"},
        )
        with self.assertRaises(TypeError):
            module.GateEvidence(
                gate="FINITE_STATE",
                verdict=module.GateVerdict.PASS,
                authority=module.EvidenceAuthority.CONTROLLER,
                evidence_sha256="0" * 64,
            )

    def test_only_solved_with_every_authoritative_pass_is_admitted(self) -> None:
        module = self.require_module()
        evidence = self.passing_evidence()
        decision = module.adjudicate(
            outcome=module.SolverOutcome.SOLVED,
            evidence=evidence,
            worker_claimed_success=True,
        )
        self.assertEqual(decision.status, module.AdmissionStatus.ADMITTED)
        self.assertEqual(decision.reasons, ())
        self.assertRegex(decision.evidence_digest, r"^[0-9a-f]{64}$")

        permuted = module.adjudicate(
            outcome=module.SolverOutcome.SOLVED,
            evidence=tuple(reversed(evidence)),
            worker_claimed_success=False,
        )
        self.assertEqual(permuted.status, module.AdmissionStatus.ADMITTED)
        self.assertEqual(permuted.evidence_digest, decision.evidence_digest)

        changed = list(evidence)
        changed[0] = replace(changed[0], evidence_sha256="f" * 64)
        changed_decision = module.adjudicate(
            outcome=module.SolverOutcome.SOLVED,
            evidence=tuple(changed),
        )
        self.assertNotEqual(changed_decision.evidence_digest, decision.evidence_digest)

    def test_one_gate_mutation_always_fails_closed(self) -> None:
        module = self.require_module()
        baseline = self.passing_evidence()
        for index, item in enumerate(baseline):
            for verdict, expected in (
                (module.GateVerdict.FAIL, module.AdmissionStatus.REJECTED),
                (module.GateVerdict.MISSING, module.AdmissionStatus.BLOCKED),
                (module.GateVerdict.INCONCLUSIVE, module.AdmissionStatus.BLOCKED),
            ):
                with self.subTest(gate=item.gate.name, verdict=verdict.name):
                    mutated = list(baseline)
                    mutated[index] = replace(item, verdict=verdict)
                    decision = module.adjudicate(
                        outcome=module.SolverOutcome.SOLVED,
                        evidence=tuple(mutated),
                    )
                    self.assertEqual(decision.status, expected)
                    self.assertIn(item.gate.name, decision.reasons)

    def test_missing_duplicate_and_wrong_authority_are_blocked(self) -> None:
        module = self.require_module()
        evidence = self.passing_evidence()

        missing = module.adjudicate(
            outcome=module.SolverOutcome.SOLVED,
            evidence=evidence[:-1],
        )
        self.assertEqual(missing.status, module.AdmissionStatus.BLOCKED)
        self.assertIn("CORRECTED_LINEAGE", missing.reasons)

        duplicate = module.adjudicate(
            outcome=module.SolverOutcome.SOLVED,
            evidence=evidence + (evidence[0],),
        )
        self.assertEqual(duplicate.status, module.AdmissionStatus.BLOCKED)
        self.assertIn("DUPLICATE_GATE:FINITE_STATE", duplicate.reasons)

        wrong = list(evidence)
        residual = next(
            index for index, item in enumerate(wrong) if item.gate.name == "RESIDUAL"
        )
        wrong[residual] = replace(
            wrong[residual], authority=module.EvidenceAuthority.WORKER
        )
        wrong_decision = module.adjudicate(
            outcome=module.SolverOutcome.SOLVED,
            evidence=tuple(wrong),
        )
        self.assertEqual(wrong_decision.status, module.AdmissionStatus.BLOCKED)
        self.assertIn("WRONG_AUTHORITY:RESIDUAL", wrong_decision.reasons)

    def test_worker_self_success_and_non_solved_outcomes_never_admit(self) -> None:
        module = self.require_module()
        self_success = module.adjudicate(
            outcome=module.SolverOutcome.SOLVED,
            evidence=(),
            worker_claimed_success=True,
        )
        self.assertEqual(self_success.status, module.AdmissionStatus.BLOCKED)

        failed = module.adjudicate(
            outcome=module.SolverOutcome.FAILED,
            evidence=self.passing_evidence(),
            worker_claimed_success=True,
        )
        self.assertEqual(failed.status, module.AdmissionStatus.REJECTED)

        unresolved = module.adjudicate(
            outcome=module.SolverOutcome.UNRESOLVED,
            evidence=self.passing_evidence(),
        )
        self.assertEqual(unresolved.status, module.AdmissionStatus.BLOCKED)


if __name__ == "__main__":
    unittest.main()
