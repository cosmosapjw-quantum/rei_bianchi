# BRPERF01 독립 소스 검토와 현재 런타임 회귀

## 판정

검토자 `/root/opt_photon`는 atomic catalog와 native rate receiver를 작성하지 않았다. 원 owner와 원저자 계수·설명 파일을 직접 읽고, 작성자 generator/validator를 import하지 않는 별도 `inspect_sources.py`로 필요한 대응을 확인했다. 현재 채택 범위 안에서 추가 구현·물리 blocker를 발견하지 않았다. 원소 반응망 활성화와 온도 표가 만든 진화 이력 오차는 이번 검토의 채택 범위에 포함되지 않는다.

`run_regression.py`가 현재 Rust 1.94.1과 별도 `audit/target`에서 보존된 부모 및 BR06 gate를 실제 실행했다. 이전 결과를 상속한 표시가 아니다.

| 현재 실행 | 결과 | wall seconds |
|---|---|---:|
| Parent `cargo test --locked --offline --all-targets` | 233 passed, 0 failed | 56.1531 |
| BR06 `cargo test --locked --offline --all-targets` | 16 passed, 0 failed | 66.7265 |
| Parent strict Clippy, all targets | PASS | 4.8454 |
| BR06 strict Clippy, all targets | PASS | 44.7156 |
| BR06 reconstructed wrapper 6개 scoped rustfmt | PASS | 0.0324 |

전체 source snapshot의 **129개 파일**은 실행 전후 SHA-256이 모두 같았다. 이 inventory는 `parent/br05`, `parent/crate`, `br06`이며 dependency vendor와 전체 native input을 다시 감사한 수치가 아니다. 원 physical owner나 큰 source 파일은 format하지 않았다. rustfmt는 `--check --config skip_children=true`로 fixture, quadrature, main, lib, vigilode_moments, vigilode_native 여섯 파일만 확인했다. photon 11개·native 9개·atomic 8개 신규 테스트는 이번 gate에서 재실행하지 않았다.

## Native rate receiver

원 `midpoint_gas.rs`의 helper와 전체 RHS를 비교했다. 함수의 evaluator 인수 추가, 원 igm rate 호출의 치환, zero-photo/non-CX D 호출의 private adapter 치환, D net field의 대응 네 가지를 적용하면 나머지가 whitespace-normalized source와 정확히 같다. midpoint와 Strang 본문도 evaluator 호출 및 원 모듈 이름의 경로 변화 후 같다. 실행에서의 bit parity는 작성자가 보존한 실제 9개 테스트의 범위이며, 이 검토는 그 구현 대응을 독립적으로 확인한다.

D adapter에서 CI/RR의 `cm^3/s -> m^3/s`는 원 순서의 `1e-6`, cooling의 `erg cm^3/s -> J m^3/s`는 `1e-13`이다. 원 density product, underflow/overflow 검사, 6개 energy row의 합산 순서 및 atomic/CX net 순서를 유지한다. PI/CX의 영인 row도 남겼다. 반환하지 않는 D 온도 변화와 diagnostic의 arithmetic rejection도 보존한다. photo input은 원 provider가 zero-rate와 동일 source/threshold로 생성한 private 입력이므로 제거된 public threshold 검사에 대응하는 전제가 성립한다.

글로벌 free-free는 원 `sum(q^2 n)`으로 spectator를 포함하며 CMB는 전체 전자 밀도를 쓴다. 열·결합·escape 항을 중복하지 않는다. state update, CX 양쪽 half-flow, budget 추가는 원 함수를 직접 호출한다. 준비된 T의 bit 일치는 검사하지만 일반 evaluator API의 계수 provenance와 interpolation accuracy는 호출자 계약이다. root가 온도 표를 연결할 때 원 source/hash와 해당 오차 검증을 함께 연결해야 한다.

## Atomic catalog와 표

원 ASCII와 현재 generated Rust를 독립적으로 비교해 **24개 PI/CI entry와 12개 RR entry 전부 일치**를 확인했다. 별도 원시 source 9개도 기존 download receipt의 size/hash와 일치한다.

