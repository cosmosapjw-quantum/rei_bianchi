# PHYS22 evidence ledger

| Claim | 근거 상태 | 직접 evidence |
|---|---|---|
| 실제 paired IC, source와 7개 source blob identity | Observed source | SOURCE_MANIFEST.json, PHYSICS_CONTRACT.json |
| PHYS21 scalar kernel과 local gas functional | Inherited closed input | inputs/PHYS21_REPORT_KO.md, inputs/PHYS21_DECISION_REVIEW.json |
| Cohort u²/u³, birth 적분, count/energy time jet | Derived + exact Fraction check | contributions/radiation/INITIAL_TIME_RADIATION_KO.md, INITIAL_TIME_SERIES_CHECK.json |
| 실제 H/w/T t³ 및 full t⁴ | Derived + Decimal80 local checks | evidence/initial_time_coefficients_v1.json |
| 실제 HeII/HeIII 첫 부호와 electron/temperature 분해 | Derived + distinct local implementation | contributions/gas/LOCAL_INITIAL_RESPONSE.json, evidence/INDEPENDENT_COEFFICIENT_COMPARISON.json |
| 온도 thermal functional | 식의 대수적 재표현 | PHYS22_REPORT_KO.md 식 (15)–(19), final reviewer |
| 최종 이론 채택 | Separate final reviewer | independent/DECISION_REVIEW.json |
| 유한시간 부호·remainder, native arithmetic equivalence | Not established | claim ceiling 유지 |

최초 실행은 52/52, 11/11, 21/21, 구현 비교 16/16 PASS였다. 항목 수를 독립 물리 법칙의 수로 세지 않는다. Source-exact-real Decimal과 binary64 local arithmetic의 최대 상대차는 7.71105352001234e-15다. 모든 실제 command와 exit code는 각 EXECUTION JSON 및 root auxiliary receipt에 있다.

문서 전사/단위 수정은 v1과 correction receipt에 남겼다. 과학 최초 실행 실패는 0, tolerance relaxation은 0이다. Portability replay의 실제 횟수와 환경은 별도 evidence를 따른다.
