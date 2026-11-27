# 중앙 게시 후보 검토

과거 검토base `1a38f94fa50c763bb9df6ccc8ba569f287fe97d5`에서 만든 HE 누적 후보를, 이후 B3h가 반영된 실제base `152b82cac23fedcb75a9effe0c159bae3d800c01`에 HE delta만 재적용했다. 최신HEAD/AGENTS는2026-10-27 13:12:04UTC(22:12:04KST)에 다시읽었고 그대로였다.

후보17파일1,845,553bytes, 기계적 비교15/15 및 독립 변경범위 검토31/31 PASS, blocking0이다. 실제S03source4349f3cc92543085f7135bb3b556cb9756eec9ec와 시험대상S02a4745150c30af2c6a71b6b61bde0a7e17b8b9ddc를 구분한다.

바뀐 노드는HE-EXCHANGE,HE-EXP-PAIR,HE-CLOSURE,HE-EXP-CLOSURE,HE-EXP-NUCLEAR의5개다. 바뀐 필드는status_observation 및대응observation뿐이다. ANGULAR06 새관찰은뒤의3개노드에들어간다. 나머지83개노드,B3h상태·다음행동,CR,owner/status/budget/dependencies와DAG순서를보존했다. 중앙parent-declared27/88,delta0이다. Node plan5개는최신base전체를접두부로보존했고append의20개pointer가실제로해결된다.

DRIFT02/EVENT03/STATE04/PHOTON05 역사4파일은exactbytes다. PHOTON05plotFAIL/workflowPARTIAL과HE101원결과는그대로다. 중앙README는변경대상에서제외했다.

이폴더의payload는로컬검토후보이며source_published=false,central_published=false다. 자동승인심사차단은우회하지않는다. 게시가승인되면그시점의HEAD/AGENTS를다시읽고HEdelta만재적용·검토한다. Source의실제게시ACK를받은경우에만현재publication상태를갱신한다. 역사시점의false기록은덮어쓰지않는다. 실제expectedSHA와force=false로처리한다.
