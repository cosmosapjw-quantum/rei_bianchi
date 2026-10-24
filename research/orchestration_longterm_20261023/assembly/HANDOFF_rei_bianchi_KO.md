# cosmosapjw-quantum/rei_bianchi 인수인계

중앙 경로: `cosmosapjw-quantum/rei_bianchi`, 브랜치 [research/orchestration-sandbox-20261022](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/orchestration-sandbox-20261022), `research/orchestration_longterm_20261023/`.

첫 행동: 동결 계약을 읽고 진행 중인 소유자 결과와 실제 잔여 예산을 확인한다. 완료 근거를 재사용하며 예산·실패 기록을 초기화하지 않는다. 이 문서는 새로운 과학적 판정을 추가하지 않는다.

현재 소스 핀·예약·자원 정책(원본 계약 기준):

```json
{
  "rei/CONTRACTS.json": {
    "schema_version": 1,
    "date_utc": "2026-10-23",
    "reservations": [
      {
        "id": "external:ANGTHERM02_OWNER_ADMISSION",
        "owner_branch": "research/rei-coupled-isotope-contract-20261022",
        "head": "1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c",
        "status": "ACTIVE_OWNER_PREPARED_REMOTE_LOCAL_PREFLIGHT",
        "allowed_action_here": "read-only reuse; no execution or repair",
        "new_cases_admitted_here": 0
      }
    ],
    "selected_current_unit": "external:X1_HE38_ANGULAR_PSD_REVIEW",
    "historical_budget_limits": {
      "ANGTHERM01": {
        "cpu": 224.778756,
        "cpu_cap": 300,
        "wall": 238.352717,
        "wall_cap": 420,
        "status": "completed; not transferable"
      },
      "D10": {
        "failed_initial_cpu": "UNKNOWN_NOT_ZERO",
        "aggregate60s": "NOT_ESTABLISHED"
      }
    },
    "publication": "Master contracts/handoffs only, not future-node implementation."
  }
}
```


## REI-L0

원본: `rei/CONTRACTS.json/nodes/0`. 내부 선행: 내부 없음. 외부 선행: `["external:ANGTHERM01@6daf382ee698835e7a141378c232d1d97c1c5cf1", "external:X1_HE38_ANGULAR_PSD_REVIEW"]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
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
}
```


## REI-L1

원본: `rei/CONTRACTS.json/nodes/1`. 내부 선행: REI-L0. 외부 선행: `["external:BASS_CR_C23B_PHYSICAL_SOURCE", "external:WU088_HH_SOURCE_MOMENTS", "external:REC_SELECTED_LINE_OR_COMPTON_PROVIDER"]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
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
  "id": "REI-L1",
  "dependencies": [
    "REI-L0",
    "external:BASS_CR_C23B_PHYSICAL_SOURCE",
    "external:WU088_HH_SOURCE_MOMENTS",
    "external:REC_SELECTED_LINE_OR_COMPTON_PROVIDER"
  ],
  "title": "One source-qualified gas/radiation provider pair",
  "status": "PARTIAL_DONORS_OPEN_BINDINGS",
  "owner": "REI adapter; BASS_CR/WU088_HH/REC physical providers",
  "scope": "Finite selected spectrum with explicit nonthermal/escape reservoirs and exclusive event owner",
  "allowed_paths": [
    "research/rei_source_pair_binding/**"
  ],
  "input_sources": [
    "ANGTHERM02 source assessment at1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c",
    "external:latest source receipts from thermal authority"
  ],
  "acceptance": [
    "source identity and domain pinned",
    "matched number/energy/STF measure",
    "unsupported stopping stays explicit nonthermal reservoir",
    "support zero distinct from missing rate",
    "Planck bath and actual monopole conventions distinct",
    "one native line/beta/PI owner",
    "donor physical uncertainty retained"
  ],
  "claim_limit": "Adopted finite provider and conditional heat model, not empirical full reionization",
  "budget": {
    "initial_probe_cpu_s_max": 30,
    "cumulative_cap": "NOT_FROZEN",
    "new_cosmological_ivps": 0
  },
  "pass_next": "REI-L4 isotropic zero-n/T variant",
  "failure_action": "Narrow explicit reservoir model or physical-source input dependency"
}
```


## REI-L2

