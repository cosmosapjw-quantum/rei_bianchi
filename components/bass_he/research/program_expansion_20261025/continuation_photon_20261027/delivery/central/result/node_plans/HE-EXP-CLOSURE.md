# HE-EXP-CLOSURE

Lead: cosmosapjw-quantum/BASS_HE

Current status: `CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING`

Source: `authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/6`

```json
{
  "id": "HE-EXP-CLOSURE",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/6",
  "contract": {
    "id": "HE-EXP-CLOSURE",
    "status": "GATED",
    "depends_on": [],
    "provider_domain": "Allspecies gas+nonthermal populations; molecules internal modes",
    "equations": "pi_b=sum[pi_s+rho_s driftSTF]; Uth=sum(3/2)n_s kBT_s+U_internal;liftcommutator",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/BASS_HE",
    "prerequisites": "Species timescales/source/relaxation uncertainty and observables",
    "claim_gate": "CommonT/u requires calibrated reduction; particlecount/heatcapacity separate",
    "pass_next": "Saved-background finitegas thenHE-FEEDBACK",
    "budget": "NoIVP authorized",
    "tests": "Only affected source/state/measure/units/conservation/tangent checks; original numerical tolerance retained; no unchangedsuite replay",
    "fail_action": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
    "uncertainty": "Provider/model/interpolation/quadrature/floating error separate; null until actual evidence",
    "units": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
    "lead_repo": "cosmosapjw-quantum/BASS_HE",
    "consumer_repo": "cosmosapjw-quantum/BASS_HE",
    "outputs": [
      "source-qualified result within stated domain",
      "explicit unresolved provider/model uncertainty",
      "consumer-facing event/state contract",
      "unchanged historical evidence with additive status observation"
    ],
    "conditional_dependencies": [
      {
        "id": "HE-EXP-PAIR",
        "predicate": "selected_reduction_uses_pair_exchange"
      },
      {
        "id": "HE-EXP-STOPPING",
        "predicate": "selected_model_has_nonthermal_stopping"
      },
      {
        "id": "HE-RESERVOIR",
        "predicate": "selected_model_has_external_injection"
      }
    ],
    "independent_review": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
    "resource_allowance": {
      "cpu_s": null,
      "wall_s": null,
      "memory_bytes": null,
      "status": "UNALLOCATED_BY_THIS_PROSPECTIVE_PLAN",
      "reset_or_borrow_historical": false
    }
  },
  "dependencies": [],
  "conditional_dependencies": [
    {
      "id": "HE-EXP-PAIR",
      "predicate": "selected_reduction_uses_pair_exchange",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    },
    {
      "id": "HE-EXP-STOPPING",
      "predicate": "selected_model_has_nonthermal_stopping",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    },
    {
      "id": "HE-RESERVOIR",
      "predicate": "selected_model_has_external_injection",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    }
  ],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Species timescales/source/relaxation uncertainty and observables",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
  "claim_gate": "CommonT/u requires calibrated reduction; particlecount/heatcapacity separate",
  "pass_next_action": "Saved-background finitegas thenHE-FEEDBACK",
  "budget_status": "NoIVP authorized",
  "change_class": [
    "scope_expansion"
  ],
  "historical_contract_id": null,
  "source_fields": {
    "lead_repo": "lead_repo",
    "current_status": "status",
    "claim_gate": "claim_gate",
    "pass_next_action": "pass_next",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "Species timescales/source/relaxation uncertainty and observables",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "pi_b=sum[pi_s+rho_s driftSTF]; Uth=sum(3/2)n_s kBT_s+U_internal;liftcommutator",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Allspecies gas+nonthermal populations; molecules internal modes",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/provider_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "source-qualified result within stated domain",
        "explicit unresolved provider/model uncertainty",
        "consumer-facing event/state contract",
        "unchanged historical evidence with additive status observation"
      ],
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "CommonT/u requires calibrated reduction; particlecount/heatcapacity separate",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": [
        "research/program_expansion_20261025/**"
      ],
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/allowed_paths",
      "qualification": "SOURCE_DECLARED"
    }
  },
  "status_observation": {
    "source_file": "status/HE_EXP_FINITE_DRIFT_20261027.json",
    "json_pointer": "/observations/HE-EXP-CLOSURE",
    "value": {
      "unit_id": "HE-EXP-DRIFT-02",
      "current_scoped_state": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
      "scoped_contribution": "Conditional same-law finite-drift linear force and quadratic centered heat verified with exact kinetic-energy ownership; reduction and physical closure inputs remain pending.",
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

Population-derived internal energy witness has a single owner; product birth pool remains UNASSIGNED. Source is locally prepared and unpublished; physical inputs remain open. See `status/HE_EXP_EVENT03_20261027.json#/observations/HE-EXP-CLOSURE`.

## HE-EXP-STATE-04 observation

Named scalar level-edge consumer retains internal energy witness ownership and UNASSIGNED birth pool; Bennett 2008 corrected rate selection supersedes, never adds to, the historical same-owner 2003 table. Source is locally prepared and unpublished; physical dependencies remain open. See `status/HE_EXP_STATE04_20261027.json#/observations/HE-EXP-CLOSURE`.

## HE-EXP-PHOTON-05 observation

Photon loss, population rest-energy witness and daughter kinetic energy close one event ledger; material nucleus count +1 remains distinct from Gamma_thermal, Cv, heating and deposition. Native zero-flux examples do not supply or set a physical rate. Core24 tests PASS; generated plot has a preserved CPU-cap FAIL, so the local workflow is partial. Source remains local/unpublished; no physical promotion. See `status/HE_EXP_PHOTON05_20261027.json#/observations/HE-EXP-CLOSURE`.
