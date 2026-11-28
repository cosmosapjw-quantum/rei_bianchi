# B1 수치 기록 독립 검토

판정: **PASS_BOUNDED_RECORD_REVIEW — 수치·메타데이터 안전성 확인 범위 내 차단 사유 없음.** 이는 전체 B1 권위성 폐쇄 또는 1,131개 값의 전수 재전사를 뜻하지 않는다.

수치 CSV 1,131행, matrix 13행을 확인했다. source/table/row/column key의 중복은 없고, CSV가 인용하는 서로 다른 원자료 8개의 SHA256은 v3 파일과 일치했다. 전체 행은 interpolation, frame conversion, new shell sum을 `NOT_RUN`으로 유지한다. 원자료 추출 전체 및 과학 테스트는 재실행하지 않았다.

P04 PDF8의 실제 page image를 열어 Table A3의 원문 5 keV/u 및 cm² 단위를 확인했다. n=1, 2s, 2p, n=2, 두 published-total 행의 24개 값을 CSV와 대조해 일치했다. Lab/CM 미지정과 H(1s)의 P01 교차 출처 귀속이 보존돼 있다. 기존 P01 추출 서론에서 Minami의 H(1s) 계산 귀속도 확인했다. AOCC-A는 원문으로 가져온 Toshima 자료라는 점, n=1–20 quantum total의 CTMC top-up 의미도 별도로 기록한다.

P08 PDF5의 실제 page image를 열어 Table II의 두 native 20 keV 행 16개 값을 대조해 일치했다. 단위는 10⁻¹⁷ cm²이며, 5 keV/u로 자동 변경하지 않는다. 질량수 A=4 convention은 조건부이고 n=2/n=3 합을 새로 만들지 않는다. 해당 page에 151-state n=3의 신뢰성 한계가 명시돼 있어 큰 basis를 자동 상위 기준으로 삼지 않는 metadata가 타당하다.

P09의 300개 ε token은 무차원 basis-convergence 진단이며 통계 표준편차로 쓰지 않는다. ScienceDB 743개 cell은 cross-section 단위·frame 미확정 때문에 admission이 막혀 있으며 native grid에 정확한 5 또는 0.5 token이 없다. IAEA proton 자료 2개는 matrix에 배제 상태로만 남고 He²⁺ CSV에 섞이지 않는다. P04 errata는 이전 table indexing 오류를 정정하지만 v3와 미전사 범위를 보존한다.

낮은 우선순위였던 `P08_verified_cells.json`의 render 경로 문제는 `P08_page5.png`로 수정되어 닫혔다. 실제 packaged image는 직접 열어 확인했다.

최종 B1 RESULT·VERIFICATION·CLAIM_LEDGER·handoff도 제한된 범위에서 대조했다. `PRIMARY_NUMERIC_AUTHORITY_MATRIX_PARTIAL`, `SOURCE_AUTHORITY_UNRESOLVED`, `global_authority_closed=false`, `G1_authorized=false`와 다음 A1b가 일관된다. 작성자의 portable verification은 15개 source identity·1,131개 cell·13개 matrix 행의 PASS를 기록하며 이를 독립 실행으로 표현하지 않는다. 이 검토자가 직접 재해시한 범위는 수치 CSV가 참조하는 원자료 8개다.

이 검토로 G1, collision 계산, frame adapter 또는 전체 authority closure를 승인하지 않는다. 나머지 문헌의 모든 방법 세부사항과 미전사 표의 전수 재검증은 범위 밖이다.
