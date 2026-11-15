# 원래 REI IGM 목표의 복원과 실제 과학 진전

2026-11-16 KST. 기준 owner는 REI PR374, commit `4554fc34765422f1c67e91c99ecac1bc9559fcce`다. 이 통합은 원래 `REI-AXBI-GOAL-20261014`의 `PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1`을 유지한다. 목표는 homogeneous non-tilted axisymmetric Bianchi I와 matched FLRW의 z̄=20→4 H/He/electron abundance·온도·proper-clock 차이를 계산하고 수치·모델 불확실성에 비추어 해석하는 것이다. 단순 재현 plot, 문서 수, PR 수는 과학적 진전으로 계상하지 않는다.

## 이번에 실제로 달라진 것

1. 원본 네 trajectory의 1,248,952행을 소비해 누락된 radiation stress의 누적 shear forcing과 추가 에너지 규모를 계산했다. 순간 moment가 원본 solver에 이미 있다는 사실을 확인했고, 그것을 새 발견으로 세지 않았다. 새 결과는 전체 history에서의 누적 응답·극값·기여 분해다.
2. REC의 Killing-ray label을 순간 tetrad 방향으로 사용하던 오류를 실제 source 정의로 확인하고 고쳤다. 같은 640단계·81,920 photon rows의 Thomson 결과가 바뀌었다. 이 F08 결과는 원래 AXBI baseline abundance의 완료로 세지 않는다.
3. HE 생산자의 photons 대 erg 비교를 같은 단위의 양 끝점 비교로 고쳤다. 이는 검증 오류의 수정이며 새로운 물리 효과로 세지 않는다.
4. 누락된 +0.01 원본의 durable checkpoint를 복구했다. 사라진 종료 영수증과 checkpoint 뒤 47행을 성공으로 해석하지 않았고, 이전 비용의 unknown 상태를 보존했다. 새로 한정한 단일 실행의 결과와 endpoint 상태는 `plus_recovery/`와 `CURRENT_OUTCOME.json`에서 확인한다.
5. 기존 PR318 실행 경로와 PR374 계획을 실제로 고쳤다. 원래 17개 AX 노드가 88개 expansion 노드에서 누락된 문제를 별도 goal view로 복원했다. 기존 28/88은 그대로 보존하며 원래 IGM 성공률로 사용하지 않는다.

## 새로운 과학 결과와 해석의 한계

부호는 (-,+,+,+), 시간은 proper seconds이고 c, ħ, k_B를 유지한다. 원래 metric은

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,\qquad s=\dot b.
\]

처음 등방인 collisionless radiation에 대해 현재 국소 방향 μ에서 D=(1−μ²)e^(−2b)+μ²e^(4b), M=⟨D^(−2)⟩, F=⟨P₂D^(−2)⟩이고 M′(b)=−2F다. 따라서 ΔP=u_ref F와 원본 이온화 photon J₂를 사용한 일차 forcing은

\[
\delta s(a)=a^{-3}\int_{t_i}^{t}a(t')^3\frac{8\pi G}{3c^2}\Delta P(t')\,dt'.
\]

이 식은 고정된 원래 geometry 위의 perturbative 진단이다. background를 다시 푼 coupled Einstein–radiation 결과는 아니다. 이온화 광자는 ΔP_ion=n_H J₂ eV_J를 사용하며, 원본 J₂에 factor 5나 angular weight를 다시 넣지 않는다. 추가 에너지 비교의 분모는 원래 계약대로 3H_FLRW²c²/(8πG)다.

| 원본 case | max abs(δs/H) | max abs(δs_ion/H) | max 추가 에너지/원래 기준 에너지 |
|---|---:|---:|---:|
| q=0 | 3.77656415×10⁻²³ | 3.77656415×10⁻²³ | 5.80937768×10⁻⁹ |
| q=+0.005 | 5.08053550×10⁻⁶ | 6.29377658×10⁻¹⁴ | 2.56913088×10⁻⁸ |
| q=−0.005 | 5.09707434×10⁻⁶ | 6.29483038×10⁻¹⁴ | 2.57471796×10⁻⁸ |
| q=−0.01 | 1.02104978×10⁻⁵ | 1.25906452×10⁻¹³ | 9.72886130×10⁻⁸ |

