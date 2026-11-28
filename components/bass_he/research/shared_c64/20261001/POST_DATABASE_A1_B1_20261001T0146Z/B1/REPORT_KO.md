# B1 원문 수치 권위 — 첫 부분 완료

판정은 `PRIMARY_NUMERIC_AUTHORITY_MATRIX_PARTIAL`이며 물리 비교 gate는 `SOURCE_AUTHORITY_UNRESOLVED`다. 13개 출처 행의 메타데이터를 정리하고, 원문 값 1,131개를 보존했다. ScienceDB 743개, P03 HSCC 9개, P04 63개, P08 16개, P09 300개다. P09 수렴 진단 300개는 별도 열이며 추가 단면적이나 통계 표준편차가 아니다.

Minami2008 Appendix A1–A12가 존재한다. A3(PDF8/인쇄7)는 **원문 5keV/u** 표다. 이전 v3에서 lettered appendix table을 놓친 색인 오류를 `SOURCE_RECOVERY_ERRATA.json`으로 정정한다. v3 자체는 보존한다. A3의 27행 중 비어 있지 않은 63셀을 전사했고, 빈칸은 0으로 채우지 않았다. n=1의 LTDSE/AOCC-A/AOCC-B/CTMC 값은 각각 1.95e-19/2.55e-19/2.33e-19/3.20e-17 cm²다. AOCC-A는 Minami의 새 계산이 아니라 Toshima1995 NIFS-DATA-26에서 가져온 열이다. 원문에는 lab/CM 명시가 없고, 초기 H1s는 P01 Liu2024 서론의 교차 참조로 연결했다. n1–20 quantum 총량은 원저자의 CTMC tail 보충을 포함하므로 순수 유한 껍질 합과 구별한다.

Winter2007 TableII의 20keV alpha 두 행은 원문 이미지에서 확인했다. 107-state와 151-state 각 8셀을 **20keV laboratory**로 보존했다. 20/4=5라는 질량수 규약은 조건부 관계로만 기록하며 에너지 열을 바꾸지 않았다. n2/n3 합은 새로 만들지 않았다. 저자가 151-state n3 포획의 신뢰성 문제를 설명하므로 상태 수만으로 우월성을 정하지 않는다. TableIV의 graphically interpolated 비교값은 권위 수치로 채택하지 않았다.

P03은 중심질량 에너지 eV의 4-channel HSCC n2 결과다. 4000eV를 자동으로 5keV/u로 바꾸지 않는다. P09는 원문 속도 축을 유지한다. 114개 표 중 Tables25–30만 전사했으며 나머지 108개는 미전사다. P07은 속도 표의 메타데이터와 격자만 확인했다. P10은 10–1000keV/amu 범위이고 단면적 결과가 그림이어서 5와0.5 자료로 쓰지 않는다. P22의 5keV는 3He 전체 입사에너지이므로 5keV/u와 다르다. IAEA proton 두 파일은 He2+ 자료에서 제외했다.

ScienceDB 네 파일은 각 열에 대응하는 에너지 격자를 따로 확인했다. 원문 Decimal 5와0.5가 모두 없으며, 원시 CSV의 단면적 단위와 frame도 미확정 상태로 유지했다. 이는 R10N의 해당 파일에 관한 기존 판정을 바꾸지 않는다. **검토한 제한된 표·격자에서는 admissible exact0.5keV/u를 확립하지 못했다.** 전체 문헌에 그런 자료가 없다는 주장은 아니다.

`code/verify_source_cells.py`는 source-root를 명시적으로 받아 원본15파일의 SHA256/크기, ScienceDB743셀의 원시 행·열, 보존된 PDF 전사 기록, 중복 키, 값 개수와 금지 작업 플래그를 검사했다. 결과는 PASS다. 이 검사는 원 논문의 물리 계산 재현이나 새로운 독립 PDF 전사를 뜻하지 않는다. `review/B1_INDEPENDENT_RECORD_REVIEW.json`은 별도 기록 검토다. 전체 solver·보간·curve digitization·새 shell sum·fitting·G1은 실행하지 않았다.

다음 단일 작업은 전체 패키지의 `NEXT_HANDOFF_KO.md`에 명시한 A1b다. B1의 단위·frame·정확 에너지 권위 문제는 후속 비교의 명시적 의존성으로 남긴다.
