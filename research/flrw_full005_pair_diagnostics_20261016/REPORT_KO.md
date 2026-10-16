# FULL005 저장 이력의 연속 PL 쌍 진단

저장된 두 적응격자 이력을 `L=ln(a)`에서 연속 조각선형(PL) 함수로 재구성하고, 공통 구간의 supremum 및 L1·L2·RMS 차이를 계산하는 구현을 완성했다. 독립 C9 판정은 **PASS_SCOPED**이며 지적과 추가 수리는 없다. 판정 범위는 저장 이력 재구성의 진단 구현이다. 실제 FULL005 전체 원자료에 대한 새 연속 진단값은 **NOT_RUN**이다. 현재 작업 환경에 전체 history/abundance 원자료가 제공되지 않아 합성 입력으로 구현을 검증했다.

기준은 동결된 `CONTRACT.json`과 `THEORY.md` R1–R10이다. 두 격자의 knot를 순서대로 병합하면 각 구간의 차이는 affine 함수다. 구간 폭 h와 끝점 차이 p,q에 대해 supremum은 병합 knot에서 얻으며, 제곱 적분은 `h(p²+pq+q²)/3`이다. 절댓값 적분은 같은 부호 또는 영점 끝점에서 `h(|p|+|q|)/2`, 반대 부호에서 `h(p²+q²)/(2(|p|+|q|))`이다. 구간 기여를 합산하고 제곱근과 구간 길이 정규화로 L2와 RMS를 얻는다. 적분 측도는 무차원 `d ln(a)`이며 observable 단위와 기존 H/He 정규화를 유지한다.

`vendor/pair_diagnostics.py`는 입력 배열을 복제하거나 병합 격자를 저장하지 않고 순회한다. 계산량은 O(k(n+m)), 추가 작업 메모리는 O(k)다. 입력 배열과 출력 저장공간은 이 추가 메모리에서 제외된다. `analyze_saved_pair.py`는 Python 표준 라이브러리만 사용하며 history/abundance를 각각 한 번 읽는 동안 SHA256을 계산한다. 동일한 동결 입력의 기존 성공 영수증을 통해 물리·ledger 검증을 재사용하고 ledger/checkpoint는 열지 않는다. 누락·불일치 입력은 새 지표가 null인 HOLD로 반환한다. 기존 후처리 caller에는 기본값이 꺼진 선택 기능으로 연결해 기존 sampled 출력과 milestone을 유지했다.

새로 실행한 검증의 관측 결과는 다음과 같다.

| 단계 | 실제 결과 | 근거 |
|---|---|---|
| R6 | Wolfram 구간 적분과 대수 항등식 잔차 0 | `evidence/wolfram_pl_integrals.json` |
| R7 | 독립 Fraction 다항식 원시함수·영점 분할로 8개 합성 fixture의 적분식 정확 일치; 기존 Fraction supremum과 일치 | `probe/RESULT.json`, `probe/stdout.log` |
| C6 | 서로 다른 구현 사례 9개 통과 | `coding_evidence/C6.json` 및 실행 로그 |
| C7 | 과학·수학 사례 4개 통과; 독립 exact lifted-binary64 fixture 8개 대비 최대 관측 절대 잔차 `2.220446049250313e-16` | `coding_evidence/C7.json`, `C7_oracle_residuals.json` |
| C8 | 두 크기의 합성 benchmark 및 동일 입력 재실행 결과 일치 | `coding_evidence/C8.json` |
| C9 | 최종 코드·수식·실제 C6–C8 증거의 독립 읽기 검토 PASS_SCOPED; 새 수치 실행 0회 | `INDEPENDENT_REVIEW.json` |

C6 최초 실행은 8개 통과와 AST guard 개수 기대값 오류 1개를 기록했다. 선택 기능과 실패 정리에 각각 guard가 있다는 사실에 맞춰 테스트 기대값을 고치고 CSV handle을 닫은 뒤 관련 2개 사례를 통과했다. 생산 코드는 C5 이후 바뀌지 않았다. C6–C7은 부분 overlap, 가까운 서로 다른 knot, 부호·영점, 교환 대칭, 중복 knot 삽입, norm 부등식, 단위·좌표 스케일과 저장 순서를 따르는 비단조 Tgas를 확인했다. 시험용 상대 `1e-12`, 절대 `1e-14`는 동결된 합성 비교 기준이다.

