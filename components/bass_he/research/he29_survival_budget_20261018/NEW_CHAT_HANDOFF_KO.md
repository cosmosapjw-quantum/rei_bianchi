# 새 대화에서 이어갈 프롬프트 — HE29 실제 HPC64 canary 완료

```text
$physmath-research-loop로 BASS_HE HE29 작업을 이어서 진행해 줘.
필요한 새 이론·코딩 연구에 SciSpace/Exa/Wolfram을 사용하되 완료 연구·검증·native 실행을 반복하지 마.
여기서 가능한 코드 수정은 여기서 완료하고 push하며 NCP에는 compile/작은 환경 수정/준비된 실행만 넘겨.
사용자에게 파일 다운로드·업로드·터미널 작업을 요구하지 마.

[현재 실제 완료]
기존 native reference4/4 pair 재사용 + 신규 packed canary1/1 완료를 별도로 집계해.
모두 m8/GL4/q0. reference는 r2/512,r4/512,r8/512,r4/1024의 Radau+DOP853.
packed canary는 r4/table512 한 건이며 원래 모든 finite gate PASS.
현재 준비된 HE29 미완료 실행은0개. RUN_READY/START_REFERENCES/PUBLISH를 다시 호출하지 마.
다른 모델의 미완료 작업을 HE29 queue에 자동 추가하지 마.

[Git]
https://github.com/cosmosapjw-quantum/BASS_HE
branch research/he29-survival-budget-20261018
PR78 https://github.com/cosmosapjw-quantum/BASS_HE/pull/78
PR81 https://github.com/cosmosapjw-quantum/BASS_HE/pull/81
둘 다 Draft/open/unmerged를 유지해.
실행 code802a32361288bf5aa0e0d1f63c912768f1a1d407, treebf52fcabc3b03e00df140d2fdf913f05b3699d08.
소비자 분석 pin5eb38cbfeed7abf60e1827e358611c8f763c2da4, treea01fbb23bc3fec9b45092fd7caa42e01861830c4, 실제12/12 raw readback PASS.
결과 원본d6c1cf97ee216269114b1b0d1bb45984e2140f8b는 tree가13결과파일만 포함하는 게시 결함이 있었어.
fcdf56d9a66b2d159d42a9a72131f94040cd5891(treeffef714245a9a69a008395e0f93ae7893173d91a)에서
base4b7621bab965913608e76f9a82991935f22d5c23의6189blob과 원본13결과blob을 그대로 보존해 복구했어.
원본d6c1와base4b762를 모두parent로 유지하고 force/PRmerge없이 수정, 실제PRdiff13추가/삭제0.
결과13/13raw Git readback과manifest12/12 PASS. 각단계의중복파일수를합산하지마.
최신 문서HEAD와 최종raw영수증/보존identity는 PR78·최신DELIVERY에서 실제로 읽어.

[먼저 읽기]
research/he29_survival_budget_20261018/README_KO.md,DAG_STATUS.json,CODEX_HANDOFF_PROMPT_KO.md,NEW_CHAT_HANDOFF_KO.md.
현재lane canary_intake_20261021T0118Z의 README_KO,RESEARCH_KO,DAG_STATUS,DELIVERY,NCP_HANDOFF_KO.
evidence/CONSUMER_ANALYSIS.json,EXECUTION_PROVENANCE.json,PRODUCER_RETURN_RECEIPT.json,
PR81_TREE_REPAIR.json,ANALYSIS_PUBLICATION_READBACK.json,INTAKE_BOUNDARIES.json 및최종closeout영수증.
기존hpc64_20261021과native_intake_20261020T1315Z의완료검증은재사용해.
새 연구 전에 다른대화/GitHub관련branch/repo/백업의 이후 실제변경분부터 확인해.
기존 intake의 bounded범위와오류기록을읽고 모든대화/미게시실행 부재를주장하지마.
이번 personal-context조회는 성공했지만 이전PR80/ready/auth-HOLD 문맥만반환했어. 예전서비스오류이력은별도야.

[실행과수치identity]
packed corea5d4711460c09b310b78c9692aa62534b7a843d3, VigilODEa21d573980f66fe02891bd216153443b5352f921,
watchdoged5adca43f474553a9bce7f5de45d464be5905cb, ownerf7830e2f55e7a1938bc3c98f61b60651f8dae474.
native binarySHA a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9.
bridgeSHA28d637a9011ad0e23c087659cd07574cfb0ddc55511380c4c807165aee3123eb.
tableSHA919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd.
소비자는새bridge bytes/gzip전체182281record/6adapter source bytes를확인했어.
새archive에는원래owner binary/table arrays/22DATA bytes가없으므로producer검사와이전admission을재사용한범위를명시해.
Python3.12.3,NumPy2.3.5,SciPy1.17.0,solverthread1,full-state663=640photon+4gas+19ledger.
온도8.239220060997875K,photonnumber3.851175483221473e-8/H,energy9.546047635593837e-7eV/H.
packed−Radau=-1.1191048088221578e-13K,packed−DOP853=-8.881784197001252e-14K.
두후보hull밖이지만원래1e-9K gatePASS. 후보hull/solver일치를참ODEerrorradius로사용하지마.

[실측성능과자원]
native182280calls,83segments,accepted7889,attempts12565,rejected4676.
table48worker/build8jobs/solver1thread,CPU55보호와8CPUreserve.
bridgecompile104.118856s,tablepool2.790717s,tablediagnostics3.753131s,source-model/cache3.808606s,
packedsolve/checkpoints710.211015s,worker717.158505s,watchdog717.331125s. 중첩timer를합산하지마.
이전45.139469s/newtablediagnostics의12.0271비는역사적phase비교이며통제된scaling이아니야.
이전1190.317610s는두reference방법작업이므로canary와나눠전체speedup을만들지마.
CSR/제조IVP/제조I/O배율도곱하지마. 동일packed전후대조speedup은아직미측정.
solve/checkpoints가worker99.0312%이므로향후최적화질문은그내부비용분리야. count만으로walltime귀속하지마.

[실행경계]
다섯유휴Codex process의정확한PID/start_ticks/cmdlineSHA만사용자가일회성승인했고종료·신호0.
원래Gitbytes는유지됐지만외부runtime sitecustomize shim이존재했어. 미래실행예외로재사용하지마.
초기wrongpackedroot HE29_HPC_GIT_REVISION 실패는build/canary0인실행전기록으로보존됐어.
이전SSH인증HOLD는역사적시도이며현재완료canary상태가아니야.
이번소비자NCP제출/시작/native/compile은모두0. 현재liveNCPcensus는수행하지않았어.
Remote Desktop Commander의quota/no-retry금지유지,어떤메서드도다시호출하지마.

[보존]
BASS_HE_HE29_HPC64_CANARY_RETURN_20261021_a00990e5.tar.gz,32120999bytes,
SHAa00990e5f8a5978a8881c1b56fb96072df5abd91600495494b9397cc9360aec7.
Dropboxid:BSpOijBcT10AAAAAAD_ceQ,Drive1IrWYFe_08-s1CfAcV2FgszDoMj5E_5sG.
producerdualrawPASS와consumerDropboxrawPASS. outer20/21,nested39/40은중복구조,고유합산금지.
중단중workspacepruning으로사라진local자료는같은Git/archive에서복원했어.
앞독립검토임시원본은pruning으로유실되어byte동일복원을주장하지않고읽었던범위만PRIOR_REVIEW_RECOVERY에기록했어.
미완료였던consumerrawgzip분석은실제PASS. 완료suite/62tests/09929/native4pair는재실행0.
새분석·현재두prompt·최종Git영수증보존identity는최종PR78와detachedreceipt에서읽어.
과거DriveUNKNOWN은그대로이며이번소비자Drive/RDC0,기존upload재시도금지.

[과학gate와범위]
fraction1e-11,방법간온도1e-9K,number3e-15/H,energy3e-12eV/H,species3e-12,
원래positivity,rtol1e-10/scaledatol1e-12와19ledger full-state norm유지.
연속스펙트럼/전역gas온도오차상한/전체EoR/wholeGrackle/관측Bianchi-CMB HOLD.
실제DAG/Git/백업상태와재사용결과/새실행결과를분리해기록해.
```
