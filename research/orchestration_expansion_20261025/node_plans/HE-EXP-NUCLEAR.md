# HE-EXP-NUCLEAR

Lead: cosmosapjw-quantum/WU088_HH

Current status: `SOURCE_INPUT_PENDING`

Source: `authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/tasks/5`

```json
{
  "id": "HE-EXP-NUCLEAR",
  "lead_repo": "cosmosapjw-quantum/WU088_HH",
  "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/tasks/5",
  "contract": {
    "id": "HE-EXP-NUCLEAR",
    "status": "SOURCE_INPUT_PENDING",
    "depends_on": [
      "HE-EXP-SPECIES"
    ],
    "provider_domain": "n/Tdecay,source-selected nuclearfragment/Be7 daughter channels",
    "equations": "Nuclear massQ partitions neutrino,photons,atomicbinding,chargedparticles",
    "physical_ownership": "WU species/elementary channels and branching; REC level populations/spectra/history; HE differential collisions/thermalization; CR external nonthermal distribution/cascade/stopping; BASS geometry/background; REI selected scenario/assembly; this task lead=cosmosapjw-quantum/WU088_HH",
    "prerequisites": "Daughter distribution,charge/state,massQ/lepton and sourcevalidity",
    "claim_gate": "No nuclearQ reused as heat;neutrino escape tracked; beta branching sourced",
    "pass_next": "One daughter packet toHE-RESERVOIR",
    "budget": "No nuclear simulation budget assigned",
    "tests": "Only affected source/state/measure/units/conservation/tangent checks; original numerical tolerance retained; no unchangedsuite replay",
    "fail_action": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
    "uncertainty": "Provider/model/interpolation/quadrature/floating error separate; null until actual evidence",
    "units": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
    "lead_repo": "cosmosapjw-quantum/WU088_HH",
    "consumer_repo": "cosmosapjw-quantum/BASS_HE",
    "outputs": [
      "source-qualified result within stated domain",
      "explicit unresolved provider/model uncertainty",
      "consumer-facing event/state contract",
      "unchanged historical evidence with additive status observation"
    ],
    "conditional_dependencies": [],
    "independent_review": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
    "resource_allowance": {
      "cpu_s": null,
      "wall_s": null,
      "memory_bytes": null,
      "status": "UNALLOCATED_BY_THIS_PROSPECTIVE_PLAN",
      "reset_or_borrow_historical": false
    },
    "input_dependencies": [
      {
        "kind": "source_input",
        "lead_repo": "cosmosapjw-quantum/WU088_HH",
        "required": "selected nuclear/weak channel, isotope/isomer and daughter identities, masses/Q, charge/level branching, lepton and recoil source payload",
        "status": "SOURCE_INPUT_PENDING"
      }
    ],
    "consumer_bindings": [
      {
        "consumer": "HE-EXP-STOPPING",
        "predicate": "selected_nonthermal_stopping_model_contains_this_nuclear_daughter_source",
        "direction": "source_payload_to_stopping_consumer",
        "blocks_source_production": false
      }
    ],
    "readiness_rule": "Produce the WU-led nuclear source from catalog/mass/branch/source evidence; downstream stopping completion is not a prerequisite."
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "HE-EXP-SPECIES",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "depends_on"
    }
  ],
  "conditional_dependencies": [],
  "external_prerequisites": [
    {
      "type": "external",
      "source_reference": "Daughter distribution,charge/state,massQ/lepton and sourcevalidity",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "prerequisites"
    }
  ],
  "current_status": "SOURCE_INPUT_PENDING",
  "claim_gate": "No nuclearQ reused as heat;neutrino escape tracked; beta branching sourced",
  "pass_next_action": "One daughter packet toHE-RESERVOIR",
  "budget_status": "No nuclear simulation budget assigned",
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
      "value": "Daughter distribution,charge/state,massQ/lepton and sourcevalidity",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/prerequisites",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": "Nuclear massQ partitions neutrino,photons,atomicbinding,chargedparticles",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": "SI at interrepo boundary; source-native eV/a.u. converted explicitly with hbar,k_B,c retained",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "n/Tdecay,source-selected nuclearfragment/Be7 daughter channels",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/provider_domain",
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
      "json_pointer": "/tasks/5/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": "No nuclearQ reused as heat;neutrino escape tracked; beta branching sourced",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/claim_gate",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Preserve original failure, classify affected dependency, one authorized targeted repair; stop on exhausted own allowance",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/fail_action",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh authority reviews only changed source/equation/implementation and actual raw outcome; no admission from structural validation; one targeted repair and finite stopping rule",
      "source_file": "authority/thermal/BASS_HE/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/tasks/5/independent_review",
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
  }
}
```


## Preserved historical observation context

