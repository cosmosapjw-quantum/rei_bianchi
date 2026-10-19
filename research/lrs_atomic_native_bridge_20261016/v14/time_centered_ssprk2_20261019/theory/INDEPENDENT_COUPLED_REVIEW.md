# V15 Contract B 독립 source·실행·회계 검토 — clock 수정 후

검토일: 2026-10-19. 검토자: `/root/dropbox_v15_intake` — root 및 실제 구현자와 분리된 subagent. 이 검토자는 native source 수정, native 실행, GitHub/cloud 변경을 수행하지 않았다. 완성된 실제 CSV의 독립 Python 후처리와 source 검토를 수행했다.

## 최종 판정

**공통 기체 중점과 native photon SSPRK(2,2)의 결합 구현, 안정적 clock 수정, 실제 bounded 실행의 사건·열·광자 회계를 확인했다. clock finding은 해결됐다.** 양의 초기 photon과 evolving gas의 fixed-geometry 대조군, positive-seed source-disabled GL2 대조군에서 약 2차 수렴을 관측했다. 짧은 실제 physical GL2 source-on에서는 photon N/U, HII/HeII, photo 사건, w/T 및 photoheat 등 분해 가능한 채널이 약 2차로 수렴했다.

**source-on HeIII endpoint와 일반 source-on 전체 2차 주장은 HOLD다.** 수정 후 HeIII의 successive differences는 약 7e-18…4e-17로 불규칙하다. uniform stiff, CaseB, fullEoR, signed Bianchi, native 일반 4차도 이번 증거로 승격하지 않는다.

Contract B 행렬은 **16개 고유 설정을 수정 전 16회, 수정 후 같은 설정 16회 실행**한 것이다. 이를 32개 새 과학 설정으로 세지 않는다. unique 표적시험은 transport 7 + coupled 7 = **14개**이며 clock 결함 회귀가 그중 한 개다. 이전 NCP 84이력, projection 62행, 제조 76문제, Python57 검증은 새 실행에 합산하지 않는다. 새 NCP 실행은 없다.

## 1. 실제 완료와 source 정체성

명시적 data-ready 이후 `v15_work/execution_coupled/`의 수정 후 command, stdout, stderr, exit, timing, source/execution receipt 및 여덟 raw CSV를 읽었다. 두 이력 실행의 stdout는 0 bytes이며 START/COMPLETE는 stderr에 있다. 목록 또는 CSV 존재만으로 완료를 판정하지 않았다.

| 수정 후 실제 실행 | 결과 | 경과시간 |
|---|---|---:|
| `cargo build --offline --locked --release --example v15_ssprk_coupled_diagnostic -j 2` | exit 0 | 9.1509 s |
| `cargo test --offline --locked --release --test ssprk_transport --test ssprk_coupled -j 2 -- --nocapture` | 7 + 7 passed, 0 failed, exit 0 | 0.5254 s |
| diagnostic `fixed` | 6 COMPLETE 이력, exit 0 | 3.5292 s |
| diagnostic `birth` | 10 COMPLETE 이력, exit 0 | 37.5879 s |

compiler receipt는 Rust 1.94.1, x86_64-unknown-linux-gnu다. 16 energy cells × 8 angular cells, transport threads 1, background panels 128, nonlinear tolerance 1e-15를 사용했다. 초기 기체는 `(x,y,z)=(.075,.12,.03), T=15000 K, a=1/21`이고 native physical c, MD14 source, Verner/Grackle/EOS를 사용했다.

기존 branch 기준은 final HEAD `ddfa6f5210ed6e17b54c0757fc23ed40d16f18c6`, 이전 source/results `806ad09be146486a492f62393e0a2c578330acf5`다. 아래는 새 실행의 **파일 content SHA256**이며 Git commit SHA와 구별한다.

| 수정 후 실제 source | SHA256 |
|---|---|
| `src/axbi_ssprk_driver.rs` | `d9c8d9823b3d3cba88e2bc5d6f0ffc2eab1be3cbf9a37b891cfe66d13776a985` |
| `src/axbi_ssprk_transport.rs` | `c0ce3d0bc431bdb34b1fa1bdeca8ca56239f93aa16fcdf8eb4c49681333f5de2` |
| `examples/v15_ssprk_coupled_diagnostic.rs` | `1f552469b680057dd6f1a5d455113c1b0228ab68434dceb6980aba4469335a00` |
| `tests/ssprk_coupled.rs` | `048ba6414bcc832aa8301b1650e6fa01c525929220fdfd58bb316c871978329c` |

