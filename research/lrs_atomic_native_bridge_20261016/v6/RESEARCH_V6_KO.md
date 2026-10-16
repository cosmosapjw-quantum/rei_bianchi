# REI-LRS V6: 온도 자기일관 midpoint 재결합 갱신의 구성과 실제 경량 검증

날짜 2026-10-16 KST. 독립 이론/코딩 연구 범위: 기존 [REI PR #158](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/158), 소스 HEAD `3006d48026b422f4c3db030638eb3091ac517734` 위에 **additive**로 적용할 시간적 결합 알고리즘. 기준 `recomb_thermal.py` 파일 SHA256 `9a21ed0ddbef826bfb7e393056e202df3d9666ea994274ab6035e84211f12433` 그대로 둔다. `PR #150` production native Rust, v3/rux, PR #154, 다른 원자/핵물리 원본 저장소, 원격 NCP 기존 작업은 수정하지 않았다.

## R2/R3: 학술·기존 코드 출처

- Grackle 3.4.1 원본 Case-A HII/HeII/HeIII RR, HeII DR 및 각 재결합 냉각. 실제 대조 전단은 PR158의 원본 Rust owner `igm_rates`, `igm_thermal`, `.1e-6 cm^-3` 등 검산을 재사용. 이 루프에서는 **기존 129행 immutable** `owner_grackle_rates_129.csv` + `rate_table.py`를 사용하고 원본 968개 비교를 재반복하지 않았다. 그 원본 출처와 물리적 인증 범위는 PR158의 `RESEARCH_V5_KO.md` 참조. 129행 donor SHA256 `33396b071c840b40ad79d68ee626de59f12bb2cf0b1df2159627efd7fde42aec`.
- [Mackey (2012), A&A 539 A147](https://doi.org/10.1051/0004-6361/201117984): raytracing/photoionization의 실제 1차/2차 시간 정확도 비교, 분할·stiff regime 문제의 문헌 비교 기준.
- [Formaggia & Scotti (2011), SIAM J. Numer. Anal.](https://doi.org/10.1137/100789592): mass-action positivity와 보존성을 지키는 수치해법 맥락. 이번 exact-midpoint 구성이 해당 논문의 특정 알고리즘을 복제하거나 전역 수렴정리를 증명하는 것은 아니다.
- [Grackle 3.4.1 원본 `rate_functions.c`](https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/rate_functions.c).
- 병렬 repo 신규 결과: [BASS_HE HE23 PR70](https://github.com/cosmosapjw-quantum/BASS_HE/pull/70)는 **total-H nuclei density**를 native owner에서 다시 취하고 fraction+energy 양쪽 Newton acceptance를 동시에 요구했다. [bass_cr C21 PR75](https://github.com/cosmosapjw-quantum/bass_cr/pull/75)는 source-age/common-q, source 시간적 GL2, conditional photon energy를 정리했다. [rec_bianchi R3f PR98](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/98)의 HyRec FULL H+He `q=0` 결과는 초기 recombination epoch에 속하므로 이번 낮은 적색편이의 Case-A reionization rate owner와 동일시하지 않는다. [WU088_HH PR95](https://github.com/cosmosapjw-quantum/WU088_HH/pull/95)는 별도 H-H 원자계산 lane으로 이 시간 적분 공식에 직접 이식하지 않았다.

## R5: 일반 2체 반응의 고밀도 1차 결손 구조

고정된 물리 부피/comoving stock 정의, signature (-,+,+,+), X=ln(a/a0), dt/dX=1/H, s/H signed, Sigma=sqrt(3)|s|/H. 물리적 RR source rate는

    alpha(T) nstar_cm3 exp(-3X) / H(X) [per X],

그리고 전체 이온·전자 반응은 dI/dX=dne/dX= - alpha(T)nstar exp(-3X) I ne/H(X).

재결합 단일 channel의 시작 이온 I0, 자유전자 E0 (오해 방지: photon energy와 다름), D=|I0-E0|, B0=min(I0,E0)에 대하여 고정 k에서 정확한 양의 소비량은

    A = B0 - B0*D*exp(-D*k*h)/[D+B0*(1-exp(-D*k*h))],

D=0이면 A=B0²*k*h/(1+B0*k*h). 시작 온도에 k(Tinitial)를 얼려 정확히 적분하는 기존 map은 **상태 의존 k(T)** 의 도함수에 의한 O(h²) local defect를 남겨 global 1차가 된다. 축약된 B'=-k(B)B(B+D)에서 Wolfram Language 검산:

    delta_frozen - delta_continuum = -(h²/2) k k'(B) [B(B+D)]² + O(h³),

반면 k((B+Bnext)/2)의 midpoint 평가는 order-h² 잔차가 정확히 0이다. 실제 Grackle 경로에는 k(T)와 cooling ratio Lambda(T)/alpha(T)를 **같은 중간 온도**에서 평가해야 한다.

현재 구현에서 각 채널에 대해 Tmid를 비선형 1차원 brentq로 풀어

    A(Tmid) = PairExact(I0,ne0, h*alpha(Tmid)*nstar exp(-3Xmid)/H),
    Q(Tmid) = A(Tmid)*Lambda(Tmid)/alpha(Tmid)/EV_ERG,
    Tmid = [Uinitial - Q(Tmid)/2] / [(3/2)kB*(nparticle,initial - A(Tmid)/2)],

로 정의한다. 
두 종의 양수성/보존성은 소비량 0<=A<=min(I0,ne0)에 기인한다. 총 H/He 원자수는 변화하지 않고 자유전자 stock은 정확히 A만 줄며, escaped photon-energy ledger에는 binding*A+Q를 기록한다. Uthermal도 정확히 Q만큼 감소한다. 평균 입자수 nparticle,mid=nparticle,initial-A/2은 재결합 전자 1개 제거에 정확히 해당한다. 원래 symmetric photo/recomb/photo 갱신과 전후 gas drift/광자 redshift drift는 변경하지 않는다. 물리 rate donor의 검증 온도 범위를 벗어나는 step은 **실패로 중지**하며 외삽 또는 사후 에너지 correction을 쓰지 않는다.

## C5–C8: 실제 샌드박스 계산

코드: `midpoint_recomb_v6.py`(새 양의 미시 반응 맵), `recomb_thermal_midpoint_v6.py`(원래 V4/V5 전체 clone의 물리 provider 분기만 추가), `bootstrap_v6.py`(기존 branch 또는 독립 ZIP run), `test_midpoint_v6.py`(새 경량 회귀), `run_dense_v6.py`, `run_dense_multichannel_v6.py`, `run_mixed_v6.py`, `run_cost_v6.py`.

- SciPy Radau 독립 baseline: 원본 `recomb_dominated_v5.py`와 동일 nstar=0.1 cm^-3, H0=1e-16/s, T0=15000 K, Xend=.01; midpoint 결과는 discrete thermal/chemical/escaped-energy ledger 잔차 machine precision; source photons=0.
- H-only: h={.0025,.00125,.000625,.0003125}, 기존 T error={.0125253,.00627693,.00314200,.00157188} K, 새={5.69408e-5,1.42363e-5,3.55908e-6,8.89811e-7} K. 새 관측 p={1.99989,1.999999,1.99993}.
- He-only: 기존 최종 h=.0003125 error=.00776701 K, 새 5.70305e-5 K; 3개 refinement p≈2.000.
- H/He mixed: 기존 최종 error=.000362891 K, 새 1.55551e-5 K; 신규 p={1.9884,1.99710,1.99927}.
- 저밀도 source-free H/He FLRW 및 signed s/H±.04에서는 기존 V5의 angular/photo 지배 오차와 새로운 알고리즘 결과가 표기 정밀도에서 같음. 이는 전체 source-on 다단계 parity가 아니다.
- 새 9개 pytest + V2/V3/V4/V5 그대로 유지한 회귀를 통합해 `114 passed`, 0 fail, 3.41 s (실행 컨테이너, 명령·전체 로그 별도 보존).
- 성능: 같은 dense H-only endpoint에서 V5 h=1e-5 (1000 substeps), T error≈5.03e-5 K, median 0.10815s; 새 h=.0025 (4 substeps), err≈5.69e-5 K, median 0.001827s; **유사한 정확도에서 59.2배 빠른** sandbox 특정 실행. 더 엄격한 새 h=.00125 (8 steps), err≈1.42e-5 K, median 0.003493s. NCP/native Rust 가속 주장 아님.

## R6: 제한과 다음 native 계약

- 입증한 것은 고밀도, 주어진 Grackle rate interpolant, prescribed H, Case-A RR/DR subset과 toy-free thermo ledger에서의 정합성과 수렴이다. source spectrum retransport, native full-state Jacobian, Case B, CI/CE/free-free/CMB, proper-time/full-history, full EoR는 검증되지 않았다.
- 중간 및 끝 T가 10–24kK 범위에 있는 smooth regime에서 2차가 관측됐다. 전역 unconditional positivity / stiff-limit / arbitrary spectral threshold/time-grid theorem으로 승격하지 않는다. 큰 time-step에서는 brent root가 donor 유효 범위를 벗어나면 명시적 FAIL이 맞다.
- PR150 native source-on *single-step* 이력은 원래 V5 기록에서만 검증됨. actual PR150 full-step coupled Newton은 별도 owner; 이번 Python branch가 이를 업데이트·대체하지 않는다.
- HE23 total-H density, CR21 source-age/energy, PR150 원래 implicit owner로 인계한다. **다음 실제 독립 NCP 단위**: source-on native FLRW 동일 초기 상태의 `dt`/`dt/2`/`dt/4` 다단계 비교, photon/absorber/electron/thermal/binding/escaped/redshift work의 *stepwise* ledgers 및 rate-midpoint adapter 속도/정확도. 한 행의 source-only 단일 스텝이나 이번 sandbox 2차를 production full GO로 주장하지 않는다.

`native_subagent: NOT_RUN` (현재 제공된 native subagent dispatch tool 없음). Raw 129-row Grackle donor, 기존 V5 NCP 두 archive와 PR158 source HEAD는 바이트 기록에 의해 고정. 이번 research 구현·테스트·결과는 새 additive branch에 게시하고 아래 handoff로 이어간다.
