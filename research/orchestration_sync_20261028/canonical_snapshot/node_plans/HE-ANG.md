# HE-ANG

Lead: cosmosapjw-quantum/BASS_HE

Current status: `SOURCE_INPUT_PENDING; PR10119/20 C8OPEN`

Source: `authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json#/nodes/1`

```json
{
  "id": "HE-ANG",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
  "json_pointer": "/nodes/1",
  "contract": {
    "id": "HE-ANG",
    "status": "SOURCE_INPUT_PENDING; PR10119/20 C8OPEN",
    "depends_on": [
      "HE-X1"
    ],
    "equations_scope": "Same joint event law electron2/ion1; recoilSTF requires cross moment; W=4|FM|²/(|P|Delta⁴)",
    "inputs_domain": "Current H1 measured DDCS20 marginal,sparseTDCS54,TDCS413 shape; finiteM labelled directCBA",
    "claim_gates": [
      "Fullsupport/exchange/count/spin/frame/recoil/calibrated validity;directCBA not physicalprovider"
    ],
    "pass_action": "Owner export only new explicit cap; independent source intake may proceed",
    "budget": "PR101reserve0; PASS/FAIL/FAIL and11.882829CPU retained",
    "fail_action": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
    "review": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
    "tests": "Same-source contract controls and affected derivative/conservation tests only; original tolerance preserved",
    "conditional_dependencies": []
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "HE-X1",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "SOURCE_INPUT_PENDING; PR10119/20 C8OPEN",
  "claim_gate": [
    "Fullsupport/exchange/count/spin/frame/recoil/calibrated validity;directCBA not physicalprovider"
  ],
  "pass_next_action": "Owner export only new explicit cap; independent source intake may proceed",
  "budget_status": "PR101reserve0; PASS/FAIL/FAIL and11.882829CPU retained",
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "HE-ANG",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "claim_gates",
    "pass_next_action": "pass_action",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "Current H1 measured DDCS20 marginal,sparseTDCS54,TDCS413 shape; finiteM labelled directCBA",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "Same joint event law electron2/ion1; recoilSTF requires cross moment; W=4|FM|²/(|P|Delta⁴)",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/equations_scope",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "historical/baseline/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "Current H1 measured DDCS20 marginal,sparseTDCS54,TDCS413 shape; finiteM labelled directCBA",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/inputs_domain",
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
        "Fullsupport/exchange/count/spin/frame/recoil/calibrated validity;directCBA not physicalprovider"
      ],
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/claim_gates",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
      "source_file": "authority/thermal/BASS_HE_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/1/review",
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
