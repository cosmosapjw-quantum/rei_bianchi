# R10G endpoint-resolution bounded execution

원 입력 ZIP `BASS_HE_R10G_ENDPOINT_20260930_v1_REATTACHED.zip`의 SHA256은 `90e5b3a0dbecd9fef6ef82f8cbe30f5440cd77796de615e66e66ce6fea40d6ee`이다. 34 members의 CRC와 MANIFEST 33 payload의 크기·SHA256이 모두 일치했다. 원 ZIP은 Dropbox object `id:BSpOijBcT10AAAAAADwTag`에서 회수했다. GitHub의 다른 R10G 패킷으로 대체하지 않았다.

원 source는 PR17 R10F basis `5efe052460e85f7e9785b9391d188ba394efee73`이며, 실제 실행은 동일 dependency digest `496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba`를 가진 새 detached checkout에서 했다. 환경은 Python 3.12.3, NumPy 2.3.5, SciPy 1.17.0이다. R10F archive SHA256 `082fd7ec94e2873ee218043828179e3c4db8d9f0d4ce28f9fa29f8c807207578`를 manifest 검증 후 입력으로 사용했다.

## Fresh gates and result

- Focused tests: `16 passed`, exit 0.
- Archived first-panel high/error difference: `1.4432899320127035e-15` / `1.0763959168436088e-15`; old-domain representation overlap maximum `2.295188983314489e-09`. Frozen diagnostic 3 leaves / 60 queries PASS. 새 Delta 0회인 audit이다.
- Dry-run input inventory: `PREPARED_NOT_EXECUTED`, exit 0. Source/environment gate를 별도로 확인한 후 `execute_endpoint.py --execute` exit 0.
- 새 첫 구간: q=`asinh(rho/a_ref)`, 3 leaves, 60 rho evaluations, 새 Delta 300 calls. 각 branch 60건. 기존 R10F exact-node table 재사용 hit 0건; 기존 다른 16구간 high/error는 원문 그대로 재사용했다. 최대 8 leaves / 210 rho / 1050 Delta 범위 이내이다.
- Rotation batch 2개 PASS. 24개 selected DOP853 audit 기록. 최대 eta128/256 확률 차 `6.708222033413591e-09`, 최대 eta256/DOP853 차 `4.476329862335149e-10`.
- 90/90 component embedded gate PASS. 두 complete grid 모두 PASS; 최종 최대 normalized embedded error `0.005278656247380242`, grid high 변화 `3.2392387231292003e-06` tolerance 단위로 0.25 기준 통과.
- 저장된 300 cache key/record hash, Delta finite/nonnegative, exact rho hex, source/endpoint/depth/panels identity를 read-only 재검증했다. `INTERVALS.json`의 새 세 구간 high/error와 원 16구간 high/error를 재합산하면 저장된 90성분 high/error와 차이가 정확히 0이다. 원 16구간 high/error의 canonical JSON SHA256은 `6232572ead0ec9d1443ac58a5c9eca17aa34c428002a862994091c233975b418`이다.

R10F의 historical `R10F_BOUNDARY_SPLIT_GK_UNRESOLVED`는 수정하거나 소급 PASS로 바꾸지 않았다. 새 판정은 `R10G_LOCAL_ENDPOINT_NUMERICAL_PASS_NOT_GLOBAL_OR_PHYSICAL_CERTIFICATE`이다. Embedded GK와 successive-grid 결과는 전체 continuum interval bound나 물리 검증이 아니다.

## Post-gate comparisons

R10F 사전 baseline consistency 규칙으로 R10C F2-RHO와 새 SL_CPC를 비교했다. 24 indexed/shell rows에서 flagged 0, 최대 절대 차 `1.9362195180505637e-09`, 최대 비영 reference 상대 차 `1.0559230016325783e-08`로 PASS했다. 이는 일관성 heuristic이다.

다섯 lane의 finite indexed-state 결과와 cutoff/trajectory/interaction/frozen-rho 차이는 `FIVE_LANE_RESULT.json`, `EFFECT_DECOMPOSITION.json`에 있다. Appendix-A 비교는 `AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`이다. `COUL_AUTHOR`의 all-six RMS `2.0125238508601755`, dominant n2/n3 RMS `1.288856784431187`; SL_CPC의 대응값 `1.9757710695915256`, `1.412799752438273`이다. 두 지표 모두 5% 개선하는 사전 기준은 거짓이다. 이 결과에서 특정 원인의 물리적 판정을 선언하지 않는다.

## Scope and frozen gates

Production source/default/tolerance, Eq55 production, CODE-I02, 56-action replay, worker sweep, 다른 16구간의 재적분, author FORTRAN, L2/Krawczyk는 실행하거나 변경하지 않았다. 기존 R10F 실패 기록과 원 archive/cache는 보존했다.

`CODE_I02_CLOSED=true`; `full_certificate_fail_closed=true`; `scientific_PROMOTE=HOLD`; `Eq55_next_node_authorized=false`; `Eq55=NOT_RUN`.
