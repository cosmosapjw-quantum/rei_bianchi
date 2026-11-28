# SHARED_C64_R2: 실제 evaluator의 오차 계약과 교차 저장소 연구

2026-09-28. R1 publication/backup 복구 뒤 수행한 bounded 추가 연구. Production solver, 원래 scientific tolerance, 다른 저장소, live VM 설정을 변경하지 않았다. 세 프로젝트의 유휴 상태는 사용자 보고이며 live process census가 아니다.

## 1. 이번에 고정한 외부 상태

GitHub connector로 다음을 읽었다. 아래는 현재 작업에서 직접 읽은 pinned evidence이지, 다른 작성자의 실험을 이 세션에서 다시 실행했다는 뜻이 아니다. 상세 경로와 Git blob은 SOURCE_PINS.json에 둔다.

- BASS_HE PR16 publication `2c3812e390b91b89da1de30988b3933646b79f30`, tree `e96885f705dcaa43861107672fbf6d597051da6d`. 실행 commit은 `6ddc4ff821ab5d1397fbd08493dd3954a89750f1`, tree `e80a9218d9d275546132110605da35160a878bb0`. resume-004는 full216/cloud75/fault52, geometry56/panel-pair28, imported0, checkpoint65results를 PASS로 기록한다. scientific_PROMOTE는 HOLD, CODE-I02 독립 재검수는 남아 있다. 따라서 예전 resume-003 mismatch를 현재 blocker로 재사용하거나 같은 56-action을 다시 시작할 이유는 없다.
- bass_cr PR4 publication `820b3e0a6da9f7a8c8ece8fcbd3afcf3fa9a6dc3`, tree `3cf2a99680001b9da550343136417812429190ca`. F1-R2 `20260928T101921Z`가 F1_ENGINE_ADMISSION_PASS, elapsed1817.893839s를 기록한다. frozen implementation `f1d69165c6d1e799d9474db23166cb665880576f`, tree `5842046d6bf9d4865566dad28a3fec5b22235f41`. 이 run은 exactly-once였고 이미 소비됐다. Capture/F2/F3 또는 자동 재실행은 승인된 것으로 간주하지 않는다. 생산 admission HOLD, all-bound OPEN, b-grid NO_GO는 그대로다.
- WU088_HH PR12 `a49a704bf84fa86c34c16cd26a631dfabfbbc5ab`는 B160 M3A를 완료했지만 B192 M3B는 경쟁 BASS F1 pool 때문에 유효 측정이 없다. R31U 연구 `ff3db87dfbadd5f1eed89b413e5b785baf63a429`, tree `6dbd1fbfa9e0cbfa34f69147178b7954fdafa2b0`는 동일 workload를 이용한 제한된 finalist 재측정과 실제 interpolant derivative 검사를 제안한다.

## 2. 이식할 방법과 이식하지 않을 물리

bass_cr에서 가져올 것은 expensive exact operator preparation과 cache-only reducer의 분리, exact context/time identity, 실제 evaluator의 finite-difference metric 검사다. H/O/D 행렬, scattering channel, physical rates를 가져오지 않는다. 읽은 다섯 metric sentinel residual의 최대는 2.3253812582402828e-9지만 이는 그 엔진의 검증 결과이지 HE bound가 아니다.

WU088_HH의 중요한 반례는 algebraic metric gap 약5.12e-15가 actual derivative defect0.24807을 막지 못했다는 것이다. Hermite 후보도 구조식은 맞춰도 withheld midpoint O/D 정확도가 나빠 거절됐다. 전달할 교훈은 '구조 항등식과 실제 근사 함수의 정확도를 따로 검사한다'이다. 다른 물리 모델의 수치값이나 tolerance는 이식하지 않는다.

HE의 common-contour는 rho 변화가 알려진 analytic kernel에만 들어가므로, 알 수 없는 에너지곡선을 interpolation하는 것보다 강한 오차 계약을 직접 유도할 수 있다. 이 R2의 실질적 신규 연구다.

## 3. 실제 공통-contour evaluator의 rho jet

R, rho는 길이, G(R)는 에너지, A는 에너지×길이이다. 저장된 계산은 R/a0, G/Eh와 A/(Eh*a0)를 사용한다. Static spectrum과 같은-sheet homotopy를 전제로 한 R1 정의를 유지한다.

A(rho)=integral_Gamma G(R) K(rho,R) dR,
K=(1-rho^2/R^2)^(-1/2), Delta=abs(Im A).

0<=rho<=rho_max<r_min=min_Gamma |R|이고 branch를 연속 선택하면 K의 급수와 그 도함수가 compact rho구간에서 uniformly convergent다. G가 적분 가능하므로 미분과 적분을 교환할 수 있다. Simple fold의 G=O(sqrt(R-Rc))는 그 조건을 만족한다.

K_rho = rho/R^2 * (1-rho^2/R^2)^(-3/2),
K_rhorho = (1+2rho^2/R^2)/[R^2*(1-rho^2/R^2)^(5/2)].

