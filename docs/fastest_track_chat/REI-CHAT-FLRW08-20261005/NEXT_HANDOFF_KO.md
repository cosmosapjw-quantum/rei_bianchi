# FLRW08: next actual accepted-slab continuous defect

대상 cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, PR83. 시작/단계경계/게시전후 live ref와 관련 diff만 읽는다. 마지막 inspected external e63ca0735a3e3e7eebbf4498c697d806d375e191은 F08 discrete histories15개 완료, F09blocked, continuum time certificate NOT_ESTABLISHED다.

완료된 FLRW07 finite-beam source13개와6개추가 common-grid refinement, 계승 DOP853/Radau를 매번 재실행하지 않는다. 각 .5K/차분1e-4K finite목표는level6에서 충족했고 엄밀certificate는 아니다. Scalar Richardson을 photon/species state에 적용하지 않는다. Escape relative2e-11 진단FAIL은 보존한다. 작은 absolute값이라는 이유로 FAIL을 PASS로 바꾸지 않는다.

Logical node는 계속 REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL이며 실제 continuous-defect 부분은 partial이다. 다음 최소산출물은 실제 F08 fixed spectral/angular generator f_h와 첫 accepted slab의 연속재구성 residual이다. endpoint/transport/source/root identity를 exact commit/path/blob에 묶는다. 시간h->0와 spectral-grid->0는 서로 다른 극한이다. 기존 paired campaign을 다시 돌리거나 F09 provider를 임의 생성하지 않는다.

정확 paired identity는 delta'=AB delta+(AB-AF)eF-(rB-rF)다. 두 해를 공통 scale로 무차원화하고 전체 tube의 logarithmic norm, Jacobian 차이, residual 차이와 한쪽 error bound가 필요하다. Root endpoint box를 시간구간 전체의 residual bound로 부르지 않는다. T/lnT에는 (gB-gF)eF 항도 추가되므로 common grid라는 이유만으로 버리지 않는다.

Source pulse 및 threshold를 공통 구간에서 나누고 numerical jump defect를 기록한다. 정답 궤적이나 reference source를 소비자 입력으로 강제하지 않는다. 첫 slab이 없으면 필요한 필드/정확 source identity를 명시하고 제한된 추출만 요청한다. 전체 재감사로 되돌아가지 않는다. 최신 F08 conservative solver와 본 과거 primary_stage_step 진단은 구별한다.

읽기 순서는 TASK_RETURN/contract -> full REPORT §§6–7 -> F08_SELECTED_RETURN -> actual source 및 accepted slab이다. 원 production source/CODEX_SYNC/runtime_returns/source locks/F00/F03/FT03/S0를 변경하지 않는다. 같은 branch append-only non-force 및 기존 Drive/Dropbox create-only backup. R1 metadata, byte identity, science validation은 별개다. local<2e-4,width<2e-3,[160,161] FAIL/tick160/physical HOLD를 유지한다.
