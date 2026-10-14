# PHYS22 재현 안내

이 패키지는 고정된 초기조건에서 얻은 전단의 초기시간 응답 계수, 그 유도와 기록된 검증을 포함한다. 표준 Python 라이브러리만으로 파일 식별을 확인하고 **PHYS22에서 새로 작성한 네 프로그램**을 재실행할 수 있다. 가스 시간궤적이나 유한시간 오차한계를 구하는 프로그램은 아니다.

## 필요한 환경과 명령

Python 3.10 이상이 필요하다. 기록된 실행 환경은 각 실행 JSON에 있다. 추가 패키지 설치, 네트워크, Rust 컴파일은 필요하지 않다. 압축을 푼 뒤 `reproduce.py`가 있는 디렉터리에서 다음 명령을 실행한다.

```bash
python3 -B reproduce.py --verify-only
```

이 명령은 패키지 전체 파일의 크기와 SHA-256, 일곱 Rust 입력의 SHA-256과 Git blob ID, 상속한 함수 파일의 고정 SHA-256을 확인한다. 패키지에 누락되거나 목록에 없는 파일, 심볼릭 링크가 있으면 실패한다. 어떤 과학 계산도 실행하지 않는다. `MANIFEST.json`은 자기 자신만 해시 대상에서 제외한다.

새 계산 결과를 만들려면 패키지 **밖의, 아직 존재하지 않는** 디렉터리를 지정한다.

```bash
python3 -B reproduce.py --output-dir ../PHYS22_reproduced
```

다른 위치에서 실행해도 `reproduce.py` 기준으로 모든 입력을 찾는다. 기존 결과나 패키지 안의 파일을 덮어쓰지 않는다. 이미 존재하는 출력 디렉터리를 다시 지정하면 중단한다. 각 하위 명령의 stdout, stderr, 종료 코드와 실제 경과시간을 기록한다. 실패하면 그때까지의 출력은 남기고 후속 실행을 멈춘다.

## 실행 범위

| 순서 | 프로그램 | 기록된 검증 | 새 출력 |
|---|---|---:|---|
| 1 | `code/initial_time_coefficients.py` | 21개 | `owner.json` |
| 2 | `contributions/radiation/check_initial_time_series.py` | 52개 정확 유리수 검사 | `radiation.json` |
| 3 | `contributions/gas/local_initial_response.py` | 11개 국소 검사 | `gas.json` |
| 4 | `code/compare_initial_coefficients.py` | 두 계산 방식 사이 16개 비교 | `comparison.json` |

세 번째 프로그램은 SHA가 고정된 `inputs/inherited/PHYS21_local_gas.py`의 함수만 가져온다. 그 파일의 이전 `__main__` 검사, PHYS19·20·21의 닫힌 검증 묶음, native 실행, 가스 IVP, 그림 재생성은 실행하지 않는다. 결과 그림은 이미 만들어진 파일로 포함되며 manifest에서 바이트 식별만 확인한다. 하위 Python 실행에는 `-B`와 `PYTHONDONTWRITEBYTECODE=1`을 적용해 패키지에 캐시를 만들지 않는다.

## 기록 결과와 비교하는 방법

각 새 JSON을 패키지의 원래 결과 JSON과 비교한다. 계수, 단위, 정밀도, 허용오차, 개별 잔차, 입력 식별, 한계, 각 검사 판정을 포함한 **모든 과학 필드에 정확한 JSON 형식·값 일치**를 요구한다. 숫자 비교에 새 허용오차를 적용하거나 실패 잔차를 제외하지 않는다. 출력 정렬이나 들여쓰기의 차이는 JSON 의미 비교에 영향을 주지 않는다.

제외하는 메타데이터는 다음과 같이 제한한다.

- owner와 gas 결과의 최상위 `/python`: 계산에 사용된 Python 버전 문자열이다.
- comparison 결과의 `/inputs_sha256`: 기록 쪽 해시가 기록된 두 입력 파일에, 재생성 쪽 해시가 실제 재생성된 두 입력 파일에 각각 일치하는지 먼저 확인한다. Python 버전 문자열만으로 파일 바이트가 바뀔 수 있으므로 그 뒤 양쪽 JSON 비교에서 이 해시 필드를 제외한다. 열여섯 비교의 숫자와 결과는 모두 그대로 비교한다.

방사선 결과에서는 어떤 필드도 제외하지 않는다. 코드 SHA와 상속 입력 SHA는 비교에 남긴다. 이 정책과 실제 비교 판정, 원래·재생성 파일 SHA 및 바이트 일치 여부는 `PORTABILITY_REPLAY.json`에 기록한다. 각 명령의 실행 기록은 `PORTABILITY_EXECUTION.json`에 있다.

Decimal 계산과 binary64 계산의 독립 비교에는 원래 PHYS22 프로그램이 정한 `5e-12` 기준이 포함된다. 이는 그 과학 비교 프로그램의 기존 기준이다. 패키지 재생성 결과를 원래 JSON과 대조하는 단계에서는 숫자나 잔차를 그 기준으로 느슨하게 비교하지 않는다. 다른 Python·수학 라이브러리 환경에서 부동소수점 차이가 생기면 정확 JSON 비교가 실패할 수 있으며, 이 결과를 임의로 성공 처리하지 않는다.

## manifest와 실행 영수증

작성자는 최종 보고서와 독립 검토가 갖춰진 시점의 manifest를 검증한 뒤, 위 네 명령을 한 차례 실행했다. `evidence/PORTABILITY_REPLAY.json`과 `evidence/PORTABILITY_EXECUTION.json`에는 그 실행 **직전** manifest의 SHA가 기록된다. 그때의 정확한 manifest 바이트는 `evidence/PRE_PORTABILITY_MANIFEST.json`으로 보존한다. 이 사본과 두 영수증을 넣은 뒤 최종 `MANIFEST.json`을 다시 만들기 때문에 최종 manifest SHA가 실행 직전 SHA와 다른 것은 정상이다. 영수증은 미래의 최종 manifest를 검증했다고 주장하지 않는다. 최종 manifest의 실제 파일 크기와 해시는 `--verify-only`로 따로 확인한다.

이 로컬 재실행은 원격 저장소·파일 서비스에서 전체를 내려받아 복원한 검증이 아니다. 또한 다른 플랫폼에서의 비트 일치, native Rust와의 산술적 동등성, 실제 유한시간 온도나 이온화 궤적, 중력 역반응을 입증하지 않는다. 물리 상태는 `HOLD`이며 `[160,161] FAIL`, `tick160`, auxiliary escape `FAIL`, HH/RCT/CR `OFF`, precision atomic `PARKED`를 유지한다.