따라서 A,A',A''는 같은 spectral trace에 세 kernel을 가중해서 얻는다. 새 spectral solve가 필요 없다. 이 식은 도함수 파일을 별도 보간해 사용하는 것이 아니라 실제 A evaluator 자체의 미분이다. Wolfram과 독립 SymPy에서 두 derivative identity residual0을 확인했다. Wolfram context 연결은 한 번 실패했고 이후 evaluator 호출은 성공했다. 실패를 삭제하거나 첫 호출도 성공한 것으로 기록하지 않았다.

## 4. 연속 정의와 이산 trace bound를 분리한다

q=(rho_max/r_min)^2<1, L_G=integral |G| |dR|라 두면

sup |A''| <= L_G/r_min^2 * (1+2q)/(1-q)^(5/2).

증명은 |1-rho^2/R^2|>=1-q, |1+2rho^2/R^2|<=1+2q를 쓰는 것이다. 길이 h의 rho구간에서 복소 A의 선형보간 L은 Green/Peano kernel로

sup |A-L| <= h^2/8 * sup |A''|

를 만족한다. 실수/허수 각각의 최대값을 따로 합쳐 느슨하게 만들 필요 없이 복소 norm에서 같은 적분 kernel bound를 쓴다. 절댓값의 Lipschitz성으로 |Delta-abs(Im L)|<=|A-L|다. Delta 자체를 보간하면 Im A의 영점에서 cusp가 생기므로 이 논증을 그대로 쓸 수 없다.

R1의 양수 Simpson weight w_j와 A_d=sum_j w_j G_j R'_j K_j에 대해서는
L_d=sum_j w_j |G_j R'_j|
를 대입하면 동일한 유한합 bound가 성립한다. R2 구현은 이 이산 모델을 검사한다. 연속 L_G의 rigorously enclosed upper bound를 계산한 것이 아니다. 실제 total error는 적어도

E_total <= E_spectral + E_contour/quadrature + E_rho_interpolation + E_roundoff

로 분리해야 하고, same-sheet homotopy는 별도의 전제다. 이 연구는 기존의 32/64 수렴검사를 interval true-error bound로 승격하지 않는다.

만일 같은 R_j에서 |delta G_j|<=e_j라는 별도 유효 오차한계가 주어지면

|delta A_d(rho)| <= (1-q)^(-1/2) sum_j w_j |R'_j| e_j.

이는 rho에 균일하다. rho_max/r_min=.75이면 증폭인자는1.511857892다. 그러나 32/64 shared-knot gap 차이를 e_j로 대입한 값은 두 trace 사이의 비교 bound일 뿐 exact spectrum 대비 error certificate가 아니다.

## 5. 원본 14개 trace를 이용한 새 계산

R1 archive의 manifest로 확인한 7개 result 파일에서 32/64 각각의 trace를 읽었다. 원래 CF/Sturm solver 호출은0, cloud 실행0이다. 새 절대 interpolation research budget은1e-5 Eh*a0이며 기존 scientific tolerance를 변경하는 값이 아니다.

각 trace에서 rho in[0,.75ReRc]의 analytic interval bound가 budget 이하가 되도록 이분했다. trace당62~197구간, 각 구간의5개 withheld interior points, 총7970개의 비교를 수행했다.

- 최대 복소 action interpolation 차이9.016531431205941e-6 Eh*a0.
- 관측 error/analytic interval bound의 최대0.9394373138909932.
- 모든 interval의 analytic bound가 지정 research budget 안이며 관측 위반0.
- 실제 evaluator의 중앙 finite difference와 analytic rho jet을 별도로 비교했다. 정확한 per-branch 값은 RESULT_SUMMARY.json이다.
- 원본 trace32/64는 재사용한 과거 독립 trace이며, R2가14개 spectral trace를 새로 계산했다고 하지 않는다.

이 결과는 known kernel을 이용한 off-grid uniform control이 가능함을 보인다. 현재처럼 rho4점이면 직접 vectorized evaluation이 이미 저렴하다. 따라서 새로운 interpolation layer를 production에 당장 추가하거나 전체 wall-time 단축을 주장하지 않는다. 우선 error certificate/validation oracle로 쓰고 큰rho-grid에서 실제 이득을 별도 측정한다.

## 6. 목표 observable 중심의 exact hybrid telescope

Column-stochastic actual event T_e와 approximate event Q_e, probability y0, bounded observable0<=w<=1을 둔다. 아래첨자가 증가할수록 늦은 event다.

prod T - prod Q = sum_e (T_last...T_(e+1))(T_e-Q_e)(Q_(e-1)...Q_0).

lambda_e^T=w^T T_last...T_(e+1), y_e=Q_(e-1)...Q_0 y0라 하면 reversible i<->j event의 signed contribution은

c_e=(p_e-q_e)(lambda_j-lambda_i)(y_i-y_j),

