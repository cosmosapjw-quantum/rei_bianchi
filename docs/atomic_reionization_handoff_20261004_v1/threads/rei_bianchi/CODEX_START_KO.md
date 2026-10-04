# Codex 시작 지시 — rei_bianchi

목표는 공개 원자 입력으로 기존 Rust 소비자를 완성하고 검증된 FLRW/Bianchi-I 재이온화 이력에 도달하는 것이다. 새로운 원자 ab-initio 계산은 시작하지 않는다. 현재 사용자의 요청은 fast-track 게시/실행 준비와 원계획 보존이다. 이 handoff가 scientific gate를 통과 처리하지는 않는다.

1. 현재 repository와 branch를 확인한다. 대상은 `cosmosapjw-quantum/rei_bianchi`, 기존 `forward/rust-reion-kernels-20260922`다. 새 branch를 자동 생성하지 않는다. 사용자 변경을 덮어쓰지 않는다.
2. 이 파일 → `REPO_SNAPSHOT.json` → `TASKS.json` → 선택 작업의 입력만 읽는다. source의 현재 branch가 snapshot보다 진행되었다면 crate와 연결 lock의 diff만 읽어 조정한다. 전체 repo와 문헌 조사를 재시작하지 않는다.
3. `REI-F00`부터 dependency가 모두 충족된 첫 작업을 실행한다. 현재 완료한 것은 채팅 선행연구·정확 정수 회계 검산뿐이고 새로운 Rust code/physical history 실행은 0이다.
4. `rust/rei_microphysics/src/coverage.rs`는 현재 외부 rate 모두 거절한다. metadata만 추가하여 source를 admitted로 만들지 않는다. typed provider와 source/domain/unit/closure tests가 있는 새 admission path를 만든다.
5. 가장 중요한 compatibility 함정: 기존 `opacity_cMpc_inv` lowgroup effective-HI table에 explicit HI opacity를 더하지 않는다. R1 `HomogeneousBoundFree` adapter를 별도 구현한다. 기존 seven functions와 Rust binary64/subnormal semantics는 유지한다. retired Python/JAX runtime을 복구하지 않는다.
6. 먼저 `CONTROLLED_FIXTURE.json`의 모든 H/He species+3photon group toy를 구현한다. 이 fixture는 값이 완전히 지정되어 있으며 과학관측 입력을 대신하지 않는다. actual science SED/geometry/IC는 F07에서 결과 관찰 전에 고정한다.
7. strict local-error <2e−4, public width <2e−3, positivity, structural ledgers, table-event restart를 유지한다. 46,080-node/3 shape lanes는 inherited NodeHistory를 이어갈 때 적용한다. 새 homogeneous successor는 실제 parent와 applicable lanes/sites를 F00에서 잠그고 그 전체를 검증한다. 그 성공으로 원 NodeHistory gate를 닫지 않는다. 공동 parent는 서로 독립인 source sites를 모두 같은 값으로 묶는 뜻이 아니다. source-variable 합집합을 명시하라.
8. 해당 task targeted tests가 닫히면 receipt를 쓰고 다음 ready task로 진행한다. 테스트를 의미 없이 더 늘리거나 새 audit planning loop를 시작하지 않는다. actual nonlinear remainder를 증명하지 못하면 그 항만 unresolved로 기록한다.
9. 종료 또는 handoff는 완료 task·실제 command/exit·artifact hashes·미완료 gate·다음 task를 반환한다. R0 provider ACK, R1 metadata identity, 실제 restore, science validation은 분리한다. 이 연구 파일들의 GitHub·Drive·Dropbox receipt는 최상위 게시 파일을 참조한다.

기준 코드 commit은 `0100b1dfa023928d67602877876b586fea319d13`이다. historical whole-interval FAIL 및 old judge는 변경 금지. 첫 coupled Bianchi history는 F05 first full interval을 통과한 후다. finite tilt/REC splice/CAMB/all11 families는 `LEGACY_LANE.json`의 명시적 reopen 조건에서 호출한다.

반환 JSON 최소형:

```json
{"task_id":"REI-F00","status":"NOT_RUN","base_commit":"0100b1dfa023928d67602877876b586fea319d13","commands":[],"artifacts":[],"scientific_claim":"none","gate_changes":[],"failure_kind":"none","next_ready_task":"REI-F00"}
```

실제로 수행한 값만 바꾼다. `NOT_RUN`을 문서 존재만으로 PASS로 바꾸지 않는다.
