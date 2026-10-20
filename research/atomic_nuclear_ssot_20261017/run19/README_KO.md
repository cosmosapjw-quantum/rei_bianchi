# RUN19 — T 계수 재사용, 경량화 및 원자·핵반응 provider 확장

현재 기준 원격 부모는 RUN18 `99e07bcff126d0a73a03bafc4b71e0b735dbcc3e`다. 원래 RUN13 standard/tight 이력은 보존하며 새 IVP를 실행하지 않았다. 원래 45/26 DAG는 `DAG_PROGRESS_UNIT_A.json`의 원본 경로와 SHA로 유지한다.

## Unit A 완료

`native/`는 immutable RUN13 91-file source에서 만든 개발 fork다. 3개 파일 수정 및 3개 신규 파일로 prepared T bundle 공유, 정확한 EOS T 비트 재사용, caller-owned batch, text IPC batch를 구현했다. Direct 기본 경로는 264개 입력 × 28개 출력에서 원래 assembly와 비트 단위로 같다. 신규 Rust 검사 8개와 같은 CPU/worker 조건의 실제 짧은 benchmarks를 완료했다. 전체 명령·원시 결과·실패 기록·수치 제한은 `execution/unit_a/UNIT_A_REPORT_KO.md`와 receipt에 있다.

원래 source의 물리 계수식과 threshold는 유지했다. `owner_src`라는 이름을 가진 원본은 RUN13에 그대로 있고, RUN19 fork의 deuterium_atomic.rs에는 prepared assembly seam만 명시적으로 수정했다. 기본 source-off gas RHS 이외의 전체 photo/transport integration 가속을 입증한 결과는 아니다.

## 새로 확인된 오차 구조

고정 source의 T-only 표는 값 오차를 줄이지만, CI와 RR의 작은 차로 이루어진 net RHS에는 cancellation이 있다. 기존 log-linear 표의 본 표본에서 양의 CI/RR event 최대 상대차는 2.369e-7인 반면 chemical net은 7.171e-5까지 증가했다. 절대오차와 채널별 예산을 유지한다. 정확 T cache는 계수 근사를 추가하지 않는다.

## 현재 진행 중인 후속 작업

Unit B는 logT 위 계수값의 4점 cubic 표, source-bound 저장/재사용 및 실제 SIMD/배치 측정이다. Unit C는 선행 Li6/Li7 구현의 compatibility forwardport, 저자 VF1996 Be RR 계수의 제한된 provider와 사용자 그림의 19반응 coverage다. 아직 이 두 단위의 완료를 선언하지 않는다.

## Inventory 정정

`inventory/remote_selected/INVENTORY_KO.md`의 초기 R9 요약에 쓰인 “Li/Be 6개”는 잘못된 범위 해석이었다. 실제 R9 contract는 H I, He I, He II, Li I, Li II, Li III이며 Be 채널은 없다. 원문을 삭제하지 않고 `inventory/R9_SCOPE_CORRECTION.json` 및 실제 contract를 함께 보존한다.

## 게시와 백업

이 source snapshot의 실제 원격 commit, archive SHA와 Drive/Dropbox 응답은 `delivery/UNIT_A_DELIVERY.json`에 게시 후 추가한다. 큰 gzip 원시 IPC 입력/응답과 실행 binaries는 전체 archive에 포함한다. Git에는 원시파일 SHA를 담은 manifest, 재현 source와 모든 텍스트 수치 결과를 보존한다. 업로드 응답, byte readback, 계산 재현은 각각 별도 상태로 보고한다.
