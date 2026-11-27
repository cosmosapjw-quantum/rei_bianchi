# BASS_HE EOR_T3 적용성·채널·tail 연구 기록

작성일: 2026-10-03 KST.
판정: CONDITIONAL_APPLICABILITY_CHANNEL_TAIL_THEORY_AND_EVALUATORS_READY.

T2 복구본에서 이어서 핵 궤적의 오차, 출사 채널 분할과 time/impact/energy tail의 조건부 유도 및 reference evaluator를 작성했다. 실제 Coulomb 정확도·물리 적용영역·단면적·전체 이론 종료·독립 심사는 완료하지 않았다. 원 ARSENY 재현이나 범용 원자충돌 라이브러리를 주장하지 않는다.

## 고정 산출물

Archive: BASS_HE_EOR_T3_APPLICABILITY_TAIL_20261003_v1.zip
Bytes: 1934135
SHA256: 874d09c28a8afcb2c382fb661862a4677876b4bcf267acbf97f0a5bb4768fb8f
ZIP entries: 67; manifest payloads: 66.
CRC, 모든 payload hash, 새 디렉터리에서 시험 재현과 실행 뒤 hash를 확인했다.

부모 T2 복구 archive SHA256: 10669704b978cbf0b9027d4b41c8219b34c7260bed3c4b1c7156e0a8bee631e5.
부모 복구32개/T2 51개/T1 50개 manifest payload를 확인했다. 부모 코드는 수정하지 않았고 기존 scientific suite를 반복하지 않았다. 원 DAG16개 node IDs와 requires 및 기존 physical gates를 보존했다.

## 직접 유도한 제한 결과

1. Coulomb center perturbation: 무차원 h_X=-Δ/2-ΣZ/|x-X|에 대해 u,v∈H1이면 |δh[u,v]|≤4 D_X ||∇u||||∇v||, D_X=ΣZ|X-Xhat|. 역삼각부등식과 shifted Hardy inequality로 유도했다. 전역 bounded L2 operator-Lipschitz 가정을 하지 않는다. 두 exact normalized path solutions, 공통 lab/time convention, Hilbert-triple regularity와 각자의 shifted-form norm 상한 G_X,G_Xhat 아래 e_path²≤e0²+32∫D_X G_X G_Xhat dτ다. 실제 G와 물리 path 오류는 아직 미계산이다.

2. 같은 classical force model μ_N Xddot=F(X,t) 안에서 force residual rbar와 tube-local Lipschitz L_F를 사용하면 κ=sqrt(L_F/μ_N)에 대한 majorant는 d0 cosh(κt)+v0 sinh(κt)/κ+(rbar/μ_N)(cosh(κt)-1)/κ²다. 끝점 majorant가 tube radius보다 작으면 bootstrap 충분조건을 만족한다. 안정적 sinhc 평가 및 L_F=0 극한을 구현했다. 이 결과는 quantum nuclear motion의 생략을 인증하지 않는다.

3. time-tail 대 impact-tail 반례: K(t;b)=C/(b²+v²t²)σ_x에서 exact transition probability는 sin²(πC/(ℏvb))다. 각 b>0에서 시간 적분은 유한하지만 2π∫b p(b)db는 로그 발산한다. 실제 He-H 단면적이 발산한다는 주장이 아니다. 초기 event population=0이고 event off-block norm≤C/R^p라면 A=C sqrt(π)Γ((p-1)/2)/(ℏvΓ(p/2)), p_event≤min(1,A²b^(2-2p))다. 이 절대 envelope 경로는 p>2일 때 유한 impact tail을 준다. p=3 비포화 구간에서는 πA²/B²다. leading R^-2 항이 event projector와 commute할 때 그 항은 block-diagonal dynamics로 유지하고 실제 전이 remainder를 제어할 수 있다. 실제 C3는 미확인이다.

4. Impact Bernoulli event의 작은 core는 [0,πb0²]로 감쌀 수 있다. spinless initial-s quantum low-partial-wave core는 별도로 π(L0+1)²/k_N²다. 임의 b0로 양자 low partial waves를 삭제하지 않는다. 물리 outgoing partition·completeness와 omitted-bound upper가 있어야 ionization interval을 계산한다. finite Q norm, positive box eigenvalue 또는 unvalidated CAP loss는 ionization이 아니다.

5. 실제 σ envelope가 주어졌을 때에만 Maxwell energy tail을 incomplete gamma로 평가한다. 분포의 작은 tail을 미지 σ의 상한으로 바꾸지 않는다. Count envelope를 heat/momentum으로 대체하지 않는다. R_CX는 별도 source와 energy/photon owner를 요구한다. reference-path residual + trajectory error와 target-path full lifted residual의 소유권을 구분하여 중복 합산을 거부한다.

