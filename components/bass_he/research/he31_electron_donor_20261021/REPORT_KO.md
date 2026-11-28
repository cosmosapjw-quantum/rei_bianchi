# HE31 연구·코딩 루프 보고서

## 결과와 연구 단위

HE30의 z20→2 preliminary 자료가 완료된 뒤, 다음 구성적 연구 단위를 실제 코드로
완성했다. H/He ionization history를 검증된 electron donor로 바꾸고, 기존 full40
non-tilted LRS Bianchi I solver의 Thomson hook에 연결했다. 같은 canonical
quadrature의 고정 운동량과 가중치를 미리 구성하는 evaluator를 추가했으며,
NCP용 sweep 설정·협력 실행·재개·그림 경로를 준비했다.

샌드박스에서 실제 복원 history를 사용한 on/off 두 사례와 원본 FV evaluator의
reference 한 사례가 완료됐다. source와 donor 계약, 정확한 대수, 작은 scalar
상태 비교, 저장 결과 재사용을 검사했다. 상세 속도 benchmark나 완료된 HE30
237-case sweep은 실행하지 않았다. 아래 수치는 scoped preliminary 근거다.

새 실제 donor가 제공하는 범위는 z20→4다. z20→2의 기존 HE30 collisionless
그림과 새 prescribed-donor 그림은 서로 다른 입력을 갖는다. 원래 H/He source의
z4 한계를 숨기거나 extrapolation으로 물리 z2 결과를 만들지 않았다. 실제 z2까지
지원하는 H/He source 채택·생성은 다음 단일 의존성이다. 이 단위의 consumer는
그런 입력이 들어오면 같은 API로 z2까지 실행할 수 있다.

## 1. 연구 전에 새 자료를 조사한 결과

관련 GitHub PR/branch, 실제 Drive/Dropbox 목록과 archive를 먼저 조사했다.
세부 coverage와 누락 범위는 `evidence/context/COVERAGE.json`, 최신 branch
관찰은 `evidence/upstream/UPSTREAM_DELTA.json`에 있다. 이 조사에서 확인한
범위를 넘어 모든 대화·모든 저장소를 완전히 읽었다고 주장하지 않는다.

| 관찰 항목 | 이번 관찰과 판단 |
|---|---|
| BASS_HE PR83 | e173f373… 유지; 완료된 HE30 자료를 기준으로 사용 |
| rei_bianchi PR216 | 1f32cc44… 유지; D8 저장 표본 bracket 결과 재사용 |
| rei_bianchi PR215 / ACCEL02 | d669298f… branch와 새 실제 NCP archive를 발견 |
| rei_bianchi PR199 | eb8042b7…로 전진; 새 D8 bracket/게시 commit이며 donor kernel 변경은 없음 |
| 실제 NCP 결과 | ACCEL02 custom 5 cases ×2 steps, a=.1999→.2; 기본729는 REUSED_ALL/jobs0 |
| 새 전자 입력 여부 | ACCEL02에는 명시적인 ne/HeIII donor가 없으며 HE31 실행 증거가 아님 |
| 다른 대화 조회 | 이번 Personal Context 호출은 unavailable; 읽었다고 간주하지 않음 |
| Dropbox | HE direct3278개(6page), REI recursive71, BASS_BACKUPS220 목록 완료 |
| Drive | REI153, HE first1000 목록; HE 전체 coverage는 partial |

새 NCP archive의 SHA256은
`ad92f4207a6845a0326a095cb904792b6d34bf0654f7148fe3c530b47f5e2817`이다.
이 결과는 동시 작업이 실제 진행 중임을 확인하는 자료다. 64-core scaling이나 새
z2 H/He history의 증거로 사용하지 않는다. 개인 대화 원문이나 서명된 다운로드 URL은
Git 산출물에 넣지 않았고, source/coverage 사실만 보존했다.

### 복원한 실제 donor

R15/HG97-B RUN002 FLRW의 `history.npz`를 원본 archive에서 복원했다.
archive SHA, member SHA, 실제 전체 다운로드 SHA를 대조했고 원래 source ODE는
재실행하지 않았다. 원본 member는 1,179,779bytes, SHA256
`93d16f478d2cc28b1f7b3d5287f07432b0e17107b3dd3f684890e77f6133cfa4`다.

