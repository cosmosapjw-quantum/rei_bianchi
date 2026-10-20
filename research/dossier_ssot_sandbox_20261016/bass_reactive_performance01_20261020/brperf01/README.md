# BRPERF01 — 온도 계수 재사용·광자 병렬 평가·추가 원자 데이터

**판정: `COMPLETE_VERIFIED_BOUNDED_OPTIMIZATION`.**

원 H/He/D 물리, CX half-flow와 S10 제어기를 보존한 별도 opt-in 연구 구현이다. 전체 설명과 정량 결과는 [한국어 보고서](docs/REPORT_KO.md), 진행 상태는 [DAG](contracts/DAG_PROGRESS.json), 실행 근거는 각 하위 디렉터리의 verification receipt에 있다.

통합된 [정량 결과](evidence/SCIENCE_RESULTS.json), [검증 색인](evidence/VERIFICATION.json), [단계별 게시 영수증](contracts/STAGE_PUBLICATION.json)과 [그림 설명](figures/CAPTIONS.md)을 함께 제공한다. 전체 ZIP의 최종 SHA와 클라우드 raw readback은 자기참조 hash를 피하기 위해 별도 `PUBLICATION_RECEIPT.json`으로 발행한다. 전체 ZIP을 동결한 시점의 DAG와 그 후 게시 완료 영수증을 구분한다.

| 구현 | 코드 | 검증 범위 |
|---|---|---|
| 양의 compact T table | `rates/` | 15개 원 계수, 1…10⁶ K, 분기 fallback, scalar/SIMD, cache 복원 |
| 원 native RHS의 같은 T 공유 | `native_rates/` | 원 H/He/D ledger와 direct 비트 일치, CX flow 위임 |
| 반응 이력·성능 연결 | `integration/` | 고정 체적·광원 OFF H/He/D + 원 Strang/CX |
| 광자 계산 재사용·영속 작업자 | `photon/` | 실제 384개 source labels, BASS ±shear, 동결 기체 |
| Li/C/N/O 계수와 T table | `atomic_theory/catalog/` | 24 PI + 24 CI + 12 sparse RR, 계수 단계 |

기본 rate backend는 Direct, 기본 photon mode는 Baseline이다. 단위별 opt-in이 명시적으로 선택된다. 원 production, 기존 PR 및 물리 owner 파일은 변경하지 않았다.

## 재현

최종 전체 ZIP은 `brperf01/`와 `repo/research/.../bass_reactive06_vigilode_reference_20261019/`가 나란한 실제 검증 레이아웃을 포함한다. ZIP에서 복원하려면 다음처럼 새 경로를 지정한다.

```sh
python brperf01/VERIFY_ARCHIVE.py REI_BRPERF01_OPTIMIZATION_20261020_FULL.zip --extract /absolute/new/workspace
```

GitHub 소스 차분만 받은 경우에는 `MATERIALIZE_GIT.py`에 SHA가 고정된 이전 BR06 전체 ZIP과 새 작업 경로를 준다. 이전 ZIP identity는 `3137ad8903ef62073485a18e78b84966d3a9d09b9a60698dddfd492876432135`이다. 전체 Git 이력을 임의로 병합할 필요는 없다.

검증된 Rust 1.94.1과 offline registry를 선택한 뒤:

```sh
python brperf01/REPRODUCE.py /absolute/new/run-output --stage all
```

이 router는 benchmark·외부 업로드·원 source formatting을 실행하지 않는다. 개별 테스트와 native 이력 재현을 호출한다. 이번 실행의 실제 원 명령/종료코드는 `audit/`, `native_rates/evidence/`, `rates/evidence/`, `photon/evidence/`, `atomic_theory/evidence/`, `final_restore/`에 보존했다. 새 router 자체는 구문·인자 처리를 확인했고, 그 구성 명령들은 해당 기록대로 실제 실행했다.

Rust installer 전체 바이너리는 재생 가능한 의존성이므로 ZIP에 넣지 않았다. `runtime_evidence/RESTORE_RUNTIME.py`는 checksum이 고정된 제공 Rust archive와 포함된 99-package registry archive를 새 prefix에 복원한다. compiler 재설치와 science source fresh restore는 별도 검증 항목이다.

## 외부 원자 자료와 게시 범위

새 Rust 구현, numerical fit tables, 생성 계수, 원문 URL·SHA 및 검산 결과를 제공한다. 명시적인 재배포 허가가 확인되지 않은 새 외부 Fortran/설명 원문과 그 원문을 담은 snapshot은 게시 ZIP에서 원문 fetch 계약으로 표현했다. `atomic_theory/data/PROVENANCE.json`과 `fetch_sources.py`가 정확한 경로와 identity를 보존한다. 원문을 다시 받으면 hash를 확인한 뒤 독립 Fortran–ASCII 대조를 재실행할 수 있다. 이 참조 프로그램은 Rust 실행 의존성이 아니다. 각 하위 manifest의 원 실행 inventory와 최상위 archive의 제공 inventory는 이 명시된 omission 때문에 구분한다.

`wide=1.7.1`, `sha2=0.10.9`는 검증된 offline registry에서 실제 연결했다. 기존 VigilODE kernel pin을 유지하며, 최신 관측 default ref를 더 새로운 과학 revision으로 간주하지 않는다. 자세한 commit 관계와 SIMD compile-target 교정은 `reuse_notes/`에 있다.
