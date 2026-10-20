# BRPERF01 최적화 연구 결과

**기준일: 2026-10-20 KST. 프로젝트: cosmosapjw-quantum/rei_bianchi.**

이번 bounded unit은 원래 물리 계산을 유지하는 재사용 경로와, 오차를 따로 제한한 경량 온도 표를 실제 Rust로 구현했다. 새 표를 원 native H/He/D 반응 RHS와 Strang–CX 이력에 연결했으며, 광자 계산에서는 실제 BASS 두 전단 부호의 원 384개 source labels를 보존하는 영속 작업자 경로를 검증했다. Li/C/N/O의 원자 계수도 원저자 자료를 읽어 추가했다.

## 1. 최종 판정과 주요 수치

**`BRPERF01 = COMPLETE_VERIFIED_BOUNDED_OPTIMIZATION`**이다. 실제 검증 범위는 계수·native 기체 제어 연구·동결 기체 광자 reference이다.

| 대상 | 직접 관측한 결과 | 적용 범위 |
|---|---:|---|
| H/He/D 같은 T direct bundle 공유 | native RHS 약 1.411× | 원 direct와 비트 일치 |
| compact 8193 scalar | native RHS 약 2.918× | 원 coefficient 대비 표본 최대 상대오차 1.30017×10⁻⁵ |
| compact table 메모리 | 9,109,624 → 4,259,840 B | coefficient/mask payload 53.238% 감소 |
| compact coefficient kernel | paired median 4.9166× | 100,000 query, 15개 채널과 diagnostics 소비 |
| 광자 영속 2-worker, 음전단 | paired median 1.80473× | 전 경로·ledger 원시 바이트 일치 |
| 광자 영속 2-worker, 양전단 | paired median 1.77507× | 전 경로·ledger 원시 바이트 일치 |
| 추가 원소 | 24 PI + 24 CI + 12 RR | 원소·전하 단계 계수 이식 |

Table 경로는 원 direct보다 근사오차가 크다. 기존 65,537-node loglinear 표의 같은 넓은 probe 최대오차는 약 3.83×10⁻⁷이다. 새 표는 이번 표본 수용 기준 10⁻⁴를 만족하며 더 적은 메모리와 시간을 사용한다. 정확도 자체의 개선으로 해석하지 않는다. 성능 표는 서로 다른 계산 범위를 구분하며, 전체 배경–광자–CX solver의 가속률로 합산하지 않는다.

## 2. 기준 소스와 물리 계약

작업 시작 시 PR #208 HEAD `54948439be7039c9b2b1f9580bee69bebeb80129`를 다시 읽었다. 새 PR #210은 이 commit에서 시작한 별도 add-only Draft이다. 기존 scientific BR06 commit은 `0c71466c0a9b4fb357f9b168dbbe4cae74e1f8dd`이고, 검증된 전체 ZIP SHA는 `3137ad8903ef62073485a18e78b84966d3a9d09b9a60698dddfd492876432135`이다.

원 archive와 실제 source/native input 625개 payload를 비교하여 전부 일치했다. `owner_src`의 13개 파일은 원 12개 physical owner와 기존 `rate_table.rs` utility이다. 원 source·spectrum·threshold·signed shear identity를 유지했다. Metric은 (−,+,+,+), 체적은 a³이며 광자는 실제 출생 시각·geometry·Killing K·방향·weight·spectral label을 유지한다. BASS는 one-way background다.

원 source의 Grackle 3.4.1 pin, Verner H/He, H-equality D, Savin CX, 원 CMB/FF 및 chemistry energy 소유권이 그대로다. H binding 13.598434599702 eV와 Verner fit edge 13.60 eV, 제조된 D threshold 13.602134599702 eV를 구분한다. 새 Li/C/N/O의 fit threshold를 원 chemical binding energy owner에 덮어쓰지 않았다.

검토에서 기존 코드에 이미 T table, SoA, std workers, PreparedIgmRates와 reflection cache가 있음을 확인했다. 이를 신규 기능으로 세지 않고 실제 남은 비용을 출발점으로 삼았다. S10 `budget_native.rs` 계보와 별도 `nested_budget.rs` 계보의 병합은 없다.

## 3. T-only rate의 분리와 양의 경량 표

