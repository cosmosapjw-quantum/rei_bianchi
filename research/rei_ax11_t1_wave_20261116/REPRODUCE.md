# T1 물리 비교 자료의 재현

이 묶음은 완료된 두 native T1 이력의 표본 입력, 실제 T0–T1 비교,
owner 수용·감사·실행·백업 receipt와 source binding을 포함한다.
원 DAG10/17, 확장28/88이다. Native 진화를 재실행하지 않고 저장된 자료만 소비한다.

실제 cloud 분석 환경은 Python3.12.14, NumPy2.3.5, SciPy1.17.0이었다.
그림 재생성에는 Matplotlib이 필요하다. 정확한 native compiler·binary·source
identity는 SOURCE_BINDING.json 및 native control archive에 보존되어 있다.

압축 묶음의 최상위(하위에 research/가 있는 디렉터리)에서 새 출력 경로를 골라 실행한다.

```bash
python3 research/rei_ax11_t1_wave_20261116/harness/analyze_t1_response.py research/rei_ax11_t1_wave_20261116/native_inputs results_reproduced
python3 research/rei_ax11_t1_wave_20261116/harness/audit_t1_response.py results_reproduced research/rei_ax11_t1_wave_20261116/native_inputs research/rei_ax11_t1_wave_20261116/receipts/CLOSED_RUN_LEDGER.json audit_reproduced.json
python3 research/rei_ax11_t1_wave_20261116/harness/owner_decision_t1.py results_reproduced audit_reproduced.json owner_admission_reproduced.json
```

`results_reproduced`와 두 새 JSON 출력이 이미 있으면 다른 경로를 사용한다.
기존 결과를 덮어쓰지 않도록 프로그램이 중단한다. 본 묶음 생성 단계에서
native 진화나 이 분석을 다시 실행하지 않았다. 실제 실행 근거는
receipts/CLOUD_ANALYSIS_EXECUTION.json이다.

T0의두gzip,원ownerphysics_consumer.py,원scenario lock와두milestone표를
원래repo-relative경로로 함께 넣었다. 다른 관측량이나 tolerance를 새로 만들지 않는다.
두수준 D01의재현은D12·수렴차수·fullAX11완료를확립하지않는다.

전체원본raw출력과126파일source/binary/preflight/analysis는
9개native archive로보존했다. Provider 식별자·bytes·SHA256·Dropboxcontenthash는
receipts/PROVIDER_BACKUP_VERIFICATION.json에서확인한다. 이archive에는
전체history,abundance,spectrum,ledger,feedback,checkpoint와실패기록이포함된다.
정확한재개지점과금지된중복실행은HANDOFF.md에있다.
