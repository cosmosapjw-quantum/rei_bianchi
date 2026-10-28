# HE-FEEDBACK

Lead: cosmosapjw-quantum/BASS_HE

Current status: `INPUT_DEPENDENT_NOT_SCHEDULED`

Source: `authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json#/nodes/5`

```json
{
  "id": "HE-FEEDBACK",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
  "json_pointer": "/nodes/5",
  "contract": {
    "id": "HE-FEEDBACK",
    "status": "INPUT_DEPENDENT_NOT_SCHEDULED",
    "depends_on": [
      "HE-CLOSURE"
    ],
    "equations_scope": "Ttotal=Tnonbaryonic+Tbaryon+Tradiation; internal four-source exchanges cancel",
    "inputs_domain": "Selected baryon kinetic stress vs storednonbaryonic/radiation stress",
    "claim_gates": [
      "Finitegas control then Einstein/source closure then separate convergence"
    ],
    "pass_action": "Metric feedback control only after upstream source admission",
    "budget": "HE32reused;newlongrun not scheduled",
    "fail_action": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
    "review": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
    "tests": "Same-source contract controls and affected derivative/conservation tests only; original tolerance preserved",
    "conditional_dependencies": []
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "HE-CLOSURE",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "INPUT_DEPENDENT_NOT_SCHEDULED",
  "claim_gate": [
    "Finitegas control then Einstein/source closure then separate convergence"
  ],
  "pass_next_action": "Metric feedback control only after upstream source admission",
  "budget_status": "HE32reused;newlongrun not scheduled",
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "HE-FEEDBACK",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "claim_gates",
    "pass_next_action": "pass_action",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "Selected baryon kinetic stress vs storednonbaryonic/radiation stress",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "Ttotal=Tnonbaryonic+Tbaryon+Tradiation; internal four-source exchanges cancel",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/equations_scope",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "Selected baryon kinetic stress vs storednonbaryonic/radiation stress",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/inputs_domain",
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
        "Finitegas control then Einstein/source closure then separate convergence"
      ],
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/claim_gates",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/review",
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
