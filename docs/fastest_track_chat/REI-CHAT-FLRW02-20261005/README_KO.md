# REI-FLRW02: 세 방정식의 source-bound 복원 검증

2026-10-05 KST. **기존 원자 공급기와 H/He 사건 함수에 연결한 국소 photoionization–recombination 방정식, spectral edge를 명시한 FLRW 광자수 방정식, 조건부 sharp-phase filling-factor 환원을 이론·native 코드·독립 수치 검산으로 확인했다.** 기하학적 ionization front의 운동이나 실제 EoR history 전체를 구현한 결과는 아니다.

## 판정부터 읽기

| 대상 | 이번 판정 | 실제 증거와 조건 |
|---|---|---|
| 국소 이온화율 | implementation-verified / numerically checked | 실제 `AtomicProvider → hhe_rhs`와 `homogeneous_photo_rates`를 연결. 순수 H, 지정 Case-A/B, proper density와 선택적 충돌이온화 |
| 광자수 방정식 | implementation-verified / numerically checked | proper/comoving 변환, 동일 spectral edge flux의 group 간 상쇄, threshold exit와 upper inflow. prescribed spectrum의 실제 시간 적분까지 수행 |
| filling-factor 표준식 | derived / conditional implementation-verified | \(X_M=Q_V\Delta_I\)의 외부 sharp-phase 선언과 밀도 변화율을 받는 inventory 환원. 실제 front geometry/속도는 미구현 |
| 일반 Bianchi·physical EoR·엄밀 구간 인증 | unresolved / not claimed | 이번 finite point·controlled trajectory 검증으로 승인하지 않음 |

FLRW geometry만 취한다고 세 식의 모든 closure가 자동 성립하지 않는다. 특히 local x, \(X_V=\langle x\rangle_V\), \(X_M=\langle n_Hx\rangle/\langle n_H\rangle\), geometric \(Q_V=\langle b\rangle\)를 구분해야 한다. 문헌의 Q도 정의가 다르다. Gnedin–Madau 2022에서 Eq32 다음 Q 정의는 \(X_M\)이고, 이를 geometric filling factor로 읽으려면 추가 조건이 필요하다.

## 네 스레드의 최신 상태와 이번 증분

| 스레드 | 관측 HEAD | 검토 결과 |
|---|---|---|
| rei_bianchi | `aa3e98d7` | F03 유지. 다른 스레드의 FLRW02 source algebra·ranked sharp capacity 연구가 추가됨. 그 prepared probe는 미실행; 이번 native 검증은 별도 증분 |
| bass_cr | `4a1db971` | F03 exact event·residual projection 연결. CR-OFF dispatch의 native 증거는 별도 필요 |
| WU088_HH | `5731c27f` | actual 7-coordinate optional HH source jet와 보고된 Python 24 tests. 소비기 미연결·domain 대기 유지 |
| BASS_HE | `97b38bbd` | matched absorption·부피·잔차 투영 추가. owner native coverage 재사용 지침, RCT 제외·opt-in 조건 유지 |

Exact branch/commit/blob와 읽은 자료는 `survey/`에 있다. REI crate 24/24 파일을 Git blob identity와 대조했다. 이번 구현은 기존 24개 중 `lib.rs`의 additive export 외 23개를 그대로 보존하고 모듈·시험·probe를 추가했다. CR/HH/He의 기존 과학 suite나 Peebles 대조를 재실행하지 않았다.

## 세 식과 연결 장부

자세한 정의·경계항·유도·단위 검사는 `theory/THREE_EQUATIONS_DERIVATION_KO.md`와 `THREE_EQUATIONS_CONTRACT.json`에 있다. metric은 (-,+,+,+), 시간은 proper seconds다. native atomic density는 proper cm^-3, alpha와 collisional coefficient는 cm^3/s다.

순수 H에서 \(n_e=n_Hx\)이고 핵수 보존식과 HII 보존식을 나누면

\[
\dot x=(1-x)\Gamma_H+k_{\rm ci}n_Hx(1-x)-\alpha n_Hx^2.
\]

분율에 별도 \(-3Hx\)는 없다. 실제 재결합률의 전자 밀도를 고정하면 마지막 항의 x 의존성이 달라진다. 시험에서는 기존 fixed-ne F02를 nonlinear pure-H 기준식으로 대신하지 않았다.

