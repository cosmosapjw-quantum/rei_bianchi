# E13C8 전달 부분 정적 검토

**판정: `PASS_STATIC_PENDING_ACTUAL_RESTORE_AND_REMOTE_PUBLICATION`**

보고서·현재 상태·내부 NCP 인계문·재현 안내와 최신 복구 helper를 읽고, 파일 identity 및 두 dependency ZIP의 중앙 디렉터리/manifest 구성을 확인했다. 전체 과학적 채택은 별도 `e13c8_intake`의 독립 결정에 근거한다. 이 검토자가 저술한 성능 분석이나 portable 수정에 독립 과학 PROMOTE를 부여한 검토가 아니다.

## 전달 내용의 정합

- 전체 고정 캡처 OFF 유한 문제의 채택과 physical/continuum/production/receiver HOLD가 문서와 JSON에서 일치한다.
- 다음 signed Volterra 방법은 유도된 후보이며 구현·새 수치 적분·새 포함 구간 채택은 아직 없다.
- 실제 64 MPI rank의 wall, rank 균형, 개별 RSS 최대값 합이 원래 텔레메트리와 맞는다. CPU 이용률·직렬 대비 speedup·동시 전체 메모리 peak로 의미를 확장하지 않는다.
- 현재 NCP 작업은 0이며 ACK는 새 명령 실행을 요구하지 않는다. 복구도 현재 작업 명령이 아니고, 미래 heavy 실행은 별도 과학적 조건과 작업 목록이 있어야 한다.
- 전체 백업 안의 `dependencies/E13C7_INPUT.zip` 및 `dependencies/E13C7_NCP_RETURN.zip`가 실제로 존재하고 각각 예상 bytes/SHA와 일치한다. 추가 입력 첨부 없이 source와 반환을 복구할 구조다.
- Git의 작은 검토용 구성과 원본 데이터를 모두 담은 전체 백업을 구분한다. 외부 delivery receipt가 최종 전송 identity와 실제 업로드·복구 결과를 담당한다.

## 발견 후 해결된 사항

1. Manifest/part 선택 실패가 실패 영수증 범위 밖에 있던 문제는 root가 수정했다. 새 출력 디렉터리에서 입력 검증부터 `FIRST_FAILURE.json` 경로 안에 들어간다.
2. 사후 LPT의 16.22초 차이를 모든 scheduler의 최대 개선 여지처럼 읽을 수 있던 문구를 root가 고쳤다. 현재는 한 고정-duration LPT 배치의 결과라고 명시한다.
3. 원래 성능 분석 코드가 출력 폴더 안에 자신의 코드가 있다고 가정한 부분은 역사 파일을 보존하고 `code/analyze_telemetry_portable.py`에 최소 수정했다. 이 수정은 본 검토자의 구현이며, 1회 실행 검증은 **author verification**이다. 별도 새 출력 폴더에서 실제 exit 0, 전체 핵심 텔레메트리 동일, 한국어 메모 bytes 동일이었다. 이 과정의 kernel/MPI/benchmark 호출은 0이다.
4. 일부 프로그램이 입력과 출력을 같은 트리에서 사용하는 사실을 재현 안내에 반영했다. 잔여 매개변수와 그림 재현의 fresh staging 방식이 명확하다.

## 아직 이 검토가 확인하지 않은 일

Root가 최종 봉인 후 실제 `.bin` 이름의 part에서 전체 hydrate 복구 1회와 별도 missing-part 실패 영수증 control 1회를 수행해야 한다. 외부 transfer manifest의 dependency key는 재현 문서의 `E13C7_INPUT`와 `E13C7_NCP_RETURN`에 맞아야 한다. 새 source reducer 경로 및 반환 `BATCH`가 실제 hydrate 결과에 존재하는지는 그 영수증으로 닫는다.

최종 Drive/Dropbox 업로드, ACK/readback, 최종 외부 인계문, 전체 ZIP/조각/kit identity 및 draft PR 공개 상태는 root의 외부 전달 영수증에서 확인할 항목이다. 이 정적 검토는 그 행동이 이미 완료되었다고 주장하지 않는다.

검토한 각 파일과 최신 helper/portable 코드의 bytes/SHA, 두 dependency ZIP의 정확한 구성, 수정 증거 및 실제 portable 검증 영수증 pin은 `DELIVERY_STATIC_REVIEW.json`에 있다.
