# Non-tilted Bianchi I Σ–Π 첫 pilot: 실제 625조건 결과

## 결과

2026-10-21에 독립적인 signed 초기 조건625개를 z̄=20→4까지 실제 계산하고, Σ₀–Π₀ parameter-sweep 그림과 대표 진화 곡선을 만들었다. 모두 완료되었고 실패0이다. 이번 그림은 원본 REI PR145/147의 **자체 중력·충돌 없는 reflection-even LRS Bianchi I** 모델에 대한 첫 preliminary 결과다. 해당 원본과의 표적 비교 및 구현하지 않은 Astra의 독립 raw 검토를 거쳐 **PASS_SCOPED_PRELIMINARY**로 판정했다.

대표 그림은 [최종 Σ heatmap](results/pilot/plots_v3/sigma_end_heatmaps.png), [Σ·Π 진화](results/pilot/plots_v3/sigma_pi_evolution.png)이다. 두 그림의 PDF와 계산에 사용한 CSV도 같은 폴더에 있다. 전체 endpoint는 [endpoints.csv](results/pilot/endpoints.csv), 수치 요약은 [analysis.json](results/pilot/analysis.json)이다. 원자료625개 NPZ, JSON checkpoint와 stdout/stderr는 최종 dual-cloud 패키지에 모두 들어 있다. Git에는 코드, 검증·실행 receipt, endpoint, 그림과 plot table을 게시하고, 원자료 archive의 정확한 위치/해시는 FINAL_DELIVERY.json에서 연결한다.

## 1. 최신 자료를 종합해 선택한 실행 경로

REI의 branch253개와 PR211개 목록을 마지막 빈 페이지까지 확인했다. 접근 가능한 소유자 repo51개도 열거하고 관련 BASS/VigilODE/배경 공급 경로를 조사했다. 실제 source·receipt의 정밀 확인은 목표와 관련된 branch에 집중했다. Dropbox 관련 폴더40/38개는 has_more=false까지 목록을 확인했고, Drive는 현재 백업 폴더141개 및 기존 LRS13개 하위 폴더의 반환 범위를 확인했다. 다른 대화 검색은 실제 unavailable 오류였다. 전역 파일 내용의 전수 검증으로 확대하지 않았다. 원문 coverage와 오류는 [조사 기록](evidence/intake_stage_A/COVERAGE.json), [백업 intake](evidence/intake_stage_A/INTAKE_BACKUPS.json)에 있다.

최신 PR199 HEAD964b2e3…의 v11 AGE 결과는 이미 time8/16/32를 완료했다. 12 scalar의 인접 차이가 줄어도 원래 .005 기준은 여전히 실패한다. 이 완료 실행을 반복하지 않았다. PR198의 과거246-job 반환은144완료/100 cap미실행/2dependency차단이며 V12 debit200.39897231891518초와 cap180초를 유지한다. 이번625개는 별도 모델·별도 새 pilot 계약으로 실행했다.

회수한 C15 및 PR141/142의 native chemistry–Einstein 결과는 따뜻한 z≈4의 짧은 구간이고, PR149는 고정 배경의 선형 압력 응답이다. 오늘 z20→4 그림으로 이어지는 직접적인 기존 경로는 PR145/147의 positive canonical momentum solver였다. 새 고비용 solver를 재구현하지 않고 원본3개 Python 파일과 원래 cosmology/clock JSON을 byte-identical하게 포함했다. 원본 canonical_fv.py SHA256은 `91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5`다. 출처와 파일 identity는 [SOURCE_ATTRIBUTION.json](SOURCE_ATTRIBUTION.json)에 있다.

## 2. 물리적 정의와 초기조건

기존 저장소의 norm을 유지한다:

\[
|T|=\sqrt{T_{ab}T^{ab}/2},\quad
\sigma^i{}_j=\operatorname{diag}(-s,-s,2s),\quad
\pi^i{}_j=\operatorname{diag}(-p,-p,2p),\quad p=(P_\parallel-P_\perp)/3.
\]

따라서 사용한 두 축은

\[
\Sigma=\sqrt3|s|/H,\qquad
\Pi=\sqrt3K|p|/H^2,\qquad K=8\pi G/c^2.
\]

여기 H와 s는 고유초의 역수, p는 J/m³다. Einstein 계수 κ_E=8πG/c⁴를 쓰면 같은 무차원 Π=κ_E|π|/(H/c)²이다. full Frobenius norm을 사용하는 convention의 두 값은 각각√2배다. 과거 `Pi_*` 압력 column을 무차원 Π로 오인하지 않도록 실제 초기 fields로 변환을 확인했다.

