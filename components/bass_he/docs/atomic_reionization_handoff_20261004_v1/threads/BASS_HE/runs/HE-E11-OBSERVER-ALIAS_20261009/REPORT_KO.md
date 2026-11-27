# HE-E11: E10 live vs E7 endpoint 광이온화율의 paired signal, 원 장부 관측가능성, NCP telemetry 인계

2026-10-09 KST. 상태: **STORED_E10_E7_OBSERVER_ALIAS_AND_PHOTO_SOURCE_DECOMPOSED__OWNER_INTERNAL_NATIVE_VALIDATION_PENDING**.

## 1. 새 연구 질문 및 실제 실행 범위

E10 NCP full-shadow는 원 receiver의 OFF/KF96/GM25 저온 제조모형에서 3×384 accepted step, 동일 정의 50,820비트 비교 PASS를 반환했다. 그러나 원 owner live density에서 얻은 `Gamma_hi/hei/heii`와 E7 cutoff-aware `Gamma_HI/HeI/HeII`는 최대 E7 allowance ratio 3.543295로 다르다. 내부 BH/BY/BZ/bindMicro/thermalMicro와 accepted-stage trace도 E10 native CSV에 없다. 이 연구는 **기존 raw CSV만** 사용해 observer 차이가 paired photoelectron 신호에 주는 영향을 독립적으로 분해하고, 정확히 어떤 추가 native telemetry가 필요한지 판별한다. 기존 full 1,152-step, E6 5,199-row, E7 export, E8 신호 검증은 재실행하지 않는다.

원본 E10 runtime ZIP: 2,528,362 bytes, SHA256 `d2cec9451719d534b78bdd6ebd7570e03697e9fdd69696c24a966c1a25c91598`. 내부 E7 원본 ZIP SHA256 `020a58ebc4c57a89d973fde66fd1cd82cd5bc3e3f3bccf9f8dce8856cb8bfe2a`. 각각 CRC·매니페스트 SHA/size 280/280 및 64/64 확인. 현재 BASS_HE branch observed `857045e0047f29a19fce18bf6d715afd085665c3`, 실제 receiver `39c39eab1cc2f1a215723680accc123e67ef13b6`. 다른 실행계열 E3 remote tolerance `2.5e-23`은 사용하지 않고 **첨부 E7의** `1e-22 + 1e-6 max |Gamma|`를 유지했다.

모든 상태·clock 비교는 CSV의 17자리 표기를 `float` binary64로 복원한 뒤 **비트 비교**한다. 수학적 신호는 그 binary64 값을 `Fraction.from_float`로 exact-rational lift하여 계산한다. 저장된 십진 문자열을 완전한 실수로 취급하거나 차후 과학 참오차라고 하지 않는다.

## 2. 서로 다른 관측기를 명시한 exact algebra

종분율 `x=HII`, `y=HeII`, `z=HeIII`, `fHe=nHe/nH`, photon-induced electron rate `P`의 단위는 electrons/(H s). 두 관측기 `L`(원 native live grid)과 `E`(동일 저장가스 경로의 E7 cutoff-aware Endpoint)를 구별한다.

\[
\nu=(1-x,\;f_{\rm He}(1-y-z),\;f_{\rm He}y),\quad
P_m^{O}=\sum_{i\in\{\rm HI,HeI,HeII\}}\nu_{m,i}\Gamma_{m,i}^{O},\quad O=L,E.
\]

모드별 alias `D_m=P_m^L-P_m^E`와 선택형 모드의 OFF 대비 response `S_m^O=P_m^O-P_{OFF}^O`를 정의하면,

\[
S_m^L-S_m^E=D_m-D_{OFF}
=\sum_i\overline\nu_i\bigl(\delta\Gamma_{m,i}-\delta\Gamma_{OFF,i}\bigr)
+\sum_i\overline{\delta\Gamma}_i(\nu_{m,i}-\nu_{OFF,i}),
\]

여기서 `δGamma_m = Gamma_m^L−Gamma_m^E`, 윗줄 평균은 `m,OFF`의 2점 산술평균이다. 식은 bilinear identity이므로 exact finite data attribution이지만 유일한 인과적 분해가 아니다. RCT 직접 전자 추가는 0; 이 `P`는 photoionization만의 instantaneous source이며 nonphoto CI/RR/DR, total Xe_dot, 적색편이·가열·F09 이력의 대체가 아니다.

