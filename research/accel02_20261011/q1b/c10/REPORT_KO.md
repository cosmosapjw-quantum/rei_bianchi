# REI-ACCEL02 C10 — C09B 후속 결과

C09B의 `Q1B_SOURCE_ENTRY_POSITIVE_STEP`에서 재개하여 C2 양의 source-entry/native gas 단계와 새 C3 검증을 병렬로 수행했다. C3 초기조건 격자 비교, source/흡수 연산자, 실제 native gas 결합 및 실제 checkpoint 복원 후 다음 상태의 동일성을 검증했다. 전구간 scientific admission은 아직 부여하지 않는다. 최종 독립 판정은 `review/INDEPENDENT_DECISION.json`이 권위 있는 범위 판정이다.

중단 전 미게시 C10 파일은 작업 환경 정리로 유실되었다. Git C09B `3581a236`와 해시가 일치하는 백업을 복구하고 386개 manifest member 및 두 native binary를 확인했다. 유실된 새 C10 작업만 다시 작성했다. RUN002·EVENT003·Q0·Q1A 및 이미 완료된 C1/C2 검산의 재실행은 0회다.

| 항목 | 실제 결과 | 허용 범위 |
|---|---|---|
| C3 source / IC | 최대 2.24664e-15 / 3.88069e-15, 기준1e-12 | 저장된129/65 reference에 대한 새 C3 적분만 |
| C3 / 직접 UVB opacity | 최대1.88141e-6 | 초기 z15.9만 |
| 저장 C2 / 새 C3 opacity | 최대6.17443e-5 <1e-4 | 348×2 cell C3와 C2의 초기조건 쌍 |
| C3 셀 실행 | 696셀 완료, 실패0; SIGMA1248회 | native gas/history 실행 아님 |
| Source-entry | 양의 시간적분, 물리적 redshift work 및 zero-state 구현 | source-only; 임의 photon seed 없음 |
| 양의 흡수 | 공통 moment-fitted 가중치, 실제 native sigma, K0/KE/heat/counter 일관성 | backward-Euler 국소 연산자 |
| 수정 후 실제 C2 결합 | 공통 종료시간1e11 s의1·2·4단계, 총7개 accepted boundary | FLRW 초기의 유한 구간만 |
| 실제 결합 ledger | 에너지/초기에너지 최대3.72931e-12, 광자수/초기nH 최대1.90208e-19 | 모두1e-9 이내; 전구간 증명 아님 |
| 실제 checkpoint 복원 | 2.5e10→5e10 s의 다음 gas/N/U/counter/support/R 상태 차이0 | 같은 코드·입력·시간표의 다음 경계 재현 |

Source 시간적분의 별도 prospective 기준1e-10은 유지했다. 첫 h=1e10 s는 통과했지만 5e9 및2.5e9 s는 각각 최대2.75e-10 및3.14e-10의 quadrature disagreement로 거부됐다. 1e11·5e10·2.5e10 s의 source-only 계산은 통과했다. 더 큰 시간 간격의 source 계산 성공이 결합 시간오차의 성공을 뜻하지 않는다. 실패 원본과 코드·입력 identity를 보존했다.

독립 검토에서 K0와 KE 각각의 수렴만으로 작은 차이 KE−chi*K0인 photoheat의 수렴을 보증할 수 없다는 결함을 확인했다. 실제 반례에서는 K0 오차0, KE 오차2.875e-8이 기존1e-7 검사를 통과하지만 heat 오차3.383e-5는 넘는다. 동일 가중치의 직접 heat 적분과 native ABI의 차이식 각각에1e-7 검사 및 상호 일치 검사를 추가했다. 새7개 focused test가 통과했고, 변경 전 코드와 최초 결합 실행은 별도 원본으로 남겼다. Photon seed·clipping·threshold 이동·provider 교체는 없다.

수정된 연산자로 수행한 실제 공통 종료시점 비교는 시간 민감성을 보였다. 2단계/4단계의 국소 정규화 차이는 xHII1.785e-4, T2.543e-4, photon number2.601e-5, GammaHeI5.073e-2, xHeIII3.61457e-1이다. **이 분모는 초기의 한 종료시점 값이다. 전구간65/129 시점에서 각 field의 fine 최대값으로 정규화하는 기존 scientific 기준의 분모와 다르다.** 따라서 이 결과를 전구간 time FAIL, 모든 가능한 h의 불가능성, 극미량 HeIII의 국소 ppm 정확도 필요성으로 승격하지 않는다. 정규화 보정 해석은 `evidence/NATIVE_ENTRY_NORMALIZATION_ADDENDUM.json`을 우선한다.

현재 HOLD의 근거는 production 시간오차 제어·endpoint/precision 전략과 전구간 측정이 아직 완성되지 않았다는 점이다. 알려진 source 정밀도 거부를 회피하려고 시간을 키우거나 허용 기준을 낮추지 않는다. 반대로 임의의 더 엄격한 초기 한 점 기준으로 장시간 연구를 무기한 지연하지도 않는다. 다음 단계는 고정된 solver 오차 scale과 cell-relative 정밀도 표현을 설계하고, 그 변경분만 국소 검증한 뒤 실제 전구간65/129 비교로 판단하는 것이다.

물리는 기존 non-tilted axisymmetric Bianchi I test-field, 현재 r=0, HM12 emissivity RHS/초기 UVB, 조건부 T20K/xHII2e-4/neutral-He, 10–50000eV source, H/He primary Case-A 및 signed prescribed CMB exchange 그대로다. CR/RCT/secondary는 OFF_noncompletion이며 원래 확장 lane을 보존한다. BASS의 기존 reduced N4 채택은 유지하고 새 native receiver 호출은0회다.

`NEXT_DAG.json`과 `HANDOFF.json`이 현재 다음 작업을 지정한다. 원래 전구간 계약 파일은 actual checkpoint의 identity에 포함되어 수정하지 않았다. 단계별 checkpoint와 첫 실패는 Git 및 Drive/Dropbox에 보존하며 업로드 확인과 실제 원격 복구 검증을 구별한다. 이번 C09B 복구는 실제 다운로드·해시 검증까지 수행했고, 새 C10 백업은 별도 표기가 없으면 upload-verified다. 기존 unrelated repository verify의 cargo fmt 실패를 이번 targeted 연구 검증의 성공으로 바꾸어 보고하지 않는다.
