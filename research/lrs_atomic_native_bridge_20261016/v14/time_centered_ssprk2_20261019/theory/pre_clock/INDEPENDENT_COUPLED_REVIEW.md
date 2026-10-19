# V15 Contract B 독립 source·실행·회계 검토

검토일: 2026-10-19. 검토자: `/root/dropbox_v15_intake` — root 및 실제 구현자와 분리된 subagent. 이 검토자는 native 소스를 수정하거나 native 실행을 추가하지 않았다. 완성된 실제 CSV를 읽는 Python 후처리만 실행했다. GitHub·cloud 변경도 수행하지 않았다.

## 판정

**공통 기체 중점과 native photon SSPRK(2,2)의 결합 구현이 정해진 Contract B와 일치하고, 기록된 16개 bounded native sandbox 이력의 사건·열·광자 회계를 재구성했다.** 양의 초기 광자와 evolving gas를 사용하는 두 대조군에서는 분해능 증가에 따른 약 2차 수렴이 관측된다. 짧은 실제 GL2 source-on에서는 광자, HI/HeI 사건, photoheat 등 분해 가능한 채널의 약 2차 수렴을 관측했다.

**source-on의 모든 기체 출력에 대한 2차 주장은 보류한다.** HeIII의 successive differences는 불규칙하며, 최세분 w/T 기울기를 고차 정확도로 해석할 수 없다. 특히 기록된 매우 짧은 구간의 `(end/begin).ln()` 시계가 binary64 소거오차의 영향을 받는다. 이 실제 시계 진단은 아래에 정량화했다. Newton residual만으로 w/T의 마지막 기울기를 설명하는 것도 근거가 부족하다.

이는 16개 새 sandbox native 이력의 검토다. 이전 NCP 84이력, projection 62행, 제조 76문제와 Python57 검증을 새 실행으로 다시 세지 않는다. 새 NCP 실행은 없다.

## 1. 읽은 실제 실행과 source 정체성

검토 입력은 `v15_work/execution_coupled/`의 실제 command JSON, stdout, stderr, exit, timing JSON, source/execution receipt 및 여덟 raw CSV 파일이다. 명시적인 data-ready 통지 후 수치 판정을 시작했다. `audit_*`, `owner_*` CSV 열은 모든 독립 회계 판정에서 제외했다.

| 실행 | 실제 결과 | 기록된 경과시간 |
|---|---|---:|
| `cargo build --offline --locked --release --example v15_ssprk_coupled_diagnostic -j 2` | exit 0 | 8.8483 s |
| `cargo test --offline --locked --release --test ssprk_coupled -j 2 -- --nocapture` | 6 passed, 0 failed, exit 0 | 0.5220 s |
| `v15_ssprk_coupled_diagnostic fixed` | 6 COMPLETE 이력, exit 0 | 3.2246 s |
| `v15_ssprk_coupled_diagnostic birth` | 10 COMPLETE 이력, exit 0 | 33.2786 s |

두 실제 이력 실행의 stdout는 0 bytes이며, START/COMPLETE 기록은 stderr에 있다. CSV 존재만으로 완료를 판정하지 않았다. compiler receipt는 Rust 1.94.1, x86_64-unknown-linux-gnu를 기록한다. 16 energy cells × 8 angular cells, transport threads 1, background panels 128, nonlinear tolerance 1e-15, native physical c 및 native MD14 source를 사용했다. 초기 기체는 `(x,y,z)=(.075,.12,.03), T=15000 K, a=1/21`이다.

기존 branch 기준은 final HEAD `ddfa6f5210ed6e17b54c0757fc23ed40d16f18c6`, 이전 source/results `806ad09be146486a492f62393e0a2c578330acf5`다. 다음 값은 새 실행의 **실제 파일 content SHA256**이며 Git commit SHA로 혼동하지 않는다.

| 실제 source | SHA256 |
|---|---|
| `src/axbi_ssprk_driver.rs` | `5d09d9b2170d71e091a722aaacd0875bbeba1adea03bd2ffede2d8a6eeaeb8c6` |
| `src/axbi_ssprk_transport.rs` | `c0ce3d0bc431bdb34b1fa1bdeca8ca56239f93aa16fcdf8eb4c49681333f5de2` |
| `examples/v15_ssprk_coupled_diagnostic.rs` | `64c6e231edc2ef0b4eeed57d4822c46355823c91652164bf545e669d91760145` |
| `tests/ssprk_coupled.rs` | `72cc9a25985fafdf401b04c358c8fb5c2fbd686ba1f6f6467e50f9a6a4539d98` |

