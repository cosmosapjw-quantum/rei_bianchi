# WU_LI_SOURCE_UNCERTAINTY

Lead: cosmosapjw-quantum/WU088_HH

Current status: `PARTIAL_CONDITIONAL_MODELS`

Source: `authority/atomic/EXPANDED_NODE_CONTRACTS.json#/nodes/1`

```json
{
  "id": "WU_LI_SOURCE_UNCERTAINTY",
  "lead_repo": "cosmosapjw-quantum/WU088_HH",
  "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
  "json_pointer": "/nodes/1",
  "contract": {
    "id": "WU_LI_SOURCE_UNCERTAINTY",
    "legacy_repository": "WU088_HH",
    "owner_repository": "WU088_HH",
    "status": "PARTIAL_CONDITIONAL_MODELS",
    "legacy_contract_preserved": {
      "status": "OPEN",
      "execution": "NOT_RUN",
      "budget": {
        "inherited_spend": null,
        "remaining": null,
        "currency": null,
        "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
      },
      "publication": {
        "kind": "separate additive draft",
        "merge": false
      },
      "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
      "no_replay": "completed identities reused, changes verify only affected obligations",
      "id": "WU_LI_SOURCE_UNCERTAINTY",
      "depends_on": [],
      "equations": [
        "K(T)=sqrt(8/(pi*me))*(kBT)^(-3/2)*integral(E*sigma(E)*exp(-E/kBT)dE)",
        "sigma_model=sigma6*((E-I)/(6-I))^p*(6/E)^q"
      ],
      "domain": "Li7 I=5.39172060034581eV to6eV; measurement response and source tail separated",
      "input": [
        "PHYS82 ca9d53983459ea08f9992a8a24663e46b7180344 conditional families",
        "original experimental instrument response, isotope composition"
      ],
      "output": [
        "admissible source envelope or explicit source-limited conditional rates"
      ],
      "admission_gate": "unconvolved source uncertainty justified from data; family spread alone does not satisfy confidence gate",
      "pr_boundary": "Source analysis PR distinct from coupled trajectory PR"
    },
    "equations": [
      "K(T)=sqrt(8/(pi*me))*(kBT)^(-3/2)*integral(E*sigma(E)*exp(-E/kBT)dE)",
      "sigma_model=sigma6*((E-I)/(6-I))^p*(6/E)^q"
    ],
    "units": {
      "number_density": "m^-3 internal; cm^-3 accepted only with declared conversion1cm^-3=1e6m^-3",
      "energy": "J internal; source-native eV kept,1eV=1.602176634e-19J",
      "cross_section": "m^2;1cm^2=1e-4m^2;1barn=1e-28m^2",
      "two_body_rate": "m^3 s^-1",
      "one_body_rate": "s^-1",
      "volumetric_event_rate": "m^-3 s^-1",
      "energy_source": "J m^-3 s^-1",
      "clock": "declared proper seconds, coordinate conversion explicit",
      "temperature": "K"
    },
    "inputs": [
      "PHYS82 ca9d53983459ea08f9992a8a24663e46b7180344 conditional families",
      "original experimental instrument response, isotope composition"
    ],
    "outputs": [
      "admissible source envelope or explicit source-limited conditional rates"
    ],
    "domain": "Li7 I=5.39172060034581eV to6eV; measurement response and source tail separated",
    "evidence": "PHYS82 conditional endpoint-matched families complete; physical unsmeared Li6/Li7 uncertainty open",
    "admission_gate": [
      "primary data instrument response and isotope composition",
      "fit spread does not equal confidence interval",
      "Li7 native I5.39172060034581eV and source floor6eV separate"
    ],
    "pass_next": "Pass source envelope => finite rate/tail bounds; otherwise preserve conditional families and seek instrument/isotope source.",
    "fail_next": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
    "pr_boundary": "Source analysis PR distinct from coupled trajectory PR",
    "budget": {
      "new_scientific_run_authorized_by_this_audit": false,
      "heavy_launch": false,
      "global_remaining": null,
      "currency": null,
      "unknown_is_zero": false,
      "PHYS91_remaining": 0,
      "CR105_known_lineage_CPU_s": "39.097868524",
      "CR105_new_CPU_s": "4.86342341",
      "C23E_separate_lineage_CPU_s": "15.493261114",
      "sum_lineages_without_overlap_proof": false,
      "new_unit_limit": "UNBOUND until existing authority budget and actual resource lease are pinned",
      "completed_identity_replay": false
    },
    "claim_ceiling": "Current evidence only; no global physical completion or blanket production admission",
    "execution_this_audit": "NOT_RUN",
    "readiness_policy": "conditional on selected model, source domain and actual consumer; do not AND every future catalog channel",
    "independent_review": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review"
  },
  "dependencies": [],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PARTIAL_CONDITIONAL_MODELS",
  "claim_gate": [
    "primary data instrument response and isotope composition",
    "fit spread does not equal confidence interval",
    "Li7 native I5.39172060034581eV and source floor6eV separate"
  ],
  "pass_next_action": "Pass source envelope => finite rate/tail bounds; otherwise preserve conditional families and seek instrument/isotope source.",
  "budget_status": {
    "new_scientific_run_authorized_by_this_audit": false,
    "heavy_launch": false,
    "global_remaining": null,
    "currency": null,
    "unknown_is_zero": false,
    "PHYS91_remaining": 0,
    "CR105_known_lineage_CPU_s": "39.097868524",
    "CR105_new_CPU_s": "4.86342341",
    "C23E_separate_lineage_CPU_s": "15.493261114",
    "sum_lineages_without_overlap_proof": false,
    "new_unit_limit": "UNBOUND until existing authority budget and actual resource lease are pinned",
    "completed_identity_replay": false
  },
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "WU_LI_SOURCE_UNCERTAINTY",
  "source_fields": {
    "lead_repo": "owner_repository",
    "current_status": "status",
    "claim_gate": "admission_gate",
    "pass_next_action": "pass_next",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": [
        "PHYS82 ca9d53983459ea08f9992a8a24663e46b7180344 conditional families",
        "original experimental instrument response, isotope composition"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/inputs",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": [
        "K(T)=sqrt(8/(pi*me))*(kBT)^(-3/2)*integral(E*sigma(E)*exp(-E/kBT)dE)",
        "sigma_model=sigma6*((E-I)/(6-I))^p*(6/E)^q"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": {
        "number_density": "m^-3 internal; cm^-3 accepted only with declared conversion1cm^-3=1e6m^-3",
        "energy": "J internal; source-native eV kept,1eV=1.602176634e-19J",
        "cross_section": "m^2;1cm^2=1e-4m^2;1barn=1e-28m^2",
        "two_body_rate": "m^3 s^-1",
        "one_body_rate": "s^-1",
        "volumetric_event_rate": "m^-3 s^-1",
        "energy_source": "J m^-3 s^-1",
        "clock": "declared proper seconds, coordinate conversion explicit",
        "temperature": "K"
      },
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Li7 I=5.39172060034581eV to6eV; measurement response and source tail separated",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "admissible source envelope or explicit source-limited conditional rates"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "primary data instrument response and isotope composition",
        "fit spread does not equal confidence interval",
        "Li7 native I5.39172060034581eV and source floor6eV separate"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/admission_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/fail_next",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": "Source analysis PR distinct from coupled trajectory PR",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/1/pr_boundary",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
