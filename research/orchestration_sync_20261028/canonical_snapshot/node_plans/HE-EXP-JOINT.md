# HE-EXP-JOINT

Lead: cosmosapjw-quantum/BASS_HE

Current status: `SOURCE_INPUT_PENDING`

Source: `authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/1`

```json
{
  "id": "HE-EXP-JOINT",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/1",
  "contract": {
    "id": "HE-EXP-JOINT",
    "status": "SOURCE_INPUT_PENDING",
    "depends_on": [
      "HE-EXP-SPECIES",
      "HE-X1"
    ],
    "provider_domain": "Alltarget impact/photoelectron daughter events and correlated recoil",
    "equations": "pion=pin-p1-p2; ionSTF requires C12 same-law cross moment",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/BASS_HE",
    "prerequisites": "Differential measure,labels,spin/exchange,count,support,finiteM",
    "claim_gate": "Source-consistent law+uncertainty; marginal DDCS cannot fill missing joint support",
    "pass_next": "One source admittedHE-ANG event to transport/closure",
    "budget": "NoPR101replay;new source numerical budget pending",
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
    },
    {
      "type": "internal",
      "id": "HE-X1",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Differential measure,labels,spin/exchange,count,support,finiteM",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "SOURCE_INPUT_PENDING",
  "claim_gate": "Source-consistent law+uncertainty; marginal DDCS cannot fill missing joint support",
  "pass_next_action": "One source admittedHE-ANG event to transport/closure",
  "budget_status": "NoPR101replay;new source numerical budget pending",
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
      "value": "Differential measure,labels,spin/exchange,count,support,finiteM",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/1/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "pion=pin-p1-p2; ionSTF requires C12 same-law cross moment",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/1/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/1/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Alltarget impact/photoelectron daughter events and correlated recoil",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/1/provider_domain",
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
      "json_pointer": "/tasks/1/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "Source-consistent law+uncertainty; marginal DDCS cannot fill missing joint support",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/1/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/1/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/1/independent_review",
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
  }
}
```
