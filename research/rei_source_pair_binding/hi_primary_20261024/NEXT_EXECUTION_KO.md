# 다음 실행 단위: 비열적 압력 구간의 한정 fixture

현재 L1 source-summary consumer는 ADMITTED_SCOPED_SUMMARY_CONSUMER다. 그 child는 한 번 완료되었고 재실행하지 않는다. 이 문서는 다음 압력 모듈의 별도 실행 제안이다.

## 완료된 준비

next_pressure/THEORY_KO.md의 가정은 M=m_e c^2>0와 [0,L] 위의 유한 비음수 측도다. N=∫dν, U=∫k dν, 0≤U≤NL에서
U(L+2M)/(3(L+M)) ≤ Π ≤ U(U+2MN)/(3(U+MN))
를 유도했다. 양 끝은 각각 (N−U/L)δ0+(U/L)δL와 Nδ(U/N)로 달성된다. 0 경계, gap, 비상대론적 근사의 오차 상한도 포함한다.

별도 native reviewer가 이 해석적 유도를 PASS_SCOPED로 검토했다. 코드의 독립 정적 심사는 review/PRESSURE_STATIC_REVIEW.*에 기록된다. 수치 실행은 NOT_RUN, physical stock/pressure closure는 NOT_ADMITTED다.

| 파일 | SHA256 |
|---|---|
| pressure_interval.py | 8ab04ea247a43328432fd0b57899c501e298f356736b60a73e5e1ec345228e77 |
| focused_check.py | 0bdd8c8017a6e52953a713fa7b74603f5cbc14b42794cbad676be7be4c4ba7d4 |
| run_focused_once.py | 3eff72d14c6ee996e1cfb4b617ddc0fc3cfb914d9cca8e29c28a0906bbea24fe |
| PROPOSED_EXECUTION.json | d6cf6a8759766f1bbf0aa55eca8b626b50fb50ff7f39afe740075e9395ab9fcc |

구현은 exact represented Fractions로 구간 및 supplied atoms의 압력 모멘트를 반환한다. 저장된 HI moments, source API 또는 원 공급자 파일은 바꾸지 않았다. 한 미래 fixture는 정확한 8/9·1 끝점,17/18 혼합,0 경계, U>NL 거절과 공통 scaling을 검사하도록 준비됐다. 이 숫자는 종이 위 기대값이며 실행 결과가 아니다.

## 별도 제안과 실행자

- 상태: NOT_AUTHORIZED.
- 실행자: 기존 /root/uv_coding. 요청 모델 gpt-6.1-sol/high; 관측 backend는 unknown.
- child1회, CPU soft=hard1초, launch-inclusive wall5초, 자동 재시도0.
- 현재 L1의 남은 CPU나 과거 cap을 이전/리셋하지 않는다.
- 정확한 현재 환경 명령:

~~~bash
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python -B /workspace/scratch/03a65a604d4c/rei_l1_execute_20261024/work/research/rei_source_pair_binding/hi_pressure_next_20261024/run_focused_once.py
~~~

별도 실행 승인 후 기존 입력/소스 identity와 미사용 attempt marker를 확인하고 이 단일 child만 실행한다. 실패하더라도 동일 child를 자동 재시도하지 않으며 실제 raw/CPU/wall을 보존해 오류 종류와 최소 수리를 판단한다. 출력은 raw/attempt.json, stdout.jsonl, stderr.txt, resource_receipt.json에 남긴다. 성공 후 원자료의 독립 심사와 scoped 판정을 거쳐 최신 AGENTS/HEAD/병렬 변경을 확인해 허용 경로에 expected-SHA/non-force로 게시한다.

## 그 다음 DAG 의무

조건부 압력 구간의 코드 검증은 물리적 EOS나 Einstein feedback의 채택과 다르다. 실제 source의 압력 주입을 원자별로 계산하려면 실제 positive-atom payload/schema와 support를 읽고 같은 event measure를 결속한다. 주입된 입자의 현재 압력 재고에는 초기 분포와 redshift/transport/stopping 또는 명시적 closure가 더 필요하다.

L4는 이 선택을 포함한 source qualification, finite radiation stock/공급 모델, geometry/solver/IC·오차 척도·별도 실행 예산을 갖출 때 진행한다. L2와 L3는 선택한 beta 및 anisotropic-baryon 채널에만 조건부로 연결한다. ANGTHERM02는 계속 읽기 전용 예약이다. 전체 모델 완료율은 null이다.
