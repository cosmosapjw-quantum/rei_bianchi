# PHYS24 재현 안내

완성 ZIP을 새 디렉터리에 풀면 고정 입력, 정확한 곡률 인증, 독립 수치 계산, 보고서·그림·검토 기록을 함께 읽을 수 있다. 기본 두 계산과 wrapper는 Python 3.10 이상 및 표준 라이브러리를 사용한다. Git에 게시한 문서 투영본의 README는 archive identity를 가리키며, 전체 파일 무결성과 portability를 재현하려면 완성 ZIP을 사용한다.

## 파일 무결성만 확인

묶음 루트에서 실행한다.

```bash
python3 -B reproduce.py --verify-only
```

루트 MANIFEST.json의 모든 파일에 대해 SHA256·바이트 수·정규 상대경로·실제 inventory를 확인한다. 누락·목록 밖 파일·symlink·특수 파일을 거부한다. Manifest는 자기 해시 순환을 피하기 위해 자체 파일만 목록에서 제외하며, 검증 출력에는 실제 읽은 manifest identity가 포함된다. 이 모드는 어떤 과학 프로그램도 실행하지 않는다.

이는 제공된 manifest와 파일의 일치를 확인하는 절차다. Manifest에 대한 외부 서명이나 실제 과학적 타당성은 별도 근거다. 완성 ZIP의 외부 SHA는 detached publication receipt에서 확인한다.

## 새 PHYS24 프로그램만 재생

출력의 부모 폴더는 존재해야 하고 출력 폴더 자체는 아직 없어야 한다. 다음 절대경로를 실제 새 경로로 바꾼다.

```bash
python3 -B reproduce.py --replay --output-dir /absolute/existing-parent/PHYS24_replay_01
```

출력은 묶음 루트와 그 하위에 둘 수 없다. Wrapper는 먼저 무결성을 확인하고 다음 두 프로그램만 각각 한 번 실행한다.

| 프로그램 | 비교할 원 결과 | 역할 |
|---|---|---|
| contributions/curvature/exact_curvature_certificate.py | CURVATURE_CERTIFICATE.json | 새 14차 곡률·8차 끝점 다항식 인증 |
| contributions/numerics/moment_envelope.py | MOMENT_ENVELOPE.json | 원식 Taylor jet/직접 차분·고정 모멘트 결과 |

현재 wrapper와 같은 interpreter를 쓰고 프로그램별 timeout은 60초다. 실패·시간 초과의 원 로그를 보존하며 자동 재시도하지 않는다. 초기 무결성 실패면 과학 실행을 시작하지 않는다. 두 subprocess의 exit 0과 결과 비교 PASS가 모두 필요하다.

결과의 모든 과학 값·타입·해시·허용오차·검산 항목은 canonical JSON으로 정확히 같아야 한다. 객체 키 순서와 공백 외에 제외하는 것은 **최상위 Python 버전 문자열 하나씩**뿐이다. 정확 인증의 필드명은 python, 수치 결과는 python_version이며 원래/재생 값을 receipt에 모두 남긴다. 같은 interpreter에서의 실제 raw-byte 일치도 closeout에 별도로 기록한다. 과학 값이 다르면 수치 허용오차를 새로 적용하거나 원본을 바꾸지 않는다.

새 결과 JSON, stdout/stderr, REPLAY_RECEIPT.json에 실제 명령·시각·exit·코드/결과 identity가 남는다. 이 재생은 이동 가능한 패키지인지 확인하는 절차이며 최초 exact20/20, numerical156/156을 새로운 독립 물리 검산으로 다시 세지 않는다. 중단된 출력 폴더는 그대로 보존한다.

## 닫힌 입력의 경계

inputs/PHYS22_INITIAL_COEFFICIENTS.json의 수치 Jacobian과 inputs/inherited/PHYS23_SPECTRAL_RESPONSE.json의 기존 mono bracket·반례가 읽기 입력이다. inherited Python 파일들은 출처를 보존한 참고 자료다. 두 새 프로그램과 wrapper는 inherited Python의 main이나 suite를 import/실행하지 않는다. 곡률 기여는 읽은 이전 polynomial utility의 알고리즘을 새 코드에 명시적으로 재사용했다.

Inherited 보고서/노트의 본문은 원래 바이트를 유지했다. 그 문서 안의 원래 상대 링크는 PHYS23의 immutable publication 문맥에 속한다. PHYS24의 주요 보고서·코드·새 기여문 링크는 이 묶음 안에서 해석된다. 이전 원문 위치는 PHYS24_REPORT_KO.md와 detached receipt의 input commit으로 찾을 수 있다.

Native run, gas IVP, 닫힌 PHYS19–23 suite, source/default/runtime 변경, threshold crossing, 유한 시간/전단 잔차 계산은 재현 범위에 포함되지 않는다. 수학 명제는 고정 수치 J의 exact-real 해석에 조건부이며 physical HOLD를 유지한다.

## 그림만 다시 만들기

제공된 PNG/PDF를 바로 사용할 수 있다. 그림 생성이 필요할 때만 Matplotlib과 NumPy가 있는 환경에서 실행한다.

```bash
python3 -B code/make_envelope_figure.py --output-dir /absolute/new-figure-directory
```

이 명령은 새 PHYS24의 response helper를 241개 표시점에서 평가하고 PNG·PDF·표시용 JSON을 만든다. 어떠한 과학 main도 호출하지 않으며 표시 격자를 새 구간 인증이나 독립 검산으로 세지 않는다. 기본 wrapper는 그림 프로그램을 실행하지 않는다.

## 판정과 게시 기록

최종 과학 판정은 independent/DECISION_REVIEW.json, portability는 portability/REPLAY_RECEIPT.json, 최종 상태는 state/CLOSEOUT.json을 따른다. 완성 archive를 새 경로로 복구한 verify-only와 Git 원격의 ACK/tree/blob 확인은 detached PHYS24_PUBLICATION_RECEIPT.json의 서로 다른 항목이다. Local restore를 full remote restore라고 부르지 않는다.