현재 source를 재독해 execution receipt의 8개 native source hash/byte count가 모두 일치함을 확인했다. `axbi_driver.rs` 첫 **98,113 bytes** SHA256는 기존 anchor `fd5b040bceb2134dc92c09f4bf49e6b04be2e8115f553c19fe989f472f32c01d`와 같고, child module 선언/재수출 212 bytes만 뒤에 붙었다. `axbi_physical_birth.rs` 전체 hash는 `3de9ca2dc4a442cb6d4d7fa6eaeb0f993ffc634d6ffdeb2b9410faec38fee0fa`로 보존됐다. source readback은 `COUPLED_REVIEW_SOURCE_READBACK.json`에 있다.

수정 전 source/raw는 `v15_work/execution_coupled_pre_clock/`, 최초 독립 검토는 `v15_work/theory/pre_clock/`에 보존됐다. 아래 수치는 달리 표시하지 않으면 수정 후 실행이다.

## 2. source의 수학·실행 계약

| 의무 | 실제 확인한 동작 |
|---|---|
| 네 기체 unknown | `SsprkContext::evaluate`는 fractions 3개와 w_eV/H 하나로 endpoint gas를 만들고 native domain 검사를 거친다. |
| 공통 기체 중점 | `mid=(old+trial)/2`를 한 번 만들며 그 absorber density를 두 photon FE stage에 공통으로 전달한다. stage 2는 stage 1 photon 결과에서 다시 prepare한다. |
| native 비광학 RHS | `AxbiProvider.point(&mid, nh, nhe, 0, Tcmb, photo=0)`가 기존 `igm_point_rhs`, Grackle Case-A rate와 EOS를 사용한다. CI/RR/DR/CE/FF/CMB 사건·에너지는 같은 중점이다. |
| 사건과 기체 | 평균 `AbsorptionResult`를 기존 `add_absorption_rhs`에 한 번 전달한다. P, threshold binding, excess heat는 같은 photon stage weights를 사용한다. |
| AllMid 관계 | 기존 `compose_source_free_rhs`가 AllMid에서 선택하는 비광학 필드와 새 native 중점 RHS가 일치한다. rate 계수나 EOS를 재정의하지 않는다. |
| geometry/source | 기존 중점 geometry → 화학/광자 → 마지막 geometry 조합, 실제 GL2 birth 위치와 양의 proper-time source weight를 유지한다. |
| accepted dt | `SsprkChemicalReport.dt_s`가 실제 solve dt를 반환하고 additive `BirthMicroSegment::from_rhs_with_dt`가 그 dt를 모든 사건·열 ledger와 report에 사용한다. |
| opt-in guard | AllMid, opacity midpoint, Disabled inner source, serial Jacobian을 요구한다. 기존 `set_source_clocks`의 FLRW/q_ref=0/same_h=false/BASS exclusion 경로를 사용한다. |
| attenuation enum | Exponential/BackwardEuler enum은 이름이 명시된 새 SSPRK API에서만 무시한다. 기존 API byte prefix는 보존된다. |
| 실패 transaction | 성공 전 clone에서만 physical state를 변경한다. macro 실패 시 state와 last_clock_rhs를 복구하며 실제 RHS budget과 시도수는 남긴다. |
| worker 호출 | serial Jacobian helper로 공유 pool의 중첩 transport worker 제출을 피한다. |

clock 수정은 새 child의 구간 계산과 새 diagnostic의 macro dx/actual X에만 적용됐다. 원본 `BirthMicroSegment::from_rhs`는 그대로이며 SSPRK 경로가 새 explicit-dt constructor를 사용한다. constructor의 모든 events/energy 단위 변환은 원본과 같고 dt를 다른 clock으로 다시 계산하지 않는다.

결합식은 root의 `TIME_CENTERED_CONTRACT_KO.md`와 일치한다.

\[
M_*=M_0+hF(M_0,\bar g),\quad M_1=M_0+\tfrac h2[F(M_0,\bar g)+F(M_*,\bar g)],
\]
\[
g_1-g_0=hC(\bar g)+\tfrac h2[Q(M_0,\bar g)+Q(M_*,\bar g)].
\]

고정 support의 매끄러운 branch, 충분히 정확한 nonlinear solve와 각 photon FE stage CFL 아래에서 혼합항 `F_g(C+Q)` 및 `Q_M F`를 포함하는 2차 Taylor consistency가 성립한다. root가 보존한 Wolfram 출력의 h² 잔차 `{0,0}`도 읽었다. 이를 native 시간정확도 증명으로 사용하지 않는다. photon SSP/realizability가 전체 기체 SSP positivity 정리를 뜻하지 않는다.

