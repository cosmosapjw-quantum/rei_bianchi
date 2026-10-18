# REC → REI FLRW production 입력 조사 (2026-10-15)

현재 사용 가능한 최소 delta는 **REC PR94의 REI 우주론에 맞춘 원본 HyRec FULL zbar=20 반환을 새 REI q=0 초기상태에 연결하는 것**이다. REC 전체 브랜치를 병합하거나 미완성 Python FULL history를 기다릴 필요는 없다. 이번에는 저장된 원본 코드·반환·검산 영수증을 읽었으며 수치실행, 재검산, git 변경은 하지 않았다.

## 고정 원본과 수신 일치

| 항목 | 확인값 |
|---|---|
| 저장소 | cosmosapjw-quantum/rec_bianchi |
| 현재 main | 5a09f3797210284f83a1a1adb0e0092d1ac48475 |
| 선택 branch | research/rec-r3c-rei-bridge-20261015 |
| 선택 commit | 8071d2e26d1befe2efe4599c5abd416d90e5e031 |
| tree | 95a21d2c4ab1fbb72898bd64d5109f37441b05b7 |
| 직접 부모 | 2c4627bf480a306f34bb35d0ec5a3d18182b170e |
| 공개 반환 | [PR94](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/94), open |
| 원본 HyRec ZIP SHA256 | 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27 |
| 실제 C stdout SHA256 | 6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400 |
| REI scenario SHA256 | 07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696 |

수신 repo의 `research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json`을 실제 읽고 SHA256을 계산했다. PR94의 source binding과 **byte-exact 일치**한다. main의 오래된 August HANDOFF는 이 반환의 최신상태가 아니다. 검색 범위는 112 branches, 최근 갱신 PR 30개, 선택 commit 전체 recursive tree 2750개이며 tree truncated=false였다.

주요 실제 읽은 경로는 `research/rec_r3c_rei_bridge_20261015/` 아래의 `REI_DONOR_CANDIDATE_OPTIN_ONLY.json`, `REI_CONDITIONAL_BOUNDARY.json`, `SOURCE_EXECUTION_RECEIPT.json`, `TEST_RECEIPT.json`, `NEXT_LOOP.json`, `REPORT_KO.md`, history CSV와 구현 `src/full_bianchi_hyrec/trajectory/rei_initial_boundary.py`이다. 정확한 URL·git blob·내용 SHA256은 `rec_intake.json`에 있다. 소비에 필요한 네 JSON 원본을 `rec_public_return/`에 내용 그대로 저장했다.

## 바로 소비 가능한 값과 규약

| 수량 | 고정 값 / 의미 |
|---|---|
| h, Omega_m, Omega_r | .674, .315, .000092 |
| Omega_b h², YHe, Tcmb0 | .0224, .2454, 2.7255 K |
| source effective massless Neff | 3.03821934419124; 총 radiation H(z) 일치용이며 관측 neutrino 추정이 아님 |
| 초기 zbar | 20; a_ref=1/21 |
| source xe=ne/nH | 0.000210349192936 |
| Tgas | 9.306042400380866 K |
| 선택 projection | xHII=xe, xHeII=xHeIII=0 |
| 원래 baseline | xHII=.0002, Tgas=8.098143045064857 K |
| clock | zbar=a^-1−1, 각 z20 면부터 경과한 proper seconds |
| 초기 ionizing photon stock | 선택한 astrophysical source-onset 조건의 정확한 0 |

원본 HyRec stdout 세 번째 열은 **Tm/[T0(1+z)]**다. 반환 JSON 및 CSV의 Tgas_K는 이미 Kelvin이므로 다시 T0(1+z)를 곱하면 안 된다. HyRec-2는 Kelvin 직접 출력, RECFAST1.7은 이 비교에서 Tm 반환이 없으며 서로 같은 열로 읽을 수 없다.

헬륨 값은 원본 late H-only switch에 근거한 **중성 He 조건부 투영**이다. 원본 stdout은 total xe만 제공하므로 독립 species-resolved HeII/HeIII 관측값으로 해석하지 않는다. 이 조건은 명시된 1H/4He 모델의 새 초기값 선택으로 기록할 수 있다.

수신 정규화는 그대로 유지한다. REI는 mH=mp, mHe=4mp, fHe=Y/[4(1−Y)]=.08130135170951498이다. 원본 HyRec는 fHe=Y/[3.97153(1−Y)]=.08188416223421702와 nH0=11.223846333047·omega_bh²·(1−Y) m^-3를 사용한다. z20의 nH는 source1756.970280931192 m^-3, recipient1757.9215875815148 m^-3로 source가 0.05411542% 작다. 따라서 xe/T를 recipient의 nH와 fHe에 적용하는 조건부 IC이며 완전 동일 미시물리 우주론으로 부르지 않는다.

