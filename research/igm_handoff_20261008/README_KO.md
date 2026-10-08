# IGM 후속 handoff — 2026-10-08

이 패키지는 IGM branch `forward/rem-hhe-igm-20261006@39c39eab1cc2f1a215723680accc123e67ef13b6`에 연결할 HE·HH·CR·REI의 최신 결과를 고정하고, **같은 상태·같은 시각의 공동 광이온화율/입사에너지 moment를 전달하는 연결부**를 실행·검증한다. 생산 solver·원자율·closure·허용오차·기본 OFF 설정은 변경하지 않는다.

네 작업 경로는 실제 cross-thread 반환 자료에서 확인했다. 모든 채팅의 전체 원문이나 채팅 제목과 저장소의 일대일 대응을 확인한 것은 아니다. 과거 대화 기억은 탐색에만 썼으며 아래 판정은 실제 파일과 commit을 읽어 갱신했다. 다른 채팅에 직접 게시되었다거나 owner가 채택했다고 주장하지 않는다.

## 최신 상태와 IGM 연결

| 경로 | 최신 결과/고정 source | 완료된 부분 | IGM에서 아직 필요한 것 |
|---|---|---|---|
| HE | RCT03E5, BASS_HE `91218a1d496fad1b7231f96488a8df56e4fd532a` | 8 heldout 시각, 96 snapshot, 72 비교 PASS; exact-bit prefix cache | E6 전체 지정 시각의 time/panel/order 예산; receiver 채택; 연속 참오차 |
| HH | ENERGY02; 원격 WU088_HH `649ecb06321d3f7956fc13902666f062dfcde50c`보다 최신 비원격 산출물 | opaque return API, passive photon-energy parameter 전달 | ENERGY03 fixed-grid remap; origin gas clock 보존; directional state; 원격 채택 |
| CR | R11, bass_cr `a45c8404b341c0595a2c429c8c4be8ad61a3ae89` | Gamma3+incident-energy3→전자·열·온도·광학 source의 exact fixed-state 사상 | 실제 시간 jump/node error/M4; IGM producer payload; 연속 tau 오차 |
| REI fastest track | BRIDGE10, rei_bianchi `42db9791eceab6988c9700682b7a2cd6edd614db` | 8→16 event mesh, 48 parameter roots의 제한적 비교 | BRIDGE11 16→32, estimator floor; canonical restart/uniform escape-work/연속오차 |
| IGM receiver | PR86 `8477bae16accaf3de168669aafd2f31eac2ca811` | canonical ledger, 별도 point/BE, frozen checkpoint, unprojected midpoint accepted record/restart | instantaneous 공동 moment exporter; projected feedback 및 full history HOLD |
| BASS·REC 보조 | BASS PR132/133, REC PR81의 SYNC03 head 유지 | 기존 visibility 수신·pure-H Peebles 및 Rust reference 자산 | 실제 short IGM history→BASS observable; late-IGM 초기조건/radiation 계약 |

HE의 1000–10000 K와 HH의 35000–60000 K 허용 범위는 겹치지 않는다. 공통 ON 이력으로 합치지 않는다. HE E5가 선택한 E4 archive와 CR R11이 사용하는 다른 E4 archive의 SHA가 다르므로 같은 fixture라고 합치지 않는다. `inputs/HE_HH_INTAKE.json`, `inputs/CR_INTAKE.json`을 따른다. REC PR81 첫 설명보다 현재 `FORWARD_STATUS.json`이 앞서 있다: 76 Rust 시험과 parity PASS는 완료 자산이며 consumer Gate I는 별개로 열려 있다.

## 이번 이론·코딩 루프

`THEORY.md`는 고정 상태의 공동 moment를 `m=m0+Σ gj uj`, `|uj|≤1`로 전달하는 정확한 사상을 유도한다. 같은 generator를 Gamma와 에너지에 함께 적용하면 각 출력 범위는 `L m0 ± Σ|L gj|`다. 입력을 독립 box로 풀어버릴 때의 불필요한 폭을 줄이면서 원래 상관을 보존한다. source당 입자 수가 변하므로 온도에는 `−T*Xedot/D` 항이 들어간다.

`bridge/joint_moment.py`는 실제 R11 core를 그대로 재사용한다. 이 추가 코드는 exact rational 입력, 명시적 epoch/state/provider/context, 단위, 최대 6개 공유 generator, 필요한 positivity/threshold/zero-rate 조건을 검사한다. 출력은 **제공된 family의 조건부 대수 결과**다. 입력 family가 참오차를 감싼다는 증명이나 공통 spectrum의 물리적 실현 증명은 제공하지 않는다.