충돌 사건수는 예를 들어 R_CI=nₑ n_HI k_CI(T), 냉각은 nₑ n_ion Λ(T)처럼 source 계수와 상태 의존 인자로 분해된다. 원 metastable HeI CE 항은 nₑ² n_HeII Λ(T)이므로 그 계수는 erg cm⁶/s다. 이를 다른 CE의 erg cm³/s와 섞지 않았다. 밀도, photon spectrum과 에너지, 방향, 팽창 H, CMB bath 온도는 계수표에 숨겨 넣지 않는다.

15개 표 채널은 H/He CI 3개, RR 3개, HeII DR 1개, CE 3개, RR kinetic cooling 3개, DR raw cooling, free-free이다. D는 원 H-equality 모델이 선택한 H 계수를 같은 T bundle에서 투영한다. 온도나 조성이 바뀌면 EOS에서 실제 새 T를 구한다. 준비 온도와 EOS T가 한 ULP라도 다르면 native prepared API가 거부한다.

### 계산식

x=ln T의 균일 격자에서 k_i=k(T_i), δ_i=k_(i+1)−k_i로 둔다. 같은 부호의 두 이웃 secant에 대해서만 정규화 기울기 m_i=2δ_(i−1)δ_i/(δ_(i−1)+δ_i)를 사용하고, 극값이나 평탄 구간에서는 0으로 둔다. 구현은 작은 절댓값을 먼저 쓰는 harmonic 표현으로 중간 곱을 피한다.

구간의 네 Bernstein control은 (k_i, k_i+m_i/3, k_(i+1)−m_(i+1)/3, k_(i+1))이고, q∈[0,1]에서 가중치는 ((1−q)³, 3(1−q)²q, 3(1−q)q², q³)이다. 이 가중치는 비음수이며 합이 1이다. 모든 control이 비음수·유한한 cell만 수용하므로 평가도 양의 조합이다. 저온 DR의 원 구조적 0은 유지된다.

원 5,500 K RR 분기, T/11605≤0.8 DR/CI 분기, CE/DR exponent cap, CI floor-mask 전환을 가로지르는 cell과 이웃 두 cell은 direct fallback이다. 끝 구간도 direct를 쓴다. 입력 domain을 벗어나거나 비유한 T인 경우 원 owner 오류를 반환한다. 원 source는 builder에서 노드당 한 번만 호출한다. 매 query는 한 번의 ln(T)/cell 계산과 다항식 곱·합을 공유하며, 기존 loglinear의 채널별 exp 15회를 제거한다.

| 노드 수 | 최대 표본 상대오차 | 10⁻⁴ 기준 |
|---:|---:|---|
| 1025 | 7.70451294×10⁻³ | 미달 |
| 2049 | 8.97607721×10⁻⁴ | 미달 |
| 4097 | 1.06664028×10⁻⁴ | 미달 |
| 8193 | 1.30016634×10⁻⁵ | 통과 |

기본 opt-in 선택은 8193이며 default backend는 Direct다. 4097의 근소한 미달을 수용 기준 변경으로 통과시키지 않았다. 최대오차 위치는 HI CE cap 바깥 약 1723.5255 K다. 이 probe는 연속된 모든 실수 T의 엄밀한 supremum 증명이 아니다.

검증한 네 해상도에서 scalar/SIMD 1,891,260개 coefficient 비교의 bit mismatch는 0이었다. 독립 SciPy PCHIP와 60자리 Decimal Hermite 검산 14,910개 채널 표본의 최대 상대차는 각각 9.53×10⁻¹⁴, 4.44×10⁻¹⁶이다. Wolfram은 Hermite−Bernstein=0, 가중치 합=1, 비음수 조건을 확인했다.

### 저장과 SIMD

Cache는 numerical schema, 실제 compile된 원 source bytes의 SHA-256, node 수, control/mask와 payload SHA를 포함한다. `from_bytes`는 source mismatch·길이·hash·잘못된 mask·음수/비유한 control을 거부한다. 이는 우발적 손상과 source 혼용을 검출하는 계약이며 신뢰할 수 없는 작성자의 진위를 인증하는 서명은 아니다.