전체 가정·유도·단위·한계·계산형은 archive의 math/T3_DERIVATION_KO.md에 있다. 입력 증명과 outward-rounded enclosure가 제공되지 않은 평가 결과는 physical_certificate=false다.

## 구현과 실제 검증

code/t3_core.py의15개 public 함수, create-only CLI, package/ownership 검사기와 tests를 작성했다. 전체 분자 eigensolver, 실제 nuclear force provider나 continuum wave operator를 구현했다고 하지 않는다.

Focused tests: 70 passed, exit0. 44개 행동/ownership 시험은 실제 assertion red 후 green, 나머지26개는 구현 후 독립 수치/edge/CLI 검증이다. 봉인 ZIP을 새 폴더에 풀어70개 재통과(3.26s), 실행 뒤66개 hash도 일치했다. 이 시간을 성능 benchmark로 해석하지 않는다.

Analytic/manufactured checks:
- Gaussian Coulomb expectation9개: radial quadrature 대 erf oracle 최대차4.440892098500626e-16.
- Classical F=-X fixture: 실제 endpoint deviation0.1585290151921035, majorant0.5430806348152438, tube radius0.6. DOP853 대 sin(t) 차4.246603069191224e-13.
- R^-2 pulse, B=10000의 [B,2B] 기여42.983825756173594, nonzero 점근 상수42.983826521222795.
- R^-3 pulse, B=8 tail0.1963282372250342, 조건부 envelope0.19634954084936213.
- 정상 제조 CLI3개 exit0/physical_certificate=false; R^-2만으로 유한 impact tail 요구 및 기존 output 덮어쓰기 exit2.

Wolfram은 scalar ODE/limit/pulse/core 항등식을 확인했다. 최초 removable-singularity 경고는 보존했고 regularized 재계산은 경고 없이 반환했다. 함수해석 가정과 실제 Coulomb upper bounds에 대한 독립 심사는 아니다.

Python3.13.5/NumPy2.3.5/SciPy1.17.0/pytest9.0.2. 실측 CPU quota4 cores, affinity5 logical CPUs, memory4GiB. 새 molecular solve, physical σ/k, cosmological history, Fortran build, MPI run, independent review는 모두0/NOT_RUN이다. binary64/no-fast-math/no-reassociation/explicit backend 유지. 실제 NCP64 성능은 미측정이다.

## 문헌과 비승격

SciSpace는 탐색에 사용하고 원 학술지 초록/HTML을 확인했다. DOI 10.1103/PhysRevA.69.062703은 같은 He2++H1s의 두 quantal 방법 비교이지 semiclassical accuracy 인증이 아니다. DOI 10.1103/PhysRevA.67.052705는 저에너지 HSCC 비교, DOI 10.1103/PhysRevA.26.3164는 별도 radiative charge-transfer 메커니즘의 근거다. 원 수치표/전체 PDF 회수나 외부 physical data admission을 주장하지 않는다. 위 부등식은 자체 유도이며 문헌의 BASS-specific certificate가 아니다.

## gate와 다음 단일 node

C0 physical_ready=false; EOR_THEORY_GATE=NOT_SATISFIED; independent_review=NOT_RUN; scientific_PROMOTE=HOLD; full_C2_closed=false; continuum_certificate=false; full_H_gap_certificate=false; atomic_correlation_established=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.

다음 단일 node: EOR_T4_RATE_EVENT_ENERGY_AND_BIANCHI_INTERFACE. C0 16개 반응의 종/thermal/nonthermal/internal/radiation owner와 rate functional을 연결한다. T3의 count/energy-tail 구분, proper-time/volume과 R2-N/R2-T thermal-bulk 경계를 보존한다. T4/필요한 review 후 I1-I4 기능 구현은 이 대화에서 수행하며 NCP에는 큰 검증·host optimization을 남긴다.

## 배포

이 Git 파일은 additive scientific summary/verification/archive record이며 전체 코드를 개별 Git 파일로 모두 게시한 것은 아니다. 완전한 code/tests/math/contracts/부모원본/실패와재현근거/다음handoff는 SHA-bound ZIP에 있다. ZIP은 승인된 Drive/Dropbox/Library에 저장됐고 두 cloud에서 ACK/object ID/size를 확인했다. 새 cloud restore는 NOT_RUN. 정확한 최종 Git commit/tree와 private provider IDs는 detached DELIVERY_RECEIPT가 소유한다. 봉인 ZIP은 게시 후 다시 쓰지 않는다.