실제 R11 저장 snapshot 3개와 두 finite-rule family를 새 연결부로 읽고, 원 출력과 exact parity 및 별도 열역학 식을 비교한다. 독립 이론 agent가 만든 synthetic rational oracle도 사용한다. 원 108008 spectral row 합·기존 chemistry 이력·Rust/interval campaign은 재실행하지 않는다. 최종 12개 시험, 실제 저장 출력 55개 exact parity, 별도 수식 20개 비교가 통과했다. 초기 구현의 세 가지 의도적 오류도 검출했고 최종 metadata 보강 전의 증거로 보존했다. 독립 reviewer는 조건부 adapter만 PROMOTE했으며 physical HOLD를 유지했다. 두 finite-rule family의 온도 범위는 독립 box보다 각각 약 126배·173배 좁지만 참오차 범위는 아니다. 실행 수치와 실제 실패/수정 내역은 `evidence/` 및 `RESULTS.json`에 둔다.

핵심 blocker를 더 구체화했다. PR86 `Accepted.total`의 A/B는 적분된 photons/H·erg/H이고 `midpoint.rhs`의 photo 0은 nonphoto stage 표식이다. 이것을 instantaneous Gamma/Ecal로 읽으면 안 된다. 지금 필요한 것은 양쪽의 **동일 상태·동일 시각에 실제로 관측한 순간 공동 moment payload**다. integrated owner를 dt로 나눠 순간값을 만들어 넣지 않는다. 현재 PR86 record의 이 rate-admission 거절은 원래 replay 기능의 실패가 아니다.

## 재현과 이어가기

저장소 root에서 Python 3.10 이상과 표준 라이브러리만으로 실행한다. output은 아직 존재하지 않는 경로여야 한다.

```bash
python3 research/igm_handoff_20261008/scripts/verify_package.py
python3 research/igm_handoff_20261008/scripts/reproduce.py --output /tmp/igm-joint-bridge-new
```

`START_PROMPT_KO.md`를 local Codex에 전달한다. 읽을 순서는 이 문서 → `HANDOFF.json` → `DAG.json` → `RECEIVER_CONTRACT.json` → `RESULTS.json` → `evidence/INDEPENDENT_REVIEW.md`다. 큰 donor archive는 이 패키지의 offline replay에 필요하지 않다. 생산 native 연결을 시작할 때는 해당 source/seed 의존성을 먼저 해소하며, 비공개 checkpoint나 host identity를 공개 Git에 넣지 않는다.

첫 local 구현은 `IGM-RATE-EXPORT01`: 실제 instantaneous joint moment를 명시적으로 export하고 이 연결부에 read-only로 넣는 것이다. 기존 accepted owner·source·control 수치는 그대로 보존하고 추가 observer 비용을 별도로 센다. 필요한 원 moment가 없으면 `MISSING_INSTANTANEOUS_JOINT_MOMENTS`로 반환한다. PR85의 compensated-log tail과 PR86의 dyadic Wide를 임의로 교체·혼합하지 않는다.

## 병렬 작업과 판정 제한

`DAG.json`은 각 owner가 예약한 E6/ENERGY03/BRIDGE11과 새 IGM 작업을 분리한다. 병렬로 할 일은 native export 계약, BASS visibility 입력 schema, REC late-IGM 초기조건 schema다. 새 material·time·spectrum 예산이 실제로 돌아온 뒤에만 coupled validation과 장시간 검증으로 이동한다.

PR85와 PR86은 이 패키지의 부모가 아니라 동일 IGM base에서 갈라진 독립 연구 브랜치다. 이 PR은 additive handoff이며 자동 merge를 하지 않는다. 원래 long-history 37-field 중 8개 실패, 별도 short m8→16 work_E RED, 각 donor의 physical HOLD를 그대로 보존한다. 짧은 제한 검증·정확 대수·build 성공을 첫 물리적으로 승인된 재이온화 곡선으로 승격하지 않는다.

Git/백업/CI의 최종 수신 상태는 별도 `PUBLICATION.json`에 기록한다. 현재 repository의 cargo-fmt 실패는 새 Python 연결부 검증과 별개이며 정확한 새 head의 실제 CI 결과만 기록한다.
