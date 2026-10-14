# Pushed RUX 결과와 axisymmetric 목표 연결 감사

**판정: 기존 구현·보존 결과·보고서는 재사용할 수 있지만, non-tilted axisymmetric Bianchi I reionization 목표는 아직 실행되지 않았다.** `069d6c8 → bccbe30 → 477f375`의 변경은 22파일(신규 21, lib 등록 1)이다. 본 감사는 읽기 전용이며 build/test/solver를 재실행하지 않았다. 요청 reviewer는 gpt-6-astra, 관측 runtime identity는 null이다.

## 실제 완료와 남은 범위

| 대상 | 완료된 재사용 범위 | 완료되지 않은 것 |
|---|---|---|
| RUX00 | 선택 source의 정확한 identity와 결손 기록 | 실제 scenario/provider admission |
| CC-PREP05 | typed warm adapter, 1-step executable, worker 보고 targeted tests 2개 | cold provider, source callback, axisymmetric transport, history runtime |
| RUX06 | 기존 ray/packet API와 결합 계약 조사 | 물리 axisymmetric geometry instantiation |
| Retained/review/report | 기존 15 끝점으로 만든 7 paired 차이, 그림, Markdown/LaTeX/PDF | 새 EoR 이력·새 물리 τ·full scientific PASS |
| Sibling intake | source별 exact identity·scope·후속 계약 | provider/receiver 새 실행 |

`rux_science.rs`는 단일 energy packet의 InitialStock을 받아 `primary_stage_step` 한 번을 호출한다. 새 코드에 a_perp/a_parallel, shear, 방향별 packet, geometry transport, 시간 변화 emissivity callback이 연결되지 않았다. adapter는 external emissivity와 imposed UVB를 명시적으로 거부한다. 따라서 이 executable의 컴파일 성공은 axisymmetric reionization 성공이 아니다.

실제 신규 scientific solver run은 0이다. `SOURCE_INTEGRATION_RECEIPT.json`의 imported_files도 비어 있다. PR114 warm FT03 후보와 30000–110000 K 지원은 유지됐으며 6.137/20 K 후보를 지원하는 source-backed rate/thermal provider와 실제 cosmology/clock/IC/source 선택은 미완료다. 이는 새 solver의 물리·수치 FAIL을 관측한 것이 아니라 입력·구현 미완료다.

## 바로 고칠 실행 전이

state-aware workflow를 읽기 전용 호출한 결과 ready는 빈 목록이다. 기존 완료 근거를 다시 만들지 말고 새 목표 overlay에서 다음 전이를 열어야 한다.

1. 현재 RUX03은 SOURCE-INTEGRATION 완료를 기다린다. 반대로 integration은 선택 provider/domain/ownership 결손으로 HOLD다. source-backed scenario/provider 계약 수립을 integration과 분리해 완료된 RUX00 근거에서 착수하고, 그 계약을 code integration이 소비하도록 한다. 원본 v2의 RUX03은 RUX00에만 의존했다.
2. CC-RECV는 rei 안의 schema/units/interface 준비와 sibling 코드 변경, 실제 ne(t) segment 계산을 분리한다. 첫 segment 부재가 interface 작업까지 막지 않게 한다. 기존 dirty sibling을 임의 수정할 필요는 없다.
3. 목표를 non-tilted axisymmetric Bianchi I로 명시하고 supported provider/source callback → axisymmetric geometry/transport → first supported interval → multi-epoch axisymmetric 및 FLRW control → paired/receiver → plots/report의 실제 구현·출력을 각 task에 배정한다. prescribed geometry인지 dynamical background인지도 선택 계약에 명시하며, 지원하지 않은 backreaction/continuum/sky claim을 자동 추가하지 않는다.
4. 새 prompt는 실제 `DAG_STATE.json`과 evidence로 완료 상태를 가져와 반복을 막는다. 최종 goal 미완료인데 generic HOLD 보고서만 다시 만드는 것을 종점으로 삼지 않는다. 해당 결손을 푸는 준비·구현의 다음 작업이 실제 ready로 남아야 한다.

## 관측한 제한과 작은 정정

CC-PREP05의 준비 명령 11/8 초과, 별도 cargo raw stdout/stderr 부재, 첫 LaTeX 실패 log 덮어씀은 이미 공개됐으며 다시 테스트해 과거 근거를 만들 필요가 없다. 성공 PDF와 압축 log는 존재한다. checkpoint의 baseline fmt CI 실패/후속 test skip도 green으로 바꾸어 말하지 않는다.

6개 input/figure SHA와 PDF SHA가 모두 현재 파일과 일치한다. 다음 두 metadata 항목만 작게 정정할 수 있다.

- `research/rux_science_20261014/report/SOURCE_MANIFEST.json`의 `inputs[0].role`: 해당 derived CSV는 **7행**, 원본 endpoint CSV가 15행이다.
- 같은 파일 `latex.compile_log`: 게시된 파일은 `report.log.gz`이며 `report.log`는 없다. 압축 경로와 gzip encoding을 적으면 된다. 데이터 재계산이나 PDF 재컴파일이 필요하지 않다.

후속 문서 위치 제안과 machine-readable 완료/결손 목록은 `AXIS_GOAL_SOURCE_AUDIT.json`에 기록했다. 현재 과학 admission은 HOLD로 유지하되 이미 완료된 준비와 retained 결과는 재사용한다.
