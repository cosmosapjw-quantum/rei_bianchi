# HE-EXP-CLOSURE

Lead: cosmosapjw-quantum/BASS_HE

Current status: `CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING`

Source: `authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/6`

```json
{
  "id": "HE-EXP-CLOSURE",
  "lead_repo": "cosmosapjw-quantum/BASS_HE",
  "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/6",
  "contract": {
    "id": "HE-EXP-CLOSURE",
    "status": "GATED",
    "depends_on": [],
    "provider_domain": "Allspecies gas+nonthermal populations; molecules internal modes",
    "equations": "pi_b=sum[pi_s+rho_s driftSTF]; Uth=sum(3/2)n_s kBT_s+U_internal;liftcommutator",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/BASS_HE",
    "prerequisites": "Species timescales/source/relaxation uncertainty and observables",
    "claim_gate": "CommonT/u requires calibrated reduction; particlecount/heatcapacity separate",
    "pass_next": "Saved-background finitegas thenHE-FEEDBACK",
    "budget": "NoIVP authorized",
    "tests": "Only affected source/state/measure/units/conservation/tangent checks; original numerical tolerance retained; no unchangedsuite replay",
    "fail_action": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
    "uncertainty": "Provider/model/interpolation/quadrature/floating error separate; null until actual evidence",
    "units": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
    "lead_repo": "cosmosapjw-quantum/BASS_HE",
    "consumer_repo": "cosmosapjw-quantum/BASS_HE",
    "outputs": [
      "source-qualified result within stated domain",
      "explicit unresolved provider/model uncertainty",
      "consumer-facing event/state contract",
      "unchanged historical evidence with additive status observation"
    ],
    "conditional_dependencies": [
      {
        "id": "HE-EXP-PAIR",
        "predicate": "selected_reduction_uses_pair_exchange"
      },
      {
        "id": "HE-EXP-STOPPING",
        "predicate": "selected_model_has_nonthermal_stopping"
      },
      {
        "id": "HE-RESERVOIR",
        "predicate": "selected_model_has_external_injection"
      }
    ],
    "independent_review": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
    "resource_allowance": {
      "cpu_s": null,
      "wall_s": null,
      "memory_bytes": null,
      "status": "UNALLOCATED_BY_THIS_PROSPECTIVE_PLAN",
      "reset_or_borrow_historical": false
    }
  },
  "dependencies": [],
  "conditional_dependencies": [
    {
      "id": "HE-EXP-PAIR",
      "predicate": "selected_reduction_uses_pair_exchange",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    },
    {
      "id": "HE-EXP-STOPPING",
      "predicate": "selected_model_has_nonthermal_stopping",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    },
    {
      "id": "HE-RESERVOIR",
      "predicate": "selected_model_has_external_injection",
      "type": "internal",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    }
  ],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Species timescales/source/relaxation uncertainty and observables",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
  "claim_gate": "CommonT/u requires calibrated reduction; particlecount/heatcapacity separate",
  "pass_next_action": "Saved-background finitegas thenHE-FEEDBACK",
  "budget_status": "NoIVP authorized",
  "change_class": [
    "scope_expansion"
  ],
  "historical_contract_id": null,
  "source_fields": {
    "lead_repo": "lead_repo",
    "current_status": "status",
    "claim_gate": "claim_gate",
    "pass_next_action": "pass_next",
    "budget_status": "budget"
  },
  "pr_plan": {
    "inputs": {
      "value": "Species timescales/source/relaxation uncertainty and observables",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "pi_b=sum[pi_s+rho_s driftSTF]; Uth=sum(3/2)n_s kBT_s+U_internal;liftcommutator",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Allspecies gas+nonthermal populations; molecules internal modes",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/provider_domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "source-qualified result within stated domain",
        "explicit unresolved provider/model uncertainty",
        "consumer-facing event/state contract",
        "unchanged historical evidence with additive status observation"
      ],
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "CommonT/u requires calibrated reduction; particlecount/heatcapacity separate",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/6/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": [
        "research/program_expansion_20261025/**"
      ],
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/allowed_paths",
      "qualification": "SOURCE_DECLARED"
    }
  },
  "status_observation": {
    "source_file": "status/HE_EXP_INTAKE01_20261025.json",
    "json_pointer": "/observations/HE-EXP-CLOSURE",
    "value": {
      "unit_id": "HE-EXP-INTAKE-01",
      "current_scoped_state": "CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING",
      "scoped_contribution": "Conditional caloric-count and energy-ownership implementation verified; physical closure inputs pending.",
      "source_intake": {
        "source_file": "status/HE_EXP_INTAKE01_20261025.json",
        "json_pointer": "/source_intake"
      },
      "source_repository": "cosmosapjw-quantum/BASS_HE",
      "source_commit": "965da72aa7a5e885e12956fafadfb8dc2519b81f",
      "physical_provider_admitted": false,
      "production_status": "NOT_APPROVED",
      "activation": false,
      "physical_allocation": "UNALLOCATED"
    }
  }
}
```


