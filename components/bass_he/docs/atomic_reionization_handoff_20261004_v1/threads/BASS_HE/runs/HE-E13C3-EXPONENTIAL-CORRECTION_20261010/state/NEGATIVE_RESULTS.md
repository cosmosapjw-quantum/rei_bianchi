# Negative results and unresolved claims

새 scientific calculation의 첫 실행 실패는 없었다. Actual command 결과는 RUN_HISTORY.json과 contributor receipts에 있다.

## 확립하지 못한 것

- Uniform interval enclosure: variation integrals는 quadrature 추정치다.
- Exact original-model conservation: first variation에는 delta_Lambda*e1과 species residual이 남는다.
- Whole-interval positivity: endpoint 및 제한된 Decimal samples만 확인했다.
- Physical continuum budget와 receiver adoption: owner gate가 열려 있다.
- Controlled wall-time acceleration: 서로 다른 단계의 과거/현재 시간은 context다.
- 실제 atomic RCT photons/heat/recoil: null. 새로운 gas history, late stock, nonzero outflow는 실행하지 않았다.

## 문서 검토에서 수정한 사항

Captured midpoint와 exact continuum midpoint를 동일하게 표기하지 않도록 수정했다. 이에 따라 derivative bound에 h*abs(Lambda(m)-L)를 추가했다. 최대 상대오차가 여섯 macro aggregate에 대한 값임을 보고서 첫 문단에 명시했다. Numerical code/results 또는 사전 기준 변경은 없다.

Optional recompute wrapper는 fresh-output parity를 검사하지 않는다. REPRO-01 검토 후 출력 필드와 문서에 이를 명시했고, PASS_SCOPED를 저장된 증거 검증으로 제한했다. 과학 결과를 바꾸거나 옛 reference를 재실행하지 않았다.
