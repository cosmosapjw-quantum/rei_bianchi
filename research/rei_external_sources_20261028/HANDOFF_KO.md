# 재개 인계 — 외부 source 및 n/T 모형

현재 상태는 검사7개 방법·201 epoch 평가·그림을 각1회 완료하고
별도 저자의 독립 검토 PASS_SCOPED를 받은 전달 결과다.
`STATE.json`과 실제 outputs/review/receipt를 먼저 읽고 완료된 실행을 반복하지 말라.

기준 PR243 HEAD는 `48c5656c3ff396edf61390214c40cbdcc203f172`;
실행 전 checkpoint는 `3a70372726f2be5eb3fc0b28a503e23eb68b8932`,
branch는 `research/rei-external-sources-20261028`이다.
source와 nHref는 같은201 baseline epoch를 사용한다.
새 결과는 source operator와 frozen-epoch QSS 진단이며 time evolution이 아니다.

사용자 승인 예산은 planning 임시누적30, presentation65 CPU초다.
이전 누적17.295332885/54.561494494와 main595.225063/600 NO_MORE_IVPs를
보존한다. 검사·평가·plot은 각1회, 자동 재시도0, 단일 worker,3GiB다.
실제 child+관측 wrapper와 남은 명시 tail reserve1/0.5를 기록한
누적 planning19.204540885/presentation56.217331494 CPU초로 closeout했다.
원래 cap10/30으로 복귀했고 누적 debit을 유지한다.
입수·저작·운송 등 미계측 비용은 UNKNOWN_NOT_ZERO다.

독립 검토의 scoped 판정과 F4 현상론적 하위 의무 COMPLETE_SCOPED만 반영하고, 원래33/88·중앙28/88·fast4/7을
임의로 늘리지 말라. 원래 physical F4와 이번 phenomenological 하위 의무를
구별한다. CR113 및 공급자 예약을 보존한다. 다음 과학 작업은 scoped 결과를
토대로 실제 source calibration·transport/charge branch·QSS timescale 검증 또는
별도로 승인된 dynamics 중 하나를 선택하는 것이다.

Controller가 승인한 선택된 공개 문서·코드·CSV·PNG를 additive Git commit으로
게시하고 draft PR을 만들며 같은 파일 집합의 작은 JSON capsule을 기존 Drive/Dropbox
목적지에 보존한다. 원본 archive를 중복 다운로드하지 않는다.
업로드 ACK와 별도 metadata size만 확인했다면 원격 byte hash 검증을 주장하지 말라.


최종 Git/PR/provider 식별자와 검증 범위는 DELIVERY_RECEIPT.json을 읽어라.
eta 정렬은 절대5e-15 이내이며 이전 exact라는 raw label은 역사 기록으로 보존했다.
