# REC-COUPLED

Lead: cosmosapjw-quantum/rec_bianchi

Current status: `CONSTRUCTIVE_PARTIAL_CONDITIONAL_NATIVE_THERMAL_JOIN`

Source: `authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json#/nodes/5`

```json
{
  "id": "REC-COUPLED",
  "lead_repo": "cosmosapjw-quantum/rec_bianchi",
  "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
  "json_pointer": "/nodes/5",
  "contract": {
    "id": "REC-COUPLED",
    "status": "INPUT_DEPENDENT_NOT_SCHEDULED",
    "depends_on": [],
    "equations_scope": "dY/dt=Nu R; C(Y,T)dT/dt=Q_th+work-(partial U_th/partial Y)dY/dt; matter/radiation tensor separate",
    "inputs_domain": "Declared selected source subset and matchingIC",
    "claim_gates": [
      "Selected source gates,independent oracle,observable error allocation; U5holds retained"
    ],
    "pass_action": "Genuinely new bounded control then separate convergence",
    "budget": "NewIVP NOT_AUTHORIZED",
    "fail_action": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
    "review": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
    "tests": "Same-source contract controls and affected derivative/conservation tests only; original tolerance preserved",
    "historical_source_dependencies": [
      "REC-HISTORY",
      "REC-LI",
      "REC-FIELD"
    ],
    "conditional_dependencies": [
      {
        "id": "REC-HISTORY",
        "predicate": "selected_model_uses_retarded_radiation_history",
        "scope": "selected-model prerequisite only"
      },
      {
        "id": "REC-LI",
        "predicate": "selected_species_or_channels_include_Li",
        "scope": "selected-model prerequisite only"
      },
      {
        "id": "REC-FIELD",
        "predicate": "selected_model_evolves_spectral_radiation_or_gas_radiation_exchange",
        "scope": "selected-model prerequisite only"
      }
    ],
    "dependency_change": "2026-10-25 current readiness correction; original source contracts preserved in EVIDENCE_FILTERED"
  },
  "dependencies": [],
  "conditional_dependencies": [
    {
      "id": "REC-HISTORY",
      "predicate": "selected_model_uses_retarded_radiation_history",
      "scope": "selected-model prerequisite only",
      "type": "internal",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "source_field": "conditional_dependencies"
    },
    {
      "id": "REC-LI",
      "predicate": "selected_species_or_channels_include_Li",
      "scope": "selected-model prerequisite only",
      "type": "internal",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "source_field": "conditional_dependencies"
    },
    {
      "id": "REC-FIELD",
      "predicate": "selected_model_evolves_spectral_radiation_or_gas_radiation_exchange",
      "scope": "selected-model prerequisite only",
      "type": "internal",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "source_field": "conditional_dependencies"
    }
  ],
  "external_prerequisites": [],
  "current_status": "INPUT_DEPENDENT_NOT_SCHEDULED",
  "claim_gate": [
    "Selected source gates,independent oracle,observable error allocation; U5holds retained"
  ],
  "pass_next_action": "Genuinely new bounded control then separate convergence",
  "budget_status": "NewIVP NOT_AUTHORIZED",
  "change_class": [
    "status_correction",
    "dependency_change"
  ],
  "historical_contract_id": "REC-COUPLED",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "claim_gates",
    "pass_next_action": "pass_action",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "Declared selected source subset and matchingIC",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "dY/dt=Nu R; C(Y,T)dT/dt=Q_th+work-(partial U_th/partial Y)dY/dt; matter/radiation tensor separate",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/equations_scope",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": null,
      "source_file": "historical/baseline/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "domain": {
      "value": "Declared selected source subset and matchingIC",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/inputs_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": null,
      "source_file": "historical/baseline/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "positive_acceptance": {
      "value": [
        "Selected source gates,independent oracle,observable error allocation; U5holds retained"
      ],
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/claim_gates",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure; one diagnosed affected repair; return substantive scientific ambiguity to authority",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Independent changed-dependency review;source/science/runtime/CI/delivery separate",
      "source_file": "authority/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
      "json_pointer": "/nodes/5/review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": null,
      "source_file": "historical/baseline/thermal/rec_bianchi_LONGTERM_CONTRACTS.json",
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

## Selected runtime observation, 2026-10-27

Decision: `CONSTRUCTIVE_PARTIAL_SELECTED_NATIVE_PW19_PREASSIMILATION_SOURCE`. This is a constructive selected-source partial at the saved native PW19 He II snapshot. The original JSON source contract in the fenced block above, its missing fields and `runnable=false` remain unchanged; the additive selected runtime contract is in this plan's corresponding standalone JSON and DAG wrapper. The original REC-COUPLED gate, REC-EXP-COUPLED, L4 and full physical pilot remain open; canonical count is 32/88.

Reviewed evidence:

- `admission`: `research/rei_expanded_event_consumer/coupled_source_20261027/ADMISSION.json` (SHA-256 `17473a9b0586cb89aa8e2a1cdd937e461cd0880d0fe9c5ee767d969686140f06`)
- `independent_review`: `research/rei_expanded_event_consumer/coupled_source_20261027/review/VALIDATION.json` (SHA-256 `88456ff3ca01a1b7ea08b8b5d0689467d16b7f1ef5370cb65c3cfe58320960b3`)
- `raw_result`: `research/rei_expanded_event_consumer/coupled_source_20261027/implementation/attempt03/stdout.json` (SHA-256 `c8901be9237badf5191b6663177d307bf4e9b9d1c536ed9c178cafb895165f71`)
- `run_receipt`: `research/rei_expanded_event_consumer/coupled_source_20261027/implementation/attempt03/RESOURCE_RECEIPT.json` (SHA-256 `228a34e99eeb08bca640e229be79721e9aa9bc89aa532578ca0e8f9806bc6d29`)
- `original_scientific_check_failed_stderr`: `research/rei_expanded_event_consumer/coupled_source_20261027/implementation/attempt01/stderr.log` (SHA-256 `5a5f9a8adb89a9acb87d76361e9dc9c353affad7bf755d75b935ead37d6805e8`)
- `original_scientific_check_failed_receipt`: `research/rei_expanded_event_consumer/coupled_source_20261027/implementation/attempt01/RESOURCE_RECEIPT.json` (SHA-256 `cce1bfe4b8e72ca56bb90f90ba4fd46ab13e3948ce8e0fa48acb6abdbbe22756`)
- `runner_precheck_failed_stderr`: `research/rei_expanded_event_consumer/coupled_source_20261027/implementation/attempt02/stderr.log` (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)
- `runner_precheck_failed_receipt`: `research/rei_expanded_event_consumer/coupled_source_20261027/implementation/attempt02/RESOURCE_RECEIPT.json` (SHA-256 `c725fe304cb55d1ca7578419327f3d9cffabb230228fc15a587ad25b0834263b`)

Scoped owner return: `research/orchestration_expansion_20261025/returns/REI_COUPLED_SOURCE_20261027.json`.

## Conditional thermal assimilation observation, 2026-10-27

Decision: `CONSTRUCTIVE_PARTIAL_CONDITIONAL_NATIVE_THERMAL_JOIN`. The saved native PW19 He II source now has a conditional local 25-state join to prescribed constant-in-energy number and energy relaxation, native RR/DR cooling, Planck-reference Compton and the actual HE caloric helper. Every thermal term uses the same thermal electron subset. The preserved attempt01 produced 118 passing focused checks; the independent C9 review is `PASS_CONDITIONAL_NATIVE_COUPLED_LOCAL_SOURCE` with zero blocking findings.

This observation uses a manufactured fast reservoir on the saved native background. Its prescribed rate is an independent conditional parameter; physical stopping/assimilation rate and physical uncertainty remain null. Local directional-derivative evidence does not certify the full state Jacobian, a whole-domain VigilODE client, a history, or a new IVP. REC-COUPLED and REC-EXP-COUPLED retain their original open gates. Working original finite admissions remain 32/88; this update contributes zero new original-node completions. L4 and full physical completion remain open.

The original fenced source wrapper and prior photo-source observation above are preserved. The separate `thermalAssimilationContract` pointer in the standalone wrapper and DAG resolves to the new frozen contract below; the old `selectedRuntimeContract` remains unchanged.

- Source code commit: `20b91606493fb7bad015c62fd62e2faa971faee0` (pre-execution code only).
- `admission`: `research/rei_expanded_event_consumer/thermal_assimilation_20261027/ADMISSION.json` (root admission; resolve from the containing publication commit).
- `frozen_contract`: `research/rei_expanded_event_consumer/thermal_assimilation_20261027/theory/ROOT_FROZEN_CONTRACT.md` (SHA-256 `d6db25daef4c89be9c85c268a5d21cb9aa8a3f34548068f2e76ee95bcd7019b3`).
- `derivation`: `research/rei_expanded_event_consumer/thermal_assimilation_20261027/theory/THERMAL_JOIN_DERIVATION.md` (SHA-256 `ad8f2ca6b77da92b229aae8bc18906ce264989700aeb9d077005938f839ab480`).
- `independent_review`: `research/rei_expanded_event_consumer/thermal_assimilation_20261027/review/C9_VALIDATION.json` (SHA-256 `122749e2d50a49d76e6eb0442cc5abd063246ceecf390508d80f1e839c261189`).
- `raw_result`: `research/rei_expanded_event_consumer/thermal_assimilation_20261027/implementation/attempt01/stdout.json` (SHA-256 `3f6e942336cb18cf1422ce4736984fb5d7f7d85ca1af39aa0f126748a0c66d99`).
- `forward_raw`: `research/rei_expanded_event_consumer/thermal_assimilation_20261027/implementation/attempt01/FORWARD_RAW.json` (SHA-256 `de1fbe6b125efce45a4999f1e4666b7e8bde1274a4d3b81d6dba854853284149`).
- `run_receipt`: `research/rei_expanded_event_consumer/thermal_assimilation_20261027/implementation/attempt01/RESOURCE_RECEIPT.json` (SHA-256 `126f716340b1e42a0c90e2a06fdddfe299e3e822c5c382be55f51a1da877575e`).
