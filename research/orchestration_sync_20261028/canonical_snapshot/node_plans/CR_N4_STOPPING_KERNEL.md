# CR_N4_STOPPING_KERNEL

Lead: cosmosapjw-quantum/bass_cr

Current status: `PARTIAL_OPEN`

Source: `authority/atomic/EXPANDED_NODE_CONTRACTS.json#/nodes/7`

```json
{
  "id": "CR_N4_STOPPING_KERNEL",
  "lead_repo": "cosmosapjw-quantum/bass_cr",
  "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
  "json_pointer": "/nodes/7",
  "contract": {
    "id": "CR_N4_STOPPING_KERNEL",
    "legacy_repository": "bass_cr",
    "owner_repository": "bass_cr",
    "status": "PARTIAL_OPEN",
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
      "id": "CR_N4_STOPPING_KERNEL",
      "depends_on": [
        "CR_N4_C23B_CUTOFF_BINDING"
      ],
      "equations": [
        "partial_t F+partial_K(dotK*F)=S+gain-loss",
        "Jcut=(dKc/dt-dotK(Kc))*F(Kc)",
        "Qbath=int b_coll(K)*F(K)dK + cutoff_energy_transfer"
      ],
      "domain": "K<10eV plus above-cutoff source; finite-T Coulomb/elastic/inelastic channels, density and ionization explicit",
      "input": [
        "primary low-energy stopping rates with validity",
        "bath composition and thermal distribution",
        "C23B low-energy source atoms"
      ],
      "output": [
        "positive conservative stopping/exchange operator and timescale ratios"
      ],
      "admission_gate": "finite-time t_stop/t_evolution and escape assumptions established; no cold drag extrapolation through thermal bath; count/energy same boundary flux",
      "pr_boundary": "Physical kernel PR separate from algebraic cutoff connector and integrated ODE"
    },
    "equations": [
      "partial_t F+partial_K(dotK*F)=S+gain-loss",
      "Jcut=(dKc/dt-dotK(Kc))*F(Kc)",
      "Qbath=int b_coll(K)*F(K)dK + cutoff_energy_transfer"
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
      "primary low-energy stopping rates with validity",
      "bath composition and thermal distribution",
      "C23B low-energy source atoms"
    ],
    "outputs": [
      "positive conservative stopping/exchange operator and timescale ratios"
    ],
    "domain": "K<10eV plus above-cutoff source; finite-T Coulomb/elastic/inelastic channels, density and ionization explicit",
    "evidence": "C23D EE; PR102 CE; PR103 EI; PR104 neutral; PR105 ground RR finite-chain children admitted scoped",
    "admission_gate": [
      "first entry versus irreversible assimilation distinguished",
      "finite-T diffusion/current and moving cutoff share number/energy flux",
      "source initialW<10eV does not bound pathenergy",
      "saved chains reused, no cold drag extension through thermal bath"
    ],
    "pass_next": "Pass actual complete source-domain+time/boundary gate => conservative component; otherwise isolate missing process/physical error.",
    "fail_next": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
    "pr_boundary": "Physical kernel PR separate from algebraic cutoff connector and integrated ODE",
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
      "id": "CR_N4_C23B_CUTOFF_BINDING",
      "source_file": "historical/baseline/assembly/DAG.json",
      "source_field": "preserved_baseline_dependencies"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PARTIAL_OPEN",
  "claim_gate": [
    "first entry versus irreversible assimilation distinguished",
    "finite-T diffusion/current and moving cutoff share number/energy flux",
    "source initialW<10eV does not bound pathenergy",
    "saved chains reused, no cold drag extension through thermal bath"
  ],
  "pass_next_action": "Pass actual complete source-domain+time/boundary gate => conservative component; otherwise isolate missing process/physical error.",
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
  "historical_contract_id": "CR_N4_STOPPING_KERNEL",
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
        "primary low-energy stopping rates with validity",
        "bath composition and thermal distribution",
        "C23B low-energy source atoms"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/7/inputs",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": [
        "partial_t F+partial_K(dotK*F)=S+gain-loss",
        "Jcut=(dKc/dt-dotK(Kc))*F(Kc)",
        "Qbath=int b_coll(K)*F(K)dK + cutoff_energy_transfer"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/7/equations",
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
      "json_pointer": "/nodes/7/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "K<10eV plus above-cutoff source; finite-T Coulomb/elastic/inelastic channels, density and ionization explicit",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/7/domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "positive conservative stopping/exchange operator and timescale ratios"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/7/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "first entry versus irreversible assimilation distinguished",
        "finite-T diffusion/current and moving cutoff share number/energy flux",
        "source initialW<10eV does not bound pathenergy",
        "saved chains reused, no cold drag extension through thermal bath"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/7/admission_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve raw failure/unknown; classify source,physics,numerics,implementation or environment; repair only changed dependency.",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/7/fail_next",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/7/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": "Physical kernel PR separate from algebraic cutoff connector and integrated ODE",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/7/pr_boundary",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