one-way absorbing event는 마지막 괄호가 y_i다. 따라서 delta observable=sum_e c_e가 exact하고

|delta observable| <= sum_e |c_e| <= sum_e |p_e-q_e|.

이 식은 '작은 확률이므로 버림' 대신 population과 downstream observable sensitivity를 결합하는 연구 경로를 준다. 여기서는 p,q 모두를 알아야 hybrid lambda를 계산한다. 실제 production에서 계산하기 전 branch를 생략하는 권한을 얻으려면 lambda/population에 대한 별도 상계가 필요하다. 이 identity를 사전 pruning theorem으로 과장하지 않는다.

2000개 synthetic4-state/12-event chain에서 exact identity의 최대 float residual3.7556763254897874e-16, bound 위반0. weighted/global bound ratio 중앙값0.024942019926149896였다. 이 수치를 실제 He cross-section 오차나40배 speedup으로 해석하지 않는다. 어떤 atomic probability나 Eq55 production도 계산하지 않았다.

## 7. 이제 세션이 idle일 때의 운영 변경

같은 현재상태에서 모든 세션을 다시16workers로 시작하지 않는다. HE의 이전16worker plateau와 resume004의32worker 선택은 서로 다른 측정 receipt다. HH는64x1/32x2 등의 workload를 갖고 CR F1은60worker exactly-once였다. Raw cases/s 단위도 프로젝트별로 다르다.

HH m3_throughput.py의 measured_task_count=max(24,2P),12pair cyclic mix를 직접 읽었다. 64worker128tasks는 type별10/11회,32worker64tasks는5/6회다. 이는 동일pair-frequency 분포가 아니다. 12pair를11회씩132tasks로 통일하면 분포 차이를 없앨 수 있지만132개의 새 scientific pair가 되는 것은 아니다. 현재 owner의 승인된 M3B 계약을 수정하지 말고 별도 amendment로 다룬다.

권고 순서:
1. 한 coordinator가 read-only live census와 각 owner의 다음 승인 node를 확인한다. 유휴라는 보고만으로 남은 process/lease를 지우지 않는다.
2. 이미 종료된 CR F1-R2와 HE resume004는 현재 closure의 역사적 검증으로 보존하고 재실행하지 않는다. BASS_HE의 즉시 다음 node는 CODE-I02 focused independent rereview다.
3. HH의 미완료 M3B에는 짧은 BENCHMARK_EXCLUSIVE 창을 배정하도록 owner와 조정한다. 이 연구 thread가 HH node를 실행하거나 재승인하지 않는다.
4. 병행 생산/연구 epoch는 실제 job-local cpuset/quota, threadteam, memorypeak에 맞춰 예약한다. Exclusive benchmark 결과와 shared-condition 결과는 다른 performance binding으로 관리한다.
5. pending native task의 출력을 준비하고 reducer를 cache-only로 돌리는 CR 패턴을 HE 공통-trace layer에 적용할 수 있다. Missing key는 실패하거나 명시적으로 준비하며 reducer에서 몰래 새 solver를 호출하지 않는다. Reviewer의 독립 재현은 이 cache를 읽었다는 이유로 대체하지 않는다.

동일ancestor memory.current를 각세션 몫으로 중복계상하지 않는다. TTL만료는 liveworker 자원을 재할당할 충분조건이 아니다. 다른owner 프로세스 kill/강제 cgroup이동, cloud자원 변경, systemd설치/시작은 수행하지 않는다. root CB1에 mkfs/repartition하지 않는다.

## 8. 결과·검증·남은 조건

새12 tests는 missing implementation에 대한12 FAIL(exit1) 뒤 같은 command12PASS(exit0)였다. 연구 data replay는exit0. 기존 scientific suite는 dependency를 바꾸지 않았으므로 재실행하지 않았다. New code는 research/ namespace에만 게시한다.

R1 archive는 기존두 provider object를 metadata확인했고 중복업로드하지 않았다. R2 archive에는 R1 archive를 그대로 포함해 복원 가능한 연구문맥을 보존한다. 새R2 backup은별도 receipt에서 실제ACK 이후에만 완료로 기록한다.

CODE-I02 independent review, common-contour same-sheet homotopy, 전체rho domain, exact-spectrum/interval rounding은 미완료다. scientific_PROMOTE=HOLD; Eq55=NOT_RUN; continuum=NOT_ADMITTED. 이번 replica/수식검산이 독립decisionreview는 아니다.

## 재현

R2 directory에서:

python -m pytest -q test_error_envelopes.py
python evaluate_r2.py --r1-root <unpacked-R1>/shared_c64_research_20260928 --out RESULT_SUMMARY_NEW.json

`RESULT_SUMMARY.json`은보존하고 재현출력은다른파일로쓴다. R1은archiveSHA 및manifest를먼저확인한다. /mnt/data 또는실서버경로는독립환경의위치이며동일하다고가정하지않는다.
