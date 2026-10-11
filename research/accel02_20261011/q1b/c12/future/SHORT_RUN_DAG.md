# 현재 할당 이후의 실행 DAG — 제안만 작성됨

현재 C2_FULL004 첫 chunk는 3개 새 attempt와 3개 accepted macro를 62.04116624 s에 처리하여 gen63, t=25482337810583.33 s에 도달했다. 이 시간은 해당 구간의 실측이며 전구간 ETA가 아니다. 이 문서는 현재 실행 할당·코드·상태를 바꾸지 않는다.

동결 schedule에는 208개 양의 mandatory endpoint가 있고 모두 PILOT02 gen3 이후에 있다. 현재 controller는 가장 가까운 hard event에서 macro를 끝내므로 하나의 accepted macro가 둘 이상의 미도달 mandatory endpoint를 넘을 수 없다. 따라서 최초 추가100-attempt 할당만으로 전구간 완주는 구조적으로 불가능하다. 관측한004 첫 chunk 시점에도206개가 남았다. 아래 추가100회 역시 유한한 다음 실행분이며 완주 보장이 아니다.

| 단계 | 선행 조건 | 실행·산출물 | 중단 조건 |
|---|---|---|---|
| A. 현재 할당 종료 | 현재 GO 범위 | 기존004에서 새 attempt만 수행; completedcap102+외부실패차감3=총105 유지 | 실제 실패, 미해결 inflight, 할당소진, 전구간 도달 |
| B. 동적 parent 확정 | A의 durable 상태 | 최신 committed journal과 accepted manifest를 선택; gen63으로 고정하지 않음 | 신규 실패·누락·identity 불일치 |
| C. 추가 할당 전환 | B와 명시적 prospective 채택 | **제안:** 총 물리attempt cap205, 차감3 유지 시 completedcap202; macrocap=선택시점 accepted수+100. 동일99 dependency·전체 prefix·cursor·kernel·output을 보존한 새 control identity | 기준·physics·source 변경이 필요한 경우 별도 후보 |
| D. 전구간 계속 | 새 child의 identity와 정확한 예산 확정 | 동일3-attempt/45s cooperative chunk, 각 accepted boundary·failure durable 저장 | 다시 cap 또는 실제 failure에서 명시적 결정 |
| E. 전구간 과학적 판정 | 각 필요한 전체 history 완성 | same-grid time9 및 C2/C3 full24 비교, 65/129 각각 own-fine-max 정상화 | 어느 gate든 실패하면 해당 원인만 진단 |

변경하지 않는 최종 기준은 time9의2e-6, spectral/angular24의1e-3, 최초 에너지·최초nH로 정상화한 각 ledger1e-9, geometry1e-11이다. 65와129 subset마다 각 field의 fine 최대값을 독립적으로 사용하며 fine 최대값이0이면 차이도 정확히0이어야 한다. 잔차·positivity·gas domain 검사는 모든 accepted boundary와 공통 output epoch를 포괄한다. Local source time1e-10, pairing/momentfit1e-12, opacity 및 direct/ABI heat own-component1e-7, native gas residual1e-11도 유지한다. Local controller defect는 전역 time gate를 대체하지 않는다.

B/C와 병렬로 가능한 작업은 다음 새 chunk의 source·opacity·gas·serialization 시간 및 bytes 계측 설계, C3와 시간정밀도 비교의 입력계약 준비다. 기존 완료 검산·h0·accepted trajectory는 재실행하지 않는다.

Checkpoint가 매번 길이n의 전체 prefix와 kernelmetadata를 다시 저장하는 현재 구조는 C개 cell에 대해 누적 O(n²C) 저장·검증 비용을 낳는다. 실제 wall time의 지배항인지 측정하지 않았으므로 별도 성능 lane으로 남긴다. 동일 차수의 leggauss node/weight 재사용도 먼저 기존 caching 여부와 새 구간 profile을 확인할 가설이며 측정된 속도 향상이 아니다. Incremental prefix 형식은 현재 완전한 restart 의미를 보존하는 별도 구현·검증 없이는 채택하지 않는다.

Reionization 과학적 admission, r≠0 Bianchi/angular comparison, 새 BASS receiver 실행은 각각 별도 의무다. CR/RCT OFF는 원래 lane의 완결을 뜻하지 않는다. 이 문서에서는 추가 코드·테스트·native 계산·할당 채택을 수행하지 않았다.
