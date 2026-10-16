# REI-LRS V8: Grackle Case-A RR/DR 단독 시간 적분과 네 채널 냉각 회계

**상태 (2026-10-16):** R5/C5/C6/C8 샌드박스 단계 완료. V7 PR #163 HEAD `a6fe0e8b1932ddf60496c5a9dbb68c19d6f0851f`에서 새 독립 연구 브랜치로 분기. 원래 PR #150 native owner는 **`6ea2b1b4b3875c9163cafc45efe720afded43fc4`**로 고정. 다른 NCP 계산, production worktree와 checkpoint는 수정하지 않았다. Native Rust owner 실제 RR-only midpoint 실행은 **NOT_RUN**이며 따라서 native-vs-Radau 직접 동등성을 주장하지 않는다.

## 물리·부호·단위

Grackle 3.4.1 기반의 Case-A H II, He II, He III radiative recombination(RR), He II dielectronic recombination(DR)을 *하나의 재결합 부분계*로 고정한다. 온도 범위 10,000–24,000 K, flat FLRW `a0=1/21`, `X=ln(a/a0)`. 서명 `(-,+,+,+)`. `q_ref`나 Bianchi shear는 이번 단계의 변수가 아니며, 향후 Bianchi에서는 표준 `Σ=√3|s|/H`, orientation은 별도.

각 반응의 ion counter, electron counter, `Λ_j(T)` thermal cooling, `χ_j A_j` binding capture를 독립으로 저장한다. He II RR과 He II DR은 같은 목표 ion과 결합에너지(`χ_HeI`)를 쓰지만 **각기 다른 α,Λ,Q,A ledger**를 갖는다. He III→He II는 `χ_HeII`를 방출한다. 각 원자핵수는 보존된다.

`w=(3/2)k_B T(1+Y+e)` (erg/total H), `e=n_e/n_H`, `Y=n_He/n_H`; `χ`는 native HHeModel의 eV 값을 `EV_ERG=1.602176634e-12`로 변환. Proper `n_H(a)` [cm^-3], `H(a)` [s^-1], `α` [cm^3/s], `Λ` [erg cm^3/s]. RR/DR 사건 `dA_j/dX = (n_H e I_j/H) α_j`, 냉각 `dQ_j/dX=(n_H e I_j/H) Λ_j`. `Eesc=Σ(χ_j A_j+Q_j)`는 **선택한 Case-A escaping radiation closure**의 별도 bookkeeping이다. 이것을 diffuse Case-B spectrum / RT의 완료로 해석하지 않는다.

Wolfram Language에서 `w'+B'+Eesc'+Wgas'=0`, exact pair-flow 미분방정식 잔차가 각각 정확히 0으로 환원됨을 확인했다. 이 증명은 정의된 연속 부분계와 가정에서만 유효하다.

## 구현 및 보호장치

새 `rrdr_sourcefree_v8.py`: 두 개씩 생성된 양의 mass-action subflow를 4-channel 대칭 Strang으로 합성한다. `Tmid`를 `[10000,24000]` K 구간의 Brent root로 자기 일관적으로 계산하고 시간 의존 geometry는 `Xmid`에서 평가한다. 기체 단열 work는 `w'=−2w`의 정확한 half-step으로 처리한다. Nonnegative populations, finite T domain 및 thermal reservoir를 만족하지 못하면 reject한다. Cooling과 binding은 사건수에서 독립적으로 적립, residual을 억지로 0으로 맞추지 않는다. 현재 구현은 Python 기반 연구용 검증기다. Rust production에 자동 이식하지 않았다.

실제 owner `igm_rates.rs` SHA256 `310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf`; V7 literal rate 함수와 original 129-row donor 테이블이 전 온도 행에서 bitwise/숫자 동일(검사 최대 상대오차 0). Grackle 외부 원본과의 광범위한 provider certification까지 주장하지 않는다.

## 실행한 과학적 검증

**C6:** Python pytest `21/21 PASS`, original native V7 continuous RHS와 동등성, source-free zero-density adiabatic limit, nuclear/electron/thermal+binding+escaped radiation ledgers, He II RR/DR 분리, 양수 exact pair map, domain 거절. 기존 부모 suite 전체를 반복하지 않고 새 코드에 집중했다.

