# HE-RESERVOIR

Lead: cosmosapjw-quantum/BASS_HE

Current status: `PROPOSED_SOURCE_INPUT_PENDING`

Source: `authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json#/nodes/3`

```json
{
  "id": "HE-RESERVOIR",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
  "json_pointer": "/nodes/3",
  "contract": {
    "id": "HE-RESERVOIR",
    "status": "PROPOSED_SOURCE_INPUT_PENDING",
    "depends_on": [],
    "equations_scope": "Separate photon/electron/ion birth rates and energy; nuclearQ/neutrino/recoil/stopping explicit",
    "inputs_domain": "UV/CMB/Xray/external baryon beams/cosmic rays/nuclear daughters only source-qualified",
    "claim_gates": [
      "C23AUVB z<=15.1 cannot supply z20; spectrum not inferred from total heating"
    ],
    "pass_action": "One admitted source to closure; nuclear daughter only after input gates",
    "budget": "NoHE32replay;new evolution gated",
    "fail_action": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
    "review": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
    "tests": "Same-source contract controls and affected derivative/conservation tests only; original tolerance preserved",
    "conditional_dependencies": []
  },
  "dependencies": [],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PROPOSED_SOURCE_INPUT_PENDING",
  "claim_gate": [
    "C23AUVB z<=15.1 cannot supply z20; spectrum not inferred from total heating"
  ],
  "pass_next_action": "One admitted source to closure; nuclear daughter only after input gates",
  "budget_status": "NoHE32replay;new evolution gated",
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "HE-RESERVOIR",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "claim_gates",
    "pass_next_action": "pass_action",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "UV/CMB/Xray/external baryon beams/cosmic rays/nuclear daughters only source-qualified",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/3/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "Separate photon/electron/ion birth rates and energy; nuclearQ/neutrino/recoil/stopping explicit",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/3/equations_scope",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "UV/CMB/Xray/external baryon beams/cosmic rays/nuclear daughters only source-qualified",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/3/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "positive_acceptance": {
      "value": [
        "C23AUVB z<=15.1 cannot supply z20; spectrum not inferred from total heating"
      ],
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/3/claim_gates",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/3/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/3/review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    }
  },
  "runnable": false,
  "missing_contract_fields": [
    "units",
    "outputs",
    "PR_boundary"
  ],
  "execution_readiness_guard": {
    "source_file": "authority/FINAL_ASSEMBLY_MISSING_FIELDS.json",
    "scope": "Execution-readiness guard only; retain finite past admissions and source object unchanged",
    "other_nodes_runnable_not_inferred": true
  }
}
```
