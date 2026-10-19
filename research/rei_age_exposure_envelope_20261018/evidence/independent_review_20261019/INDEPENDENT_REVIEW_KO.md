# Age-exposure 오류 제어·진단 독립 검토

검토자: `/root/runtime_probe`. 소스는 읽기 전용으로 검토했고 수정은 구현 담당 agent가 수행했다. 검토 범위의 결과는 `pass_scoped`이며 production scientific admission을 발급하지 않는다. 실제 native NCP 실패 원인과 age/source/spectral 수렴성은 이 검토의 통과 항목에 포함하지 않는다.

## 1. DOP853 block norm

설치된 SciPy 1.17.0의 실제 `_estimate_error_norm` 소스를 확인했다. 동일한 단계 \(K\), step \(h\), 성분별 scale에서 정규화된 5차·3차 오차를 \(a_i,b_i\)라 두면 기존 기준은

\[
A=\sum_i a_i^2,\quad B=\sum_i b_i^2,\qquad
E_{\rm old}=|h|\frac{A}{\sqrt{n(A+0.01B)}}.
\]

상태를 빠짐없이 중복 없이 분할한 블록 \(g\)에 대해 \(A_g=\sum_{i\in g}a_i^2\), \(B_g=\sum_{i\in g}b_i^2\), \(C_g=A_g+0.01B_g\), 크기 \(n_g\)라 두면

\[
E_g=|h|\frac{A_g}{\sqrt{n_gC_g}},\qquad
E_{\rm block}=\max_g E_g.
\]

\(C_g=0\)인 블록은 \(E_g=0\)으로 정의한다. \(h=0\)도 전체 추정치 0으로 처리한다. \(h\ne0\)이고 모든 값이 유한한 정확한 산술에서 \(M=\max_gE_g\)라 두면

\[
A_g\le \frac{M}{|h|}\sqrt{n_gC_g},\qquad
\sum_g A_g\le\frac{M}{|h|}\sum_g\sqrt{n_gC_g}
\le\frac{M}{|h|}\sqrt{\Big(\sum_g n_g\Big)\Big(\sum_g C_g\Big)}.
\]

마지막 부등식은 Cauchy–Schwarz다. 따라서 \(E_{\rm old}\le E_{\rm block}\)가 성립한다. 새 기준의 수용은 같은 단계·scale에서 정확한 산술의 기존 기준보다 약하지 않다. binary64 구현에는 마지막 반올림 차이가 있으므로 비트 단위 부등식 보장으로 기술하지 않는다.

개별 ledger가 단일 블록이면 다른 블록에 오차 0인 광자 좌표를 추가해도 그 ledger의 \(E_g\)에는 전체 차원 \(n\)이 들어가지 않는다. 광자 좌표 전체를 하나의 블록으로 묶는 현재 설계에서는 그 블록 내부의 RMS 차원 의존성은 남는다. 초기 step 선택도 SciPy 원본의 전역 휴리스틱을 상속하므로 estimator의 이 성질을 전체 adaptive trajectory의 완전한 차원 불변성으로 확대하지 않는다.

### 구현 대응과 실제 근거

- `error_control.py`는 block formula를 구현하며 SciPy의 RK 단계, dense interpolation, 초기 step 선택을 상속한다.
- compressed state 순서는 기존 solver의 gas 4개 → 실제 active photon log 좌표 → ledger 14개이며 `production_blocks`의 `(4, active_logs, 1, ..., 1)`과 일치한다. active log 좌표가 없는 구간도 빈 블록을 생성하지 않는다.
- 새 모드는 `--error-norm=block-max`로 명시적으로 선택된다. 기본 `rms`, native command, 원래 `rtol/atol`, RHS, source 및 \(10^{-8}\) 보존 gate는 유지된다.
- generated Python에 helper source를 직접 포함하므로 외부 helper import 누락이 없다. generated solver SHA에 helper 코드가 포함되고 config fingerprint·solver return에 모드가 기록된다. 설치된 SciPy estimator의 버전·소스 SHA도 반환한다.
- 독립 20개 block partition 산술 확인에서 직접 계산한 공식과 구현의 최대 상대차는 `5.09193780994167e-16`이었다. 단일 블록의 수학적 등호 사례는 반올림으로 `new/old=0.9999999999999999`까지 달랐다. 원자료는 `BLOCK_NORM_INDEPENDENT_CHECK.json`이다.

구현 담당자가 실행하고 검토자가 원자료를 읽은 prescribed-opacity control은 \(z'=-50\), \(P'=50e^z\), \(e^z+P=10^{-4}\), 고정 `first_step=.01`을 사용한다.

| 전체 차원 | RMS 정규화 광자 잔차 | block-max 정규화 광자 잔차 |
|---:|---:|---:|
| 2 | `7.212316139325336e-12` | `5.094733771215646e-12` |
| 144 | `4.458910183165445e-11` | `5.093852856950511e-12` |
| 1152 | `1.0938556374600845e-10` | `5.093852856950511e-12` |
| 9234 | `2.6749754476804685e-10` | `5.0939206195862904e-12` |

이 표는 scalar prescribed-opacity control의 결과다. nonlinear Grackle 또는 native age64 결과를 대신하지 않는다.

### 발견한 지적과 종료

`validate_outputs`가 새로 추가한 `error_norm`의 요청값과 실제 solver return을 대조하지 않는 한 곳을 발견했다. 구현 담당자가 reference 경로에 `r.get('error_norm','rms') == c.get('error_norm','rms')` 검사를 추가했다. 모드 필드가 없는 과거 반환은 RMS로 해석한다. 검토자가 해당 mismatch/historical regression 하나를 직접 실행해 exit 0을 확인했다. 근거는 `NORM_RETURN_MATCH_REVIEW_TEST.json`이며 이 지적은 종료했다.

