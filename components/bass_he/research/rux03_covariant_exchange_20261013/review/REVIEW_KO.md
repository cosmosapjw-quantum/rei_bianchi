# 독립 R6 검토 — 공변 H/He 사건 전달

## 1. 최종 판정

**`PROMOTE_SCOPED_THEORY`**로 판정한다. `HERE_RUX03_COVARIANT_EXCHANGE_04`의 C01–C07은 고정된 공통 기체 프레임·비상대론적 warm Case A·각도 및 단계 배치 가정 아래 채택한다. R00은 이전 결과의 재사용으로 유지한다. 최종 v2 범위에서 미해결 중대 오류나 채택을 막는 지적은 없다.

이는 공변 전달식과 해당 조건부 구성의 이론 채택이다. 현재 receiver에 새 momentum provider가 연결되었다거나, gas velocity·escape radiation transport가 구현되었다는 판정은 아니다. 일반 four-force와 1+3 shear 구조의 문헌상 우선권도 새 성과로 주장하지 않는다.

최종 freeze는 `CANDIDATE_FROZEN_INPUTS_v2.json`의 27개 파일이며, SHA256은
`bfaee413277ad99a6ee39caafaeaf9c2a5242abbcd1f416c528d1b318d2b73af`다.
전부 실제 bytes와 대조했다. 전체 검토 파일과 직접 읽기·이전 검토 재사용·hash-only 범위는 `REVIEWED_ARTIFACTS.json`에 기록했다. 이 메모와 그 목록의 해시는 `DECISION.json`이 묶는다.

## 2. 독립성과 검토 방법

검토자 `/root/dropbox_checkpoint`는 이번 후보의 유도·계산 코드·수용 기준을 작성하지 않았다. 앞선 일차 문헌 검토와 현재의 독립 판정만 담당했다. Root의 공변 유도, 별도 author의 기하 유도와 symbolic 입력, 실제 원응답, 최종 문서·구현 계약을 읽고 원식·소스·단위를 대조했다. 신규 native/원자계수/RHS/ODE/기호 계산은 실행하지 않았다. 수행한 기계적 작업은 저장 JSON의 파싱·동일성 비교, embedded input 비교, 파일 해시 확인이다.

v1의 16개 파일은 보완 전 모두 freeze와 일치했다. 이후 세 설명 보완과 새 문서를 추가한 v2를 검토했다. 최종 계산 입력·원응답·결과는 v1과 동일하다. 지적에 대한 최소 설명 수정은 아래 §5에 기록하며, 검토자가 후보 파일을 수정한 일은 없다.

## 3. 주장별 채택 범위

| 주장 | 독립 확인과 판정 |
|---|---|
| R00 | 이전 shared event/binding/provider 및 endpoint-work 유도와 47개 symbolic group을 재사용한다. `2s DeltaP`는 이미 source에 있다. 새 실행·새 알고리즘으로 세지 않는다. |
| C01 | 양의 흡수 사건에 전체 photon momentum을 곱한 합과 comoving-isotropic escape의 두 투영, 세 부문의 전달 소거가 맞다. 현재 μ node에는 ring 평균을 사용한다. Escape isotropy는 scalar counter로부터 새로 명시한 angular closure다. |
| C02 | neutral reference mass와 binding을 포함한 perfect-fluid stress의 에너지·운동량 투영이 맞다. 핵수 보존을 사용하면 기존 `dot w=-2H w+Q_th^(H)`와 `dot u_th=-5H u_th+Q_th`가 회복된다. 비상대론적 한 온도 constitutive model의 결과다. |
| C03 | 일반 공간 flux와 STF anisotropic stress를 유지한 미분 투영이 맞다. `D·q`로 바꿀 때 가속도–flux 항이 두 개 생긴다. 추상 텐서 미분과 별도 local-frame 행렬 검산이 같은 부호·c 인자를 준다. |
| C04 | prescribed diagonal Bianchi I의 방향 에너지비·방향 갱신, native characteristic, `sigma:pi=2s DeltaP` 및 endpoint-energy discrete work의 대응이 맞다. 일반 반응 과정의 연속 work 적분과 유한 BE work는 구별한다. |
| C05 | 같은 에너지/count/source 및 반사에 대해 같은 channel opacity를 갖는 pair는 공통 물리적 candidate에서 대칭을 보존한다. 양의 BE 분모는 이 pair 성질을 보존하되 gas root의 존재·유일성을 별도로 증명하지 않는다. Zero force와 비영 shear work가 공존하는 여섯 빔 구성이 성립한다. |
| C06 | 반대 방향의 같은 energy density와 다른 양의 opacity는 `q=0`이면서 `f_abs != 0`인 반례다. 이는 flux-only 조건의 불충분성에 한정된다. 실제 두 Verner energy에서 2:1 비율을 측정한 결과나 strong no-go가 아니다. |
| C07 | 이미 정의된 four-force를 임의의 timelike observer로 투영한 식이 맞다. `|beta|<1`과 명시된 gamma 관계를 사용한다. Rest-frame atomic fit을 상대론적으로 재유도하거나 moving-gas integrator를 검증한 결과는 아니다. |

