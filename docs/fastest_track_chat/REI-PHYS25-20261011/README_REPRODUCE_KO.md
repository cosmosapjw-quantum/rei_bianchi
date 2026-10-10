# PHYS25 재현 안내

완성 ZIP에는 고정 입력, 세 번째 미분 인증, 최소 분산 후보 계산, 전역 최적성 유도, 최초 실행 기록과 최종 독립 판정이 들어 있다. Python 3.10 이상 및 표준 라이브러리로 아래 두 계산을 재생할 수 있다. 그림을 새로 만들 때만 Matplotlib과 NumPy가 필요하다.

## 파일 무결성 확인

ZIP을 새 디렉터리에 푼 뒤 묶음 루트에서 실행한다.

```bash
python3 -B reproduce.py --verify-only
```

루트 MANIFEST.json에 기록된 모든 파일의 SHA256·바이트 수·상대 경로·실제 inventory를 대조한다. 누락·추가 파일·symlink·특수 파일을 거부한다. Manifest는 자체 파일만 목록에서 제외하며 검증 출력에 manifest identity를 남긴다. 이 모드는 과학 프로그램을 실행하지 않는다.

## 두 새 프로그램의 제한 재현

출력 폴더의 부모는 존재해야 하고 출력 폴더 자체는 아직 없어야 한다. 아래 절대경로를 실제 새 경로로 바꾼다.

```bash
python3 -B reproduce.py --replay --output-dir /absolute/existing-parent/PHYS25_replay_01
```

출력은 묶음 밖의 새 디렉터리에만 쓴다. 사전 파일 검증이 통과하면 다음 두 프로그램을 각각 한 번 실행한다.

| 새 프로그램 | 결과 | 목적 |
|---|---|---|
| contributions/derivative/exact_third_derivative_certificate.py | THIRD_DERIVATIVE_CERTIFICATE.json | 실제 HeIII 커널의 세 번째 미분에 대한 정확한 유리수 인증 |
| contributions/numerics/variance_candidate.py | VARIANCE_CANDIDATE.json | 평균 18 eV의 제한 근·접촉·분산 계산과 원식 유한차분 비교 |

프로그램마다 timeout은 60초다. Wrapper는 같은 interpreter를 사용하고 stdout/stderr, 시작·종료 시각, exit, 코드·입력·결과 identity를 새 폴더의 REPLAY_RECEIPT.json에 기록한다. 실패 또는 시간 초과를 자동 재시도하지 않는다. 원 결과를 덮어쓰지 않는다.

결과 비교는 모든 과학 JSON 필드의 정확한 canonical equality다. 키 순서·공백 외에 제외되는 필드는 최상위 Python 버전 문자열 하나씩뿐이다: derivative는 python, numerics는 python_version. 원본·재현 버전을 receipt에 보존한다. 수치 값, 허용오차, root bracket, assertion, 코드 해시 등에는 추가 오차 허용을 적용하지 않는다. 같은 interpreter에서 실제 raw-byte 일치도 따로 기록한다.

이 재생은 이동 가능한 재현 묶음의 확인이며, 최초 exact 17/17과 numerical 127/127을 새 독립 과학 검증으로 더하지 않는다. 최종 상태에서 별도 재현이 이미 완료됐으면 같은 suite를 기본 준비 절차로 반복하지 않는다.

## 정확한 해와 수치 표현

최적 스펙트럼은 원식의 유일한 정확한 영점으로 정의한다. 수치 JSON의 midpoint는 유한 정밀도 근삿값이며 원시 응답 잔차를 유지한다. 잔차가 음수인 midpoint를 그대로 엄밀 feasible spectrum으로 부르지 않는다. 수치 sign bracket과 양쪽 endpoint 기록은 rigorous interval enclosure 또는 물리 입력 불확실성의 경계가 아니다. 전역 최적성은 미분 인증과 별도 변분 증명을 함께 사용한다. 수치 샘플의 dual positivity만으로 인증하지 않는다.

## 상속된 입력

inputs/PHYS22_INITIAL_COEFFICIENTS.json은 고정 수치 J 입력이다. inputs/inherited/PHYS24_*는 닫힌 과학 결과 및 출처 보존 자료다. 두 새 프로그램과 wrapper는 상속된 Python main/suite를 import·실행하지 않는다. 기존 helper 알고리즘을 읽고 명시적으로 옮긴 부분은 각 PROVENANCE.json을 따른다. 상속 보고서의 원래 상대 링크는 원래 PHYS24 publication 문맥에 속한다.

Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. Native·gas IVP·닫힌 PHYS19–24 suite·source/default/runtime 변경은 이 재현에 포함되지 않는다.

## 그림과 종료 증거

제공 PNG/PDF를 그대로 사용할 수 있다. 그림이 필요하면 code/make_variance_figure.py의 --output-dir에 새 절대경로를 지정한다. 이 프로그램은 새 수치 helper를 표시점에서 평가하며 과학 main을 호출하지 않는다. 표시 격자는 연속구간 증명이나 새 독립 검산으로 세지 않는다.

최종 과학 판정은 independent/DECISION_REVIEW.json, 실제 재현은 portability/REPLAY_RECEIPT.json, 연구 종료는 state/CLOSEOUT.json을 따른다. 완성 archive를 새 경로에 푼 최종 verify-only와 Git 게시 ACK·tree/blob 확인은 archive 밖 PHYS25_PUBLICATION_RECEIPT.json에 구분해 기록한다. Local restore는 full remote restore가 아니다. Git 문서 투영에서는 루트 wrapper/manifest 등 일부를 생략하므로, 엄격한 전체 재현에는 완성 ZIP을 사용한다.
