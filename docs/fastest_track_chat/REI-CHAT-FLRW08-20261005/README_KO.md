# FLRW08: paired 시간오차의 유한 검증과 연속 defect 조건

판정: FINITE_REFINEMENT_TARGETS_MET__AUXILIARY_DIAGNOSTIC_FAIL_PRESERVED__CONTINUUM_CERTIFICATE_OPEN.

Logical task는 REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL이다. 실제 F08의 연속 시간오차 인증은 계속 partial이며, 이번에 완료한 finite diagnostic과 조건부 정리를 그 인증으로 바꾸지 않는다.

## 실제 연구 결과

FLRW07의 12개 공통 사건구간을 24,48,96,192,384,768 source 단계로 각기 세분화했다. 두 기하는 모든 수준에서 같은 nested grid를 사용한다. 원 source 13개, 원자모형, residual tolerance 1e-14를 유지한 Rust 1.94.1 단일 process에서 12개 제한된 이력, 3024개 source 단계를 실행했다. 이전 level0과 독립 DOP853/Radau reference는 byte identity를 확인해 계승했고, 새 ODE 적분과 독립 root solve 및 외부 대규모 campaign은 0회다.

최종 TF=46141.20576830989 K, TB=46141.84215510958 K, 차분=0.636386799691536 K. 계승 연속 기준 대비 각 오차는 0.4237038169/0.4236587551 K, 차분 오차는 -4.506178084e-5 K다. 사전 목표 각 0.5 K/차분 1e-4 K를 만족했다. 마지막 관측 차수는 TF0.99924644, 차분1.00025980이다. Scalar Richardson 차분0.6364318664564053 K는 기준과4.984e-9 K 차이지만, positivity-preserving state나 엄밀한 continuum certificate가 아니다.

추가 escape increment 상대진단은 기준2e-11에 대해 최대2.79592e-11로 실패한 채 보존했다. 최대 절대차는3.83587e-19 eV/H다. 옛 primary_stage_step의 prethermal-rate 사용과 total-energy-normalized 종료조건을 독립 재구성으로 확인했다. 기준 완화와 source 수정은 없고, 최신 F08 conservative solver의 결함으로 확대하지 않는다.

## 새로운 직접 유도

연속 재구성 residual r_g, 실제 오차 e_g, 평균 Jacobian A_g를 두면 delta=e_B-e_F에 대해

delta'=A_B*delta+(A_B-A_F)*e_F-(r_B-r_F).

같은 residual 또는 공통 grid만으로 차분오차가 0이 되지 않는다. 허용된 전체 tube에서 lognorm L_B, Jacobian차 M_delta, residual차 R_delta, 한쪽오차 B_F가 검증되면 exp-propagated integral(R_delta+M_delta*B_F)로 상계한다. 비선형 T/lnT goal에는 gradient 차이 항도 남는다. Scalar9조합을60자리 quadrature로 검산했다. 실제 F08 time-slab tube/residual/stability bounds는 아직 없다.

## 최신 외부 결과 수신

시작/연구경계/게시직전 HEAD e63ca0735a3e3e7eebbf4498c697d806d375e191을 읽었다. F08은15개 prescribed discrete histories를 완료했고 F09는 provider/domain blocker다. F08의 xHII 차분 T2-T1 점변화 -3.57507e-11과 인증된 이산 차분 변화구간 약 +/-2.11e-8은 별개다. 점값은 대략1차 수렴하지만 interval width는 증가한다. 모든 수신 차분구간이 양수라는 사실도 discrete scope를 넘지 않는다. External tests나 campaigns를 새 실행으로 재집계하지 않았다.

본 진단의 finite rays/pulse/G-BE-G와 F08 S0의 연속 source/fixed energy deposition/conservative two-half method는 서로 다르다. 정확한 source/blob과 수신 필드는 SOURCE_BINDING 및 CONCURRENT_SOURCE_ACK, ZIP의 inputs/F08_SELECTED_RETURN.json에 있다.

## 재현과 인계

REI_CHAT_FLRW08_20261005.zip, 2843898 bytes,72 entries/71 manifest payloads.
SHA256: 929fbff75088931f0135435722eab3d46f82f950f6127de81aa242272c486ab3.
Drive: https://drive.google.com/file/d/1WrwX0zc5FH3yOhJmausraQPWmWNWQA-4/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW08_20261005.zip

전체 REPORT_KO.md, frozen sources, 실제 binary/stdout, 독립 검사기 및 실패 로그는 ZIP의 rei_chat_flrw08_20261005/ 아래에 있다. research/final_check.py는 저장 증거를 검사하며 보존된 auxiliary FAIL을 PASS로 바꾸지 않는다. research/reproduce.py --output NEW_DIR는 신규 디렉터리에서만 실제 진단을 재현한다. 이 orchestration wrapper는 문법 검사만 수행했고 동일 전체 재현을 반복하지 않았다.

다음 최소 연구는 실제 F08의 fixed spectral/angular 연속 semidiscrete generator와 첫 accepted time slab의 reconstruction defect를 연결하는 일이다. 새로운 전체 campaign 재실행은 필요하지 않다. 현재 logical FLRW08은 그 certificate 부분에서 partial이다.

기존 local<2e-4/public width<2e-3, [160,161] FAIL=2.1245050576368385e-4, tick160 및 physical HOLD를 유지한다. 이 신규 연구 폴더 외 production source/CODEX_SYNC/runtime_returns/fixtures는 수정하지 않았다. R1 backup metadata와 원격 byte restore는 별개다.
