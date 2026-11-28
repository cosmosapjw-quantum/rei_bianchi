# 다음 단일 의존성: C2D_LARGE_R_SCALED_NUMERICAL_AUDIT

C2c STOP은 SCOPED_SMALL_R_SCALED_SEQUENCE_CONVERGED다. 세 새 작은-R quartet, x=.125 구면 앵커, 여섯 fixed-m 연결, 네 parity 모두 통과했다. 최소 x=.03125의 S=.34943305290567644는 극한계수4√2/15보다7.34257% 낮다. 수치적 기저 차이는 최대2.65547e−9로 작지만 remainder 상수·유효 반경은 여전히 알려지지 않았다. 성공은 유한 수열의 경험적 판정이며 full C2=false, PROMOTE=HOLD, Eq55=NOT_RUN, full-certificate fail-closed를 유지한다.

새 선택 상태28개, 두 batch40 tasks, wall320.102636386s, max workerRSS548.34765625MiB. 과학 task failure/fallback0. C2a x=.25는 기존 두 차수 evidence를 재사용했다. 재사용을 새 세 차수 검증으로 쓰지 않는다. 코드 실행 당시 identity는 provenance/MAIN_CODE_SNAPSHOT.zip 및 FOLLOWUP_CODE_SNAPSHOT.zip, final scalar 판정은 evidence/FINAL_AUDIT.json, 독립 검토는 review/에 있다. 다음 세션은 필요한 DATA/STATE와 입력만 size/SHA로 확인하고 완료 suite를 반복하지 않는다. 외부 업로드 ACK+size는 restore검증이 아니다.

다음 연구는 큰 x의 iL_O/(ℏx)→32√2/243 및 −iL_B x²/ℏ→128√2/729를 분리해 조사한다. A2 derivation과 C2a/C2b의 x4,8,16 상태·적분을 pin해 재사용한다. 새 x 후보와 물리 box/꼬리 보존, 독립 basis/앵커, 실제 overlap 단계, h/p/q/tail/raw+scaled 오차, cancellation, state/적분/task/wall 예산과 제한된 fallback을 먼저 새 계약으로 확정한다. 한 coupling의 성공을 다른 coupling에 전용하지 않는다. 새 large-R 계산은 이번에0회이며 이 handoff 자체는 실행 manifest가 아니다.

Fortran real64/OpenMP/SIMD, explicit OpenMPI, strict flags/no-fast-math, actual topology/memory preflight를 계속 사용한다. direct_stream은32patch, force/overlap은 C2b geometry를 유지한다. NCP64 actualscaling은NOT_RUN이다. local bind-to none은 sandbox 예외이며 NCP default core를 유지한다. 현재 opt-in clean-file-half-v1은 clean cache 절반을 회수가능량으로 추정하며 보장은 아니다. default raw-headroom을 바꾸지 않았다. same-command preflight 통과 없이 MPI를 launch하지 않는다. worker와 whole-batch timeout은 own-token/namespace/starttime/pidfd/PDEATHSIG 경로로 정리한다.

큰-R 이후에도 전체 충돌 관련 R/adaptive grid, hidden crossing/isolation, H1s+He n2 rank-five cluster 및 continuum enclosure가 남는다. D1·단면적·Eq55로 넘어가지 않는다.