광자 spectral number density \(n_E\)가 proper cm^-3 eV^-1일 때, 고정 proper-energy group의 comoving count \(N_g=a^3n_g\)에 대해

\[
\dot N_g=a^3(S_g-A_g)+F_{g+1}-F_g,
\qquad F_g=a^3H E_g n_E(E_g).
\]

proper density는 ​\(\dot n_g=\dot N_g/a^3-3Hn_g\)다. 이 native 모듈의 \(N_g\) 단위는 reference comoving cm^-3이며 기존 cMpc^-3 API와 구분한다. 기존 photo bridge를 호출할 때 cMpc 변환을 명시적으로 수행한다. Group 평균만으로 \(n_E(E_g)\)를 추정하지 않고 spectrum/reconstruction 입력을 요구한다.

동일 H absorption 사건을 matter와 photon 양쪽에서 사용하면, 고정 co-expanding cell 평균과 경계 matter flux가 없는 이번 코드 범위에서

\[
\frac{d(X_M+\eta)}{dt}=s-r+c_{\rm ion}-a_{\rm other}-\ell_z,
\qquad\eta=\frac{\langle n_\gamma\rangle}{\langle n_H\rangle}.
\]

여기서 r은 선언한 photon ownership에 따른 net recombination sink다. Case-A primary-only 모형에서는 재결합 복사를 tracked field 밖으로 내보낸다. Case-B local OTS에서는 제거한 ground-recombination photon을 다시 source에 더하지 않는다. 기존 `hhe_rhs`의 thermal/escape-energy 출력은 새 Case-B number adapter에서 사용하지 않으며, 열·방출 spectrum의 closure 검증도 주장하지 않는다.

Sharp fully-ionized/neutral phase가 시간 구간에 유지되고 ionized conditional density contrast \(\Delta_I\)와 그 미분이 외부에서 정해졌다면

\[
X_M=Q_V\Delta_I,\qquad
\dot Q_V=\frac{\dot X_M-Q_V\dot\Delta_I}{\Delta_I}.
\]

이를 \(\Delta_I=1\), \(\dot\Delta_I=0\), negligible photon-storage derivative·threshold/other losses, Case-B 및 지정 recombination average로 제한하면

\[
\dot Q_V=\frac{\dot n_{\rm ion}^{c}}{\bar n_H^{c}}-\frac{Q_V}{t_{\rm rec}}
\]

가 복원된다. 이 검증은 조건부 moment/inventory 환원이다. 단일 시점에서 binary인 cell에 local x-dot를 계산한 사실만으로 front가 유지되거나 geometric Q-dot가 독립적으로 결정되었다고 주장하지 않는다. 새 helper는 \(0<Q_V<1\), \(\Delta_I>0\), \(Q_V\Delta_I\le1\), mass closure와 명시적 phase 선언을 확인한다. Endpoint의 phase 생성·소멸은 별도 과제다.

## 실행한 코드와 검증

실제 저장소 변경 위치는 `rust/rei_microphysics/{src/flrw_three_equations.rs,src/lib.rs,tests/flrw_three_equations.rs,examples/flrw_three_probe.rs}`다. Rust 1.94.1로 실행했고 crate에 새 외부 dependency는 없다. Probe는 `cell`, `photon`, `ensemble` 모드를 제공한다.

| 검증 | 최종 결과 |
|---|---:|
| 원본 crate의 새 API import | E0432, exit 101: 구현 공백 확인 |
| 새 native tests | 21 PASS |
| 최종 통합 crate | 84 PASS: 기존 63 + 신규 21 |
| 70자리 Decimal 독립 대조 | cell 144점 + photon 24점 + ensemble 4사례, 2352 checks PASS |
| native photon 시간 적분 | 570 RHS calls, RK4 16/32/64 step 및 DOP853 PASS |

국소 RHS의 최대 gross-flux-scaled 오차는 9.06e−16, photon proper-density RHS는 2.31e−16이다. 사전 기준은 2e−12다. Decimal oracle는 Rust가 반환한 atomic coefficients를 입력으로 받되 event stoichiometry·평균화·comoving 변환은 독립 계산한다. 기존 raw fit의 원전 정확도를 새로 검증한 것으로 집계하지 않는다.

