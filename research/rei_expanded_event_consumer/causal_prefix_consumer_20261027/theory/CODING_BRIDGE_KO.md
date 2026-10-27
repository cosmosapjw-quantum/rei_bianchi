# R9 정식 결과와 코딩 연결

식은 consumer.closure, window, feasible, endpoint_range, basis_si, joint_map, quotient, clock_averages, endpoint로 연결한다. Source book은 validate_book, scalar binary64와 rational값은 interval/rational/read_ratio가 처리한다. 상세 대응은 implementation/IMPLEMENTATION.md가 최종 코드에 맞춰 기록한다. Source4개와 exactbinary64·rationalcoef identity는 implementation/INPUT_MANIFEST.json에서 고정한다.

원자료 크기는6source×7horizon×2reward이며252scalarwindows를 전수 확인한다. 동일 연속window126개에 대해 실제 canonical bin marginal 합과 prefix range를 비교한다. 두endpoint oracle은 별도 inequalities/corners로 계산하고 extremizer를 원래 모든 interval/cap/monotonicity에 대조한다. Actual36bin map, raw source rationalcoefficients, 겹침·중복·cumulative extra event 거부, 양수 normalization·binwidth domain을 검사한다.

Exact fraction 결과와 outward binary64 enclosure를 함께 저장하며 zero row는 exact0이다. FD는 동결한 feasible witness에서2방향step과 상대잔차2e−8을 사용하며 max(1,scale)형식의 floor를 쓰지 않는다. fullJacobian 또는 source horizon derivative 인증을 주장하지 않는다.

실행은 C5의 수정 후 독립 GO, 실제 manifest, root의 명시적 start 후 단1회다. 새로운83·NCP·IVP·producer solve·projection·quadrature·oldfullsuite는 자동실행하지 않는다. 실제 raw결과를 C7/C8/C9에 재사용하며 같은 검사를 장부 때문에 반복하지 않는다.

