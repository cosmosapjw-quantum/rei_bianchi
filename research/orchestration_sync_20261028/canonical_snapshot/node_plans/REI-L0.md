# REI-L0

Lead: cosmosapjw-quantum/rei_bianchi

Current status: `ADMITTED_SCOPED`

Source: `historical/baseline/rei/CONTRACTS.json#/nodes/0`

```json
{
  "id": "REI-L0",
  "lead_repo": "cosmosapjw-quantum/rei_bianchi",
  "source_file": "historical/baseline/rei/CONTRACTS.json",
  "json_pointer": "/nodes/0",
  "contract": {
    "repository": "cosmosapjw-quantum/rei_bianchi",
    "authority": "REI scientific authority; independent review required",
    "publication_target": {
      "branch": "research/orchestration-sandbox-20261022",
      "base": "b4b5d289aaad9ef167f683f19418b0ff87ed8425",
      "path": "research/orchestration_longterm_20261023",
      "mode": "central additive master contracts; future leaf code not executed now"
    },
    "no_replay": [
      "ANGTHERM01 completed10",
      "ANGTHERM02 active owner cases",
      "C3 atomic156+separate2",
      "localflow103+separate96",
      "D10 saved35",
      "PR220127+2 cases"
    ],
    "units": {
      "clock": "proper seconds; eta via d/deta=H^-1 d/dt",
      "energy": "eV per Href with explicit SI conversion",
      "stress": "physical tensor=nHref * eV_to_J * perHref tensor",
      "metric": "(-,+,+,+)",
      "shear_norm": "full Frobenius"
    },
    "id": "REI-L0",
    "dependencies": [
      "external:ANGTHERM01@6daf382ee698835e7a141378c232d1d97c1c5cf1",
      "external:X1_HE38_ANGULAR_PSD_REVIEW"
    ],
    "title": "Source-exchange and signed stress adapter",
    "status": "READY_THEORY_CONTRACT_FUTURE_EXECUTION",
    "owner": "REI",
    "scope": "Finite energy-exchange and signed STF assembly; dynamic escape separated from bolometric ledger",
    "allowed_paths": [
      "research/rei_closed_exchange_20261023/**"
    ],
    "input_sources": [
      "THEORY_AND_PR_PLANS.md#constructive-source-and-stress-assembly",
      "ANGTHERM01 THEORY blob7e110c8328ace7d7b4a511bbe3c14d8cb00a40c6"
    ],
    "equations": {
      "PI": [
        "E-chi",
        "chi",
        "-E",
        "0",
        "0"
      ],
      "RR": [
        "-K",
        "-chi",
        "0",
        "chi+K",
        "0"
      ],
      "column_order": [
        "gas_thermal",
        "binding",
        "uv_radiation",
        "dynamic_escape_radiation",
        "source_reservoir"
      ],
      "balance": "du_A/dt+3H*p_A+sigma:pi_A=q_A",
      "lrs": "pi=diag(-Q/3,-Q/3,2Q/3); sigma:pi=2*s_h*Q",
      "realizability": "U>=0 and -U/2<=Q<=U"
    },
    "acceptance": [
      "Exact rational source-column sums0",
      "charge/photon event accounting",
      "Jacobian column cancellation",
      "scaled binary64 residual<=2e-12",
      "sum signed tensors before norm; opposite-stress cancellation",
      "detect duplicate bolometric/dynamic escape owner",
      "explicit external feed in open balance"
    ],
    "claim_limit": "Selected algebraic assembly only; no physical source calibration, transport or Einstein solution",
    "budget": {
      "initial_probe_cpu_s_max": 30,
      "cumulative_cap": "NOT_FROZEN; controller must bind previous debit before execution",
      "new_ivps": 0,
      "ncp": 0
    },
    "pass_next": "REI-L1",
    "failure_action": "One concrete targeted repair then authority decision"
  },
  "dependencies": [
    {
      "type": "external",
      "source_reference": "external:ANGTHERM01@6daf382ee698835e7a141378c232d1d97c1c5cf1",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "source_field": "dependencies"
    },
    {
      "type": "external",
      "source_reference": "external:X1_HE38_ANGULAR_PSD_REVIEW",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "source_field": "dependencies"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "ADMITTED_SCOPED",
  "claim_gate": [
    "Exact rational source-column sums0",
    "charge/photon event accounting",
    "Jacobian column cancellation",
    "scaled binary64 residual<=2e-12",
    "sum signed tensors before norm; opposite-stress cancellation",
    "detect duplicate bolometric/dynamic escape owner",
    "explicit external feed in open balance"
  ],
  "pass_next_action": "REI-L1",
  "budget_status": {
    "initial_probe_cpu_s_max": 30,
    "cumulative_cap": "NOT_FROZEN; controller must bind previous debit before execution",
    "new_ivps": 0,
    "ncp": 0
  },
  "change_class": [
    "status_correction"
  ],
  "historical_contract_id": "REI-L0",
  "source_fields": {
    "lead_repo": "source_group_repository",
    "current_status": "status",
    "claim_gate": "acceptance",
    "pass_next_action": "pass_next",
    "budget_status": "budget"
  },
  "status_observation": {
    "source_file": "authority/rei/DAG_DELTA.json",
    "json_pointer": "/observations/REI-L0",
    "value": {
      "current_scoped_state": "ADMITTED_SCOPED",
      "source_commit": "c5050305f84a051cb797cd84c84768c76bcb18b9",
      "source_path": "research/rei_closed_exchange_20261023/uv_mixed_20261024/ADMISSION.json",
      "candidate_sha256": "c8dc1d8e8ad1ee72693bae20b86367b0e1aa1e52e9ff307575d21ca0b9279f77",
      "whole_L0_debit": "UNKNOWN_NOT_ZERO",
      "legacy_failed_cpu_s": 10.110448,
      "legacy_cap_cpu_s": 10,
      "old83_replay": 0
    }
  },
  "pr_plan": {
    "inputs": {
      "value": [
        "THEORY_AND_PR_PLANS.md#constructive-source-and-stress-assembly",
        "ANGTHERM01 THEORY blob7e110c8328ace7d7b4a511bbe3c14d8cb00a40c6"
      ],
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/0/input_sources",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": {
        "PI": [
          "E-chi",
          "chi",
          "-E",
          "0",
          "0"
        ],
        "RR": [
          "-K",
          "-chi",
          "0",
          "chi+K",
          "0"
        ],
        "column_order": [
          "gas_thermal",
          "binding",
          "uv_radiation",
          "dynamic_escape_radiation",
          "source_reservoir"
        ],
        "balance": "du_A/dt+3H*p_A+sigma:pi_A=q_A",
        "lrs": "pi=diag(-Q/3,-Q/3,2Q/3); sigma:pi=2*s_h*Q",
        "realizability": "U>=0 and -U/2<=Q<=U"
      },
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/0/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": {
        "clock": "proper seconds; eta via d/deta=H^-1 d/dt",
        "energy": "eV per Href with explicit SI conversion",
        "stress": "physical tensor=nHref * eV_to_J * perHref tensor",
        "metric": "(-,+,+,+)",
        "shear_norm": "full Frobenius"
      },
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/0/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Finite energy-exchange and signed STF assembly; dynamic escape separated from bolometric ledger",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/0/scope",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": "Finite energy-exchange and signed STF assembly; dynamic escape separated from bolometric ledger",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/0/scope",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "Exact rational source-column sums0",
        "charge/photon event accounting",
        "Jacobian column cancellation",
        "scaled binary64 residual<=2e-12",
        "sum signed tensors before norm; opposite-stress cancellation",
        "detect duplicate bolometric/dynamic escape owner",
        "explicit external feed in open balance"
      ],
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/0/acceptance",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "One concrete targeted repair then authority decision",
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/0/failure_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": null,
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": null,
      "qualification": "NOT_DECLARED_SEPARATELY_IN_SOURCE"
    },
    "PR_boundary": {
      "value": [
        "research/rei_closed_exchange_20261023/**"
      ],
      "source_file": "historical/baseline/rei/CONTRACTS.json",
      "json_pointer": "/nodes/0/allowed_paths",
      "qualification": "SOURCE_DECLARED"
    }
  },
  "runnable": false,
  "missing_contract_fields": [
    "independent_review"
  ],
  "execution_readiness_guard": {
    "source_file": "authority/FINAL_ASSEMBLY_MISSING_FIELDS.json",
    "scope": "Execution-readiness guard only; retain finite past admissions and source object unchanged",
    "other_nodes_runnable_not_inferred": true
  }
}
```
