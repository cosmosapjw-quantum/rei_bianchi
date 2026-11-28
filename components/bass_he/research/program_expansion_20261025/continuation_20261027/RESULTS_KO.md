# HE-EXP-DRIFT-02: 동일 충돌법칙의 유한 드리프트 가열과 실제 공급자 연결

**현재 전달 상태:** 과학·구현 검증과 소스 ZIP 이중백업은 완료했다. 작업 공간 초기화 뒤 Dropbox의 정확한 ZIP으로179개 파일과 원 실행기록을 복구했다. GitHub 게시 호출은 재개 전후2회 모두 승인 계층에서 거절됐으며 사유는 제공되지 않았다. 로컬 소스·중앙88노드 중4개 관찰의12파일 변경안은 독립 검토 완료 상태다. 실제 게시를 완료했다고 표시하지 않으며 `delivery/PUBLICATION.json`, `BACKUP_ACK.json`, `RECOVERY_INVENTORY.json`에 확인 범위를 기록했다.

## 이번에 얻은 결과

고정 인계 `c456b05e0f1c53faa3ae36720826f43e57c06a91`을 읽고 실제 확장 HEAD `ac6042a6b0610b09d0576538767ee0299389a5eb`까지의 완료 결과를 재사용했다. 새 결과는 서로 다른 두 탄성 종의 **선형 운동량 교환과 2차 드리프트 가열을 같은 충돌법칙에서 유도한 조건부 구현**, 실제 WU 종·상태 92개에 대한 소비자 투영, 선택된 중성 H1/He4의 질량 환산, 그리고 H–He 충돌적분의 한 점 일관성 진단이다. 물리적 전종 공급자 완성이나 production 승인이 아니다.

새 검사 24개가 한 process에서 PASS했다. 측정 CPU는 0.14653116 s, wall은 0.14577179600019008 s이며 사전에 고정한 새 한도 4 CPU/15 wall s 안에 들었다. repair 0, overshoot 0이다. 실행 전 독립 검토에서 identity/기록 경계/수치 표현성 문제를 교정했다. 실행 원문은 `evidence/validation/01_tests/`, 실제 코드 해시는 `sources/TESTED_DEPENDENCIES_01.json`과 START/FINISH에 연결되어 있다. 준비·모델·네트워크·IO의 전체 비용은 미관측이며 0으로 세지 않는다.

## 1. 전종 입력의 실제 범위

WU 현행 HEAD `87933da5654bb2e4d93f7de4341df5e0fa0f8716`의 R1/R2 원전 17개 파일을 Git blob 및 SHA256으로 고정했다. 기계적 source/hash/관계 검사 340개가 통과했고 CPU 0.038832042 s, wall 0.038856827 s를 별도로 기록했다. WU의 과거 249-check compiler나 과학 suite는 재실행하지 않았다.

| 원전 역할 | 종·상태 ID 수 | 소비자 해석 |
|---|---:|---|
| Atomic | 70 | 전하 상태와 원전의 resolved/aggregate population을 보존 |
| Molecular | 17 | H2, p/o-H2, H2+, H3+, HeH+, HD J0…8, Li6H1/Li7H1 |
| Neutron | 1 | 핵반응 daughter와 중성자 충돌 의무를 별도로 유지 |
| Anion | 1 | 원전 H− 후보; 다른 음이온의 완전성 주장은 없음 |
| Electron | 3 | thermal/fast/source-pool-unresolved 의미를 합치지 않음 |
| 합계 | **92** | 동시에 독립 진화시킬 population 92개라는 뜻은 아님 |

검증 당시 R1/R2 snapshot은 공급자 variant 128개, 사건 참조 column 149개다. R2는 기존 종 9개를 재사용하고 새 종을 추가하지 않았다. 게시 직전 최신 WU `80c0d758a5d5b3c030b20c874b8e1852fcb46f82`의 R3를 별도 overlay로 반영했다. R3는 He4(gamma,d)D의 EXFOR 공급자 4개와 원 수치 36행(24 SIG, 12 CM angular DA)을 추가했다. 따라서 현재는 **92개 종 ID, 132 variants, 기존 149 event columns, 원래 19 target/28 direction 모두의 primary source reference**다. 보조 E2 7행은 36행에 더하지 않는다. 원래의27/28 snapshot은 역사적 근거로 보존한다. 이 갱신에는 원전8파일의 identity와21개 관계 검사를 사용했으며 과학 계산은 반복하지 않았다. 12 angular points를 전체 event-normalized DCS/joint law로 넓히지 않는다. 동일 D counting, beam response, state, covariance와 MeV photon consumer 결속은 여전히 필요하다.

