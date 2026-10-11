# Q1B9 이동 threshold의 positive quadrature

기존 N1/Q1B의 power-law closure와 authoritative N/U를 유지하고, native threshold/R에서 probability panel을 분할하는 positive quadrature를 구현했다. 각 panel의 양성 가중치를 모은 뒤 하나의 exponential tilt로 동일 N/U를 맞춘다. 표현 불가능한 panel과 threshold side는 typed failure로 반환한다.

실제 저장 IC moments에서 세 cell(12,17,34), 세 epoch(0,T/2,T), 두 angle의 18개 collisionless-redshift operator fixture를 평가했다. 새 IC/source 적분이나 gas RHS/history 실행은 없다. 별도 제조 bath의 absorption map은 기존 물리 초기상태를 바꾸지 않는다.

첫 실행은 exit0, 306개 검사 통과다. Decimal80 truncated step-kernel의 최대 상대차는 1.02661e-10, 실제 native split reference는 5.10910e-9, GL64/128 absorption 값은 6.50952e-10, number/energy pairing은 5.10e-16 이하다. 기존 unsplit rule의 새 fixture 진단 차이는 최대 0.00113870으로 기록했다. 기존 결과·실패를 덮어쓰지 않았다.

관측 실행: native1, SIGMA90/13824 energies, positive absorption maps36; wall1.760246458 s, 합산 child CPU1.259180 s. 이전 누적에 더하면 native17, SIGMA790/176976 energies, CELL121, unit05 이후 FP64 maps185, Decimal maps76, 측정 wall54.084825930 s, 알려진 CPU51.845727 s다. 미측정 overhead는 UNKNOWN_NOT_ZERO다.

RESULT SHA256: d4e4d6ac776f213aea013731b3e8d889ab8bee2dec673ab21e45387eb145bc16. 실행 계약·원시 stdout/stderr·STARTED·실제 exit는 evidence/attempt1에 있다. 별도 독립 판정은 INDEPENDENT_REVIEW.json으로 기록한다.

범위는 위 18개 quadrature/absorption fixture다. full-field spectral/time convergence와 CR-first/global physical admission은 HOLD다. scoped PASS 이후 다음 실행은 같은 N1 모델 전체 C02의 실제 source를 포함한 한 substep trial이다.
