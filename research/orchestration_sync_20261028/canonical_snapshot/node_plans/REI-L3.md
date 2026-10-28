# REI-L3

Lead: cosmosapjw-quantum/rei_bianchi

Current status: `PARTIAL_MOMENT_CONSTRUCTIONS_PHYSICAL_BARYON_TRANSPORT_OPEN`

Source: `historical/baseline/rei/CONTRACTS.json#/nodes/3`

```json
{
  "id": "REI-L3",
  "lead_repo": "cosmosapjw-quantum/rei_bianchi",
  "source_file": "historical/baseline/rei/CONTRACTS.json",
  "json_pointer": "/nodes/3",
  "contract": {
    "repository": "cosmosapjw-quantum/rei_bianchi",
    "authority": "REI scientific authority; independent review required",
    "publication_target": {
      "branch": "research/orchestration-sandbox-20261022",
      "base": "b4b5d289aaad9ef167f683f19418b0ff87ed8425",
      "path": "research/orchestration_longterm_20261023",
      "mode": "central additive master contracts; future leaf code not executed now"
    },
    "no_replay": [
      "ANGTHERM01 completed10",
      "ANGTHERM02 active owner cases",
      "C3 atomic156+separate2",
      "localflow103+separate96",
      "D10 saved35",
      "PR220127+2 cases"
    ],
    "units": {
      "clock": "proper seconds; eta via d/deta=H^-1 d/dt",
      "energy": "eV per Href with explicit SI conversion",
      "stress": "physical tensor=nHref * eV_to_J * perHref tensor",
      "metric": "(-,+,+,+)",
      "shear_norm": "full Frobenius"
    },
    "id": "REI-L3",
    "dependencies": [
      "external:BASS_HE_FINITE_MASS_TRANSPORT",
      "external:X1_HE38_ANGULAR_PSD_REVIEW",
      "external:BASS_MASSIVE_COMPONENT_MAP"
    ],
    "title": "Baryonic material pressure with separate collisionless matter",
    "status": "CONDITIONAL_MOMENT_MODELS_PHYSICAL_TRANSPORT_OPEN",
    "owner": "BASS_HE physical baryon closure; REI assembly; BASS collisionless nonbaryonic component",
    "scope": "Optional anisotropic baryonic gas, not relabeling D10 massive stress",
    "allowed_paths": [
      "research/rei_baryon_pressure_binding/**"
    ],
    "input_sources": [
      "D10 scientific67205cb9a9fc3e36b959e584d3e06c74bdfbbf5e reused",
      "external:HE38 exact authority survey pins"
    ],
    "acceptance": [
      "pair total momentum/energy conservation",
      "pressure PSD necessary gate",
      "appropriate equilibrium and relaxation",
      "l2 transport cross section not event frequency",
      "signed stress sum and Frobenius norm",
      "kinetic closure/source validity separately admitted"
    ],
    "claim_limit": "Finite supported baryon moment model; X1 necessary cone is not full realizability or empirical transport",
    "budget": {
      "type": "small matrices/scalars only",
      "cumulative_cap": "inherit actual HE owner ledger; freeze before execution",
      "new_ivps": 0
    },
    "pass_next": "REI-L4 optional anisotropic-baryon variant",
    "failure_action": "Keep explicit isotropic pi_b=0 smaller model available"
  },
  "dependencies": [
    {
      "type": "external",
      "source_reference": "external:BASS_HE_FINITE_MASS_TRANSPORT",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "source_field": "dependencies"
    },
    {
      "type": "external",
      "source_reference": "external:X1_HE38_ANGULAR_PSD_REVIEW",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "source_field": "dependencies"
    },
    {
      "type": "external",
      "source_reference": "external:BASS_MASSIVE_COMPONENT_MAP",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "source_field": "dependencies"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PARTIAL_MOMENT_CONSTRUCTIONS_PHYSICAL_BARYON_TRANSPORT_OPEN",
  "claim_gate": [
    "pair total momentum/energy conservation",
    "pressure PSD necessary gate",
    "appropriate equilibrium and relaxation",
    "l2 transport cross section not event frequency",
    "signed stress sum and Frobenius norm",
    "kinetic closure/source validity separately admitted"
  ],
  "pass_next_action": "REI-L4 optional anisotropic-baryon variant",
  "budget_status": {
    "type": "small matrices/scalars only",
    "cumulative_cap": "inherit actual HE owner ledger; freeze before execution",
    "new_ivps": 0
  },
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "REI-L3",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "acceptance",
    "pass_next_action": "pass_next",
    "budget_status": "budget"
  },
  "status_observation": {
    "source_file": "authority/rei/DAG_DELTA.json",
    "json_pointer": "/observations/REI-L3",
    "value": {
      "current_scoped_state": "PARTIAL_MOMENT_CONSTRUCTIONS_PHYSICAL_BARYON_TRANSPORT_OPEN",
      "HI_strain_is_source_cohort_derivative_not_full_transport": true
    }
  },
  "pr_plan": {
    "inputs": {
      "value": [
        "D10 scientific67205cb9a9fc3e36b959e584d3e06c74bdfbbf5e reused",
        "external:HE38 exact authority survey pins"
      ],
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/3/input_sources",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": null,
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "units": {
      "value": {
        "clock": "proper seconds; eta via d/deta=H^-1 d/dt",
        "energy": "eV per Href with explicit SI conversion",
        "stress": "physical tensor=nHref * eV_to_J * perHref tensor",
        "metric": "(-,+,+,+)",
        "shear_norm": "full Frobenius"
      },
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/3/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Optional anisotropic baryonic gas, not relabeling D10 massive stress",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/3/scope",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": "Optional anisotropic baryonic gas, not relabeling D10 massive stress",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/3/scope",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "pair total momentum/energy conservation",
        "pressure PSD necessary gate",
        "appropriate equilibrium and relaxation",
        "l2 transport cross section not event frequency",
        "signed stress sum and Frobenius norm",
        "kinetic closure/source validity separately admitted"
      ],
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/3/acceptance",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Keep explicit isotropic pi_b=0 smaller model available",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/3/failure_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": null,
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "PR_boundary": {
      "value": [
        "research/rei_baryon_pressure_binding/**"
      ],
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/3/allowed_paths",
      "qualification": "SOURCE_DECLARED"
    }
  },
  "runnable": false,
  "missing_contract_fields": [
    "equations",
    "independent_review"
  ],
  "execution_readiness_guard": {
    "source_file": "authority/FINAL_ASSEMBLY_MISSING_FIELDS.json",
    "scope": "Execution-readiness guard only; retain finite past admissions and source object unchanged",
    "other_nodes_runnable_not_inferred": true
  }
}
```
