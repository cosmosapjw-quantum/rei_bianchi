# REI IGM Physical Fast F05 | 승인된 원본 네 시점의 26-event 반응·열원과 실제 이력 변화량

2026-11-02, 원본 소스 기반 한정 물리 연구. 소유자: cosmosapjw-quantum/rei_bianchi. 원본 parent PR365 HEAD fab9429140038974a98f3ad3212036b0227e600e. 기존 source/solver/V1 policy/accepted tick/history/main 미변경. 새 canonical node 미승인.

## 원본과 수행 범위

REI 원본 46,080셀, 네 역사적 승인 시점 0/64/128/160, 26-event H/He 이온화·재결합/OTS/열역학, 4-group 원본 UV photon owner. 원본 봉인 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644, 원본 source TAR a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, 정책 V1 c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9. 원본 tick64 state aae4607ec..., tick128 bbb349102..., tick160 74c7cbb78... 모두 실제 local source 및 역사적 SHA와 일치함. 원본 REC PR195 184,320개 이력 데이터 SHA256 6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c. BASS_HE PR150 동일 tick160 46,080셀 원본 9-event/6 OTS branch donor SHA256 f0aba50cf048499ecaed4642b050d2e4c76de9fbe6a77be5d3cc9a3f39ee641c.

원본 부호/차원: (-,+,+,+), proper source time s, 광자·충돌 이온화 사건/s, 화학 Bdot·열 Udot erg/s. 전자수 N_e=N_HII+N_HeII+2N_HeIII, binding B=EV[chi_H*N_HII+chi_HeI*(N_HeII+N_HeIII)+chi_HeII*N_HeIII], gas U=3k_B(N_H+N_He+N_e)T/2. 열에너지율은 실제 원본 floating_reference_rhs와 동일 모델 thermal RHS를 독립 교차 평가함.

## 실제 새 원본 물리 데이터

4 원본 시점 × 46,080 H/He/OTS 셀 = **184,320개** 원본 source RHS 행, 단 하나의 우주 물리 데이터셋의 네 시점. 계산 source code: research/rei_f05_owner_accepted_trajectory_rhs_20261102/compute_original_source_rhs.py. 비공개 source-inclusive 원본 결과 ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz SHA256 **5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913** (34,110,925 bytes). Git 공개 aggregate JSON ORIGINAL_F05_4EPOCH_RHS_SCIENCE.json SHA256 **759b3b265bfbe540bcca28fe8fa51c06177256c825c3d10bb3541d44c703d351**.