### 단위·에너지 소유

Root의 `E_q`는 eV이고 기하 문서의 `E_q`는 erg다. 후자는 `E_erg/epsilon_eV`를 원자 cross-section callback에 넘긴다. 실제 photon momentum과 흡수 force에는 `mathcal E=epsilon_eV E`를 사용한다. 따라서

\[
\mathcal Q_{\rm abs}=\sum_{iq}\mathcal E_q\mathcal R_{iq},\qquad
f^a_{\rm abs}=\frac1c\sum_{iq}\mathcal E_q\mathcal R_{iq}e_q^a
\]

의 단위는 각각 erg cm\(^{-3}\) s\(^{-1}\), erg cm\(^{-4}\)다. Heat의 `E-chi`를 momentum에 넣지 않는다. Per-H 사건과 proper 사건 사이의 `n_H`, reference count와 proper density 사이의 `V`, quadrature weight도 각각 한 번만 들어간다. 새 코딩 계약의 SI 변환은 energy density/power ×0.1, flux ×10\(^{-3}\), force와 four-force component ×10으로 맞다.

Gas reference mass는 중성 H/He 원자 및 그 전자 질량을 이미 포함한다. 양의 binding 다항식이 이온화에 따른 조성 에너지를 더하므로 자유전자 rest mass를 다시 더하지 않는다. 실제 `Q_esc`는 RR/DR binding과 captured kinetic powers의 합이며, 추가 line/free-free channel을 가정하지 않는다.

### 공간 투영과 기하 예의 양화

일반적인 기체 공간 방정식은

\[
\frac{\rho_g+p_g}{c^2}a^a+D^ap_g=f^a_{\rm abs}-\ell^a_{\rm esc}
\]

이다. 선택된 geodesic·homogeneous-pressure·isotropic-escape 적용에서만 우변의 순힘 0이 호환 조건이 된다. 공통 속도라는 말만으로 geodesic 조건이 따라오지 않는다. 현재 코드는 일반 비대칭 node도 허용하므로 scalar energy ledger의 통과가 이 공간 방정식의 완료를 뜻하지 않는다.

각도 pair는 odd first moment를 소거하면서 even pressure를 남긴다. 여섯 빔의 `eta=2/3` 예와 `s h=ln 2`에서 energy ratio `5/6`, work ratio `1/6`이 맞다. `eta=1/3`의 `17/12` 및 `-5/12`도 지정된 비등방 redshift의 정확한 값이다. 이 `H=0` 예는 prescribed 시험 계량이며 선택된 Einstein dust+Lambda 배경의 해로 채택하지 않는다. 기존 실제 초기 자료의 반사 대칭, pair invariant subspace의 수학적 증명, 장기 trajectory의 기계적 parity는 서로 다른 주장이다.

## 4. 실제 검산과 source 근거

최종 xAct wrapper의 `ToExpression` 안 문자열이 `XACT_COVARIANT_PROGRAM.wl`과 byte-for-byte 동일함을 확인했다. 원응답의 출력 JSON 문자열을 직접 파싱한 결과가 저장된 xAct 결과와 같고, geometry 원응답도 그 결과 JSON의 `result`와 같다.

| 최종 근거 | 확인된 수 |
|---|---:|
| xAct tensor group | 24개 True, 24개 residual 모두 `0` |
| 같은 실행의 scalar group | 5개 True |
| 별도 geometry scalar/matrix group | 16개 True |
| 최종 이름이 서로 다른 검사 그룹 | 45개 |

45는 검사 그룹의 수다. 서로 독립인 45개 물리 실험이나 45개 새 정리를 뜻하지 않는다. Geometry input의 두 저장 경로는 같은 bytes이고 한 실행으로 센다. Smoke 6개, metadata 교정 전 동일한 29개, 이전 단위 47개는 더하지 않았다. CLAIMS의 모든 검사 이름이 실제 최종 출력에 존재한다.

xAct는 실제 metric·covariant derivative·tensor를 선언했다. 미분 규칙은 velocity decomposition과 `u·q=0`, `u·pi=0`의 미분이며 목표 에너지식을 규칙으로 주입하지 않는다. `CD`가 stress divergence를 전개한다. 양성 영역과 비영 힘의 조건은 문서의 가정·삼각부등식·직접 대수 추론으로 확인했으며, 단순히 True 출력이 부등식의 모든 가정을 인증한다고 취급하지 않았다.

