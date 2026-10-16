# V10 독립 과학 검토

결정: **제한된 실험 결과 게시 PASS; source-on 2차 시간 수렴 HOLD**.
2026-10-16의 별도 Astra 연구 심사는 원시 archive SHA-256
`822f176dabb2d554abfabd6c13cff5779b8ff35e541e62d1d8724d27b1aa1a32`,
최초 빌드 실패와 수선 로그, 51개 완료 이력, Rust 표적 시험 13/13 PASS,
원본 owner와 `legacy_be` N8 첫 41열의 바이트 일치를 확인했다.
이는 전체 production 경로·checkpoint 재개의 동등성 판정이 아니다.

51개 CSV의 모든 행을 독립 재계산한 최대 절댓값은 광자 수
`1.006e-21/H`, H 사건 `1.755e-13/H`, HeII/HeIII 사건 각각
`7.07e-17/H` 미만이었다. 직접 photoheating과 광자·binding 재구성 차이는
`2.88e-20 eV/H`, escaped radiation 성분합은 `5.50e-18 eV/H`,
thermal 성분합은 `7.37e-11 eV/H`, binding 성분합은
`2.39e-12 eV/H` 이하였다. 평균 absorber의 photo 사건 보정과 RR/DR
제거·midpoint 재삽입은 이 실험에서 부호와 회계를 유지했다.

온도 self-difference 차수는 원래 BE `0.99999`, 전체 수정군 `0.99991`,
방사선 제거+RR midpoint `0.99998`이다. N128 대 같은 군 N2048 차이는
원래 BE `2.19987e-4 K`, 전체 수정군 `2.17669e-4 K`이며, 광자 수 차이는
각각 `1.93654e-11/H`, `5.16479e-13/H`이다. RR midpoint HeIII의 미소
차이는 반올림 영역이므로 차수를 채택하지 않는다. 독립 source-on 연속
RHS 정확도는 측정하지 않았다.

PR #167 donor patch에는 failed `fixed_step` 비용 누적 변경도 포함된다.
이번 성공 이력의 과학 값에는 영향이 관측되지 않았으나 실패 실행
accounting은 심사 범위 밖이다. 영수증의 source SHA는 최종 재현 소스의
identity이며 모든 이전 빌드의 개별 identity를 뜻하지 않는다.

심사가 요구한 유일한 수정은 DAG의 source-off CI/CE/free-free/CMB 시간
배치 시험을 GL2 source-age에 종속시키지 않는 것이다. 이를 독립
`READY_AFTER_CONTRACT` 노드로 고쳤다. 관측된 HI collisional-excitation
cooling은 약 `1.552e-3 eV/H`로 RR 냉각보다 크지만, 이 사실만으로 시간
오차의 지배 원인을 확정하지 않는다. 다음 최소 계산은 source-off thermal
시간 배치 분리다. Source-on GL2와 matched control, full EoR, Case-B
재수송, signed Bianchi의 주장은 HOLD다.
