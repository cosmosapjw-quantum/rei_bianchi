# REI-PHYS23 현재 상태

## 연구 결과

- Task: SPECTRAL_INITIAL_RESPONSE_AND_THERMAL_SIGN.
- 과학 phase: 완료. 별도 최종 decision reviewer의 판정은 PROMOTE_SCOPED / research PROMOTE / physical HOLD.
- 남은 필수 과학 수정 0; 추가 과학 검산 요구 0.
- 주 결과: 실제 HI-only 열린 에너지 구간 전체의 HII·heat·50000 K 온도 초기 t^3 계수 음수; 정확한 r 단조성; 모든 허용된 양의 spectrum으로 음의 부호 전달.
- HeIII t^4의 약 15.43367 eV 전환과 같은 N,U의 반대 부호 반례는 inherited numerical Jnp에 조건부.
- 보고서 PHYS23_REPORT_KO.md와 RESULTS_SUMMARY.json, CLAIM_DAG.json을 final decision이 고정 SHA로 채택함.

## 검증과 재현

- 최초 새 exact main: 31/31 PASS, exit0.
- 최초 새 direct-FD numerical main: 65/65 PASS, exit0.
- 과학 code/result/tolerance는 최초 성공 뒤 변경 없음.
- 후보 32-file freeze 유지. 초기 SOURCE_MANIFEST task label만 동결 전 정정했고 원본과 correction receipt 보존.
- 별도 portability: 새 두 PHYS23 main만 각각1회; exit0; 원래 JSON과 실제 raw bytes까지 같음. 추가 독립 물리 검산으로 합산하지 않음.
- 완성 archive의 최종 fresh local restore/verify-only 및 remote ACK/tree/blob 증거는 archive에 수반되는 detached PHYS23_PUBLICATION_RECEIPT.json을 따른다. Local restore를 full remote restore라고 부르지 않는다.

## 입력과 보호

- Input commit: e334866a4ac1be963f573c0b35182d25eb4d666b.
- Scientific Rust src tree: cb69b4736dd046e4675557577eb8e0ead037d1f3.
- [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED.
- Native0, gas IVP0, closed PHYS19/20/21/22 scientific replay0, source/default/runtime 변경0.
- Same branch additive docs publication만 허용된 closeout 범위이며 merge는 포함하지 않음.

## 다음 단일 질문

- PHYS24_FIXED_MOMENT_HEIII_ENVELOPE.
- 같은 N0와 평균 에너지 아래 HeIII 초기 응답의 최솟값·최댓값과 부호 강제 영역.
- PHYS24_NEXT_HANDOFF_KO.md가 최소 읽기와 완료 기준. PHYS24는 미실행.