EX00은 preinstalled package 부재, EX01은 잘못된 Global namespace, EX02–EX04는 canonicalization invocation 실패, EX06–EX07은 differential MakeRule 생성 단계에서 최종 과학 결과가 없는 것으로 원자료와 일치한다. `isError:false`가 있더라도 `Hold[Throw[Null]]`이나 최종 결과 부재를 통과로 해석하지 않았다. EX06과 최종 program의 차이는 kinematic/spatiality 규칙의 표현 및 metadata이며 target 식을 바꾸지 않았다. EX08과 최종 embedded science의 차이는 `$Version`을 ``System`$Version``으로 한정한 한 줄이다. 두 실행의 scientific result fields는 같다.

최종 성공 계산은 공식 xAct archive SHA256 `7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`를 확인하고 xTensor를 적재했다. Startup의 external-link 메시지와 별개로 실제 selector는 `xPermExternalBackend=false`이며 순수 Wolfram backend를 사용한다. EX00의 원래 input이 저장되지 않았다는 제한도 execution record가 밝힌다. 최종 성공 input·원응답·실행 identity는 보존되어 있다.

현재 source의 실제 node absorption loop, owned event ledger, AXI derivative와 cgs/SI boundary, `work_ref`, Python characteristic/source/counter, quadrature를 읽었다. 선택 source 12파일과 기존 build receipt의 identity가 맞는다. `run_interval.py`의 실제 retained 위치는 `recovery_drive/physical_v2/research/physical_provider_20261010/run_interval.py`이며 부분 checkout의 같은 repo path에는 없었다. 이 경로 차이는 파일 목록에 남겼다.

NPZ의 SHA256과 188,284 bytes를 확인했고, producer가 기록한 초기 2,904 node/1,452 pair 정적 비교를 채택한다. 검토자는 이 배열 계산이나 과거 ODE를 다시 실행하지 않았다. 일반 `ConditionalStage`는 opposite-μ equality를 강제하지 않는다는 것은 실제 validation 코드에서 확인했다.

원전은 앞서 직접 읽은 Farris et al. 식 (19),(20),(30), Barrow–Maartens 식 (11),(12), Rosdahl–Teyssier 식 (27),(28), Rosdahl et al. Appendix A의 해당 범위를 재사용한다. 일반 four-force와 shear 항의 기존 지식, 이번 project-specific normalization/ownership 연결을 구별했다. Farris의 추가 grey/Kirchhoff/Eddington 가정과 Rosdahl 2015 mixed-frame appendix의 의심스러운 부호식을 새 유도의 전제로 삼지 않았다. 자세한 URL·페이지·읽은 범위는 `LITERATURE_MAP.md`와 `SOURCE_EVIDENCE.json`에 있다.

## 5. 지적과 최소 보완의 해소

| ID | 관측한 문제와 최초 제기 | 최종 해소 |
|---|---|---|
| R6-C01 | Parent가 μ ring과 실제 unit direction의 대응을 먼저 점검 요청했다. 검토자는 root §2의 bin/node 표현만 읽으면 ring 평균을 개별 null vector로 오해할 수 있다고 확인했다. | Root §2, REPORT, CODING에서 평균 방향 `(0,0,mu)`와 별도 second moment를 명시한다. 양의 null photon의 평균은 비영·`|mu|<1`에서 timelike이며 개별 null 검사를 평균에 적용하지 않는다. |
| R6-C02 | 검토자가 REPORT §7의 현재 code의 “endpoint work” 표현을 지적했다. 실제 source는 순간 `work_ref`를 반환하고 ProductionInterval이 ODE로 누적한다. | REPORT §7와 CODING §5.3이 현재 순간/연속 work와 미래 endpoint-energy BE의 `-sum DeltaE N^-` 수지를 분리한다. 일반 반응 단계의 연속 적분과 동일시하지 않는다. |
| R6-C03 | 검토자가 선택 consumer 및 직전 SHARED 식 (5)에서 RR/DR 이외 추가 escape cooling channel이 없음을 확인했다. 병렬 “retained cooling” 나열이 범위를 넓힐 수 있었다. | Root 식 (13a)와 설명, scientific contract, REPORT에서 기존 RR/DR binding 및 captured kinetic loss만 명시한다. `L_r`도 DR captured kinetic power임을 밝힌다. |

세 보완은 source 대응·설명 범위의 수정이다. 채택한 원자 사건식이나 검산 기준을 바꾸지 않았고 검산을 재실행할 이유가 없었다. 최종 v2에서 모두 해소되었다.

## 6. 남는 구현·이론 의무

현재 채택은 `HERE_RUX03_PRIMARY_PROVIDER_03`의 실제 ordinary/conservative point·endpoint·interval/root·paired caller 연결을 완료시키지 않는다. 그 기존 코딩 의무를 먼저 유지하고, 이후 `HERE_RUX03_COVARIANT_MOMENTS_04`가 같은 raw event에서 새 energy/force/state moments를 실제 소비하도록 한다. 새 코딩 계약의 사례와 허용오차 출처는 후속 C1에서 고정할 대상이며, 이미 통과한 native 근거로 세지 않는다.

비영 힘을 실제 velocity·bulk kinetic energy에 소비하는 `HERE_RUX03_MOVING_GAS_SOURCE_05`는 열린 구성이다. Doppler-shifted opacity, transformed photon measure, common-stage primitive recovery와 finite four-momentum balance는 이번 observer 항등식만으로 끝나지 않는다. `RUX02 + RUX03 -> RUX04 -> RUX05` owner 상태와 D2.3의 별도 범위를 유지한다. 전체 physical EoR admission, recoil-resolved atomic certification, escape spectrum/transport, 일반 moving-frame finite map은 이 판정에 포함되지 않는다.
