# REI M1 원본 26-event 전역 광자 source 유한차분 연구 결과

2026-11-01 · Original science owner: cosmosapjw-quantum/rei_bianchi · Project scientific gate: **HOLD**

## 실행 및 원본 identity

- 원본 소스 immutable PR #332 HEAD `2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a`.
- 원본 첫 interval frozen 35-member archive SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; original source state array SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`.
- 실제 원본 46,080 노드의 중성종 합 `S_HI,S_HeI,S_HeII`, 네 photon groups, 외부 sink를 물리적으로 사용하는 원본 `photon_global_feedback.py`의 유효 계수·clock·forcing을 그대로 호출. 세 shape lane의 source 배열은 서로 독립적인 상태가 아니므로 추가 집계하지 않았다.
- 동일한 원본 tick160 부모 집합을 고정하고, clock begin/quarter_sdirk/half/full_sdirk/end **5개 frozen-parent source time**에서 4개 광자군을 계산: **20개 실제 source-owner group records**. 이 시간점들의 진화된 thermal 또는 population stage state를 주장하지 않는다.
- GitHub Actions 수정된 코드 scientific CI [#41282103367](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41282103367) **SUCCESS**, generic verify #41282103363 SUCCESS, source SHA lock 검사, exact Fraction normal+optimized 10/10 테스트 모두 통과. 실제 물리 원본 결과 ZIP artifact #13073556623; 3,666 bytes; SHA256 `88f7e5bb1c6c44c0ca0c7f2ef2c81ac70098cc7ed773096868b1e7b4db25c035`; ZIP CRC PASS. 결과 JSON 20 group rows.
- 기존 PR #332의 직접 source 각 군 fraction `p`와 새 원본 time begin 값의 최대 절댓값 차이 `1.1102230246251565e-16` (동일 정보가 완전히 다른 계산 루트로 전달됐음을 확인).

## 유한 비선형 항등식과 실제 결과

각 photon group g에서 `A=(C_HI S_HI,C_HeI S_HeI,C_HeII S_HeII,E_external)`, `p=A/Σ A`. 각 원본 모멘트 구간에서 유한 변화 `δA`에 대해 `η=ΣδA/ΣA0`, `L_j=δA_j/ΣA0-p0_jη`라 하면 `Δp_j=L_j/(1+η)`, `R_j=-L_jη/(1+η)`는 **정확한 대수 항등식**이다. `R_j`의 원본 물리 입력에 대한 인증 범위는 독립적인 외부 구간 enclosure로 설정했으며 exact Fraction으로 계산한 상계가 float로 출력될 때 위쪽으로 반올림되도록 했다. Wolfram exact 4-channel residual zero. 

원본 source의 `tick160`에서 가장 큰 유한 흡수 비율 변화 상계:

- `max |Δp_s|`: **0.00041688819642683153**, group `2`, species index `1` (0=HI, 1=HeI, 2=HeII).
- 동일 source family의 **정확한 1차 비선형 remainder 상계** `max |R_s|`: **3.066078028184254e-07**, group `2`, species index `1`.
- 한 tick photon absorption 변화 규모 (고정 source rate × tick) 수소 핵당 최대 **6.7534268945959144e-12**; 에너지 photon heating 변화 규모 수소 핵당 최대 **5.0053738156385012e-11 eV/H**. 이것은 시간이력 적분의 엄격한 상계가 **아니고**, 각각의 frozen-parent source 시간점에서 측정된 rate를 한 tick 길이에 곱한 sensitivity scale이다.
- 각 original original photon group에 외부 sink를 합하여 정확한 확률/광자 수 비율 보존, zero support channels는 exact 0. source-parent box의 모든 독립 모멘트 조합에 대한 외부 상계를 얻었지만 실제 원본 동역학의 상관관계를 소급 증명하지 않는다.

## 가장 중요한 과학적 한계

원래 `[160,161]` full-minus-twohalf box local error 상계 **2.1245050576368385e-4**, 엄격한 한계 **2e-4** (FAIL/HOLD). 새 결과는 그 원인을 제거하거나 첫 canonical interval을 수용시키지 않는다. 특히 다음은 **NOT_RUN**: 실제 26-event MPRK22(1) 전체 step 함수의 `J_D(X)` 및 uniform remainder, 네 source evaluation site 사이의 stage-parent transport, thermal implicit root, Hummer–Seaton event branch, correlated cross-site source variation, first-interval 전 구간 수치 인증. 실제 physical input sum interval은 핵수 constraint와 추가 상관관계를 포함하는 진짜 reachable set의 단순 outer enclosure이며, coarse overbounds가 실제 source response를 정확히 측정하는 것은 아니다.

원본 PR #332는 단일 source의 global moment Jacobian을 도출했지만 finite remainder 전역 bound까지 제공하지 않았다. 이번 결과는 이 **source 부분 연산자에 한정된** 새로운 과학적 봉합이며, 전체 D_h에 대한 다른 저차 source와 local thermal 원인까지 무시하는 소거 증명이 아니다. 추가적인 동일한 9-point atlas를 만드는 대신, 이 소스 인증을 실제 MPRK/SDIRK2 stage sensitivity에 삽입하는 것이 다음 **단일** 과학적 critical path다.

REI central **28/88**, working **33/88**, FAST **4/7**, 이번 canonical delta **0**. 원본 source·checksum·과거 실패 이력·허용오차·계산 예산 보존. `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false`, `PRODUCTION=HOLD`. Same-author 적대적 검토만 수행, distinct-author referee와 native subagent `NOT_RUN`.
