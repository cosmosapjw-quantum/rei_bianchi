# R10J 결과: Appendix-A와 비교하던 support가 달랐다

R10I 기준 commit은 8a240af8f490a9fe519a15b837d9678bfed53405다. 전체 WRN 행렬은 비동등이고 현재 H(1s) 입력에서 소비하는 m=0 열은 동등하다는 판정을 보존했다. 접근 단계의 reversible/absorbing 차이도 이 입력에서는 receiving upper state가 비어 있어 결과를 바꾸지 않는다. 이는 32개 active mask의 도달성과 1,000개 수치 대조로 확인했다.

새 source finding: 배포 arseny.f의 1191행은 최종 RB slot에 Re(Rc)를 저장한다. 1593행 JRO=JRQ가 그 slot을 선택하고 1903/1977행의 gate가 이를 소비한다. Appendix-A p.18도 LESS THEN RE(RC)라고 출력한다. 반면 본문 Eq.(52)와 현재 clean-room은 Re(Rc)+Im(Rc)다. 원 author source SHA256은 96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78이다.

같은 R10G frozen Delta(0), factor2, Coulomb/author-cutoff rotation을 두고 support만 바꾸는 실제 수치 probe를 실행했다. 안쪽은 고정 9구간 GL32/64/128, 바깥쪽은 회전이 I이므로 구간별 해석적 적분이다. 실제 2,016 rho 평가, Magnus 102회, DOP853 102회, 새 Delta/contour 0회였다. 36성분의 successive-order gate와 R10G baseline을 통과했고 exit0이다. 테스트는 행동 RED3 후 focused42 PASS다.

| E keV/u | n | EXTENDED / Appendix | REAL / Appendix |
|---|---:|---:|---:|
| 0.5 | 1 | 4.9487566641 | 0.9987843524 |
| 0.5 | 2 | 1.9654812426 | 1.0004155392 |
| 0.5 | 3 | 1.0895028087 | 0.9999977190 |
| 5.0 | 1 | 4.9486109253 | 0.9988334131 |
| 5.0 | 2 | 2.3578669417 | 0.9999794620 |
| 5.0 | 3 | 1.2431437500 | 0.9992359265 |

All-six multiplicative RMS: 2.8001741333 -> 1.0007748316.
Dominant n2/n3 RMS: 1.7478122217 -> 1.0004352047.
Extended baseline과 R10G의 최대 shell 차이: 3.95684e-12 a0^2.
회전 eta128/256 최대차: 6.71671e-9; eta256/DOP853: 4.48200e-10.

Q23 outer annulus의 조건부 정확식은 pi*(b_ext^2-b_real^2)*p*(2-p)다. 이 고리만으로 기존 frozen n2 초과량의 99.9737%/100.3398%에 해당했다. 전체 REAL-support 비교는 inner support 변경까지 계산한 위 표이며, 고리만 빼서 전체 결과라고 부르지 않았다.

이 결과는 source-support 누락이 frozen benchmark 잔차를 설명한다는 정량 증거다. author FORTRAN 실행, 원 author action discretization과의 identity, 실험적 검증, 어느 support가 물리적으로 더 좋은지는 주장하지 않는다. 기존 COUL_AUTHOR_FROZEN이라는 명칭은 partial author settings였으며 complete-author reproduction으로 해석하면 안 된다. 예전 수치와 failure는 수정하지 않았다.

다음 R10K는 제공된 전체 실행 ZIP의 제한된 독립 검토와 최대 한 번의 0-Delta 재생이다. GitHub에는 이 문서 subset만 게시하고 full runner/fixtures/tests/logs는 DELIVERY_RECEIPT.json이 가리키는 immutable ZIP에 둔다. package를 새로 구현하지 않는다.

CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
