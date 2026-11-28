# C1–C5 구현 및 bounded 실행

`CONTRACT.json` 및 `THEORY_KO.md`의 binary64 reference다. 입력 source를 바꾸지 않고 40개 전사값을 JSON/CSV로 대조한 뒤 E=3,4,5,6 eV의 32개만 선택한다. 표 angle 순서를 increasing mu 순서로 뒤집되 row uncertainty와 cell을 같이 옮긴다.

`ddcs_window.py`는 segment primitive로 analytic hats를 적분한다. `quadrature_moments`는 같은 hat 함수를 호출하지 않고 cell의 네 꼭짓점으로 local bilinear interpolation을 직접 평가한다. GL16/32를 사용하며 theta 대조 모델에서는 theta를 radian으로 변환하고 sin(theta)를 곱한다. Box ratio는 scalar마다 n+1 threshold vertex를 스캔하고 서로 별개인 extremizer witness를 반환한다. Covariance에는 이 ratio scan의 exact-range 주장을 붙이지 않는다.

`test_ddcs_window.py`는 standard-library unittest로 constant/affine closed forms, signed/tied/equal b/a와 collapsed bounds에 대한 n<=6 exhaustive vertex oracle, witness equality/stationarity, scale invariance, theta Jacobian, positivity/PSD 및 입력 거부를 확인한다. `run_analysis.py`는 실제 32-cell raw moments/per-energy/individual ratio bounds+witness/PSD/theta alternative 및 validation을 JSON으로 저장한다. `plot_results.py`는 실제 결과를 읽어 source quoted errors와 deterministic scalar ranges를 구별한 PNG/SVG를 생성한다. 그림에는 CI나 full-domain/event-law 주장을 넣지 않는다.

Root가 승인한 실행 명령은 unit 디렉터리에서 순서대로 다음과 같다.

```sh
python -B code/run_bounded.py tests
python -B code/run_bounded.py actual_analysis
python -B code/run_bounded.py plot
```

R6 PASS identity를 확인한 뒤 실행한다. 각 child에는 kernel RLIMIT_CPU 6 s, RLIMIT_AS 1 GiB, 부모가 감시하는 wall 20 s 및 단일 thread 환경을 적용한다. 누적 20 CPU/60 wall, 최대 4 child다. Planned invocation 시작 시 이번 cap 6/20과 repair reserve 6/20을 모두 남겨 둔다. 실패/관측 overshoot 후 자동 재시도하지 않는다. Root가 명시한 targeted repair는 `--repair-authority`로 instruction reference를 기록하며 한 번만 허용한다. Lock 및 미종결 START는 UNKNOWN_NOT_ZERO로 자동 replay를 막는다.

START, FINISH/FAIL, stdout/stderr, code/source freeze 및 실제 child CPU·parent CPU·elapsed wall을 보존한다. 누적 CPU에는 child CPU와 timed parent CPU delta를 함께 더한다. MaxRSS는 Linux getrusage KiB다. 기존 Hex 비용과 unknown remote CPU는 새 allocation에 합치거나 0으로 만들지 않는다.

구현 준비 완료는 코드 검증 완료가 아니다. R6 뒤 실제 C6–C8 결과와 C9 독립 검토를 거쳐야 scoped admission을 결정할 수 있다.
