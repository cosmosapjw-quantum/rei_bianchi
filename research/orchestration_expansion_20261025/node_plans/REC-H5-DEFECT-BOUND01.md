# REC-H5-DEFECT-BOUND01

Lead: cosmosapjw-quantum/rec_bianchi

Current status: `PASS_DERIVED_SCOPED`

Source: `authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/4`

```json
{
  "id": "REC-H5-DEFECT-BOUND01",
  "lead_repo": "cosmosapjw-quantum/rec_bianchi",
  "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/4",
  "contract": {
    "id": "REC-H5-DEFECT-BOUND01",
    "status": "READY_THEORY_ONLY_ACTUAL_BOUND_INPUT_PENDING",
    "depends_on": [],
    "provider_domain": "Original z~1100 eta history; source-matched forward solution/defect",
    "equations": "e(t)<=exp(Ldt)e0+integral exp(L(t-s))r(s)ds; eps_j<=(1-a)eL+a eR+M2 h²/8; |delta o|<=|Ks|eps",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/rec_bianchi",
    "prerequisites": "Same cosmology/reference/clock/source and actual L,defect,endpoint/curvature bounds",
    "claim_gate": "Assumptions checked and bounded numerical defects independent of stored h/2-h/4 agreement; physical epsilon remainsnull until inputs",
    "pass_next": "Feed actual eps to existing Ks/PB01, affected uncertainty propagation only",
    "budget": "Analytic derivation now; no new RHS/IVP/certification run; new cap required for finite proof artifact",
    "tests": "Only affected source/state/measure/units/conservation/tangent checks; original numerical tolerance retained; no unchangedsuite replay",
    "fail_action": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
    "uncertainty": "Provider/model/interpolation/quadrature/floating error separate; null until actual evidence",
    "units": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
    "lead_repo": "cosmosapjw-quantum/rec_bianchi",
    "consumer_repo": "cosmosapjw-quantum/rec_bianchi",
    "outputs": [
      "source-qualified result within stated domain",
      "explicit unresolved provider/model uncertainty",
      "consumer-facing event/state contract",
      "unchanged historical evidence with additive status observation"
    ],
    "conditional_dependencies": [],
    "independent_review": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
    "resource_allowance": {
      "cpu_s": null,
      "wall_s": null,
      "memory_bytes": null,
      "status": "UNALLOCATED_BY_THIS_PROSPECTIVE_PLAN",
      "reset_or_borrow_historical": false
    },
    "parent_containment": "REC-HISTORY",
    "input_dependencies": [
      {
        "kind": "completed_source_artifact",
        "unit": "REC-HISTORY-PB01",
        "repository": "cosmosapjw-quantum/rec_bianchi",
        "commit": "ea89c97abeb7a663a813f00e9aadddaf0b32a6a9",
        "path": "research/rec_history_pullback_20261025/NEXT_INPUT_CONTRACT.md",
        "status": "COMPLETE_SCOPED_SOURCE_HISTORY_PULLBACK"
      },
      {
        "kind": "completed_source_artifact",
        "unit": "REC-HISTORY-KS01",
        "repository": "cosmosapjw-quantum/rec_bianchi",
        "commit": "f9edbfe7b56ad002f1b7fb35d4c5aec4970682a4",
        "science_commit": "309776ec263f10853a7ed4c404387c1474994e96",
        "status": "COMPLETE_SCOPED_SAME_SOURCE_KS_AND_ACTUAL_HISTORY_ADMISSION"
      },
      {
        "kind": "immutable_input",
        "name": "original_source_history",
        "sha256": "d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1",
        "bytes": 35239470,
        "queries": 313,
        "prefix": 5127,
        "status": "ACTUAL_PAYLOAD_ADMITTED"
      },
      {
        "kind": "actual_physical_input",
        "status": "INPUT_PENDING",
        "required": "source-matched endpoint/reference uncertainty or defect+tube+curvature bounds"
      }
    ],
    "readiness_rule": "Parent REC-HISTORY completion is not a prerequisite: this child supplies a remaining parent obligation. Reuse exact completed artifacts and bind only selected actual inputs."
  },
  "dependencies": [],
  "conditional_dependencies": [],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Same cosmology/reference/clock/source and actual L,defect,endpoint/curvature bounds",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "PASS_DERIVED_SCOPED",
  "claim_gate": "Assumptions checked and bounded numerical defects independent of stored h/2-h/4 agreement; physical epsilon remainsnull until inputs",
  "pass_next_action": "Feed actual eps to existing Ks/PB01, affected uncertainty propagation only",
  "budget_status": "Analytic derivation now; no new RHS/IVP/certification run; new cap required for finite proof artifact",
  "change_class": [
    "scope_expansion",
    "new_result"
  ],
  "historical_contract_id": null,
  "source_fields": {
    "lead_repo": "lead_repo",
    "current_status": "status",
    "claim_gate": "claim_gate",
    "pass_next_action": "pass_next",
    "budget_status": "budget"
  },
  "status_observation": {
    "source_file": "authority/ROOT_ASSEMBLY_OBSERVATIONS.json",
    "json_pointer": "/REC-H5-DEFECT-BOUND01",
    "value": {
      "current_status": "PASS_DERIVED_SCOPED",
      "implementation_status": "NOT_RUN",
      "physical_epsilon": null,
      "physical_H5_status": "INPUT_DEPENDENT_UNCALIBRATED",
      "review": "authority/REC_H5_INDEPENDENT_REVIEW.md",
      "reviewed_source": "authority/thermal/REC_H5_DEFECT_BOUND01_DERIVATION.md",
      "reviewed_source_sha256": "e4dc39a4d142a5baea3458b8a68ca2d68ce7aed0a1537c6160401c646258169b",
      "scope": "Conditional defect/stability/tube to endpoint/interpolation/frozen-response derivation only; no physical epsilon or runtime admission"
    }
  },
  "parent_containment": "REC-HISTORY",
  "pr_plan": {
    "inputs": {
      "value": "Same cosmology/reference/clock/source and actual L,defect,endpoint/curvature bounds",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/4/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "e(t)<=exp(Ldt)e0+integral exp(L(t-s))r(s)ds; eps_j<=(1-a)eL+a eR+M2 h²/8; |delta o|<=|Ks|eps",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/4/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/4/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Original z~1100 eta history; source-matched forward solution/defect",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/4/provider_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "source-qualified result within stated domain",
        "explicit unresolved provider/model uncertainty",
        "consumer-facing event/state contract",
        "unchanged historical evidence with additive status observation"
      ],
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/4/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "Assumptions checked and bounded numerical defects independent of stored h/2-h/4 agreement; physical epsilon remainsnull until inputs",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/4/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/4/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/4/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": [
        "research/program_expansion_20261025/**"
      ],
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/allowed_paths",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
