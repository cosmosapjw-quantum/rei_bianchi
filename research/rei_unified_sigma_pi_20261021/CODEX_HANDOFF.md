# Codex handoff — REI unified LRS pilot, 2026-10-21

아래 block을 다음 Codex 세션에 그대로 전달한다. 최종 source/results commit과 provider ID는 FINAL_DELIVERY_ACK.json의 실제 readback 값을 우선한다. 마지막 metadata delivery HEAD는 현재 PR의 실제 HEAD 또는 포장 후 외부 transport ACK에서 확인한다. 이 파일 안의 과거 확인점은 현재 HEAD를 대신하지 않는다.

~~~text
[$physmath-research-loop] cosmosapjw-quantum/rei_bianchi 통합 연구를 이어가라.

먼저 현재 원격 PR198/199 HEAD, AGENTS.md, owner checkout branch/HEAD/dirty/untracked와 실제 Python/C++ runtime을 read-only로 확인하라. 기존 owner checkout을 사용하고 새 clone/worktree, reset, force-push, merge, unrelated process kill을 하지 마라. expected-head fast-forward와 draft 상태를 유지하라.

필수 intake:
research/rei_unified_sigma_pi_20261021/UNIFIED_STATUS.md
research/rei_unified_sigma_pi_20261021/UNIFIED_DAG.json
research/rei_unified_sigma_pi_20261021/FINAL_DELIVERY_ACK.json
research/rei_unified_sigma_pi_20261021/PHYSICAL_CONVENTION_ADAPTER.md
research/rei_unified_sigma_pi_20261021/CASE_PROVENANCE_LEDGER_INDEX.json
research/rei_unified_sigma_pi_20261021/independent_audit/
research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021/


최종 source/results publication=3a525e3e16f1ba9393818a800327cc58597fd7b5, tree=d12858ca1caa2496374e87f3fe3f489425eebda9.175files 전체GitreadbackPASS.
최종archive=REI_UNIFIED_FINAL_20261021_20261021T111808Z.tar.gz,36855980B,SHA7b39d8c8ffa0b61762211295a25d14412de37f6e1a6d163ebf0b93a8337f2251;Drive1PeQ_F7oNut4qjcy7dv5RCuEZBUk6th72;Dropboxid:BSpOijBcT10AAAAAAD_gOw.양쪽wholeGET와2900payloadhashPASS.
포장후metadata는별도ACK이며sourcepublicationcommit을실행당시commit이나미래의currentHEAD로가정하지마라.

과학 상태:
A: PR198 HEAD8bd35af5f11c7ea5945b656be1c013d1c1933498, reviewedsourceb140170ce0c58159368b6b81be49ac35ca764851.625+606,z20→4,8-state,half-contraction,기존PASS_SCOPED_PRELIMINARY. 재실행하지 마라.
B: 원래91+3=94개복구.175componentnominal=35exactreuse+140new,별도3newguards.중복제거231nominal+6guards=237unique histories 모두z20→2,153epochs. 현재 scientific pending cases=0.
B2 첫100개는 fullraw 저장후 RESULT JSON 직렬화 실패를0ODEdata-only검증으로복구했다. 실패INPUT/ATTEMPT/RESULT copy와raw는보존했다.137미실행tail만후속적분했다. ODEretry0.
실행 source: kernelPR1473b85dedce84d37b3e165da00685a8a984950aafe.
B1및최초100tail runner49d4464ecb4682846ace0d07411d3a9f9e49bc494fa8d641b567306725374d97.
137tail runnera7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64.
역사적94wrapper는UNPUBLISHED_WITH_SHA256이었다. 이후Git게시commit을 과거 실행commit으로소급하지마라.
B1child22.980342250994/240초(기존8.778983763986616포함),B2child100.95804054901964/120초(실패90.08237553801882포함).controller/operationreceipts도누적하고디렉터리/profile변경으로리셋하지마라.
C: PR199 AGE historicalHEAD964b2e3c098f6e475999a4eddc7a6aa0f8f053cc. 현재HEAD로가정하지마라. AGEtimeconvergenceHOLD,nonlinearGrackleNOT_ESTABLISHED,productionNOT_ISSUED.완료time8/16/32재실행0. V12cap180/debit200.39897231891518/remaining100NOT_AUTHORIZED유지.
PR213729case는a=.1999→.2의nativewarmslice다. 장시간z20→2pilot과합치지마라.