The following narrative is historical local/unpublished observation context, not a replacement for the latest base contract above. DRIFT02 historical file: `status/HE_EXP_FINITE_DRIFT_20261027.json` (no observation for this node).


## HE-EXP-PHOTON-05 observation

HE consumer-side conditional finite-recoil contribution for EXFOR M0475002 native12 coordinates with NIST2022 bare nuclear masses. This does not promote WU-led source/channel/branch/normalization admission: WU lead, SOURCE_INPUT_PENDING status, original budget and all contract gates remain unchanged. No nuclear Q is assigned to heat. Source remains local/unpublished; no physical promotion. See `status/HE_EXP_PHOTON05_20261027.json#/observations/HE-EXP-NUCLEAR`.


## Current local observation pointer

See `status/HE_EXP_ANGULAR06_20261027.json#/observations/HE-EXP-NUCLEAR`. Central publication has not occurred. Current scoped state, budget, lead and dependency gates remain unchanged.


## HE-EXP-APERTURE-07 prepared observation (C9 accepted; actual S09/P09 and S10/P10 identities)

Root accepted the HE consumer-side conditional aperture bounds and pair-coincidence reference under its explicit continuous-measure and fixed-parameter domain. The demonstrated native density is manufactured symmetric Bernstein data, not empirical DCS. WU source/channel/branch ownership and SOURCE_INPUT_PENDING, original experimental normalization, liquid-He projection, complete angular law with actual photon flux, and named deposition consumer remain open.

See `status/HE_EXP_APERTURE07_20261027.json#/observations/HE-EXP-NUCLEAR`. S09/P09 science identity is actual; S10/P10 delivery identity is actual in the status record. Current physical status, budget, lead, dependencies and claim gates remain unchanged.


## KINEMATIC08 scoped observation — 2026-10-28

HE consumer-side stationary bare-alpha gamma+alpha->d+d conditional kinematic reference accepted. Manufactured Bernstein examples do not supply empirical DCS, actual photon history or the WU-owned nuclear channel/species/branch source. SOURCE_INPUT_PENDING and ownership remain unchanged.

ROOT decision: `ACCEPT_SCOPED_PHYSICAL_INPUT_REFERENCE_WITH_WORKFLOW_PARTIAL`. Local DAG: 8 complete + 1 partial + 3 physical open /12; central 28/88, HE delta 0. Validation 14/14 PASS, scientific suite 1. Saved-only plot 1, scientific calls 0; CPU 7.040661/6 s FAIL. Workflow PARTIAL; no all-checks PASS, physical activation, new budget or rerun. Existing owner, dependencies, status, claim gates and budget remain unchanged.

Observation: `status/HE_EXP_KINEMATIC08_20261028.json#/observations/HE-EXP-NUCLEAR`; actual source and dual backup identities: `status/HE_EXP_KINEMATIC08_20261028.json#/final_identities`. Central publication flags in that file are a `PRE_CAS_CANDIDATE_SNAPSHOT`; the actual post-CAS external receipt is authoritative.


## AZIMUTH09 scoped observation — 2026-10-28

Stationary bare-alpha gamma+alpha->d+d finite-azimuth conditional reference accepted. Empirical DCS, actual photon encounter history and the WU-owned nuclear channel/species/branch source remain pending; SOURCE_INPUT_PENDING and ownership remain unchanged.

ROOT decision: `ACCEPT_SCOPED_FINITE_AZIMUTH_REFERENCE`. Local DAG: 9 complete + 1 partial + 3 physical open /13; central 28/88, HE delta0. One validation22/22 PASS; one Wolfram call109/109 literal zeros plus2 true comparisons, remote CPU unknown/null. One saved-data plot PASS CPU2.053974/8 s; scientific imports/calls0. Workflow COMPLETE_SCOPED only for this reference. KINEMATIC08 plot7.040661/6 s FAIL, PARTIAL and reserve0 remain unchanged. Existing current status, owner, dependencies, budgets and physical gates remain unchanged; no new execution or physical activation.

Observation: `status/HE_EXP_AZIMUTH09_20261028.json#/observations/HE-EXP-NUCLEAR`; actual source/dual-backup identities: `status/HE_EXP_AZIMUTH09_20261028.json#/final_identities`. Central publication flags are a PRE_CAS_CANDIDATE_SNAPSHOT; later actual post-CAS external receipt is authoritative.


## HARMONIC10 scoped observation — 2026-10-28

Fixed stored-mass stationary bare-alpha gamma+alpha->d+d second-harmonic reference accepted within explicit cone and geometry scope. Empirical DCS, actual polarization/encounter history and WU-owned nuclear species/channel/branch payload remain pending; ownership and SOURCE_INPUT_PENDING unchanged.

