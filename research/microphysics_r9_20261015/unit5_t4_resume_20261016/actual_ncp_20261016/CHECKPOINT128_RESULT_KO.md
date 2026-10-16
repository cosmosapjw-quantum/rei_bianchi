# R9 Unit5 실제 NCP 재개: 128차 중간 단계

승인된 새 allocation에서 기존 64차 checkpoint를 재생 없이 복원했다. 재구성 3회, cache 표본 3회, 64→128 연장 64회로 새 H 작용은 정확히 **70회**다. 기존 Unit4의 만료 기한과 terminal 작용 `UNKNOWN [86,160]`은 유지하며 캠페인 총량은 `[156,230]`이다.

복원 seam scaled 오차는 3.545e-15, Hamiltonian 재구성 9개 gate와 cache 3개 표본은 모두 PASS였다. 128차 Gram 오차 1.049e-13, ground leakage 4.144e-16, 질량 오차 2.220e-16을 포함한 내부 gate도 모두 PASS였다. 가중치 합은 W=0.4243608179922081이다.

| η (Eh) | spectrum L1/W | max CDF 변화/W | window 질량 변화/W | 기준 0.001 |
|---:|---:|---:|---:|---|
| 0.05 | 0.0768174 | 0.00368889 | 0.000768741 | HOLD |
| 0.10 | 0.0319647 | 0.00140951 | 0.000391403 | HOLD |
| 0.20 | 0.00747651 | 0.000266958 | 0.0000954086 | HOLD |

128개 Ritz node는 약 0.145751–45.659683 Eh에 있다. 최대 가중치 node 0.400506 Eh의 잔차는 1.624e-13 Eh이나, 다른 상위 가중치 node는 최대 약 0.420 Eh의 잔차를 보인다. 유한공간 refinement 미달은 물리적 no-go가 아니다. 결합 들뜬상태를 포함하므로 W는 이온화 확률이 아니며, continuum·electron capture·완전기저 closure는 별도 의존성이다.

이 S1 시점에 잔차 그리드와 최종 supervisor 영수증은 실행 중이다. 완성 checkpoint와 단계별 raw는 [Drive](https://drive.google.com/file/d/1Evtyw3O7KK85JkVfMK37LgS0dGFAVRyV/view), Dropbox `id:BSpOijBcT10AAAAAAD-X9g`에 이중백업했다. archive SHA256은 `3c279a2c35b317b477a309f5cefe06058e1785ceda609d93bf03cf3982f46503`이다.
