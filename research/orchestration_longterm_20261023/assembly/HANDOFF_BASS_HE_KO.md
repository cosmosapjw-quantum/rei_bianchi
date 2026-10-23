# cosmosapjw-quantum/BASS_HE 인수인계

중앙 경로: `cosmosapjw-quantum/rei_bianchi`, 브랜치 [research/orchestration-sandbox-20261022](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/orchestration-sandbox-20261022), `research/orchestration_longterm_20261023/`.

첫 행동: 동결 계약을 읽고 진행 중인 소유자 결과와 실제 잔여 예산을 확인한다. 완료 근거를 재사용하며 예산·실패 기록을 초기화하지 않는다. 이 문서는 새로운 과학적 판정을 추가하지 않는다.

현재 소스 핀·예약·자원 정책(원본 계약 기준):

```json
{
  "thermal/BASS_HE_LONGTERM_CONTRACTS.json": {
    "schema": "longterm_pr_contracts.v1",
    "as_of": "2026-10-23",
    "repository": "cosmosapjw-quantum/BASS_HE",
    "no_merge": true,
    "no_activation": true,
    "scientific_status": "scoped_only",
    "protected_holds": "All existing holds remain; no unit-completion percentage for total physical goal"
  }
}
```


## HE-X1

원본: `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/0`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "HE-X1",
  "title": "Outgoing angular moment-cone admission",
  "depends_on": [],
  "status": "current_unit_selected",
  "entrypoints": [
    "research/he38_h1_finite_mass_gain_20261023/NEXT_DAG.json",
    "research/he38_h1_finite_mass_gain_20261023/theory/DERIVATION.md",
    "research/orchestration_longterm_20261023/current_unit/X1_FROZEN_CONTRACT.md"
  ],
  "inputs_domain": "inclusive count2 electron measure, epsilon>=0, one common COM frame",
  "equations_scope": "S=integral epsilon nnT; S PSD,trS=K; D=(3aTSa-K)/2; -K/2<=D<=K; K=E-I-Kp",
  "claim_gates": [
    "Exact algebraic fixtures and numerical tri-state boundary; no clipping",
    "Necessary moment realizability only, empirical calibration remains open"
  ],
  "pass_action": "Permit source candidate to next source/frame/event-correlation gate",
  "budget": "Fresh algebraCPU10s/wall30s; oldHE38 budget unchanged;IVP0",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## HE-ANG

원본: `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/1`. 내부 선행: HE-X1. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "HE-ANG",
  "title": "Source-qualified H1 angular provider",
  "depends_on": [
    "HE-X1"
  ],
  "status": "planned",
  "entrypoints": [
    "research/he38_h1_finite_mass_gain_20261023/NEXT_DAG.json",
    "research/he38_h1_finite_mass_gain_20261023/components/finite_mass/h1_finite_mass/model.py"
  ],
  "inputs_domain": "DDCS inclusive electron count2 + ion recoil in consistent energy/frame; actual measured domain",
  "equations_scope": "Integrate K_e,D_e and ion momentum/energy/STF from same differential law",
  "claim_gates": [
    "Labels/exchange/slow-electron support and lab/COM mapping admitted",
    "No unmatched CCC total times Le-Cambier partition",
    "Physical uncertainty and quadrature allocations must be calibrated; existing HE38 raw1e-8 gate is model-numerics only"
  ],
  "pass_action": "Replace uniform-angular law only in a new pinned source model; affected moment checks",
  "budget": "Source admission first; no provider scan/newIVP until own bounded budget; do not rerun HE38129T",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## HE-EXCHANGE

원본: `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/2`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "HE-EXCHANGE",
  "title": "Finite-mass species elastic exchange",
  "depends_on": [],
  "status": "planned",
  "entrypoints": [
    "research/he35_finite_mass_pair_20261023/CONTRACT.json",
    "research/he34_lorentz_transport_20261022/",
    "research/he34_sandbox_certified_relaxation_20261022/NEXT_DAG.json",
    "research/he38_h1_finite_mass_gain_20261023/NEXT_DAG.json"
  ],
  "inputs_domain": "e-H/e-p/ion-neutral source-qualified cross sections on selectedT domain; HE35 supplied-kappa pseudo-Maxwell finite-mass pair already complete within conditional model; reuse it",
  "equations_scope": "Species momentum,heat,STF exchange sums conserve total; compare relaxation/source/Hubble times",
  "claim_gates": [
    "Lorentz instantaneous l2 rate distinct from finite-time one-rate closure",
    "Neutral p/eta distinct from species quadrupole rate",
    "Rate/model uncertainties currently uncalibrated; obtain primary domain and independent witness",
    "HE35 oracle/conservation/C-Python5e-13 already scoped verified; empirical kappa admission remains open, do not redo conditional pair derivation"
  ],
  "pass_action": "Provide numerical coefficients and error bounds to closure assessment",
  "budget": "No oldLorentz/HE34 tests replay; one admitted pair first; fresh numerical cap pending",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## HE-RESERVOIR