기존 HE fixture 32개의 `ground/free/synthetic` 표기를 새 원전의 상세 state ID로 자동 alias하지 않는다. 특히 aggregate와 resolved level을 partition map 없이 함께 진화시키지 않는다. C12/C13/C12m/C12C13 synthetic 확장을 실제 공급자로 바꾸지 않는다. 핵 카탈로그 5,843행은 확장 가능한 별도 자료이며 현재 92개에 활성 non-ground nuclear isomer는 없다. 전체 ID와 다음 의무는 `sources/CONSUMER_PROJECTION.json` 및 `ALL_SPECIES_SUPPLIER_PLAN_KO.md`에 있다.

REC의 HD adapter(9 levels/8 lines/2 colliders/18 pairs/54 rates, T=50/100/200 K)와 H5 결과는 재사용한다. 35 Hz bridge의 1 pass/7 fail과 physical 0/313을 보존한다. CR의 He4 RR/external source는 이미 완료된 stationary-heavy-target/recoil=0 범위로 재사용한다. fast E, 내부 I, photon E+I의 소유권을 유지하며 일반 finite recoil을 완료했다고 바꾸지 않는다.

## 2. 같은 사건에서 운동량과 종별 가열을 얻기

두 종의 질량비를 a=m_a/M, b=m_b/M, M=m_a+m_b, μ=m_am_b/M로 놓는다. 각 종은 자체 온도와 평균속도를 가진 Maxwell 분포이며 U=u_a−u_b다. 상대 온도와 분산은 T*=bT_a+aT_b, s²=k_B T*/μ이고 β=μ(T_a−T_b)/(M T*)다.

기존에 검증한 K=(4/3)n_a n_b μ sqrt(8k_B T*/(πμ)) Q11, G=3k_B K/M을 그대로 사용한다. r=Q12/Q11이면 새 Taylor 결과는 다음과 같다.

```text
R_a = −K U + O(|U|³),                 R_b = −R_a
Q_a = G(T_b−T_a) + K[b+β(5/2−3r)]|U|² + O(|U|⁴)
Q_b = G(T_a−T_b) + K[a−β(5/2−3r)]|U|² + O(|U|⁴)
```

여기서 Q_s는 각 종의 평균속도에 대해 중심화한 열원이다. raw kinetic source는 E_s=Q_s+u_s·R_s다. 절단한 구현 안에서 Q_a+Q_b=K|U|²=−U·R_a이고 E_a+E_b=0이다. **K|U|²는 두 열원에 이미 한 번 배분되어 있으므로 다시 heat에 더하지 않는다.** 같은 온도에서는 질량비 b:a로 마찰열을 나눈다. 다른 온도에서는 한 종의 2차 보정항이 음수일 수 있어 양수로 clamp하지 않는다.

독립 유도는 Gaussian conditional expectation E[V|g]=V_c+β(g−U)와 integration by parts를 쓴다. `THEORY_KO.md`에는 정확한 기대값 식, Q11/Q12 정규화, 근사 차수 및 검증용 다항식 해가 있다. σ1=Λ/g에서는 모든 U에 대한 정확해를, σ1=Λg에서는 O(U³) force와 O(U⁴) heat 잔차 및 U를 절반으로 줄인 1/8·1/16 scaling을 비교했다. cutoff |U|/s<η는 실행 도메인 선언이며 실제 source의 remainder bound를 보증하지 않는다.

열용량은 고정된 독립 population 좌표에서 열에너지를 T로 미분한 C_V다. 입자수는 별도 n_th이며 이 탄성 사건의 Γ_th는 0이다. 코드에서는 종마다 기존 monatomic caloric adapter를 호출하고, n=0인 종에 온도를 만들지 않는다. binding/internal/nonthermal energy source는 이 사건에서 0이다. 이 결과만으로 분자의 내부 자유도를 3k_B/2에 흡수하거나, 비열적 birth를 즉시 thermal particle/heat로 바꾸지 않는다.

## 3. 실제 H–He 원전의 한 점에서 발견한 불일치

Bruno et al., Phys. Plasmas 17, 112315 (2010), DOI https://doi.org/10.1063/1.3495980 의 정규화와 기존 HE34/PR102 frozen fit를 사용한다. source T*=50–50,000 K 범위 중 **기존 HE34 선택점 20,000 K 하나**를 사용했다. 저장된 Q11을 재사용하고 새 Q12 및 Q11의 log-temperature 미분만 추가 진단했다. 원 C++ quotient 표현의 60자리 Decimal 미분을 독립 oracle로 사용했다.

| 양 | 결과 |
|---|---:|
| 저장 Q11 [m²] | 2.8378312527861555×10⁻²⁰ |
| 현재 원 evaluator와 저장 Q11의 상대 차이 | 0 |
| Q12 [m²] | 2.229085677933474×10⁻²⁰ |
| Q12/Q11 | 0.7854891568147256 |
| dQ11/dlnT [m²] | −1.797615401645635×10⁻²⁰ |
| dlnQ11/dlnT | −0.6334468971263719 |
| D=dlnQ11/dlnT−3(Q12/Q11−1) | **0.010085632429451152** |