16,385개의 edge가 z20→4를 덮는다. 입력은 R15 emissivity, HG97 Case-B,
T=20,000K, clumping3, escape fraction.2의 filling-factor Q model이다.
ionized region에서 HII+HeII, 바깥은 neutral이며 `xHII=xHeII=Q`, `xHeIII=0`이다.
residual electrons, HeIII evolution, 새 thermal feedback을 포함하지 않는다.
원본 `COMPUTED_SCOPED_NOT_YET_REVIEWED` status는 그대로 남겨, 입력 복원과
전자 census 검사만으로 원래 chemistry 전체에 새 인증을 붙이지 않았다.

실제 donor의 FLRW background는 h=.6774, Omega_m=.309, Omega_b h²=.02230,
Y=.2453이다. target의 고정 background와 다르며 평균 scale factor a에서의
일방향 입력으로 사용한다. 광학깊이는 source가 저장한 값 대신 target H로 계산한다.

## 2. 물리 규약과 유도

### 서로 다른 matter/radiation stress

LRS basis `D=diag(-1,-1,2)`에서 `sigma_ab=s D_ab`, `pi_ab^(X)=p_X D_ab`로 쓴다.
본 구현의 Frobenius convention은

\[
\Sigma_F=\sqrt6\,|s|/H,\qquad
P_X=\frac{8\pi G}{c^2}\frac{\sqrt6\,p_X}{H^2},\qquad
\Pi_X=|P_X|.
\]

여기서 p_X는 SI energy density/pressure J m^-3이고 evolution time은 초다.
기존 코드의 proper-time coefficient 8πG/c²를 사용한다. 8πG/c⁴ convention을
추가 c² 변환 없이 끼워 넣지 않는다. radiation을 합칠 때는 signed 값으로
`P_r=P_gamma+P_nu`를 만든 뒤 `Pi_r=abs(P_r)`를 취한다.
`Pi_total=abs(P_m+P_r)`이며 성분 magnitude의 단순 합과 다르다.

이 코드의 matter는 기존 canonical collisionless nonbaryonic massive fraction
fm=.1, m/T_ref=30이다. H/He nuclei는 전자 donor의 baryonic census다. 이 둘을
같은 pressure sector로 취급하지 않는다. 출력은 P_m, P_gamma, P_nu, P_r 및
각 필요한 magnitude를 별도로 보존한다.

### H/He census와 clock

균질하고 non-tilted인 보존 핵 밀도는 a^-3으로 희석된다. 따라서

\[
n_e(a)=a^{-3}\left[N_Hx_{\rm HII}(a)
+N_{\rm He}\{x_{\rm HeII}(a)+2x_{\rm HeIII}(a)\}\right],
\quad N_H=a^3n_H,\quad N_{\rm He}=a^3n_{\rm He}.
\]

H/He fraction의 simplex와 핵 보존을 검사한다. 입력의 단위는 proper/comoving_a3와
cm^-3/m^-3를 필수로 기록한다. cm^-3 proper density의 기존 callback에서

\[
\Gamma_T=c_{\rm cgs}\sigma_{T,{\rm cm}^2}n_{e,{\rm cm}^{-3}},\qquad
\frac{d\tau_T}{d\eta}=\frac{\Gamma_T}{H_{\rm target}},\quad
\eta=\ln(a/a_{\rm ref}).
\]

41번째 진단 상태만 추가했다. 원래 RHS의 첫 성분 `H_ref/H`를 이용해
`tau'=GammaT*rhs[0]/H_ref`로 계산한다. 원래40 physics state와 elapsed-time 의미는
그대로이며, 진단값을 얻기 위한 추가 FV moments 호출이 없다.

보간은 ln(a)에서 comoving electron density a³ne의 PCHIP다. 구간별 overshoot를
피하므로 비음수성과 핵 수로 정해지는 전자 상한을 유지한다. zero knot를 그대로
보존하며 로그 ne 보간을 쓰지 않는다. 단조 knot에서 PCHIP가 shape를 보존한다는
성질과 실제 chemistry의 정확도는 구별한다. 구간 밖 요청은 거절하고 endpoint의
명시적인8ULP 이내 반올림만 경계에 맞춘다. [SciPy 공식 문서](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html)
조회 당시 문서 버전은1.18.0, 실제 검증 runtime은1.17.0이다.

### Photon-only Thomson과 polarization 범위

