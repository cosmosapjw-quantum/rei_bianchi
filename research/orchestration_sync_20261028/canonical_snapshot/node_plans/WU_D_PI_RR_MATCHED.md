# WU_D_PI_RR_MATCHED

Lead: cosmosapjw-quantum/WU088_HH

Current status: `PARTIAL_CONDITIONAL_C23E_REUSED`

Source: `authority/atomic/EXPANDED_NODE_CONTRACTS.json#/nodes/3`

```json
{
  "id": "WU_D_PI_RR_MATCHED",
  "lead_repo": "cosmosapjw-quantum/WU088_HH",
  "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
  "json_pointer": "/nodes/3",
  "contract": {
    "id": "WU_D_PI_RR_MATCHED",
    "legacy_repository": "WU088_HH",
    "owner_repository": "WU088_HH",
    "status": "PARTIAL_CONDITIONAL_C23E_REUSED",
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
      "id": "WU_D_PI_RR_MATCHED",
      "depends_on": [],
      "equations": [
        "R_PI=int(4*pi*Jnu*sigma_nu/(h*nu)dnu)",
        "H_PI=int(4*pi*Jnu*sigma_nu*(h*nu-I)/(h*nu)dnu)",
        "dT/dt=2*Q/(3*kB*Nthermal)-T*dNthermal/dt/Nthermal"
      ],
      "domain": "D source-qualified PI and Case-A RR using same isotope gap and radiation history",
      "input": [
        "PR135 existing event-energy adapter",
        "D threshold/cross section/RR capture moments"
      ],
      "output": [
        "source-matched event rates and kinetic/binding/photon moments"
      ],
      "admission_gate": "same event count in electron source and binding ledger; Milne relation under stated degeneracies/frame; dimensional guard",
      "pr_boundary": "Preserve event adapter; add source-moment supplier PR then consumer PR"
    },
    "equations": [
      "R_PI=int(4*pi*Jnu*sigma_nu/(h*nu)dnu)",
      "H_PI=int(4*pi*Jnu*sigma_nu*(h*nu-I)/(h*nu)dnu)",
      "dT/dt=2*Q/(3*kB*Nthermal)-T*dNthermal/dt/Nthermal"
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
      "PR135 existing event-energy adapter",
      "D threshold/cross section/RR capture moments"
    ],
    "outputs": [
      "source-matched event rates and kinetic/binding/photon moments"
    ],
    "domain": "D source-qualified PI and Case-A RR using same isotope gap and radiation history",
    "evidence": "C23E D43 source completed; empirical finite-mass microscopic D PI/RR pair open",
    "admission_gate": [
      "same source-native binding and statistical weights",
      "same event count in PI/RR and e/binding/photon rows",
      "finite-mass/recoil mapping must be complete"
    ],
    "pass_next": "Pass isotope qualified matched source => source moments; otherwise retain threshold-gated H equality only.",
    "fail_next": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
    "pr_boundary": "Preserve event adapter; add source-moment supplier PR then consumer PR",
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
  "current_status": "PARTIAL_CONDITIONAL_C23E_REUSED",
  "claim_gate": [
    "same source-native binding and statistical weights",
    "same event count in PI/RR and e/binding/photon rows",
    "finite-mass/recoil mapping must be complete"
  ],
  "pass_next_action": "Pass isotope qualified matched source => source moments; otherwise retain threshold-gated H equality only.",
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
  "historical_contract_id": "WU_D_PI_RR_MATCHED",
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
        "PR135 existing event-energy adapter",
        "D threshold/cross section/RR capture moments"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/inputs",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": [
        "R_PI=int(4*pi*Jnu*sigma_nu/(h*nu)dnu)",
        "H_PI=int(4*pi*Jnu*sigma_nu*(h*nu-I)/(h*nu)dnu)",
        "dT/dt=2*Q/(3*kB*Nthermal)-T*dNthermal/dt/Nthermal"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/equations",
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
      "json_pointer": "/nodes/3/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "D source-qualified PI and Case-A RR using same isotope gap and radiation history",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "source-matched event rates and kinetic/binding/photon moments"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "same source-native binding and statistical weights",
        "same event count in PI/RR and e/binding/photon rows",
        "finite-mass/recoil mapping must be complete"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/admission_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/fail_next",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": "Preserve event adapter; add source-moment supplier PR then consumer PR",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/3/pr_boundary",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
