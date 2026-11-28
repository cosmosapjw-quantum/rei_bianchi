# B1 → Atomic-Reuse DAG 기술 매핑 검토

2026-10-12 · 역할: 기술 매핑 조언. **최종 계획 승인 또는 새 과학 결과 판정이 아니다.**

검토 입력은 사용자가 첨부한 `REI_ATOMIC_REUSE_DAG_20261012(3).json`,
`REI_ATOMIC_REUSE_PLAN_20261012(2).md`,
`REI_ATOMIC_REUSE_CODEX_HANDOFF_20261012(2).md`와 로컬 B1
`review/DECISION.json`, `SCIENTIFIC_CONTRACT.md`다. Git/Drive의 현재 상태,
P01/P02/P03/v2 archive 내용과 physical admission은 새로 조회하지 않았다.
첨부의 외부 파일 존재·source 상태는 **reported evidence**이며, 이 문서에서
독립 확인된 원격 사실로 승격하지 않는다. 과학 실행은 하지 않았다.

## 1. 새 DAG와 무관하게 보존할 B1 결과

로컬 독립 decision의 판정은 `PROMOTE_SCOPED_PYTHON`이다. 이는 고정된
전자 이력과 처방된 test radiation에 대한 LRS Bianchi-I 비교의 유한 수치
결과를 채택한 것이다. RUX02의 미확인 archive나 향후 full coupled 이력
완료를 기다릴 이유가 없으며, 새 DAG에서도 다음을 retained 항목으로 둔다.

| 보존 대상 | 실제 근거와 범위 | 확대하면 안 되는 주장 |
|---|---|---|
| F/M/B/B0/B_F/M_F의 실제 비교 | 평균 부피 z20→4, 기존 Python Thomson, 고정 source/input identity 및 13개 실행 영수증 | 물리적 이온화 스펙트럼과 H/He gas를 함께 진화시킨 이력 |
| 공통 physical-energy 충돌과 LRS screen/특성선 | 독립 검토의 `PASS_SCOPED`, B0 해석해 비교와 등방/null 결과 | 모든 Bianchi형 또는 native Rust 적분 검증 |
| 처방 이력의 시간 셀 투영 | 원래 Q-cell measure, H_F/H_B 및 명시한 sigma_T convention으로 B clock에 투영 | producer ODE·closure의 연속체 정확도 재채택 |
| q2와 편광 반응 | 선언한 guarded domain의 비초기 3072개 표본에서 경험적 paired 10% 기준 충족 | 엄밀 오차 상계, 통계 신뢰구간, source/thermal/closure 전반의 강건성 |
| 원본 코드·CSV·그림·오차 진단 | `DECISION.json`이 식별한 이미 저장된 산출물 | 새 RUX 노드 전체의 완료 |
| 실행 자원과 미실행 상태 | campaign wall 약 55.22초, 3개 독립 작업 동시 실행, 최대 process RSS 92132 KiB; NCP 0 | 새 coupled runtime도 같은 속도라는 예측 |

원래 native gate는 `HOLD_RUNTIME_ENVIRONMENT`, native parity는 `NOT_RUN`이다.
이 상태와 최초 환경 실패도 보존한다. Python 채택 결과를 취소할 이유도 없고,
반대로 Python 결과로 Rust 실행 gate를 닫을 근거도 없다. 완료된 B1 campaign은
다시 실행하지 않는다. 새 registry에는 B1 decision·계약·산출물의 별도 source
항목을 추가해야 한다. 현재 첨부의 S01–S17에는 B1이 없다.

## 2. RUX 노드에 대한 매핑은 항목 단위로 해야 한다

