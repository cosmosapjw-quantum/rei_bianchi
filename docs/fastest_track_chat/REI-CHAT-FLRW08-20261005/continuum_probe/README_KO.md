# FLRW08 짧은 연속시간 기준해 진단

원래 m8, mu8×phi16 grid에서 0..1e10 proper s 구간의 실제 paired trial
6개를 실행했다. FLRW와 BI 각각 macro dt=1.25e9,6.25e8,3.125e8 s이며,
실제 수락 궤적은 내부 두 half step을 사용한다. 합계112 macro 호출이다.
생산 소스·완료 campaign·기존 frozen 검사·Cargo.lock은 변경하지 않았다.
초기 미분 진단4회와 경계 witness2회는 별도 호출로 기록했다.

핵심 발견은 최저10 eV 경계다. 원 remap은 이 노드에 있는 photon을
임의의 양수 시간 간격에서 전부 lower guard로 옮긴다. 따라서 전체 상태
공간에서 유한 생성자가 존재한다는 처음의 가정은 틀렸다. 원 intent를
보존한 채 Host가 수정한 `P M_dt P` 축소 모델을 독립 기준해에 사용했다.
P는 최저 노드를 guard로 옮겨 number와 energy를 보존한다. 원 수치법의
장기 극한이 이 모델이라는 전역 수렴 증명은 하지 않았다. 실제 dt=10000과
1000 s witness 모두 .05 photons/H를 guard로 이동했고, number secant는
5e-6에서5e-5 /s로 증가했다. 자세한 식과 주장 경계는 MODEL.md에 있다.

| FLRW macro dt (s) | xHII − 독립 DOP853 | T − 독립 DOP853 (K) |
|---:|---:|---:|
| 1.25e9 | −8.007202099e-7 | +0.0197770230 |
| 6.25e8 | −4.006153556e-7 | +0.0098947379 |
| 3.125e8 | −2.003715631e-7 | +0.0049489273 |

BI 개별 bias도 같은 크기이며, 이 세 값은 일차 시간 수렴과 양립한다.
BI−FLRW xHII 차분은0,−3.33e-16,−6.66e-16이고 DOP853 차분은0,
RK45 차분은4.44e-16이다. 이 구간의 차분 부호는 **NOT_ESTABLISHED**다.
끝 시간을 늘려 신호가 나오도록 조정하지 않았다.

독립 Python 기준해는 FT03 비광화학 계수와 Verner sigma를 직접 계산했다.
원 Rust의 실제 계수5개 온도 sample과 상대차1.74e-16 이내이며 sigma는
실제33개 노드 sample과 정확히 일치한다. 물리 binding chi와 fit cutoff는
구분한다. DOP853/RK45의 최대 끝점 정규화 차이는4.44e-16으로 고정 기준
1e-8을 만족했다. 두 수치 적분법의 일치는 엄밀한 reference enclosure나
continuum time-error 상계가 아니다. 같은 원 RHS를 호출하는 비교도 아니다.

모든 짧은 궤적의 최대 local bound는9.3126e-5 미만, public width는
1.051e-8 미만, ledger는6.05e-16 미만이다. 기존 완료 이력의 같은1e10 s
끝점6개를 읽어 비교했고 Host가 지정한 단위별 scale에서 최대차
1.605e-14로1e-12 parity를 만족했다. 과거 V1와 compensated V2의 byte
동일성을 요구하지 않았다. 첫 parity 검사에서 온도에 absolute1e-12 K를
적용한 false-FAIL과 수정 전 RESULTS는 raw 출력 폴더에 보존했다.

기준해 201개 dense sample의 온도는49963.860842..50000 K, gas simplex는
유효했다. Number ledger residual≤2.78e-17 photons/H, energy residual≤
1.43e-14 eV/H다. Dense interpolation에는 최대 약−2.90e-23 photons/H의
아주 작은 음수가 있었다. Guard N/U도 약−2.66e-75/−2.66e-74까지였다.
이 값을 clipping하지 않았고 exact positivity 또는 tiny-tail 상대정확도를
주장하지 않는다. 끝점의 기록된 photon/guard 값은 비음수다.

초기 투영 미분 진단의 정규화 secant 오차(1e10 s를 곱함)는 dt1e6,
1e5,1e4,1e3에서3.87e-8,3.87e-9,1.70e-9,1.27e-8이다. 마지막 단계는
binary64 반올림의 영향을 보여 주며 원 최소 macro1000 s gate를 바꾸지
않았다. Self-check70개와 frozen acceptance를 실행한다. 후보 자체 검증은
독립 review나 과학 admission이 아니다. 결과는 **HOLD**, continuum
time-error certificate는 **NOT_ESTABLISHED**다.

재현 명령은 다음과 같다. 실제 실행은 cuhg-telemetry로 동일 task를 기록했다.

```bash
cuhg-telemetry run --project /home/cosmosapjw/Dropbox/bianchi/rei_bianchi --task REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL -- /usr/bin/python3.12 docs/fastest_track_chat/REI-CHAT-FLRW08-20261005/continuum_probe/run_probe.py
/usr/bin/python3.12 docs/fastest_track_chat/REI-CHAT-FLRW08-20261005/continuum_probe/self_check.py
/usr/bin/python3.12 .cuh/fastest-track/REI-CHAT-FLRW08/continuum-probe/acceptance.py
```

Native sample 재사용 시 `run_probe.py --reuse-native <native.json>`은 궤적을
추가 실행하지 않고 기준해·보고만 다시 계산한다. 이번 parity scale 수정은
이 방법으로 처리해 성공한 궤적112회는 반복하지 않았다. Rust1.94.1을
고정해 원 library를 독립 rlib로 컴파일하고 원 paired_runtime 모듈을
그대로 include한다. Rust driver·library 컴파일 argv와 오류, native 원문,
두 기준해 state, 원 포함 소스 SHA, binary SHA는 RESULTS가 가리키는
`.cuh/.../continuum-probe/outputs/`에 있다. 첫 컴파일 오류도 보존했다.
Python3.12, SciPy1.17.0, NumPy2.4.2를 실행 전에 확인한다.

독립 GPT-6 Astra/xhigh 리뷰와 Host의 frozen acceptance 재확인을 완료했다.
리뷰어는 저장된 원 배열로 오차·차분·parity를 다시 계산했고 실제 acceptance
70개 검사를 실행했다. 차단·주요·경미 결함은 발견되지 않았다. 검토 당시
9개 후보 파일,34개 보존 대상,23개 포함 소스의 identity가 일치했다.
REVIEW.json에 정확한 검토 범위·원문·runtime identity를 보존한다. 이 결과는
짧은 projected fixed-grid 진단의 검증 통과이며 과학적 HOLD를 바꾸지 않는다.

CODEX_ONLY 실제 새 native 실행은 author GPT-6.1 Sol/high1회와 독립 reviewer
Astra/xhigh1회다. 이번 unit의 native 사용량은 author1,994,324 + review681,833
=2,676,157 tokens다. Cached input와 reasoning output는 이미 input/output에
포함되어 중복 합산하지 않았다. 이전 FLRW08 review418,735와 합친 FLRW08
누적 native는3,094,892 tokens/3 dispatch, 이전 F08의10,419,630 tokens/4
dispatch도 별도 보존했다. 이전 local helper3회/928 tokens를 새 CODEX_ONLY
호출로 바꾸지 않는다. 새 local coding 호출은0회다. Host 사용량·금액·절감률은
NOT_MEASURED이며 native target 초과는 동일 task의 재계획으로 처리했다.
