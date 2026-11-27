# R10E rotation numerical closure: 회전 PASS, fixed GK 미해결

## 신원과 판정

PR15 HEAD/tree는 `b8b2fe47a367459f6faf6796eb2f251feacbbd7c` / `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`이다. PR17 실행 basis HEAD/tree는 `4b38c2288e97952940498c1fc443944258667bc8` / `c458ca2937191529784c4f353b6476317a5b9429`이다. R10C table SHA256은 `21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49`, R10D Coulomb adapter Git blob은 `543ff5e5c20ff2969547f03410cd30353998348c`로 확인했다. R10D의 64/128/256 실패 판정은 수정하지 않았다.

**최종 상태: `R10E_FIXED_GK_QUADRATURE_UNRESOLVED`.** 새 R10E 회전 수치 계약은 `R10E_ROTATION_NUMERICS_PASS_EXTENDED_CONTRACT`로 통과했지만, 다섯 lane의 기존 fixed GK15/GK7 105 node 적분은 오차 게이트를 통과하지 못했다. 따라서 five-lane 적분값, 2×2 효과 분해, Appendix-A RMS, 저자 잔차 설명 여부는 채택하거나 판정하지 않는다.

## 회전 수치 게이트

실행 전에 `GATE_PRECOMMITTED.json`에 105개 rho hex, 12조합, steps 256/512/1024, 확률 한도 `1e-7`, 유니터리성/열합 한도 `5e-13`, 기존 실패 세 조합의 관측 차수 하한 3.5, DOP853 `rtol=1e-12`, `atol=1e-14`, 비교 한도 `1e-8`을 기록했다. 모든 12조합에서 동일한 R10D adapter를 새로 실행하고 각 조합의 최대 512→1024 차이 node를 사후 선택하여 독립 DOP853로 검증했다. 최대 512→1024 차이는 `2.5050147844929427e-8`, 최대 Magnus1024/DOP853 차이는 `1.7024043286184565e-9`, 최대 유니터리성 결함은 `3.8791192542343904e-13`, 최대 열합 결함은 `3.452793606584237e-13`이다. 기존 실패 세 조합의 같은 node에서 계산한 관측 차수는 각각 `3.98897`, `3.91230`, `3.89647`이다. DOP853는 auditor로만 사용했다.

## Fixed GK 게이트

회전 PASS 이후에만 R10C exact table과 rho=0 frozen Delta 기록을 읽어 다섯 lane의 105개 고정 node integrand를 계산했다. Hidden crossing의 branch support, factor-two 정책, Nmax=3, E=0.5/5 keV/u 및 upper-shell sink 처리는 기존 그대로다. Straight rotation은 64 step, Coulomb rotation은 1024 step이다. `SL_CPC`의 rotation matrix는 기존 `full_rotation_batch(..., steps=64)`와 정확히 일치함을 확인했다. 새 Delta/contour solve는 0회다.

기존 GK15/GK7, `rtol=2e-4`, `atol=1e-10`, 기존 support split, 최대 7 interval을 그대로 적용했다. 평가 node 105, refinement 0이었다. 90개 성분 중 49개에서 embedded estimate가 허용치를 넘었고 최대 정규화 오차는 `250.11715964925966`이다. `SL_CPC`는 두 에너지 모두 0개 실패였으나, `SL_AUTHORCUT`, `COUL_CPC`, `COUL_AUTHOR`, `COUL_AUTHOR_FROZEN`은 각각 13, 11, 13, 12개 성분 실패였다. 이는 새 회전/컷오프 lane에서 기존 support split의 GK 추정이 충분하지 않음을 보여 주는 **수치 관측**이다. 특정 불연속 원인은 이 노드에서 인증하지 않았다. 다른 split, 추가 refinement, 허용오차 변경으로 우회하지 않았다.

Focused tests는 새 R10E 4개, 기존 R10D/rotation 21개, 총 **25 PASS**다. Production source/default/tolerance는 변경하지 않았고, full repository pytest는 영향받는 production source가 없으며 GK stop이 발생하여 실행하지 않았다. Author FORTRAN, Eq55, CODE-I02, 56-action replay, worker sweep, L2/Krawczyk는 실행하지 않았다.

Frozen gates: `CODE_I02_CLOSED=true`; `full_certificate_fail_closed=true`; `scientific_PROMOTE=HOLD`; `Eq55_next_node_authorized=false`; `Eq55=NOT_RUN`.
