# HE-EXP-PAIR

Lead: cosmosapjw-quantum/BASS_HE

Current status: `SOURCE_INTAKE_AND_CONDITIONAL_IMPLEMENTATION_VERIFIED_PHYSICAL_BINDING_PENDING`

Source: `authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/2`

```json
{
  "id": "HE-EXP-PAIR",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/2",
  "contract": {
    "id": "HE-EXP-PAIR",
    "status": "SOURCE_INPUT_PENDING",
    "depends_on": [
      "HE-EXP-SPECIES"
    ],
    "provider_domain": "e-neutral/e-ion/ion-neutral/ion-ion and molecular internal exchange",
    "equations": "sum R_s=0,sum(Q_s+u_s dot R_s)=0 using declared energy convention",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/BASS_HE",
    "prerequisites": "Actual transport crosssection,thermal/nonthermal distributions,domain",
    "claim_gate": "l2 relaxation distinct from event rate;HE35 conditionalkappa reused;sourceuncertainty calibrated",
    "pass_next": "Coefficient tensor toHE-CLOSURE",
    "budget": "One pair first;no large allpair scan",
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
    "conditional_dependencies": [],
    "independent_review": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
    "resource_allowance": {
      "cpu_s": null,
      "wall_s": null,
      "memory_bytes": null,
      "status": "UNALLOCATED_BY_THIS_PROSPECTIVE_PLAN",
      "reset_or_borrow_historical": false
    }
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "HE-EXP-SPECIES",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Actual transport crosssection,thermal/nonthermal distributions,domain",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "SOURCE_INTAKE_AND_CONDITIONAL_IMPLEMENTATION_VERIFIED_PHYSICAL_BINDING_PENDING",
  "claim_gate": "l2 relaxation distinct from event rate;HE35 conditionalkappa reused;sourceuncertainty calibrated",
  "pass_next_action": "Coefficient tensor toHE-CLOSURE",
  "budget_status": "One pair first;no large allpair scan",
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
      "value": "Actual transport crosssection,thermal/nonthermal distributions,domain",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "sum R_s=0,sum(Q_s+u_s dot R_s)=0 using declared energy convention",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "e-neutral/e-ion/ion-neutral/ion-ion and molecular internal exchange",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/provider_domain",
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
      "json_pointer": "/tasks/2/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "l2 relaxation distinct from event rate;HE35 conditionalkappa reused;sourceuncertainty calibrated",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/independent_review",
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
    "source_file": "status/HE_EXP_INTAKE01_20261025.json",
    "json_pointer": "/observations/HE-EXP-PAIR",
    "value": {
      "unit_id": "HE-EXP-INTAKE-01",
      "current_scoped_state": "SOURCE_INTAKE_AND_CONDITIONAL_IMPLEMENTATION_VERIFIED_PHYSICAL_BINDING_PENDING",
      "scoped_contribution": "Source intake and conditional pair implementation verified; source isotope/state/mass, actual Q value and calibrated uncertainty pending.",
      "source_intake": {
        "source_file": "status/HE_EXP_INTAKE01_20261025.json",
        "json_pointer": "/source_intake"
      },
      "source_repository": "cosmosapjw-quantum/BASS_HE",
      "source_commit": "965da72aa7a5e885e12956fafadfb8dc2519b81f",
      "physical_provider_admitted": false,
      "production_status": "NOT_APPROVED",
      "activation": false,
      "physical_allocation": "UNALLOCATED"
    }
  }
}
```
