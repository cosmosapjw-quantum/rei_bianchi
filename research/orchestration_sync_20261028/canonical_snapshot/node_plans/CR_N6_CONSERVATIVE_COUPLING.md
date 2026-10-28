# CR_N6_CONSERVATIVE_COUPLING

Lead: cosmosapjw-quantum/bass_cr

Current status: `PREDECESSOR_GATED`

Source: `authority/atomic/EXPANDED_NODE_CONTRACTS.json#/nodes/9`

```json
{
  "id": "CR_N6_CONSERVATIVE_COUPLING",
  "lead_repo": "cosmosapjw-quantum/bass_cr",
  "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
  "json_pointer": "/nodes/9",
  "contract": {
    "id": "CR_N6_CONSERVATIVE_COUPLING",
    "legacy_repository": "bass_cr",
    "owner_repository": "bass_cr",
    "status": "PREDECESSOR_GATED",
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
      "id": "CR_N6_CONSERVATIVE_COUPLING",
      "depends_on": [
        "CR_N4_STOPPING_KERNEL",
        "CR_N5_ATOMIC_ISOTOPE_COVERAGE"
      ],
      "equations": [
        "d(Uth+Unt+Ubind+Urad+Uescape)/dt=external_supply-expansion_work-shear_work",
        "dNe,all/dt=charge_incidence",
        "pi_total=sum signed frame-aligned pi"
      ],
      "domain": "non-tilted LRS; original isotropic gas; source3z no unqualified z interpolation",
      "input": [
        "admitted source kernels and bath",
        "radiative escape/reabsorption and normal-frame mappings"
      ],
      "output": [
        "closed conservative thermochemical RHS, block Jacobian and audit"
      ],
      "admission_gate": "single owner for photoheat/fast kinetic/binding; no simultaneous direct heat and full nonthermal source; FS physical composition gate independently closed",
      "pr_boundary": "Conservative component PR followed by consumer integration PR"
    },
    "equations": [
      "d(Uth+Unt+Ubind+Urad+Uescape)/dt=external_supply-expansion_work-shear_work",
      "dNe,all/dt=charge_incidence",
      "pi_total=sum signed frame-aligned pi"
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
      "admitted source kernels and bath",
      "radiative escape/reabsorption and normal-frame mappings"
    ],
    "outputs": [
      "closed conservative thermochemical RHS, block Jacobian and audit"
    ],
    "domain": "non-tilted LRS; original isotropic gas; source3z no unqualified z interpolation",
    "evidence": "No global N6 admission from frozen-bath finite-chain children",
    "admission_gate": [
      "exclusive event owner for all reservoirs",
      "same incident photon cannot produce full fast source and direct full photoheat",
      "thermal particle number includes actual thermal membership",
      "coupled bath/composition/radiation feedback distinct from fixed-reservoir diagnostics"
    ],
    "pass_next": "Pass all named component closure => frozen new parcel request; otherwise supply dependency not new trajectory.",
    "fail_next": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
    "pr_boundary": "Conservative component PR followed by consumer integration PR",
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
  "dependencies": [
    {
      "type": "internal",
      "id": "CR_N4_STOPPING_KERNEL",
      "source_file": "historical/baseline/assembly/DAG.json",
      "source_field": "preserved_baseline_dependencies"
    },
    {
      "type": "internal",
      "id": "CR_N5_ATOMIC_ISOTOPE_COVERAGE",
      "source_file": "historical/baseline/assembly/DAG.json",
      "source_field": "preserved_baseline_dependencies"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PREDECESSOR_GATED",
  "claim_gate": [
    "exclusive event owner for all reservoirs",
    "same incident photon cannot produce full fast source and direct full photoheat",
    "thermal particle number includes actual thermal membership",
    "coupled bath/composition/radiation feedback distinct from fixed-reservoir diagnostics"
  ],
  "pass_next_action": "Pass all named component closure => frozen new parcel request; otherwise supply dependency not new trajectory.",
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
  "historical_contract_id": "CR_N6_CONSERVATIVE_COUPLING",
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
        "admitted source kernels and bath",
        "radiative escape/reabsorption and normal-frame mappings"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/9/inputs",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": [
        "d(Uth+Unt+Ubind+Urad+Uescape)/dt=external_supply-expansion_work-shear_work",
        "dNe,all/dt=charge_incidence",
        "pi_total=sum signed frame-aligned pi"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/9/equations",
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
      "json_pointer": "/nodes/9/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "non-tilted LRS; original isotropic gas; source3z no unqualified z interpolation",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/9/domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "closed conservative thermochemical RHS, block Jacobian and audit"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/9/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "exclusive event owner for all reservoirs",
        "same incident photon cannot produce full fast source and direct full photoheat",
        "thermal particle number includes actual thermal membership",
        "coupled bath/composition/radiation feedback distinct from fixed-reservoir diagnostics"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/9/admission_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/9/fail_next",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/9/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": "Conservative component PR followed by consumer integration PR",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/9/pr_boundary",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