실제 도입한 `wide=1.7.1`은 safe `f64x4` 곱·합, `sha2=0.10.9`는 source/cache hash를 담당한다. 호스트에는 AVX/AVX2/AVX-512 기능이 노출돼 있지만 측정 바이너리는 AVX를 활성화하지 않은 기본 SSE2 대상으로 빌드했다. 정적 disassembly의 해당 함수에는 packed f64 `mulpd` 28개와 `addpd` 21개가 있고 AVX/FMA 명령은 없다. scalar kernel은 4.9166×, SIMD는 4.4201×였으므로 추가 SIMD 가속을 인정하지 않았다. native RHS에서 두 경로의 작은 시간 차이 역시 공유 환경 잡음보다 확실하게 크다고 보지 않는다.

## 4. 실제 native H/He/D 연결

원 `midpoint_gas::rhs`에서 H/He와 D가 반복하던 같은 온도 rate 계산을 하나로 공유하는 receiver를 추가했다. Native state/budget/error 타입은 원형을 사용하고, 상태 적용·CX half-flow·budget 합산은 원 `apply`, `cx_flow`, `add_budget`에 위임했다. D의 단위 변환, 순차 density product, 여섯 energy row의 합산 순서를 대조했다. 전체 controller를 새 적분기로 바꾼 것이 아니다.

고정 체적·광원 OFF 세 제어 초기온도 3000/10000/60000 K와 Nt=48/96/192를 사용했다. 각 표 해상도에 다섯 backend를 연결하여 45개 이력·5040 macrostep을 실제 완료했다. 4097 탐색과 8193 primary 실행을 구분한다. Primary original↔reused direct 9쌍, scalar↔SIMD 9쌍의 전체 이력이 비트 단위로 일치했다.

8193에서 같은 Nt의 direct 이력 대비 최대 population family-scaled 차이는 1.82572×10⁻¹¹, 최대 최종 T 상대차는 2.22948×10⁻¹¹이었다. 독립 Python은 CSV의 원 population으로 EOS, free electron 수, binding energy와 nuclei/baryon 합, thermal/chemical/escape/CMB budget을 재구성했다. 최대 total-energy drift는 1.26338×10⁻¹⁵, thermal budget 잔차 1.89644×10⁻¹⁵, chemical budget 잔차 1.03632×10⁻¹⁵이며 음수 population은 없었다.

HOT direct의 Nt=192 최종 T는 42301.6443469075 K이고, 마지막 두 격자 차이는 0.14386610 K, 세 격자 형식 차수는 약 2.01425다. COOL/MID의 작은 차분과 내부 CX tolerance를 고려하여 보편적인 2차 정확도를 주장하지 않는다. 보존 잔차와 time/table accuracy는 별도로 판단했다.

### Native RHS 측정

같은 64개 fixture, window마다 32768 RHS 호출, backend마다 프로세스당 6쌍 ABBA/BAAB를 다섯 독립 프로세스에서 순차 측정했다. 표의 speedup은 프로세스별 중앙값의 중앙값이다.

| 경로 | Speedup | 프로세스 중앙값 범위 | 표 setup 중앙값 | setup 손익분기 |
|---|---:|---:|---:|---:|
| Reused direct | 1.41147× | 1.39723–1.49686 | 0 | 0 |
| 기존 65537 | 2.17612× | 2.07671–2.20859 | 134.122 ms | 251809 RHS |
| Compact 8193 scalar | 2.91818× | 2.69265–3.06154 | 7.739 ms | 11601 RHS |
| Compact 8193 SIMD | 2.88468× | 2.46764–3.00474 | 같은 표 | 11917 RHS |

A/A 중앙비 1.04668, 범위 0.83379–1.15336을 함께 보존했다. `Reused direct`는 같은 정확도이고 table은 각각 근사오차를 따로 제시했다. 표 생성 비용을 제외한 속도와 생성비를 회수하는 호출 수를 구분했다. 전체 CX·배경·photon trajectory의 end-to-end speedup은 측정하지 않았다.

## 5. 광자 계산 재사용과 결정적 병렬화

원 BR06는 이미 reflection-equivalent path와 geometry cache를 쓴다. 새 경로는 Gauss 규칙 두 개를 사전 생성하고 opacity 임시 Vec를 경로별 1024-byte scratch로 바꾸며, 동결 EOS·흡수자 밀도·threshold·provider와 birth-ray 구성을 재사용한다. 실제 E(t)의 단면적, Killing pullback, 구적 차수, Newton/bisection와 thin/subnormal 처리·합산 순서는 원 함수와 같다.

