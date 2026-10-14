# FLRW08 continuum probe 완료 인계

같은 task `REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL`과 원 source parent
`e63ca0735a3e3e7eebbf4498c697d806d375e191`을 유지한다. 이 폴더의 MODEL.md,
RESULTS.json, VALIDATION.json, REVIEW.json을 읽는다. 짧은6개 궤적112 macro
호출+진단6회, self-check70개, Host/독립 reviewer의 frozen acceptance 검증을
완료했다. 독립 higher review에는 actionable finding이 없다. 원 생산 코드와
완료15개 campaign·기존 FLRW08 파일·dirty Cargo.lock은 보존됐다.

원 transport는 occupied10eV 노드에서 불연속이다. full-domain finite generator를
가정하지 않는다. P가 p0를 guard로 옮기는 축소 상태에서는 lambda1*p1을 guard에
직접 보내는 후보 생성자를 사용했다. 원 반복 map과 projected ODE의 전역 수렴은
미증명이다. DOP853/RK45 agreement4.44e-16, 개별 xHII bias의 약일차 감소는
수치 진단이다. 짧은 BI−FLRW 부호는 반올림 수준이며 미확립이다. 작은 dense
음수·최소 dt의 반올림 상승·실패 컴파일·수정 전 온도 false-FAIL을 보존한다.

다음 가장 작은 연구 행동은 원 transport와 P를 합성한 map의 경계/단일 격자
전이 오차를 임의의 허용 양수 photon 상태에서 제한하고, 그 관계를 chemistry와
결합할 때 필요한 안정성 조건을 명시하는 것이다. 기존 initial-state probe를
다시 실행해 임의 상태 또는 전역 certificate를 주장하지 않는다. 성공한 정확한
출력과 외부 검증 영수증을 재사용한다. 이후 연속 enclosure가 필요하면 동일
모형·구간·초기값을 고정한 별도 계산으로 진행한다. 전체 campaign이나 임의의
시간/격자 tuning은 이번 완료 조건이 아니다. F09 공통 domain/supplier binding과
물리 fit·관측 admission 의무는 그대로 미완료다.

CODEX_ONLY 이번 unit의2 native dispatch/2,676,157 tokens, 기존 FLRW08
review418,735 및 local helper928 tokens를 .cuh/.../continuum-probe/
continuation-accounting.json에서 이어받는다. 모르는 Host 비용을0으로
취급하지 않는다. 과학적 HOLD와 continuum_time_error_certificate=
NOT_ESTABLISHED를 유지한다. commit/push/외부 메시지 전송은 수행하지 않았다.