| RUX | B1에서 가져올 수 있는 내용 | 지금 전체 PASS로 바꿀 수 없는 이유 |
|---|---|---|
| RUX00 | B1의 정확한 source/input/output 식별자와 기존 판정 | 첨부가 요구하는 모든 repo 현재 head·외부 retained source를 확인한 것은 아님 |
| RUX01 | 이미 만든 B1 CSV·그림·claim ceiling을 추가 retained 진단으로 포함 | 기존 F08/SYNC02/SYNC03 source는 이번 검토에서는 reported evidence. B1과 같다고 치환할 수 없음 |
| RUX02–04 | B1의 고정 Q·배경·전자 셀은 해당 역할의 후보/기준 | P01/P02/P03/v2 archive가 입증되지 않았고, B1 radiation은 자유 온도 척도의 Planck test field, 후속 emissivity=0. 실제 ionizing spectrum·gas/source coupling을 공급하지 않음 |
| RUX06 | 정확 LRS 특성선 관계, 공통 에너지/프레임, 등방 극한과 B0 비교의 scoped 근거 | B1은 semi-Lagrangian occupation pullback이다. RUX06이 요구한 **frequency-face flux telescoping과 전파 photon-number ledger**를 별도로 입증하지 않았다. 충돌 단계의 적분 세기 보존은 그 대체물이 아님 |
| RUX05/07–09 | 대조군 설계, 이력/기하 효과 분리, 기존 구현 재사용 원칙 | 실제 H/He 흡수·화학·열 피드백·source photons를 동시 진화시키지 않았으며 reionization ODE 실행은 0 |
| RUX10 | proper ne cell→충돌 깊이의 투영 및 실제 Python Thomson 수신 의미 | RUX09의 physical coupled ne가 없고, observer-tail·full visibility/total tau gate를 닫지 않았다. B1 자체를 source-backed CMB receiver 완료로 바꾸면 안 됨 |
| RUX11/16 | 완료된 scoped figure/release package와 claim 구분 | 전체 physical EoR release의 대상 관측량·오차예산과 입력 채택은 다른 gate |
| RUX12–14 | 이후 sensitivity의 대조군/오차 분석 방식 | B1의 전자 이력 차이는 특정 HE·CR·HH rate에 대한 perturbation이나 source uncertainty 계산이 아님 |

추천 상태는 B1 자체에는 `RETAINED_SCOPED_COMPLETE`, RUX06/10에 대한 관계에는
`PARTIAL_EVIDENCE_REUSED`다. 이것은 조언용 명칭이며 원 첨부의
`PROPOSED_NOT_EXECUTED`를 과거 시점으로 소급 수정하지 않는다.

## 3. 불필요한 직렬화를 줄이는 수정

1. **RUX02와 RUX03은 RUX00 뒤 병렬이다.** JSON의 depends_on은 이미 그렇게
   되어 있다. handoff의 “RUX00 and RUX02, then RUX03”는 실제 DAG보다 더 강한
   직렬 제약이므로 고친다. `main_critical_path`의 단순 배열도 실행 순서를
   강제하는 목록으로 읽지 않아야 한다. RUX05/06, RUX07/08 역시 각각 허용된
   선행조건 아래 병렬로 진행할 수 있다.
2. **RUX06을 재사용 근거와 새 target 통합으로 나눈다.** 기존 특성선/frame
   근거의 수입은 새 physical scenario 전체를 기다릴 필요가 없다. 실제
   coupled frequency grid의 remap/flux 검사는 RUX04 뒤 새 seam에 한정한다.
   B1 전체 반복을 regression이라고 이름만 바꾸어 실행하지 않는다.
3. **RUX10도 기존 수신 의미와 새 physical history 평가를 나눈다.** 기존
   opacity/clock 계약과 retained 진단은 먼저 활용할 수 있다. 새 물리적
   paired tau/visibility 결과만 RUX09 산출물에 의존한다. 완성된 FLRW 이력의
   부분 tau는 필요한 한계와 이름을 명시하면 Bianchi 전구간을 기다리지 않는다.
4. **RUX11의 그림은 공급된 결과마다 나온다.** FLRW 그림은 RUX08, paired
   그림은 RUX09, tau/visibility 그림은 해당 RUX10 결과에서 각각 생성한다.
   모든 목록이 완성되어야 첫 scientific plot을 낼 수 있는 구조는 피한다.
   RUX04가 좁힌 종/관측량 범위를 허용하면서 RUX11이 모든 H/He/Gamma/T
   그림을 무조건 요구하면 계약 충돌이다. 선언한 scope에 맞춰 산출물을 정한다.
