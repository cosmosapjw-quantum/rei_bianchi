rei_bianchi의 research/flrw-production-integration-20261015에서 이어가라.
AGENTS.md와 research/ncp_direct_resume_20261016/{HANDOFF.json,NEXT_DAG.json,RUNBOOK_KO.md,INDEPENDENT_REVIEW.json,CONCURRENT_INTEGRATION.json}을 먼저 읽어라. 최신 Git HEAD를 확인하고 다른 작업 스레드의 변경을 보존하라. SOURCE_RESTORE.json은 최초005 복구 기준이다. 현재 ZIP은 d3bbd732의 opt-in source006을 포함하며 현재 파일 목록/해시는 ZIP_CONTENTS.json과 CONCURRENT_INTEGRATION.json을 따른다. source006 코드를 실행 중 stage005에 덮어쓰지 말라.

이 Codex는 NCP 로컬 파일시스템에서 실행한다. ncp_resume.py status로 source005 full_campaign001의 실제 argv/receipt/checkpoint를 확인하고 backup_ncp.py compact로 보존하라. 기존 solver와 owner watcher를 중복 실행하지 말고 최초 epoch1792075817.77407 및 campaign 마감2026-10-16 02:50:17.774 UTC를 유지하라. 진행률은 관측시각과 함께 기록하라.

중요: resume_20261016_001의 post-cache profile은 실제 완료·독립 PASS·게시·백업됐다. repair/build/run allowance는0/0이다. 개행 수정이나 진단을 재실행하지 말라. 완료된28개 검산,5개 short screen,cache benchmark도 재사용한다. v1 ZIP의 pending profile 안내는 폐기된 역사본이다.

완료된 source006도 재사용하라: research/flrw_jacobian_columns_20261016/{CONTRACT.json,LOOP_RECORD.json,RESULT.json,INDEPENDENT_REVIEW.json}. opt-in Jacobian4열 구현, 집중 테스트7개, 단일504RHS 진단이 완료됐다. test/build/run 잔여량은0/0/0이며 반복하지 않는다. 기본 flag=false, source005 배포/재시작·새 full run은 이 완료된 실험 범위에 포함되지 않는다.

병렬 작업A: 실제 donor·photo/recombination·thermal provider 연구 및 다음 production-adoption/refinement 단위의 설계를 진행하라. 완료된 source006의 한 fixture 1.324배를 전체 속도로 일반화하지 말라. 실제 full005 검토 이후 필요한 변경 의존성/수렴 근거만 대상으로 이론 R1–R10→코딩 C1–C10을 수행하고, 추가 실행 전에 별도 유한 contract와 worker·CPU/메모리/출력 예산을 정하라.64코어/128GB 개선은 측정된 처리량과 필요한 독립 refinement/parameter tasks를 함께 설계하며 메모리를 인위적으로 채우지 않는다. 실행 중 source005는 보존한다.

병렬 작업B: 기존 두 full case의 실제 successful terminal/binding/ledger 조건이 충족되면 기존 owner 결과를 재사용하거나 postprocess_ncp.py로 경과 proper time·실제 Tgas에 따른 H/He 비율과 보고서를 생성하라. 후처리는 원래 절대마감2026-10-16 03:50:17.774 UTC를 유지한다. partial/failed는 해당 상태로 보존하고 자동 연장하지 않는다. Q512/Q1024 공간해상도 쌍을 whole-history time/angular 수렴 근거로 승격하지 말라. backup_ncp.py full로 종료된 case별 원자료를 보존하고 승인된 저장소 업로드/readback을 기록하라.

최종 목표: FLRW production solver와 필요한 전구간 수렴을 완성한 뒤, 지원되는 signed backend로 비경사 축대칭 Bianchi I를 연결한다. D/추가 핵종 donor·photo/recombination·thermal provider 연구는 병렬로 계속할 수 있지만 실제 provider/에너지 소유권 조건 전에는 반응망을 활성화하지 않는다. 실제 시간/Tgas에 따른 핵종·이온 비율 plot과 보고서를 완성한다. 완료 단위별 durable checkpoint·push·백업을 유지하고 비공개 raw/접속자료는 공개 Git에서 제외하라. 생산 변경과 통제된 실행은 사용자가 승인했다. 이미 완료된 검산·승인을 반복하지 않는다.

구현: gpt-6.1-sol/high. 이론 판단·독립 과학 검토: gpt-6-astra/high. 실제 런타임 모델은 별도 관측 없이 단정하지 말라.
