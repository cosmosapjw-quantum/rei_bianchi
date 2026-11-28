# C1b 독립 검토

**판정: ACCEPT_SCOPED_R2_EMPIRICAL_CONVERGENCE.** `C1B_R2_REFERENCE_CONVERGENCE_CLOSED`를 인정한다. 범위는 R=2 a_A, Z_A=1, Z_B=2의 fixed-sector ground/bright pair에서 명시한 energy·angular coupling·commutator 기준과 실제로 시험한 refinement다. 엄밀한 continuum error enclosure나 R 전역 정확도는 인증하지 않는다. 다음 단일 의존성은 C2의 구체적 실행 계약이며 C2 physical grid는 이번에 실행하지 않았다.

검토자는 solver·pilot을 작성하지 않았고 새 physical solve를 실행하지 않았다. 직접 수학 검산, code-path inspection, 실제 결과의 사전 tolerance 재계산, 24개 저장 state array의 size/SHA256 검사, 실행 당시와 전달용 코드 identity 대조를 수행했다. 원 C1의 실패·단위검사와 원전 provenance를 재사용했으며 기존 과학 suite는 반복하지 않았다. Git 게시·백업·remote restore는 이 과학 검토의 범위가 아니다.

## 수학과 구현

B 중심으로 수치 구면 좌표를 옮겨도 축방향 평행이동은 m sector를 보존한다. 물리적 charge-center 연산자는 정확히 L_y(O)=L_y(B)+z_B p_x다. 직접 momentum 구현은 radial derivative와 angular selection |ℓ−k|=1을 사용하며 energy gap이나 force로 정의되지 않는다. 부호, azimuth의 1/√2 인자, positive meridional phase 및 a_A,E_A,ℏ 단위 복원을 확인했다.

Off-center force의 Q=A_ℓ0 A_k1√(1−η²)는 endpoint에서 소거된다. Unit-charge W=−1/r_C에 ∂ηW=−s_C r/r_C³를 적용하면 T_C=(√2 s_C)^−1 Σ∫u_g u_b∫Q′W가 된다. Q′의 유한 차수 때문에 필요한 potential multipoles도 유한하다. Cusp endpoint에서도 QW→0이므로 부분적분은 정당하며 중심 s_C=0은 별도 radial 식을 사용한다. 이 force assembly에는 direct operator나 eigenenergy가 들어가지 않는다.

다만 force moments가 Hamiltonian의 Coulomb multipoles를 공유한다. 특히 같은 ℓ cutoff에서 L_B는 trial space를 보존하므로 B-origin direct/torque 일치는 finite projected commutator에서 이미 닫힐 수 있다. 이 일치를 independent magnitude convergence로 세지 않았다. 독립성의 실질적 근거는 coupled spherical hp-FEM과 separated prolate weighted B-spline의 다른 좌표·trial space·assembly·eigensolve, 실제 cross-representation 비교와 별도 refinement다.

유한 B-centered Dirichlet 구에서는 O-origin torque에 +z_B/(2Δ)∮n_x∂nψ_g∂nψ_b의 표면항이 가능하다. xψ_b는 Dirichlet 조건을 보존하므로 position commutator와 domain 문제가 다르다. 측정된 표면항과 tail-only 변화는 작지만 continuum 상계로 바꾸지 않았다. 작은 matrix residual이나 두 Ritz root의 차이도 full-space residual 또는 exact gap lower bound가 아니다.

## 실제 수렴과 기준

Selected reference는 B_l96, radial elements56, degree4, rmax24, Hamiltonian q14다. 비교값은 부모 C1의 unchanged refined prolate 결과다. 다음 값은 실제 artifact에서 재계산했으며 임계값을 완화하지 않았다.

| 검사 | 측정값 | 기준 | 판정 |
|---|---:|---:|---|
| 독립 E_g 차이 / E_A | 2.93144×10^−7 | 10^−5 | PASS |
| 독립 E_b 차이 / E_A | 5.37670×10^−10 | 10^−5 | PASS |
| 독립 L_O 차이 / ℏ | 1.10693×10^−6 | 10^−5 | PASS |
| ℓ72→96의 최대 energy 변화 / E_A | 3.85574×10^−7 | 2×10^−6 | PASS |
| ℓ72→96의 L_O 변화 / ℏ | 1.45734×10^−6 | 2×10^−6 | PASS |
| 별도 h/p/q/box의 최대 energy 변화 / E_A | 2.45279×10^−9 | 2×10^−6 | PASS |
| 별도 h/p/q/box의 최대 L_O 변화 / ℏ | 9.36132×10^−9 | 2×10^−6 | PASS |
| Selected O direct/torque 차이 / ℏ | 7.21159×10^−11 | 10^−7 | PASS |
| Selected momentum–dipole residual / (ℏ/a_A) | 6.89592×10^−10 | 10^−7 | PASS |
| Prolate tail 최대 energy 변화 / E_A | 7.25553×10^−12 | 2×10^−6 | PASS |
| Prolate tail L_O 변화 / ℏ | 3.28737×10^−13 | 2×10^−6 | PASS |

Accepted axis 설정 전체의 force q14→22 및22→30, normalization과 두 Ritz root의 algebraic residual도 각각 계약의10^−8,10^−10,10^−9 기준을 충족한다. JSON 검토본은 각 기준의 실제 최대값을 담는다. 원 summary의 prolate-tail energy10^−8 검사는 원 계약2×10^−6보다 엄격한 추가 진단이며 두 기준 모두 통과했다.

