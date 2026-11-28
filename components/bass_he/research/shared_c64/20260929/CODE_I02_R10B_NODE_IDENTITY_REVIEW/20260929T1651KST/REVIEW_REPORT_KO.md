# R10B Q23 node-identity repair: 독립 범위 한정 검토

## 판정

`NODE_IDENTITY_REPAIR_REVIEW=PASS_BOUNDED_RESEARCH_VIEW`. 이는 Q23 입력 node의 provenance에 따른 fit view 수리 판정이다. R10A의 `SURROGATE_REBUILD_UNRESOLVED`는 유지하며 기존 세 lane 적분값과 3.333/1.880 비율, Appendix A 비교는 탐색값으로 격리한다. 과학적 승격과 R10C 신규 reference 계산은 승인되지 않았다.

## 신원과 완전한 package

- PR17 고정 publication HEAD/tree: `9a75378a903f154d1372a70236f78296abf21daa` / `bc21cf63da65b8219e0a79a4a26878ec4b9aa3e3`. Handoff blob `d92679a4f4a600f4027e3533e81f1c41afd010f1` 확인.
- PR15 HEAD/tree: `b8b2fe47a367459f6faf6796eb2f251feacbbd7c` / `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`.
- `BACKUP_RECEIPT.json`의 Drive object `1Dmv3uxhuezFya3Xb_DIJIZkaIvU-2b8H`에서 R10B ZIP 전체를 회수. 실제 76,410 bytes, SHA256 `aa2a5a62841e3e28a14cb731f26ff4aa6ecb25a704a7327178d3f2c1af20bf2e`. ZIP CRC 통과, 31개 member는 MANIFEST 1개와 명시된 payload 30개에 정확히 일치. 모든 payload 크기와 SHA256가 일치한다. 세부 목록은 `PACKAGE_VERIFICATION.json`에 있다.
- GitHub R10B 문서 subset을 전체 실행 package로 간주하지 않았다. 복원된 다섯 R10A fixtures는 R10A Git `attempt2/` 파일과 각각 바이트 동일하다. R10A runner와 geometry source snapshot도 기준 commit `5954d5d31d1c4536b41e13b4868aa5fa97cd2924`의 Git bytes와 각각 동일하다.

## 독립 검증

새 격리 venv: CPython 3.12.3, NumPy 2.3.5, pytest 8.4.2. 제공 `tests/test_node_view.py`에 대해 `PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 .../python -m pytest -q -p no:cacheprovider tests/test_node_view.py`를 실행하여 exit 0, **12 passed in 0.21s**를 얻었다. CODE-I02나 repository full suite는 반복하지 않았다.

복원 package를 scratch에 복사한 뒤 `OPENBLAS_NUM_THREADS=1 .../python replay_analysis.py`를 실행해 exit 0을 얻었다. 이 스크립트는 blob 검증된 `DeltaSurrogate`, validation, GK node generator의 AST 정의만 사용한다. 생성된 JSON 일곱 개 중 여섯 개는 archive evidence와 구조적으로 동일하고 `FORENSIC_RESULT.json`은 Python 버전 문자열(archive 3.13.5, reviewer 3.12.3)만 달랐다.

R10A runner `scripts/r10a_rho_freeze.py:136-150`은 초기 anchor를 `adaptive_seed_rhos([0,Rb], rule='gk7')`로 만든 뒤, 실패할 때 `mid=Rb/math.sqrt(2)`를 추가한다. pinned `geometry.py:254-258,284-293`는 GK7의 u 중앙점에서 `sqrt(u)`를 취한다. Q23에서 초기 parent는 `0x1.a0e8bdf74847dp+2`, 추가 split은 `0x1.a0e8bdf74847cp+2`이다. 1 rho ULP 차이지만 둘 다 의도된 `u/Rb²=1/2`를 나타낸다. 이 선택은 생성 단계와 역할에 근거한다. reference 오차가 작은 record 선택, 거리 기반 병합, cache key 반올림을 사용하지 않았다.

`node_view.py:13-56`은 canonical parsed manifest SHA256 `3279b84a3fa1698b076a270ecf8543fa411c71acc769d0319d968e396e8cd8d3`에 pin되고, 정확히 24개 Q23 row 및 각 hex 하나를 요구한다. 원본을 deep copy하고 split row 하나만 새 Q23 fit view에서 제외하며 receipt에 그 record를 보존한다. Q23 24→23, 다른 branch 동일, 원본 raw record 동일. 기존 cubic method와 2e-4 gate를 유지한다.

Archive witness 64-panel 상대오차는 raw `1.4166045154428908e-3`에서 view `3.746852183319305e-8`로 바뀌었다. 해당 stencil rank 3→4, condition number `5.917069719313704e15`→`139.679889423492`. 저장 fixed holdout 30개 통과, 저장 nontraining reference 50개 위반 0건, 재구성 GK15 105 좌표/360 active pair의 rank 결함 1→0을 재현했다. 새 Delta 평가 0, transport 적분 0. 저장 reference 검사는 posthoc이며 모든 소비 pair의 reference 정확도를 입증하지 않는다. S23 저장 최대 상대오차 `1.9715317060022399e-4`는 `2e-4` gate에 가깝다.

## 남은 경계

`PROPOSED_QUERY_CONTRACT.json`은 105 좌표/360 active pair의 별도 R10C 계약이며 `PROPOSED_SEPARATE_APPROVAL_REQUIRED_NOT_EXECUTED`다. 이번 검토에서는 queue를 시작하지 않았고 저장 reference 재사용 0, 새 reference 계산 0이다. 새로운 refinement, 다른 interpolant, author FORTRAN, Eq55, Eq50/54 변경, 56-action replay, worker sweep, R1/R2, L2/Krawczyk를 실행하지 않았다.

Gate ledger: `CODE_I02_CLOSED=true`; `full_certificate_fail_closed=true`; `scientific_PROMOTE=HOLD`; `Eq55_next_node_authorized=false`; `Eq55=NOT_RUN`.
