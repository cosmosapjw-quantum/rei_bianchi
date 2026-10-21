# 2026-10-21 Sigma–Pi first pilot: 결과와 구현 결정

## 완료 범위

PR199의 v11 native time 진단 이후 사용자가 요청한 새 목표인 non-tilted Bianchi I의 첫 parameter-sweep plot을 완료했다. PR147의 검증 이력이 있는 Einstein–kinetic Python RHS를 그대로 재사용하여 **축대칭 LRS, source-free, 고정 species 할당**에 대한 초기 norm 격자 91개와 사전에 지정한 해상도 확인 3개를 계산했다. 94/94 완료, 실패0, 자동 재시도0다. 기존 native time8/16/32, age32/64, spectral128, v7 benchmark, v8 fixed-model은 재실행하지 않았다.

독립 계약 검토는 실행 전에 PASS_SCOPED_EXECUTION을 부여했고, 독립 C9는 실제 원시 배열94개를 읽고 PASS_SCOPED_PRELIMINARY를 부여했다. 최종 receipt의 bounded repair는 CLOSED_PASS, 열린 지적0이다. 이 새 pilot의 판정과 기존 native age/time HOLD, nonlinear Grackle response NOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED를 구분한다.

- 결과 표: [results/finite_grid.csv](results/finite_grid.csv)
- 전체 격자: [PNG](results/sigma_pi_finite_grid.png), [PDF](results/sigma_pi_finite_grid.pdf)
- 부호 보존 전단: [PNG](results/signed_final_shear_vs_signed_initial_stress.png), [PDF](results/signed_final_shear_vs_signed_initial_stress.pdf)
- 계약: [PILOT_CONTRACT.md](PILOT_CONTRACT.md)
- 이론: [THEORY_KO.md](THEORY_KO.md)
- 검토: [CONTRACT_REVIEW.json](CONTRACT_REVIEW.json), [C9_REVIEW.json](C9_REVIEW.json)
- 실행: [results/STATUS.json](results/STATUS.json), [results/CHECK.json](results/CHECK.json)
- 원 실행 코드: [EXE_SOURCE_MANIFEST.json](EXE_SOURCE_MANIFEST.json), verification/executed_source/
- 후속 운영 수정: [OPERATIONAL_REPAIR.json](OPERATIONAL_REPAIR.json)

## 모형과 축의 정확한 의미

초기 a=1/21(z_bar=20), 마지막 a=1/5(z_bar=4)다. Initial shear orientation은 양으로 고정하고 stress orientation은 양·음 모두 계산했다. 초기 Sigma_F는 0,0.0003,0.001,0.003,0.01,0.03,0.1; |Pi_F|는 0,0.00001,0.00003,0.0001,0.0003,0.0006,0.001이다. Zero stress 중복을 제거해 7×13=91개의 서로 다른 초기값이 된다.

Public norm은 Frobenius convention이다. LRS tensor diag(-s,-s,2s), diag(-p_s,-p_s,2p_s)에서
Sigma_F=sqrt(6)|s|/H, Pi_F=sqrt(6)(8piG/c^2)|sum_A p_s,A|/H^2다.
H와 s는 s^-1, p_s는 J/m^3이다. Einstein coefficient kappa_E=8piG/c^4를 쓸 때는 c^2가 추가되어야 같은 dimensionless Pi다. 기존 PR147 Sigma_half=sqrt(3)|s|/H와의 sqrt(2) 변환도 출력에 보존한다.

Gamma/nu는 collisionless energy·number Legendre hierarchy다. Matter의10%는 canonical massive Vlasov 종에, 나머지는 cold dust에 배분하고 Lambda를 포함한다. Radiation quadrupole 두 종에 동일 k를 주어 초기 signed Pi를 맞췄다. Massive 초기 분포는 isotropic이다. 이 species 할당·정렬 조건 없이 두 norm만으로 일반 Bianchi I 초기자료가 정해지지 않는다. 상세 식·단위·허용 domain은 THEORY_KO.md에 있다.

