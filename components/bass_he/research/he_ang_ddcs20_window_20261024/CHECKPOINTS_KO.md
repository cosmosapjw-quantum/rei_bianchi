# 단계별 evidence 및 checkpoint 연결

20개 R1–R10/C1–C10 각 행은 `LOOP_PROGRESS.json`에 자체 predecessors/status/evidence/checkpoint/Dropbox·Drive backup 상태를 가진다. 여러 닫힌 단계가 하나의 실제 archive/업로드 ACK를 공유할 수 있다. 단계별 표기는 서로 다른 20개 압축본 생성을 뜻하지 않는다.

첫 checkpoint `HEANG_DDCS20_R1_R10_C1_C5_20261024.tar.gz`는 theory loop 완료 및 implementation preparation C1–C5만 포함한다. C6–C10의 실제 run/review/admission은 이 checkpoint에서 완료가 아니다. Git publication은 `PENDING_C9`, 원격 backup은 실제 provider ACK 전 `PENDING_PROVIDER`다. Root가 업로드를 마치면 해당 닫힌 stage 행에 같은 실제 ACK identity를 연결한다.

Archive는 공개 가능한 전사 수치/독립 유도/코드/범위화한 survey만 포함하며 원문 논문 PDF·이미지·전체 추출·full personal search는 포함하지 않는다. RAW_OBSERVATIONS는 원위치와 hash reference만 들어간다. Archive 자체를 자신 안에 넣지 않으며 archive 외부 receipt가 SHA256/bytes/member list를 기록한다.

두 번째 이후 checkpoint는 C6–C8 raw outcomes와 C9 결정이 생긴 뒤 root 승인된 범위로 닫는다. 실패·pending을 complete로 바꾸거나 과거 Hex ledger를 초기화하지 않는다. Scientific admission과 게시/backup 성공은 별도 상태다.

## 확정된 게시와 B1/B2 ACK

B1은106123 bytes, SHA256 `e64e5a96d0f55736e3cc17232569a82cdff16d0eee6bf07f8dbca33756503eba`이며 `delivery/CHECKPOINT1_BACKUP_ACK.json`에 실제 Dropbox/Drive IDs와 양쪽size readback을 보존했다. 위의 B1 pending 문장은 archive 생성 시점의 역사적 상태이며 후속 ACK와 충돌하지 않는다.

Science S=`d8bae9f7e24ad3494e399f7ab46c4167a5623d48`, central observation C=`6cf7c53757ce4049046a3463c57f36bece555830`, central ACK E=`3fba7cd91f84b4687cf6356f87400056ca32e37e`가 실제 게시됐다. Draft PR94는 no_merge/no_activation이다.

B2 `HEANG_DDCS20_20261024_d8bae9f7_6cf7c537.tar.gz`는441890 bytes, local SHA256 `bca49013628469f7d149366d651a1a004f936ad15fc1e5d74f8029ba3799223e`다. `delivery/FINAL_BACKUP_ACK.json`의 Dropbox `id:BSpOijBcT10AAAAAAD_8YA`, Drive `1myTzgvqhm3Dfz9mUH805ASoRNnJhUW64`에서 각각441890 bytes metadata readback을 확인했다. 독립 remote SHA256 검증은 하지 않았다. B2는 고정 S56members+C3members+post-S metadata9members이고 자신의 미래 ACK나 이후 E/D는 포함하지 않는다.

현재20행의 scoped completion/실제 과학 게시/두provider B2 ACK는 완료다. C10의 최종 delivery 문서는 current-file-commit으로 식별하고 자기SHA를 넣지 않는다. 게시 후 알려진 D/E와 실제 handoff/20행을 담는 작은 외부 postdelivery capsule은 보충본이다. 같은 archive 안에 자신의 미래 upload ACK를 넣을 수 없으므로 snapshot 당시의 historical pending을 보존한다. 이는 완료된 C10의 admission/게시/backup을 재개방하는 blocker가 아니다.
