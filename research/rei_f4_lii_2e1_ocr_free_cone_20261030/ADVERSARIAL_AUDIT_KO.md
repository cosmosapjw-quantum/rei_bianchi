# F4 한정 blind-referee-style 적대적 검토, 1회 수행

이 감사는 **동일 모델/동일 작성자가 반례·범위·정규화를 공격적으로 검토**한 결과다. 실제 native subagent/독립 작성자 referee는 사용할 수 없었다. `R6_distinct_author=NOT_RUN`, `C9_distinct_author=NOT_RUN`. 다른 저자의 검산을 가장하지 않는다.

| 대상 | 적대적 finding | 실제 반례·검증 | 교정/판정 |
| --- | --- | --- | --- |
| Source identity | OCR ordinate 도입이면 'OCR-free' 위반 | `hat`, `step` 구축 때 A_TAB 참조 없음, parent witness에서만 사용 | source-*ordinate*-free 한정, PASS_SCOPED |
| 단조성 | 양의 spectrum이면 단조라고 오판 가능 | single hat j1, z20 P2=0 vs Cmono min .567724678 | 단조성 별도 조건을 명시, 비단조 positive cone 병렬 유지 |
| Source time | epoch마다 최적 spectrum 교체 | 원본 저장 193 epoch 통합에 한 기준 `j`만 사용 | generator history를 먼저 통합하고 min/max, PASS |
| 비선형 observable | covariance TV에 선형 극값을 적용 | covariance, TV는 p의 비선형 함수 | 이들 한계 claim NOT_RUN |
| PDF 원전 | 표 글자 OCR 불확실 | Windsor bitstream 403, CHIANTI 파일 raw 미확보 | original glyph source BLOCKED_INPUT, 제시한 정확 문헌/URL 요청 |
| Formally certified | source-cone sharp=finite quadrature certified 오판 | 8/16 numerical max~1e-15 | exact convex math + numerically checked payload만 인정 |
| Radiation | 동결 광자 흡수=실제 CMB τ 오판 | 임의 proper L=c/H, 무각도·비자기일관성 | actual RT/thermal/CMB HOLD |
| Review provenance | self-review 독립성 과장 | subagent spawn API 없음 | true distinct-author R6/C9 NOT_RUN |

결론: 새 finite-cone 수학은 source-ordinate 정량값 없이 완성되었지만, 원본 Drake 표 이미지와 물리 source closure가 확정되지 않았다는 결함은 현 F4 상위 노드의 진짜 blocker로 남는다. 새 strong no-go theorem은 제기하지 않았다.