REI 상태의 열량은 `w=(3/2) kB T(1+fHe+xe)`, **erg/H**다. source boundary의 `thermal_energy_J_m3`를 그 칸에 그대로 넣으면 안 된다. 공개 boundary는 recipient 밀도에서 u=3.6641250800852963e−19 J/m³, ne=.3697773871925435 m^-3를 계산했다. xe +5.1746%, T +14.9158%는 초기상태 차이이며 integrated tau나 이후 REI abundance 효과가 아니다.

## clock과 핵종 inventory

REC C8의 `AxisymmetricBianchiIBackground.interval_log(l1,l2)`는 L=ln(a/a_ref)로 주어진 구간을 직접 적분한다. method는 `rec_lrs_bianchi_i_positive_rate_hermite_log_interval_v1`, domain a∈[1/21,.2], 검증 mesh1024/2048이다. 반환 dt=∫dL/H>0는 seconds, db=∫s/HdL은 q0에서0이다. tiny log step을 a_ref·exp(L)로 변환한 뒤 빼면 이미 표현 가능한 구간을 잃을 수 있다. 공급자 기존 C8 영수증은17 targeted PASS,70 integration PASS/2SKIP,30개 clock 기준 최대 상대차3.907985e−14, 과거 roundtrip collapse211/256을 기록한다. 이번에 반복하지 않았다.

REI가 이미 안정적인 finite-increment 구현을 채택했다면 그것을 재사용한다. 새 연결에서는 **동일한 tentative step dt를 source·chemistry·radiation·energy ledger에 전달하는 callsite**가 핵심이다. clock 구성요소 검증을 native 전체 궤적 승인으로 승격하지 않는다. R9 오차 합성은 수정된 alpha+(1+alpha)eta_eval이며 단순 합은 아니다.

현재 SCENARIO_LOCK의 inventory는 명시적으로 selected 1H/4He aggregate다. nb=nH+4nHe, Yi=ni/nb, xe=ne/nH, Ye=ne/nb이고 electron은 nb에서 제외한다. D,T,3He,Li는 hidden tracked reservoirs가 아니라 선택 모델에서 제외됐다. **PR94는 전체 BBN nuclide inventory를 공급하지 않는다.** 추가 핵종이 필요한 새 목표는 BBN 생산자의 정확한 species/질량/정규화 반환으로 확장해야 하며 REC helium projection으로 채울 수 없다.

## 최소 구현 순서와 재사용할 근거

1. source PR94 commit, 원본 stdout SHA, boundary SHA, scenario SHA를 고정한 intake를 추가한다. 현재 사용자 생산변경 승인은 이미 있으므로 source의 과거 disabled 표기는 역사적 상태로 보존하고 별도 승인 질문을 만들지 않는다. 새로운 run ID와 source identity를 만든다.
2. 기존 baseline checkpoint를 재개하면서 IC를 바꾸지 않고 **fresh z20 q0 상태**를 생성한다. donor xe/T, recipient nH/fHe, MD14/BB50K, 초기 ionizing0을 함께 고정한다. native 초기 charge/baryon/thermal ledger와 온도 역변환만 새 연결 경계에서 확인한다.
3. 기존 finite clock 증거를 재사용하면서 새 native callsite의 dt 일관성을 확인한다. 공급자 검산 및 원본 HyRec 3개 history를 다시 실행하지 않는다.
4. 승인된 q0 production trajectory를 durable checkpoint와 함께 끝까지 진행하고 species·T·elapsed proper time·z20→4 tau segment 및 refinement를 보고한다. baseline은 비교용으로 보존한다.
5. 이후 signed-q를 사용한다면 같은 q0 IC의 조건부 민감도 비교다. z20→4 처방을 recombination으로 역외삽해 primordial anisotropic history라고 부르지 않는다.

실제 읽은 source 영수증은 unchanged original HyRec H+He FULL z8000→0 8001행, central 및 YHe±.002의3사례, targeted7PASS, 전체474PASS/41SKIP를 기록한다. 이번 조사에서는 영수증과 구현을 재사용했고 gzip을 새로 내려받아 재검산하거나 원본 C를 재실행하지 않았다. PR91의 독립 H-only HMLA z1600→600과 PR93의 제조 accepted-history 순간 FULL step은 각각 유효한 별도 범위이며 PR94 z20 반환을 대체하지 않는다. PR90/91 우주론 h=.6735837,YHe=.245,Neff3.0은 이번 수신 우주론과 다르다.

Library에서는 PR94보다 최신의 해당 반환 또는 nuclide inventory가 해소되지 않았다. 이는 미존재 증명이 아니며 현재 GitHub PR94의 직접 읽은 원본을 우선한다. 별도 `rec_library_intake.json`에 실제 읽은 5문서와 탐색 한계를 기록했다.