| Original tick | Bdot net (10^39 erg/s) | gas Udot net (10^39 erg/s) | OTS chemical (10^39 erg/s) | primary photoheat (10^37 erg/s) | cooling + expansion (10^39 erg/s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | -8.0985186483 | -4.2986114556 | -8.3269254864 | +5.4485344651 | +4.3547515790 |
| 64 | -7.9008763419 | -5.1321678689 | -8.2695669820 | +6.5827979363 | +5.1994786514 |
| 128 | -7.7564968306 | -5.8997280841 | -8.2503004363 | +7.6905974863 | +5.9780696424 |
| 160 | -7.6931379466 | -6.2580308331 | -8.2446274302 | +8.2271327493 | +6.3417241962 |

화학적 이온화 binding reservoir의 원본 순간 방출률 절댓값은 감소하는 반면, 기체 순 Udot 감소율의 절댓값은 증가한다. 보존되는 화학/열 에너지 장부는 다른 물리적 기작을 측정하며, OTS의 unresolved term 약 8e39 erg/s를 실제 탈출 photon sky나 가스에 즉시 흡수된 열이라고 오해할 수 없다. 원본 resolved photoheat는 수치적으로 늘지만 cooling+expansion의 증가를 상쇄하지 못한다. 이 마지막 설명은 원본의 선택한 물리 점에서는 성립하는 것일 뿐, 추가 흡수/외부 CMB bath를 포함한 해나 관측 예측이 아니다.

## 원본 승인 구간의 finite secant 대조

REC PR195가 실제 원본 26-event full/half/half 재생으로 얻은 \Delta B/\Delta t와 \Delta U/\Delta t를 그대로 재사용한다. 다음 수치는 모두 10^39 erg/s 단위.

| source accepted interval | B source secant | B end-point trapezoid | U source secant | U end-point trapezoid |
| --- | --- | ---: | --- | ---: |
| [0,64] | [-7.981976,-7.970627] | **-7.999697 (outside)** | [-4.724647,-4.695860] | -4.715390 (inside) |
| [64,128] | [-7.833221,-7.797323] | -7.828687 (inside) | [-5.568991,-5.458258] | -5.515948 (inside) |
| [128,160] | [-7.774009,-7.661650] | -7.724817 (inside) | [-6.299891,-5.846375] | -6.078879 (inside) |

중요한 negative witness: 처음 [0,64]의 B end-point trapezoid는 승인된 원본 source secant 구간 밖이다. 따라서 '원본 source RHS와 실제 구간 상태의 모든 사다리꼴 평균이 같음'이라는 강한 주장은 **REFUTED**. 이는 표본 endpoint 보간, 시간의존 원본 photon forcing, 화학 비선형성 및 finite interval의 조합으로 충분히 가능하며, 그중 단일 원인이 확정된 것은 아니다. **원본 화학식 또는 역사적 상태가 틀렸다는 결론은 아니다.** 서로 다른 물리량과 계산 대상의 엄밀한 구분이 이번 새 결과이다.

## C6/C7/R6/C9 검증 및 적대적 감사

- 원본 4×46,080셀 모든 레코드의 표준 라이브러리 독립 reader가 H/He nuclei, T>0, 비음수가 아닌 재료, 시각·row order, 26-event 화학 \dot B=P_photo+P_coll+OTS_chemical, OTS chemical+heat+unresolved+escaped=0, native \dot U=\dot U_thermal 을 확인했다.
- BASS_HE PR150의 기존 46,080셀에서 Bdot/photo/collision/OTS 8개 핵심 원본 rate 채널을 **셀별 직접 교차검증**, 틀린 셀 **0**, 검증한 rate 중 최대 상대 차이 **0.0** (동일 원본 소스 식/동일 point-choice의 일치, 완전 독립 학술 재현이 아님).
- 원본 값이 아닌 과거 secant 보간 평균을 시간적분 LTE 이론으로 승격하면 FAIL: [0,64] 화학에너지 trapezoid negative witness를 그대로 보고하고 보존한다.
- 원본 26-event energy stoichiometry 최대 약 7.9e-16 scaled, OTS source residual 약 1.1e-16, thermal RHS 재구성 최대 약 7.1e-16 native producer; 원본 endpoint BASS_HE independent source 재계산 0 mismatches.
- 독립 audit JSON SHA256 8f70f56a479353d067b26bf525de5d695437edf715e0cbb11a7e5d942a5e6344; Python normal과 -O deterministic byte result identical, source JSON tamper negative test EXPECTED_REJECT.
- 원본 source runtime Python NumPy2.3.5/Pandas2.2.3/SciPy1.17.0의 pinned virtualenv 사용. 외부 예전 NumPy1 numexpr/bottleneck ABI 경고가 stderr에 발생하지만 source python 종료 코드 0. 사전 별도 PYTHONNOUSERSITE=1은 시스템 SciPy1.11로 잘못 해석하여 런타임 실패, 환경 문제로 수정함. BASS_HE original event SOURCE SHA와 전체 sealed KERNEL SHA는 서로 다른 원본인 것을 별도 구분해 source check 수정했으며, 출처를 바꾸지 않았음.
- 독립 저자 referee NOT_RUN, 동일 모델의 서로 다른 구현 경로에 의한 적대적 감사만 수행. Formal MPFR outward global enclosure NOT RUN.

## Owner R8 결정 및 드리프트 방지

**PROMOTE_FOR_SPECIFIED_USE:** 실제 원본 F05 source-conditional four-epoch 26-event RHS, source OTS chemical and gas thermal rate time trend, actual REC195 historical material secant and BASS_HE150 true 46k source readback. NOT PROMOTED: 원본 worker runtime 계약, 131072-tick continuum solution, point-sampled trapping/re-emission photon transport or versioned V2 [160,161] admission. BASS_HE150 기존 source authority를 원본 owner에서 독립 원본으로 확인했을 뿐 새 source photon 모델로 교체하지 않음. Three-lane REI PR365 = one original universe/one numerical dataset.

오리지널 F05 [160,161] V1 logT source upper 2.1245050576368385e-4 > frozen gate2e-4 remains FAIL; V2 candidate requires explicit new original versioned worker/runtime contract, 14/14 ledgers and current source and output identity, not physics-only R5/RHS comparison. No source, f, UV, OTS, clock or gate modifications. Next SINGLE canonical act: F05 current versioned V2 worker with 0→64 historical all-lane predecessors and exact physical 160→161 computation ACCEPT/REJECT. No more ancillary static source catalogues.

DAG through every stage: REI Central **28/88**, working **33/88 nonadditive**, Physical Fast **4/7**, canonical delta **0**. Production **HOLD**, no merge/force push, no tolerance relax, no original owner history modifications. Distinct author referee and native subagent NOT_RUN.