이 결과는 native H/He ionization/thermal evolution, stellar UV source, polarized Thomson 또는 일반 non-LRS tensor 방향 sweep을 포함하지 않는다. 기존 PR199의 0.005 chemistry criterion을 새 pilot의 해상도 확인으로 대체하지 않는다.

## 저장된 endpoint에서 보이는 물리

아래 signed Sigma는 저장된 s와 H에서 sqrt(6)s/H로 계산했다. Signed Pi도 species stress coefficient를 먼저 더한 값이다. 모든 값은 a=0.2의 실제 계산 endpoint이며 fitting 또는 보간 결과가 아니다.

| Sigma_F,i | Pi_F,s,i | Sigma_F,s,f | Pi_F,s,f | b_f |
|---:|---:|---:|---:|---:|
|0|+0.001|+2.4182144208e-4|+2.3443724709e-4|+1.4091326381e-4|
|0|-0.001|-2.4187073061e-4|-2.3453174581e-4|-1.4092613120e-4|
|0.001|0|+1.1438016260e-4|-1.4431820794e-6|+2.4017758707e-4|
|0.001|+0.001|+3.5614192710e-4|+2.3291383632e-4|+3.8106789503e-4|
|0.001|-0.001|-1.2743084318e-4|-2.3589463950e-4|+9.9274422679e-5|
|0.01|0|+1.1438255107e-3|-1.4409089296e-5|+2.4017927419e-3|
|0.1|0|+1.1449062331e-2|-1.4190845024e-4|+2.4030746148e-2|

첫째, 초기 전단이0이어도 비등방 응력이 전단을 생성한다. 이 모형의 shear equation ds/dt+3Hs=kappa_t p_s와 일치하는 관측이다. 양·음 stress의 끝점은 대략 반대 부호지만 정확한 대칭을 가정하지 않는다.

둘째, 초기 Sigma=0.001에서 음의 Pi=-0.001은 마지막 shear 부호를 바꾼다. 이때 b는 여전히 양수다. b는 누적 anisotropic expansion이고 s=db/dt는 순간값이므로 두 값의 부호가 다를 수 있다. Norm-only panel에서는 전단 방향 변화가 사라지므로 signed endpoint 그림을 함께 제공한다.

셋째, 초기 Pi=0인 세 대표점 Sigma_i=0.001,0.01,0.1의 Sigma_f/Sigma_i는 각각0.1143802,0.1143826,0.1144906이다. 이는 이 고정 모델·구간의 감쇠 관측이다. 초기 stress가0이어도 anisotropic redshifting 이후 stress가0으로 남는다고 가정할 수 없고, 실제 endpoint signed Pi는 음수다.

Isotropic 입력의 최대 |Sigma|는1.48e-19, |Pi|는2.35e-19로 수치 floor 부근이다. 이 점을 작은 physical anisotropy의 탐지로 해석하지 않는다.

전체 격자 그림은 actual samples를 discrete grid positions에 표시하며 축 label은 실제 입력값이다. Signed shear 그림은5개 초기 Sigma 곡선의65개 실제 endpoint를 숫자 Pi축 위에 놓는다. 선은 눈을 돕는 연결선이다. 보간된 등고선·추가 sample·전역 response fit은 없다.

## 검증과 그 한계

DOP853와 rtol3e-11,atol3e-13을 유지했다. 각 trajectory는121개 출력 epoch를 갖는다. 독립 C9가 원시 state와 결과 JSON, tensor contraction, source byte identity를 검산했다.

| 검사항목 | 관측 |
|---|---:|
| 완료 nominal / refined |91 / 3|
| 초기 Sigma calibration 최대 절대차 |1.04e-17|
| 초기 signed Pi calibration 최대 절대차 |8.67e-19|
| Photon/nu number monopole 최대 abs(N0−1) |0|
| 전체 저장 hierarchy의64-node sampled brightness 최소 |0.5496039448|
| Canonical population 최소 |3.56e-65|
| Refined corners의 Sigma endpoint 최대 절대차 |2.18e-13|
| Refined corners의 signed Pi endpoint 최대 절대차 |1.40e-14|
| Refined corners의 b endpoint 최대 절대차 |7.25e-14|
| Refined corners의 H endpoint 최대 상대차 |3.48e-13|

