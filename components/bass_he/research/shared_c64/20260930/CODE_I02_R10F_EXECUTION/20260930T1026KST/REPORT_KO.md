# R10F rotation-boundary-aware fixed GK: 경계 분할만으로 미해결

**최종 판정: `R10F_BOUNDARY_SPLIT_GK_UNRESOLVED`.** R10F의 정확한 18 cutpoint·17구간을 사용하여 255개 내부 GK15 rho node와 1035개 active branch/rho pair의 exact Delta table을 완성했지만, 고정 GK15/GK7의 90성분 중 27성분이 embedded error gate를 통과하지 못했다. 따라서 five-lane 적분값, baseline over-split regression, 2×2 효과 분해, Appendix-A RMS 및 author residual 설명은 채택·판정하지 않는다.

## Fresh identity와 계약 결함 처리

PR15 HEAD/tree는 `b8b2fe47a367459f6faf6796eb2f251feacbbd7c` / `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`이다. 요청한 PR17 publication `b015647acf1a2bf719327409ce0adf2005d6cba9`의 네 blob이 모두 예상값과 일치했다. 그중 handoff는 byte offset 3449 이후 UTF-8이 유효하지 않고, handoff/DECISION의 `1.916666666666667`은 BOUNDARY_ANALYSIS/CUTPOINT_IDENTITY의 `1.9166666666666667`과 1 ULP 다르다. 사용자 확인을 받아 원본 네 blob을 보존하고 UTF-8 보완 계약을 PR17 `f33be349fc087e994a6a7dfe7d343c97d621d9a0`에 append-only 게시했다. Query에는 CUTPOINT_IDENTITY의 **`0x1.eaaaaaaaaaaabp+0`**을 사용했다.

R10C table SHA256은 `21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49`, R10D Coulomb adapter Git blob은 `543ff5e5c20ff2969547f03410cd30353998348c`다. R10D의 64/128/256 실패, R10E의 extended rotation PASS 및 옛 7구간 GK 실패는 각각 historical verdict로 유지한다.

## Exact Delta table

새 solve 전에 18 cutpoint hex·SHA256, 255 node hex, ordered 1035 pair SHA256을 `CUTPOINT_QUERY_PRECOMMITTED.json`에 기록했다. 사전 결정 count는 90개 R10C exact pair 재사용, 최대 945개 신규 pair였다. R10A 복구 archive SHA256과 다섯 endpoint cache key/payload hash, source revision, Python/NumPy 환경 및 depth=96·panels=32를 검증했다.

3건의 측정 pilot은 총 4.06초, 새 geometry 평균 1.333초였다. 완성된 table은 R10C exact reuse **90**, pilot 신규 결과의 local cache reuse **3**, 연속 실행 신규 solve **942**, 전체 신규 solve **945**건이다. 연속 실행은 1239.1초였다. 1035개 행과 945개 신규 cache key/payload를 다시 열어 모두 검증했다. 최대 spectral residual `1.9994590576209168e-11`, 최소 normalized sheet gap `0.08111867363754102`, contour/certificate 실패 0건, panel64 호출 0건이다. 이 진단값은 별도 물리 인증으로 승격하지 않는다.

## 고정 GK15/GK7

완전한 table과 cache 감사 PASS 후에만 같은 255 node에서 다섯 lane integrand를 계산했다. Lanes 1–4는 factor-two exact Delta(rho), `COUL_AUTHOR_FROZEN`만 구현 재현 진단용 factor-two Delta(0)이다. Straight rotation=64 step, Coulomb=1024 step, Nmax=3, E=0.5/5 keV/u, 기존 다섯 hidden-crossing branch 및 upper-shell sink를 유지했다.

GK15/GK7, `rtol=2e-4`, `atol=1e-10`, evaluations=255, refinements=0이었다. 실패 성분은 총 **27/90**, 최대 정규화 오차는 `192.33551438635763`이다. 최악은 `COUL_AUTHOR`, 0.5 keV/u, energy 내 0-based 성분 4, 전체 0-based 성분 58, 첫 구간 `[0, 0.5111982111775345]`이다. 첫 구간 밖의 interval별 error/tolerance 최대는 약 `5.11e-6`으로, 실패는 첫 구간에 집중된다. `SL_CPC`와 `SL_AUTHORCUT`은 두 에너지 모두 0성분 실패다. `COUL_CPC`, `COUL_AUTHOR`, `COUL_AUTHOR_FROZEN`은 각각 9성분 실패다. 이는 boundary union split이 기존 실패를 줄였지만 전체 90성분 gate에는 **불충분**하다는 bounded 판정이다. Coulomb 저-rho 수치 거동의 원인을 추가로 단정하지 않는다.

첫 lane 시도는 R10E helper의 360-pair 고정 길이에 막혀 GK 평가 전에 종료됐다. R10F 전용 1035-pair identity helper를 RED 1건→GREEN 1건으로 수정하고 동일한 255 node를 다시 평가했다. 신규 Delta solve는 발생하지 않았다. 최종 affected focused tests **34 PASS**. Production source/default/tolerance와 회전 step 수는 변경하지 않았다.

계약에 따라 새로운 split/refinement/tolerance 완화, baseline 회귀 판정, 2×2 분해, Appendix-A 비교, panel64, full repository pytest, CODE-I02, Eq55, 56-action replay, worker sweep, author FORTRAN, L2/Krawczyk는 실행하지 않았다. `CODE_I02_CLOSED=true`, `full_certificate_fail_closed=true`, `scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`을 유지한다.
