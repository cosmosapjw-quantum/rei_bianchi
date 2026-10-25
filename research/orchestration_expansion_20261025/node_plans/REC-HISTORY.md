# REC-HISTORY

Lead: cosmosapjw-quantum/rec_bianchi

Current status: `PARTIAL; PB01/KS01/THERMO01 complete_scoped`

Source: `authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json#/nodes/1`

```json
{
  "id": "REC-HISTORY",
  "lead_repo": "cosmosapjw-quantum/rec_bianchi",
  "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
  "json_pointer": "/nodes/1",
  "contract": {
    "id": "REC-HISTORY",
    "status": "PARTIAL; PB01/KS01/THERMO01 complete_scoped",
    "depends_on": [
      "REC-LINE02"
    ],
    "equations_scope": "do=Js Dtheta+Ks P DY+Ks diag(g) DQ+dreference; r_j=xi_j(dy_R-dy_L)/h",
    "inputs_domain": "Same actual z1099.9986525171403,T0=2.728K,nH0=.18745798773143102m^-3,prefix5127,313queries,626slots",
    "claim_gates": [
      "H5 physical source-matched reference/bounds;H6 actual geometry/frame/clock trace;H7 actual derivative owners"
    ],
    "pass_action": "Bind one actual H5/H6 provider then affected H7 composition check",
    "budget": "No solve/IVP/new cap yet; PB01 remainder not portable",
    "fail_action": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
    "review": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
    "tests": "Same-source contract controls and affected derivative/conservation tests only; original tolerance preserved",
    "conditional_dependencies": []
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "REC-LINE02",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PARTIAL; PB01/KS01/THERMO01 complete_scoped",
  "claim_gate": [
    "H5 physical source-matched reference/bounds;H6 actual geometry/frame/clock trace;H7 actual derivative owners"
  ],
  "pass_next_action": "Bind one actual H5/H6 provider then affected H7 composition check",
  "budget_status": "No solve/IVP/new cap yet; PB01 remainder not portable",
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "REC-HISTORY",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "claim_gates",
    "pass_next_action": "pass_action",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "Same actual z1099.9986525171403,T0=2.728K,nH0=.18745798773143102m^-3,prefix5127,313queries,626slots",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "do=Js Dtheta+Ks P DY+Ks diag(g) DQ+dreference; r_j=xi_j(dy_R-dy_L)/h",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/equations_scope",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "historical/baseline/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "Same actual z1099.9986525171403,T0=2.728K,nH0=.18745798773143102m^-3,prefix5127,313queries,626slots",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/inputs_domain",
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
        "H5 physical source-matched reference/bounds;H6 actual geometry/frame/clock trace;H7 actual derivative owners"
      ],
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/claim_gates",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/review",
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