Nominal L8,24×12cells,Gauss3를 세 corners에서 L12,48×24,Gauss3와 비교했다. 사전 기준은 endpoint 절대차2e-6 및 H 상대차2e-6이다. 위 값은 지정한 세 점의 안정성 관측이다. 전체 parameter plane이나 continuum trajectory의 오차 경계를 증명하지 않는다. Brightness 양성성은64개 angular nodes에서 검사했고, 모든 mu에 대한 정리를 주장하지 않는다. H는 Hamiltonian constraint로 구성하므로 residual은 독립적인 동역학 검사와 구분한다.

## 최적화와 경량화의 실제 변경

PR147의 세 kernel, source lock, MIT license를 byte-identical로 재사용했다. Python 최소 의존성만 있어 이번 pilot에는 native chemistry build나 전체 workspace compilation이 필요하지 않았다.

1. 동일 Legendre matrix와 canonical momentum packet, cosmology setup을 worker별 immutable cache에 넣었다. Keys는 물리·격자 구성 인수를 포함한다.
2. Canonical Vlasov moments는 기존 NumPy 벡터 연산을 유지했다. Momentum population을 매 time step 재격자화하지 않는다.
3. 각 IVP의 adaptive error control은 독립적으로 유지하고 persistent process workers로 dispatch했다. 큰 vectorized mega-system으로 묶어 가장 어려운 case가 모든 case의 step을 결정하게 하지 않았다.
4. BLAS/OpenMP/MKL/NumExpr inner threads를1로 제한해 process concurrency와 겹치는 과잉 thread를 방지했다.
5. Input+vendor identity, completed-result reuse, per-case exclusive writes, failed-attempt preservation, 누적 wall-budget debit을 구현했다.
6. Affinity/cgroup CPU와 memory headroom을 읽고, affinity에 속한 CPU tick만 사용해 worker 수를 조절한다. 첫 관측 전에는 한 worker로 시작하며 worker nice=10을 사용한다. 다른 process를 kill/pause/renice하지 않는다.
7. 실제 실행 전 코드는 verification/executed_source에 보존했다. C9 운영 수정 뒤 future resume identity는 wrapper SHA와 Python/NumPy/SciPy semantic version을 함께 비교한다. Executable path와 compiler build string은 환경 진단용으로만 둔다.

Observed sandbox controller wall은2.720931695s, cumulative charged child wall은8.778983764s, 최대worker peak RSS는68,358,144bytes였다. 이 한 번의 관측은 benchmark, speedup ratio,64core scaling 또는 전체 campaign acceleration의 증거가 아니다. 사용자 요청대로 추가 benchmarking campaign은 하지 않았다.

Mechanical tests8개 PASS(0.156s), C9가 승인한 운영 수정 관련3개 PASS(0.049s). 운영 수정과 추가 signed plot은 저장 결과만 사용했고 새 IVP를 만들지 않았다.

## NCP와 후속 실행

Desktop Commander device inventory는 실제 성공했다. 이어진 실행 도구 호출은 월 사용량 cap으로 SSH 실행 전에 거절됐고, 그 제한을 우회하거나 반복 호출하지 않았다. 따라서 이번 대화의 NCP host/job/resource 실제 관측과 NCP 실행은 없다. 이전 연결 실패를 자동 상속한 판정이 아니다.

NCP profile은 up to63 single-thread workers, case60s, cumulative child1800s, controller1200s,128GB급 host reserve16GiB, worker admission budget0.5GiB다. Affinity/quota, measured idle, memory headroom, remaining worst-case budget이 실제 동시 실행 수를 더 제한한다. 다른 Codex 작업이 있다는 이유만으로 전체 STOP하지 않는다. Memory가 허용하면 busy CPU에도 nice worker1개로 전진할 수 있다.

현재94개가 모두 완료되어 새 NCP queue는 없다. Codex 인계는 원시 결과를 자동 복원하고 check/plot을 재생성하는 절차를 제공한다. 동일 완료 case를 빈 results directory에 다시 실행하지 않는다. 새로운 radiation allocation, native H/He/UV coupling, non-LRS 방향 확장은 별도 물리 계약이 필요한 다음 연구다.