## Preserved historical observation context

The following narrative is historical local/unpublished observation context, not a replacement for the latest base contract above. DRIFT02: `status/HE_EXP_FINITE_DRIFT_20261027.json#/observations/HE-EXP-CLOSURE`.


## HE-EXP-EVENT-03 observation

Population-derived internal energy witness has a single owner; product birth pool remains UNASSIGNED. Source is locally prepared and unpublished; physical inputs remain open. See `status/HE_EXP_EVENT03_20261027.json#/observations/HE-EXP-CLOSURE`.

## HE-EXP-STATE-04 observation

Named scalar level-edge consumer retains internal energy witness ownership and UNASSIGNED birth pool; Bennett 2008 corrected rate selection supersedes, never adds to, the historical same-owner 2003 table. Source is locally prepared and unpublished; physical dependencies remain open. See `status/HE_EXP_STATE04_20261027.json#/observations/HE-EXP-CLOSURE`.

## HE-EXP-PHOTON-05 observation

Photon loss, population rest-energy witness and daughter kinetic energy close one event ledger; material nucleus count +1 remains distinct from Gamma_thermal, Cv, heating and deposition. Native zero-flux examples do not supply or set a physical rate. Core24 tests PASS; generated plot has a preserved CPU-cap FAIL, so the local workflow is partial. Source remains local/unpublished; no physical promotion. See `status/HE_EXP_PHOTON05_20261027.json#/observations/HE-EXP-CLOSURE`.


## Current local observation pointer

See `status/HE_EXP_ANGULAR06_20261027.json#/observations/HE-EXP-CLOSURE`. Central publication has not occurred. Current scoped state, budget, lead and dependency gates remain unchanged.


## HE-EXP-APERTURE-07 prepared observation (C9 accepted; actual S09/P09 and S10/P10 identities)

Root accepted the scoped conditional finite-aperture pair-observable reference, retaining separate event, daughter-count and energy ownership. The 32/32 validation, separately allocated saved-data plot and same-pass C9 actual-result review passed. Physical reduction, heat capacity and thermal-deposition admission are unchanged.

See `status/HE_EXP_APERTURE07_20261027.json#/observations/HE-EXP-CLOSURE`. S09/P09 science identity is actual; S10/P10 delivery identity is actual in the status record. Current physical status, budget, lead, dependencies and claim gates remain unchanged.


## KINEMATIC08 scoped observation — 2026-10-28

Scoped physical-input pair-observable reference accepted with event, daughter-count and rest/binding energy ownership separate. Validation passes; plot CPU gate fails, so workflow remains PARTIAL and physical closure inputs remain pending.

ROOT decision: `ACCEPT_SCOPED_PHYSICAL_INPUT_REFERENCE_WITH_WORKFLOW_PARTIAL`. Local DAG: 8 complete + 1 partial + 3 physical open /12; central 28/88, HE delta 0. Validation 14/14 PASS, scientific suite 1. Saved-only plot 1, scientific calls 0; CPU 7.040661/6 s FAIL. Workflow PARTIAL; no all-checks PASS, physical activation, new budget or rerun. Existing owner, dependencies, status, claim gates and budget remain unchanged.

