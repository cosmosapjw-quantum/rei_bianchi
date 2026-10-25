# REI-EXP-OPACITY-CONSUMER

Lead: cosmosapjw-quantum/rei_bianchi

Current status: `LIBRARY_SCOPED_PROVIDER_OBSERVED_ACTUAL_CONSUMER_BINDING_PENDING`

Source: `authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json#/nodes/2`

```json
{
  "id": "REI-EXP-OPACITY-CONSUMER",
  "lead_repo": "cosmosapjw-quantum/rei_bianchi",
  "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
  "json_pointer": "/nodes/2",
  "contract": {
    "id": "REI-EXP-OPACITY-CONSUMER",
    "title": "Optional GRID044 observer-frame opacity residual and local Jacobian consumer",
    "lead_repo": "rei_bianchi",
    "consumers": [
      "rei_bianchi"
    ],
    "change_class": [
      "scope_expansion",
      "dependency_change"
    ],
    "current_status": "LIBRARY_SCOPED_PROVIDER_OBSERVED_ACTUAL_CONSUMER_BINDING_PENDING",
    "dependencies": [
      "REI-EXP-SCENARIO"
    ],
    "conditional_dependencies": [
      {
        "condition": "scenario does notmatch GRID044providerdomain",
        "dependency": "external:qualified_replacement_opacity_provider_required"
      },
      {
        "condition": "full coupled thermal or photon tangent claimed",
        "dependency": "external:provider_state_history_thermal_and_radiative_Jacobians"
      }
    ],
    "inputs": [
      "Libraryreportlibfile_53326da92a14819195233da5fbfea464 and actualreceiptlibfile_15074de9d37c8191afe844ce33215a32;18/18reportedPASS_SCOPED",
      "Finalarchive libfile_11624a776d6481918c3dfc0c92b51d72 SHA b12cc903a9d1d813416b2b77c2f7a8c74c1b657c5c85cf5a683e5e5c64001d9f;originalrawonlyafterretrievedidentitychecked",
      "ANGTHERM01 provider d870ce943005bf93e332ca32ca8c945798b1331c;actual grid044 observer/source support,z2,nHref5.151254745827818m^-3",
      "Two sources(stellar,externalIGM),six electronicchannels(HI,HeI,HeII,LiIvalence,LiII,LiIII),21targetstates and25x23target/source-templateJacobian",
      "Actual chosen consumerstate,observerandnormalization; no physicaln/T abundance inferredfromsyntheticfixture"
    ],
    "equations": [
      "Gamma=c*nHref*integral sigma(E)dM",
      "P=c*nHref*integral E*sigma(E)dM",
      "K=c*nHref*integral (E-chi)*sigma(E)dM;P=chi*Gamma+K",
      "targeteventrate=x_target*Gamma; energycolumns=(-P,+chi*Gamma,+K) with multipliedtargetnormalization",
      "Local25x23Jacobian maps target/source-template perturbations only; full photon/thermal/geometry derivatives require separateproviders"
    ],
    "units": {
      "abundance": "x_s=n_s/n_ref,dimensionless; default n_ref is a fixed-comoving bookkeeping reference, not evolving actual H/isotope/baryon density",
      "time": "proper second; coordinate conversion explicit",
      "cross_section": "m^2",
      "rate_one_body": "s^-1",
      "rate_two_body": "m^3 s^-1",
      "event_source": "events per reference nucleus per proper second",
      "energy": "source native eV with exact1eV=1.602176634e-19J;SIboundaryJ m^-3 s^-1",
      "density": "m^-3",
      "stress": "J m^-3, full signed tensor sum before Frobenius norm",
      "metric": "(-,+,+,+)",
      "constants": "c,hbar,kB retained"
    },
    "domain": "Optional only if selectedscenario matches originalnormalobserver,grid044,z2,valencefit,sourcehistory/support and fixed derivativevariables; otherwise hold/requalify",
    "outputs": [
      "GRID044_PROVIDER_OBSERVATION.json with Libraryonlypublication and rawintakestatus",
      "ACTUAL_STATE_BINDING.json with targets/units/observer/source identity",
      "Optional finite residual/JVP adapter and uncertainty/derivative coverage map"
    ],
    "acceptance": [
      "No replay of opacityintegrals merelyto moveenvironment",
      "Providerfit64.39eVLiI branch boundary notfalse cutoff",
      "Same photons/Href measure,observer and normalization",
      "Labelmap retainsLi6/Li7order and declaredisotopeequalrateapproximation",
      "Photon/internal/primaryelectronenergyassignedonce",
      "LocalJwidth25x23 preserved and omitted derivatives remainOPEN",
      "Originalreportedgates reused at theirdomain;newbindingchecks frozen separately",
      "N6HOLD/mainNO_MORE_IVPs and physicaln/Tsource gaps preserved",
      "Reference policy fixed-comoving versus evolving-physical explicitly bound; external injection and any S_ref correction retained in source/Jacobian"
    ],
    "claim_gate": "Source-qualified selected scenario only; exact conservation does not establish physical rate correctness; globalphysicalcompletionnull",
    "failure_disposition": "Retain originalraw;classifyphysical/input/numerical/implementation/environment;missinginputsUNQUALIFIED;one targetedrepair afterauthoritydecision;do not borrowoldbudget",
    "independent_review": "Fresh scientific authority reads actual source,units,modelselection,diff,raw and plots at claimed scope;not implementer",
    "pass_next_action": "Provide one actualstate-qualified sourceblock to REI-EXP-EVENT-CONSUMER or existingL1; fullcoupledJacobian remains explicit nextinput",
    "budget_status": {
      "CPU_s": null,
      "wall_s": null,
      "memory_MiB": null,
      "new_numeric_authorization": false,
      "reason": "Future separateunit requiresfrozen measured allowance;no historicalbudgettransfer"
    },
    "pr_plan": {
      "kind": "additive draft PR",
      "allowed_paths": [
        "research/rei_grid044_opacity_consumer/**"
      ],
      "base_policy": "fresh current owner branch inspected immediately before additive publication;expectedSHA forcefalse",
      "preserve": [
        "original40contracts17edges7authorities",
        "originalsource/raw/failures",
        "completed83cohort",
        "ANGTHERM02read-only",
        "allownerlineages"
      ],
      "review_scope": "new chosen provider-to-consumer binding and changeddependencies only",
      "publication_does_not_authorize_run": true
    },
    "source_budget_preserved": {
      "mainCPU_s": 595.225063,
      "maincapCPU_s": 600,
      "mainstatus": "NO_MORE_IVPs",
      "continuationCPU_s": 8.001104,
      "continuationcapCPU_s": 10,
      "continuationwall_s": 8.029615335,
      "continuationwallcap_s": 20,
      "remaining_allowance_authorizes_further_evaluation": false,
      "externalGitpublication": false,
      "wholeZIPreadback_by_this_task": false
    },
    "reference_normalization_policy": {
      "default": "N_ref is a fixed bookkeeping count in a comoving volume; n_ref(t)=n_ref0*a(t)^(-3). It is not the evolving actual hydrogen/isotope/baryon count when injection or transmutation occurs.",
      "source_equation": "For physical species density dot(n_s)+3H*n_s=S_s, x_s=n_s/n_ref gives dot(x_s)=S_s/n_ref under the default fixed comoving reference. External injection belongs to S_s and is not absorbed into the reference.",
      "changing_physical_reference": "If a scenario explicitly selects an evolving physical reference, use dot(x_s)=dot(n_s)/n_ref-x_s*dot(n_ref)/n_ref. With dot(n_ref)+3H*n_ref=S_ref this becomes dot(x_s)=(S_s-x_s*S_ref)/n_ref; bind S_ref and its derivative explicitly.",
      "reference_identity": "Record n_ref0,scale-factor normalization,comoving volume convention and selected reference policy in SCENARIO and all consumer bindings."
    }
  },
  "dependencies": [
    {
      "type": "internal",
      "id": "REI-EXP-SCENARIO",
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "dependencies"
    }
  ],
  "conditional_dependencies": [
    {
      "condition": "scenario does notmatch GRID044providerdomain",
      "dependency": "external:qualified_replacement_opacity_provider_required",
      "type": "external",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    },
    {
      "condition": "full coupled thermal or photon tangent claimed",
      "dependency": "external:provider_state_history_thermal_and_radiative_Jacobians",
      "type": "external",
      "qualification": "SOURCE_DECLARED_EXTERNAL_REFERENCE; PROVIDER_STATUS_NOT_INFERRED",
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "source_field": "conditional_dependencies"
    }
  ],
  "external_prerequisites": [],
  "current_status": "LIBRARY_SCOPED_PROVIDER_OBSERVED_ACTUAL_CONSUMER_BINDING_PENDING",
  "claim_gate": "Source-qualified selected scenario only; exact conservation does not establish physical rate correctness; globalphysicalcompletionnull",
  "pass_next_action": "Provide one actualstate-qualified sourceblock to REI-EXP-EVENT-CONSUMER or existingL1; fullcoupledJacobian remains explicit nextinput",
  "budget_status": {
    "CPU_s": null,
    "wall_s": null,
    "memory_MiB": null,
    "new_numeric_authorization": false,
    "reason": "Future separateunit requiresfrozen measured allowance;no historicalbudgettransfer"
  },
  "change_class": [
    "scope_expansion",
    "dependency_change"
  ],
  "historical_contract_id": null,
  "source_fields": {
    "lead_repo": "lead_repo",
    "current_status": "current_status",
    "claim_gate": "claim_gate",
    "pass_next_action": "pass_next_action",
    "budget_status": "budget_status"
  },
  "pr_plan": {
    "inputs": {
      "value": [
        "Libraryreportlibfile_53326da92a14819195233da5fbfea464 and actualreceiptlibfile_15074de9d37c8191afe844ce33215a32;18/18reportedPASS_SCOPED",
        "Finalarchive libfile_11624a776d6481918c3dfc0c92b51d72 SHA b12cc903a9d1d813416b2b77c2f7a8c74c1b657c5c85cf5a683e5e5c64001d9f;originalrawonlyafterretrievedidentitychecked",
        "ANGTHERM01 provider d870ce943005bf93e332ca32ca8c945798b1331c;actual grid044 observer/source support,z2,nHref5.151254745827818m^-3",
        "Two sources(stellar,externalIGM),six electronicchannels(HI,HeI,HeII,LiIvalence,LiII,LiIII),21targetstates and25x23target/source-templateJacobian",
        "Actual chosen consumerstate,observerandnormalization; no physicaln/T abundance inferredfromsyntheticfixture"
      ],
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/inputs",
      "qualification": "SOURCE_DECLARED"
    },
    "equations": {
      "value": [
        "Gamma=c*nHref*integral sigma(E)dM",
        "P=c*nHref*integral E*sigma(E)dM",
        "K=c*nHref*integral (E-chi)*sigma(E)dM;P=chi*Gamma+K",
        "targeteventrate=x_target*Gamma; energycolumns=(-P,+chi*Gamma,+K) with multipliedtargetnormalization",
        "Local25x23Jacobian maps target/source-template perturbations only; full photon/thermal/geometry derivatives require separateproviders"
      ],
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/equations",
      "qualification": "SOURCE_DECLARED"
    },
    "units": {
      "value": {
        "abundance": "x_s=n_s/n_ref,dimensionless; default n_ref is a fixed-comoving bookkeeping reference, not evolving actual H/isotope/baryon density",
        "time": "proper second; coordinate conversion explicit",
        "cross_section": "m^2",
        "rate_one_body": "s^-1",
        "rate_two_body": "m^3 s^-1",
        "event_source": "events per reference nucleus per proper second",
        "energy": "source native eV with exact1eV=1.602176634e-19J;SIboundaryJ m^-3 s^-1",
        "density": "m^-3",
        "stress": "J m^-3, full signed tensor sum before Frobenius norm",
        "metric": "(-,+,+,+)",
        "constants": "c,hbar,kB retained"
      },
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/units",
      "qualification": "SOURCE_DECLARED"
    },
    "domain": {
      "value": "Optional only if selectedscenario matches originalnormalobserver,grid044,z2,valencefit,sourcehistory/support and fixed derivativevariables; otherwise hold/requalify",
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/domain",
      "qualification": "SOURCE_DECLARED"
    },
    "outputs": {
      "value": [
        "GRID044_PROVIDER_OBSERVATION.json with Libraryonlypublication and rawintakestatus",
        "ACTUAL_STATE_BINDING.json with targets/units/observer/source identity",
        "Optional finite residual/JVP adapter and uncertainty/derivative coverage map"
      ],
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/outputs",
      "qualification": "SOURCE_DECLARED"
    },
    "positive_acceptance": {
      "value": [
        "No replay of opacityintegrals merelyto moveenvironment",
        "Providerfit64.39eVLiI branch boundary notfalse cutoff",
        "Same photons/Href measure,observer and normalization",
        "Labelmap retainsLi6/Li7order and declaredisotopeequalrateapproximation",
        "Photon/internal/primaryelectronenergyassignedonce",
        "LocalJwidth25x23 preserved and omitted derivatives remainOPEN",
        "Originalreportedgates reused at theirdomain;newbindingchecks frozen separately",
        "N6HOLD/mainNO_MORE_IVPs and physicaln/Tsource gaps preserved",
        "Reference policy fixed-comoving versus evolving-physical explicitly bound; external injection and any S_ref correction retained in source/Jacobian"
      ],
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/acceptance",
      "qualification": "SOURCE_DECLARED"
    },
    "failure_disposition": {
      "value": "Retain originalraw;classifyphysical/input/numerical/implementation/environment;missinginputsUNQUALIFIED;one targetedrepair afterauthoritydecision;do not borrowoldbudget",
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/failure_disposition",
      "qualification": "SOURCE_DECLARED"
    },
    "independent_review": {
      "value": "Fresh scientific authority reads actual source,units,modelselection,diff,raw and plots at claimed scope;not implementer",
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/independent_review",
      "qualification": "SOURCE_DECLARED"
    },
    "PR_boundary": {
      "value": {
        "kind": "additive draft PR",
        "allowed_paths": [
          "research/rei_grid044_opacity_consumer/**"
        ],
        "base_policy": "fresh current owner branch inspected immediately before additive publication;expectedSHA forcefalse",
        "preserve": [
          "original40contracts17edges7authorities",
          "originalsource/raw/failures",
          "completed83cohort",
          "ANGTHERM02read-only",
          "allownerlineages"
        ],
        "review_scope": "new chosen provider-to-consumer binding and changeddependencies only",
        "publication_does_not_authorize_run": true
      },
      "source_file": "authority/rei/rei_bianchi/research/program_expansion_20261025/TASK_ASSIGNMENT.json",
      "json_pointer": "/nodes/2/pr_plan",
      "qualification": "SOURCE_DECLARED"
    }
  }
}
```