ROOT decision: `ACCEPT_SCOPED_SECOND_HARMONIC_REFERENCE`. Local DAG: 10 complete + 1 inherited partial + 3 physical open /14; central 28/88, HE delta0. Actual validation: 25 unique methods, 26 evaluations; initial full suite 24 PASS + 1 FAIL, followed by one targeted test20 PASS. Initial failure and original empty control remain preserved; production code unchanged, no full-suite rerun, repair reserve0. One Wolfram call returned117 literal-zero residuals and14 True checks with2 precision warnings; attained130-digit precision is not certified, remote CPU/wall null. Saved-only plot PASS CPU2.806525/10 s and wall2.835772674/30 s, one attempt, scientific imports/calls0; original footer clipping remains qualified. Recorded independent pass1: theory12/12, static15/15, actual13 unqualified PASS +1 precision-qualified/14; two findings closed, blockers0.

Actual S09 science publication: `39dc63b4bf4d60b255ea3ca5323661ccc80ca880`, tree `10ab6a622a4e0101cfffefdef93a8156bfe35c32`. Actual S10 delivery publication: `a73773a9e1056bf18405453a0e88b9d12a15e9ac`, tree `4e308ea37c6907f6b0064951e71d14667831a6a3`; both source and dual backups ACKed. Both validation execution pins and the plot execution pin are retained at `status/HE_EXP_HARMONIC10_20261028.json#/final_identities/execution_sources`.

Three physical inputs remain open; single rest/binding owner population_rest_energy_witness, null thermal quantities, birth_pool UNASSIGNED, global completion null, L4 false, production NOT_APPROVED, activation false. Existing statuses, owners, dependencies, gates, budgets,17 integration edges and prior outcomes remain unchanged. Observation: `status/HE_EXP_HARMONIC10_20261028.json#/observations/HE-EXP-NUCLEAR`; prior observations are preserved by actual source surface in that document. Central publication flags remain a PRE_CAS_CANDIDATE_SNAPSHOT; actual central publication is pending external ACK/readback.


## EXFOR11 data-conditioned aperture reference — 2026-10-28

- Scoped decision: ACCEPT_SCOPED_DATA_CONDITIONED_APERTURE_REFERENCE.
- Source: cosmosapjw-quantum/BASS_HE@1e393c7901d08aaf97c4c3568ef4ab120d43e9c5; tree 7c33ed3f6a9b88402ff9c0ebe7b45840202b7fef.
- Unit: research/program_expansion_20261025/continuation_exfor_20261028/.
- Central observation: status/HE_EXP_EXFOR11_20261028.json#/observations/HE-EXP-NUCLEAR.
- Consumer-side use of12 official DCS rows at213/258/330MeV. Six total-cross-section rows on a disjoint energy grid are kept separate. Degree4/8, endpoint choices, ERR-S coordinate sensitivity windows and uniform azimuth are declared assumptions. Three outer-empty finite families at330MeV are retained; no global no-go.
- Local11 complete +1 inherited partial +3 physical open /15; Central28/88, HE delta0.
- Existing current_status, lead, budgets, dependencies and gates are unchanged. All3 physical inputs remain open; global_physical_completion=null, L4_ready=false, production=NOT_APPROVED, activation=false.
- Validation6PASS/0FAIL in1 new campaign,12cases/274 exact certificate vertices; Wolfram21zero/8True;1saved-only plotPASS. Complete source/Drive/Dropbox stageACKs are bound in the observation record. Historical HARMONIC10 initial24PASS+1FAIL/targeted1PASS/reserve0 and earlier partial workflows remain preserved.
- This paragraph and in-Git observation are creation-time PRE_CAS snapshots. Actual central publication is established by the external POSTPUBLICATION CENTRAL_PUBLICATION_RECEIPT, not a predicted future commit.


## QUARTIC12 scoped reference return — 2026-10-28

Actual HE source 4c71acfa2b8721a0d0b8f9cec8814f75f1c55739; exact tree 08e11c808d86cdf2a00ceb9feb3de43fc1bf3089.
Decision ACCEPT_SCOPED_FULL_POSITIVE_QUARTIC_REFERENCE. Local12complete+1inheritedpartial+3physicalopen/16; central28/88,HEdelta0.
One primary7PASS0FAIL,12cases,132vertices; Wolfram16zero12True; one saved-onlyplotPASS; nonauthorfinalsciencePASS.
Fullpositive free330MeV witness lies outside old sufficient cone; endpointzero330 remains an exact scoped empty outer polytope;258 minimum finitegap retained.
Current status SOURCE_INPUT_PENDING and lead ownership remain unchanged. No new normalized physical source, flux, projection, deposition, globalbinding or productionapproval is supplied.
Detailed observation: status/HE_EXP_QUARTIC12_20261028.json. In-Git PRE_CAS fields reflect creationtime; actual publication receipt is external POSTPUBLICATION_EXTERNAL_DELIVERY.
