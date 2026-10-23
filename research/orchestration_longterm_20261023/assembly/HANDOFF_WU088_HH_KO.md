# WU088_HH 인수인계

중앙 경로: `cosmosapjw-quantum/rei_bianchi`, 브랜치 [research/orchestration-sandbox-20261022](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/orchestration-sandbox-20261022), `research/orchestration_longterm_20261023/`.

첫 행동: 동결 계약을 읽고 진행 중인 소유자 결과와 실제 잔여 예산을 확인한다. 완료 근거를 재사용하며 예산·실패 기록을 초기화하지 않는다. 이 문서는 새로운 과학적 판정을 추가하지 않는다.

현재 소스 핀·예약·자원 정책(원본 계약 기준):

```json
{
  "atomic/LONGTERM_CONTRACTS.json": {
    "schema": "ATOMIC_LONGTERM_CONTRACT_V1",
    "as_of": "2026-10-23",
    "scope": "survey and planning; no science executed",
    "pins": {
      "WU088_HH": "09289300ec2e500806aa2cb82365f00329e41c8c",
      "bass_cr": "aa57be95b7459eb397d9881b686d9c7bc4444755"
    },
    "selected_current_loop": "Root chose HE38 angular moment-cone; cutoff is future only",
    "coverage": {
      "WU_branches": 148,
      "CR_branches": 175,
      "pages_each": 3,
      "terminal_cursors": null,
      "PR_search": "updated>=2026-10-22 top100 returned6WU/2CR; connector exposes no total or cursor",
      "actual_file_reads": "selected latest contracts/reports/handoffs, root AGENTS; full branch contents not exhaustively read",
      "private_conversations": "UNAVAILABLE",
      "external_runtime": "UNOBSERVED",
      "backups": "C23B authority+terminal full text read; producer R3 reused, no archive redownload"
    }
  }
}
```


## WU_CE83_OWNER_COMPLETION

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/0`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "WU_CE83_OWNER_COMPLETION",
  "depends_on": [],
  "equations": [
    "W(eps)=(eps+Delta)*sigma_up(eps+Delta)",
    "eps*sigma_down=(g0/gi)*W",
    "dx/dt=a-(diag(c+A)+a*1^T)x",
    "Qth+DeltaUatom+Egamma=0"
  ],
  "domain": "H I LS1s/2s/2p finite native Delta10.20435eV,255<=T<=50000K, fixed ne/T, optically thin",
  "input": [
    "PR139 S0 09289300ec2e500806aa2cb82365f00329e41c8c CONTRACT; owner active"
  ],
  "output": [
    "owner-completed matched rates, populations, energy profiles"
  ],
  "admission_gate": "132rates+324steady+732transient rows and frozen contract independent gates; confirm current owner result first",
  "pr_boundary": "Do not duplicate PHYS83; ingest owner completion, then separate consumer PR"
}
```


## WU_LI_SOURCE_UNCERTAINTY

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/1`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "WU_LI_SOURCE_UNCERTAINTY",
  "depends_on": [],
  "equations": [
    "K(T)=sqrt(8/(pi*me))*(kBT)^(-3/2)*integral(E*sigma(E)*exp(-E/kBT)dE)",
    "sigma_model=sigma6*((E-I)/(6-I))^p*(6/E)^q"
  ],
  "domain": "Li7 I=5.39172060034581eV to6eV; measurement response and source tail separated",
  "input": [
    "PHYS82 ca9d53983459ea08f9992a8a24663e46b7180344 conditional families",
    "original experimental instrument response, isotope composition"
  ],
  "output": [
    "admissible source envelope or explicit source-limited conditional rates"
  ],
  "admission_gate": "unconvolved source uncertainty justified from data; family spread alone does not satisfy confidence gate",
  "pr_boundary": "Source analysis PR distinct from coupled trajectory PR"
}
```


## WU_HE_LI_CX_STATE_ENERGY

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/2`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "WU_HE_LI_CX_STATE_ENERGY",
  "depends_on": [],
  "equations": [
    "DeltaEevent=sum(Ebinding_products)-sum(Ebinding_reactants)",
    "Qthermal+Qphoton+Qrecoil+DeltaEevent=0",
    "dn/dt=S*r"
  ],
  "domain": "state-resolved He/Li CX with explicit projectile/target charge, excited branches, collision energies",
  "input": [
    "primary channel cross sections",
    "branch probabilities, thresholds, photon/recoil owner"
  ],
  "output": [
    "positive incidence columns; level-resolved rates and thermal/photon source"
  ],
  "admission_gate": "nuclei and charge exact per event, all included branch energy closure, domain coverage table",
  "pr_boundary": "One source/branching PR; separate thermal consumer activation"
}
```