**검증**: 3모드×385행의 5개 state/clock을 owner/sidecar/E7 endpoint·history에서 17,325개 exact-bit 비교했고, 원 E10 live Γ와 E7 history Γ 3,465개를 대조했다. ON/OFF 770개 common clock 및 2,310개 background-field bit 확인; 모두 불일치0. 1,155개 mode별 weighted source identity, 770개 ON–OFF paired observer exact decomposition 확인. 새로운 native gas/root/collision solver 호출0.

## 3. 실제 관측기 alias 수치 결과

| 관측 | 최대 원 E7 allowance ratio | 발생 시각 |
|---|---:|---|
| live−Endpoint HI, OFF | 0.996020 | step 5 |
| live−Endpoint HeI, OFF | 2.512049 | step 5 |
| live−Endpoint HeII, OFF | **3.543295** | step 59 |

KF/GM에서도 최대 비는 각각 거의 같은 수치다. `N24` anchor인 `k=0,16,32,...,384`의 **25개 시각**에서 각 모드의 3개 Γ가 live/Endpoint 비트 동일하며, 나머지 **360개 off-anchor 시각에서는 세 종 동시 비트 동일 0회**였다. 이는 원 `Grid::new`의 N24 source/cutoff anchors와 E7의 현재 cutoff/source boundary 추가가 다른 적분 measure를 만들었다는 소스 구조와 일치한다. 같은 가스 경로의 common discretization bias, 정확 연속 photon 스펙트럼 오차를 제한하는 정리는 아니다.

**Paired 전자 생성률**은 alias가 크게 상쇄된다. 저장된 비영 response에서 `|S^L−S^E|/|S^E|` 최대는 KF **0.00684984**, GM **0.00701847**, 모두 **step 24**였다. 이는 바로 step24→25 사이에서 `S` 부호가 음→양으로 뒤집히는 매우 작은 신호 구간이어서 상대비가 분모 때문에 확대된다. 최대 **절대** alias는 step379에서 KF `−4.01739468e−27`, GM `−6.82735182e−26` electrons/(H s). 최종 step384의 source alias와 양 모드의 paired observer-effect는 선택된 source binary64에 대해 exact zero였다. 최종 paired source KF≈`5.43877441e−22`, GM≈`9.24327836e−21` electrons/(H s)로 live/Endpoint 모두 같다. 종별 절대 Γ에서 ratio>1 실패를 paired cancel로 지우거나 허용차를 완화하지 않는다.

120자리 별도 Decimal-from-f64 계산으로 선택한 70개 photo source/paired source를 대조했다. 최대 상대 차이 `<1e−108`. 이는 **같은 저장입력에 대한 대수·산술 검산**이며 독립 원자단면적/ODE/spectral reference가 아니다. 새 Python 시험 18개(초기 RED 및 Green 포함) 통과; 먼저 발생한 test harness Decimal default precision 실패 기록도 보존했다.

## 4. E10 native에서 빠진 5개 내부 장부

`material.rs`의 cumulative `MaterialOwners`는 `nonphoto_binding`과 `nonphoto_thermal`을 보관하고, `radiation.owners.be`는 세 종의 누적 absorbed photon energy를 보관한다. 그러나 E10 원 41-column CSV 및 선택형 RCT sidecar에는 이 **5개 내부값이 출력되지 않았다**.

같은 original photon budget의 저장된 scalar 열을 이용한
\[
B_{\rm sum}^{\rm recon}
=Q_E-E_{\rm active}-E_{\rm out}-E_{\rm redshift}
\]
은 E7 원 `BH+BY+BZ`와 비교할 수 있다. 1,155개 행의 scalar reconstruction은 모든 모드에서 저장 f64 반올림 수준으로 일치했으며, 최대 상대차는 OFF `6.233e−13`(step1), KF `5.649e−13`(step1), GM `6.110e−13`(step1)이다. 절대차는 해당 점에서 약 `1.4–1.5e−29 erg/H`. 별도 새 정밀도 tolerance를 만들어 pass시킨 결과가 아니라 measured roundoff comparison이다.

