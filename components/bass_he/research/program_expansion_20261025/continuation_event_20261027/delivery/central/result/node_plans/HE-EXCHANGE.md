# HE-EXCHANGE

Lead: cosmosapjw-quantum/BASS_HE

Current status: `SOURCE_INTAKE_AND_CONDITIONAL_IMPLEMENTATION_VERIFIED_PHYSICAL_BINDING_PENDING`

Source: `authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json#/nodes/2`

```json
{
  "id": "HE-EXCHANGE",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
  "json_pointer": "/nodes/2",
  "contract": {
    "id": "HE-EXCHANGE",
    "status": "PROPOSED_SOURCE_INPUT_PENDING",
    "depends_on": [],
    "equations_scope": "Sum species momentum/energy exchange=0; tensor collision rate differs from event frequency",
    "inputs_domain": "All seven isotope nuclei/allq+e/n and selected molecular partners; e-neutral/e-ion/ion-neutral/ion-ion",
    "claim_gates": [
      "One admitted differential pair source,domain/uncertainty,timescale; HE35 conditional pair reused"
    ],
    "pass_action": "Coefficients/error to HE-CLOSURE",
    "budget": "New pair cap pending; oldHE34/35 no replay",
    "fail_action": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
    "review": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
    "tests": "Same-source contract controls and affected derivative/conservation tests only; original tolerance preserved",
    "conditional_dependencies": []
  },
  "dependencies": [],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "SOURCE_INTAKE_AND_CONDITIONAL_IMPLEMENTATION_VERIFIED_PHYSICAL_BINDING_PENDING",
  "claim_gate": [
    "One admitted differential pair source,domain/uncertainty,timescale; HE35 conditional pair reused"
  ],
  "pass_next_action": "Coefficients/error to HE-CLOSURE",
  "budget_status": "New pair cap pending; oldHE34/35 no replay",
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "HE-EXCHANGE",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "claim_gates",
    "pass_next_action": "pass_action",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "All seven isotope nuclei/allq+e/n and selected molecular partners; e-neutral/e-ion/ion-neutral/ion-ion",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/2/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "Sum species momentum/energy exchange=0; tensor collision rate differs from event frequency",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/2/equations_scope",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "All seven isotope nuclei/allq+e/n and selected molecular partners; e-neutral/e-ion/ion-neutral/ion-ion",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/2/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "positive_acceptance": {
      "value": [
        "One admitted differential pair source,domain/uncertainty,timescale; HE35 conditional pair reused"
      ],
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/2/claim_gates",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/2/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/2/review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
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
  },
  "status_observation": {
    "source_file": "status/HE_EXP_FINITE_DRIFT_20261027.json",
    "json_pointer": "/observations/HE-EXCHANGE",
    "value": {
      "unit_id": "HE-EXP-DRIFT-02",
      "current_scoped_state": "SOURCE_INTAKE_AND_CONDITIONAL_IMPLEMENTATION_VERIFIED_PHYSICAL_BINDING_PENDING",
      "scoped_contribution": "Conditional same-law finite-drift linear force and quadratic centered heat verified with exact kinetic-energy ownership; physical source binding and calibrated uncertainty remain pending.",
      "source_intake": {
        "source_file": "status/HE_EXP_FINITE_DRIFT_20261027.json",
        "json_pointer": "/source_intake"
      },
      "source_repository": "cosmosapjw-quantum/BASS_HE",
      "source_commit": "76beebc67493c7d931fa3eea35a1d3f362a55805",
      "source_publication_status": "LOCAL_PREPARED_NOT_PUBLISHED",
      "source_published": false,
      "physical_provider_admitted": false,
      "production_status": "NOT_APPROVED",
      "activation": false,
      "physical_allocation": "UNALLOCATED"
    }
  }
}
```

## HE-EXP-EVENT-03 observation

Conditional raw reactive number, momentum, kinetic energy and full second-moment stress contributions for a supplied 2-to-2 event. Source is locally prepared and unpublished; physical inputs remain open. See `status/HE_EXP_EVENT03_20261027.json#/observations/HE-EXCHANGE`.
