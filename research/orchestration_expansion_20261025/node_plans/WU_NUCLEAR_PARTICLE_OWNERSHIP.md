# WU_NUCLEAR_PARTICLE_OWNERSHIP

Lead: cosmosapjw-quantum/WU088_HH

Current status: `PARTIAL_INPUT_DEPENDENCIES`

Source: `authority/atomic/EXPANDED_NODE_CONTRACTS.json#/nodes/4`

```json
{
  "id": "WU_NUCLEAR_PARTICLE_OWNERSHIP",
  "lead_repo": "cosmosapjw-quantum/WU088_HH",
  "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
  "json_pointer": "/nodes/4",
  "contract": {
    "id": "WU_NUCLEAR_PARTICLE_OWNERSHIP",
    "legacy_repository": "WU088_HH",
    "owner_repository": "WU088_HH",
    "status": "PARTIAL_INPUT_DEPENDENCIES",
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
      "id": "WU_NUCLEAR_PARTICLE_OWNERSHIP",
      "depends_on": [],
      "equations": [
        "Nth=Nnuc,thermal+Ne,thermal",
        "dUtotal=dUth+dUnt+dUbind+dUrad+dUescape+work=0",
        "<rate*Eproduct> differs from <rate>*<Eproduct> unless justified"
      ],
      "domain": "thermal finite-T reactants, explicitly tracked fast products and normal-frame photons",
      "input": [
        "PHYS81 b3ec271a96cb67e583bffa9b61533802838236f9 photon/recoil kinematics",
        "C23B boost and clock pins",
        "HE source moment contracts"
      ],
      "output": [
        "particle transfer incidence and event-weighted thermal/photon/recoil moments"
      ],
      "admission_gate": "every product has unique thermal/fast owner; thresholds and recoil kinematics consistent; no rate activation without source",
      "pr_boundary": "Theory and source-ownership PR before stopping/rate implementation"
    },
    "equations": [
      "Nth=Nnuc,thermal+Ne,thermal",
      "dUtotal=dUth+dUnt+dUbind+dUrad+dUescape+work=0",
      "<rate*Eproduct> differs from <rate>*<Eproduct> unless justified"
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
      "PHYS81 b3ec271a96cb67e583bffa9b61533802838236f9 photon/recoil kinematics",
      "C23B boost and clock pins",
      "HE source moment contracts"
    ],
    "outputs": [
      "particle transfer incidence and event-weighted thermal/photon/recoil moments"
    ],
    "domain": "thermal finite-T reactants, explicitly tracked fast products and normal-frame photons",
    "evidence": "PHYS85 theory; PHYS86–88 conditional moments/remap; PHYS89–91 covariance source diagnostic/conditional distance. PHYS91 source consumer still null",
    "admission_gate": [
      "current MT102 nominal-covariance authority and approved formatter/correction",
      "actual atomic-to-bare kernel, electron+target+mass deck",
      "B0/BA full-support bounds and each named consumer measure/clock/density/owner",
      "PHYS91 B1 unresolved does not imply source repair"
    ],
    "pass_next": "Pass full source/mass/support/consumer binding => affected finite-T nuclear supplier; missing object => input-dependency status.",
    "fail_next": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
    "pr_boundary": "Theory and source-ownership PR before stopping/rate implementation",
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
  "current_status": "PARTIAL_INPUT_DEPENDENCIES",
  "claim_gate": [
    "current MT102 nominal-covariance authority and approved formatter/correction",
    "actual atomic-to-bare kernel, electron+target+mass deck",
    "B0/BA full-support bounds and each named consumer measure/clock/density/owner",
    "PHYS91 B1 unresolved does not imply source repair"
  ],
  "pass_next_action": "Pass full source/mass/support/consumer binding => affected finite-T nuclear supplier; missing object => input-dependency status.",
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
  "historical_contract_id": "WU_NUCLEAR_PARTICLE_OWNERSHIP",
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
        "PHYS81 b3ec271a96cb67e583bffa9b61533802838236f9 photon/recoil kinematics",
        "C23B boost and clock pins",
        "HE source moment contracts"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/4/inputs",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": [
        "Nth=Nnuc,thermal+Ne,thermal",
        "dUtotal=dUth+dUnt+dUbind+dUrad+dUescape+work=0",
        "<rate*Eproduct> differs from <rate>*<Eproduct> unless justified"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/4/equations",
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
      "json_pointer": "/nodes/4/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "thermal finite-T reactants, explicitly tracked fast products and normal-frame photons",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/4/domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "particle transfer incidence and event-weighted thermal/photon/recoil moments"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/4/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "current MT102 nominal-covariance authority and approved formatter/correction",
        "actual atomic-to-bare kernel, electron+target+mass deck",
        "B0/BA full-support bounds and each named consumer measure/clock/density/owner",
        "PHYS91 B1 unresolved does not imply source repair"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/4/admission_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/4/fail_next",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/4/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": "Theory and source-ownership PR before stopping/rate implementation",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/4/pr_boundary",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