**중요한 비식별성**: 이 scalar conservation만으로 `BH`,`BY`,`BZ`를 종별로 복원할 수 없다. `Bsum`을 고정하면서 양수 종별 B 벡터를 여러 방식으로 나눌 수 있다. `bindMicro`·`thermalMicro`도 **E10 CSV 열만으로** 직접 읽을 수 없으며, 미시물리 함수를 재호출하는 별도 계산 없이 0으로 채울 수 없다. 원 E7 history에는 5개 모두 있으나 E10 native 측의 실제 identity를 인증하려면 별도의 native `State` 직독 telemetry가 필요하다.

## 5. 다음 NCP bounded telemetry 구현 준비

`native_candidate/e11_native_telemetry.rs`는 원 E10 opt-in shadow example을 **별도 새 실행기**로 복사해 오직 sidecar 두 개를 추가하는 후보 코드다.

- `OWNER_INTERNAL_5.csv`: `step,s,BH,BY,BZ,bindMicro,thermalMicro`, 실제 `state.radiation.be` 및 `state.material.nonphoto_*` 직독.
- `OWNER_ACCEPTED_STAGES.csv`: 기존 `state.accepted_trace` stage count/temperature extrema/continuity summary 직독. 이 자료는 독립 stage root/interval 인증이 아님.
- 기존 `OWNER_NATIVE_41.csv`, `OWNER_SELECTED_RCT.csv`, `STEPS.csv` 기록 로직·상태진화·TOL·origin source·branch/ledger는 그대로다. `READY.json`은 모든 파일 sync 후 마지막 기록. full384는 원 `--authorized-full` gate가 유지된다.

**이 Rust 후보는 이번 ChatGPT 런타임에 rustc/cargo가 없어 컴파일·실행하지 않았다**. Python `e11.verify_telemetry`의 3개 synthetic contract tests만 통과했고, 실제 native evidence가 아니다. NCP가 원 E10 source blob 확인→`cargo build --offline --locked --release --example e11_native_telemetry`→3모드 각2step→실제 E7 history의 5필드 전수 비트 대조 순서로 검사해야 한다. Full3×384의 중복 진화를 새 telemetry 영향 범위로 재실행하려면 이후 별도 명시적 조건과 비용/claim 계약을 유지해야 한다. 기존 E10 1152 accepted steps를 E11의 재실행 결과처럼 기록하지 않는다.

## 6. 다른 연구 스레드의 최신 관계

- bass_cr branch 최신 `58295e59e1c1815832a26769b05a3b5fcb96b47b`: R14 (`19d7a61...`)가 REI 첫 cell의 조건부 continuous Thomson τ 경계를 제시하지만 전역 τ·물리 인증 HOLD. 이 결과를 HE 385시각의 source error interval로 이전하지 않는다.
- rei_bianchi primary branch 최신 `126d01e920a16b8d310b0ce8aed1635b5c9f5565`/BRIDGE16: native 32-step compensation 및 **test-only checkpoint** 의미를 감사한다. E9 Debug checkpoint 비재개와 일치하는 failure policy만 참고하고 다른 고온 FT03 누적오차를 HE의 저온 RCT에 이식하지 않는다.
- WU088_HH 최신 `c455875643a34639f57b24dda2f8d60155addd6c`: NCP 마스터 인계와 Google Drive restore의 범위 명료화; HH ON06G 고온 조건부 source/rate positivity와 low-T HE는 다른 guard/physics. HH photon-moment 인증을 E11에 자동 부여하지 않는다.

## 7. 과학 판정 및 후속 DAG

E11 closed: source/clock identity checked; full saved Γ-observer alias diagnosed; paired photoelectron rate attribution exact for saved f64; scalar absorbed photon energy reconstructed within observed CSV precision; source-bound NCP telemetry candidate and verifier prepared.

E11 OPEN: owner 5field native direct telemetry; accepted-stage independent numeric residual/interval audit; owner live readout adoption; Gamma observer discrepancy target (>1) closure; true-spectrum/time error, calibrated photon first moment/photoheat/recoil; HH/CR/REI global F09 coupling; independent scientific review. `R0 physics: baseline RCT OFF`, `physical/production HOLD`, `actual atomic moments null`, `HE-F2/F09 global OPEN`, `receiver remote owner adoption false`를 유지한다.

우선순위는 **새 원자 theory나 무제한 시간 refinement가 아니라, 동일 source의 native telemetry를 검증하고 owner의 두 Gamma 관측 정의를 명시적으로 등록하는 것**이다. 전체 NCP 실행 및 다음 반환 형식은 `NCP_LOCAL_CODEX_HANDOFF_KO.md`를 따른다.