5. **RUX02의 필수값은 선택한 입력 묶음의 역할별 합성으로 판단한다.** 모든
   archive 각각이 모든 mandatory field를 담아야 한다고 읽으면 불필요한
   실패가 생긴다. 선택한 source set, 우선순위/대체 관계와 남은 필드를 명시한다.
   archive 이름의 PRODUCTION이나 P03 같은 순번으로 admission을 추론하지 않는다.
6. **NCP의 선행 gate는 실제 job별로 둔다.** `no_new_heavy_until`의 RUX07 PASS를
   모든 별도 원자 작업이나 FLRW-only 작업에 보편 적용할 이유는 없다. 해당
   job의 physical authority와 목적·측정이 필요하다. 현재 생성된 heavy job은
   없고, B1의 작은 실행시간은 coupled history 성능 근거가 아니다.

## 4. HE/CR/HH 선택 경로의 문제와 조정

선택 경로를 baseline의 필수조건에서 제외한 방향은 유지한다. 다만
RUX12/13/14가 모두 RUX11을 기다리는 배치는 실제 소비자 민감도를 늦게
확인하게 만든다. **provider 확인/작은 민감도와 full history effect를 나눈다.**
RUX00/03과 관련 scenario가 준비되면 named-process의 단위·domain·ownership
확인과 짧은 RHS/moment 민감도는 할 수 있다. 그 결과가 목표 observable에
유의미한 경우에만 해당 baseline과 matched history 비교를 연다. 이 작업들이
main lane의 공통 barrier가 되지는 않는다.

- **HE:** ordinary H/He atomic model과 선택적 고정밀 보정은 다르다. H/He
  화학을 주장하면서 필요한 기초 rate/cross-section/heating을 “HE optional”로
  제거해서는 안 된다. ON/OFF는 named correction/source choice에 적용한다.
  첨부 S13의 E13C10은 finite-interval bound 결과로 보고됐으므로, 그것을
  physical rate uncertainty나 실제 emission spectrum으로 수입할 수 없다.
- **CR:** 첨부 S15는 point photon-stock과 wide propagated error 상태만
  보고한다. 그 설명만으로 RUX13의 “hard-particle/deposition” 경로가 같은
  과정이라는 근거는 없다. 저장소 이름의 `CR`로 cosmic-ray/hard-particle
  의미를 추정하지 말고 named process, 입출력량, 반응식과 원 provider 계약을
  확인한다. 당장은 이 process mapping을 `UNRESOLVED`로 둔다.
- **HH:** singlet ion-pair와 free-electron LCS의 구분은 유지한다. named
  reaction의 species/stoichiometry, threshold/energy ownership, domain이
  정해져야 local sensitivity가 물리 의미를 갖는다. 첨부가 보고한 PHYS11
  보존과 native/continuum OPEN을 각각 유지하며, 이를 EoR effect의 채택으로
  바꾸지 않는다.

Case-A/Case-B와 local HI/effective-MFP 중복 방지 역시 **같은 사건의 중복
소유**에 대한 규칙으로 명료화한다. 이름이 다른 두 수치 항이 있다는 이유만으로
서로 다른 공간/종/광자 사건의 정당한 분업까지 전역 XOR로 금지하지 않는다.
반대로 소유권이 겹치는 동일 사건을 두 번 세는 것은 허용되지 않는다.

## 5. 계획 owner에게 권고하는 최소 수정

이번에는 새 full solver나 추가 B1 정밀화를 열지 않는다. B1을 별도 retained
source로 추가하고, RUX06/10을 component evidence와 target-specific acceptance로
나누며, RUX02/03 및 그림/민감도 경로의 불필요한 직렬 의존성을 제거한다.
첨부의 외부 상태는 reported evidence로 남긴다. 실제 다음 physical 실행의
선택은 입력/owner admission에서 확인된 최소 미완료 항목을 기준으로 한다.

이 문서의 판단은 로컬 근거의 기술 매핑이며, archive physical admission,
외부 repository의 현재 채택 상태, 개정 계획의 최종 승인을 제공하지 않는다.
