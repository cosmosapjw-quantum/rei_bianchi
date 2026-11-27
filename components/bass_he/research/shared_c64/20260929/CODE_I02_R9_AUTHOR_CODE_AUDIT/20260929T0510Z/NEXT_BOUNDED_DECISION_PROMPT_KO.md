# 다음 bounded decision prompt: author-code normalization 결과의 정책 해석

고정 근거: R9 `AUTHOR_SOURCE_MANIFEST.json`, `STATIC_DATA_FLOW.md`, `NORMALIZATION_CROSSWALK.json`, `EQ43_IMPLEMENTATION_FINDING.json`; Mendeley DOI 10.17632/n43srxwdnm.1 Version 1의 provider ZIP/arseny.f SHA256. CPC PDF의 R8 페이지 감사는 별도로 보존한다.

결정할 명제는 좁다. 배포된 author SECTION은 STCKLBR2가 저장한 값을 factor-two exponent로 행렬에 넣는다. 이는 인쇄 Eq.(55)의 지수와 맞고 Eq.(52)의 factor-one 행렬 정의와 충돌한다. 그러나 author SECTION은 impact-parameter Delta grid의 첫 표본만 사용하며, Eq.(43) gap 근사는 구현하지 않는다. 이 두 제한을 과학적 claim 및 재현성 판단에 반영하라.

SOURCE(인쇄식), AUTHOR-CODE(정적 식), DERIVED(정규화 해석), BENCHMARK(과거 수치), OPEN(원인)을 분리해, (1) Eq.(52) 호환 lane 유지 여부, (2) factor-two standalone analysis lane의 허용 범위, (3) 향후 clean-room Eq.(50) 정책 변경을 위한 별도 검토 조건을 제안하라. 변경이나 실행을 이 prompt에서 승인하지 않는다. 원문 FORTRAN을 clean-room source로 복사하지 말고, author code를 실행하거나 재현 benchmark로 승격하지 마라.

현재 판정 `CODE_I02_CLOSED=true`, `full_certificate_fail_closed=true`, `scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`을 그대로 보존한다.