판별용 합성 spike는 영인 reference와 candidate knot `[0,0.50025,0.5005,0.50075,1]`, 값 `[0,0,1,0,0]`이다. `j/1000`의 1001개 표본은 모두 0이지만 PL supremum은 **1**, L1은 **1/4000**, 제곱 적분 I2는 **1/6000**이며 단위 구간에서 L2=RMS=`sqrt(1/6000)`이다. `probe/synthetic_sampling_gap.png`는 이 합성 반례를 명시한 그림이다. 실제 H/He 관측 결과와 구별된다. R7의 별도 endpoint-formula probe에서 관측한 최대 binary64 잔차 `4.440892098500626e-16`과 C7 생산 구현의 잔차는 서로 다른 실행 결과다.

| C8 단일 observable 합성 입력 | wall [s] | CPU [s] | 추적된 추가 메모리 peak [bytes] |
|---|---:|---:|---:|
| 이력당 2,000 knots | 0.066804112 | 0.066775209 | 2,088 |
| 이력당 20,000 knots | 0.703806943 | 0.703218767 | 2,072 |

입력은 메모리 추적 전에 할당했고 process peak RSS는 14,592 KiB였다. 두 크기 모두 affine 기준값 L1=1, I2=4/3과 동일 입력의 정확한 replay 일치를 얻었다. 이 값은 해당 합성 실행의 비용이며 전체 loader는 두 이력을 메모리에 보유한다. 이번 단위의 실제 물리 원자료 읽기와 native solver 실행은 모두 0회다.

실제 FULL005 결과는 완료 commit `5e0becf8709215e7ec8cc482c933663b045c47f9`의 기존 후처리를 재사용했다. 기존 9개 그림은 원소 내 H/He ionic fraction, 실제 `ni/nb` abundance와 별도 electron panel을 포함한다. 시간은 z20 이후 경과 proper time이며 온도 축은 실제 Tgas의 저장 시간 순서를 유지한다. 전체 render는 wall 87.989959793 s, CPU 78.86205 s, peak RSS 222,785,536 bytes였고 Yi 추가 표시는 wall 12.646288412 s, CPU 11.854283 s, peak RSS 131,772,416 bytes였다. 누적 외부 후처리 debit은 103.79374452296179 s다. 이 9개 그림, strict 검증과 기존 scoped review를 다시 실행하지 않았다.

결과의 수학적 대상은 저장된 PL 이력 간 차이다. 보편적인 binary64 오차 인증서나 solver 정확도·시간/각도 수렴 판정을 추가하지 않는다. 매우 작은 제곱 적분의 underflow를 포함한 binary64 표현 범위가 남으며 비유한 산술은 거부한다. 전체 과학 판정의 HOLD와 SOURCE007 및 기존 canonical 연구 DAG의 소유권을 유지한다.

단계별 GitHub commit과 Dropbox·Drive 백업의 실제 응답은 `DELIVERY_LOG.json`에 보존했다. R1–R10 및 C1–C9의 GitHub publication과 두 백업 acknowledgment를 확인했다. C9 검토 코드 commit은 `e881b38951bc896c29d5ea57bb8fb1f2803873e1`이다. C10 최종 배포의 실제 상태와 이 보고서를 담은 commit·ZIP identity 및 두 백업 응답은 `DELIVERY_LOG.json`과 `DELIVERY_SUMMARY`에 기록된 범위를 따른다. 원격 파일을 다시 내려받아 byte hash를 계산했다고 주장하지 않는다.

다음 실행은 `HANDOFF_PROMPT.md`와 `NEXT_DAG.json`에 따라 기존 owner 측 원자료를 찾아 연속 진단을 한 번 수행하는 것이다. 원래 절대 deadline `2026-10-16T03:50:17.774070Z`와 누적 debit을 유지하고 `deadline_reset=false`로 기록한다. intake 시 남은 외부 상한은 196.206255477 s이며 현재 deadline까지 남은 시간과 이후 debit으로 실제 상한을 줄여야 한다. 입력 부재 또는 만료된 할당은 HOLD로 반환한다.
