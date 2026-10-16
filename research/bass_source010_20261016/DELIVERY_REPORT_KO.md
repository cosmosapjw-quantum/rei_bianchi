# SOURCE010 결과

같은 SOURCE009 source·ELF·초기조건·물리에서 local target을 `1e-5 → 5e-6`으로 줄인 두 NCP 계산을 완료했다. 범위는 **z20→19.8**이다.

| 구간 | accepted | RHS | native process wall |
|---|---:|---:|---:|
| SIGNED_MINUS | 39,624 | 832,569 | 872.08 s |
| COLD_FLRW | 39,580 | 831,672 | 852.04 s |

총 79,206개 상태를 저장했다. 두 native exit0, 각 26개 검사 통과, 저장된 공통 ln(a) 위 21개 관측량 비교도 한 번 실행해 exit0으로 완료했다. 전체 원시 출력 1,353개, 803,020,952 byte는 NCP와 로컬에 보존했다.

기존 이력과의 온도 최대 차이는 SIGNED_MINUS `0.000229520536635 K`, COLD_FLRW `0.000229182018014 K`다. 비교 대상은 LOCAL baseline과 NCP 계산이므로 **target과 실행 환경을 함께 바꾼 민감도 진단**이다. 이것만으로 시간 수렴 차수나 오차 상한을 정하지 않는다. 실제 accepted step 분포도 기록했으며 target 절반을 고정 dt 비율로 해석하지 않았다.

[독립 검토](INDEPENDENT_REVIEW.json)는 이 구간 결과와 진단의 게시를 scoped PASS로 승인했다. 전체 Bianchi 재이온화·시간/각도/에너지 수렴·isotope-native 반응망·dynamic Einstein coupling·64-core scaling은 미완료/HOLD다. Unknown/tail/absolute-IVP null을 유지한다. 기존 cargo fmt 실패와 Rust skipped를 green CI로 보고하지 않는다.

## 산출물과 다음 실행

- [실제 명령·source·설정·exit·자원·비교 결과](RETURN_CONTRACT.json)
- [21개 관측량 비교](comparison_001/COMPARISON.json)
- [기존 SOURCE009 abundance 그림 4개와 보고서](../bass_source009_20261016/DELIVERY_REPORT_KO.md): 경과 proper time과 실제 Tgas에 따른 H/He/전자 이력. SOURCE010에서 새 그림을 그렸다는 주장은 하지 않는다.
- [Dropbox와 새 PR 반영 기록](../external_update_intake_20261016_001/refresh_003/INTEGRATION_KO.md)
- [다음 frozen 실행 계약](NEXT_AUTHORITY.json): retained SIGNED_MINUS checkpoint에서 남은 24단계의 accepted-state residual/Jacobian을 관찰한다. 전체 이력을 반복하지 않는다.

GOAL_DONE은 false다. 게시와 백업의 실제 readback은 별도 delivery receipt에 기록한다.
