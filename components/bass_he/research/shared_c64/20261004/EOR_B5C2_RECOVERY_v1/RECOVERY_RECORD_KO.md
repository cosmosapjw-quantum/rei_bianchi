# B5C2 중단 복구 기록

2026-10-04. RECOVERY_COMPLETE__B5C2_REPLAY_VERIFIED__B5C3_NOT_STARTED.

## 실제 회수

B5C2의 응답 전달은 끊겼지만 과학 산출물과 게시·백업은 이미 완료되어 있었다. Library의 실제 ZIP을 materialize하여 CRC, 101개 payload와 동봉 B5C1의 101개 payload를 확인했다. 원 연구 worker는 현재 runtime에서 관측되지 않았다. 원 worker의 과거 종료 시각은 판정하지 않는다.

원 ZIP: BASS_HE_EOR_B5C2_INNER_BOUNDARY_20261004_v1.zip
bytes: 12588189
SHA256: 5d3450b04234bdc0b65e770ebdb142114fae4ce89ab158391fe60854aa24f5b7
기존 scientific publication commit: 35b5fa6d2a3a8676e8312ccb4373d1b20c329a3c
기존 tree: b9e417ee53b8e70354ed8a6c865a85eacf3fa6bf

기존 공개 11개 파일의 blob와 크기를 원 publication mapping과 대조했다. 4개 scalar runtime, 4개 시험 파일, 3개 문서가 일치한다. 전체 8개 runtime 모듈과 전자 endpoint 코드, 59개 시험은 원 ZIP에 있다. 기존 Drive/Dropbox 사본은 현재 object metadata에서 원 크기와 일치했다. 원 ZIP을 다시 업로드하지 않는다.

## 새 환경 재현

- 복원본 59개 시험과 설치본 59개 시험이 통과했다. 고유 시험118개로 세지 않는다.
- 설치된 8개 Python 모듈의 bytes가 원 src와 일치한다. 수치·시험 dependency는 기존 환경을 사용했다.
- UA 및 local-seed CLI 2개 출력이 원 데이터와 byte 동일하다. 기존 출력 덮어쓰기와 production 요청은 exit2로 거부했다.
- 원 80자리 Coulomb/Kummer oracle 15개를 재현했다. 최대 상대차이: log derivative 1.6111160359567919e-16, inner absorption integral 5.1568295922949026e-14.
- 원 payload는 실행 전후 동일하다. 새 전자 continuation campaign, 산란 campaign, Fortran build, MPI, 독립 scientific review는 미수행이다.

최초 복구 helper가 부모 manifest 형식을 잘못 가정하여 IndexError로 종료됐다. 실제 MANIFEST.json을 읽도록 helper만 수정했고 실패본을 보존했다. 제품 코드·원 숫자·허용오차는 바꾸지 않았다. pip cache 권한 경고와 exact-check runner의 TERM 환경 경고도 보존했다.

## 과학 범위와 다음 단계

회수된 B5C2는 Z3 united-atom branch/gap/dipole과 2/R 특이점을 유지한 Frobenius 초기화, endpoint-normalized inner absorption을 다룬다. 원8개 작은-R 점과5개 독립 변분 비교를 이번 복구에서 다시 계산하지 않았다. 유한 local polynomial의 series tail 상한은 실제 전자곡선·부동소수점 전체 오차 인증이 아니다.

Next: EOR_B5C3_INNER_OPTICAL_REMAINDER_AND_BOUNDARY_SENSITIVITY.
실제 내부 V-2/R와 Gamma의 나머지를 정칙 radial 해 및 matching 오차에 연결하는 단계이며 이번에는 시작하지 않았다. NCP64는 현재 필수 아니다. rei_bianchi 기하·유체·수송은 변경하지 않는다.
scientific_PROMOTE=HOLD; EOR_THEORY_GATE=NOT_SATISFIED; Eq55=NOT_RUN; physicalsourceadmission=false; independent_review=NOT_RUN.

## 새 복구 증거 묶음

BASS_HE_EOR_B5C2_RECOVERY_20261004_v1.zip
bytes: 59524; entries: 41; manifest payloads: 40
SHA256: 6ca6b13eec968faf602870b2c6ec3bb45ee76932d9ecfe721f8b4aa799f8b02a

이 작은 묶음은 원 12.6MB ZIP을 중복 포함하지 않는다. 원본 identity, recovery inventory, 실제 재현 로그와 코드, 결과·다음 handoff를 포함한다. 새 전송 최종 상태는 detached delivery receipt가 소유한다. Library 원 ZIP은 실제 복원했지만 Drive/Dropbox raw ZIP download/restore는 실행하지 않았다.