네 represented case는 원래 두 10⁻⁴ 진단 기준 아래다. 최대 상대 shear 보정 |δs/s|는 약0.8714%다. 이 수치는 작은 paired abundance 효과를 해석할 때 무시할 수 있는지 별도로 확인해야 한다. |δs/H| 기준 통과가 abundance 오차 상한이나 physical detection을 제공하지는 않는다. 모든 극값은 저장된 native nodes 위의 극값이고 연속시간 supremum 증명이 아니다. 전체 effective Ω_r를 massless free-streaming으로 취급한 비교 모델은 arbitrary radiation initial data와 massive species 전체에 대한 엄밀한 upper bound가 아니다.

**실제 결정:** 이 네 history의 결과만으로 새 backreaction solver를 필수 선행조건으로 만들 근거는 없다. 원래 AX11의 dt/dE/dμ refinement와 AX12의 f_esc·초기온도 민감도를 먼저 수행한다. 기존 PR374가 얻은 fixed-a와 equal-proper-time abundance 차이는 재사용하며, 이번 성과로 중복 계산하지 않는다. 새로운 +0.01 endpoint가 승인된 경우의 증분 결과는 별도 파일로 네 case의 고정 검토본과 구분한다.

독립 reviewer는 다른 초기각 좌표, long-double proper-time 적분과 원본 −0.01 전체312,238행으로 검산했다. 총 shear 극값 차이는 1.064×10⁻¹⁷이다. production의 10개 테스트와 independent 계산을 보존했다. pandas 기본 parser가 미소 고정소수점 H를 잘못 읽던 실제 실패를 검출해 round-trip parsing으로 수정했고 원본 값이나 허용오차는 변경하지 않았다. 자세한 유도·검산·해시는 `approximation_validity/`에 있다.

## 저장소별 소비 경계

| 저장소 | 원래 IGM에 대한 소유권 | 이번 소비·수정 | 다음 행동의 조건 |
|---|---|---|---|
| rei_bianchi | scenario, IC, geometry 선택, 결합 history, 최종 scientific admission | 원본 결과와 새 stress 진단의 통합; +0.01 복구 | AX08 완료 후 AX11, AX12 |
| bass | 같은 scenario의 proper clock·geometry·photon characteristic interface | 기존 geometry/clock 결과 재사용, Type-II/HYREC 결과를 AXBI로 대체하지 않음 | 원래 source의 clock/geometry 차이가 실제 수치 gate를 막을 때 |
| vigilode | 같은 원 RHS의 오차제어·solver 효율 | 기존 native 실패·negative work-precision 보존 | AX11에서 식별한 실제 source hot path만 최적화하고 같은 정확도에서 비용 비교 |
| WU088_HH | 선택된 종의 reaction rates·threshold·stoichiometry·유효범위 | 원 H/He provider와 source/clock 불일치 판정 재사용 | named AXBI source row나 rate 오차가 있을 때 |
| rec_bianchi | recombination/opacity·proper-electron collision·Thomson 연산자 | PR200 물리 tetrad·차수4 quadrature 교정 | source-matched 소비자의 실제 요청; optional sky가 abundance를 막지 않음 |
| BASS_HE | source가 요청한 열화·에너지 분배 | PR155 escaped photon energy guard 교정 | baseline은 primary-only Case-A; F05 OTS를 추가 source로 넣지 않음 |
| bass_cr | 지정된 spectrum·clock·transport의 외부 CR source | CR OFF를 명시적으로 소비 | AX12 이후 별도로 선택한 CR 시나리오에 입력이 있을 때 |

F05 material quadrature, F08 constant-H S0, 원래 AXBI는 서로 다른 모델이다. F05 Hmean=2.2532997324×10⁻¹⁷/s와 F08 10⁻¹⁴/s는 약443.7936배 다르다. 46,080개 material node를 공간 cell로 읽거나 row adjacency로 수송을 만드는 것은 허용되지 않는다. F05의 He OTS heating은 그 원 RHS에 이미 포함되어 있어 재주입하면 double counting이다. CR spectrum 부재는 CR OFF baseline의 blocker가 아니다.

## 실제 수정의 수치 근거

