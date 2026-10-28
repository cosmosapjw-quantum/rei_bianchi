# REC-EXP-COUPLED

Lead: cosmosapjw-quantum/rec_bianchi

Current status: `GATED`

Source: `authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/7`

```json
{
  "id": "REC-EXP-COUPLED",
  "lead_repo": "cosmosapjw-quantum/rec_bianchi",
  "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/7",
  "contract": {
    "id": "REC-EXP-COUPLED",
    "status": "GATED",
    "depends_on": [
      "REC-COUPLED"
    ],
    "provider_domain": "Selected-source all-species network and history/thermal state",
    "equations": "Full coupled residual/JVP; signed matter/radiation stress retained",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/rec_bianchi",
    "prerequisites": "Closed selected channels only,IC,observable/error allocation",
    "claim_gate": "No global completion from finite pilot;nohistoricalU5reset",
    "pass_next": "One new bounded selected control",
    "budget": "NOT_SCHEDULED",
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
    "conditional_dependencies": [
      {
        "id": "REC-EXP-SPECTRAL",
        "predicate": "selected_scenario_uses_new_spectral_channel"
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
  "dependencies": [
    {
      "type": "internal",
      "id": "REC-COUPLED",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [
    {
      "id": "REC-EXP-SPECTRAL",
      "predicate": "selected_scenario_uses_new_spectral_channel",
      "type": "internal",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    }
  ],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Closed selected channels only,IC,observable/error allocation",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "GATED",
  "claim_gate": "No global completion from finite pilot;nohistoricalU5reset",
  "pass_next_action": "One new bounded selected control",
  "budget_status": "NOT_SCHEDULED",
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
      "value": "Closed selected channels only,IC,observable/error allocation",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/7/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "Full coupled residual/JVP; signed matter/radiation stress retained",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/7/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/7/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Selected-source all-species network and history/thermal state",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/7/provider_domain",
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
      "json_pointer": "/tasks/7/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "No global completion from finite pilot;nohistoricalU5reset",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/7/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/7/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/7/independent_review",
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
