# R10L 이후 독립 검토용 bounded prompt

Repository cosmosapjw-quantum/BASS_HE PR17을 fresh-fetch한 뒤 R10L EXECUTION/20260930T081637Z의 REPORT_KO.md, DECISION.json, BENCHMARK_MANIFEST.json, MODEL_CONTRACT.json, QUERY_CONTRACT.json, RAW_COMPARISON.json, INDEPENDENT_FINAL_REVIEW.json, BACKUP_RECEIPT.json을 읽는다. 실제 publication identity와 package MANIFEST를 검증한다. Git 문서 subset을 전체 historical package 복원으로 표현하지 않는다.

S1 PDF는 Dropbox id:BSpOijBcT10AAAAAADwi-g /BASS_DERIVATION_DOSSIERS_20260912/PhysRevA.81.052704.pdf, SHA256 e544c755ef76841fa161bb16f64073bd9e698c0bdebd009ffccf5e9728f45ffb, 693837bytes다. 원문은 private로만 회수하고 Fig8 END solid curves와 Minami open symbols를 구별한다. 두 독립 추출의 최종 union uncertainty를 사용한다. S2 SHA256 d111275b1225e8d128f80c1188daf9b7eef9bddf8dad350db44a25c989dba81b의 TableII/HSCC 마지막 열과 Fig3을 독립 확인한다. Ecm=.8 EkeV/u의 He4/H1 approximation을 별도로 유지한다. S3 원문이 회수되면 5keV/u tabulated values의 method 열만 검증한다. 0.5keV/u 외삽은 금지한다.

우선 source-series/energy/unit/uncertainty와 5keV/u n2 S1/S2 discrepancy를 source-bound로 검토한다. 동일 energy/shell의 독립 계산이 다른 모델 근사를 사용한다는 사실을 숫자 평균으로 숨기지 않는다. R10L C의540 신규 exact Delta와540 기존 exact-pair reuse,345 rho/3 endpoint leaves/60 endpoint queries,18개 numerical component gate를 저장 기록만으로 재합산한다. 새 Delta/contour/rotation integration은 실행하지 않는다.

A는 locked R10K AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION control, B는 F2-RHO/EXTENDED/straight-CPC, C는 B의 support만 REAL인 모델이다. raw ratio/log를 출처별로 유지하며 지원 radius fitting, exponent/trajectory/cutoff/tolerance 변경, 새 interpolation/refinement, production 수정, CODE-I02 재감사, Eq55 production, 56-action/worker/R1/R2, author FORTRAN, C_S_AT/MODKG, L2/Krawczyk는 금지한다. 허용된 physical verdict와 수치 gate를 별도로 반환한다. 새 설계/추가 계산이 필요하면 연구 thread의 새 계약을 요청한다.

Frozen gates: CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
