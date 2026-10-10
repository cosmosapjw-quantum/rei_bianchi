# REI-ACCEL02 C08A2 재개

현재 Q1A_FIXED_Q_GAUSS의 새 실행 세 개가 진행 중이다. 먼저 q1a/LIVE_STATUS.json과 q1a/RUN_SESSIONS.json을 읽고 실제 process/RESULT 존재 여부를 확인하라. **살아 있는 실행을 중복 시작하지 마라.** RUN002·EVENT003·Q0와 기존 N1/N4 검산은 반복하지 않는다.

실행은 GAUSS1_FINE(384 energy, rtol1e-11), GAUSS2_FINE(768 energy, rtol1e-11), GAUSS1_TIGHT(384 energy, rtol3e-12)다. 동일384 panels, nmu2, FLRW r0, 전체 mean-z15.9→4, 각5400s wall ceiling이다. 실제 command/identity는 각 IDENTITY.json에 있다. 현재 session/PID는 transient handle이므로 재사용 전에 process 명령을 대조하라.

C08A 구현 checkpoint는 Drive1ZPpKPK43caNvJ-T4RCQYNa_9PboJnsve 및 Dropbox id:BSpOijBcT10AAAAAAD36cg에 이중 upload ACK가 있다. 구현 GitHub commit f823b3e8b1c7819d0d3b7d70d07a128d8dc46647, PR110. 이후 checkpoint는 q1a/receipts를 읽는다. bare RESTART.npz를 resume 가능한 완전한 solver 저장본이라고 주장하지 마라. 지원 resume CLI는 아직 없다.

## 다음 한 단계

RESULT.json이 생기면 성공/실패 여부와 관계없이 package_checkpoint.py로 새 C08B_RAW_<RUN> archive를 만들고 기존 Drive/Dropbox에 업로드하라. 이미 receipt가 있다면 재업로드하지 않는다. 업로드 ACK와 bytes/hash/ID 확인 후 postprocess.py로 새 saved-run MOMENTS를 생성한다. 세 실행이 끝나면 compare.py로 G1fine/G2fine spectral과 G1fine/G1tight time을 비교하고 독립 reviewer가 actual artifacts를 검토하도록 한다. postprocess/compare는 ODE를 수행하지 않는다. 비교파일도 create-only다.

## 기존 기준과 이미 확정된 결과

q1a/CONTRACT.json과 상위 NEXT_DAG.json의 물리/허용 기준을 유지한다: time9fields2e-6, initial-energy ledger1e-9, initial-nH number ledger1e-9, geometry1e-11, spectral24fields1e-3. 65/129 epoch를 각각 자체 fine amplitude로 정상화하고 zero channel은 exact zero다. accepted finite/gas/photon positivity를 실제 run별로 확인한다. 기존128 시간 인증을 새 grid로 전이하지 않는다.

새 local preflight는 PASS이고 initial UVB number 오차는 약−2.91e-15다. 하지만 saved Q0 exact reference를 이용한 source-only N 오차는 G1.06835466003, G2.03448234347이다. 독립 triangle-inequality bound에서 공식 source-N pair error>=.03274325249>1e-3이므로 전체24-field spectral PASS는 불가능하다. 이 결과는 gas response 오차를 뜻하지 않는다. 실행은 evolvedresponse 정량 진단을 완성하기 위한 것이며 과학적 승격을 전제하지 않는다.

Q1B 설계는 q1a/NEXT_DESIGN.md와 review/Q1B_PROPOSAL_REVIEW.json에 있다. 고정 q-cell N,U 두 모멘트, exact source moments 및 threshold-split shared opacity/heat integrals의 보존식만 독립 검토됐다. 빈 cell/realizability/native ABI/Jacobian 계약은 미해결이며 아직 코드 구현이나 새 ODE 권한 판단의 대체물이 아니다. Q1A 결과를 보존한 다음 값싼 local gate부터 진행하며 무제한 point-grid 증가는 하지 않는다.

BASS N4는 옛 reduced FLRW/r=.1 cell adoption만 DONE이다. 새 native BASS receipt는 NOT_EXECUTED/HOLD다. r=.05 Bianchi pair, observational/continuum claim, CR/RCT·secondary physics는 승격하지 않는다. 최종 실제 결과/독립 결정/보고서/DAG/그림을 PR110에 additive publish하고 BASS PR140에는 producer gate 변화만 연결한다. 마지막으로 새 final checkpoint를 Drive+Dropbox에 이중백업한다.