방위각 적분된 unpolarized elastic Thomson gain kernel에 Legendre mode를
넣으면 gain eigenvalue는 `(1,0,1/10,0,...)`다. 따라서 loss diagonal은
`(0,1,9/10,1,...)`이며 monopole을 보존한다. Wolfram Language의 실제 symbolic
적분과 독립 exact-rational 계산이 이 결과를 확인했다. SI/cgs rate 변환과
전자 dilution identity의 symbolic residual도0이다.

collision-only quadrupole은 `J2=J2_initial exp(-.9 tau)`지만, 전체 Bianchi evolution의
Liouville matrix A와 damping D는 commute하지 않는다. 현재 convention에서
`A02=-2`, `[A,D]02=-9/5`이다. 완료된 collisionless history에 사후 감쇠를 곱해
live coupling을 대신할 수 없다. 구현은 기존 전체 RHS를 직접 적분한다.

Thomson 직접항은 photons에만 들어간다. neutrino와 massive matter는 공통 H와
shear를 통한 간접 변화만 받는다. full polarized Thomson에서는 intensity
quadrupole이 polarization을 만든다. 현재 scalar unpolarized closure가 full
polarized 계의 닫힌 zero-polarization 부분공간이라고 주장하지 않는다.

원전 조사에는 실제 Exa·SciSpace 호출과 Ma–Bertschinger(1995),
Hu et al.(1995), Tram–Lesgourgues(2013), Friedrich et al.(2012)를 사용했다.
논문에서 확인한 규약·구현에서 유도한 관계·실제 수치 근거를
`evidence/physics/SOURCE_MAP.json`에서 구분한다. 새 atomic-rate fit이나 별개의
polarization model을 현재 on/off 비교에 혼합하지 않았다.

## 3. 최적화·경량화·병렬화의 실제 변경

### 고정 canonical quadrature 준비

고정 packet마다 q_perp², q_parallel², normalized w, wq_perp², wq_parallel²를
한 번 구성한다. 상태별 A=e^(-2eta+2b), B=e^(-2eta-4b), C=e^(-3eta)에 대해

\[
E_i=\sqrt{m^2+Aq_{\perp,i}^2+Bq_{\parallel,i}^2},\quad
\rho=C\sum_iw_iE_i,
\]
\[
P_\perp=\frac{CA}{2}\sum_i\frac{w_iq_{\perp,i}^2}{E_i},\quad
P_\parallel=CB\sum_i\frac{w_iq_{\parallel,i}^2}{E_i}.
\]

상태별 packet 작업 배열은2개, sqrt1회, reciprocal1회, dot reduction3회다.
고정 data는 bytes-backed immutable snapshot이고, source object의 나중 mutation과
분리된다. binary64, 원래 packet·Gauss order·normalization을 유지한다.
batch 경로는 최대256상태 chunk와 두 작업 행렬의 기본64MiB 한도를 갖는다.
상주 준비 배열과 입출력·validation·BLAS 내부 memory는 그 두 행렬 한도 밖이다.
RHS는 scalar interface를 쓰며 별도 ODE들을 억지로 같은 time-step에 맞추지 않는다.

원본 mass-shell 합을 독립 미분하면
`partial_eta rho=-3(rho+Pbar)`, `partial_b rho=-6p_m`, `a³n=constant`가 나온다.
원본 evaluator와의 작은 상태 비교 및 이 work identity를 검사했다.
실제 범위 eta∈[0,ln7]에서 parity를 적용한다. eta245 같은 극단 subnormal 영역의
연산 순서 차이는 별도 기록했으며 모든 eta의 상대·bitwise 동등성은 주장하지 않는다.

### Donor 및 실행 경계

PCHIP 계수도 한 번 준비하고, uniform ln(a) grid에서는 scalar interval index를
직접 구한다. 실제 knot 구간을 포함하는지 검사하고 필요하면 searchsorted로
돌아간다. 매 RHS마다 interpolator object나 전체 density table을 만들지 않는다.
actual donor의 준비 배열은917,528bytes다. reference density census의 최대
상대 차이는8.70e-16, 실제 knot 복원의 상대 차이는8.80e-16이다.

입력과 과학 source는 전체 content SHA를 사용한다. rounded-state cache는 없다.
자원/실행 receipt의 hash는 과학 identity와 분리했다. 이미 import된 잘못된 vendor
module을 감지하고, 경로를 우선 배치한 뒤 실제 `__file__`도 확인한다. NumPy scalar
JSON 변환은 payload SHA 계산 전에 수행한다. 성공 결과만 hash·형상·gate·identity를
확인해 재사용한다. 실패/부분 결과는 덮어쓰지 않는다.

