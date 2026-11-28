# R10F UTF-8 계약 보완 기록

원 publication `b015647acf1a2bf719327409ce0adf2005d6cba9`의 네 파일은 요청된 Git blob과 일치한다. 다만 `R10F_HANDOFF_KO.md`는 `No new contour solve outside the precommit` 뒤 byte offset 3449부터 올바른 UTF-8이 아니다. 원본 blob `210475e2511c69703737b0a1131787aee07d768c`는 historical evidence로 보존한다. 이 문서는 손상된 suffix의 실행 계약을 읽을 수 있게 보완하며 원본의 앞부분과 사용자의 R10F 지시를 바꾸지 않는다.

## Exact cutpoint 신원

Handoff의 명시적 지시인 “Use exactly the union in `BOUNDARY_ANALYSIS.json`”과 `CUTPOINT_IDENTITY.json`의 18개 hex가 권위다. `DECISION.json` 및 handoff 본문에 쓰인 `1.916666666666667`은 해당 목록의 `1.9166666666666667`과 1 ULP 다르다. Query 생성에는 **`0x1.eaaaaaaaaaaabp+0`**을 사용한다. `0x1.eaaaaaaaaaaacp+0`을 alias로 취급하지 않는다. 사용자가 이 hex 기준을 확인했다. 다른 cutpoint를 합치거나 반올림하지 않는다.

## 실행 순서와 게이트

1. 새 Delta solve 전에 18개 cutpoint의 hex 목록과 SHA256, 17구간의 255개 양의 내부 GK15 rho node, 1035개 active branch/rho pair, R10C exact pair와 일치하는 90개, 최대 945개 신규 pair를 기록한다. Source/environment, endpoint/certificate, depth=96, panels=32 및 exact branch+rho identity를 검증한다. 각 새 결과와 실패 기록을 즉시 내구적으로 저장한다.
2. 완전한 exact table이 있을 때에만 공통 255 node에서 `SL_CPC`, `SL_AUTHORCUT`, `COUL_CPC`, `COUL_AUTHOR`, `COUL_AUTHOR_FROZEN` integrand를 계산한다. 앞 네 lane은 factor-two Delta(rho), 마지막은 구현 재현 진단용 factor-two Delta(0)이다. Straight=64 step, Coulomb=1024 step, Nmax=3, E=0.5/5 keV/u, 기존 다섯 branch와 upper-shell sink를 유지한다.
3. 17개 사전 split에서만 GK15/GK7을 적용한다. `rtol=2e-4`, `atol=1e-10`, evaluations=255, refinements=0을 고정한다. 90개 모든 성분의 embedded estimate가 tolerance 이내이면 `R10F_ROTATION_BOUNDARY_SPLIT_FIXED_GK_PASS_NOT_GLOBAL_CONTINUUM_BOUND`, 하나라도 실패하면 `R10F_BOUNDARY_SPLIT_GK_UNRESOLVED`이다. 실패 시 최악 lane/energy/component/interval을 보고하고, 같은 실행에서 split·refinement·tolerance·rotation steps를 바꾸지 않는다.
4. GK PASS 후 R10C의 같은 물리적 `SL_CPC` baseline을 R10F `SL_CPC`와 indexed component·shell별로 비교한다. 절대/상대 차이와 양쪽 embedded estimate를 기록한다. 예상 밖의 큰 불일치는 `R10F_BASELINE_REGRESSION_UNRESOLVED`로 중단하고 query/table 신원을 먼저 점검한다.
5. GK와 baseline 점검 후에만 R10D의 cutoff effect, trajectory effect, interaction, frozen Delta addition effect와 기존 materiality rule을 적용한다. Appendix-A 비교의 분류는 항상 `AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`이다. 모든 90개 성분이 통과하면 breakpoint split 원인 가설을 이 범위에서 확인하고, 실패하면 split이 불충분하다고 분류한다.

새 runner/helper는 구현 전 RED 테스트, exact cutpoint·255/1035/90 counts, no-refinement, SL_CPC baseline regression 및 `git diff --check`를 요구한다. Production source/default/tolerance, Magnus steps, factor-two policy, CODE-I02, 56-action replay, worker sweep, author FORTRAN, L2/Krawczyk, 새 물리 channel, merge/force-push는 범위 밖이다. `scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`을 유지한다.