`Rc<RefCell>` geometry를 임의의 thread-safe 객체로 취급하지 않았다. 각 영속 작업자가 원 fixture를 독립 로드하며, batch와 worker의 semantic identity를 작업 제출 전에 비교한다. 결과는 원 unique path index 순으로 정렬한 다음 원 순서로 ledger에 더한다. 모든 labelled birth는 그대로 유지한다. 중간 검토에서 발견된 다른 fixture 혼용 가능성은 immutable borrow, pointer guard 및 worker identity 검사로 해결했다.

최종 각 사례는 실제 384 source labels, 3648 labelled births, 1824 reflection-unique paths다. Birth refinement 1, path slabs 2, opacity Q2, event E4에서 warmup 2회, paired 7쌍, A/A 3쌍을 실행했다.

| 전단 | Baseline 중앙값 | 2-worker 중앙값 | paired speedup | paired 범위 |
|---|---:|---:|---:|---:|
| 음전단 | 1.41228 s | 0.758894 s | 1.80473× | 1.70890–1.91633 |
| 양전단 | 1.47134 s | 0.807587 s | 1.77507× | 1.52490–1.96095 |

직렬 cache의 paired 비는 각각 1.01848과 0.985805로, wall-time 향상은 NOT_ADMITTED다. 음전단에서 임시 할당 37,194회와 누적 payload 1,190,208 B, 반복 EOS 111,872회와 Gauss 구성 3646회를 제거했지만 geometry 등 남은 비용이 크다. 누적 할당 감소를 전체 peak-memory 감소로 바꾸어 말하지 않는다. 작업자별 fixture와 준비 batch는 별도 메모리를 사용한다.

모든 PathResult 27개 필드의 41-word 및 Ledger 전체 33-word가 세 모드에서 원시 바이트로 일치했다. 독립 Python의 Killing K 재구성 상대차 최대값은 0, 경로별 photon-number 잔차 최대값은 4.44089×10⁻¹⁶이다. 정확히 같은 결과를 평가하는 최적화이므로 원 BR06의 birth/age/spectral 정확도 상태도 그대로다.

## 6. 추가 원소의 실제 이식