현재 source를 다시 읽어 execution receipt의 8개 native source hash/byte count와 모두 일치함을 확인했다. `axbi_driver.rs`의 첫 **98,113 bytes** SHA256는 `fd5b040bceb2134dc92c09f4bf49e6b04be2e8115f553c19fe989f472f32c01d`로 이전 원본 anchor와 같다. 뒤에는 새 child module 선언과 report type 재수출 212 bytes만 붙었다. `axbi_physical_birth.rs` 전체 hash는 `3de9ca2dc4a442cb6d4d7fa6eaeb0f993ffc634d6ffdeb2b9410faec38fee0fa`로 보존됐다. 세부 readback은 `COUPLED_REVIEW_SOURCE_READBACK.json`에 있다.

## 2. 실제 구현 계약 검토

| 의무 | source에서 확인한 동작 |
|---|---|
| 네 기체 unknown | 새 `SsprkContext::evaluate`가 fractions 3개와 w_eV/H 하나로 endpoint gas를 만들고 native domain 검사에 통과시킨다. |
| 동일 기체 중점 | `mid=(old+trial)/2`를 한 번 만들고 그 neutral/ion absorber density를 `absorb_ssprk2`에 전달한다. 두 photon FE stage 모두 같은 값이다. |
| native 비광학 RHS | `AxbiProvider.point(&mid, nh, nhe, 0, Tcmb, photo=0)`가 기존 `igm_point_rhs`와 Grackle Case-A rate/EOS를 직접 사용한다. CI/RR/DR/CE/FF/CMB 사건과 에너지가 같은 중점에서 평가된다. |
| 사건과 기체 연결 | 평균 `AbsorptionResult`를 기존 `add_absorption_rhs`에 한 번 전달한다. P는 fractions/electron, threshold binding은 B, excess energy는 w에 일관되게 반영된다. |
| 기존 AllMid와 관계 | 기존 `compose_source_free_rhs`의 AllMid가 선택하는 CI/RR/DR/CE/FF/CMB 필드는 native 중점 RHS와 같다. 새 경로는 중점 RHS를 직접 요청한다. endpoint의 불필요한 비광학 rate 평가를 피하며, rate 계수나 EOS를 대체하지 않는다. |
| source와 geometry | `tentative_ssprk2`는 기존 log-midpoint geometry → 화학/광자 → 마지막 geometry 조합을 유지한다. GL2 node와 양의 source weight는 기존 `PhysicalBirthRule`을 재사용한다. |
| 실제 microsegment | `BirthMicroSegment::from_rhs`는 원본에서 이미 public이다. 각 실제 segment의 반환 RHS와 자체 구간을 사용한다. 마지막 RHS를 macro dt에 곱하지 않는다. |
| opt-in guard | AllMid, opacity midpoint, Disabled inner source, serial Jacobian을 요구한다. `set_source_clocks`의 기존 FLRW/q_ref=0/same_h=false/BASS exclusion 경로를 거친다. |
| scalar attenuation | Exponential/BackwardEuler enum은 이름이 명시된 새 SSPRK API에서만 무시된다. 기존 API byte prefix는 보존된다. |
| 실패 transaction | 성공 전 clone에서만 기체·광자·ledger를 변경한다. macro 실패 시 실제 state와 last_clock_rhs를 복구하며 시도수와 소모한 RHS budget은 남긴다. |
| 실행 병렬성 | serial `jacobian_columns(..., false, ...)`를 사용한다. 공유 worker pool 안에서 다시 광자 worker를 제출하는 중첩 경로를 만들지 않는다. |

같은 중점의 결합식은 `TIME_CENTERED_CONTRACT_KO.md`에 쓰인

\[
M_* = M_0+hF(M_0,\bar g),\qquad
M_1=M_0+\tfrac h2[F(M_0,\bar g)+F(M_*,\bar g)],
\]
\[
g_1-g_0=hC(\bar g)+\tfrac h2[Q(M_0,\bar g)+Q(M_*,\bar g)]
\]

와 일치한다. 고정 support의 매끄러운 branch, 충분히 정확한 nonlinear solve, CFL를 만족하는 조건에서 혼합항 `F_g(C+Q)`와 `Q_M F`를 포함하는 2차 Taylor consistency가 성립한다. root가 보존한 Wolfram 출력의 h² 잔차 `{0,0}`도 읽었다. 이 대수 검산을 native 시간정확도 증명으로 사용하지 않는다.