원본: `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/3`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "HE-RESERVOIR",
  "title": "Thermal/UV and selected extra-channel admission",
  "depends_on": [],
  "status": "planned",
  "entrypoints": [
    "research/he38_h1_finite_mass_gain_20261023/NEXT_DAG.json",
    "research/he37_h1_differential_gain_20261023/NEXT_DAG.json"
  ],
  "inputs_domain": "C23AUVB0<=z<=15.1 vs HE32startz20; actual spectrum and thermal/fast census",
  "equations_scope": "Separate electron/photon/ion reservoir energy; selected RR/DR/CX or nuclear daughter source ownership",
  "claim_gates": [
    "Supply earlier-z provider or later-start matchingIC; never extrapolate UVB",
    "Total rates/heating do not determine spectrum; nucleus daughters need charge/angle/stopping",
    "Each new source needs calibrated uncertainty obligation"
  ],
  "pass_action": "Emit source-reservoir schema with exact scope and ownership for closure",
  "budget": "NoHE32394replay; no new evolution until source admission",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## HE-CLOSURE

원본: `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/4`. 내부 선행: HE-ANG, HE-EXCHANGE, HE-RESERVOIR. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "HE-CLOSURE",
  "title": "Species-to-total-gas closure and source-aware reduction",
  "depends_on": [
    "HE-ANG",
    "HE-EXCHANGE",
    "HE-RESERVOIR"
  ],
  "status": "planned",
  "entrypoints": [
    "research/he38_h1_finite_mass_gain_20261023/components/finite_mass/h1_finite_mass/bridge.py",
    "research/he38_h1_finite_mass_gain_20261023/NEXT_DAG.json"
  ],
  "inputs_domain": "Independent speciesT/u/STF or explicitly justified commonT/u; selected species manifest",
  "equations_scope": "pi_b=sum_species pi_s; projection(source(liftY)) versus reduced source; thermal particle count follows reactions",
  "claim_gates": [
    "Relaxation/source timescale ratios plus error budget calibrated, not presumed",
    "Lift commutator defect bounded against declared observable tolerance",
    "Positive birth kinetic energy never asserted thermalization rate"
  ],
  "pass_action": "Freeze one saved-background coupled gas control with initial state/oracle/output obligations",
  "budget": "Input-dependent; inherited budgets unreplenished; no currentIVP",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## HE-FEEDBACK

원본: `thermal/BASS_HE_LONGTERM_CONTRACTS.json/nodes/5`. 내부 선행: HE-CLOSURE. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "id": "HE-FEEDBACK",
  "title": "Saved-background gas then metric feedback",
  "depends_on": [
    "HE-CLOSURE"
  ],
  "status": "input_dependent",
  "entrypoints": [
    "research/he38_h1_finite_mass_gain_20261023/NEXT_DAG.json",
    "research/he32_sandbox_primordial_20261021/RESULTS_KO.md"
  ],
  "inputs_domain": "One savedHE32 background then separate metric-coupled problem",
  "equations_scope": "Baryon tensor/source budget distinct from nonbaryonic matter stress",
  "claim_gates": [
    "First finite scoped gas control convergence; then Einstein/source energy closure",
    "Quantitative gates need observable/error allocation calibration before execution"
  ],
  "pass_action": "Admit only declared finite coupling result, then design global convergence study",
  "budget": "NOT_SCHEDULED; HE32394 remain reused; new budget requires frozen scope",
  "fail_action": "Preserve raw failure and source identity; repair only diagnosed affected dependency; no campaign reset",
  "review": "Independent theory/implementation review on changed dependencies; packaging and science verdicts separate"
}
```


## 저장소 간 조건부 연결

채널을 선택할 때만 해당 공급자 조건을 적용한다. 모든 공급자의 동시 완료를 요구하지 않는다.


- `HE-X1` → `REI-L0`: using angular-moment injection. Necessary PSD/moment-cone gate only; does not supply angular distribution or physical cross section


- `HE-ANG` → `REI-L3`: selecting anisotropic baryonic scattering transport. Source-qualified angular moments needed; event frequency is not l2 transport


- `HE-EXCHANGE` → `REI-L3`: selecting finite-mass baryonic pressure exchange. Momentum/energy and pair symmetry from supported physical model


- `HE-CLOSURE` → `REI-L4`: selecting nonzero baryonic anisotropic stress. Isotropic pi_b=0 minimal pilot does not require this extension
