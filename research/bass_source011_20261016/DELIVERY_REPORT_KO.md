# SOURCE011 실제 잔차·Jacobian 진단

외부에서 독립 검토된 비선형 오차 진단 모듈을 현재 native 실행에 연결했다. SOURCE010 SIGNED_MINUS의 고정 checkpoint에서 **마지막 24 accepted 단계만** 실행하고, 실제 수렴 상태의 유한차분 Jacobian과 잔차를 관찰했다.

- native RHS 504회와 관찰용 288회를 별도로 계상했다. 새 계산 총량은 792회다.
- 전체 72개 chemical stage 중 마지막 adaptive comparison의 FULL/FIRST_HALF/SECOND_HALF 세 packet을 분석했다. FULL trial은 최종 trajectory로 채택되지 않은 branch임을 구분했다.
- 끝점의 물리 상태·여섯 photon 배열·ledger·native counter를 포함한 측정 항목 6,185개가 기존 결과와 비트 단위로 일치했다. H/s는 직접 새로 저장한 표본이 아니므로 null과 provider 기반 추론을 구분했다.
- 세 stage의 국소 EOS 온도 보정 절댓값은 최대 `3.3226e-14 K`, 최종 trajectory stage는 `+3.3210e-15 K`다. 이는 그 세 chemical stage의 선형화 진단이며 전체 이력의 오차 상한이나 기존 민감도의 원인 판정이 아니다.

초기 구현 검토에서 RHS 한도의 호출별 적용 결손을 발견했다. 첫 HOLD와 source/ELF를 보존하고 한 번의 표적 수정을 했다. 기존 2개 명령에 명시적으로 승인된 2개 보충 명령을 더해 총 4개 명령, `30.309731820 s`를 계상했다. 실제 suffix는 `0.253145756 s`, 분석은 `0.201828702 s`였고 모두 exit0이다. 원래 총 시간과 절대 마감은 초기화하지 않았다.

[구현 재검토](INDEPENDENT_IMPLEMENTATION_REVIEW_AFTER_REPAIR.json)와 [실제 결과 독립 검토](INDEPENDENT_RESULT_REVIEW.json)는 이 진단·재현 대응·게시를 scoped PASS로 승인했다. 기본 solver의 물리식·허용오차와 일반 checkpoint 정책은 유지했다. 새 source/ELF identity는 기존 SOURCE010과 별도로 기록했다.

## 재현과 연결

- [정확한 명령·입력·source·출력·자원 기록](RETURN_CONTRACT.json)
- [실제 세 stage 분석](results/analysis_001/ANALYSIS.json)
- [외부 자료 재조사와 적용 경계](../external_update_intake_20261016_001/refresh_004/ADOPTION_REVIEW.json)
- [최신 abundance 이력 보고서](../bass_source010_20261016/DELIVERY_REPORT_KO.md)

전체 signed Bianchi 재이온화, 시간·각도·에너지 수렴, isotope-native 반응망, 64-core scaling은 미완료다. GOAL_DONE=false이며 unknown/tail/absolute-IVP null을 유지한다. 기준 cargo fmt 실패와 Rust skipped는 green CI가 아니다.
