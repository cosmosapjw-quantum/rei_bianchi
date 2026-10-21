# 다음 대화 인계

$physmath-research-loop를 사용해 cosmosapjw-quantum/rei_bianchi의 독립 non-tilted LRS pilot을 이어라. 최신 사용자 요구는 π_ab를 matter와 radiation으로 각각 고려하는 것이다. 초기 Σ0뿐 아니라 signed Pi_m0, signed Pi_r0를 구분하라. 기존 PR198 branch `research/rei-lrs-v14-physical-birth-20261018`을 사용하고 실제 remote HEAD를 먼저 확인하라. 최신 상세 경로는 `research/rei_bianchi_sigma_pi_pilot_20261021/matter_radiation_20261021/`다.

먼저 FINAL_DELIVERY.json, SOURCE_DELTA.json, ROOT_ADMISSION.json, DAG.json, RESEARCH_REPORT_KO.md, evidence/FINAL_REVIEW.json, evidence/RESPONSE_FIT_ADDENDUM.json, CODEX_NCP_EXECUTE_KO.md를 읽어라. Source/validation checkpoint `34f93a48778a2d8a36b058e33de5302732752bae`와 과거 parent delivery `53eb52f57e5de2f2f850bde97daf3a1f5235c039`를 현재 HEAD로 오인하지 말고, 최종 metadata의 containing commit와 실제 branch를 재확인하라.

이번 thread에서 기존 625개 history의 40,625개 sample을 ODE 재실행 없이 분해했다. 새 matter 600개 + mixed 6개 = 606개 trajectory/39,390개 sample이 실제 완료됐고 실패는 0이다. Matter zero axis의 25행은 기존 source/actual k/axes/hash를 보존한 REFERENCE_REUSE이며 새 실행 수가 아니다. 원래 parent model 6개 및 raw 2,500개 파일은 byte-identical하다. 완료된 local numerical gate, 독립 Astra PASS_SCOPED_PRELIMINARY와 fit addendum을 의무 반복하지 말라. 새로운 실행 반환이 있으면 command/source/stdout/stderr/exit/raw부터 읽고 그 결과를 우선하라.

물리 범위는 자체 중력·충돌 없는 reflection-even LRS, 동일 orthonormal normal frame, zbar 20→4, massive fm=.1, m/Tref=30, 24×12 Gauss3, L8, 8 states다. Matter는 massive collisionless 성분과 stress가 0인 dust, radiation은 photons와 massless neutrinos다. Half-contraction norm을 유지한다: Sigma=sqrt3|s|/H, signed Pi_X=sqrt3(8piG/c²)p_X/H² (p는 J/m³). Pi_total=|signed Pi_m+signed Pi_r|이며 Pi_m+Pi_r로 대체하지 말라. 일반 non-LRS tensor 방향이나 native H/He feedback을 완료했다고 확대하지 말라.

실제 mixed S0=0, Pi_m0=+.0004, Pi_r0=−.0004에서 초기 total≈0이어도 Sigma_end=4.908041156489128e-5가 생긴다. 실제 1,225개 training 조건(기존 radiation 625+새 matter 600)의 descriptive fit은 S_end≈.11438019418589546 S0+.11914730406637555 Pi_m0+.24184661410997463 Pi_r0다. Mixed 6개는 fit에 쓰지 않았으며 heldout 최대 차이는 5.950057285048459e-8이다. 이 유한 empirical fit을 일반 선형 superposition 법칙이나 continuous certificate로 승격하지 말라.

새 NCP 실행은 NOT_RUN이다. 지정 연결은 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`다. 이전 sandbox에는 key가 없었고 remote tool은 월 사용량 소진이었다. 실제 접속 가능한 환경이면 기존 checkout/dirty 상태/다른 작업을 보존하고 가용 자원 안에서 진행하라. 다른 세션이 있다는 이유로 일괄 중지하거나 kill하지 말라. 사용자에게 수동 SSH/SCP나 파일 다운로드를 요구하지 말라.

정상 wrapper는 `bash research/rei_bianchi_sigma_pi_pilot_20261021/matter_radiation_20261021/run_ncp.sh`다. 새 606개만 실행하며 최대 64 workers, 실제 resource observations, single BLAS, wall 900초/aggregate child 3,600초, 자동 retry 없음을 유지한다. 기존 625개 raw 전체가 없어도 게시된 reference_controls와 old_representative table로 실행·plot이 가능하다. 이 경로는 Python pilot이며 기존 native Cargo 실행 계약과 구분한다.

기존 V12 cap 180초/debit 200.39897231891518초와 남은 100개 NOT_AUTHORIZED를 보존하라. 완료된 AGE time8/16/32와 기존 84/19를 새 연구로 재집계하거나 replay하지 말라. Native age/time convergence HOLD, nonlinear Grackle bound NOT_ESTABLISHED, production NOT_ISSUED다. Borrowed-cell clone 제거 결과를 speedup으로 승격하지 말고 default legacy/performance cell-cache를 유지하라. 이번 8-state 구현·성분 분해·병렬 실행은 scope가 다르다.

Full archive의 코드·raw·manifest는 최종 delivery가 연결한 Drive/Dropbox 위치에서 직접 읽어라. Archive 문서는 포장 시점 상태이며 이후 ACK와 최종 Git metadata가 게시 완료를 닫는다. 대화 검색 unavailable, Drive 부분 목록, 첨부 선택 멤버 조사를 전체 전수검색 성공으로 꾸미지 말라. Astra 계약/판정 → lower-tier 구현/실행 → 구현하지 않은 Astra 독립 검토를 유지하고, 닫힌 수치 검토를 반복하기보다 새 NCP 반환과 다음 유한 과학 질문을 우선하라.
