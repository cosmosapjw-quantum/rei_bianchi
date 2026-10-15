# Unit5: 출력 자원 확장과 실제 full 실행

과학식·tolerance·counter·30초 checkpoint 및 spectrum cadence를 바꾸지 않고 output_budget_mib=12288을 명시적 허용값으로 추가했다. Scientific12160MiB+launcher128MiB이며 기존256/2048/4096배분은 그대로다. 새3검사와 pinnedRust1.94.1 build 및 독립C9가 통과했다. 설치된defaultRust1.99는 inventory만 기록하고 이 source/binary를 재컴파일하는 데 쓰지 않았다.

실제5개 short-control이 모두 z19.8에 도달했고 독립 space/time/angle screen이 통과했다. Source005의 freshq512/q1024 fullz20→4가 2026-10-15T14:50:17.774072Z에 실제 시작됐다. 최초30초 checkpoint는 각각550/254accepted이며 아직 full끝점이나 전체이력 refinement결과가 아니다. 공통마감은2026-10-16T02:50:17.774070Z, science hard stop은02:45:17.774070Z다. Resume/추가case가 이 마감을 초기화하지 않는다.

FULL005_INITIAL_STATE.json과 execution/stage005/full_resource_plan.json을 먼저 읽는다. 각case8worker,12GiBoutput이며 실제초기평균3.30busycores이므로64core지속활용은 입증되지 않았다. NEXT_PARALLEL_RESEARCH는 제안이며 구현·새실행이나 현재과학의 blocking조건이 아니다.

완전한 code/config/fixture/bittrace와 compact증거는 이 ZIP에 있다. 5개대형 pilot fullraw236857384bytes는 중복포함하지 않고 별도불변cloud archive의 검증된 ID/hash/owner/NCP경로를 FIVE_CASE_RAW_ARCHIVE_INDEX.json에 보존한다. 새로운 fullrun은 진행중이며 완료나수렴으로 표시하지 않는다.
