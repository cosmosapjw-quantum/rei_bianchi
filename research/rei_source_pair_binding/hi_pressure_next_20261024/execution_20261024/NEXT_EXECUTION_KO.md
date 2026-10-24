# 다음 한 실행: Bianchi stock 유한 exact fixture

## 상태·실행자·추가 예산 조건

해석적 이론 ADMITTED_SCOPED_CONDITIONAL_ANALYTIC_BOUNDS,
구현 PREPARED_PASS_STATIC_SCOPED, 실제 수치 실행 NOT_RUN이다.
현재 pressure 한 child release는 소진되었다. 이 문서는 다음 prospective increment의 구체적인 제안이다.

- 실행자: 재사용 가능한 lower-tier /root/pressure_coding.
- 요청 모델/effort: gpt-6.1-sol/high; 실제 backend unknown.
- 추가 한도 제안: scientific child1, CPU soft=hard1초, launch-inclusive wall5초, retry0.
- 기존 known partial10.238107초, 원10초 cap 초과0.110448 FAIL,
  wholeL0 UNKNOWN_NOT_ZERO, original cumulative cap NOT_FROZEN 유지.
- model/review/IO/remote 비용은 별도 미측정이며0이 아니다.
- 새 release를 아래 exact candidate에 결속한다. 이전 pressure/HI/L0를 재생하거나 unused seconds를 옮기지 않는다.

## 정확한 명령과 입력

~~~bash
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python -B /workspace/scratch/03a65a604d4c/rei_pressure_execute_20261024/work/research/rei_source_pair_binding/bianchi_stock_bounds_20261024/run_focused_once.py
~~~

Python3.12 standard library, 추가 설치 없음.

source SHA:
25c0e7919df496b79c131ffe0a25cc1101e9bf1d804e721bf190e48d3a165907
fixture SHA:
47ecf7dc0ec59790e4eb339d59c527e71c07aab4ecb7b2fc0c4e265e77b35f43
runner SHA:
f3c40f3d426104503370e7ba3f833a15ec19ef41d0cbbab3f70d78f30e3e9cda
theory SHA:
4041f7bd3971e3930ddcd76adca2b91f74c63cee05cca674f522cfbe3dfa15e9
contract SHA:
b65528e96764b5eb7dc44284b1b50d61ee406d0a0bf692ec01ca61be09e93fb9

나머지 입력·명령은 PROPOSED_EXECUTION.json와 SOURCE_BINDING.json에 있다.
새 작업 환경에서 경로가 사라졌다면 저장 bytes를 복구하고 실제 경로를 확인한다.
이전 provenance·비용·실행 표시는 보존한다.

## 고정 판별 기준

N=U=L=2,M=1의 identity,
r=(1/2,1/2,1/2) expansion,
r=(2,2,2) contraction,
r=(1/2,1,2) mixed axes의 radical endpoint를
production sqrt helper를 쓰지 않는 유리수 제곱 부등식 oracle로 확인한다.
tiny k=2^-200의 엄밀히 양의 lower, 영 경계, invalid moments/ratios/type/bits 거부,
공통 weight scale7/3을 같은 한 fixture에서 검사한다.
Fraction numerator/denominator 문자열을 출력한다.

수용은 source/fixture/runner 일치, 고정 assertions 도달, exit0,
timeout/launcherror 없음, 실제 child CPU≤1/wall≤5에 한정한다.
성공해도 generic conditional arithmetic의 유한 근거이며
실제 HI history·thermalization·EOS·Einstein·L4 admission이 아니다.
bits 격자는 물리 tolerance나 기존2e-12 gate가 아니다.

## 반환과 다음 전이

raw/attempt.json, stdout.jsonl, stderr.txt, resource_receipt.json을 보존한다.
실패도 남기고 자동 재시도하지 않는다.
Root가 실제 finding과 원인을 분류해 필요한 최소 수리만 승인한다.
별도 native reviewer가 실제 raw/source를 읽고 root가 scoped admission을 결정한다.
게시 전 실제 AGENTS·HEAD·병렬 변경·ANGTHERM02 예약을 확인하여
owned path를 expected-SHA/non-force로 게시한다.

그 다음 물리 cohort 응용에는 초기 저장고, 양의 주입 이력과 표적밀도,
a_i(t), tensor/shear work와 collision/stopping 선택이 필요하다.
현재 준비물이 이 입력을 제공한 것으로 간주하지 않는다.

