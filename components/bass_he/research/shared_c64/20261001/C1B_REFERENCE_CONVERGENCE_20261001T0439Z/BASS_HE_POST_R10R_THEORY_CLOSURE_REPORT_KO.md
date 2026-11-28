# C1b: R=2 독립 reference 수렴

**`C1B_R2_REFERENCE_CONVERGENCE_CLOSED`.** 독립 spherical reference와 prolate 경로가 R=2a_A의 energy·charge-center angular coupling 사전 기준을 통과했다. Continuum certificate와 R 전역·collision 정확도는 미인증이다.

| 결과 | 값 |
|---|---:|
| B-centered l96 E_g/E_A | −2.512192723447947 |
| E_b/E_A | −0.899646911631157 |
| L_O/(−iℏ) | 0.34097886468907423 |
| 독립 prolate 대비 L 차이 | 1.11×10^−6ℏ |
| l72→96 L 변화 | 1.46×10^−6ℏ |

B로 전개 중심을 옮기고 L_O=L_B+z_Bp_x로 물리 원점을 보존했다. 초기 l40 실패 뒤 한 번의 operational amendment를 새 실행 전에 기록해 l72,l96을 추가했다. Acceptance tolerances는 그대로이며 실패 기록을 보존했다. Angular·radial h/p·quadrature·tail의 분리 검사가 통과했다.

R2 계산은14쌍=28상태와 second Ritz roots24개, solver/operator 시간 합52.60초다. 변경 범위 검사5개와 force 검사3개도 통과했다. Max RSS1,206,608 KiB는 spherical drivers에만 해당하며 prolate-tail v1의 계측 누락을 명시했다. 출력 자릿수·method spread·Ritz gap은 continuum accuracy나 통계적 오차 인증이 아니다.

세부 근거는 `C1B_REFERENCE_CONVERGENCE_KO.md`, `evidence/CONVERGENCE_SUMMARY.json`, `evidence/STATE_INCREMENT_AUDIT.json`에 있다. B1의1131 native cells와13행 matrix는 그대로이며 자체계산 coupling 진단6행만 append했다.

다음은 **C2_FINITE_R_COUPLING_NUMERICAL_AUDIT — READY_NEXT_NOT_RUN**이다. Exact R-grid·tolerances·continuation 계약을 먼저 고정한다. `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, production 변경 금지를 유지한다. 게시·백업 확인은 external receipt가 소유한다.
