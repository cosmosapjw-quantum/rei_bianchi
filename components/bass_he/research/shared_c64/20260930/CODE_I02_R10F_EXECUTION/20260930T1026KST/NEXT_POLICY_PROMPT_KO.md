# R10F 이후 제한된 정책 프롬프트

R10F exact table은 18 cutpoint·17 interval·255 rho node·1035 active pair를 완성했고, 90 R10C exact reuse와 945 신규 Delta solve의 content identity를 검증했다. R10D의 원래 rotation failure 및 R10E의 옛 7구간 GK failure는 유지한다. 새 boundary union split에서는 `SL_CPC`와 `SL_AUTHORCUT`이 모든 성분을 통과했지만, 세 Coulomb lane이 첫 구간 `[0, 0.5111982111775345]` 중심으로 총 27/90 성분 실패했다. 현재 verdict는 `R10F_BOUNDARY_SPLIT_GK_UNRESOLVED`; baseline, 2×2 효과, Appendix-A, author residual 설명은 미판정이다.

별도 후속 노드는 첫 구간의 Coulomb integrand regularity와 fixed-GK embedded estimator 실패 원인을 분석하는 **새 연구 설계**여야 한다. 새 split/refinement·tolerance·rotation steps 또는 Delta panel64은 R10F 실행에 소급 적용하지 않는다. 후속 query가 새 rho를 요구하면 exact Delta 비용과 source identity를 먼저 제안한다. Production source/default, Eq55, CODE-I02, author FORTRAN, L2/Krawczyk는 범위 밖이다. `scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`을 유지한다.
