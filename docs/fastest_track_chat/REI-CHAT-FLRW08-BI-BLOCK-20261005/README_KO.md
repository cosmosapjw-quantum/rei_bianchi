# FLRW08: Bianchi angular block comparison와 원 transaction 입력

판정: ANGULAR_BLOCK_COMPARISON_DERIVED_AND_LIGHT_CHECKED__ACTUAL_BI_RECORD_BLOCKED.
Logical task는 REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL이다. 직전 FLRW macro certificate를 유지하고, 실제 BI first macro 인증은 입력 대기로 남긴다. 기하나 FLRW 값으로 BI 각도별 endpoint를 만들지 않았다.

## 실제 자료 상태

Source-read HEAD a2bc41f848854e99e8eae9a3c5bfed06f14ccd43에서 T0_BI header와 independent receipt, source_manifest를 읽었다. README는 complete raw JSONL이 local-only라고 명시한다. 원 raw는 .cuh/fastest-track/REI-F08-PAIRED/whole-matched/T0_BI/T0_BI/trials.jsonl,273925074 bytes,SHA256 a908fe80eea46bdab2ca1f3b140fe8e03aa3f96ca6351e2dbf70eb9c2c133bd8이다. 이는 원 공개 receipt 값이며 이 환경의 raw readback hash가 아니다. 필요한 것은 원 첫 accepted transaction 하나다. 전체 campaign을 재실행하지 않는다.

## 새 이론

상수 H_i>0, fixed q_d에서 h_d=sum(H_i*q_di²*exp(-2H_i*t))/sum(q_di²*exp(-2H_i*t)), c_j=E_j/(E_j-E_(j-1)), lambda_dj=h_d*c_j. 실제 source weights는 w_d=J_d/sumJ,J_d=exp(-sumH*t)/g_d³다. Counts는 conserved H당, time은 proper s, density는 proper cm^-3,energy는 eV다.

Angular sum P_j=sum p_dj의 수송에는 C_j=sum(h_d-Hmean)*p_dj가 남는다: Pdot_j=Hmean*(c_(j+1)P_(j+1)-c_jP_j)+c_(j+1)C_(j+1)-c_jC_j-k_jP_j+Sdelta. 따라서 BI에서 FLRW mean-H closure로 바꾸지 않는다.

고정 b_d>0,sum b=1,p*=0.05와 v_dj=p_dj/(p*b_d)를 사용한다. Gas error u_i=|e_gi|, photon error V_j=sum b_d|e_dj|, residual R_j=sum b_d|r_dj|다. 공통 tube 전체의 derivative bounds가 있으면
D+V_j <= lambda_(j+1)^+ V_(j+1) -(lambda_j^-+k_j^-)V_j + Vhat_abs_j sum_i K_ji u_i + R_j.
Gas4와 이 photon9를 합한 13D Metzler comparison으로 원 gas4+128*9=1156D error를 지배할 수 있다. 이것은 물리적 angular state closure가 아니며 실제 BI tube/residual은 아직 계산하지 않았다.

|sum b*r|를 사용하면 안 된다. e1'=-2e1-1,e2'=-e2+1,e(0)=0,b=(1/2,1/2)에서 평균 residual은0이지만 t1의 mean error=0.0998941002234320이다. 유효 mean-absolute bound는1-exp(-1)=0.632120558828558이다.

기하적으로 h_d'=-2Var_d(H_i), w_d'=3w_d(h_d-sum w*h)이고 sum|w(t)-w(0)|<=2tanh(3(Hmax-Hmin)t/4)를 유도했다. H=(1.01,.99,1)*1e-14/s,T=1.25e9s,S=5e-15/H/s의 exact-decimal 진단에서 weight L1<=3.75e-7, integrated emissivity redistribution<=1.171875e-12/H다. 이는 actual binary header 대체나 gas/temperature/time-error bound가 아니다.

## 검증 및 다음 동작

정확 유리수 Dini241개, 기호항등식5개, finite geometry384점, unit4개, manufactured extractor protocol6개를 검사했다. 최종5명령 exit0. 잔차평균 순서 helper의 red/green은 기록했고 나머지는 tests-after다. Native/IVP/old campaign 실행0. Actual BI macro certificate0, 실제 raw extractor 실행0이다.

ZIP의 research/extract_bi_prefix.py는 기존 repo에서 고정 header를 읽고 원 raw 전체를 한번 streamhash하되 첫 accepted record까지만 JSON parse한다. Header와 acceptedline 원바이트/offset/hash를 새폴더로 반환한다. Full audit0와 committed audits1/2의 시각 및 gas chain을 검사한다. Schema가 다르면 exit78로 fail-closed하며 원문 기반 adapter를 요구한다. Solver/network/cargo는 호출하지 않는다. 추출 후 source-bound angular reconstruction과 arithmetic enclosure가 여전히 필요하다.

## 재현 산출물

REI_CHAT_FLRW08_BI_BLOCK_20261005.zip:48840bytes,40entries,39payload files.
SHA256:8acfc52a5a82bb1c792a35254a07e325fb446f4b4e0cc75fe29937969c2d2520
Drive:https://drive.google.com/file/d/1uOZb6rR49KwyUnkRhxeYrBQQ6ReVYA7u/view?usp=drivesdk
Dropbox:/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW08_BI_BLOCK_20261005.zip

ZIP의 rei_chat_flrw08_bi_block_20261005/ 아래 REPORT_KO.md에 전체 유도, research/에 검산·추출 코드, results/FINAL_VERIFICATION.json에 실행 증거가 있다. 이 repo폴더는8개 요약/계약/요청/결과/연결/반환/인계/백업 파일만 추가한다. 기존 code/CODEX_SYNC/runtime_returns/F00/F03/FT03/S0는변경없다. Samebranch non-force,이중백업 R1metadata. 전체 원격 restore는없다. local<2e-4,width<2e-3,[160,161]FAIL/tick160,physicalHOLD,auxiliaryescapeFAIL보존.
