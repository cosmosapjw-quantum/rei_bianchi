# FLRW08 first-half defect -> half2 propagation

같은 rei_bianchi / forward/rust-reion-kernels-20260922 / PR83을 유지한다. Logical task는 계속 REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL이다. 현재 source-parent는8629a63059597d4fdd01be0f4e3c8b120a7766d0. 시작과 단계 경계 및 게시 전후 live ref를 확인하고 관련 변경만 계승한다.

이번 계산은 F08 T0_FLRW actual_records[0].audits[1], 첫 수락 macro의 첫 committedhalf0..625000000s다. 버린 fullstep과 혼동하지 않는다. 별도 native 또는 전체 campaign을 재실행하지 않았고, 두13변수 짧은 IVP는 구간상계의 독립 진단이다.

고정 에너지 격자의 generator lambda_j=HE_j/(E_j-E_(j-1)), 연속source, real analytic FT03CaseA가 target이다. Same f64 node/constant를 정확 실수로 해석한다. Literal f64 program의 dt->0나 spectral continuum 주장이 아니다. 최저 활성gap은 실제index15->16이다. Passive subfit photons를 삭제하거나 physical chi와 fit threshold를 합치지 않는다.

읽기: TASK_RETURN/계약 -> SLAB_CERTIFICATE 및 JACOBIAN_MAJORANT -> 필요한 REPORT. Picard radius.02, supF<.008853, contraction<.442865, Ttube[48426.01,51611.75]K. 64개 interval 전체의 residual과 Metzler majorant로 xHII<1.169e-7,T<.002915K의 endpoint오차를 얻었다. Decimal directed연산과 exp/ln 반올림 의미는 신뢰 기반이며 formal independent verifier는 없다.

다음 bounded 산출물은 첫 macro의 half2다. 이번 연속 endpoint오차를 초기오차로 넘기며, 새 discrete root box로 오차를0으로reset하지 않는다. Actual half2 native point/재구성/tube/residual을 연결한다. 이후 같은 시각의 BI half 데이터를 먼저 확보해 paired bound를 계산한다. FLRW 각도합 닫힘을 BI에 자동 적용하지 않는다.

Delta'=ABdelta+(AB-AF)eF-(rB-rF)의 Jacobian차 및 한쪽 절대오차항을 보존한다. 자료가 없으면 정확필드와최소추출요청을 남긴다. 전체 F08캠페인이나 완료된 F04/F05/FLRW06/07회귀를 반복하지 않는다. PriorauxiliaryescapeFAIL도 그대로 유지한다.

재현 ZIP의 research/run_checks.py --output NEW_DIRECTORY는 새 interval 계산과 저장된IVP검사를 수행한다. 선택적 --fresh-ivp에서만 두IVP를 새로실행한다. Originalproduction/runtime/source-lock/F00/F03/FT03/S0는 변경하지 않는다. Samebranch append-only non-force와 기존Drive/Dropbox create-only백업을 유지한다. strictlocal<2e-4/publicwidth<2e-3,[160,161]FAIL과tick160/physicalHOLD는 보존한다.