**Telemetry 범위:** stage max tau/quad defect와 node 수는 수렴해 반환된 accepted chemical segment만 모은다. node 수는 해당 stage들의 누계이고, 버려진 Newton/Jacobian/line-search의 모든 node work 또는 최대 tau가 아니다. residual 호출수는 별도 `rhs_calls`다. 실제 실패 시험은 CFL 명시적 거부와 rollback/budget charging을 확인했다. 자동 subcycling 또는 rate 완화는 없다.

## 3. 실제 clock 결함과 해결

첫 raw 검토에서 source-on 최세분 w/T 기울기는 `2.6586/4.1889`였다. endpoint 회계 결함의 refinement 차이는 w 차이의 0.58%, T 차이의 3.61% 규모라서 Newton tolerance만으로 전체 현상을 설명할 수 없었다. 짧은 실제 segment에서 binary64 `(end/begin).ln()`의 소거오차를 찾았고 root가 한 번의 최소 수정을 승인했다.

최악 상대 log 오차 sample은 `physical_gl2, m=512, step=386, segment=2`다.

| 항목 | 값 |
|---|---|
| begin | `4.76194064268309000e-2`, hex `0x1.8619222842efbp-5` |
| end | `4.76194066233770821e-2`, hex `0x1.86192243464a5p-5` |
| H(mid) | `1.1834967938773352e-16 s^-1` |
| 정확 endpoint의 ln 비율 | `4.127438715637692638508616750982844170742287791888885211…e-9` |
| 기존 실제 dt | `34874947.2579072639 s` |
| 같은 binary64 H의 참조 dt | `34874946.320010778640… s` |
| 기존 dt 오차 | `+0.937896485294 s` |
| 안정식 dt 오차 | `+2.64787e-9 s` |

CSV를 float로 round-trip해 실제 binary64 endpoint를 복구한 뒤 `Decimal.from_float`로 정확히 펼쳐 참조를 계산했다. 같은 산술 순서의 native H 식으로 기존 실제 dt를 bit-identical하게 재현했다. 안정식은 `ln_1p((end-begin)/begin)/H(mid)`다. 실제 sample/hex/reference는 `COUPLED_CLOCK_EXACT_ENDPOINT_REFERENCE.json`에 있다. 이 sample과 accepted dt/ledger 공유를 확인하는 새 native 회귀가 통과했다.

각 level의 자기 실제 endpoint들 및 같은 binary64 H에 대한 midpoint 합을 독립 비교했다.

| m | 수정 전 dt 합 − 참조 | 수정 후 dt 합 − 참조 |
|---:|---:|---:|
| 32 | +1.12335 s | −1.02579e-6 s |
| 64 | +15.02651 s | −4.13305e-7 s |
| 128 | +4.12509 s | −1.20760e-7 s |
| 256 | −3.81739 s | +3.29636e-7 s |
| 512 | +112.28612 s | −4.88281e-7 s |

초기 `+112.28144 s`는 CSV 문자열을 그대로 Decimal로 읽은 진단이었다. 최종 `+112.28612 s`는 실제 binary64 endpoint를 정확히 펼친 값으로 구별한다. 최초 자료와 정확 endpoint 재평가를 모두 보존했다. 총 시간은 약 `8.4495e10 s`이며, 고정밀 물리 H와 같은 binary64 H의 누적 차이 약 `−2.7e-5 s`도 따로 기록해 clock 결함 오차에 합치지 않았다.

**수정 후 5,952/5,952 birth microsegment dt는 실제 endpoint와 native H의 안정식 재계산과 bit-identical**하다. 같은 H를 쓰는 Decimal 참조에 대한 단일 segment 상대 dt 오차 최대는 `2.80388e-16`이다. fixed geometry 504/504 segment도 실제 공급된 `1/(k_ref20*m)` dt와 일치한다. 총 **6,456개 accepted segment의 dt/ledger 일치**를 source와 raw 양쪽에서 확인했다.

수정 전후 fixed-geometry 504행은 `wall_s`를 제외한 모든 숫자 열이 동일하다. 같은 16개 설정의 한 번의 반복으로 결함 해결을 확인했다. 추가 native 캠페인을 요구하지 않는다.

## 4. 수정 후 여섯 독립 사건·에너지 회계

`independent_coupled_audit.py`는 Decimal precision 60으로 raw 숫자를 합산하며 모든 `audit_*`, `owner_*` CSV 열을 계산에서 제외한다. 출력 데이터의 독립 재구성이며 저장되지 않은 정확한 trajectory 복구를 뜻하지 않는다.

