# C1 결과: 설계·최소 구현 완료, 독립 reference 수렴 미달

이번 loop의 STOP은 **ELECTRONIC_DISCRETIZATION_NOT_CONVERGED**다. Exact two-center Hamiltonian의 prolate B-spline efficient solver와 charge-center spherical hp-FEM reference를 각각 유도·구현했고, 서로 다른 연산자로 direct angular coupling과 singular torque를 계산했다. 설계 고정은 수치 정확도 인증과 구분한다.

R=2 a_A 한 지점에서 refined prolate 결과는 E_g=−2.512193016591858 E_A, E_b=−0.899646912168827 E_A, L_O=−iℏ·0.340977757757509다. Direct/torque 차이는 약 7.4×10^−13ℏ이고 momentum/origin identity도 사전 기준 안이다. 반면 독립 spherical ℓ_max=18 결과와의 차이는 E_g에서 1.284×10^−3 E_A, L_O에서 8.20×10^−5ℏ로, 각각의 사전 기준 10^−5를 넘는다. 따라서 위 숫자는 **pilot 진단값이며 인증된 finite-R magnitude가 아니다.**

| 항목 | 이번 상태 |
|---|---|
| Prolate separation·weak form·physical normalization | 유도 및 구현 |
| 독립 spherical projected Coulomb FEM | 유도 및 구현; reference 수렴 미달 |
| Direct / Duffy force-torque / momentum / origin operators | 구현 및 좁은 검증 통과 |
| Atomic focused tests | 최종 prolate 4개, spherical 6개 PASS |
| 새 coupling analytic/failure tests | 4개 PASS; 추가 eigensolve 없음 |
| 물리 pilot | R=2만, 10개 state solve, 약 7.071초, exit 0 |
| Independent review | 별도 reviewer의 식·코드·결과·claim 검토 |
| R-grid continuation, cluster transport, HF/virial, A2 scaled sequences | 설계만, NOT_RUN |
| Broad C2, collision, cross sections, Eq55 | NOT_RUN |

초기 degree5 B-spline은 작은 energy error에도 wavefunction/derivative 검사에 실패했다. 실패 기록을 보존하고 degree7에서 해당 신규 검사를 통과했다. Independent review가 발견한 driver의 기존 로그 변경 위험은 I/O 경계만 수정했으며, 실행 당시 driver bytes를 보존하고 임시 파일 테스트로 확인했다. 물리 pilot을 재실행하지 않았다.

원전 비교는 prolate separation, 고차 FEM, B-spline, Lagrange mesh/DVR, two-center STO/GTO를 포함한다. P06 p.3 인쇄식의 coordinate/R-factor 모순을 시각 확인해 source defect로 기록하고 Cartesian Hamiltonian에서 재유도했다. Authors' ARSENY 구현을 실행하거나 그 코드에도 같은 결함이 있다고 주장하지 않는다. 새 원전 3개는 버전·페이지·SHA와 private 원문 bytes를 보존했다.

A1/A1b/A2 analytic evidence는 재사용했고, 닫힌 CAS나 과거 scientific suite를 반복하지 않았다. B1 benchmark matrix 13행과 native cells 1,131개는 그대로다. Coupling database에는 인증 상태를 명시한 이번 pilot 진단값 2개만 추가했다. Benchmark fitting, interpolation, missing shell sum은 없다.

다음 단일 node는 **C1b_INDEPENDENT_REFERENCE_CONVERGENCE**다. 같은 R=2에서 angular truncation과 radial h/p·quadrature·tail을 분리해 reference의 수렴을 판정한다. 현재 ℓ12→18 변화는 angular truncation의 미해결을 보여 주지만, 남은 오차 전체의 단일 원인을 증명하지는 않는다. Method spread는 Gaussian uncertainty가 아니다.

Gate는 `CODE_I02_CLOSED=true`, `full_certificate_fail_closed=true`, `scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`다. Whole-program 완료나 production readiness는 선언하지 않는다.

수학·구현 세부는 `C1_ELECTRONIC_DERIVATION_KO.md`, 재현 입력은 `NUMERICAL_CONTRACT.json`, 실제 결과는 `evidence/C1_SINGLE_POINT_PILOT.json`, 독립 검토는 `review/C1_INDEPENDENT_REVIEW.json`이다. Git publication과 backup object IDs는 패키지 외부 delivery receipt가 소유한다. Provider ACK+metadata를 실제 remote raw restore로 표현하지 않는다.
