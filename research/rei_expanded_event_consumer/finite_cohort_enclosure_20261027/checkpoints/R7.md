# REI finite-cohort R7 source checkpoint

Original DAG: working32/88; central27/88; increment0. Stage status: COMPLETE_ANALYTIC.

This UTF-8 JSON capsule contains exact source text for this stage. It is a raw-file backup, not a ZIP or a numerical execution report.

~~~json
{
  "schema": "REI_FINITE_COHORT_RAW_CHECKPOINT_V1",
  "stage": "R7",
  "stage_status": "COMPLETE_ANALYTIC",
  "expected_parent": "c1b736238a45ff0bd17b1280573ae441780c994d",
  "unit": "research/rei_expanded_event_consumer/finite_cohort_enclosure_20261027",
  "format": "UTF8 source text; restore each files[].text to its relative path",
  "files": [
    {
      "path": "stages/R7.md",
      "text": "# R7 — 판별 검증\n\n상태: COMPLETE_ANALYTIC. 원래 DAG: 작업 **32/88**, 중앙 **27/88**, 증분 **0**.\n\n순수 정리의 증명은 CAS나 수치 샘플에 의존하지 않는다. Root와 독립 검토자가 다음 정확한 사례를 손으로 대조했다.\n\n| Cohort와 누적 정보 | 관측창 | 정확한 infimum / supremum |\n|---|---|---|\n| h=1 on[0,1], grid(0,2), F(2)=1 | [0,1] | [0,1] |\n| 동일 | [1,2] | [0,1] |\n| 동일 | [0,2] | [0,1] |\n| 동일 | 앞 두 창의 shared kernel 합 | [0,1] |\n| h=1 on[0,1], grid(0,1,2), F(1)=F(2)=1 | [1,2] | inf0 비달성, sup1 달성 |\n| h=s on[0,2], grid(0,1,2), l=(0,1,3), u=(0,2,4) | [0,1] | [0,1] |\n| 동일 | [1,2] | [1/2,4] |\n| 동일 | [0,2] | [1/2,5] |\n\nBox 사례의 U01+U12=2>U02=1은 개별 최적 상한을 합치는 오류를 판별한다. 실제 고정 F의 관측량은 가법성을 유지한다. Lower nonattainment는 delta_epsilon에서 D=epsilon>0이고 epsilon→0인 구성으로 증명했다. Affine 환원은 기존 결과와 telescoping 증명을 재사용한다.\n\n새 과학 실행과 CAS evaluator 실행은0회다. Wolfram context 실제 조회와 공식 문서 위치는 R2에 기록했다. 새20tests와 이전 미실행16tests는 예산 승인 후 첫 검증을 위해 준비됐으며 실행 PASS로 기록하지 않는다.\n\nR6 뒤 presentation helper의 시작 비용이 예약을 넘었다. BUDGET_STOP.json에 실제 비용과 실패를 보존한다. 이번 단계부터는 원문 체크포인트를 Git에 게시하고 Drive/Dropbox 완료 ACK를 확인한다. 새 ZIP 생성과 local runtime은 중단 상태다.\n"
    },
    {
      "path": "BUDGET_STOP.json",
      "text": "{\n  \"schema\": \"REI_FINITE_COHORT_RESOURCE_STOP_V1\",\n  \"status\": \"HOLD_RESOURCE\",\n  \"original_policy_caps_CPU_s\": {\n    \"planning\": \"10\",\n    \"presentation\": \"30\"\n  },\n  \"restored_policy_caps_CPU_s\": {\n    \"planning\": \"10\",\n    \"presentation\": \"30\"\n  },\n  \"planning\": {\n    \"cumulative\": \"15.077490885\",\n    \"prior_temporary_cap\": \"14.99\",\n    \"new_local_planning_or_scientific_runs\": 0,\n    \"approval\": \"SEPARATE_GATE_PENDING\"\n  },\n  \"presentation\": {\n    \"inherited_cumulative_and_prior_reservations\": \"43.787562494\",\n    \"new_measured_closed_process_CPU_s\": \"1.103205\",\n    \"new_final_tail_reservation_CPU_s\": \"0.10\",\n    \"total_with_reservations_CPU_s\": \"44.990767494\",\n    \"unit_reservation_before_last_close_CPU_s\": \"1.19\",\n    \"actual_plus_new_tail_CPU_s\": \"1.203205\",\n    \"unit_reservation_exceeded\": true,\n    \"temporary_cap_history\": [\n      \"44.99\",\n      \"44.9999\"\n    ],\n    \"last_cap_authority\": \"44.9999 applied prospectively only to close the already running process; strictly below1.5*30; no retroactive PASS\",\n    \"current_policy_cap\": \"30\",\n    \"local_packaging\": \"STOPPED\"\n  },\n  \"closed_processes\": [\n    {\n      \"id\": \"nonTTY_EOF\",\n      \"CPU_s\": \"0.053216\",\n      \"exit\": 0\n    },\n    {\n      \"id\": \"TTYcanonical_decode_stop\",\n      \"CPU_s\": \"0.060831\",\n      \"exit\": 0\n    },\n    {\n      \"id\": \"stage_R1_R5\",\n      \"CPU_s\": \"0.459954\",\n      \"exit\": 0\n    },\n    {\n      \"id\": \"stage_R6_batchedTTY\",\n      \"CPU_s\": \"0.403988\",\n      \"exit\": 0\n    },\n    {\n      \"id\": \"final_helper_startup_budget_refusal\",\n      \"CPU_s\": \"0.125216\",\n      \"exit\": 0,\n      \"planned_cap\": \"0.11\",\n      \"startup_observed\": \"0.124035\",\n      \"metadata_operation_started\": false\n    }\n  ],\n  \"failures_preserved\": [\n    \"nonTTY immediate EOF before file work\",\n    \"orchestration store(undefined session_id) error; no science state change\",\n    \"canonical TTY JSON truncation and JSONDecodeError before file write\",\n    \"last helper startup exceeded its0.11 reservation; first metadata operation refused\"\n  ],\n  \"main\": {\n    \"cumulative\": \"595.225063\",\n    \"cap\": \"600\",\n    \"instruction\": \"NO_MORE_IVPs\"\n  },\n  \"foreign_owner_budgets\": \"UNCHANGED_NOT_BORROWED\",\n  \"historical_causal_attempt\": {\n    \"child\": \"0.192151\",\n    \"wrapper\": \"0.074169\",\n    \"held_tail\": \"0.02\",\n    \"total\": \"0.286320\",\n    \"reservation\": \"0.18\",\n    \"overrun_preserved\": true\n  },\n  \"publication\": \"Existing authorization retained for Git expected-SHA/nonforce and raw source backups\",\n  \"format_change\": \"R1-R6 retain actual ZIP/CRC/hash/dual ACK. R7 onward use UTF8 source checkpoints and completed dual raw-file ACK; final whole-unit ZIP remains pending additional presentation budget.\",\n  \"unknown_cost\": \"UNKNOWN_NOT_ZERO for connectors, remote services, LLM, patch writes, reviewer unmeasured reads and metadata overhead\",\n  \"resets\": 0,\n  \"transfers\": 0,\n  \"science_as_presentation\": false,\n  \"new_science_runs\": 0,\n  \"new_test_runs\": 0\n}\n"
    },
    {
      "path": "preflights/R7.json",
      "text": "{\n  \"stage\": \"R7\",\n  \"observed_UTC\": \"2026-10-27 13:12:08 UTC\",\n  \"actual_HEAD\": \"c1b736238a45ff0bd17b1280573ae441780c994d\",\n  \"AGENTS_blob\": \"6464cd96b7023e3e91e30246bc93650d4e435a10\",\n  \"parallel_returns\": \"Source surveys, analytic review, lower-tier implementation and independent static review returned; final CR/central/WU/BASS delta collected.\",\n  \"previous_stage_ACK\": {\n    \"stage\": \"R6\",\n    \"commit\": \"c1b736238a45ff0bd17b1280573ae441780c994d\",\n    \"drive\": \"1zQZCatKLG2Vp3GHMLmyY6Rn2-XzgO_Rj\",\n    \"dropbox\": \"id:BSpOijBcT10AAAAAAEDHng\"\n  },\n  \"DAG\": {\n    \"working\": 32,\n    \"central\": 27,\n    \"total\": 88,\n    \"increment\": 0\n  },\n  \"independent_review\": \"R6 analytic review and C9 static source review; runtime pending\",\n  \"science_executions\": 0,\n  \"local_runtime\": \"STOPPED_RESOURCE_HOLD\",\n  \"unmeasured_cost\": \"UNKNOWN_NOT_ZERO\",\n  \"delivery_format\": \"RAW_MARKDOWN_CHECKPOINT; ZIP deferred by resource hold\"\n}\n"
    },
    {
      "path": "delivery/R6_ACK.json",
      "text": "{\n  \"stage\": \"R6\",\n  \"stage_status\": \"complete\",\n  \"commit\": \"c1b736238a45ff0bd17b1280573ae441780c994d\",\n  \"parent\": \"611ff429448ec35eaa472bb9429f2eac2da2200e\",\n  \"tree\": \"a24db7157a8c23679f85cccf4b8947a052596ad1\",\n  \"expected_sha\": \"611ff429448ec35eaa472bb9429f2eac2da2200e\",\n  \"force\": false,\n  \"archive\": \"/workspace/scratch/52cc495a5f0a/rei_archives/REI_FINITE_COHORT_R6_20261027_c1b736238a45.zip\",\n  \"sha256\": \"34ccc0df9dfcbdd035741693570645ce78e34f50908794d81c62c97193511575\",\n  \"bytes\": 7314,\n  \"entries\": 6,\n  \"crc_passes\": 1,\n  \"drive\": {\n    \"id\": \"1zQZCatKLG2Vp3GHMLmyY6Rn2-XzgO_Rj\",\n    \"completed\": true,\n    \"observed_bytes\": 7314\n  },\n  \"dropbox\": {\n    \"id\": \"id:BSpOijBcT10AAAAAAEDHng\",\n    \"status\": \"completed\",\n    \"observed_bytes\": 7314,\n    \"path\": \"/bianchi/research_backups/rei_bianchi/REI_FINITE_COHORT_R6_20261027_c1b736238a45.zip\"\n  },\n  \"DAG\": {\n    \"working\": 32,\n    \"central\": 27,\n    \"total\": 88,\n    \"increment\": 0\n  },\n  \"science_runs\": 0,\n  \"presentation_cpu_cumulative_process\": 0.40273,\n  \"self_receipt\": \"This ACK is published with next stage; final ACK uses one nonrecursive closeout.\"\n}\n"
    }
  ],
  "science_executions": 0,
  "DAG": {
    "working": 32,
    "central": 27,
    "total": 88,
    "increment": 0
  },
  "resource_status": "HOLD",
  "ZIP_status": "DEFERRED_SEPARATE_BUDGET_GATE",
  "unmeasured_cost": "UNKNOWN_NOT_ZERO"
}
~~~