Negative controls는 추가 -3Hx, comoving -3HN, threshold exit 누락, edge 부호 반전, fixed-ne 재결합 치환, mass/volume 평균 혼동을 검출했다. 한 사례에서 \(X_V=0.56\)인데 \(X_M=0.8094017094\)였다. 동일 photon bin count를 가진 descending-triangle spectrum과 endpoint-zero parabola는 threshold flux가 달라졌다. 이는 edge closure가 bin count만으로 결정되지 않는다는 직접 반례다.

E3는 \(a=a_0e^{Ht}\), spectral number density \(n_E\propto E^{-3}\), 흡수·방출 0, 고정 유한 energy band의 controlled FLRW 문제다. 상단 밖 power-law tail에서 오는 유입도 포함한다. 해석해는 각 bin \(N_g(s)=N_g(0)e^{-2s}\), \(s=Ht\)이고 proper density는 초기값 대비 \(e^{-5s}\)다. 실제 native RHS를 호출한 RK4 최대 상대오차는 16/32/64 steps에서 1.449e−6, 8.688e−8, 5.318e−9로 줄었고 감소비는 16.68/16.34다. DOP853 오차는 1.363e−11이었다. 그림과 CSV는 `evidence/flrw_photon_recovery.*`, `photon_history.csv`에 있다. 실제 재이온화나 photon–matter coupled history로 부르지 않는다.

## 수정·미수행·검토 경계

독립 oracle의 첫 실행은 photon-mode comoving N을 proper n으로 잘못 사용해 실패했다. 원 실패 결과를 보존하고 oracle의 dilution 변환만 수정했다. Native에는 이 오류가 없었으며 tolerance는 바꾸지 않았다.

독립 reviewer는 public `Ensemble` 입력의 NaN이 phase mass 비교를 우회하는 구현 결함 IR-F01을 발견했다. 두 public helper와 ensemble에 들어가는 개별 public CellResult의 finite/domain 검사 및 반례 시험을 추가해 닫았다. `coding/NATIVE_IMPLEMENTATION_STATUS.json`은 수정 전 full82와 수정 후 targeted20의 작업자 기록이며, **최종 통합 권위는 `evidence/FINAL_INTEGRATION.json`과 `final_crate.log`의 full84**이다. 같은 최종 binary로 E2/E3도 실행했다.

Rustfmt는 복구된 실행환경에 없어 수행하지 않았다. 구간 전체 오차 증명, 일반 Bianchi anisotropic spectrum, selected-He/RCT admission, phase-front solver, physical source fit 오차, 재이온화 관측량은 이번 완료 범위 밖이다. 기존 strict local error<2e−4, public width<2e−3와 [160,161] 실패 기록은 그대로 보존했다.

## 재현·후속·게시

`coding/README_NATIVE_KO.md`는 native 명령·입출력 계약, `research/`는 동결 계획과 독립 실행기, `review/`는 독립 판정, `publication/`은 다음 handoff·DAG·low-cost entry다. Science payload에 compiled target 또는 runtime/toolchain을 포함하지 않는다. 문서에 쓰인 local runtime 경로는 당시 실행 provenance이며 재현자는 자신의 cargo/Python/probe 경로를 지정한다.

최신 동시 갱신의 다음 task ID `REI-CHAT-FLRW03_EXPANDING_ADAPTER_AND_INTEGRATED_BUDGET`를 보존했다. 그 문서의 미실행 prepared probe를 이번 결과로 소급 승인하지 않는다. 현재 F04 production 작업을 이 diagnostic pass로 완료 처리하지 않는다. 다음 과제는 production call-site에 모델·단위·source ownership을 결속하고, 실제 spectral edge reconstruction 및 phase-density/front law를 명시하는 일이다. 원자 CR/HH/He의 중장기 lane은 필요한 source/domain이 발생할 때 다시 호출한다.

같은 GitHub 연구 branch의 기존 PR83에 실제 코드를 게시한다. Drive와 Dropbox의 `REI_FLRW02_THREE_EQUATIONS_20261005_v1` 폴더에는 같은 immutable core archive와 machine-readable 자료를 저장한다. Remote upload/size verification과 full restore verification은 별도로 기록한다. 새 백업을 되돌릴 때는 이 새 폴더만 삭제하며 이전 백업은 보존된다.