**stage telemetry의 범위:** `SsprkStageDiagnostics::include`는 수렴해 반환된 accepted chemical segment의 stage report만 포함한다. max tau/quad defect는 그 accepted stage들 사이의 최대값이고, node 수는 그 accepted stage들에서 사용한 수의 누계다. Newton/Jacobian/line-search의 버려진 평가 전체에 대한 최대 tau나 node-work count가 아니다. 실제 residual 평가 횟수는 `rhs_calls`다. 별도 실패 시험은 `AXBI_SSP_CFL` 반환과 physical rollback/budget charging을 검증했다. 자동 subcycling이나 CFL 완화는 없다.

## 3. 여섯 독립 사건·에너지 재구성

`independent_coupled_audit.py`는 Python Decimal precision 60으로 원시 출력 숫자를 읽는다. 출력된 binary64 값을 더 높은 정밀도로 합산하는 작업이며, 저장되지 않은 정확한 native trajectory를 복구하는 계산은 아니다. 기존 V14 `event_energy_audit.py`의 여섯 회계 항을 새 native CSV 필드에서 다시 구성했다.

\[
Y=\frac{.2454}{4(1-.2454)},\quad e=x+Y(y+2z),
\]
\[
B=\chi_Hx+Y[\chi_{HeI}y+(\chi_{HeI}+\chi_{HeII})z],
\quad w_{EOS}=\tfrac32(k_B/\mathrm{eV})T(1+Y+e).
\]

원 native threshold는 `(13.598434599702, 24.587389011, 54.41776)` eV다. `K=ΣCE+ΣRRDR+FF`, `R_B=χ·R+χ_HeI D`라 두고 다음을 구성했다. 모든 사건은 total-H 기준이다.

| 독립 재구성 잔차 | 2,488행 최대 절댓값 |
|---|---:|
| 보고 전자수 − `x+Y(y+2z)` | `2.6803e-17 /H` |
| `Δe − Σ(P+C−R) + D` | `2.1763e-15 /H` |
| `photo_binding − χ·P` | `4.2558e-15 eV/H` |
| `ΔB − χ·P − χ·C + R_B` | `3.4285e-14 eV/H` |
| `escape − R_B − K` | `1.2846e-17 eV/H` |
| `Δw_EOS − photo_heat + χ·C + K − signed_CMB + gaswork` | `4.6267e-14 eV/H` |

thermal audit에서 w는 T와 fractions의 EOS로 다시 계산했다. 별도로 기록된 w_eV/H와 w_erg/H의 단위 변환, EOS 에너지와의 일치도 확인했다. 기록된 w를 사용하는 thermal 잔차의 최대값은 `4.6115e-14 eV/H`다.

종별 사건도 각각 확인했다. `A_j=P_j+C_j−R_j`에 대해 `Δx=A_0`, `YΔy=A_1−D−A_2`, `YΔz=A_2`의 최대 오차는 각각 `2.0119e-15`, `4.5694e-16`, `5.7306e-18` /H다. CI floor는 이미 native CI 사건 안에 포함된 rate 선택이며 별도 사건으로 중복 가산하지 않았다. CE cap/excluded DR는 기존 owner의 진단량이고, escape/thermal 조합은 실제 native 채택된 냉각량으로 만들었다.

이 수치는 보존/출력 일관성 오차다. 물리 rate의 정확도나 시간적분 오차 상한으로 해석하지 않는다. 특히 수천 개 accepted segment의 누적 회계 오차가 단일 Newton norm과 같을 필요는 없다.

## 4. 광자 inventory와 사건의 분리 회계

새 출력은 initial/final active 및 passive photon N/U와 boundary N/U를 함께 기록한다. 따라서 이 16이력에서는 이전 CSV에서 빠져 있던 inventory 항까지 재구성할 수 있다. `N=N_active+N_passive`, `U=U_active+U_passive`를 사용하고 초기 packet은 source ledger의 초기값으로만 처리했다. 이미 초기 inventory에 있는 seed를 다시 source increment에 더하지 않았다.

\[
\Delta N+\Sigma P+N_{boundary}-(N_{source}-N_{seed})=0,
\]
\[
\Delta U+W_{photon}+U_{boundary}+P_{binding}+Q_{heat}
 -(U_{source}-U_{seed})=0.
\]

| 재구성 | 최대 절댓값 |
|---|---:|
| 광자수 회계 | `2.6657e-16 /H` |
| 광자 에너지 회계 | `2.5258e-15 eV/H` |
| 기체+binding+광자 전체 에너지, 기록 w 사용 | `4.5096e-14 eV/H` |
| 같은 전체 에너지, EOS로 w 재구성 | `4.5608e-14 eV/H` |
| endpoint cell 합과 active N 일치 | `8.3972e-19 /H` |
| endpoint cell Uref 합 × FLRW `(a_ref/a)`와 active U 일치 | `1.4185e-17 eV/H` |