원본: `rei/CONTRACTS.json/nodes/2`. 내부 선행: 내부 없음. 외부 선행: `["external:C3_ZERO_TINY_SOURCE", "external:LOCALFLOW@9620e1fcc4bdda76e0311206f614234926600381", "external:PHYSICAL_BETA_DAUGHTER_AND_STOPPING_PROVIDER"]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
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
  "id": "REI-L2",
  "dependencies": [
    "external:C3_ZERO_TINY_SOURCE",
    "external:LOCALFLOW@9620e1fcc4bdda76e0311206f614234926600381",
    "external:PHYSICAL_BETA_DAUGHTER_AND_STOPPING_PROVIDER"
  ],
  "title": "Nonzero n/T beta daughter and energy channels",
  "status": "OPEN_PHYSICAL_INPUTS",
  "owner": "REI event integration; physical daughter/stopping provider must be named before binding",
  "scope": "Branch-resolved beta with electron/neutrino/recoil and nonthermal accounting",
  "allowed_paths": [
    "research/rei_beta_resolved_energy/**"
  ],
  "input_sources": [
    "localflow scientific9620e1fcc4bdda76e0311206f614234926600381",
    "ANGTHERM02 B2 dependency"
  ],
  "acceptance": [
    "nonnegative branches sum1",
    "baryon and full charge bookkeeping",
    "energy sumQ in one mass-defect convention",
    "total Q not assigned to heat",
    "source domains and uncertainty explicit",
    "electron density updated once"
  ],
  "claim_limit": "Source-qualified local beta operator; cosmic evolution requires separate L4 extension",
  "budget": {
    "initial_probe_cpu_s_max": 30,
    "cumulative_cap": "NOT_FROZEN; no inherited new allowance",
    "new_cosmological_ivps": 0
  },
  "pass_next": "REI-L4 nonzero-beta variant",
  "failure_action": "INPUT_DEPENDENCY rather than no-go if source missing"
}
```


## REI-L3

원본: `rei/CONTRACTS.json/nodes/3`. 내부 선행: 내부 없음. 외부 선행: `["external:BASS_HE_FINITE_MASS_TRANSPORT", "external:X1_HE38_ANGULAR_PSD_REVIEW", "external:BASS_MASSIVE_COMPONENT_MAP"]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
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
  "id": "REI-L3",
  "dependencies": [
    "external:BASS_HE_FINITE_MASS_TRANSPORT",
    "external:X1_HE38_ANGULAR_PSD_REVIEW",
    "external:BASS_MASSIVE_COMPONENT_MAP"
  ],
  "title": "Baryonic material pressure with separate collisionless matter",
  "status": "CONDITIONAL_MOMENT_MODELS_PHYSICAL_TRANSPORT_OPEN",
  "owner": "BASS_HE physical baryon closure; REI assembly; BASS collisionless nonbaryonic component",
  "scope": "Optional anisotropic baryonic gas, not relabeling D10 massive stress",
  "allowed_paths": [
    "research/rei_baryon_pressure_binding/**"
  ],
  "input_sources": [
    "D10 scientific67205cb9a9fc3e36b959e584d3e06c74bdfbbf5e reused",
    "external:HE38 exact authority survey pins"
  ],
  "acceptance": [
    "pair total momentum/energy conservation",
    "pressure PSD necessary gate",
    "appropriate equilibrium and relaxation",
    "l2 transport cross section not event frequency",
    "signed stress sum and Frobenius norm",
    "kinetic closure/source validity separately admitted"
  ],
  "claim_limit": "Finite supported baryon moment model; X1 necessary cone is not full realizability or empirical transport",
  "budget": {
    "type": "small matrices/scalars only",
    "cumulative_cap": "inherit actual HE owner ledger; freeze before execution",
    "new_ivps": 0
  },
  "pass_next": "REI-L4 optional anisotropic-baryon variant",
  "failure_action": "Keep explicit isotropic pi_b=0 smaller model available"
}
```


## REI-L4

원본: `rei/CONTRACTS.json/nodes/4`. 내부 선행: REI-L0, REI-L1. 외부 선행: `["external:BASS_GEOMETRY_FEEDBACK", "external:VIGILODE_NUMERICAL_HOOKS"]`. 조건부 선행: `[{"condition": "nonzero_n_or_T", "dependency": "REI-L2", "external": false}, {"condition": "anisotropic_baryons", "dependency": "REI-L3", "external": false}, {"condition": "ANGTHERM02_accuracy_claim", "dependency": "external:ANGTHERM02_OWNER_ADMISSION", "external": true}]`.

원 저자 계약(변경 없음):