**C8:** 연속 RHS는 pair-map/Strang을 호출하지 않고 별도로 SciPy Radau로 통합한다. `n_H`를 prescribed original FLRW에서 `D`배 한 인위적 overdensity 조건에서 5 cases×5 step=N{8,16,32,64,128}=25 rows. `D=1,Xend=1e−5`에서는 T 오차 ~10^-11 K로 **부동소수점 오차 바닥**, 수렴 차수 주장하지 않는다.

| 조건부 밀도계수와 Xend | N=8 T 오차[K] | N=128 T 오차[K] | 최종 구간 관측 p |
|---|---:|---:|---:|
| D=100, Xend=.002 | 8.06659e−5 | 3.15247e−7 | 1.9992 |
| D=1000, Xend=.002 | 8.19818e−3 | 3.16236e−5 | 2.0002 |
| D=10000, Xend=.0003 | 1.15182e−2 | 4.28352e−5 | 2.0009 |
| D=1000, T0=22000K, Xend=.002 | 9.47280e−3 | 3.68375e−5 | 2.0001 |

전자 stock, 종별 cooling 전부 h-refinement에서 2차 수렴했다. Radau solution의 dense-output을 독립 1D `quad`로 다시 적분하면 **네 채널 총 최대** 누적 cooling 차이 `3.3353e−27 erg/H`, event 차이 `3.0011e−16/H`. 정해진 측정값이지 전체 함수해의 절대 오차 상계는 아니다.

**C8 stiff counterexample:** 고정 geometry, `D=1e6`, `Xend=.0001`: 양수성과 energy ledger는 N=8…1024 모두 통과했으나 coarse `max ΔX n_e α/H≈25`에서 시간 차수가 `−0.096`, finer (max exposure `.197`)에서 `1.987`로 점진적으로 회복했다. 즉 **양수성+보존이 강성 정확도 또는 uniform 2차 수렴을 보장하지 않는다**. NCP native는 relative exposure 제한/연속해 비교 없이 강성 구간을 PASS로 승격하지 말아야 한다. 이 D 변화는 실제 우주론적 overdensity 진화를 뜻하지 않는다.

## 병렬 연구 재사용 및 다음 DAG

- REI PR #163: 실제 source-on 16–128 원본/RR-midpoint 쌍 모두 약 1차, full second order HOLD.
- REI PR #150: 실제 source005 long history와 이후 source008 전진. Native 최신 코드는 실제 HEAD를 새로 확인할 것. PR #163의 frozen owner는 `6ea2b1b4...`, 최신 PR150 HEAD와 혼동하지 않는다.
- BASS_HE HE23 PR #70: n_H,total vs HI neutral를 구분해야 하며 thermal+species Newton gate 동시 판정 필요.
- bass_cr C21 PR #75: photo source-age GL2와 threshold optical depth 시간 중심화는 RR 부분계와 별도의 미래 작업. 이번 파일에서 중복 구현하지 않음.
- REC R3f의 HyRec recombination epoch은 다른 redshift/physics regime라 이번 Grackle RR owner를 대체하지 않음.

새 C10 외부 Codex의 다음 구체적 단위는 **pinned PR150 native RR-only operator**와 이번 독립 continuous Radau의 직접 수치 동등성, 특히 4채널 cooling/escaped binding ledger, `D=1`과 선언된 overdensity 입력의 time refinement, stiff max-exposure 적응 step 관리를 비교하는 것이다. 그 후에만 source-on에서 photon birth/absorption/CI/CE/freefree/CMB BE 항의 순서 오류를 별도 범위로 검증한다.

## 논문·원본 링크

- [Grackle 3.4.1 original C rates](https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/rate_functions.c)
- [Mackey 2012 raytracing time algorithms](https://arxiv.org/abs/1201.5651)
- [Norman et al. 2009 coupled implicit chemistry](https://arxiv.org/abs/0901.1110)
- [Pawlik & Schaye 2011 H/He thermal RT](https://arxiv.org/abs/1008.1071)

**Claim verdict:** Symbolic 4channel RR+thermal ledger **DERIVED/EXACT**. Sandbox 21 tests and selected nonstiff 2nd-order **NUMERICALLY VERIFIED CONDITIONAL**. Stiff uniform accuracy **HOLD**. PR150 true Rust RR-only vs Radau **NOT_RUN**. Actual source-on second-order, Case-B photon retransport, full EoR, signed Bianchi **HOLD**. Native subagent **NOT_RUN** (no native delegation surface).
