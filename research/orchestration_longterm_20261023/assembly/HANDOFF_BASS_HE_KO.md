## 최신 sparse joint TDCS 결과 — 2026-10-24 / PR96

**HE-ANG-TDCS54-ANCHORS는 COMPLETE_SCOPED**다. Science S는 `60cacdb740fa4dadcdcbff43b7ffcb52566e077d` ([draft PR96](https://github.com/cosmosapjw-quantum/BASS_HE/pull/96)), source baseline은 `2cb9f9176c2a1764bb8ceaf2392531a100eb6820`다. Jones–Madison, PRA62,042701(2000)의 Table IV와 article p8/Fig.10에서 입사 54.4eV, slow 5eV, slow 210도 CW, fast 4/10도 CCW의 두 located H1s joint TDCS 좌표를 확보했다. Source atomic units의 (CDW-EIS, CCC99, experiment)는 각각 (1.83,2.58,1.52)와 (0.99,1.51,1.24)다. 전체 8개 높이 특징량의 24개 source value와 16개 printed ratio를 보존하지만, slow angle이 없는 나머지 행을 추가 joint 좌표로 만들지 않았다.

양의 printed nominal 입력에서 exact Fraction common-scale feasibility와 witness, 자유/clipped minimax, scale-free pair contrast, signed source-angle geometry와 조건부 printing consistency를 구현했다. Located delta*는 CDW637/3145, CCC565/3434이며, A∈[13/20,27/20]의 CCC 최소치는44/171이다. All-feature CDW1593/5849≈27.235425%는 원전의 descriptive26%와 나란히 보존한다. δ=.10과 scale 상자는 지정한 결정론적 민감도 모형이며 confidence interval이나 cross-section 보정 제안이 아니다. 원전의 infinite nucleus, CDW exchange neglect와 CCC99의 unpublished Bray 제공 provenance를 유지하고 spin/count/factor4를 추가하지 않았다.

독립 R6 PASS, 14개 test method PASS, 16/16 printing control compatible, C9 PASS_AFTER_FIGURE_CORRECTION이며 현재 blocker0/root PASS_SCOPED다. 유일한 C9-FIG-01은 주석이 marker를 가린 표시 문제였다. 원래 code/runner/PNG/SVG를 보존한 뒤 annotation x=.03→.40만 고쳐 plot-only reserve를 한 번 실행했고, tests/analysis/core/source는 변경하거나 재실행하지 않았다. 측정 4개 child와 runner의 누적 CPU1.887889초/wall1.9431963300012285초, fresh allocation8/30, reserve1회이며 failures/overshoots0이다. Host orchestration과 remote 전체 CPU는 UNKNOWN_NOT_ZERO이고 end_to_end_cpu_cap_established=false다. 이전 budget·실패·unknown은 리셋·전용하지 않았다.

부모 **HE-ANG SOURCE_INPUT_PENDING**, 다음 **HE-ANG-SOURCE-PAYLOAD**, physical_provider_admitted=false를 유지한다. 이번 두 점은 희소 joint source 관측값이며 full continuous joint law, event sigma 또는 finite-mass ion recoil provider가 아니다. Count/spin/exchange/support/frame/recoil와 calibrated uncertainty의 source-consistent 전체 계약이 여전히 필요하다. C9-NB-01, C23E, 원래 HE-ANG 계약·의존성·기존 관측 및 다른 39개 node의 최신 owner 상태는 그대로 보존했다.

근거는 `research/he_ang_tdcs54_anchors_20261024/RESULTS_KO.md`, `CLAIM_GATE.json`, `source/TABLE_IV_INPUT.json`, `reviews/C9_REPORT.json`과 새 central return `assembly/returns/BASS_HE_HEANG_TDCS54_ANCHORS_20261024.json`이다. B1은178668bytes의 양쪽 upload/metadata readback을 완료했다. 현재19/20이며 C10은 actual publication/delivery 대기다. S+C의 B2와 후속 D/E/B3 backup은 실제 ACK 뒤에만 기록한다. S 게시 뒤 사라진 local workspace는 retained transport에서 91개 published file을 literal bytes로 복원해 actual S Git blob SHA1/size와 전부 대조했다. 과학 재실행이나 예산 초기화는 없고 복원 원인은 NOT_ESTABLISHED, host recovery 비용은 UNKNOWN_NOT_ZERO로 보존한다. 현재 central base는 `fca9a31de961a85f14972550c1f4c35c4fc3e773`다. 최신 parent의 REI L1은 한 child를 실제 완료한 ADMITTED_SCOPED_SUMMARY_CONSUMER이며 isotropic scalar HI photon-summary/no-deposition/zero-recoil 근사다. Raw atom payload qualification은 NOT_RUN이고 full L1 validation은 미확보다. Finite-pressure interval은 정적 준비이며 수치 NOT_RUN, 별도 budget NOT_AUTHORIZED다. 이 owner의 실제 결과·OPEN·비용과 ANGTHERM02 read-only 경계는 해당 자료와 새 base tree에 그대로 보존했다. 이를 TDCS54의 실행권이나 물리 공급자로 수입하지 않는다. No merge/no activation을 유지한다.

## 최신 전달 완료 기록 — 2026-10-24 / PR95, Delivery D

HE-ANG-CCC-EXCHANGE의 실제 Delivery D는 `2cb9f9176c2a1764bb8ceaf2392531a100eb6820`이며 Science S `63706d605ddfc5d313ca310b09b5fd54a4efdbf4` 위에 metadata만 추가했다. R1–R10/C1–C10의 20개 stage row는 COMPLETE_SCOPED다. [Draft PR95](https://github.com/cosmosapjw-quantum/BASS_HE/pull/95)는 merge/activation 없이 유지한다. Science S의 code, source, numerical results, figure, 독립 review와 raw 실행은 재사용했고 추가 과학 실행은 없다. Central observation C는 `d5aa6c94a77b5687052d3d6902d140e2df9ef798`다.

B2 archive `HEANG_CCC_EXCHANGE_20261024_63706d60_d5aa6c94.tar.gz`는 278,842 bytes, 72 members이며 local SHA256는 `21303684dbb2a0bed96d368802c70093cd343ccd644c53710036f16712c881f0`다. Science S의 정확한 65개 파일과 Central C의 3개 파일, 실제 게시 receipts와 복원 자료를 보존한다. Drive ID `1QuA8qmz8tOuLcQTAIozQEI0Jy-3pjBkV`, Dropbox ID `id:BSpOijBcT10AAAAAAD_9JQ` 양쪽에서 upload 완료와 독립 metadata size readback을 확인했다. 별도의 remote SHA256는 반환되지 않아 독립 원격 hash 검증을 주장하지 않는다.

실제 ACK와 S/D/C identity는 `assembly/returns/BASS_HE_HEANG_CCC_EXCHANGE_BACKUP_ACK_20261024.json`에 기록한다. 이 파일의 E identity는 CURRENT_FILE_COMMIT이며 실제 SHA는 후속 receipt에 남긴다. D와 E를 보존하는 B3 supplement는 아직 실제 upload/readback ACK 대기다. B3의 실제 SHA256, Drive/Dropbox ACK와 metadata size readback은 업로드 뒤 [PR95 설명](https://github.com/cosmosapjw-quantum/BASS_HE/pull/95)에 기록한다. 자체 archive 안에 그 archive의 미래 업로드 receipt를 재귀적으로 넣지 않는다. 최종 사용자 인계 보고는 B3의 이중 ACK 뒤에 한다. B2가 미래 D/E를 이미 포함했다고 해석하지 않는다.

독립 R6/C9 PASS_AFTER_CORRECTION과 root PASS_SCOPED, physical_provider_admitted=false, 부모 HE-ANG SOURCE_INPUT_PENDING 및 다음 HE-ANG-SOURCE-PAYLOAD를 유지한다. 측정된 4개 child와 runner의 CPU 1.410021초, wall 1.4436621759814443초 및 reserve 1회와 별도 prelaunch 부모 CPU UNKNOWN_NOT_ZERO를 보존한다. end_to_end_cpu_cap_established=false다. C9-NB-01, C23E, 최신 CR-N5의 Drive ACK unknown과 다른 owner의 기록, 원래 HE-ANG 계약·의존성·기존 관측은 변경하지 않는다.

## 최신 CCC equal-sharing convention 결과 — 2026-10-24 / PR95

**HE-ANG-CCC-EXCHANGE는 COMPLETE_SCOPED**다. Science S는 `63706d605ddfc5d313ca310b09b5fd54a4efdbf4` ([draft PR95](https://github.com/cosmosapjw-quantum/BASS_HE/pull/95))이며, baseline은 `c8f5818c61d14872837abf7e9bc1a73c670ae25c`다. Bray physics/9906008v3 Eq. (26)의 인쇄된 minus와 정의의 차이를 해당 pinned 식에 한정해 교정했다. Raw complex pair, 이미 coherent인 density, 이미 spin-weighted인 density, phase 정보가 없는 intensity를 구별하는 조건부 CCC exact equal-sharing adapter를 구현했다. 실제 Stelbovics TP Table I의 8개 4CCC 값은 원문 정규화를 보존하고 printed BRM과 산술 비교만 수행했다.

R6와 C9는 모두 PASS_AFTER_CORRECTION이고 현재 blocker는 0이며, root는 PASS_SCOPED를 채택했다. 초기 14개 test method의 PASS 뒤 C9-01 assertion scale 결함만 수정하여 test_05 한 method를 reserve로 검산했다. Kernel은 변경하지 않았다. 실제 4개 child와 runner 구간의 측정 누적 CPU는 1.410021초, wall은 1.4436621759814443초이며, 새 allocation은 CPU8/wall30초, reserve 사용은 1회다. 최초 reserve prelaunch는 빈 task lock의 FileExistsError 때문에 START와 child 전에 멈췄고, root가 해당 task lock만 정리하도록 승인했다. 부모 CPU의 UNKNOWN_NOT_ZERO를 별도로 보존하므로 end_to_end_cpu_cap_established=false다. 미측정 host 준비·문서 I/O와 remote symbolic 전체 CPU도 0으로 바꾸지 않았다. 과거 allocation, 실패와 unknown은 이전 ledger에 보존하며 새 예산으로 전용하지 않는다.

부모 **HE-ANG SOURCE_INPUT_PENDING**, 다음 node **HE-ANG-SOURCE-PAYLOAD**, physical_provider_admitted=false를 유지한다. 같은 source·producer·kinematics·preparation, exact energy point, 단위와 측도를 갖춘 조건부 산술이다. Full H joint payload, support, count, frame, recoil과 uncertainty 입력은 여전히 필요하다. 새 strong no-go나 전체 물리 목표의 완료를 주장하지 않는다. HE38, X1, contract, Hex와 DDCS20의 실행 근거는 재사용했으며, old suite replay, 새 IVP, CCC solve와 Hex solve는 0회다.

근거는 `research/he_ang_ccc_exchange_20261024/RESULTS_KO.md`, `CLAIM_GATE.json`, `SCIENCE_DECISION_KO.md`, `evidence/review/C9_REPORT.json`과 새 central return `assembly/returns/BASS_HE_HEANG_CCC_EXCHANGE_20261024.json`이다. B1 preparation은 양쪽 provider에서 40,303 bytes의 metadata readback을 완료했다. 최종 Science S와 central C, 후속 delivery의 backup ACK는 **PENDING_ACTUAL_BACKUP_ACK**이며 실제 응답 뒤 별도로 추가한다. C10은 실제 최종 전달 대기다. 현재 central base는 CR-N5의 최신 receipts와 Drive ACK unknown 상태를 포함한 `f3ff95c4ddbdc4279223929a777072ec4eace577`다. 원래 HE-ANG 계약, 의존성, 기존 관측과 다른 39개 node 및 C23E·CR 기록을 그대로 보존했다. no_merge/no_activation을 유지한다.

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