온도에 명시적으로 의존하지 않는 동일 σ1(g)에서 정확히 계산한 두 적분은 T dQ11/dT=3(Q12−Q11)을 만족한다. 고정된 독립 fit 두 행은 이 선택점에서 그 항등식을 정확히 만족하지 않는다. 따라서 row-based 가열과 derivative-based 가열의 차이는 a종에서 +KβD|U|², b종에서 그 음수다. 이것은 **두 근사 표현의 내부 일관성 진단**이다. 원전의 calibrated uncertainty, 전체 상대 물리 오차, H–He 충돌의 불가능성을 뜻하지 않는다. β=0인 같은 온도에서는 이 2차 partition 차이가 사라지지만 전 도메인의 정확성을 증명하지 않는다.

다음 구성적 전이는 선택한 고정 potential에서 같은 σ1와 quadrature로 두 적분을 공급하거나, 공분산과 오차가 명시된 공통 fit를 제공하는 것이다. 이때 angular σ2/stress 및 완전 final-state law는 따로 필요한 입력이다. Debye screening처럼 law 자체가 T에 의존하는 경우 위 미분에는 추가 항이 필요하다. 이번 식을 그대로 확장하지 않는다.

## 4. 중성 H1/He4 질량의 실제 환산

NIST의 AME2012 기반 원자질량 표(데이터 January 2015)에서 H1 Ar=1.00782503223(9), He4 Ar=4.00260325413(6)를 읽었다. 단위는 CODATA 2022의 m_u=1.66053906892×10⁻²⁷ kg를 썼다. 서로 다른 자료 vintage를 명시했고 원자질량과 단위상수 사이 공분산을 가정하지 않았다. 출처 URL은 `sources/NEUTRAL_H1_HE4_MASS_CANDIDATES.json`에 있다.

| WU species ID | 고정 상태 | Ar×m_u [kg], quoted-field product |
|---|---|---:|
| sp_7b3d2e472131e6c645d7 | H1 neutral, 1s_ground | 1.6735328406534731912916×10⁻²⁷ |
| sp_17efcd73203997543678 | He4 neutral, electronic_ground | 6.6464790808691923446396×10⁻²⁷ |

표의 긴 자릿수는 입력 십진수의 정확한 곱을 기록한 것이며 측정 정확도의 자릿수가 아니다. m_u·u(Ar)와 Ar·u(m_u)는 별도로 기록한다. 결합 표준불확실도와 cross-isotope covariance는 null이다. neutral atomic mass를 bare nucleus나 excited state에 대입하지 않고, 결합에너지를 질량에 다시 더하지 않는다. 이 질량 입력으로 transport isotope accuracy가 확보되는 것도 아니다. 고전적인 고정 potential 모델의 질량 의존성을 분리한 조건부 연결만 가능하다.

원본 HTTPS 세 요청의 HTTP403을 보존했다. NIST 필드는 primary web text에서 전사한 것으로, 원본 HTTP bytes/SHA256를 취득했다고 주장하지 않는다.

## 5. 유지한 과거 결과와 다음 의무

HE101 owner HEAD는 `28a26f4db951ab9085180e2ecc5d600d981a1f71`이며 C8 `PARTIAL_EXPORT`, 전달 19/20, repair reserve 0을 유지했다. 원 PASS/FAIL/FAIL, exit 0/−9/−9, 개별 CPU overshoot와 미관측 kill cause를 보존한다. HE101 science CPU 11.882829/wall 11.985978921002243 s, lineage CPU 16.870803/wall 17.108468335994985 s를 새 예산으로 초기화하지 않았다. HE101 science/plot/export START는 0이다.

INTAKE01의 31 distinct methods/36 executions와 원 FAIL/repair 기록, CPU 0.282464889/wall 0.280453644998488 s도 그대로다. 소진된 배정의 남은 시간을 물리 campaign으로 옮기지 않았다. 과거 네 source/delivery ZIP은 이번 turn에서 두 provider의 ID/size metadata가 기존 영수증과 일치함을 확인했으며 원격 전체 ZIP 재다운로드 검증과 구분했다.

다음 물리 단계는 source-compatible moments와 calibrated uncertainty, isotope/state model validity, 선택된 inelastic joint law와 finite recoil, channel-qualified thermalization/deposition, common-T/u reduction의 시간척도·관측량 오차를 필요로 한다. 각 선택 채널의 의존성만 적용하고 전종 완성을 한 쌍 진행의 선행조건으로 만들지 않는다. 현재 `physical_provider_admitted=false`, `production=NOT_APPROVED`, `activation=false`, physical allocation `UNALLOCATED`, global physical completion `null`, L4 `false`다.

게시·백업의 실제 완료 상태는 `delivery/` 영수증과 최종 `RESULT.json`을 따른다. 소스 snapshot의 delivery pending 상태는 역사적 기록으로 남기고 후속 metadata overlay와 구분한다.
