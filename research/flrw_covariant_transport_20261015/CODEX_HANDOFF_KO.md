rei_bianchi의 research/flrw-production-integration-20261015(PR150)에서 이어가라.

AGENTS.md와 research/flrw_covariant_transport_20261015/의 LATEST_RESUME.json, HANDOFF.json(current_fields 우선), NEXT_DAG.json, FIVE_CASE_INDEPENDENT_REVIEW.json, OUTPUT_ALLOCATION_005_REVIEW.json, UNIT5_DELIVERY_RECEIPT.json을 먼저 읽어라. 게시된 후처리 문서가 있으면 research/flrw_full005_postprocess_20261015/의 HANDOFF와 독립 리뷰를 함께 읽어라.

NCP /root/REI_FLRW_COVARIANT_20261015_005/full_campaign001에는 기존 Q512·Q1024 전구간 실행이 있다. 마지막 관측은 실행 중이며 완료 여부를 새로 확인해야 한다. 중복 실행하지 말라. 최초 실행 epoch 1792075817.77407, 절대 종료 epoch 1792119017.77407(2026-10-16 02:50:17.774 UTC), science hard stop 02:45:17.774 UTC를 유지하고 재개 시 초기화하지 말라. 기본 Rust는 1.99.0이지만 이 실행은 검토된 1.94.1로 빌드됐다. 실행 중 source005와 binary를 바꾸지 말라.

owner 후처리 watcher PID 3567738, 외부 timeout PID 3567737이 이미 시작됐다. /home/cosmosapjw/REI_POSTPROCESS_20261015_001/AUTO_FULL005_001/WATCHER_STATUS.json을 확인하라. 후처리는 실제 COMPLETE와 고정 source/binary/config·전 행 장부 검사를 통과한 경우에만 전체 H/He 시간·실제 Tgas plot을 생성한다. watcher의 절대 종료는 2026-10-16 03:50:17.774 UTC다. 부분 결과나 pair 진단을 전체 정확도 증명으로 승격하지 말라.

Desktop Commander 월 한도로 추가 원격 호출이 차단됐다. 우회·재접속·반복 호출하지 말고 정당하게 복원된 승인 환경에서만 남은 원격 작업을 이어가라. 이미 실행된 작업의 실제 상태를 우선 확인하라.

새 post-cache profile은 아직 수치 결과가 없다. 두 실패를 보존하고 /root/REI_FLRW_HPC_PROFILE_20261015_003/src/hpc_profile.rs의 literal backslash-n 한 곳만 실제 개행으로 고치는 기계적 수정 1회가 승인되어 있다. 빌드 성공 시에만 60초/10000 RHS 이내 진단 1회, CPU16–31 최대16 workers로 진행하라. 기존 production·완료된 28개 검산·5개 short screen·cache benchmark를 반복하지 말라. 실제 CPU 사용은 마지막 약3.37코어이며 64코어 활용 목표는 미완료다.

이론 R1–R10 → 코딩 C1–C10을 변경 단위마다 실제 증거와 함께 수행하라. FLRW full pair 검토 후 지원되는 backend로 비경사 축대칭 Bianchi I를 이어가고, isotope-native donor/photo/recombination/thermal 연구를 병렬로 진행하라. q=0 전용 inactive_hi_split을 signed Bianchi에 그대로 적용하지 말라. 단일 에너지 소유권·기존 물리 기준·durable checkpoint를 유지하고, 완료 단위만 비공개 접근정보를 제외해 push/백업하라.

실행·구현 모델은 gpt-6.1-sol/high, 이론 판단·독립 과학 검토는 gpt-6-astra/high를 사용하라. 기록된 상태와 실제 관측을 구분하고 미완료를 완료로 승격하지 말라.
