# PHYS26 재현 안내

이 묶음은 평균 18 eV·분산 고정 HeIII 초기 응답 구간을 다룬다. 연속구간 상·하한과 등호 조건의 증명은 contributions/theory/ENVELOPE_DERIVATION_KO.md에 있고, 수치 원 결과는 contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json이다. 독립 최종 판정·상태·게시 완료는 independent/DECISION_REVIEW.json, state/CLOSEOUT.json 및 별도 PHYS26_PUBLICATION_RECEIPT.json을 참조한다.

## 1. 바이트 검증만 수행

ZIP을 새 디렉터리에 풀고 그 안의 REI_PHYS26_MEAN18_FIXED_VARIANCE_RESPONSE_ENVELOPE_20261011 디렉터리에서 실행한다.

```bash
python3 -B reproduce.py --verify-only
```

Python 3.10 이상 표준 라이브러리만 사용한다. MANIFEST.json에 기록된 모든 payload의 크기와 SHA256, 예상하지 않은 파일 유무를 확인한다. 이 명령은 과학 프로그램을 실행하지 않는다. Manifest 자체의 identity와 ZIP의 identity는 detached 게시 receipt에 있으므로 자기 참조 해시를 만들지 않는다.

## 2. 이번 루프의 새 프로그램만 제한 replay

원 결과를 덮어쓰지 않도록 묶음 바깥의 존재하지 않는 절대 디렉터리를 지정한다.

```bash
python3 -B reproduce.py --replay-new-scope --output-dir /absolute/fresh/phys26-replay
```

먼저 payload를 검증한 다음 fixed_variance_envelope.py main을 정확히 한 번 실행한다. 첫 원 JSON과 새 JSON의 모든 필드 및 원 바이트를 비교하며 비교에서 제외하는 필드는 없다. 실제 Python 버전이 바뀌어 JSON의 환경 필드가 달라지면 불일치를 그대로 보고하며 허용오차나 비교 기준을 자동 완화하지 않는다. stdout, stderr, 출력 identity, exit code와 REPLAY_RECEIPT.json을 지정한 외부 디렉터리에 남긴다.

과학 프로그램은 PHYS26 계약·source identity·J 원 입력·PHYS25의 두 root 원 기록·새 protocol과 preexecution freeze를 읽는다. PHYS25 helper는 명시적으로 읽고 적응한 계산부의 계보 및 identity를 위해 포함했다. 오래된 module을 import하거나 오래된 main·부호 suite·근 탐색을 실행하지 않는다. 전역 도함수 부호는 상속한 PHYS24–25의 닫힌 증거로 소비한다.

최초 수치 실행은 7개의 고정 분산, 5개의 별도 원식 비교 에너지에서 모멘트·이차식 접촉·두 원식 경로와 혼합 구성을 검사한다. 모든 선택·허용오차·계산 예산은 contributions/numerics/PROTOCOL.json에 있다. 포터빌리티 replay는 같은 프로그램의 재현이며 독립 물리 검증으로 추가 계산하지 않는다. 첫 과학 실행과 replay 횟수는 state/CLOSEOUT.json에 따로 기록한다.

## 3. 원 결과·닫힌 입력·그림의 구별

inputs/inherited 안의 과거 문서는 PHYS26 시점에서 소비한 역사적 바이트다. 그 문서 내부의 과거 상대 링크는 PHYS25의 원 패키지를 기준으로 하며, 이 묶음에 과거 패키지를 통째로 중복 복원했다는 뜻은 아니다. 현재 입력 파일의 위치·원 경로·SHA256은 evidence/INHERITED_INPUT_MANIFEST.json을 따른다. 과학 증거 연결은 현재 report/PHYS26_REPORT_KO.md와 claims/CLAIM_DAG.json을 기준으로 한다.

그림은 직접 증명한 공식을 나타내는 표시 자료다. display 생성 코드·표본 수·원 입력은 figures/DISPLAY_PROVENANCE.json에 기록한다. 표시 곡선이나 점별 slack이 전역 최적성을 증명하지는 않는다. 기본 재현 명령은 그림 생성이나 과거 proof suite를 실행하지 않는다.

Git 게시본은 문서·코드·선별 원 증거를 읽기 좋게 옮긴 projection이다. 완전한 재현 묶음은 ZIP이며, Git tree의 blob 확인과 ZIP 전체 복원·검증은 서로 다른 완료 기록이다. 게시 전 최신 head 확인과 nonforce expected-head CAS, 게시 뒤 source tree 보존 확인을 실제 receipt에 남긴다.

## 4. 주장 범위

분포는 광자 수 기준 Borel 확률측도이며 델타 선을 허용한다. 분산은 eV², 응답은 초기 epsilon² t⁴ 계수로 s⁻⁴다. 수치 root 소수는 엄밀 interval 인증이나 물리 정확도 보장이 아니다. PHYS26의 정확한 부호 경계는 본문에 정의한 정확한 유일근으로 해석한다.

고정 직렬화 numerical J를 정확 실수로 해석하는 조건부 수학 결과다. Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED. 유한 시간·유한 epsilon·원자 데이터 또는 J 불확실성·실제 방출원 admission은 승격하지 않는다. Native, gas IVP 및 생산 source/default/runtime 변경은 0이다.
