# REI_DOSSIER_SSOT_20261016

2026-10-16 첫 번째 샌드박스 연구 단위. 2026-10-14 원본 Reionization_Standalone_Dossier와 사용자가 준 2026-10-16 추가 DAG 문서, `rei_bianchi` 공개 커밋/PR, 원 Grackle·Verner·Mackey·HYREC-2 문헌을 이용한 **추가/개발용 dossier v2**이다. 기존 repo의 production 검증을 대체하거나 기존 PR을 병합하지 않는다.

**열람 순서**
1. `docs/REIONIZATION_DOSSIER_V2_KO.md`: 물리식, 수치/관측의 적용 범위.
2. `docs/IMPLEMENTATION_SPEC_KO.md`: Rust interface·자원·claim gate.
3. `contracts/RESEARCH_DAG.json`: 21개 기존 명명 노드 + 5개 새 노드(총26), 상태/선행/수용조건.
4. `docs/DAG_NODE_GUIDE_KO.md`, `docs/DAG.mmd`: DAG의 사람용 상세 설명과 기계 변환 다이어그램.
5. `contracts/PHYSICS_CONVENTIONS.json`, `STATE_VARIABLES.json`, `PROCESS_OWNER_REGISTRY.json`, `OBSERVABLE_CONTRACTS.json`, `SOURCE_REGISTRY.json`, `CLAIM_MATRIX.json`, `CODE_MAP.csv`, `TASK_CARDS.jsonl`.
6. `rust/rei_ssot_reference/`: **제한된 제조해** exact source-age/diagonal BI transport Rust library; PR150 native Rust production에 대한 PASS가 아니다.
7. `evidence/`: 실행 로그, 테스트 결과, SHA manifest, 게시·백업 receipt.

## 실행

```sh
python scripts/build_contracts.py
python scripts/validate_ssot.py
export PATH=/mnt/data/rust-1.94.1-prefix/bin:$PATH
CARGO_BUILD_JOBS=1 cargo test --manifest-path rust/rei_ssot_reference/Cargo.toml --offline --locked
```

Rust compiler/runtime가 새 세션에서 동일하지 않으면 `rustc --version`으로 실제 환경을 다시 확인한다. `scripts/build_contracts.py`는 JSON DAG를 재생성하며 기존 saved scientific evidence나 source inputs을 업데이트하지 않는다.

## 보존 규칙

- 사용자 제공 문서의 본문은 `inputs/`에 private backup용으로만 포함된다. public GitHub는 derivative science/SSOT만 게시한다.
- `PROJECT_STATE`, `CURRENT_PLAN`, `main`, owner PR150, PR171/173/174, stored FULL005/SOURCE009/010/011/SOURCE012 결과는 변경하지 않는다.
- Python oracle은 참고/테스트 도구이고 active REI solver는 Rust binary64. full EoR, late-time isotope radiation, tilt, 11 Bianchi, global CMB sky는 HOLD.
- `BACKUP_AND_PUBLICATION.json`의 provider-level ACK vs restore/sha distinction을 매 턴 지킨다.