\[
Y=\frac{.2454}{4(1-.2454)},\quad e=x+Y(y+2z),
\]
\[
B=\chi_Hx+Y[\chi_{HeI}y+(\chi_{HeI}+\chi_{HeII})z],\quad w_{EOS}=\tfrac32(k_B/\mathrm{eV})T(1+Y+e).
\]

native threshold는 `(13.598434599702,24.587389011,54.41776)` eV다. `K=ΣCE+ΣRRDR+FF`, `R_B=χ·R+χ_HeI D`라 두었다. 원래 V14 auditor의 여섯 항을 새 CSV의 원시 P/C/R/D와 열·냉각량으로 재구성했다.

| 독립 잔차 | 2,488행 최대 절댓값 |
|---|---:|
| 보고 전자수 − `x+Y(y+2z)` | `2.8500e-17 /H` |
| `Δe−Σ(P+C−R)+D` | `1.9389e-15 /H` |
| `photo_binding−χ·P` | `2.0505e-15 eV/H` |
| `ΔB−χ·P−χ·C+R_B` | `2.4590e-14 eV/H` |
| `escape−R_B−K` | `7.9846e-18 eV/H` |
| `Δw_EOS−photo_heat+χ·C+K−signed_CMB+gaswork` | `3.0055e-14 eV/H` |

thermal audit의 w는 T/fractions로 다시 계산했다. 기록된 w를 사용하는 thermal 잔차 최대는 `2.9962e-14 eV/H`이고 w_erg/H 단위 변환과 EOS 일치도 확인했다. `A_j=P_j+C_j−R_j`에 대해 `Δx=A_0`, `YΔy=A_1−D−A_2`, `YΔz=A_2`의 최대 잔차는 각각 `2.1370e-15`, `4.6968e-16`, `4.7287e-18` /H다.

CI floor는 이미 native CI 안에 포함되며 별도 사건으로 중복 가산하지 않았다. CE cap/excluded DR 진단을 실제 채택된 cooling으로 대체하지 않았다. 위 수치는 보존/출력 일관성 오차이며 물리 rate 정확도 또는 시간적분 오차 상한이 아니다. 누적 회계 오차와 단일 Newton norm도 구별한다.

## 5. 광자 inventory 및 실제 row 구조

initial/final active·passive N/U와 boundary N/U를 모두 사용했다. `N=N_active+N_passive`, `U=U_active+U_passive`이며 실제 source increment를 `source−seed`로 계산해 초기 packet을 두 번 가산하지 않았다.

\[
\Delta N+\Sigma P+N_{boundary}-(N_{source}-N_{seed})=0,
\]
\[
\Delta U+W_{photon}+U_{boundary}+P_{binding}+Q_{heat}-(U_{source}-U_{seed})=0.
\]

| 독립 재구성 | 최대 절댓값 |
|---|---:|
| photon N | `1.3712e-16 /H` |
| photon U | `2.0110e-15 eV/H` |
| 전체 에너지, 기록 w 사용 | `2.9234e-14 eV/H` |
| 전체 에너지, EOS로 w 재구성 | `2.9327e-14 eV/H` |
| endpoint cell 합 − active N | `8.3972e-19 /H` |
| endpoint cell Uref 합 × `(a_ref/a)` − active U | `1.4185e-17 eV/H` |

전체 에너지는 `Δ(w+B+U)+escape+gaswork+photonwork+boundary_U−Δsource_U−signed_CMB`로 계산했다. 2,048개 endpoint cell의 N/Uref가 음수가 아니며 저장된 support의 `lo*N<=Uref<=hi*N` 위반이 없다.

16개 history의 2,488 accepted rows, 6,456 microsegment rows, 3,968 birth rows, 2,048 endpoint cell rows의 수량과 join을 확인했다. 실제 segment의 P/C/R/D/열·냉각량을 누적 CSV와 합산하고 birth의 추가 N/U를 source ledger 증가와 대조했다. birth는 직전 source-free segment 끝에 놓이며 세 segment가 macro endpoint까지 이어진다. 누락·중복·순서·final flag 오류를 발견하지 않았다.

실제 boundary/passive N/U는 모두 0이다. 전체 출력 inventory를 포함한 회계가 성립하지만 비영 boundary flux/passive branch를 실행했다고 확대하지 않는다. 이번 CMB는 모두 음수이며 약 `[-1.16176e-4,-3.31361e-8] eV/H`다. 새 실행의 양의 CMB heating 검증으로 표현하지 않는다. 이전 CSV에 없던 photon inventory를 과거에 검증했다는 주장도 하지 않는다.