Selected reference의 (E_g,E_b)=(-2.512192723447947,-0.899646911631157)E_A, L_O/(−iℏ)=0.34097886468907423다. Prolate와의 차이는 독립적인 수치 불일치의 크기이며 통계적 error bar가 아니다. 출력 자릿수는 재현용이다.

State L² increment도 별도로 확인했다. ℓ72→96의 (g,b) 차이는 약(1.98834×10^−5,1.36428×10^−6)다. 이는 finite state 사이의 차이이며 exact state error bound가 아니다. 거의1인 overlap에서 √(2−2overlap)을 쓰면 precision floor가 생기므로 `STATE_INCREMENT_AUDIT.json`의 직접 squared-difference 적분을 작은 increment의 근거로 채택했다. Union mesh에서 다항식 차수에 충분한 Gauss rule과 zero extension을 사용한 reducer를 확인했다.

## 원래 cap 실패와 operational amendment

원래 ℓ40 cap에서는 L 차이1.41551×10^−5가10^−5 기준을 넘었다. 이 실패는 보존되어 있다. 측정된 ℓ40 비용1.116초·210,836KiB를 근거로, 새 실행 전에 단 한 번의 amendment를 기록하여 ℓ72,96을 추가했다. 기존14쌍/600초/4GiB 전체 envelope와 모든 numerical acceptance threshold는 유지했다. 새 수준의 실제 계산값으로 판정했으며 fitted/extrapolated limit를 사용하지 않았다. Cap96 이후 추가 extension은 없었다.

전체 R2 target state는14쌍=28개, B-centered second Ritz roots는24개이며, 변경된 two-root interface를 위한 focused atomic solve1개는 별도다. R2 pair별 solver/operator 시간 합은52.595초다. 기록된 최대 RSS1,206,608KiB는 spherical drivers에만 해당한다. 실행된 prolate-tail V1에는 RSS 측정과 driver 내부 RLIMIT_AS가 없었다. 따라서 모든 child의 cap enforcement나 전체 node peak memory를 검증했다고 주장할 수 없다. 이 계측 공백은 명시되어 있으며 전달용 driver에 향후 limit/measurement가 추가되었고 물리 계산은 반복하지 않았다.

Prolate tail은 기존 내부 knots를 보존한다. 옛 outer endpoint의 clamping과 인근 basis support는 바뀌므로 모든 basis function이 그대로라고 해석하지 않는다. Spherical tail은 기존 내부 element 경계를 그대로 유지했다.

## 검토 중 발견한 수정과 증거 경계

- Zero-charge off-center force에서 charged potential을 charge로 나누는0/0 위험을 발견했다. Unit-charge 표현으로 고쳤고, 최초 bytes와 최종3개 force test의 성공 기록을 보존했다. 최초 B_l8은 positive charges에서 원 forceV1으로 이미 실행되었고 결과는 이 zero-charge 결함의 영향을 받지 않는다. B_l12와 이후 결과는 수정본을 사용했다.
- Unit runner의 기존 JSON overwrite 가능성을 발견했다. 실행 원본을 보존한 뒤 setup 전 guard와 atomic create-only writer를 넣었다. Solve 진입 시 실패하도록 계측한 I/O 검사에서 기대한 exit1이 발생했고 기존 과학 결과 hash는 변하지 않았다.
- Cached NPZ의 byte identity 확인이 빠진 부분을 수정했다. Size/SHA256·origin·grid·solver identity를 확인하고, same-length tamper rejection을 solve 없이 검증했다.
- 전달 패키지의 parent input은 exact C1 pilot·reference-code SHA256에 묶였다. 정상 sibling과 standalone snapshot을 허용하고, 같은 길이의 변조 sibling을 solve 전에 거부하는 검사가 통과했다.
- 실행된 driver와 전달용 driver의 bytes를 별도로 보존했다. 현재 전달용 파일에 대한 identity를 과거 physical execution identity로 소급하지 않았다.

변경된 origin/operator/mesh/gap 입력의 focused5개 검사와 최종 force3개 검사가 통과했다. Force point-kernel 비교는 음의 signed-center a=−2에서 핵 반경 안팎의 smooth radii를 대상으로 했다. Positive signed-center 또는 모든 parameter 영역에 대한 추가 물리 검증을 했다는 주장은 허용하지 않는다.

## 인정하는 범위와 다음 의존성

이번 closure는 명시한 한 지점의 empirical energy/coupling convergence다. Exact state-norm enclosure, continuum completeness, verified spectral gap, near-degenerate continuation, full R-grid, A2 scaled asymptotic sequence, collision/cross sections 및 Eq55는 닫히지 않았다. 부모 C1의 equal-charge/dark checks는 algebraic fixture 수준이며 새 physical numerical validation으로 승격하지 않는다.

다음은 `C2_FINITE_R_COUPLING_NUMERICAL_AUDIT`의 bounded R-grid·state/phase continuation·asymptotic acceptance 실행 계약을 고정하는 일이다. 이번 검토 자체는 broad C2 실행을 수행하지 않았다. `CODE_I02_CLOSED=true`, `full_certificate_fail_closed=true`, `scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 그대로 유지한다.

검토한 파일의 bytes/SHA256, 저장 state24개의 검사와 실행 identity 대조는 동반 JSON에 있다.
