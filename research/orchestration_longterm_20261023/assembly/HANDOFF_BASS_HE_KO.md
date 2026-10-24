# cosmosapjw-quantum/BASS_HE 인수인계

## 최신 실측 window 결과 — 2026-10-24 / PR94

**HE-ANG-DDCS20-WINDOW는 COMPLETE_SCOPED**, 과학 commit `d8bae9f7e24ad3494e399f7ab46c4167a5623d48` ([draft PR94](https://github.com/cosmosapjw-quantum/BASS_HE/pull/94)), source base `bf3c21a39b1111497ed77667d05b8a853ffe6646`다. Childers et al. PRA69,022709(2004) Table IV E0=20 eV의40개 전사값을 보존하고 E=3–6 eV/theta15–120degree의32개만 사용했다. 검출 전자 finite-window marginal, 축대칭 linear-mu 보간 및 선택한 deterministic sensitivity box 조건부 결과다. Box 범위는 confidence interval이 아니다.

N_W=1.918935932462322e-21 m², mean(mu)=0.5215950231699314, mean(P2)=0.1799846901344856, mean(E)=4.581073268756349 eV, mean(sqrt(E)mu)=1.111325457435915다. Source quoted errors/미지 covariance, 보간 가정, 미관측 영역은 별도다. 다른 scalar의 box witness를 하나의 공동 극값으로 결합하지 않는다.

R6 PASS/C9 PASS_SCOPED, 8 targeted unittest 및11 actual-output checks가 통과했다. 실제3 child 누적 local CPU1.9570049999999999초/wall2.104758352987119초(새 allocation20/60), repair0회다. 이전 Hex/HEANG/HE38/HE-X1/D10 및 remote UNKNOWN_NOT_ZERO는 보존하고 새 예산으로 전용하지 않았다. 완료된 기존 suite의 재실행과 새 IVP는 수행하지 않았다.

부모 **HE-ANG SOURCE_INPUT_PENDING**과 다음 node **HE-ANG-SOURCE-PAYLOAD**는 유지한다. 실측 single-electron marginal은 확보했지만 joint outgoing electron law, full support, count/spin/exchange convention, laboratory/COM 및 finite-mass recoil correlation 입력이 여전히 필요하다. X1 empirical angular correction/event total/collision source로 승격하지 않는다.

근거: `research/he_ang_ddcs20_window_20261024/RESULTS_KO.md`, `CLAIM_GATE.json`, `evidence/review/C9_REVIEW.json`; 중앙 return `assembly/returns/BASS_HE_HEANG_DDCS20_20261024.json`. 최종 S+C archive(441,890 bytes, SHA256 bca49013628469f7d149366d651a1a004f936ad15fc1e5d74f8029ba3799223e)는 Dropbox/Drive metadata readback 양쪽 확인을 완료했다. 실제 provider ID와 범위는 `assembly/returns/BASS_HE_HEANG_DDCS20_BACKUP_ACK_20261024.json`를 참조한다. 독립 remote SHA256 검증은 하지 않았다. 원 저자 계약, 다른39node 및 기존 Hex 성공기록은 변경하지 않았다. no_merge/no_activation.

## 최신 관측과 재개점 — 2026-10-24

HE-ANG의 source/frame/event 계약은 PR92 과학 핀 `896e5427100ad48d017deff2697b6f992ba029cd`에서 이미 `COMPLETE_SCOPED`다. 이를 재사용하여 **HE-ANG-SOURCE-HEX-INTAKE**를 [PR93](https://github.com/cosmosapjw-quantum/BASS_HE/pull/93), 과학 핀 `15053fe4445a32e0544d644e864fe27780d08743`에서 완료했다. 부모 **HE-ANG은 SOURCE_INPUT_PENDING**이다.

선택한 공식 Hex SQL 전체에서 tmat948,557행, H1초기100 tmat86,457행, 해당 Ei raw extrema1e-7..0.9374Ry, ionf0행을 확인했다. 이 파일은 H1 이온화 payload를 제공하지 않는다. 저장된 유한 Chebyshev 계수의 전체 생략 suffix bound와 명시적 ABI utility는 scoped 승인이다. HE-X1의32fixture와 기존 HE-ANG 검토는 재사용했으며 경험적 각분포로 확대하지 않았다.

첫 열린 입력은 **HE-ANG-SOURCE-PAYLOAD**다. [NEXT_SOURCE_CONTRACT.json](https://github.com/cosmosapjw-quantum/BASS_HE/blob/15053fe4445a32e0544d644e864fe27780d08743/research/he_ang_source_hex_20261024/NEXT_SOURCE_CONTRACT.json)에 실제 ionization coefficient/joint differential data, producer ABI, normalization·spin/exchange·support, finite-mass 및 동일 frame/event law 의무를 고정했다. 다음 단위 전에 AGENTS·실제HEAD·병렬변경·백업을 확인하고 새 입력에 해당하는 범위만 실행한다.

새 intake 누적 CPU18.434312초/wall18.739399초(총20/60)는 실패2회를 포함한다. nominal8초보다 큰 실제 catalogue CPU8.349479/8.144439초도 보존했다. 과거 예산과 UNKNOWN_NOT_ZERO를 초기화하거나 전용하지 않는다. 현재 예산에서 full Hex solve·새 IVP를 착수하지 않는다. 독립 science/code 판정은 PASS_SCOPED, 물리 provider gate는 유지한다.

근거: [RESULTS_KO.md](https://github.com/cosmosapjw-quantum/BASS_HE/blob/15053fe4445a32e0544d644e864fe27780d08743/research/he_ang_source_hex_20261024/RESULTS_KO.md), `assembly/returns/BASS_HE_HEANG_SOURCE_HEX_20261024.json`. 실제 Dropbox/Drive archive ACK는 `assembly/returns/BASS_HE_HEANG_SOURCE_BACKUP_ACK_20261024.json`에 별도 기록한다. 아래 원 저자 계약과 다른 39개 node는 변경하지 않았다. no_merge / no_activation.

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

## 현재 X1 실행 상태 보정

HE-X1 계획 wrapper는 `COMPLETE_SCOPED`다. `current_unit/INDEPENDENT_REVIEW.md`, `raw_outcomes.json`, `LOOP_PROGRESS.json`과 과학 커밋 `eb03981d15ad291375dd6d574a9c28809f85fc02`가 실제 32 fixture 및 독립 PASS_SCOPED를 기록한다. 위 원 계약의 `current_unit_selected`는 역사적 선택 상태로 그대로 보존했다. 물리 소스·event 상관·runtime 승인은 별도다.