### NCP 자원 사용

서로 독립인 parameter case를 process 단위로 분산한다. 기본 상한64worker,
reserve2CPU/16GiB, 각 worker의 BLAS/OpenMP1thread다. 실제 affinity, cgroup quota,
CPU busy fraction, 현재 available memory를 관찰하고 공통 CPU/case lease와
함께 배정한다. 64CPU가 전부 비어 있으면 기본 reserve로 최대62worker가 가능하다.
18-case pilot에는 최대18개만 필요하다. 다른 session 존재만으로 전체 중지하지
않고, 실제 headroom에서 작업한다. 다른 작업에 signal을 보내지 않는다.

아직 시작하지 않은 DEFERRED는 같은 명령으로 재개할 수 있다. 시작 후
FAILED/TIMED_OUT은 PRIOR_ATTEMPT_PRESERVED로 고정되므로 자동 재시도되지 않는다.
원인 분류와 실패 근거 보존 뒤 영향 범위 수정이나 명시적 retry 처리가 필요하다.

128GiB를 일부러 채우는 방식은 필요하지 않다. 반복 계산·임시 배열·중복 실행을
줄이는 것이 이 작은 ODE들의 목적이다. 1GiB/worker는 admission budget이며
실측 RSS가 아니다. 실제 NCP speedup, strong/weak scaling, NUMA bandwidth는
이번 사용자 요청 범위 밖이고 측정값으로 보고하지 않는다.

## 4. 가벼운 검증과 실제 결과

| 검증 | 결과 | 범위 |
|---|---:|---|
| FV moments 원본 대조 | 최대 상대3.69185e-16 | 2분포×6상태 |
| Energy-work identity | scaled residual1.36156e-15 | 원래 mass-shell 합의 직접 미분 |
| Number invariant | 상대4.44089e-16 | 고정 canonical cell 수 |
| Density units/dilution | 최대 상대3.33067e-16 | SI/cgs·proper/comoving |
| Actual donor knots | 최대 상대8.79858e-16 | 16,385행 |
| Collision-only analytic control | 최대 절대7.71605e-14 | quadrupole 및 tau |
| Same-state photon-only RHS | 최대 절대1.08420e-19 | 직접항 species 분리 |
| Target-clock 재계산 | 상대1.11022e-16 | FV call1/augmented RHS |
| Actual prepared/reference receiver | 최대 state 절대1.80300e-12 | 같은 IC·donor, 별도1reference |
| 완료 결과 재사용 | 2 REUSED_COMPLETE, worker0 | 별도 output에서 실제 readback |

계약8항목 중 초기7항목이 통과했고 clock 항목은 새로 정한 absolute1e-18 기준에서
1.73472e-18 residual로 실패했다. 세 binary64 연산과 직접 division의 차이에 대한
`4epsilon*abs(Gamma/H)` 기준으로 교정한 뒤 해당1항목만 다시 확인했다.
solver rtol=3e-11, atol=3e-13은 그대로다. 초기 실패와 교정 사유를 보존했다.

첫 actual paired attempt는 계산 뒤 NumPy2 bool JSON encoding에서 실패했다.
실패 로그·receipt를 보존하고 plain scalar 변환을 고쳤다. 두 영향 case만 새 output과
source identity로 다시 실행해 성공했다. 전체 accounting은 실제 적분 시도5회
(직렬화 실패2, 성공 pair2, 성공 reference1), 보존된 완료 궤적3개다.
이 외의 manufactured collision-only 작은 ODE control1개는 별도 계약 검증이다.

### Actual paired endpoint at z4

초기 `(Sigma_F,P_m,P_r)=(.003,+.0003,-.001)`, L8,24×12 cells,Gauss3,
121저장시점, DOP853 nominal tolerance에서 얻은 값이다.

| 관측량 | Thomson off | Thomson on | on−off |
|---|---:|---:|---:|
| Sigma_F | 1.371710538539e-4 | 1.389026111703e-4 | +1.731557316338e-6 |
| P_m | 1.681387010549e-5 | 1.681374261860e-5 | −1.274868877051e-10 |
| P_gamma | −1.411516294710e-4 | −1.365070457929e-4 | +4.644583678188e-6 |
| P_nu | −9.739524616598e-5 | −9.739589688550e-5 | −6.507195120470e-10 |
| P_r | −2.385468756370e-4 | −2.339029426783e-4 | +4.643932958676e-6 |
| tau_T | 0 | .0372415522066 | +.0372415522066 |

