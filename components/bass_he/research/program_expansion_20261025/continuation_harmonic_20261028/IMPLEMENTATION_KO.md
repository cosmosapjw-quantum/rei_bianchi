# HARMONIC10 S05 — R5/C5 구현 준비

S04의 실제 source·Drive·Dropbox ACK를 확인한 parent 승인에 따라 준비한
`src/harmonic.py`, `tests/test_harmonic.py`, 네 실행·도표 script를 이 단위로
바이트 그대로 복사했다. 여섯 파일의 SHA256은 독립 static review의
`reviewed_source_sha256`과 모두 일치한다. S04 ACK는 `receipts/S04_ACK.json`에
보존했다. 실행 source commit 신원은 아직 **S05 고정 대기**다.

구현은 exact rational coefficient cone, signed Bernstein primitive, 고정 유한
Machin/Taylor enclosure, 기존 같은 사건 finite detector 기하를 연결한다.
검증된 zero/half/full-turn strip에는 C,S exact0을 반환하는 승인된 한 줄
수정을 반영했다. 수정 설명과 diff는 `review/PREEXECUTION_REPAIR.*`에 있다.
독립 static 판정은 `PASS_SCOPED_PREEXECUTION`이며 실제 결과 채택은 pending이다.

준비된 unique test method는 **25개**다. 현재 실제 scientific import, test suite,
plot 실행은 모두 **0회**다. 이 복사는 scientific runtime 승인이나 runtime PASS를
뜻하지 않는다. parent가 immutable S05 SHA를 명시해 승인한 뒤 첫 suite를 실행한다.

검증은 새 누적 CPU20s·wall60s, process당 AS512MiB, thread1 한도에서 첫 full suite1회와
새 진단에 따른 targeted repair reserve1회를 공유한다. 기존 단위 예산을 초기화하거나
옮기지 않는다. 실행 pin과 tracked clean 상태를 확인하고 원 log와 JSON을 보존한다.
whole process CPU는 bounded runner 시작·종료와 waited children을 포함하며 outer
orchestration CPU는 별도 기록한다. 모든 descendant의 strict aggregate 선점 한도를
주장하지 않는다.

도표는 별도 첫 시도1회, CPU10s·wall30s, process당 AS512MiB·thread1 한도다.
같은 검증 실행이 저장한 JSON만 읽어 PNG/SVG 네 panel을 만들고 scientific import와
call은 하지 않는다. 이 문서 작성 시 도표 실행은 승인되지 않았고 수행하지 않았다.

출력의 물리 범위는 manufactured declared angular law와 exact stored mass 계산이다.
measurement uncertainty, 독립 thermal port binding, empirical production을 채택하지
않는다. `birth_pool=UNASSIGNED`, global physical completion=null, `L4=false`,
`production=NOT_APPROVED`, 중앙28/88·HE delta0 및 local9/14를 유지한다.
관측 executor model identity는 unavailable이다.