Observation: `status/HE_EXP_KINEMATIC08_20261028.json#/observations/HE-EXP-CLOSURE`; actual source and dual backup identities: `status/HE_EXP_KINEMATIC08_20261028.json#/final_identities`. Central publication flags in that file are a `PRE_CAS_CANDIDATE_SNAPSHOT`; the actual post-CAS external receipt is authoritative.


## AZIMUTH09 scoped observation — 2026-10-28

Certified finite-sector paired-event reference accepted with event/count and rest-energy ownership kept explicit. Declared azimuth and manufactured density do not supply actual birth/deposition/thermalization or global species closure.

ROOT decision: `ACCEPT_SCOPED_FINITE_AZIMUTH_REFERENCE`. Local DAG: 9 complete + 1 partial + 3 physical open /13; central 28/88, HE delta0. One validation22/22 PASS; one Wolfram call109/109 literal zeros plus2 true comparisons, remote CPU unknown/null. One saved-data plot PASS CPU2.053974/8 s; scientific imports/calls0. Workflow COMPLETE_SCOPED only for this reference. KINEMATIC08 plot7.040661/6 s FAIL, PARTIAL and reserve0 remain unchanged. Existing current status, owner, dependencies, budgets and physical gates remain unchanged; no new execution or physical activation.

Observation: `status/HE_EXP_AZIMUTH09_20261028.json#/observations/HE-EXP-CLOSURE`; actual source/dual-backup identities: `status/HE_EXP_AZIMUTH09_20261028.json#/final_identities`. Central publication flags are a PRE_CAS_CANDIDATE_SNAPSHOT; later actual post-CAS external receipt is authoritative.


## HARMONIC10 scoped observation — 2026-10-28

Certified signed Fourier-Bernstein integration and combined polar/rational-arithmetic bounds extend the finite-sector same-event reference. Manufactured law does not supply actual birth/deposition/thermalization or global species binding.

ROOT decision: `ACCEPT_SCOPED_SECOND_HARMONIC_REFERENCE`. Local DAG: 10 complete + 1 inherited partial + 3 physical open /14; central 28/88, HE delta0. Actual validation: 25 unique methods, 26 evaluations; initial full suite 24 PASS + 1 FAIL, followed by one targeted test20 PASS. Initial failure and original empty control remain preserved; production code unchanged, no full-suite rerun, repair reserve0. One Wolfram call returned117 literal-zero residuals and14 True checks with2 precision warnings; attained130-digit precision is not certified, remote CPU/wall null. Saved-only plot PASS CPU2.806525/10 s and wall2.835772674/30 s, one attempt, scientific imports/calls0; original footer clipping remains qualified. Recorded independent pass1: theory12/12, static15/15, actual13 unqualified PASS +1 precision-qualified/14; two findings closed, blockers0.

Actual S09 science publication: `39dc63b4bf4d60b255ea3ca5323661ccc80ca880`, tree `10ab6a622a4e0101cfffefdef93a8156bfe35c32`. Actual S10 delivery publication: `a73773a9e1056bf18405453a0e88b9d12a15e9ac`, tree `4e308ea37c6907f6b0064951e71d14667831a6a3`; both source and dual backups ACKed. Both validation execution pins and the plot execution pin are retained at `status/HE_EXP_HARMONIC10_20261028.json#/final_identities/execution_sources`.

Three physical inputs remain open; single rest/binding owner population_rest_energy_witness, null thermal quantities, birth_pool UNASSIGNED, global completion null, L4 false, production NOT_APPROVED, activation false. Existing statuses, owners, dependencies, gates, budgets,17 integration edges and prior outcomes remain unchanged. Observation: `status/HE_EXP_HARMONIC10_20261028.json#/observations/HE-EXP-CLOSURE`; prior observations are preserved by actual source surface in that document. Central publication flags remain a PRE_CAS_CANDIDATE_SNAPSHOT; actual central publication is pending external ACK/readback.


