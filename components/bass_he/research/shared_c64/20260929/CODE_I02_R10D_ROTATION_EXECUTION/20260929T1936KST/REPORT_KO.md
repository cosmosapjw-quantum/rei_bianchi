# R10D rotation trajectory/cutoff separation: 수치 gate 미해결

**판정: `R10D_ROTATION_NUMERICS_UNRESOLVED`.** R10C exact Delta table은 SHA256 `21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49`로 확인했고 fixed GK15 105 rho는 모두 양수다. 새 contour/Stückelberg solve는 **0건**이다. Rotation 수렴 gate가 실패했으므로 다섯 lane 적분, 2x2 효과 분해, Appendix-A 재현 비교를 수행하지 않았다.

PR15 HEAD/tree는 `b8b2fe47a367459f6faf6796eb2f251feacbbd7c` / `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`; PR17 실행 basis HEAD/tree는 `d08dd207d5c91d60db4eb1767c73109ee3470f39` / `cd5875bb36b4e1fd4810209943234d56f67d4283`이다. R10C source SHA256 `496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba`와 R10B query SHA256 `97ee706c2765cac40cb001592fe5c543053ed5457b3ee4776e282a742238f215`를 계승한다. R10A 탐색값은 격리 상태로 유지한다.

Source discrepancy는 CPC/clean-room straight line 대 분산 저자 WRN Coulomb trajectory, 그리고 `R_CPC=((l+1/2)^2-1/2)/(Z1+Z2)` 대 `R_author=(l+1/2)^2/(Z1+Z2)`이다. 독립 Eq.(47) 유도와 amu 단위 변환은 `DERIVATION_KO.md`에 있다. 저자 FORTRAN은 복사하거나 실행하지 않았다.

새 연구 adapter의 TDD는 구현 전 6 fail(exit 1), 중간 원인 수정 후 1 fail(exit 1), 최종 focused 8 pass(exit 0)였다. 기존 affected rotation tests를 합친 21 tests도 pass(exit 0)했고 compileall도 통과했다. `a=0` 및 수치적으로 작은 `a`에서 기존 straight-line 확률에 접근하고, `Rmin>=Rcut`에서 identity이며, rho=0을 거부한다. CPC cutoff를 명시해 기존 straight-line 구현을 복원한다.

105개 고정 node 전체, E=0.5/5 keV/u, `(N,l)=(2,1),(3,1),(3,2)`, CPC/author cutoff의 12 조합에 대해 사전 고정 `64/128/256` step을 검사했다. 사전 한도는 max `|P_abs(128)-P_abs(256)|<=1e-7`; 실제 최대는 **`4.6718423847291746e-6`**, 저에너지 `(3,2)` author cutoff였다. 12 조합 중 3개가 한도를 넘었다. `(3,2)` CPC 저에너지 `2.3108988950748532e-6`, `(2,1)` author 저에너지 `3.5548810706220735e-7`도 실패했다. 최대 유니터리 결함 `1.1679546219191548e-13` 및 collapse 확률 열합 결함 `8.770761894538737e-14`는 각각 `5e-13` 한도 이내였다. 수치 수렴만 미해결이다.

Handoff의 정지 조건을 적용했다. Step 수나 허용오차를 사후 변경하거나 다른 궤적으로 lane을 우회하지 않았다. R10C의 `I2_MEASURABLE_CASE_B`는 기존 범위 한정 결과로 남고, R10D의 cutoff/trajectory 효과 및 author residual 설명 여부는 **미판정**이다.

Production source/default, factor-two policy, hidden-crossing Delta, CODE-I02, 56-action replay, worker sweep, author FORTRAN, bent-trajectory Delta, L2/Krawczyk는 실행·변경하지 않았다. `CODE_I02_CLOSED=true`; `full_certificate_fail_closed=true`; `scientific_PROMOTE=HOLD`; `Eq55_next_node_authorized=false`; `Eq55=NOT_RUN`.
