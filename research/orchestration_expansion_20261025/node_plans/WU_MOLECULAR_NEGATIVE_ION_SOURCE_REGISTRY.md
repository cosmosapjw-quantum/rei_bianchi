# WU_MOLECULAR_NEGATIVE_ION_SOURCE_REGISTRY

Lead: cosmosapjw-quantum/WU088_HH

Current status: `PROPOSED_EXPANDED_SCOPE`

Source: `authority/atomic/EXPANDED_NODE_CONTRACTS.json#/nodes/14`

```json
{
  "id": "WU_MOLECULAR_NEGATIVE_ION_SOURCE_REGISTRY",
  "lead_repo": "cosmosapjw-quantum/WU088_HH",
  "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
  "json_pointer": "/nodes/14",
  "contract": {
    "id": "WU_MOLECULAR_NEGATIVE_ION_SOURCE_REGISTRY",
    "owner_repository": "WU088_HH",
    "status": "PROPOSED_EXPANDED_SCOPE",
    "depends_on": [
      "WU_ALL_TARGET_SPECIES_REACTION_REGISTRY",
      "REI-CHEM-LEDGER-01"
    ],
    "equations": [
      "dn_s/dtau=sum_a S_sa*r_a",
      "A_nuclide*S=0; q*S=0",
      "DeltaUchem=sum_s epsilon_s*S_sa; DeltaK+DeltaUchem+DeltaUgamma=0"
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
      "configured isotopologues and rovibronic states",
      "candidate Hminus,H2,HD,LiH,HeHplus constituents",
      "primary formation/destruction,photodetachment/dissociation and collisional state sources"
    ],
    "outputs": [
      "separate molecular/negativeion network manifest",
      "state-resolved opacity/emissivity interface toREC",
      "thermal/fast reaction moments toCR"
    ],
    "domain": "All configured target species with per-source admitted energy,temperature,density,frame and state domain; no extrapolation",
    "admission_gate": [
      "No molecules disguised as atoms or electronic charge ladders",
      "H2/HD/LiH labels carry full isotope constituents",
      "Rovibrational/internal degrees affect EOS separately from monatomic3kBT/2",
      "Manufactured compiler fixtures supply no empirical physicalrate"
    ],
    "pass_next": "Research source coverage first; assign REC emission/absorption and CR nonthermal impact ownership before implementation.",
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
    },
    {
      "type": "internal",
      "id": "REI-CHEM-LEDGER-01",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PROPOSED_EXPANDED_SCOPE",
  "claim_gate": [
    "No molecules disguised as atoms or electronic charge ladders",
    "H2/HD/LiH labels carry full isotope constituents",
    "Rovibrational/internal degrees affect EOS separately from monatomic3kBT/2",
    "Manufactured compiler fixtures supply no empirical physicalrate"
  ],
  "pass_next_action": "Research source coverage first; assign REC emission/absorption and CR nonthermal impact ownership before implementation.",
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
        "configured isotopologues and rovibronic states",
        "candidate Hminus,H2,HD,LiH,HeHplus constituents",
        "primary formation/destruction,photodetachment/dissociation and collisional state sources"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/14/inputs",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": [
        "dn_s/dtau=sum_a S_sa*r_a",
        "A_nuclide*S=0; q*S=0",
        "DeltaUchem=sum_s epsilon_s*S_sa; DeltaK+DeltaUchem+DeltaUgamma=0"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/14/equations",
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
      "json_pointer": "/nodes/14/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "All configured target species with per-source admitted energy,temperature,density,frame and state domain; no extrapolation",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/14/domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "separate molecular/negativeion network manifest",
        "state-resolved opacity/emissivity interface toREC",
        "thermal/fast reaction moments toCR"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/14/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "No molecules disguised as atoms or electronic charge ladders",
        "H2/HD/LiH labels carry full isotope constituents",
        "Rovibrational/internal degrees affect EOS separately from monatomic3kBT/2",
        "Manufactured compiler fixtures supply no empirical physicalrate"
      ],
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/14/admission_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Record exact missing source/identity and continue independent registry/theory obligations.",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/14/fail_next",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "fresh scientific reviewer checks exact changed contracts/source/raw results at proposed claim scope; reuse unchanged prior independent review",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/14/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": "Additive scoped source/contract child; preserve active owner branches and no main merge",
      "source_file": "authority/atomic/EXPANDED_NODE_CONTRACTS.json",
      "json_pointer": "/nodes/14/pr_boundary",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
