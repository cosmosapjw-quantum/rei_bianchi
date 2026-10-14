# PHYS23 재현 안내

이 묶음은 PHYS23의 완성 결과, 새 계산 코드, 고정 입력, 출처 정보와 검토 기록을 함께 보관한다. 재현 wrapper는 Python 3.10 이상과 표준 라이브러리만 사용한다. 전체 ZIP을 새 디렉터리에 풀고 실행한다. Git에 게시한 문서 투영본만으로는 독립 재현에 필요한 모든 입력을 갖추지 못할 수 있다.

## 1. 파일 무결성만 확인

압축 해제한 묶음의 루트에서 다음 명령을 실행한다.

    python3 -B reproduce.py --verify-only

이 명령은 과학 계산을 실행하지 않는다. 루트 MANIFEST.json에 실린 모든 payload의 SHA256과 바이트 수를 읽어 비교하며, 빠진 파일과 목록 밖의 파일도 거부한다. wrapper 자체도 payload로 검증한다. MANIFEST.json은 자기 해시의 순환을 피하려고 자신의 파일 목록에서만 제외하며, 검증 출력에는 읽은 manifest의 SHA256과 크기를 기록한다. 이 검증은 제공된 manifest와 payload의 일치를 확인한다. manifest 자체의 외부 신뢰 서명이나 외부 게시 기록을 대신하지는 않는다.

사용하는 manifest 형식은 다음과 같다. 부가 설명 필드는 허용하지만 두 필수 필드의 의미는 고정한다.

    {
      "manifest_self_excluded": true,
      "files": {
        "reproduce.py": {"sha256": "64자리 소문자 16진수", "bytes": 12345},
        "PHYSICS_CONTRACT.json": {"sha256": "64자리 소문자 16진수", "bytes": 1234}
      }
    }

위 예시는 스키마 설명이다. 실제 manifest에는 manifest 자체를 제외한 모든 파일과 필수 과학 입력·출력·두 새 프로그램이 있어야 한다. 경로는 슬래시로 구분한 정규 상대경로여야 하며, 절대경로·부모 이동·빈 구성요소·역슬래시·콜론을 허용하지 않는다. 루트와 파일까지의 경로에 있는 심볼릭 링크, 묶음 안의 심볼릭 링크와 특수 파일도 거부한다. 따라서 새 로그나 출력은 묶음 바깥에 둔다.

정상 종료는 exit code 0과 status PASS이다. 일치하지 않는 바이트를 원본에 덮어쓰거나 허용 오차를 변경하지 말고, 해당 파일명과 오류를 먼저 확인한다.

## 2. 새 PHYS23 두 계산만 한 번씩 재생

출력 부모 디렉터리는 미리 존재해야 하고, 지정하는 출력 디렉터리 자체는 아직 없어야 한다. 아래 절대경로를 원하는 새 경로로 바꾼다.

    python3 -B reproduce.py --replay --output-dir /absolute/existing-parent/PHYS23_replay_01

출력 디렉터리는 묶음의 루트와 그 하위 경로에 둘 수 없다. 기존 디렉터리, 심볼릭 링크를 거치는 경로, 부모 이동 경로도 거부한다. 새 출력 디렉터리에서 먼저 무결성 검증을 하고, 통과한 경우 다음 두 프로그램만 각각 한 번 실행한다.

| 프로그램 | 원본 비교 대상 | 재생의 역할 |
| --- | --- | --- |
| contributions/signs/exact_sign_certificate.py | contributions/signs/EXACT_SIGN_CERTIFICATE.json | 유리수 다항식과 Bernstein 계수의 고정 부호 인증을 재생 |
| contributions/numerics/spectral_response.py | contributions/numerics/SPECTRAL_RESPONSE.json | 새 고정 스펙트럼 수치 결과와 유한차분 비교를 재생 |