전체 에너지는 `Δ(w+B+U)+escape+gaswork+photonwork+boundary_U−Δsource_U−signed_CMB`로 계산했다. 2,048개 endpoint cell의 N/Uref가 음수가 아니며, 저장된 support의 `lo*N <= Uref <= hi*N`를 Decimal로 확인했을 때 위반이 없다.

2,488 accepted rows는 16개 unique history로 정확히 분해된다. 6,456 microsegment의 P/C/R/D/열·냉각 합을 각 prefix의 누적열과 대조했고, 3,968 birth의 실제 추가 N/U를 source ledger 증가와 대조했다. 각 birth는 직전 source-free segment의 끝에 놓이며, 세 segment가 이어져 macro endpoint에 도달한다. 누락·중복·join 오류를 발견하지 않았다. birth proper weight를 별도로 계산한 FLRW H(a)와 비교한 상대차 최대는 `6.36e-16`이다.

실제 passive N/U와 boundary N/U는 모두 0이다. 이 **기록된 전체 inventory를 포함하는 회계**를 비영 boundary flux/비영 passive branch 검증으로 확대하지 않는다. 이번 CMB 항은 모두 음수이며 범위는 약 `[-1.16176e-4,-3.31361e-8] eV/H`다. 새 실행에서 CMB heating 부호를 검증했다고 말하지 않는다.

## 5. 채널별 실제 수렴

외삽해를 참값으로 설정하지 않고, 동일 설정의 연속 세 level에서

\[
p=\log_2\frac{|q_m-q_{2m}|}{|q_{2m}-q_{4m}|}
\]

를 계산했다. 아래는 가장 미세한 세 level의 값이다. 전체 level 값과 부호 있는 successive differences는 `COUPLED_INDEPENDENT_AUDIT.json`에 보존했다.

| 채널 | fixed geometry, m=64/128/256 | positive seed + DisabledGL2, m=128/256/512 | empty + physical GL2, m=128/256/512 |
|---|---:|---:|---:|
| photon N | 2.0187 | 2.0130 | 2.0425 |
| photon U | 2.0177 | 2.0118 | 2.0392 |
| HII | 2.0188 | 1.9959 | 2.0418 |
| HeII | 2.0062 | 2.0239 | 2.0137 |
| HeIII | 1.9989 | 2.0087 | −3.79, 해석 보류 |
| w_eV/H | 2.0134 | 1.9898 | 2.6586, 최세분 해석 보류 |
| T | 1.9993 | 1.9742 | 4.1889, 최세분 해석 보류 |
| HI photo event | 2.0188 | 1.9958 | 2.0433 |
| photoheat | 2.0134 | 1.9992 | 2.0283 |

fixed geometry는 초기 gas의 실제 native 20 eV absorption rate `k_ref20=1.07788121977394781e-10 s^-1`로 정한 총시간 `1/k_ref20`, m=8…256의 6이력이다. 초기 MD14 photon packet은 dt_seed=1e16 s의 source 생성량이며 이를 선행 우주론 이력으로 해석하지 않는다. 두 GL2 군은 Δln a=1e-5, m=32…512의 각 5이력이다.

전체 cell L1 N/Uref 차이도 aggregate N/U와 같은 경향이다. 따라서 광자 총합에서의 우연한 상쇄만으로 2차가 보이는 것은 아니다. 예를 들어 source-on cell L1 photon N 기울기는 `2.1681,2.0848,2.0425`다.

모든 accepted stage에서 tau 최대는 `0.4652814347`, nonlinear norm 최대는 `9.98056255e-16`이다. count quadrature 상대결함은 stage1/2 각각 최대 `2.2911e-16/2.4453e-16`, energy 결함은 `4.8947e-16/4.9120e-16`이다. 이는 이 bounded 실행의 수치 조건이다. uniform-stiff 영역의 정확도를 보증하지 않는다.

## 6. source-on의 미세 기체 채널과 실제 시계 반올림

source-on HeIII endpoint의 연속 차이는 대략 `+1.145e-16,−1.492e-16,−6.24e-17,+8.604e-16`이다. 이 크기는 nonlinear precision과 누적 상태 갱신의 영향을 받는 영역이며, 약 2차의 HeII photo event가 출력된다는 이유만으로 HeIII endpoint도 2차라고 할 수 없다.