## EXFOR11 data-conditioned aperture reference — 2026-10-28

- Scoped decision: ACCEPT_SCOPED_DATA_CONDITIONED_APERTURE_REFERENCE.
- Source: cosmosapjw-quantum/BASS_HE@1e393c7901d08aaf97c4c3568ef4ab120d43e9c5; tree 7c33ed3f6a9b88402ff9c0ebe7b45840202b7fef.
- Unit: research/program_expansion_20261025/continuation_exfor_20261028/.
- Central observation: status/HE_EXP_EXFOR11_20261028.json#/observations/HE-EXP-CLOSURE.
- Exact inner/true/outer polytope sandwich and inherited finite-mass paired-detector geometry yield conditional ratio enclosures. Event count, daughter count, rest/binding ownership and heating remain distinct.
- Local11 complete +1 inherited partial +3 physical open /15; Central28/88, HE delta0.
- Existing current_status, lead, budgets, dependencies and gates are unchanged. All3 physical inputs remain open; global_physical_completion=null, L4_ready=false, production=NOT_APPROVED, activation=false.
- Validation6PASS/0FAIL in1 new campaign,12cases/274 exact certificate vertices; Wolfram21zero/8True;1saved-only plotPASS. Complete source/Drive/Dropbox stageACKs are bound in the observation record. Historical HARMONIC10 initial24PASS+1FAIL/targeted1PASS/reserve0 and earlier partial workflows remain preserved.
- This paragraph and in-Git observation are creation-time PRE_CAS snapshots. Actual central publication is established by the external POSTPUBLICATION CENTRAL_PUBLICATION_RECEIPT, not a predicted future commit.


## QUARTIC12 scoped reference return — 2026-10-28

Actual HE source 4c71acfa2b8721a0d0b8f9cec8814f75f1c55739; exact tree 08e11c808d86cdf2a00ceb9feb3de43fc1bf3089.
Decision ACCEPT_SCOPED_FULL_POSITIVE_QUARTIC_REFERENCE. Local12complete+1inheritedpartial+3physicalopen/16; central28/88,HEdelta0.
One primary7PASS0FAIL,12cases,132vertices; Wolfram16zero12True; one saved-onlyplotPASS; nonauthorfinalsciencePASS.
Fullpositive free330MeV witness lies outside old sufficient cone; endpointzero330 remains an exact scoped empty outer polytope;258 minimum finitegap retained.
Current status CONDITIONAL_OWNERSHIP_IMPLEMENTATION_VERIFIED_PHYSICAL_INPUT_PENDING and lead ownership remain unchanged. No new normalized physical source, flux, projection, deposition, globalbinding or productionapproval is supplied.
Detailed observation: status/HE_EXP_QUARTIC12_20261028.json. In-Git PRE_CAS fields reflect creationtime; actual publication receipt is external POSTPUBLICATION_EXTERNAL_DELIVERY.


## TANGENT13 scoped minimum reference — 2026-10-28

Accepted local reference HE-EXP-TANGENT-13: 13 complete + 1 inherited partial + 3 physical open / 17; central 28/88, HE delta 0. Source cosmosapjw-quantum/BASS_HE at 049e79cb453b92ac663c4e0a93577a8364c3cf54 (tree ad7c7dbf7d90159b7b938da61038989b0fc24f16), branch research/he-tangent13-20261028; successful execution pin 3beb35dc7dea7a60642497dc373c98e75ca07536.

At 258 MeV with fixed coordinate ERR-S windows, free endpoints, uniform azimuth and the full nonnegative even-quartic family, exact dual + feasible square bounds close HEMISPHERES minimum to [0.6184085476376238,0.6184085476376327] and CAPS minimum to [0.0607568813452193,0.0607568813452364] (outward decimal displays). These are minimum brackets, not the complete aperture-value range or experimental confidence interval. Actual targeted campaign 8 PASS/0 FAIL, construction 1; initial namespace-monitor failure before controls and one diagnosed repair are retained, reserve 0. One Wolfram evaluator 17 literal zero + 12 True with messages; one saved-only plot PASS/science 0 with documented axis-label overlap.