## 6. 수정 후 채널별 수렴

외삽해를 참값으로 정하지 않고 `p=log2(|q_m−q_2m|/|q_2m−q_4m|)`를 계산했다. 아래는 가장 미세한 세 level이며 모든 값/부호 있는 successive differences는 audit JSON에 있다.

| 채널 | fixed geometry m=64/128/256 | positive seed + DisabledGL2 m=128/256/512 | empty + physical GL2 m=128/256/512 |
|---|---:|---:|---:|
| photon N | 2.0187 | 2.0134 | 2.0426 |
| photon U | 2.0177 | 2.0122 | 2.0392 |
| HII | 2.0188 | 1.9965 | 2.0434 |
| HeII | 2.0062 | 2.0241 | 2.0139 |
| HeIII | 1.9989 | 2.0100 | 0.65, HOLD |
| w_eV/H | 2.0134 | 1.9906 | 2.0340 |
| T | 1.9993 | 1.9752 | 2.0232 |
| HI photo event | 2.0188 | 1.9964 | 2.0434 |
| photoheat | 2.0134 | 1.9999 | 2.0286 |

source-on w의 세 기울기는 `2.1111,2.0662,2.0340`, T는 `2.0352,2.0428,2.0232`다. 수정 전의 마지막 `2.6586/4.1889`는 clock precision 결함의 영향을 받은 관측으로 보존했다. 개선을 원래 방법의 고차 성능으로 해석하지 않는다. source-on HeIII 차이는 `+6.9e-18,−1.39e-17,−3.81e-17,−2.43e-17`로 불규칙해 차수 HOLD다. photon cell L1 N/Uref도 aggregate와 같은 약 2차 경향이므로 총합에서의 우연한 상쇄만으로 설명되지 않는다.

fixed geometry의 총시간은 초기 gas의 native 20 eV rate `k_ref20=1.07788121977394781e-10 s^-1`의 역수, m=8…256의 6이력이다. 초기 photon은 z=20에서 dt_seed=1e16 s의 native MD14 생성량이며 선행 우주론 이력이 아니다. 두 GL2 군은 Δln a=1e-5, m=32…512의 각 5이력이다. 물리 설정·refinement·nonlinear tolerance는 수정 전후 같다.

accepted stage max tau는 `0.4652814346`, nonlinear norm 최대는 `9.97712579e-16`이다. count quadrature 상대결함 최대는 stage1/2 `2.6232e-16/2.3822e-16`, energy는 `5.4347e-16/4.8346e-16`이다. 이 증거의 허용 범위는 정해진 finite/nonstiff 이력과 관측한 출력이다.

## 7. 재현 자료 및 종료 범위

최소 clock 수정 후 공통 중점, event ownership, byte 보존, failure transaction, accepted dt/ledger 및 실제 완료를 뒤집는 blocking defect를 발견하지 않았다. 정확히 실행한 bounded 채널의 결과를 채택하고 clock finding을 닫는 것이 적절하다. 일반 source-on 전체 2차와 source-on HeIII, uniform stiff/CaseB/fullEoR/signed Bianchi/native 일반 4차는 계속 HOLD다. 추가 native 캠페인은 필요하지 않다.

외부 독립 모델의 확정적 심사를 수행했다고 표현하지 않는다. 실제 분리 subagent의 source/raw 검토 범위를 기록한다. 게시·두 cloud 백업·DAG는 root 전달 단계에서 처리하며 본 문서는 외부 저장 완료를 추정하지 않는다.

```bash
python v15_work/theory/independent_coupled_audit.py
python v15_work/theory/independent_coupled_audit.py \
  --raw-dir v15_work/execution_coupled_pre_clock \
  --out-dir v15_work/theory/pre_clock/exact_endpoint_recheck
```

산출물은 `independent_coupled_audit.py`, `COUPLED_INDEPENDENT_AUDIT.json`, `COUPLED_CONVERGENCE_DECOMPOSITION.csv`, `COUPLED_CLOCK_ROUNDOFF_DIAGNOSIS.json`, `COUPLED_CLOCK_EXACT_ENDPOINT_REFERENCE.json`, `COUPLED_REVIEW_SOURCE_READBACK.json`, `COUPLED_INDEPENDENT_AUDIT.stdout`다. 원시 파일 hash/bytes, 최대 잔차 위치, 전체 채널/level, endpoint 사건 분해, stable dt 일치 수와 clock 비교를 포함한다. 최초 검토와 exact endpoint 재검토는 `pre_clock/`에 따로 보존했다.
