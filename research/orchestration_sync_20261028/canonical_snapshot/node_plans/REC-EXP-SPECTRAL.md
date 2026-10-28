# REC-EXP-SPECTRAL

Lead: cosmosapjw-quantum/rec_bianchi

Current status: `SOURCE_INPUT_PENDING`

Source: `authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/2`

```json
{
  "id": "REC-EXP-SPECTRAL",
  "lead_repo": "cosmosapjw-quantum/rec_bianchi",
  "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/2",
  "contract": {
    "id": "REC-EXP-SPECTRAL",
    "status": "SOURCE_INPUT_PENDING",
    "depends_on": [
      "REC-EXP-SPECIES"
    ],
    "provider_domain": "bb,bf,fb,ff,two-photon,Raman,stimulated/spontaneous,molecular opacity/emission",
    "equations": "dU_band=E_volume+F_in-F_out; j_nu-kappa_nu I_nu",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/rec_bianchi",
    "prerequisites": "Same-frame spectral density/occupation, frequency grid, measures,count and references",
    "claim_gate": "Units+detailed-balance where applicable+energy partner+band interfaces; native Lyalpha exclusive",
    "pass_next": "One actual source residual/JVP to REC-FIELD",
    "budget": "Frozen one-cell/one-event analytic controls; numerical cap pending",
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
    }
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "REC-EXP-SPECIES",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Same-frame spectral density/occupation, frequency grid, measures,count and references",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "SOURCE_INPUT_PENDING",
  "claim_gate": "Units+detailed-balance where applicable+energy partner+band interfaces; native Lyalpha exclusive",
  "pass_next_action": "One actual source residual/JVP to REC-FIELD",
  "budget_status": "Frozen one-cell/one-event analytic controls; numerical cap pending",
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
      "value": "Same-frame spectral density/occupation, frequency grid, measures,count and references",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "dU_band=E_volume+F_in-F_out; j_nu-kappa_nu I_nu",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "bb,bf,fb,ff,two-photon,Raman,stimulated/spontaneous,molecular opacity/emission",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
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
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "Units+detailed-balance where applicable+energy partner+band interfaces; native Lyalpha exclusive",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/2/independent_review",
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
