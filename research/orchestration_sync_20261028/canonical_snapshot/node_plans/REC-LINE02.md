# REC-LINE02

Lead: cosmosapjw-quantum/rec_bianchi

Current status: `COMPLETE_SCOPED_REUSE`

Source: `authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json#/nodes/0`

```json
{
  "id": "REC-LINE02",
  "lead_repo": "cosmosapjw-quantum/rec_bianchi",
  "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
  "json_pointer": "/nodes/0",
  "contract": {
    "id": "REC-LINE02",
    "status": "COMPLETE_SCOPED_REUSE",
    "depends_on": [],
    "equations_scope": "M*=M+delta_r ee^T; s*=s+delta_rb e; direct Lya once, native virtual/history untouched",
    "inputs_domain": "One z~1100 native313 source",
    "claim_gates": [
      "Reuse194checks; rank/full5e-10,backward5e-12,JVP5e-9,64eps conserved"
    ],
    "pass_action": "REC-HISTORY or REC-FIELD only for selected native source",
    "budget": "Original execution consumed; no replay",
    "fail_action": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
    "review": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
    "tests": "Same-source contract controls and affected derivative/conservation tests only; original tolerance preserved",
    "conditional_dependencies": []
  },
  "dependencies": [],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "COMPLETE_SCOPED_REUSE",
  "claim_gate": [
    "Reuse194checks; rank/full5e-10,backward5e-12,JVP5e-9,64eps conserved"
  ],
  "pass_next_action": "REC-HISTORY or REC-FIELD only for selected native source",
  "budget_status": "Original execution consumed; no replay",
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "REC-LINE02",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "claim_gates",
    "pass_next_action": "pass_action",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "One z~1100 native313 source",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/0/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "M*=M+delta_r ee^T; s*=s+delta_rb e; direct Lya once, native virtual/history untouched",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/0/equations_scope",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "historical/baseline/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "One z~1100 native313 source",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/0/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": null,
      "source_file": "historical/baseline/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "positive_acceptance": {
      "value": [
        "Reuse194checks; rank/full5e-10,backward5e-12,JVP5e-9,64eps conserved"
      ],
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/0/claim_gates",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/0/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/0/review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": null,
      "source_file": "historical/baseline/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    }
  },
  "runnable": false,
  "missing_contract_fields": [
    "units",
    "outputs",
    "PR_boundary"
  ],
  "execution_readiness_guard": {
    "source_file": "authority/FINAL_ASSEMBLY_MISSING_FIELDS.json",
    "scope": "Execution-readiness guard only; retain finite past admissions and source object unchanged",
    "other_nodes_runnable_not_inferred": true
  }
}
```