R1-R10/C1-C10 workproducts 20/20 and S01-S10 source/ref readback/Drive/Dropbox backups plus R01 repair checkpoint are actual. The new status status/HE_EXP_TANGENT13_20261028.json preserves per-surface previous observations. Its PRE_CAS null/false fields are creation-time snapshots; the external CENTRAL_PUBLICATION_RECEIPT and final delivery authorities record later actual ACK.

No physical source input supplied: normalization + liquid-He projection, actual angular/polarization law + photon history, named nonthermal deposition + global species binding remain open. Existing node state, lead repo, contract, deps, budgets, gates and sole binding owner population_rest_energy_witness stay unchanged. Global physical completion null, L4 false, production NOT_APPROVED, activation false. No completed science/test/CAS/plot/ACKed backup is rerun.

## ENDPOINT14 endpoint-zero sextic reference — 2026-10-28

Accepted local reference HE-EXP-ENDPOINT-14: 14 complete + 1 inherited partial + 3 physical open / 18; central 28/88, HE delta 0. Source cosmosapjw-quantum/BASS_HE at b3782bc3f778e4486c4874da826b497f4fa62e8e (tree 34f9b73d0261cfcd210cb0397ed7b4a446ce6a7a), branch research/he-endpoint14-20261028; initial and successful execution pin 501f4c5a5e5b14b0e05ff5d504578b5b9218caf7, tree 54bbaf71c917c67f3c5d3b9dcda44e3eecb740c4.

At 330 MeV, the full nonnegative even-sextic family with endpoint zero admits the fixed rational witness (1411/10000,-1/4,33/25) under the four nominal deterministic EXFOR ERR-S coordinate windows. The N16 full-family aperture ranges are HEMISPHERES [0.747050288674,0.783542448014] and CAPS [0.317079169073,0.404464291607], outward decimal displays; FULL is exactly 1. The same endpoint and data conditions had saved endpoint-zero QUARTIC12 EMPTY_OUTER. This establishes conditional model-degree/coefficient-cone sensitivity; it identifies no measured full angular or polarization law and no global physical no-go. The broad ranges describe model variation; the small extremum brackets describe certificate precision. Neither is a simultaneous experimental confidence interval.

The actual campaign used one construction, 8 PASS/0 FAIL controls, six complete enumerations, 26 vertex occurrences (14 inner,12 outer), 24690 active bases and four nesting controls. These are occurrence counts across cases, not a globally unique vertex count. Validation whole CPU2.020525s/wall1.944627875s; one CAS evaluator returned14 literal zero and16 True with remote resource values unavailable. One saved-only plot used whole CPU1.635101s/wall1.57173675s and science imports/calls0. Its minor legend overlap is documented; exact saved certificates and tables remain numerical authority. New science repairs used0, unused allowance1; predecessor reserve0 is unchanged.

R1-R10/C1-C10 workproducts20/20 and all ten source/ref/parent/tree readbacks and Drive/Dropbox terminal ACK/size checks are actual. S04 had two preserved Dropbox FETCH_FAILED transport responses before successful recovery; terminal success does not erase that history. There were no new scientific repair checkpoints. The new status status/HE_EXP_ENDPOINT14_20261028.json preserves each previous HE observation wrapper by its actual surface; prior T13 status remains unchanged. PRE_CAS false/null fields are creation-time snapshots; the external CENTRAL_PUBLICATION_RECEIPT and final delivery authorities record later actual ACK.

No physical source input was supplied. Event/inclusive normalization and liquid-He response projection; actual angular/polarization law and photon encounter history; named nonthermal deposition and global species binding remain open. Existing node status, lead repo, dependencies, budgets, gates and sole binding owner population_rest_energy_witness remain unchanged. Global physical completion is null, L4 false, production NOT_APPROVED and activation false. No completed science/test/CAS/plot or acknowledged backup is rerun.
