# REI P4: Rust 고정 부피 광자 출생시간 적분

## 완료 범위
2026-10-17 UTC, PR182 `3a2721e58fc8bd68cdbbc92ca4669bd57609695b`의 실제 Rust 소스를 격리 snapshot 브랜치에서 수정했다. PR183 `b0382198564c7e85e479d48011e880ef7c2c4d46`의 Python 진단과 다음 DAG를 읽은 뒤 중복 P3 구현을 피했다. 원본 owner_src 12개 파일은 바이트 단위로 보존했다.

추가 API는 `full_network::step_fixed_volume_uniform_births`이며, 기존 `step`과 P3 cosmological driver의 기본 동작은 그대로다. 이것은 P3 driver 수정 완료가 아니다. 같은 광자 bin 에너지에서 실제 시간간격 동안 균일하게 태어난 수밀도 B를 입력받아, 기존 공유 H/He/D 사건·열·화학 에너지 계산에 연결한다. 내부 가스 opacity는 시작 상태에 동결된다. 별도의 우주론 기하 입력을 받지 않는 고정 proper-volume 전용 API다.

## 이론 계약
고정 lambda>=0, 상수 방출률 j>=0에서 dN/dt=j-lambda*N, tau=lambda*h, B=j*h.

N_final = N_old exp(-tau) + B Phi(tau)
A = N_old [-expm1(-tau)] + B Psi(tau)
Phi = [1-exp(-tau)]/tau, Psi=1-Phi.

tau=0에서 Phi=1, Psi=0. 작은 tau에서는 Psi를 직접 급수로 계산해 소실을 피한다. 최소 subnormal에서는 B*tau를 먼저 곱하고, 매우 큰 optical depth의 기존 광자 생존량은 필요한 경우 log-product로 계산한다. 각 흡수종에는 동일한 A에서 lambda_i/lambda 비율로 사건을 배분한다. D RHS는 같은 사건을 검산하며 다시 적용하지 않는다.

주입 에너지는 Q=sum(B_i E_i)*eV_J이고 E_final-E_initial-Q를 검사한다. 흡수된 신생 광자도 Q에 포함한다. 실패는 복제한 trial만 폐기하며 원본 상태를 바꾸지 않는다. dt=0에서 비영 주입량은 거부한다. 재시도 시 호출자가 실제 짧아진 구간의 B를 다시 제공해야 한다. 적응형 재시도 scheduler는 이번 구현에 없다.

Wolfram 계산은 적분 `(1-exp(-lambda*h))/lambda`, Phi/Psi의 7차 급수 및 ODE 대입 잔차 0을 확인했다. 문헌의 variation-of-constants와 phi1 함수에 해당한다: Hochbruck & Ostermann, Acta Numerica 2010, 식1.5–1.6 및2.8, https://na.math.kit.edu/download/papers/acta-final.pdf . SciSpace 검색도 수행했으나 새 물리 입력은 도입하지 않았다. 요청한 physmath 스킬 패키지는 현재 읽기 도구에서 unavailable이었다.

## 실제 검증
- 기존 P2 20개 baseline 테스트 통과.
- 새 API가 없을 때 unresolved-import RED 확인 후 구현.
- 최종 Rust 테스트 89개 통과: 기존68 + 신규21. offline/locked, build jobs1.
- 신규 검사는 4흡수종의 직접 analytic 사건/생존 비교, D-only, 0 opacity, 공유 에너지/핵자, 전체 collision/CX, 중복 CX 거부, downstream 실패의 원본 불변성 등을 포함한다.
- Rust kernel 1,890행을 450자리 mpmath 독립 식과 비교: `abs_error <= 5e-13*abs(reference)+4*min_subnormal` 통과. 정상 범위 기준 최대 상대 차이는 생존량 약2.38e-14, 흡수량 약1.72e-13. underflow 참조값에는 상대 오차1이 있을 수 있으므로 일률적 상대오차 상계를 주장하지 않는다.
- 독립 정적 검토 PASS_SCOPED. 검토자는 테스트를 재실행하지 않았으며 원본 실행 로그를 확인했다.
- Clippy는 설치된 도구에 없어 미실행. 원래 producer의 Clippy 주장으로 대체하지 않는다.

## 유지하는 HOLD
고정 계수 광자식의 정확성이 결합 화학계의 2차 정확성을 뜻하지 않는다. 가스 opacity의 시작시점 동결과 Lie splitting 때문에 coupled 경로는 여전히 1차다. 시간 의존 MD14·Bianchi cohort driver 연결, 각도/에너지/age 수렴, full native history, BI-SIGNED와 관측 채택은 미완료다. 제조 D-H offset/테스트 스펙트럼의 물리적 채택도 하지 않았다.

이 코드는 원격 저장소에 push하거나 PR 게시하지 않았다. 프로젝트 전체 누적 CPU/wall/잔여 예산은 UNKNOWN이며 기존 만료 예산을 초기화하지 않는다. 현재 제한 검증 명령13회의 합은 wall13.530730s / child CPU13.677745s다. 도구·문서·패키징 시간은 이 합에 들어가지 않으며 전체 비용은 UNKNOWN이다. 상세 명령과 실패도 evidence/COMMAND_LEDGER.json에 보존했다.

다음 안전한 구현은 이 저수준 API에 대한 고정 기하 cohort 연결과 소스 sampling 계약이며, 그 이후에만 시간 의존 Bianchi 및 전체 solver의 독립 수렴 검증을 고려한다.
