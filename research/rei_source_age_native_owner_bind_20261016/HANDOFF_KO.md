# 재개 handoff

기준 Git branch `research/rei-source-age-native-owner-bind-20261016`, PR #164 위 stacked Draft PR. 연구 상태는 `README_KO.md`, 원본 blob은 `SOURCE_IDENTITY.json`, 독립 리뷰와 수리 판정은 `INDEPENDENT_REVIEW.json`, 첫 실패 원자료는 `evidence/`를 읽는다. 원본 PR #150 HEAD는 실행시 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`; 마지막 조회 `90f1d25b7b7700b1bd158320e2d309e9f50705f5`의 관련 일곱 blob은 같았다. 원래 PR #160 native 기준 `a42fd7c9849306074a9f7a262628cd852ce34dea`.

현재 Ubuntu 소유자 checkout은 dirty일 수 있으므로 변경하지 않는다. 재현은 isolated worktree 또는 복원 ZIP 안에서 아래처럼 한다.

```bash
mkdir -p /tmp/rei_source_age_fresh
python3 research/rei_source_age_native_owner_bind_20261016/prepare_native.py . /tmp/rei_source_age_fresh/native
NATIVE_ROOT=/tmp/rei_source_age_fresh/native bash research/rei_source_age_native_owner_bind_20261016/run_local.sh /tmp/rei_source_age_replay
python3 research/rei_source_age_native_owner_bind_20261016/analyze_refinement.py /tmp/rei_source_age_replay/history.csv /tmp/rei_source_age_refinement.json
```

`run_local.sh`는 scratch native crate의 examples와 read-only node accessor suffix를 설치한다. 실행 결과를 PR #150 production source에 덮어쓰지 않는다. 원래 source 접두 SHA-256은 `9d2d97881ca7b9b58d68dbeffad937e16ca8af237b3d9ba01de0fb5e00b67aa7`, patch는 `prepared_node_accessor.patch`. `source_matched_solver.py`는 현재 예상대로 exit 1과 native domain guard를 반환한다. 다음 노드는 `SOURCE_AGE_POSITIVE_REFERENCE_AND_AGE_QUADRATURE_DIAGNOSIS`이며 `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.