REC의 보존 Killing label q와 tetrad 방향은 n=Aq/|Aq|이고 dΩ_n/dΩ_q=det(A)/|Aq|³다. 원 photon stock에 Jacobian이 이미 포함되어 있으므로 local intensity는 N_q/J로 환산해야 한다. l≤2 intensity의 quadrupole에는 degree4 angular moments가 필요하다. 수정된 동일 F08 source의 peak photon P/scattered-in은 5.67473765937×10⁻⁶이며 기존 잘못된 frame 값3.80254×10⁻⁷과 다르다. 독립640stage·1,280tensor·81,920row 검산과 physical9tests가 통과했다. arbitrary high multipoles의 continuum convergence, multiple scattering 또는 CMB observation을 증명하지 않는다.

HE guard는 N_escaped[photons]를 Eα×1.602176634×10⁻¹²[erg/eV]로 변환해 energy interval의 양 끝점과 비교한다. 원92,160행의 독립 표현 검산은 최대 상대차1.06×10⁻¹⁵다. 공통0하한만으로 interval intersection이 통과하던 오류를 수정했다. 원 IVP와 published physical totals를 바꾸지 않았다.

## 개발 지연에 대한 적대적 판정

문제는 단순히 계산 시간이 긴 것만이 아니다. (i) 사용자의 원래 목표가 expansion DAG에서 빠져 있었고, (ii) 서로 다른 source의 어려운 조건이 중앙의 선행조건으로 전이되었으며, (iii) donor 결과의 제출이 owner 소비와 완료 결정으로 이어지지 않았고, (iv) 실패·예산 문서가 그 다음 최소 실행을 정하는 대신 같은 감사의 입력으로 반복되었다. 원 REI PR129 이후 census의244개 open/draft는 그 현상을 나타내지만, PR이 draft라는 사실 자체가 과학적 무가치함의 증명은 아니다.

이번 교정은 실제 source에 새로운 결과를 내는 작업과 정확성을 지키는 유지보수, 재사용·유예 결정을 분리한다. 새 proposal을 만들 때 중앙의 어느 입력·함수·history·관측량이 그것을 소비하는지 지정한다. 지정할 수 없으면 이번 경로에서 배정하지 않는다. 기존 결과의 복제, 동일 실패 재문서화, plot 재생성, 관찰대상 시나리오를 바꾸는 연산은 AX 진행으로 세지 않는다. 이를 위한 작은 per-turn watchdog는 `DRIFT_WATCHDOG.json`이며, 새로운 승인 gate나 문서 생산 단계가 아니다.

다음 scientific acceptance는 endpoint와 같은-grid 재현만으로 닫지 않는다. AX11은 원 계약의 baseline+최소 두 refinement 수준, dt/dE/dμ 분리, fixed-a 및 equal-proper-time 비교, 원 fractions/temperature floors와 paired-effect resolution을 요구한다. 원본에 없는 전역 Volterra theorem을 추가하지 않는다. AX12는 FESC_025와 TGAS20K를 유지한다. 실험 비용은 실제 현재 기계의 관측에 근거해 배정하며 이전 unknown 비용을0으로 초기화하지 않는다.

## 조사 범위와 미완료 사항

7개 repo의 전체 remote heads 2,062개를 enumeration했고, 2026-10-28 이후 PR metadata와 선택한 최신 source·계약·코드·결과를 검토했다. 전체 역사 파일 내용이나 모든 private 대화와 모든 Library 파일을 완전 열람했다고 주장하지 않는다. Library 최근 목록에는 traversal-limit가 있었고, targeted exact-name 검색과 실제 백업 byte 검증을 함께 사용했다. 원 네 history의 source-full ZIP SHA256 c8efb1dbde8c51c7356013ad346e97bb0223b64d8a387844d46779d380d7510d를 확인했다. 세부 scope와 source pins는 `census/`에 있다.

원래 물리 목표 전체, AX11/AX12, production solver 자격, observational calibration, optional observer tail는 완료하지 않았다. 새 결과의 status는 derived / numerically checked / implementation-verified / independently reviewed의 각 범위를 파일별로 명시한다. `GOAL_DAG.json`과 `CURRENT_OUTCOME.json`이 현재 진척을 결정하며 기존28/88 expansion count를 대신 계산하지 않는다.
