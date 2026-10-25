# D2-stage-domain

Lead: cosmosapjw-quantum/vigilode

Current status: `COMPLETE_SCOPED_REUSED`

Source: `authority/numerics/VIGILODE_CONTRACTS.json#/nodes/3`

```json
{
  "id": "D2-stage-domain",
  "lead_repo": "cosmosapjw-quantum/vigilode",
  "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
  "json_pointer": "/nodes/3",
  "contract": {
    "id": "D2-stage-domain",
    "status": "COMPLETE_SCOPED_REUSED",
    "dependencies": [
      "D1-endpoint-domain"
    ],
    "scope": "Pre-RHS domain guard, partial-work accounting, bounded Session attempts.",
    "evidence": [
      "PR85 1c829f206ab67585191231be7f5135fd0d4c804e"
    ],
    "source_status": "PINNED_SELECTED_CONTENT_OR_NAMED_REUSED_EVIDENCE",
    "execution_status": "EXISTING_EVIDENCE_REUSED; NEW_EXECUTION_NOT_RUN",
    "admission_status": "COMPLETE_SCOPED_REUSED",
    "delivery_status": "Pinned Draft/publication and provider receipts separate; production HOLD",
    "remaining": "Scalar-linear[0,2] theorem only; nonlinear cap heuristic; arbitrary model binding open.",
    "pr_boundary": "Reuse Session/abort_stage/stage guard; no old12trajectory replay.",
    "equations": [
      "All8stored-tableau stage multipliers and endpoint in[0,1] for scalar decayh*lambda in[0,2]"
    ],
    "acceptance": [
      "15new+31regression tests",
      " unsafe diagnostic507forbiddenRHS, guarded0",
      " all spent attempts retained"
    ],
    "pass_action": "Bind actual callback domain with D5 and model derivative.",
    "owner": "VigilODE numerical engine authority; physical input/Jacobian supplied by BASS/REI/atomic owner; current native implementer reservation preserved"
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "D1-endpoint-domain",
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "source_field": "dependencies"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "COMPLETE_SCOPED_REUSED",
  "claim_gate": [
    "15new+31regression tests",
    " unsafe diagnostic507forbiddenRHS, guarded0",
    " all spent attempts retained"
  ],
  "pass_next_action": "Bind actual callback domain with D5 and model derivative.",
  "budget_status": {
    "source_review_new": true,
    "scientific_execution_this_audit": "NOT_RUN",
    "ncp": false,
    "heavy_runs": false,
    "completed_campaign_replay": false,
    "new_allowance_granted": false,
    "remaining_wall": null,
    "remaining_cpu": null,
    "budget_reset": false,
    "ownership": "Existing native/REC/history/HE/atomic owners retain active work and dirty files. New adapter work only in assigned isolated lane of existing checkout.",
    "roles": "Astra frames and admits; lower-tier implements frozen contract; a distinct Astra reviews diff/raw. Requested role is not evidence of observed model identity.",
    "publication": "central plan update only by root; this authority makes no remote mutations"
  },
  "change_class": [
    "scope_expansion"
  ],
  "historical_contract_id": null,
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "acceptance",
    "pass_next_action": "pass_action",
    "budget_status": "policy"
  },
  "pr_plan": {
    "inputs": {
      "value": null,
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "equations": {
      "value": [
        "All8stored-tableau stage multipliers and endpoint in[0,1] for scalar decayh*lambda in[0,2]"
      ],
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "Pre-RHS domain guard, partial-work accounting, bounded Session attempts.",
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/scope",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": "Pre-RHS domain guard, partial-work accounting, bounded Session attempts.",
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/scope",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "15new+31regression tests",
        " unsafe diagnostic507forbiddenRHS, guarded0",
        " all spent attempts retained"
      ],
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/acceptance",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": null,
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "independent_review": {
      "value": "Astra frames and admits; lower-tier implements frozen contract; a distinct Astra reviews diff/raw. Requested role is not evidence of observed model identity.",
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": "/policy/roles",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": "Reuse Session/abort_stage/stage guard; no old12trajectory replay.",
      "source_file": "authority/numerics/VIGILODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/pr_boundary",
      "qualification": "SOURCE_DECLARED"
    }
  },
  "runnable": false,
  "missing_contract_fields": [
    "inputs",
    "units",
    "failure_disposition"
  ],
  "execution_readiness_guard": {
    "source_file": "authority/FINAL_ASSEMBLY_MISSING_FIELDS.json",
    "scope": "Execution-readiness guard only; retain finite past admissions and source object unchanged",
    "other_nodes_runnable_not_inferred": true
  }
}
```