source-on의 마지막 w 차이는 `4.26947e-12 eV/H`, T 차이는 `4.3892e-9 K`다. 각 endpoint의 원시 사건·열 ledger로 추론한 기체 변화와 실제 변화를 분해하면, 256→512 차이 중 endpoint accounting defect의 기여 규모는 w에서 `2.47477e-14 eV/H`(0.58%), T에서 `1.5860e-10 K`(3.61%)다. **최종 회계 결함만으로 비정상 기울기 전체를 설명할 수 없다.** 이 ledger 추론은 독립 참해가 아니므로 보정값으로 결과를 바꾸지 않았다.

추가로 **이미 실행된** segment endpoint와 dt를 읽어 native clock을 분석했다. 실제 코드가 사용하는 `(a_end/a_begin).ln()/H(a_mid)`와, 저장된 같은 endpoint의 비율을 Decimal60로 계산한 midpoint 시간을 비교했다. 원본 clock은 매우 가까운 두 수의 비율을 binary64로 먼저 반올림한 뒤 ln을 취한다. 기록된 가장 짧은 segment에서 상대 dt 차이가 `2.69e-8`까지 나타난다.

| m | 실제 dt 합 − 같은 endpoint의 고정밀 midpoint 합 |
|---:|---:|
| 32 | +1.11867 s |
| 64 | +15.02873 s |
| 128 | +4.12041 s |
| 256 | −3.82208 s |
| 512 | +112.28144 s |

총 proper time은 약 `8.44950483e10 s`다. 고정밀 midpoint 합과 짧은 실제 endpoint 구간에서의 고정밀 Simpson 진단 차이는 m=512에서 약 `−2.73e-7 s`다. 이는 검증된 interval bound가 아니라, 실제 clock roundoff와 매끄러운 midpoint quadrature 오차의 규모를 구별하기 위한 후처리다. m=64의 최종 scale factor는 다른 level과 한 ulp 달라, 최종 물리 시간 차이 약 1.22 s도 따로 포함된다.

source-on의 평균 thermal 변화율에 512단계의 시간 편차를 곱한 감도 규모는 약 `2.25e-12 eV/H`다. 최세분 w 차이와 같은 규모다. 이것은 clock 오차가 미세 w/T 추세에 영향을 줄 수 있다는 직접적인 수치 근거이며, nonlinear solver나 물리적 차수를 단독 원인으로 지정할 근거는 아니다. original clock/geometry byte 보존 계약을 이번 검토에서 바꾸지 않았고 native rerun도 하지 않았다. 결과는 `COUPLED_CLOCK_ROUNDOFF_DIAGNOSIS.json`에 있다.

## 7. 남는 판정 범위와 재현 산출물

소스 검토와 실제 raw 회계에서 Contract B의 공통 중점, event ownership, rollback 또는 보고된 실행 완료를 뒤집는 blocking defect를 발견하지 않았다. 위 clock 문제는 미세 source-on 기체 수렴 판정의 **구체적인 precision 제한**으로 남는다. 향후 더 미세한 수렴을 요구한다면 시간 증가량의 안정적 계산과 실제 segment dt를 공유하는 방식이 별도 최소 수정 후보이며, 그때 수정 전 결과와 실행 receipt를 보존한 상태에서 새 결과를 구별해야 한다.

이번 증거로 source-on 모든 출력의 일반 2차, uniform stiff, CaseB, fullEoR, signed Bianchi 또는 native 일반 4차를 승격하지 않는다. 양수성과 보존만으로 시간정확도를 대신하지 않는다. 외부 독립 모델 심사를 수행했다고 표현하지 않으며, 실제 분리 subagent가 수행한 source/raw 검토 범위만 기록한다.

재현 후처리 명령:

```bash
python v15_work/theory/independent_coupled_audit.py
```

완전한 audit script, 원시 파일 hash/bytes, 모든 prefix의 최대 잔차 위치, 전 채널/level 수렴, endpoint 사건 분해와 clock diagnosis는 아래 산출물에 있다.

- `independent_coupled_audit.py`
- `COUPLED_INDEPENDENT_AUDIT.json`
- `COUPLED_CONVERGENCE_DECOMPOSITION.csv`
- `COUPLED_CLOCK_ROUNDOFF_DIAGNOSIS.json`
- `COUPLED_REVIEW_SOURCE_READBACK.json`
- `COUPLED_INDEPENDENT_AUDIT.stdout`

이 검토의 게시·두 cloud 백업·DAG 기록은 root의 전달 단계에 합류한다. 본 문서는 해당 외부 저장이 이미 완료되었다고 주장하지 않는다.