metric은(-,+,+,+), a⊥=a exp(-b), a∥=a exp(2b), s=db/dt다. H0=67.4 km/s/Mpc, Ω_m=.315, Ω_r=9.2e-5, Ω_Λ=.684908, Tcmb0=2.7255K 및 z̄=20→4 clock은 원래 lock이다. 비바리온 massive fraction fm=.1은 Ω_m에서 차감하며 m/Tref=30, isotropic 초기 massive 분포,24×12 canonical cells,Gauss3를 사용한다. γ/ν는 같은 양의 초기 W=1+kP₂를 가진다. Thomson donor나 stellar/ionizing source는 이번 pilot에 들어가지 않는다. 시간에 따라 생기는 massive 및 radiation stress는 Einstein geometry에 계속 feedback한다.

Σ₀∈[0,.004], Π₀∈[0,.001]를 각각13개 크기로 sampling하고, 비영 값마다 shear와 stress 부호를 독립 선택했다. 각 영점은 하나로 합쳐25×25=625조건이다. 초기 k의 최대크기는 .473665761527515이며 원본 .5범위 안이다. 모든 조건의 실제 초기 축 오차는 최대6.505213e-19였다.

두 magnitude가 일반 Bianchi I의 텐서 방향·고유값·응력 조성 전체를 정하지 않으므로, 이 고정 LRS/공통 radiation quadrupole slice가 그림의 정확한 정의다. eps_sigma와 eps_pi를 버리지 않고 네 panel에 표시했다.

## 3. 이론 유도와 구현 경량화

에너지밀도ρ에서Λ를 분리하면

\[
3H^2=K\rho+\Lambda c^2+3s^2,\quad
\dot s=-3Hs+Kp,\quad
\dot\rho=-3H(\rho+\bar p)-6sp,\quad
\dot H=-K(\rho+\bar p)/2-3s^2.
\]

이 식들로 Hamiltonian constraint의 시간미분이0임을 직접 유도하고 Wolfram에서 검산했다. 원전은 Agullo–Olmedo–Sreenath §II의 Bianchi I background 식과 anisotropic-source 보완식이다: https://arxiv.org/html/2003.08428v2 . 논문과 저장소의 norm 차이는 위에서 명시했다.

이번 고정된 조건에서는 γ와ν energy vector가 같고, 홀수 multipole은0이며, number multipole은 geometry·energy에 feedback하지 않는다. thermal state도0이다. 따라서 원본40상태에서 필요한8상태

\[
(H_{ref}\Delta t,b,s/H_{ref},E_0,E_2,E_4,E_6,E_8)
\]

만 적분한다. 이는 해당 조건 아래 방정식의 불변 부분공간을 사용하는 reduction이다. 양의 massive cell population은 원래 canonical 좌표에서 상수이므로 시간 적분하지 않는다.

energy의 짝수 block을 M이라 하고 x=ln(a/a_ref)라 하면 E′=b′ME여서 **E(x)=exp(b(x)M)E(0)**가 성립한다. 원본 helper와 짝수 block을 재사용한8상태 DOP853 구현을 채택했고, 이 행렬지수 식은 독립 검산에 사용했다. DOP853 rtol3e-11/atol3e-13은 유지했다. 원본 `moment_batch`로 output diagnostics를 bounded NumPy 배열 연산으로 계산한다.

독립 trajectory를 process pool에 배분하고 worker 안에서 quadrature와 행렬을 재사용한다. BLAS/OpenMP는 worker당1thread다. SciPy 공식 문서의 `vectorized=True`는 독립 parameter ensemble의 자동 병렬화를 뜻하지 않으므로 사용하지 않는다: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html 및 https://docs.scipy.org/doc/scipy/tutorial/parallel_execution.html . 이번에는 사용자 요청대로 상세 benchmark를 만들지 않았다. 확정한 변화는 상태40→8과 중복 block/준비 작업 제거이며, wall-speedup 또는 peak-RSS 감소는 별도 측정하지 않았다.

## 4. 실제 pilot에서 읽히는 물리

부호를 포함한 S₀=eps_sigmaΣ₀, P₀=eps_piΠ₀, S_end=√3s/H에 대해 전체625점의 원점을 지나는 least-squares 요약은

\[
S_{end}\simeq0.1143802001S_0+0.2418466141P_0.
\]

격자에서 최대 절대잔차3.7065250e-7, RMS1.2309652e-7이다. 최대 |S_end|=.0006997381로 나눈 값은 각각.05297%,.01759%다. 작은 최종값으로 나누어 오차를 감추지 않았다. 이는 실제 격자의 경험적 요약이며, 연속 parameter 영역의 인증된 오차 bound는 아니다.

반대 부호에서의 상쇄 띠는 대략 **Σ₀≈2.11441Π₀**에 위치한다. 실제 격자의 비자명한 최소Σ_end는2.1772649e-6이며 S₀=+.0003333333,P₀=-.0001666667에서 얻었다. 이 점을 정확한 영점이라고 부르지 않는다. 초기Σ₀=0,Π₀=.001에서도 최종Σ가 약2.418e-4로 생겨, 응력의 독립적인 shear 생성 효과가 보인다. 초기Π₀=0,Σ₀=.004에서는 최종Π≈5.77e-6의 반대 부호 stress가 생긴다.

