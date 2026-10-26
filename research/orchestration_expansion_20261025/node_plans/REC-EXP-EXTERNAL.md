# REC-EXP-EXTERNAL

Lead: cosmosapjw-quantum/bass_cr

Current status: `ADMITTED_SCOPED_SELECTED_INSTANTANEOUS_SOURCE`

Source: `authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/3`

```json
{
  "id": "REC-EXP-EXTERNAL",
  "lead_repo": "cosmosapjw-quantum/bass_cr",
  "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/3",
  "contract": {
    "id": "REC-EXP-EXTERNAL",
    "status": "SOURCE_INTAKE_PROPOSED",
    "depends_on": [],
    "provider_domain": "CMB/UVB/stellar/AGN/Xray and external baryonic-source-fed secondaries",
    "equations": "Gamma=integral Phi_E sigma_E dE; Q from exclusive final yields",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/bass_cr",
    "prerequisites": "Actual source E,z,angle,time support and uncertainty",
    "claim_gate": "No UVB extrapolation fromz<=15.1 to20; integrated heating not spectrum; source branch explicit",
    "pass_next": "Couple selected incident trace to H6/REC-FIELD",
    "budget": "Read-only source acquisition; no evolution",
    "tests": "Only affected source/state/measure/units/conservation/tangent checks; original numerical tolerance retained; no unchangedsuite replay",
    "fail_action": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
    "uncertainty": "Provider/model/interpolation/quadrature/floating error separate; null until actual evidence",
    "units": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
    "lead_repo": "cosmosapjw-quantum/bass_cr",
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
        "predicate": "downstream_REC_consumer_qualification_only_not_source_distribution_construction"
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
      "id": "REC-EXP-SPECTRAL",
      "predicate": "downstream_REC_consumer_qualification_only_not_source_distribution_construction",
      "type": "internal",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    }
  ],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Actual source E,z,angle,time support and uncertainty",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "SOURCE_INTAKE_PROPOSED",
  "claim_gate": "No UVB extrapolation fromz<=15.1 to20; integrated heating not spectrum; source branch explicit",
  "pass_next_action": "Couple selected incident trace to H6/REC-FIELD",
  "budget_status": "Read-only source acquisition; no evolution",
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
      "value": "Actual source E,z,angle,time support and uncertainty",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/3/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "Gamma=integral Phi_E sigma_E dE; Q from exclusive final yields",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/3/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/3/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "CMB/UVB/stellar/AGN/Xray and external baryonic-source-fed secondaries",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/3/provider_domain",
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
      "json_pointer": "/tasks/3/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "No UVB extrapolation fromz<=15.1 to20; integrated heating not spectrum; source branch explicit",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/3/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/3/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/rec_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/3/independent_review",
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

## Scoped status observation (2026-10-26)

The selected exact PW19 z=2.479 instantaneous He II external source passes the original source gate in this scope. Native finite-support moments, a conservative local residual/JVP, and the SI consumer-facing event/state handoff were independently reviewed. See `research/rei_expanded_event_consumer/lumina_resume_20261026/ADMISSION.json`, `review/VALIDATION.json`, and raw `implementation/run01/MOMENTS.json` (SHA-256 `4856cabb34ee24d3c626b795cb1098b228e752c857dda1dc874fe4583deb936e`). The historical source contract in the JSON block above is unchanged. REC-EXP-SPECTRAL live consumption, L4, thermal heat, and the selected full physical pilot remain open. Next action: couple this selected trace to H6/REC-FIELD under its original interfaces.