물리:
(-,+,+,+); a_perp=a exp(-b),a_parallel=a exp(2b),s=bdot.
sigma_hat=diag(-s,-s,2s),pi_X=diag(-p_X,-p_X,2p_X).
B의S_F=sqrt6*s/H,Σ_F=|S_F|,P_X=sqrt6*(8πG/c²)*p_X/H²,Pi_total=|P_m+P_r|.
Ahalf변수와signed값모두sqrt2로연결한다. 동일norm만으로rawreuse를허용하지마라.
massivefraction.1,mass/Tref30,canonicalnominal24x12/Gauss3,L8,guards48x24/L12,DOP8533e-11/3e-13.
matter/radiationinitialquadrupole독립. gamma/nu는같은초기brightness와collisionlessoperator; 독립gamma/nu초기quadrupole/충돌/nativechemistry구현주장금지.
massiveqdomain[0,infinity)compactification,임의finitehigh-qcutoff없음. 각speciesreflection-even/non-tilted이며 일반q_total=0만으로개별non-tilt를추론하지마라.

보존:
AarchiveSHA2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d(37945383B),Drive1i6x-HcPTctzSQwsxkET-CfTGfjpC-Dx7,Dropboxid:BSpOijBcT10AAAAAAD_fYA.
D0/D1archiveSHA25e1196e3050ae535273f1b88baf99183656bcd0930be49ff9a359e960594abf(10829091B),Drive1qHeeBL1y1uIbd7vY0pwo8t4asdNI8kbh,Dropboxid:BSpOijBcT10AAAAAAD_gLA.
D3archiveSHA7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498(31904176B),Drive1_noyMOexSIBbHdWIqkoGsvt3nBxwGZGi,Dropboxid:BSpOijBcT10AAAAAAD_gNA.
최종figure/report/source/rawarchive와게시ACK는FINAL_DELIVERY_ACK에서읽어라. 모두create-only이고actualuploadACK+wholeGET/bytes/SHA가필요하다. 포장시점과postpackACK를구분하라.
ledgerfullJSON/CSV는backup와deliverable에있고Git에는losslessgzip+index가있다. gzip복원후index의uncompressedSHA를확인하라.

NCP:
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
64CPU/128GB는역사적설명이다. 실제affinity/cgroup/RAM/disk/load를새turn에서확인하라. 준비된wrapper는max63/innerthreads1/nicecooperative이다.다른Codex작업은전면중단이유가아니다;실제가용slot만사용하라.
이전turn로컬key없음/DesktopCommander월quotaSERVICE_ERROR는영구runtimeblocker로상속하지마라.서비스가현재재시도금지를명시하면그경로를재접속하거나우회하지마라.
완료된237histories를NCP활용또는benchmark목적으로재실행하지마라. 현pending0이므로wrapper를자동launch하지마라.

완료된단일후속노드:
cancellation_turnover_on_saved_histories.0newIVP.초기(0,+.0003,-.0003)의S_F(z2)=-3.145959056164794e-5.153sample최대는z≈4.37195627,다음samplez≈4.30809546까지S_F'부호변경. 연속극값/fitting인증아님.
Σ_F,i=.003의25점중4점이z4양수→z2음수. P_r,i=-.001,P_m,i∈{-.0003,-.0001,0,+.0001}.
다음ready단일노드D8: 위4개저장history의signedS_F zero-crossing을153sample인접구간으로bracket하고caseID/rawhash와함께기록하라. 새ODE,dense-output재적분,continuouszero-contour추정은하지마라. 기존raw/source가부족하면정확한backup부터회수하고같은IVP를다시돌리지마라.
새주장에는해당범위만독립검토하고기존닫힌gates를재개하지마라. production/observational/generalnon-LRS승격은별도계약과검증이필요하다.
~~~
