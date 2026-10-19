# 새 ChatGPT 스레드로 REI age-exposure 연구 이어가기

physmath-research-loop로 이어서 작업해줘. 먼저 아래 GitHub branch와 최신 백업을 실제로 읽고 신규 실행결과가 있는지 확인해. 이미 검증된 코드를 재작성하거나 완료된 NCP 결과를 이유 없이 재실행하지 마.

Repo cosmosapjw-quantum/rei_bianchi, branch research/rei-age-exposure-envelope-20261018, 경로 research/rei_age_exposure_envelope_20261018/. README_CURRENT_KO.md, HANDOFF_CODEX_CURRENT_KO.md, contracts/NEXT_DAG_CURRENT.json, DELIVERY_RECEIPT_CURRENT.json이 재개 기준이야. 신규 science commit a3b8c6100c12da2bbb7bb4b009f9a01057863632와 후속 bootstrap/배송 commit의 최신 HEAD를 확인해.

원 native SHA 35d9747a0bbedcafdb568467ce7c1e7a25f965b6를 유지해. PR171은 양성 source-matched reference 구현 PASS지만 age16->32 survivor90.13%, HeI spectral32->64 누적 photoevent0.749735%, native time 정확도는 HOLD야. 2026-10-18 fresh NCP q0-age8 replay는 성공했지만 age64/spectral128을 계산한 것은 아니야.

이 대화는 중단된 49-test 파일과 실제 원격74-test 코드를 복원한 뒤, 서로 다른 gas/opacity response를 비교하는 조건부 경계를 추가했어. 8개 새 경계 테스트와 1개 NCP bootstrap 테스트를 포함하여 83/83 PASS, 24개 prescribed-opacity 수치 사례를 실행했어. 같은 age measure라도 opacity가 다르면 W1=0으로 응답 차이가 사라지지 않아. 새 paired bound에는 실제 response sup-difference가 필요해. 일반적인 native nonlinear bound를 측정했다고 주장하면 안 돼.

원본 input153개를 검증해 native 준비 출력156개를 생성했어. Native Rust compile/NCP run은 이 재개에서 NOT_RUN이야. 실행기는 source/binary/config/outputs identity를 확인하고 failed attempt를 보존하며, pre/post 출생시각을 혼동하지 않아. NCP에서 컴파일/작은 연결수정/실행만 하도록 가능한 준비는 되어 있어.

다음은 age64, age32고정 time factor8/16/32, q+0.1/age8고정 transport128을 분리 실행하는 일이야. 샌드박스에서는 가능한 source 수정과 경량 검증을 끝내서 push해. NCP가 필요하면 HANDOFF_CODEX_CURRENT_KO.md의 명령을 사용하고, 필요한 프롬프트를 본문에 복사 가능하게 제공해. 단계마다 게시/백업/DAG를 명확히 표시해.

현재 Google Drive와 Dropbox는 복구 archive를 업로드한 이력이 있으며 최종 receipt의 정확한 SHA와 fresh replay 범위를 다시 읽어. 과거 tools unavailable/blocker를 현재 기능으로 단정하지 마. user checkout, PR150/R9 및 별도 BASS HHeD lane을 보호해. 전체 scientific production admission은 NOT_ISSUED야.