각 subprocess는 현재 wrapper와 같은 Python 실행 파일을 사용하고, 바이트코드 파일을 만들지 않도록 -B를 적용한다. 원본 스크립트와 입력은 읽기 대상으로 사용하고 지정한 출력 JSON과 로그는 새 디렉터리에 쓴다. 프로그램별 제한 시간은 60초다. 오류나 시간 초과가 생기면 해당 실행과 로그를 보존하며 자동 재시도하지 않는다. 두 계산은 독립 실행이므로 첫 계산의 실패도 보존하면서 두 번째 계산은 한 번 실행할 수 있다. 초기 무결성 검증이 실패하면 어느 과학 프로그램도 시작하지 않는다.

비교는 JSON 객체의 키 순서와 문서의 공백을 제외한 정확한 값 비교다. 숫자 자료형과 값, 소스 SHA, 모든 과학 결과와 검산 결과는 그대로 같아야 한다. 수치 결과의 최상위 python 문자열 값만 실행 환경 표기로 취급하여 비교에서 제외하고, 원본과 재생의 버전 문자열을 receipt에 모두 남긴다. 해당 키가 사라지거나 문자열이 아니면 실패한다. 그 외의 버전·정밀도·허용 오차·메타데이터는 제외하지 않는다. Python 또는 Decimal 구현 차이로 과학 값이 달라져도 허용 오차를 새로 적용하거나 원본을 수정하지 않는다.

출력 디렉터리에는 두 결과 JSON, 각 프로그램의 stdout·stderr 로그, REPLAY_RECEIPT.json이 남는다. receipt는 실제 명령 배열, 작업 경로, 시작·종료 시각, 소요 시간, return code, 실행 횟수, 코드·결과·로그의 SHA256과 바이트 수, 정규화한 JSON 비교 해시를 기록한다. 프로그램이 시작되지 못하면 return code는 null이며 오류 이유를 기록한다. 최종 성공은 두 subprocess의 exit code 0과 두 JSON 비교 PASS를 모두 요구한다.

이 재생은 완성 묶음의 이동 가능성을 확인하는 절차다. 원래의 31개 정확 산술 검산과 65개 수치 검산을 새로운 독립 물리 근거로 중복 계산하지 않는다. 중단되거나 실패한 출력 디렉터리를 지우고 덮어쓰는 대신 그대로 보관하고, 필요성이 설명된 새 시도는 다른 디렉터리에 둔다.

## 3. 상속 입력의 경계

inputs/PHYS22_INITIAL_COEFFICIENTS.json은 PHYS22에서 닫힌 초기 계수와 국소 Jacobian을 읽기 전용 수치 입력으로 제공한다. inputs/inherited/PHYS22_initial_time_coefficients.py는 출처를 추적하는 참고 코드다. wrapper와 새 두 계산은 이 파일을 import하거나 main·suite를 실행하지 않는다. 과거 PHYS19–22 과학 계산, native 실행, gas IVP, production 소스 변경은 재현 명령에 포함하지 않는다.

이번 결과의 물리 범위도 유지한다. 초기 시간의 epsilon 제곱 계수에 관한 결론이며, 임계 에너지 통과·유한 시간 이력·Taylor 나머지·native 부동소수점 등가성을 확인하는 절차가 아니다. physical admission은 HOLD로 유지한다.

## 4. 선택 사항: 그림만 다시 만들기

그림은 제공된 PNG·PDF로 바로 확인할 수 있다. 렌더링을 다시 해야 할 때만 별도로 Matplotlib이 있는 Python 환경에서 다음 명령을 실행한다. 필수 무결성 검증과 두 계산 재생에는 Matplotlib이 필요하지 않다.

    python3 -B code/make_spectral_figure.py --output-dir /absolute/new-figure-directory

그림 출력도 묶음 밖의 새 디렉터리를 사용한다. 이 별도 스크립트는 새 PHYS23 수치 모듈의 해석식을 161개 표시 점에서 평가하고 PNG·PDF와 표시용 JSON을 만든다. 표시용 격자는 구간 전체의 무근 또는 단조성 증명이 아니며, 추가 물리 검산 횟수로 세지 않는다. 기본 wrapper는 이 렌더링 프로그램을 호출하지 않는다.