```json
{
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
  "id": "REI-L4",
  "dependencies": [
    "REI-L0",
    "REI-L1",
    "external:BASS_GEOMETRY_FEEDBACK",
    "external:VIGILODE_NUMERICAL_HOOKS"
  ],
  "conditional_dependencies": {
    "nonzero_n_or_T": [
      "REI-L2"
    ],
    "anisotropic_baryons": [
      "REI-L3"
    ],
    "ANGTHERM02_accuracy_claim": [
      "external:ANGTHERM02_OWNER_ADMISSION"
    ]
  },
  "title": "Finite closed selected gas+radiation+geometry pilot",
  "status": "WAITING_SELECTED_PHYSICAL_BINDINGS",
  "owner": "REI integration; provider physics retains owners",
  "scope": "One declared finite model with independent exchange/work ledgers and live Einstein feedback",
  "allowed_paths": [
    "research/rei_closed_selected_pilot/**"
  ],
  "input_sources": [
    "L0-L3 reviewed artifacts as applicable",
    "ANGTHERM01 reuse only; not donor replay"
  ],
  "acceptance": [
    "included sources qualified",
    "new gas/radiation actually drive H/shear and stress",
    "full/reference vs reduced agree at frozen state scales",
    "baryon/charge/energy positivity and domain gates",
    "discriminating refinement under same physics",
    "external feeds are either closed source reservoirs or explicitly open"
  ],
  "claim_limit": "Selected-model solution only, not astrophysical or general-Bianchi completion",
  "budget": {
    "cpu": "NOT_FROZEN",
    "wall": "NOT_FROZEN",
    "tolerances": "NOT_FROZEN after model selection; preserve prior leaf criteria",
    "ncp": "NOT_READY"
  },
  "pass_next": "REI-L5",
  "failure_action": "Classify physical/numerical/implementation failure; one scoped repair with preserved debit"
}
```


## REI-L5

원본: `rei/CONTRACTS.json/nodes/5`. 내부 선행: REI-L4. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
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
  "id": "REI-L5",
  "dependencies": [
    "REI-L4"
  ],
  "title": "Claim-specific physical and observable admission",
  "status": "TARGET_AND_BUDGET_NOT_FROZEN",
  "owner": "REI with geometry/physical provider owners",
  "scope": "One named observable and parameter/geometry domain",
  "allowed_paths": [
    "research/rei_observable_admission/**"
  ],
  "input_sources": [
    "L4 result and source/physical uncertainty map"
  ],
  "acceptance": [
    "explicit target and source/emissivity/IC",
    "channel completeness only for declared claim",
    "physical/model and numerical uncertainty separate",
    "angular-continuum evidence if claimed",
    "geometry scope explicit",
    "independent review at claimed scope"
  ],
  "claim_limit": "No global percentage, all-Bianchi claim or universal speedup from scoped finite tests",
  "budget": {
    "cpu": "NOT_FROZEN",
    "wall": "NOT_FROZEN",
    "ncp": "NOT_READY"
  },
  "pass_next": "one named observable admission",
  "failure_action": "Exact missing dependency and smallest next discriminating unit"
}
```


## 저장소 간 조건부 연결

채널을 선택할 때만 해당 공급자 조건을 적용한다. 모든 공급자의 동시 완료를 요구하지 않는다.


- `HE-X1` → `REI-L0`: using angular-moment injection. Necessary PSD/moment-cone gate only; does not supply angular distribution or physical cross section


- `HE-ANG` → `REI-L3`: selecting anisotropic baryonic scattering transport. Source-qualified angular moments needed; event frequency is not l2 transport


- `HE-EXCHANGE` → `REI-L3`: selecting finite-mass baryonic pressure exchange. Momentum/energy and pair symmetry from supported physical model


- `HE-CLOSURE` → `REI-L4`: selecting nonzero baryonic anisotropic stress. Isotropic pi_b=0 minimal pilot does not require this extension


- `CR_N4_STOPPING_KERNEL` → `REI-L1`: claiming thermalization of supplied fast photoelectrons. Without provider, energy remains explicitly nonthermal; no instant heat


- `CR_N6_CONSERVATIVE_COUPLING` → `REI-L4`: selecting CR coupled radiation/deposition pathway. Source and gas use same event measure and valid domain


- `WU_D_PI_RR_MATCHED` → `REI-L1`: claiming isotope-specific D PI/RR number and energy moments. Equal-electronic isotope approximation remains distinct smaller model


- `WU_NUCLEAR_PARTICLE_OWNERSHIP` → `REI-L2`: activating nuclear daughters/fast products. Branch normalization, charge and energy carriers explicit


- `CR_BETA_FULL_OWNER` → `REI-L2`: activating source-qualified beta partition and stopping. One beta owner; total Q not all heat


- `REC-LINE02` → `REI-L1`: selecting native line source. Consume completed owner result only; active owner reservation remains


- `REC-FIELD` → `REI-L1`: selecting actual spectral radiation/Compton exchange. Planck and actual-monopole baths remain distinct


- `B3-fourforce-owner` → `REI-L4`: selecting BASS four-force geometry feedback adapter. Closed sum of sectors in matching frame/clock; signed stresses retained


- `B2-G1B-curved` → `REI-L5`: claiming curved Bianchi smooth-source domain. Not a prerequisite to all LRS selected flat pilots


- `V1-affine-native` → `REI-L4`: using native reduced30/full33 affine adaptive client. Actual full physical norm and inherited scales; other validated solvers remain available


- `V2-session-fatal` → `REI-L4`: using switching/restart driver. Accepted-state transactional semantics and all costs preserved


- `V5-sphere-production` → `REI-L5`: claiming its physical spherical transport scheme. Joint number/energy remap and source-appropriate stability; not all selected-model pilots
