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
- [기존 SOURCE009 abundance 그림 4개와 보고서](../bass_source009_20261016/DELIVERY_REPORT_KO.md): 앞선 local target 결과를 그대로 보존한다.
- [Dropbox와 새 PR 반영 기록](../external_update_intake_20261016_001/refresh_003/INTEGRATION_KO.md)
- [완료된 SOURCE011 진단](../bass_source011_20261016/DELIVERY_REPORT_KO.md): retained SIGNED_MINUS checkpoint의 마지막 24단계에서 실제 accepted-state residual/Jacobian을 측정하고 독립 검토를 통과했다. 전체 이력을 반복하지 않았다.

GOAL_DONE은 false다. 게시와 백업의 실제 readback은 별도 delivery receipt에 기록한다.

## 최신 데이터의 실제 abundance 그림

SOURCE010의 검증된 79,206개 상태를 모두 사용한 그림 4개를 추가했다. Native baryon-normalized H/He ion abundance와 전자를 분리한 log panel, 0을 포함하는 선형 elapsed proper time, 시간 순서를 보존한 Tgas 궤적을 사용했다. 정확한 0만 mask했으며 floor나 downsampling은 없다. 실제 plotting 1회는 exit0, 7.054737538 s였다. [독립 검토](presentation_001/INDEPENDENT_REVIEW.json)는 네 PNG를 직접 확인하고 게시를 승인했다.

| 구간 | 경과 proper time | 실제 gas temperature |
|---|---|---|
| SIGNED_MINUS | [그림](presentation_001/results/SIGNED_MINUS_Y_vs_elapsed_time.png) | [그림](presentation_001/results/SIGNED_MINUS_Y_vs_Tgas_chronological.png) |
| COLD_FLRW | [그림](presentation_001/results/COLD_FLRW_Y_vs_elapsed_time.png) | [그림](presentation_001/results/COLD_FLRW_Y_vs_Tgas_chronological.png) |

[실행·파일·input SHA 재계산 여부](presentation_001/RETURN_CONTRACT.json)를 기록했다. Solver·ledger·checkpoint 검산은 반복하지 않았다. 이 그림은 현재 conditional 구간의 저장 이력을 보여주며 시간·각도·에너지 수렴이나 전체 EoR 완료를 뜻하지 않는다.
