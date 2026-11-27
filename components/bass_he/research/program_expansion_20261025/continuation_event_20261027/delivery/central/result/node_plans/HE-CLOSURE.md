# HE-CLOSURE

Lead: cosmosapjw-quantum/BASS_HE

Current status: `CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING`

Source: `authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json#/nodes/4`

```json
{
  "id": "HE-CLOSURE",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
  "json_pointer": "/nodes/4",
  "contract": {
    "id": "HE-CLOSURE",
    "status": "PROPOSED_INPUT_DEPENDENT",
    "depends_on": [],
    "equations_scope": "pi_b=sum_s(pi_s+rho_s(v_s-u_b)<i(v_s-u_b)j>); Uth=sum_s3n_s kBT_s/2; lift commutator bounded",
    "inputs_domain": "Species temperature/bulk distributions or justified common closure; nonthermal kinetic stress separate",
    "claim_gates": [
      "Timescale/observable error validates reduction; changing particle count; birth kinetic≠heating"
    ],
    "pass_action": "One saved-background gas control",
    "budget": "NoIVP; own bounded cap pending",
    "fail_action": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
    "review": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
    "tests": "Same-source contract controls and affected derivative/conservation tests only; original tolerance preserved",
    "historical_source_dependencies": [
      "HE-ANG",
      "HE-EXCHANGE",
      "HE-RESERVOIR"
    ],
    "conditional_dependencies": [
      {
        "id": "HE-ANG",
        "predicate": "selected_claim_requires_angular_or_anisotropic_injection",
        "scope": "selected-model prerequisite only"
      },
      {
        "id": "HE-EXCHANGE",
        "predicate": "selected_closure_uses_finite_mass_collisional_relaxation",
        "scope": "selected-model prerequisite only"
      },
      {
        "id": "HE-RESERVOIR",
        "predicate": "selected_model_has_external_or_birth_injection",
        "scope": "selected-model prerequisite only"
      }
    ],
    "dependency_change": "2026-10-25 current readiness correction; original source contracts preserved in EVIDENCE_FILTERED"
  },
  "dependencies": [],
  "conditional_dependencies": [
    {
      "id": "HE-ANG",
      "predicate": "selected_claim_requires_angular_or_anisotropic_injection",
      "scope": "selected-model prerequisite only",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "source_field": "conditional_dependencies"
    },
    {
      "id": "HE-EXCHANGE",
      "predicate": "selected_closure_uses_finite_mass_collisional_relaxation",
      "scope": "selected-model prerequisite only",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "source_field": "conditional_dependencies"
    },
    {
      "id": "HE-RESERVOIR",
      "predicate": "selected_model_has_external_or_birth_injection",
      "scope": "selected-model prerequisite only",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "source_field": "conditional_dependencies"
    }
  ],
  "external_prerequisites": [],
  "current_status": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
  "claim_gate": [
    "Timescale/observable error validates reduction; changing particle count; birth kinetic≠heating"
  ],
  "pass_next_action": "One saved-background gas control",
  "budget_status": "NoIVP; own bounded cap pending",
  "change_class": [
    "status_correction",
    "dependency_change"
  ],
  "historical_contract_id": "HE-CLOSURE",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "claim_gates",
    "pass_next_action": "pass_action",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "Species temperature/bulk distributions or justified common closure; nonthermal kinetic stress separate",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/4/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "pi_b=sum_s(pi_s+rho_s(v_s-u_b)<i(v_s-u_b)j>); Uth=sum_s3n_s kBT_s/2; lift commutator bounded",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/4/equations_scope",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "Species temperature/bulk distributions or justified common closure; nonthermal kinetic stress separate",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/4/inputs_domain",
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
        "Timescale/observable error validates reduction; changing particle count; birth kinetic≠heating"
      ],
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/4/claim_gates",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/4/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/4/review",
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
    "json_pointer": "/observations/HE-CLOSURE",
    "value": {
      "unit_id": "HE-EXP-DRIFT-02",
      "current_scoped_state": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
      "scoped_contribution": "Inherited thermal-count, heat-capacity, binding-energy and nonthermal-energy boundaries retained; new elastic drift-work ownership check verified within the conditional implementation.",
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

Conditional reactive population count and centered heat contribution; heat capacity remains separate and no automatic thermalization is assumed. Source is locally prepared and unpublished; physical inputs remain open. See `status/HE_EXP_EVENT03_20261027.json#/observations/HE-CLOSURE`.