## WU_D_PI_RR_MATCHED

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/3`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "WU_D_PI_RR_MATCHED",
  "depends_on": [],
  "equations": [
    "R_PI=int(4*pi*Jnu*sigma_nu/(h*nu)dnu)",
    "H_PI=int(4*pi*Jnu*sigma_nu*(h*nu-I)/(h*nu)dnu)",
    "dT/dt=2*Q/(3*kB*Nthermal)-T*dNthermal/dt/Nthermal"
  ],
  "domain": "D source-qualified PI and Case-A RR using same isotope gap and radiation history",
  "input": [
    "PR135 existing event-energy adapter",
    "D threshold/cross section/RR capture moments"
  ],
  "output": [
    "source-matched event rates and kinetic/binding/photon moments"
  ],
  "admission_gate": "same event count in electron source and binding ledger; Milne relation under stated degeneracies/frame; dimensional guard",
  "pr_boundary": "Preserve event adapter; add source-moment supplier PR then consumer PR"
}
```


## WU_NUCLEAR_PARTICLE_OWNERSHIP

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/4`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "WU_NUCLEAR_PARTICLE_OWNERSHIP",
  "depends_on": [],
  "equations": [
    "Nth=Nnuc,thermal+Ne,thermal",
    "dUtotal=dUth+dUnt+dUbind+dUrad+dUescape+work=0",
    "<rate*Eproduct> differs from <rate>*<Eproduct> unless justified"
  ],
  "domain": "thermal finite-T reactants, explicitly tracked fast products and normal-frame photons",
  "input": [
    "PHYS81 b3ec271a96cb67e583bffa9b61533802838236f9 photon/recoil kinematics",
    "C23B boost and clock pins",
    "HE source moment contracts"
  ],
  "output": [
    "particle transfer incidence and event-weighted thermal/photon/recoil moments"
  ],
  "admission_gate": "every product has unique thermal/fast owner; thresholds and recoil kinematics consistent; no rate activation without source",
  "pr_boundary": "Theory and source-ownership PR before stopping/rate implementation"
}
```


## WU_SPECTRAL_GEOMETRY_COUPLING

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/WU088_HH/5`. 내부 선행: WU_CE83_OWNER_COMPLETION, WU_HE_LI_CX_STATE_ENERGY, WU_D_PI_RR_MATCHED, WU_NUCLEAR_PARTICLE_OWNERSHIP. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "WU_SPECTRAL_GEOMETRY_COUPLING",
  "depends_on": [
    "WU_CE83_OWNER_COMPLETION",
    "WU_HE_LI_CX_STATE_ENERGY",
    "WU_D_PI_RR_MATCHED",
    "WU_NUCLEAR_PARTICLE_OWNERSHIP"
  ],
  "equations": [
    "n_dot=S*r",
    "Utotal_dot+expansion_work+shear_work=external_supply-escape",
    "pi_total=sum signed same-frame tensors before norm"
  ],
  "domain": "non-tilted LRS; isotropic reacting gas, separate collisionless dark matter; recombination-to-z20 initial charge pinned",
  "input": [
    "closed rate/domain/owner contracts",
    "REC initial charge/line suppliers",
    "Li inner-shell/Auger branching"
  ],
  "output": [
    "conservative consumer prototype and distinct small new input validation"
  ],
  "admission_gate": "photon reabsorption/escape and initial-charge consistency closed; global/production adoption remains separate",
  "pr_boundary": "Consumer PR only after dependency delivery; HH_R10 stays OFF until original HH gates independently met"
}
```


## 저장소 간 조건부 연결

채널을 선택할 때만 해당 공급자 조건을 적용한다. 모든 공급자의 동시 완료를 요구하지 않는다.


- `WU_D_PI_RR_MATCHED` → `REI-L1`: claiming isotope-specific D PI/RR number and energy moments. Equal-electronic isotope approximation remains distinct smaller model


- `WU_NUCLEAR_PARTICLE_OWNERSHIP` → `REI-L2`: activating nuclear daughters/fast products. Branch normalization, charge and energy carriers explicit


- `REC-LINE02` → `WU_SPECTRAL_GEOMETRY_COUPLING`: selecting native line in WU spectral coupling. One native line owner; no detached/native double counting