On의 H(z4)=1.3830360904246056e-17s^-1, ne(z4)=2.554436647214177e-5cm^-3,
z20부터 elapsed time=4.280684457609189e16s다. 이 시간은 cosmic age가 아니다.
이 사례에서는 음의 photon stress가 완화되면서 음의 shear source가 작아져,
최종 Sigma가 약1.2623% 커진다. Pi_r magnitude는 약1.9467% 작아진다.
matter와 neutrino의 작은 차이는 직접 Thomson term 대신 공통 geometry의 영향이다.
모든 parameter에서 같은 부호·단조 변화가 생긴다는 결론은 내리지 않는다.

Prepared/reference 같은 donor-on comparison에서 최대 Sigma 절대차는
1.58523e-12, P_m1.34441e-16, P_gamma9.12546e-16, P_nu6.03860e-16,
P_r1.51637e-15, tau1.73476e-13이다. 이것은 한 실제 사례의 동등한 구현 확인이며
새 quadrature convergence sweep이나 독립 물리 인증을 대신하지 않는다.

## 5. 게시·백업·인계

작업은 원래 dirty checkout과 분리한 worktree에서 진행했다. 새 draft PR은
[BASS_HE PR84](https://github.com/cosmosapjw-quantum/BASS_HE/pull/84)이며 PR83 위에
쌓은 branch다. intake snapshot은 `c7dde7753722339a268ee0bb02d6543be88466f9`다.
구현 snapshot, provider ACK, 현재 delivery metadata head는 `delivery/`의 실제
receipt에 기록한다. 실행 당시 uncommitted source였으므로 결과의 content hash를
실행 authority로 보존하고 후속 commit과 연결한다. commit 시간이 실행 시각인
것처럼 표시하지 않는다.

P1은 intake와 복원 원본, P2는 구현·결과·검토·그림·handoff를 보존하는 coherent
snapshot이다. 여러 R/C 단계가 한 snapshot을 공유한다. 이를20개 별도 archive로
표현하지 않는다. archive 내부 과거 DAG와 업로드 후 최종 DAG/ACK의 차이는
운송 완료 시점 차이며, 파일 manifest가 실제 포함 내용을 정한다.

NCP에는 `pilot18_on.json`과 `joint175_on.json`이 준비됐다. 미실행 상태다.
실제 z2 H/He source를 확보하기 전에는 이 설정의 z4를 임의로 z2로 바꾸지 않는다.
후속 연구는 source generator의 z>=4 rate/emissivity support와 더 낮은 z의 source
가정을 먼저 명시하는 하나의 연구 단위로 다룬다. 기존 guard 제거·가짜 donor·완료된
HE30 재실행으로 그 의존성을 대체하지 않는다.

## 원전과 근거

- Ma & Bertschinger, 1995: https://arxiv.org/abs/astro-ph/9506072
- Hu, Scott, Sugiyama & White, 1995: https://arxiv.org/abs/astro-ph/9505043
- Tram & Lesgourgues, 2013: https://arxiv.org/abs/1305.3261
- Friedrich et al., 2012: https://arxiv.org/abs/1201.0602
- SciPy PCHIP: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html
- 실제 retrieval·source scope: `evidence/physics/SOURCE_MAP.json`.
- 독립 donor·prepared·receiver·paired review: `evidence/*REVIEW*`.
- 과학 결과 content authority: `evidence/EXECUTED_SOURCE_MANIFEST.json`.
- 단계별 완료·운송 권위: `DAG.json`, `RESEARCH_LOOP_LEDGER_KO.md`, `delivery/`.

### 최종 전달 확인

구현 commit `1c8a56aac89d0e40ede8770009f80ebca40a4d2c`가 실제 push되었고
119/119 Git blob이 원시 byte 기준 SHA와 일치했다. 최종 P2 archive는
2,832,001bytes, SHA256 `e7a01a46b95ae30820bde7a46a6e94f920474a6e05574b188bb084051b51e577`다.
Dropbox `id:BSpOijBcT10AAAAAAD_hjw`와 Drive `1-3utJjmUyFlzhXymeCcgOurJ02ruzoxC`의
실제 저장 완료를 확인했다. P1 Drive는 응답 미확정 이력을 그대로 보존했다.
전체20stage는 scoped 완료, HE31 NCP 실행과 실제 z2 H/He source는 후속 의존성이다.