대상은 Z=3,6,7,8의 Li/C/N/O **원소와 전하 단계**이다. isotope mass number, Li-6/Li-7 분리, 핵반응 계수 또는 활성 native population이 아니다. fully stripped 상태에는 PI/CI fit이 없고 RR label은 포획 뒤 형성되는 N-electron ion을 뜻한다. 없는 RR는 `None`이며 0 rate가 아니다.

PI의 `Mb -> m^2`는 `1e-22`이고, 문턱 아래는 0, 원 Emax 위는 오류다. 원 fit Eth/CI dE를 새 binding-energy owner로 채택하지 않는다. CI Tmin의 eV와 Tmax의 keV를 구별하고, 원 `cfit.f`의 `8.617385e-5 eV/K`를 사용한다. 선택 구간 전체에서 최대 U는 24.64333333333333이므로 원 Fortran의 U>80 cutoff가 닿지 않는다. 최저 CI Tmin은 1 eV여서 10^4 K 이하 CI의 근거로 사용하지 않는다. RR의 3..10^9 K와 최종 이온 label은 원저자 [recombination page](https://www.pa.uky.edu/~verner/rec.html)를 현재 다시 열어 확인했다.

양성·곡률 검토는 다음과 같다. x=ln(T), U=dE/(kT), z=P sqrt(U)로 두면

\[
 (\ln C)''=\frac{z}{4(1+z)^2}-\frac{XU}{(X+U)^2}-U.
\]

각 양의 유리항의 상계는 1/16과 1/4이므로 구현의 M=Umax+5/16은 유효한 보수 상계다. RR에서는 s_i=sqrt(T/T_i)에 대해

\[
 (\ln\alpha)''=-\frac{(1-b)s_0}{4(1+s_0)^2}-\frac{(1+b)s_1}{4(1+s_1)^2},\qquad M\le1/8
\]

이며 선택된 0<=b<=1을 확인했다. 로그 선형 보간의 상대오차 상계 `expm1(M h^2/8)`와 양의 exp 복원은 이 조건과 맞는다. 이것은 실수 연산에서의 보간 상계이며 실제 f64 node/log/exp 오차와 원자 fit의 데이터 오차를 함께 포함하는 상계가 아니다. 구현과 보고서가 이 분리를 유지한다. 표 범위 밖 T를 clamp하지 않고, 비정상 양수/underflow는 `ArithmeticFailure`로 반환한다.

## 남은 구체적 위험과 최소 처리

1. **외부 원문 재배포 라이선스는 확인되지 않았다.** 원 [서버 소개](https://www.pa.uky.edu/~verner/info.html)는 연구 사용 시 출처 표시를 요청한다. 받은 문서와 Fortran header에서 별도 redistribution grant를 발견하지 않았다. `NOTICE.md`는 이를 정확히 기록한다. 공개 접근 가능성을 MIT/public-domain/재배포 허가로 표시하지 말고, 전체 Fortran 원문을 게시할 때도 이 상태를 유지해야 한다. 필요하면 공개 패키지는 URL·SHA·검증 fetch 계약으로 원문을 복원하게 할 수 있다. 이 기록은 재배포를 금지한다는 별도 법률 판정이 아니다.
2. **새 native backend의 semantic source 계약은 호출자에 있다.** 동일 T와 양의 finite 값만으로 원 Grackle 계수라고 입증되지는 않는다. 현재 direct-backend receiver 검증과 새로운 table-error 검증을 독립된 evidence로 연결해야 한다.
3. **새 원소의 활성 반응망은 다음 노드다.** 누락 RR/DR/CX/CE·cooling moments, binding-energy owner와 abundance·charge·electron 제약이 아직 없으므로 catalog의 24-stage 결과를 활성 핵종 추가로 표기하지 않는다.

이번 범위의 코드 수정은 필요하지 않았다. `INDEPENDENT_SOURCE_CHECKS.json`, `REGRESSION_VERIFICATION.json`, raw stdout/stderr와 명령 intent가 검토 및 실행 근거다. 게시·백업은 root의 단계에서 진행한다.
