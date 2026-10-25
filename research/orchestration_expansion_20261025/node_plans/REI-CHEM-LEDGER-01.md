# REI-CHEM-LEDGER-01

Lead: cosmosapjw-quantum/WU088_HH

Current status: `PASS_SCOPED`

Source: `authority/rei/DAG_DELTA.json#/new_child`

```json
{
  "id": "REI-CHEM-LEDGER-01",
  "lead_repo": "cosmosapjw-quantum/WU088_HH",
  "source_file": "authority/rei/DAG_DELTA.json",
  "json_pointer": "/new_child",
  "contract": {
    "id": "REI-CHEM-LEDGER-01",
    "parent": "REI-L1",
    "additional_crosslinks": [
      "CR_N5_ATOMIC_ISOTOPE_COVERAGE",
      "WU_NUCLEAR_PARTICLE_OWNERSHIP",
      "REI-L2"
    ],
    "state": "THEORY_DERIVED_CODE_CONTRACT_FROZEN_EXECUTION_PENDING",
    "claim": "finite isotope/molecule event interface only",
    "allow_scope_expansion": "arbitrary finite producer-supplied(Z,A,isomer)catalogs",
    "new_budget": {
      "CPU_s": 30,
      "wall_s": 120,
      "workers": 1,
      "memory_MiB": 512,
      "scientific_children": 1
    },
    "contract": "FROZEN_COMPILER_CONTRACT.md",
    "theory": "THEORY.md",
    "lead_repo": "WU088_HH",
    "staging_repo": "rei_bianchi",
    "consumer_repo": "rei_bianchi",
    "ownership_reassignment_authority": "ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md",
    "historical_unit_id_preserved": true
  },
  "dependencies": [],
  "conditional_dependencies": [],
  "external_prerequisites": [],
  "current_status": "PASS_SCOPED",
  "claim_gate": "IMPLEMENTATION_CHECKED_FINITE_ISOTOPE_MOLECULAR_EVENT_INTERFACE",
  "pass_next_action": "Publish finite compiler result; prepare REC-HD-ADAPTER under separate budget.",
  "budget_status": {
    "source_file": "authority/COMPILER_ADMISSION.json",
    "resource_scope": {
      "one_scientific_child_limits": {
        "cpu_s": 30,
        "wall_s": 120,
        "memory_MiB": 512,
        "workers": 1
      },
      "known_science_and_saved_plot_cpu_s": 0.352458,
      "known_science_and_saved_plot_wall_s": 0.362115,
      "preparatory_syntax_cpu_s": 0.144212,
      "unmeasured_component": "Failed optional CairoSVG import before successful Inkscape conversion; preserved as UNMEASURED_NOT_ZERO",
      "exact_all_process_cumulative_cap_claim": "NOT_ESTABLISHED",
      "historical_budget_reset": false,
      "unused_balance_authorizes_rerun": false
    },
    "executed": {
      "scientific_children": 1,
      "retries": 0,
      "exit_code": 0,
      "checks": 249,
      "checks_by_category": {
        "catalog": 46,
        "positive_chemistry": 12,
        "radiation_count_identities": 27,
        "source_tangent_identities": 78,
        "reference_identities": 26,
        "reverse_identities": 12,
        "event_identity": 26,
        "algebraic_nuclear": 2,
        "guards": 17,
        "guard_residual_identities": 3
      },
      "positive_chemical_events": 12,
      "nuclear_algebra_events": 1,
      "cpu_s": 0.088983,
      "wall_s": 0.09208228100033011,
      "new_ivps": 0,
      "historical_suite_replays": 0
    }
  },
  "change_class": [
    "new_result",
    "ownership_reassignment"
  ],
  "historical_contract_id": null,
  "source_fields": {
    "lead_repo": "lead_repo",
    "current_status": "state",
    "claim_gate": "claim",
    "pass_next_action": null,
    "budget_status": "root_admission:/resource_scope + /executed"
  },
  "status_observation": {
    "source_file": "authority/review_compiler/FINAL_C9_REVIEW.json",
    "json_pointer": "",
    "value": {
      "schema_version": 1,
      "unit_id": "REI-CHEM-LEDGER-01",
      "review_date": "2026-10-25",
      "decision": "PASS_SCOPED",
      "admitted_claim": "IMPLEMENTATION_CHECKED_FINITE_ISOTOPE_MOLECULAR_EVENT_INTERFACE",
      "lead_repo": "WU088_HH",
      "consumer_repo": "rei_bianchi",
      "independent_reviewer": true,
      "requested_role": "Astra",
      "observed_model_identity": "UNOBSERVED",
      "source_review": "PREEXEC_PASS.md",
      "raw_results_sha256": "a340635ba0f11140d6034d64e5fb2c8c12baa95488fa0973f2f7ce495827567a",
      "raw_rows": 249,
      "failed_rows": 0,
      "visual_inspection": {
        "status": "PASS_SCOPED",
        "actual_image_viewed": true,
        "file": "figures/exact_residuals.png",
        "sha256": "40c98031f80cfca3450079ed6ad5681f355f7a5483507369a6be483d6dc09abd"
      },
      "findings": [
        {
          "id": "R1",
          "status": "CLOSED"
        },
        {
          "id": "R2",
          "status": "CLOSED"
        }
      ],
      "execution_repeated_by_reviewer": false,
      "known_measured_cpu_seconds": 0.352458,
      "known_measured_wall_seconds": 0.36211454,
      "all_process_exact_cumulative": "UNRESOLVED_ENVIRONMENT_IMPORT_PROBE_OVERHEAD_NOT_ZERO",
      "scientific_child_cpu_seconds": 0.088983,
      "scientific_child_exit_code": 0,
      "physical_rate_coverage": "NOT_ADMITTED",
      "global_physical_completion": null,
      "L4_ready": false,
      "next_action": "Publish finite compiler result; prepare REC-HD-ADAPTER under separate budget."
    }
  },
  "parent_containment": "REI-L1",
  "full_contract_source": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
  "contract_appendix": "authority/compiler/R2_PHOTON_COUNT_CLARIFICATION.md",
  "root_admission": {
    "source_file": "authority/COMPILER_ADMISSION.json",
    "json_pointer": "",
    "value": {
      "unit_id": "REI-CHEM-LEDGER-01",
      "date_kst": "2026-10-25",
      "decision": "PASS_SCOPED",
      "claim": "IMPLEMENTATION_CHECKED_FINITE_ISOTOPE_MOLECULAR_EVENT_INTERFACE",
      "lead_repository": "cosmosapjw-quantum/WU088_HH",
      "integration_consumer": "cosmosapjw-quantum/rei_bianchi",
      "location": "research/rei_chem_ledger_20261025",
      "theory": "authority/rei/THEORY.md",
      "frozen_contract": "authority/rei/FROZEN_COMPILER_CONTRACT.md",
      "independent_preexecution_review": "authority/review_compiler/PREEXEC_PASS.md",
      "independent_final_review": "authority/review_compiler/FINAL_C9_REVIEW.json",
      "root_visual_read": "Actual exact_residuals.png read: accepted chemical rows have exact zero residuals; nuclear isotope delta is explicit and energy unqualified; missing/double-electron controls have signed charge residuals; duplicate bolometric owner gives +15eV/event",
      "executed": {
        "scientific_children": 1,
        "retries": 0,
        "exit_code": 0,
        "checks": 249,
        "checks_by_category": {
          "catalog": 46,
          "positive_chemistry": 12,
          "radiation_count_identities": 27,
          "source_tangent_identities": 78,
          "reference_identities": 26,
          "reverse_identities": 12,
          "event_identity": 26,
          "algebraic_nuclear": 2,
          "guards": 17,
          "guard_residual_identities": 3
        },
        "positive_chemical_events": 12,
        "nuclear_algebra_events": 1,
        "cpu_s": 0.088983,
        "wall_s": 0.09208228100033011,
        "new_ivps": 0,
        "historical_suite_replays": 0
      },
      "resource_scope": {
        "one_scientific_child_limits": {
          "cpu_s": 30,
          "wall_s": 120,
          "memory_MiB": 512,
          "workers": 1
        },
        "known_science_and_saved_plot_cpu_s": 0.352458,
        "known_science_and_saved_plot_wall_s": 0.362115,
        "preparatory_syntax_cpu_s": 0.144212,
        "unmeasured_component": "Failed optional CairoSVG import before successful Inkscape conversion; preserved as UNMEASURED_NOT_ZERO",
        "exact_all_process_cumulative_cap_claim": "NOT_ESTABLISHED",
        "historical_budget_reset": false,
        "unused_balance_authorizes_rerun": false
      },
      "review_repairs": [
        {
          "id": "R1",
          "issue": "Negative-control residual literals were initially presented as observed residuals",
          "resolution": "Compute actual mutated-column residuals, compare separate literal expectations and plot saved observed values",
          "status": "CLOSED_BEFORE_EXECUTION"
        },
        {
          "id": "R2",
          "issue": "Case01 photon removal count was implicit in energy only",
          "resolution": "Explicit -1/+1 photon counts and independently supplied15eV, exact count/source/reverse/energy tests; others remain unqualified",
          "status": "CLOSED_BEFORE_EXECUTION"
        }
      ],
      "physical_scope": {
        "synthetic_energies": true,
        "empirical_rate_admission": false,
        "nuclear_Q_admission": false,
        "all_target_physical_coverage": false,
        "global_physical_completion": null,
        "L4_ready": false
      },
      "pass_next_action": "WU uses the checked catalog/event semantics to qualify concrete atomic/molecular reaction rows; REC can implement the pinned HD adapter; REI binds selected events with one physical owner. Future source/run contracts remain explicit.",
      "publication_and_delivery": "PENDING_SEPARATE_GIT_AND_FINAL_BACKUP_RECEIPTS"
    }
  },
  "publication_role": {
    "canonical_repository": "cosmosapjw-quantum/WU088_HH",
    "central_copy": "IMMUTABLE_INTEGRATION_MIRROR",
    "canonical_commit": "PENDING_ROOT_PUBLICATION"
  },
  "pr_plan": {
    "inputs": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Frozen synthetic fixtures",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    },
    "equations": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Derived results to implement",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    },
    "units": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Definitions and conventions",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    },
    "domain": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Objective and exact novelty",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    },
    "outputs": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Acceptance and output",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    },
    "positive_acceptance": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Acceptance and output",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    },
    "failure_disposition": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Allowed files and execution",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    },
    "independent_review": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Acceptance and output",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    },
    "PR_boundary": {
      "source_file": "authority/compiler/FROZEN_COMPILER_CONTRACT.md",
      "section": "Allowed files and execution",
      "qualification": "VERBATIM_FROZEN_MARKDOWN_CONTRACT_SECTION"
    }
  }
}
```
