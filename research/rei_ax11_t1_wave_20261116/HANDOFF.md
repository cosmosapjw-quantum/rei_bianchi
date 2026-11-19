# REI AX11 T1 두 native endpoint와 D01의 인계

상태: T1 ZERO/PLUS 모두 zbar4, 동일 저자 적대적 감사 후
`ADMIT_T1_TWO_CASE_NATIVE_HISTORY_AND_SAMPLED_D01_ONLY`.
**원 DAG10/17 · 확장28/88**, AX11 미완료, 새 완료 node0.

```text
$physmath-research-loop
PROJECT=cosmosapjw-quantum/rei_bianchi
GOAL=REI-AXBI-GOAL-20261014
CENTRAL_REVIEW_PIN=56dc609ea9b801c88d3364aed3eee140b3a20d46
RESULT_BRANCH=research/rei-ax11-source-profile-20261116
SCIENCE_RESULT_PIN=f75c35360d64420a840df6454c88ef0c7f1f2d4c
SCIENCE_RESULT_TREE=ee6c30f63fb2d912bfadb400a33b3d93b746b9db
PR=https://github.com/cosmosapjw-quantum/rei_bianchi/pull/377
UNIT=research/rei_ax11_t1_wave_20261116
먼저 이 파일을 포함하는 정확한 branch HEAD/tree와 REPORT_KO.md,
CURRENT_OUTCOME.json, OWNER_ADMISSION.json, results_v1/SUMMARY.json,
FULL_NATIVE_COST.json, receipts/CLOSED_RUN_LEDGER.json,
receipts/POSTPROCESS_LEDGER.json, DRIFT_WATCHDOG.json을 읽어라.
완료된 AX08 다섯 baseline, 원 AX08 continuation002, 이번 T1 두 이력을 재실행하지 마라.

시나리오 PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1,
homogeneous non-tilted axisymmetric Bianchi I, zbar20->4,
primary-only H/He Case-A escape; CR/HH/RCT/secondary/molecules OFF.
F05 OTS/F08 constant-H source/clock/state와 섞지 마라.
T1은 target2.5e-6, E16/mu8/background4096, 원래 physical IC/source/허용오차 유지.
각case757073accepted/2271279trials/15898977RHS, 최종a0.2, 정상exit0.
native root=/home/cosmosapjw/research_backups/rei_ax11_t1_wave_20261116_v1
evolution PID481017과 postprocess PID998068은 정상 종료했다. 재시작하지 마라.

원래 T0의fixed-a와fixed-t1001점표를 직접 소비했다.
새 T1도 두 mode 각1001점 모두 표현된다.
고정a max|D01 xHII|=0.00549585, max|D01 Tgas|=75.3988K;
ZERO xHII=.5 crossing이2.14836Myr 늦어졌다.
paired 변화는 재이온화 말기 일부 floor이상표본에서 원래0.1*|Delta1|을 초과한다.
fixed-a xHII5/766, Tgas3/753; fixed-t xHII7/682, Tgas5/791.
D01을 어느 수준의 참오차로 배정하거나 Richardson/연속상계/AX11완료로 승격하지 마라.
기존 AX08 conditional baseline admission은 유지한다.

다음 AX11 의무: full-IC T2 ZERO/PLUS와 실제D12; E와mu분리세수준 및 나머지원관측량 유지.
원12run/780만trial은폐기됨. baseline12회상당11241216trial.
실측T1한case2271279trial; 이번전체native debit11922.53CPU-s,
합산13552.735295wall-s(준비·예약·추출·archive 포함); 이전누적UNKNOWN보존.
남은첫wave예산은새T2자동실행권한이아니다. 실제현재runtime과출력비용으로다음유한량을bind하라.
이전unit research/rei_ax11_profile_20261116의 T2 original-start 실패와
별도h=1e-10 startup 성공근거를읽어라. 실패/최소step/허용오차를지우지마라.
AX12는이wave에서시작하지않았다. 새전역Volterra theorem을선행조건으로추가하지마라.

백업: /home/cosmosapjw/Dropbox/bianchi/rei_ax11_t1_wave_20261116_v1_archive
9개archive전체1,754,912,733bytes를provider에서실제읽어nativeSHA256및
Dropboxcontenthash일치확인. receipts/PROVIDER_BACKUP_VERIFICATION.json을재사용하라.
T1 sample inputs는native_inputs/의두gzip과EXTRACTION_RECEIPT.json이며,
실제결과표·milestone·그림은results_v1/에있다.
매turn consumer=rei_bianchi scientific admission owner / AX11와실제진전을확인하라.
원DAG10/17,확장28/88;문서/그림/재감사/비용개선으로node수를늘리지마라.
기존census를재사용하고변경분만읽어라. 새subagent없이자기적대적검증을수행할수있다.
```

최종 native checkpoint SHA256:

- ZERO: `85a09a8116d26b93de8a7989a0c52cc1377dec32607db7e8282cc054022becd8`
- PLUS: `c4e979b20b76fed4f06bf970901e6c613e35656f2e050353b71f6fff10aa6d5f`

검증된 T1 입력 gzip SHA256:

- ZERO: `40e536713e4cd8d872060a1213e3caaa21af8dab0bb48257bde747aab3e7c2f2`
- PLUS: `90d31e9acd3eba8286ad34fcdcd45696c35c0ce41b1500f2d751d0edddf7b91f`

부호·fraction/전자 정규화·경과 proper-time의 정의와 source binding은
SCIENCE_CONTRACT.md, receipts/BASELINE_REUSE.json 및 SOURCE_BINDING.json을 재사용한다.
