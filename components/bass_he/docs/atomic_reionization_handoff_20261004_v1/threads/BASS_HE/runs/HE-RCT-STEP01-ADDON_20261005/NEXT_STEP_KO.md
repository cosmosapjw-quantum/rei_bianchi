# HE-RCT-STEP01-ADDON 다음 인계

이 패키지는 실제 compiled/tested 별도 Rust add-on이다. 기존 RCT 설계만 다시 읽고 처음부터 구현하지 않는다. READ: REPORT_KO.md, NUMERICAL_CONTRACT.json, INPUT_PIN.json, RETURN.json, evidence/FINAL_TESTS.log, evidence/INDEPENDENT_ENDPOINT_RESULTS.json.

원 실행 의존성은 REI41e4592aa494b48929dcd23fc8504c169a98a908 full crate이고 vendor34파일을 변경하지 않았다. 최신 소비기 전체 crate/F08는 이번 실행대상이 아니다. current ft03/he_rct 관련 blob와 F08 owner 예약을 확인한 후에만 실제 consumer integration을 수행한다. 별도 addon 코드·공개 API는 이미 구현됐다.

새 event-control은 예시 aJ=1e-14 events/H,rJ=2e-4이며 암묵 default가 없다. owner의 production error budget 채택은 별도다. dt1e10/1e11은 현재 example event control에서 의도적으로 거절된다. 수치 기준을 넓히거나 실패를 clamp하지 말고 적절한 step 크기를 선택한다. full/half 차이는 rigorous exact-flow bound가 아니다.

최소 변경은 이 addon을 실제 owner build/dispatcher로 연결하는 것 또는 같은 코드를 예약된 원 source로 옮기는 것 중 하나다. 둘을 동시에 중복 구현하지 않는다. OFF는 원 baseline delegate, accepted half1+half2, RCT 별도 장부, 기존 residual/local/width 조건과 rollback을 보존한다. 기존 native/원자/F04/F05 과학 suite를 단순 인계 때문에 전수 재실행하지 않는다. Build context 변경에 필요한 관련 시험만 실행한다.

재현은 `bash run_checks.sh /absolute/new/output`이다. 전체 ZIP은 vendor/source/tests까지 포함하므로 네트워크가 필요 없다. 도구체인과 mpmath만 준비한다. GPG 인증은 본 패키지가 제공하지 않는다.

반환에는 actual source/commit/tree, addon 및 dependency hashes, 테스트/log와 command exits, 본 event/underflow 기준의 수락·수정 사유, owner dispatcher에서 활성화 여부, unchanged scientific gates를 기록한다. HE-F2 global/HE-F3/F08/physical admission을 add-on 통과에서 추론하지 않는다.
