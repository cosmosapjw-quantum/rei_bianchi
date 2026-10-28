# WU_ALL_ISOTOPE_ATOMIC_SOURCE_COVERAGE

Lead: cosmosapjw-quantum/WU088_HH

Current status: `PROPOSED_EXPANDED_SCOPE`

Source: `authority/atomic/EXPANDED_NODE_CONTRACTS.json#/nodes/13`

```json
{
  "id": "WU_ALL_ISOTOPE_ATOMIC_SOURCE_COVERAGE",
  "lead_repo": "cosmosapjw-quantum/WU088_HH",
  "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
  "json_pointer": "/nodes/13",
  "contract": {
    "id": "WU_ALL_ISOTOPE_ATOMIC_SOURCE_COVERAGE",
    "owner_repository": "WU088_HH",
    "status": "PROPOSED_EXPANDED_SCOPE",
    "depends_on": [
      "WU_ALL_TARGET_SPECIES_REACTION_REGISTRY"
    ],
    "equations": [
      "k(T)=sqrt(8/(pi*mu))*(k_B*T)^(-3/2)*integral E*sigma(E)*exp(-E/(k_B*T))dE under admitted relative Maxwell convention",
      "Gamma_PI=integral 4pi*Jnu*sigma(nu)/(h*nu)dnu",
      "per_event: DeltaUinternal+DeltaKthermal+DeltaKfast+DeltaUgamma+DeltaUrecoil=0"
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
      "current finiteCI/PHYS83 source registries",
      "primary isotope/state-qualified CI/RR/DR/CX/CE/PI records",
      "REC branch/cascade and HE differential kernels"
    ],
    "outputs": [
      "all-configured-isotope source manifest",
      "number/energy/momentum source moments with support and uncertainty",
      "explicit admitted transfer mappings"
    ],
    "domain": "All configured target species with per-source admitted energy,temperature,density,frame and state domain; no extrapolation",
    "admission_gate": [
      "Native thresholds/source axis unchanged unless separately approved model identity",
      "Finite support integral not complete rate without tail/gap bounds",
      "Source reliability and numerical interpolation error separate",
      "Unique statistical weights, CaseA/B, recoil and photon owners"
    ],
    "pass_next": "Select one missing source-qualified channel with live owner; reuse existing H1/He4/Li7 finite evidence and CR105component.",
    "fail_next": "Record exact missing source/identity and continue independent registry/theory obligations.",
    "pr_boundary": "Additive scoped source/contract child; preserve active owner branches and no main merge",
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
    "claim_ceiling": "Expanded responsibility; physical coverage remains cell-specific",
    "execution_this_audit": "NOT_RUN",
    "readiness_policy": "conditional on selected model, source domain and actual consumer; do not AND every future catalog channel",
    "independent_review": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review"
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "WU_ALL_TARGET_SPECIES_REACTION_REGISTRY",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PROPOSED_EXPANDED_SCOPE",
  "claim_gate": [
    "Native thresholds/source axis unchanged unless separately approved model identity",
    "Finite support integral not complete rate without tail/gap bounds",
    "Source reliability and numerical interpolation error separate",
    "Unique statistical weights, CaseA/B, recoil and photon owners"
  ],
  "pass_next_action": "Select one missing source-qualified channel with live owner; reuse existing H1/He4/Li7 finite evidence and CR105component.",
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
    "scope_expansion"
  ],
  "historical_contract_id": null,
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
        "current finiteCI/PHYS83 source registries",
        "primary isotope/state-qualified CI/RR/DR/CX/CE/PI records",
        "REC branch/cascade and HE differential kernels"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/13/inputs",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": [
        "k(T)=sqrt(8/(pi*mu))*(k_B*T)^(-3/2)*integral E*sigma(E)*exp(-E/(k_B*T))dE under admitted relative Maxwell convention",
        "Gamma_PI=integral 4pi*Jnu*sigma(nu)/(h*nu)dnu",
        "per_event: DeltaUinternal+DeltaKthermal+DeltaKfast+DeltaUgamma+DeltaUrecoil=0"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/13/equations",
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
      "json_pointer": "/nodes/13/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "All configured target species with per-source admitted energy,temperature,density,frame and state domain; no extrapolation",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/13/domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "all-configured-isotope source manifest",
        "number/energy/momentum source moments with support and uncertainty",
        "explicit admitted transfer mappings"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/13/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "Native thresholds/source axis unchanged unless separately approved model identity",
        "Finite support integral not complete rate without tail/gap bounds",
        "Source reliability and numerical interpolation error separate",
        "Unique statistical weights, CaseA/B, recoil and photon owners"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/13/admission_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Record exact missing source/identity and continue independent registry/theory obligations.",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/13/fail_next",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/13/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": "Additive scoped source/contract child; preserve active owner branches and no main merge",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/13/pr_boundary",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
