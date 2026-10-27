# HE-EXP-NUCLEAR

Lead: cosmosapjw-quantum/WU088_HH

Current status: `SOURCE_INPUT_PENDING`

Source: `authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/5`

```json
{
  "id": "HE-EXP-NUCLEAR",
  "lead_repo": "cosmosapjw-quantum/WU088_HH",
  "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/5",
  "contract": {
    "id": "HE-EXP-NUCLEAR",
    "status": "SOURCE_INPUT_PENDING",
    "depends_on": [
      "HE-EXP-SPECIES"
    ],
    "provider_domain": "n/Tdecay,source-selected nuclearfragment/Be7 daughter channels",
    "equations": "Nuclear massQ partitions neutrino,photons,atomicbinding,chargedparticles",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/WU088_HH",
    "prerequisites": "Daughter distribution,charge/state,massQ/lepton and sourcevalidity",
    "claim_gate": "No nuclearQ reused as heat;neutrino escape tracked; beta branching sourced",
    "pass_next": "One daughter packet toHE-RESERVOIR",
    "budget": "No nuclear simulation budget assigned",
    "tests": "Only affected source/state/measure/units/conservation/tangent checks; original numerical tolerance retained; no unchangedsuite replay",
    "fail_action": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
    "uncertainty": "Provider/model/interpolation/quadrature/floating error separate; null until actual evidence",
    "units": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
    "lead_repo": "cosmosapjw-quantum/WU088_HH",
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
    },
    "input_dependencies": [
      {
        "kind": "source_input",
        "lead_repo": "cosmosapjw-quantum/WU088_HH",
        "required": "selected nuclear/weak channel, isotope/isomer and daughter identities, masses/Q, charge/level branching, lepton and recoil source payload",
        "status": "SOURCE_INPUT_PENDING"
      }
    ],
    "consumer_bindings": [
      {
        "consumer": "HE-EXP-STOPPING",
        "predicate": "selected_nonthermal_stopping_model_contains_this_nuclear_daughter_source",
        "direction": "source_payload_to_stopping_consumer",
        "blocks_source_production": false
      }
    ],
    "readiness_rule": "Produce the WU-led nuclear source from catalog/mass/branch/source evidence; downstream stopping completion is not a prerequisite."
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
      "source_reference": "Daughter distribution,charge/state,massQ/lepton and sourcevalidity",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "SOURCE_INPUT_PENDING",
  "claim_gate": "No nuclearQ reused as heat;neutrino escape tracked; beta branching sourced",
  "pass_next_action": "One daughter packet toHE-RESERVOIR",
  "budget_status": "No nuclear simulation budget assigned",
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
      "value": "Daughter distribution,charge/state,massQ/lepton and sourcevalidity",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "Nuclear massQ partitions neutrino,photons,atomicbinding,chargedparticles",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "n/Tdecay,source-selected nuclearfragment/Be7 daughter channels",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/provider_domain",
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
      "json_pointer": "/tasks/5/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "No nuclearQ reused as heat;neutrino escape tracked; beta branching sourced",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/independent_review",
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


## Preserved historical observation context

The following narrative is historical local/unpublished observation context, not a replacement for the latest base contract above. DRIFT02 historical file: `status/HE_EXP_FINITE_DRIFT_20261027.json` (no observation for this node).


## HE-EXP-PHOTON-05 observation

HE consumer-side conditional finite-recoil contribution for EXFOR M0475002 native12 coordinates with NIST2022 bare nuclear masses. This does not promote WU-led source/channel/branch/normalization admission: WU lead, SOURCE_INPUT_PENDING status, original budget and all contract gates remain unchanged. No nuclear Q is assigned to heat. Source remains local/unpublished; no physical promotion. See `status/HE_EXP_PHOTON05_20261027.json#/observations/HE-EXP-NUCLEAR`.


## Current local observation pointer

See `status/HE_EXP_ANGULAR06_20261027.json#/observations/HE-EXP-NUCLEAR`. Central publication has not occurred. Current scoped state, budget, lead and dependency gates remain unchanged.


## HE-EXP-APERTURE-07 prepared observation (C9 accepted; actual S09/P09 and S10/P10 identities)

Root accepted the HE consumer-side conditional aperture bounds and pair-coincidence reference under its explicit continuous-measure and fixed-parameter domain. The demonstrated native density is manufactured symmetric Bernstein data, not empirical DCS. WU source/channel/branch ownership and SOURCE_INPUT_PENDING, original experimental normalization, liquid-He projection, complete angular law with actual photon flux, and named deposition consumer remain open.

See `status/HE_EXP_APERTURE07_20261027.json#/observations/HE-EXP-NUCLEAR`. S09/P09 science identity is actual; S10/P10 delivery identity is actual in the status record. Current physical status, budget, lead, dependencies and claim gates remain unchanged.