## 2. 광자 ledger 진단

현재 `photon_ledger_diagnosis.py`는 저장된 binary64 수를 `Fraction.from_float`로 정확히 해석해 residual, gross, source jump 차이 및 gate 비교를 수행한다. Decimal 80자리 문자열은 표시용으로 분리됐다. 실제 기존 assertion `abs(residual) <= TARGET*gross`와 저장된 normalized ratio도 구분한다. 따라서 표시용 반올림을 정확한 산술이나 기존 실행의 성공으로 오인하지 않는다.

진단은 원본 state·ledger를 수정하지 않는다. 최종 합셈 roundoff 분석은 이미 저장된 항의 합에 한정되며 전체 RHS·시간적분 오차를 인증하지 않는다. 연속 interval residual 차이는 source insertion과 적분 사이의 분해가 추가로 확인되기 전까지 그대로 signed difference로 읽어야 한다. 현재 `history_interpretation=UNRESOLVED`가 이 범위를 유지한다. 원자료가 없는 interval이나 source jump는 missing 상태로 남는다.

검토 중 작은 값 `1e-100`을 큰 항의 상쇄와 함께 넣은 직접 산술 확인에서 정확한 비영 residual이 보존됐다. 구현 담당자의 11개 테스트 근거와 현재 소스 SHA를 확인했다. 실제 age64 raw backup의 정밀 재합산 판정은 controller의 별도 작업이다.

## 3. native moment failure 진단

원본의 \(64\epsilon\) count gate와 \(128\epsilon\) energy gate가 이미 실패한 branch 안에만 진단을 추가했다. `AtomicBool`은 process에서 처음 관측한 실패 한 건의 출력을 제한하며 반환되는 원래 오류는 유지된다. 배열 각 노드의 \(q,p_i,Np_i\)까지 남기므로 새로운 로그는 적합/저장 양자화를 구분하는 재현 입력을 제공한다.

`prepare_native.py`의 opt-in `--moment-diagnostics`는 frozen 원본 blob을 확인하고 injection SHA와 준비 출력 identity를 기록한다. 기본 준비는 원래 prefix를 사용한다. mode/version이 다른 기존 준비 폴더를 조용히 재사용하지 않는다. `run_moment_diagnostic.sh`는 `time8`에만 제한하고 120초 실행 cap, 원래 비영 exit 및 diagnostic 미확보 상태를 보존한다. closure·물리 상태·gate를 바꾸는 fallback은 없다.

정확히 추출한 원본 Rust 알고리즘에서 \(\ell=1,h=2,N=2^{-1032},U=3N/2\)가 \(\beta=\lambda=F=0\)인데도 \(2\eta\) count defect와 \(3\eta\) energy defect를 만드는 것을 독립 재현했다. 구현 담당자가 새 진단문이 삽입된 동일 합성 셀도 컴파일·실행하여 원래 `MOMENT_FIT` 오류와 동일 숫자를 반환함을 확인했다. 근거 원문을 읽었고 독립 재현과 일치했다.

구현 담당자의 실제 로컬 `time8` 진단은 6.436초에 원래 `MOMENT_FIT`를 반환하면서 첫 실패 셀을 확보했다. 검토자는 실행 근거, 원본 입력 manifest 일치 및 진단 JSON을 읽고 그 셀 하나를 원본 추출 Rust 함수로 독립 재생했다. 두 defect, tolerance, 노드 수와 적합 잔차가 모두 일치했다. 저장된 노드의 정확한 유리수 재합산은 count 결함 \(5\eta\)가 normalization \(-0.0025752573\eta\)와 `N*p` 저장 반올림 \(5.0025752573\eta\)의 합임을 확인했다. 원래 count 허용치는 \(3\eta\)였으며 energy는 \(89\eta\le116\eta\)로 통과했다. \(F=6.7693\times10^{-17}<8\epsilon\), variance 약 1이다. 따라서 현재 로컬 첫 실패는 수렴한 tilt 이후 중량 저장 양자화로 판별됐다. 독립 근거는 `CAPTURED_NATIVE_TIME8_CELL_INDEPENDENT_CHECK.json`에 있다.

과거 NCP 로그는 실패 셀 수치를 남기지 않았으므로 동일 셀이라는 주장은 미확인이다. PR171 normalized reference는 `prepare` 전에 점유 셀 \(N=1\)로 정규화하며, native-time 경로는 실제 surviving state를 전달한다. 이 기작을 age64 normalized-reference ledger 실패 원인으로 확대하지 않는다. 두 호출 경로와 정확한 분해 유도는 `DIAGNOSIS_KO.md`에 있다.

## 검토 종료 범위

요청된 opt-in error estimator, 그 반환 identity 검사, 정확한 저장항 ledger 진단, 실패 branch 전용 native 진단에서 추가 blocking finding은 없다. 수정한 반환 모드 검사는 직접 실행으로 닫았다. 검토자가 직접 수행한 실행은 경량 산술과 단일 셀 재생이며, whole-crate 컴파일과 실제 로컬 `time8` 실행은 구현 담당자가 수행한 근거를 읽고 확인했다. 현재 로컬 native-time 첫 실패의 저장 양자화는 판별됐지만 수치 교정은 수행하지 않았다. 이 검토는 NCP 캠페인 완료, native-time 수렴성 또는 생산 과학 결과 채택을 주장하지 않는다.