원저자 [Verner PI 자료](https://www.pa.uky.edu/~verner/photo.html), [Voronov CI 자료](https://www.pa.uky.edu/~verner/col.html), [Verner–Ferland RR 자료](https://www.pa.uky.edu/~verner/rec.html)의 숫자와 식을 읽었다. 외부 dependency가 없는 별도 Rust catalog에 Li/C/N/O의 24개 bound-electron 단계 PI·CI, 최종 전자수 1–3인 12개 RR를 넣었다. RR label은 재결합하여 만들어지는 최종 이온이며, 없는 단계는 `None`이다.

독립 Decimal 60자리 비교는 PI 3096점/CI 6168점/RR 1548점, 합계 10812점이다. 최대 상대차는 1.41349×10⁻¹⁴ / 1.03834×10⁻¹⁴ / 9.28644×10⁻¹⁵였다. 원 ASCII와 Fortran coefficient identity도 별도 확인했다.

CI의 U=χ/(kT)에 대해 원 Voronov 식의 로그 곡률은

\[
\frac{d^2\ln k}{d(\ln T)^2}
=\frac{P\sqrt U}{4(1+P\sqrt U)^2}-\frac{XU}{(X+U)^2}-U.
\]

선택 구간에서 M≤Umax+5/16을 사용한다. 선택 RR의 0≤b≤1에서는 M≤1/8이다. loglinear 구간 폭 h를 정하면 정확한 실수 산술의 상대오차가 expm1(Mh²/8) 이하이므로 node 수를 직접 정할 수 있다. 부동소수 검산은 이 이론 상계와 별도다.

| 표 | 목표 | 실제 최대오차 | coefficient payload |
|---|---:|---:|---:|
| 24 CI | 10⁻⁴ | 9.84301×10⁻⁵ | 250360 B |
| 12 RR | 10⁻⁴ | 8.74151×10⁻⁵ | 23712 B |

개별 CI kernel은 마지막 RUN에서 약 1.275×, 같은 T를 24개 CI에 적용하며 ln(T)까지 공유하는 경로는 중앙 시간 비 2.221×, paired median 2.160×였다. 이 역시 coefficient kernel의 관측이다.

이 포트는 원소·전하 단계의 원자 데이터다. 동위원소별 에너지 이동·질량수·핵반응·새 abundance를 공급하지 않는다. CI Tmin은 eV, Tmax는 keV이며 원 변환상수 8.617385×10⁻⁵ eV/K를 보존한다. 선택 CI의 최저 유효온도도 약 11604 K이므로 10⁴ K 이하의 추가 원소 CI를 검증한 것이 아니다. PI Emax 밖과 미제공 RR는 명시 오류/None으로 남긴다. 완전한 network에는 나머지 RR/DR/CX/CE, cooling moment, binding owner, inner-shell PI와 population/electron/energy 연결이 필요하다.

Savin의 forward/reverse는 두 경험식이다. 제조된 D energy defect의 Boltzmann 비를 강제하지 않았다. 같은 격자·선형 로그 보간에서는 L(ln kr)−L(ln kf)=L(ln(kr/kf))이므로 ratio 표현만 바꿔 정확도가 개선된다고 주장하지 않는다. CX half-flow는 원식을 그대로 호출한다.

## 7. VigilODE와 외부 코드의 재사용 판단

기존 BR06의 검증된 VigilODE pin `a21d573980f66fe02891bd216153443b5352f921`을 유지했다. 이번 관측 default ref `8d0c79184e09efb5bdadc24a6315c60a71a44264`는 GitHub compare에서 a21의 595 commit 조상으로 나타났다. default ref에서 읽었다는 사실을 더 새로운 과학 코드라는 뜻으로 해석하지 않는다. 읽은 `kernels.rs` 3159 B는 두 ref에서 동일했다. `paired_timing.rs@8d0`는 404였다.

VigilODE의 workspace 재사용 및 ABBA/A/A/독립 session 원칙을 채택했다. 현재 15개 scalar coefficient와 4×16 Bernstein 합에는 선형 연립계가 없으므로 GMRES를 끼워 넣을 계산 대상이 없다. 더 큰 implicit 원소 반응망에 적용할 때 Jacobian, positivity, energy ledger와 원 controller 관계를 별도 검증한다.

보존 a21의 formal timing promotion은 6개 이상 독립 session 등 더 강한 조건을 요구한다. 이번 rates의 6 ABBA block이나 native의 5개 process를 그 formal gate PASS로 표시하지 않는다. 새 코드에서 `paired_timing.rs` 자체를 복사한 것으로도 표시하지 않는다. 실제 직접 도입한 package, 보존한 kernel, 차용한 측정 원칙을 구분했다.

## 8. 테스트·실패·fresh restore

현재 Rust 1.94.1에서 parent 233개, BR06 16개, 새 native receiver 9개, rates 5개, photon 11개, atomic 8개, 합계 **282개 unique Rust tests PASS**다. strict Clippy와 각 변경 표면의 scoped rustfmt를 실제 실행했다. 같은 테스트의 debug/release·restore 반복을 unique 수에 중복 가산하지 않는다.

Source snapshots를 새 디렉터리에 복원해 hash와 실행을 확인했다. Photon 640 payload 복원 후 11 tests, atomic source 24 payload 후 8 tests 및 Decimal, rates+parent 125 payload 후 5 tests와 독립 oracle, 최종 native+table 126 payload 후 빈 target build·두 해상도 이력·9 adapter tests를 통과했다. 최종 native 16개 deterministic CSV는 기존 결과와 SHA까지 같았다. Compiler와 검증된 registry는 재사용했고, 새 경로의 binary bytes가 달라지는 현상은 numerical CSV identity와 구분했다.

실패 기록은 삭제하지 않았다. 주요 분류는 다음과 같다.

| 관측 | 분류·처리 |
|---|---|
| 1025/2049/4097 rate probe 기준 미달 | COEFFICIENT_ACCURACY_TARGET_MISS; 8193 선택 |
| SIMD의 추가 gain 미확인 | NO_EXTRA_SPEEDUP_ON_MEASURED_TARGET |
| 직렬 photon cache 시간비≈1 | SERIAL_WALL_SPEEDUP_NOT_ADMITTED |
| 강제 max_rate_calls=1 | 5 backend 모두 첫 단계 Cx(WorkLimit), accepted=0 |
| photon max_samples=1 | REFERENCE_WORK_LIMIT; CX 오류와 구분 |
| 공개 prepared 객체의 fixture 혼용 | guard/lifetime/worker identity 수정, 최종 코드 재검증 |
| XOR checksum 상쇄 및 stale binary launch | 계측기 수리; 해당 결과 보존·최종 timing 제외 |
| 원 source까지 읽은 broad fmt check | 쓰기 없음, own scoped check로 수정 |
| Drive 첫 checkpoint 도구 목록 변경 | 업로드 ACK 없음, 재시도 성공 |

작은 ledger 잔차를 정확도 증거로 대체하지 않았고, work budget 고갈을 물리 해 부재나 수렴 실패로 바꾸지 않았다.

## 9. 연구 루프와 다음 DAG

사용자의 deep optimization/coding 요청 범위에서 physmath-research-loop를 적용했다. 초기에 제공된 기존 protocol 지침을 사용하고, 게시 단계에서 현재 설치된 1.3.0의 통합 정책을 확인했다. 실제 협업 하위 작업과 독립 검산을 사용했으며, Codex 서비스·사용자 local·NCP 실행을 요청하지 않았다.

| C 단계 | 완료한 산출물 |
|---|---|
| C1–C2 | source/runtime identity, 기존 T table·광자 hot path 및 coefficient/state 소유권 대응 |
| C3–C4 | 양의 PCHIP·analytic log table, SIMD/pool 선택, bounded 3축 해상도·benchmark DAG |
| C5 | rates/native/photon/atomic 실제 Rust crate와 executable harness |
| C6 | 입력 거부·OFF parity·원 source 회귀·strict Clippy/scoped fmt |
| C7 | species/thermal/chemical/CMB·photon/Killing ledger 독립 검산 |
| C8 | rate node·시간 격자·오차/메모리/ABBA·fresh restore |
| C9 | native/source·atomic·prepared provenance·codegen·그림의 한 차례 상보적 독립 검토 |
| C10 | 단계별 source/결과/실패/DAG 패키지와 GitHub·Drive·Dropbox receipt |

| 다음 노드 | 상태와 실제 다음 작업 |
|---|---|
| PERF01_T_TABLE_NATIVE | COMPLETE_VERIFIED_BOUNDED |
| PERF02_PHOTON_REUSE_POOL | COMPLETE_VERIFIED_FROZEN_REFERENCE_CONTROL |
| PERF03_ATOMIC_CATALOG | COMPLETE_VERIFIED_COEFFICIENT_ONLY |
| PERF05_BASS_NATIVE_COMBINED | NEXT: 원 BASS source-native driver에 table receiver와 pool을 함께 연결해 같은 입력의 전체 비용·state·birth ledger 비교 |
| PERF06_TARGET_DISPATCH | OPEN: AVX2/AVX-512 또는 safe runtime dispatch를 같은 정확도·입력으로 비교 |
| ATOMIC_NETWORK_01 | HOLD: 누락 채널·binding/energy/electron owner 확보 후 한 원소씩 활성화 |
| BR07_NATIVE_MOMENT_ENERGY_ADMISSION | PENDING: 원 birth/age/energy admission 연구 재개 |
| LONGSPAN_SOLUTION | NOT_ADMITTED |
| ISO_COUPLE_P4 | PARTIAL |
| SA-01/02, FLRW-CONV, BI-SIGNED, FULL_EOR | HOLD |
| Two-way Einstein feedback | NOT_IMPLEMENTED |

완료 checkpoint의 hash/게시·provider 상태는 `contracts/STAGE*_PUBLICATION.json`과 최종 `PUBLICATION_RECEIPT.json`을 따른다. ACK, provider hash 및 raw restore는 각각 다른 필드다. 최종 전체 ZIP은 코드·원 parent·실제 입력·수치 결과·실패 로그를 포함하며, 새 외부 원문 재배포가 확인되지 않은 reference는 URL/hash 복원 계약을 보존한다.
