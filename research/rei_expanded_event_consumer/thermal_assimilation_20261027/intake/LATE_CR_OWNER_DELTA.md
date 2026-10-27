# 늦게 도착한 CR owner R04 입력 — 현재 REI 단위와의 관계

**판정: 현재 동결한 REI-THERMAL-ASSIMILATION-20261027을 막는 중복은 없다.** 새 CR producer의 고유 작업 범위를 예약된 작업으로 보존한다. 이 checkpoint는 현재의 조건부 ν를 교체할 실제 유한시간 thermal assimilation 공급자가 아니다.

## 실제로 읽은 자료

요청받은 **BASS_CR_HEIII_20261027_R04_CHECKPOINT.zip** 하나만 복구했다. R04 안에 R01–R03 문서·영수증이 누적되어 있어 이전 ZIP을 따로 받지 않았다.

- Library ID: libfile_62b90eba44bc819189122030dee08a02
- Library 생성/수정: 2026-10-27T03:23:35.488022+00:00
- 실제 크기: **48,241 bytes**
- SHA256: **224b0f2997af3aadba28583f9f0af99338c99fc591c83ce96c7f5514f25c577e**
- 20 archive entries. README, LOOP_LEDGER, R01/R03/R04, source map/qualification, checkpoint authority, R03 receipt를 실제 읽었다.
- 위 9개 원문은 intake/late_cr_r04/에 그대로 보존했다. Source pins와 예산·범위는 LATE_CR_OWNER_DELTA.json에 있다.

Archive의 권한 표시는 repository cosmosapjw-quantum/bass_cr, branch **research/cr-heiii-ground-rr-20261027**, checkpoint commit **79ee44590f5f59f874d10e85cec411c17655dec4**, expected parent **d69b6775ca9a4cde60c8eb5503f095094bad9189**, force=false다. 이번 조사는 요청된 R04만 읽었으며 이 branch의 이후 live HEAD·실행은 재조회하지 않았다.

R04 ledger는 R01–R04 이론 준비 4단계 완료, 해당 수치 consumer **0/1**을 기록한다. 이후 단계의 실행·성공은 이 파일로 관측되지 않는다.

## 새 producer의 정확한 작업

Unit: **CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1**

반응은 **He4²⁺ + tagged nonthermal electron → He4⁺(1s) + spontaneous retained photon**이다. 기존 PR106의 실제 저장 HeI K_diag를 baseline으로 사용하고 새 HeIII ground-RR diagonal hazard만 추가한다. 이전 H1·HeI 행렬이나 source projection을 재생하지 않는다.

- 이전 science: 4caf4273eefd51f2c605a8667c3533d8489dd0f5
- 이전 documents: b11b2e9255f2b10fb5582376412e045bd1e9151c
- 고정 bath: T=10,000 K, thermal ne=0.14 cm⁻³, n_HeIII=0.01 cm⁻³, lnΛ=20
- 기존 3개 z source와 8개 저장 grid
- Native HeII PI threshold54.42 eV, photon Emax50,000 eV, d=1
- Elemental He→He4 조건부 대응, stationary-heavy-target, zero recoil, 실제 소비 grid에서의 nonrelativistic 해석
- Pointwise 조건 E>0와 E+54.42≤50,000 eV 외에 **기존 consumer grid 범위를 함께 유지**한다. Source 표의 50 keV 상한은 전체 수송 정확도 인증이 아니다.

정확한 table/provider/REI151 contract pin 세 개가 metadata에 보존되어 있다. 핵심 table SHA256은 a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389, provider SHA256은 71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d다. 이 문서는 owner가 읽은 원전·Milne 식을 보고하는 것으로, 우리가 별도 새 문헌 검증을 수행했다는 뜻은 아니다.

## 예약과 예산

계획은 case당 18 physical + 5 conditional-time + 4 stable-response + 1 diagnostic, 총 **8×28=224개의 새 선형 RHS**다. 독립 Decimal70 own-column 검토도 그 producer 작업에 속한다.

새 단위 cap은 **30 CPU s**, native thread1, worker address-space512 MiB, memory reserve1 GiB다. R04는 상세 실행 예약이 실행 전에 정해진다고 명시한다. **현재 실제 사용량·남은 예산·구체적인 실행 lease는 R04에 없어 null/미관측으로 보존한다.** Cap30을 remaining30으로 바꾸지 않는다. 이 예산을 REI의 cap이나 과거 CR 잔여량으로 옮기지 않는다.

이 8-case HeIII-on-HeI chain 구현·계산·독립 비교를 우리 작업에서 복제하지 않는다. R04 이후 owner의 live progress도 추정하지 않는다.

## 우리 단위와 다른 점

| 항목 | 새 CR R04 producer | 현재 REI 동결 단위 |
|---|---|---|
| 소비자 | 고정 bath의 tagged-electron killed finite chains | 실제 PW19 HeII endpoint + 명시적 constructed fast moments |
| 새 과정 | 비열적 electron의 ground RR 포획 | 조건부 energy-independent fast→thermal 편입, thermal RR/DR/Compton |
| thermal electron count | 이 RR 사건에서 변화0 | 편입에서 +j; thermal RR/DR에서 q·R |
| photon owner | retained photon 별도 output port | photo/Compton/thermal RR escape의 명시적 signed external ledger |
| export 차원 | pulse-integrated m⁻³와 J m⁻³ | proper-time source 및 그 JVP |
| source rate/exposure | export에 미제공, null | 선택 source와 ν가 명시된 s⁻¹ source |

CR 계약은 He4III index12→He4II index11, fast count−1을 함께 사용한다. 따라서 Δg=q·ΔY−Δzeta=0이며 thermal particle count도 변하지 않는다. **Q_thermal=0, Δw_ext=0**으로 두고, 방출 retained photon count/energy를 별도로 반환한다. 이는 thermal electron을 하나 늘리고 에너지를 bath에 넣는 우리 assimilation event와 다르다.

새 ground-RR component는 향후 비열적 capture 경로의 공급 후보가 될 수 있다. 그러나 R04에는 검증된 새 수치 결과가 없고, pulse-integrated 출력을 즉시 s⁻¹ RHS로 넣을 수 없다. Rate/exposure, 실제 소비 상태·분포, 해당 photon owner와 경쟁 연산자를 별도로 결속해야 한다. 기존 total thermal RR에 이 ground component를 같은 thermal pool의 추가 항으로 중복 합산하지 않는다.

## 현재 행동

현재 root-frozen 계약의 수정이나 재동결을 요구할 과학적 충돌은 발견하지 않았다. **이 producer를 별도 active owner로 기록하고, 기존 prebackup/GO 이후 우리의 승인된 bounded checker를 진행할 수 있다.** 실제 stopping ν가 이 파일명이나 Milne capture formula에서 공급됐다고 해석하지 않는다.

이 read-only intake의 producer import·과학 계산·테스트·IVP·NCP·원격 게시 실행은 모두0이다. 복구/독해 CPU·wall은 미계측 null이다. 원 DAG 변화0, working32/88·central27/88 및 L4=false를 유지한다. V6의 새 Drive delivery 완료는 root의 별도 LATE_PARALLEL_RETURNS.json에 기록된 운영상 갱신이며, V6 과학 archive와 Git no-ACK 판단을 바꾸지 않는다.

