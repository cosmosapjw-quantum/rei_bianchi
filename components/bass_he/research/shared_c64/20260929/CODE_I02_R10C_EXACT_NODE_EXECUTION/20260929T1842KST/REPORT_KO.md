# R10C exact consumed-node audit 및 fixed-GK replay

## 판정 범위

Phase A `COMPLETE_VALID_EXACT_NODE_TABLE`; repaired surrogate `SURROGATE_CONSUMED_QUERY_PASS`; Phase B `EXACT_NODE_FIXED_GK15_REPLAY_PASS_NOT_GLOBAL_CONTINUUM_BOUND`; R9 I2 `I2_MEASURABLE_CASE_B`이다. R10B의 bounded node repair PASS를 계승하지만 R10A `SURROGATE_REBUILD_UNRESOLVED`와 기존 3.333/1.880 탐색값의 격리를 해제하지 않는다. Appendix-A 비교는 모두 `AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`이다.

## Source와 입력 계약

PR15 HEAD/tree는 `b8b2fe47a367459f6faf6796eb2f251feacbbd7c` / `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`. PR17 실행 basis HEAD/tree는 `bfdf306b2bd8bb80ca4f802da6dd48267f01ca46` / `f65281ca0056a923fecd0b74c600deb3afb74867`이다. R10A source SHA256 `496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba`, R10B 고정 query SHA256 `97ee706c2765cac40cb001592fe5c543053ed5457b3ee4776e282a742238f215`를 실제 bytes로 확인했다. R10A 전체 archive는 640,484 bytes, SHA256 `2096b9f8347fd02f89bc689330fc76686a0c5c2553bf9232d7912f8a6f82ac75`이다. 원 endpoint 5개의 saved JSON과 content-addressed cache record가 동일하고 simple-fold 및 pair-membership `passed is True`를 확인했다. 실행 환경은 CPython 3.12.3, NumPy 2.3.5, `OPENBLAS_NUM_THREADS=1`이다.

105개 exact rho hex는 기존 support split 7구간의 GK15 node 집합과 일치한다. 360개 active branch-rho pair는 S23 30, Qother 75, Q12 60, Q23 105, Qm1 90으로 고정했다. R10B의 64-panel 후보는 32-panel key와 다르므로 재사용하지 않았다.

## Phase A와 surrogate

2건 pilot 후 같은 durable cache에서 358건을 이어 계산했다. 원 R10A 32-panel cache 재사용 0건, 새 32-panel contour call 합계 360건이다. depth=96, panels=32이며 실패 record 0건. 전체 table은 `EXACT_NODE_TABLE.json` 279,433 bytes, SHA256 `21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49`이다. 각 row의 source, 환경, branch, rho hex, depth, panels 및 cache-key SHA를 보존했다. 360개 cache key/payload hash와 개별 row 파일의 table 일치를 모두 검증했다. 누적 contour 실행 시간은 약 494.03초다.

독립 리뷰를 통과한 R10B fit view로 고정 360 pair를 비교했다. 360/360이 상대오차 `<=2e-4`, 최대 `1.9634309860325704e-4` (S23, rho `0x1.8ac82e6a990ecp-1`)이다. 여유가 작으므로 이 PASS는 고정 소비 좌표의 수치 판정이며 global interpolation bound가 아니다. 정확값과 surrogate의 `delta_p`, reversible/absorbing event block의 `2|delta_p|`, nodewise `4 sum |delta_p|`는 별도 진단으로 저장했고 GK estimator와 합치지 않았다.

## Phase B: 변경 없는 고정 GK15/GK7

R10A cache에서 exact rho=0 Delta 5개를 별도 key로 복원했다. F2-RHO, F2-FROZEN, F1-RHO만 기존 Nmax=3, 5 branches, rotation steps 32, E=0.5/5 keV/u로 계산했다. 기존 `adaptive_vector_quadrature`에 mandatory support interval 수 `max_intervals=7`을 지정하고 호출 rho 집합을 고정 105개 exact hex와 대조했다. 실제 `evaluations=105`, `refinements=0`, component 위반 0건, 최대 embedded-error/tolerance 비 `6.16100799689864e-5`다. 이는 interval-rigorous continuum bound가 아니다.

| lane | 0.5 keV/u indexed reaction loss (a0²) | 5 keV/u indexed reaction loss (a0²) |
|---|---:|---:|
| F2-RHO | 1.9552989487829353 | 60.457779293859446 |
| F2-FROZEN | 6.516438277394835 | 113.65790647525453 |
| F1-RHO | 21.003899569247487 | 148.52572784294793 |

F2-FROZEN/F2-RHO는 각각 `3.332706889374106`, `1.8799550331283588`이다. 이는 신규 exact-node 결과이고 기존 R10A 탐색 비율 `3.3329929242370526`, `1.8801201730778772`를 소급 승인하지 않는다. 1,440개 실제 확률 비율 비교에서 analytic `exp[-f(Delta0-Delta_rho)/v]`와 direct quotient의 최대 상대차는 `3.68e-15`다.

Appendix-A의 six-shell multiplicative RMS는 F2-RHO `1.975771`, F2-FROZEN `2.789565`; dominant n=2,3 RMS는 각각 `1.412800`, `1.707866`이다. 사전 고정 규칙은 indexed loss 변화가 1%를 넘고 두 lane의 합산 embedded 오차 추정치 10배보다 크면 output change를 material로, 두 RMS가 모두 5% 이상 감소할 때만 author reproduction 개선을 material로 본다. 두 에너지의 output 변화는 material이나 author reproduction RMS는 악화해 `I2_MEASURABLE_CASE_B`다. 이는 author 구현 재현 비교이며 물리적 검증이 아니다.

## 검증과 남은 경계

새 research helper의 TDD RED는 collection 성공 후 실제 6 fail, exit 1이었다. GREEN은 7 pass, exit 0이며 exact query set, one-ULP/cache identity, table completeness, fixed node/refinement, frozen support, 확률 비율을 검사한다. 새 Delta table과 개별 cache row는 atomic write 및 fsync로 저장됐다. Production source/default, 물리 tolerance, cubic method, fitting anchors를 변경하지 않았다. CODE-I02, 56-action replay, worker sweep, author FORTRAN, L2/Krawczyk, repository full pytest는 실행하지 않았다.

`CODE_I02_CLOSED=true`; `full_certificate_fail_closed=true`; `scientific_PROMOTE=HOLD`; `Eq55_next_node_authorized=false`; `Eq55=NOT_RUN`.