같은 magnitude corner에서 네 부호 선택의 실제 결과는 다음과 같다.

| eps_sigma | eps_pi | Σ_end | Π_end |
|---:|---:|---:|---:|
| +1 | +1 | .0006989996632 | .0002281972125 |
| +1 | -1 | .0002159805906 | .0002398664080 |
| -1 | +1 | .0002153669598 | .0002406528402 |
| -1 | -1 | .0006997380670 | .0002292279667 |

동시에 두 부호를 뒤집은 magnitude도 정확히 같지는 않다. 최대 차이는7.3840374e-7이며 전체 최대Σ_end의.10553%다. LRS에서(-s,-p)는 단순한 공간축 permutation과 동일하지 않아 이러한 비선형 차이를 삭제하지 않았다. 이 결과는 상쇄와 부호 정보를 유지하는 후속 sweep 설계에 직접 쓰일 수 있다.

## 5. 검증과 독립 판정

| 검사 | 실제 최대값 | 고정 기준 |
|---|---:|---:|
| 원본40상태/8상태6사례×65시점 비교 | 2.173e-11 absolute | 1e-8 |
| source H² constraint relative residual | 2.221e-16 | 2e-13 |
| source number monopole 차이 | 0 | 2e-10 |
| L8/L12 두 corner endpoint 비교 | 6.097e-14 absolute | 1e-7 |
| tolerance/10 한 corner | 3.267e-13 absolute | 1e-8 |
| massive directional energy identity | 1.551e-10 relative | 1e-7 |
| 독립 exp(bM) 검산,625조건×4시점 | 6.348e-15 absolute | 독립 numerical consistency |

실제 최소 angular brightness=.5217217396은65저장시점×128 angular node의 표본 진단이다. massive 최소cell population=1.4910262e-30이며 원래 positive quadrature에서 나온다. H와energy의 저장값은 모두 finite/positive였다. Isotropic control은기계정밀도에서 유지됐다.

구현하지 않은 Astra가625개 JSON/NPZ/CSV의40,625시점을 모두 열어 관측량을 원시 state와 원본 moment helper에서 다시 계산했다. 저장Σ/Π/H/E와의 최대차이는0이었다. 원본 비교 NPZ와sourcebytes도 읽고 [FINAL_REVIEW](evidence/final_review/FINAL_REVIEW.json), [addendum](evidence/final_review/FINAL_ADDENDUM.json)에 판정했다. 요청한 tier routing은 Astra계약→lower-tier구현/실행→독립Astra판정으로 실제 수행했다.

## 6. 자원·NCP·남은 연구

실제 샌드박스 실행은affinity9,cgroup quota8CPU,관측 available memory약2.23–2.33GiB 아래에서6–7workers를 골랐다. pilot 본체15.1503초, 최초전체command15.9565초, aggregate child task12.6764초다. 서로 다른 정의의 시간이므로 speedup비를 만들지 않는다. 900초wall/3600초child의 새 pilot 한도 안에서 완료됐다.

NCP용 `run_ncp.sh`는64workers를 상한으로 같은 모델을 실행하고 성공 후그림을 만든다. affinity/quota/CPUidle/메모리를 관측하고 batch마다 배분을 갱신한다. 다른Codex작업이 있다는 이유로 중단하지 않으며, 다른process를죽이지 않는다. nominal256MiB/worker는 계획값이고 실측RSS가 아니다. 완료된 실행의 재개는 identity가같을때만reuse하며 실패/중단row자동retry는없다.

현재 sandbox에는 `/home/cosmosapjw/.ssh/ncp_key`가 없고, 연결된 Desktop Commander는 월 사용량 소진을 반환했다. 따라서 **이번 NCP 실행은 NOT_RUN**이다. 샌드박스의 실제625결과를 NCP/64코어 결과로 쓰지 않는다. 사용자 수동 다운로드·SSH/SCP 없이 가능한 코드·그림·게시·백업을 마무리하고, 지정 접속 명령을 Codex 인계에 넣었다.

이 pilot의 계산 목표는 완료됐다. 다음 과학 확장은 general non-LRS 방향/응력 조성, 산란, 전체 native HHe 피드백을 선택적으로 추가하는 것이다. 원래 AGE 수렴 HOLD, 독립 LRS 광자 source-on 일반 차수/positivity/HHe/EoR/production 관련 HOLD를 이번 배경 그림으로 승격하지 않는다. **production scientific admission은 NOT_ISSUED**다.

게시된 source commit·두 백업 provider ACK·패키지 해시는 [FINAL_DELIVERY.json](FINAL_DELIVERY.json), 단계별 진척은 [DAG.json](DAG.json), 다음 대화용 프롬프트는 [NEXT_THREAD_PROMPT.md](NEXT_THREAD_PROMPT.md)를 읽으면 된다. 최신 branch HEAD는 실제 GitHub ref와 대조한다.
