# REI age-exposure/source-age 현재 상태 | 2026-10-19 pair-search 배송

진입: 이 파일, `RESEARCH_UPDATE_20261019_PAIRSEARCH_KO.md`, `HANDOFF_CODEX_CURRENT_KO.md`, `contracts/NEXT_DAG_CURRENT.json`, `DELIVERY_RECEIPT_CURRENT.json`. Repo cosmosapjw-quantum/rei_bianchi, draft PR199, branch research/rei-age-exposure-envelope-20261018. 이번 실제 intake HEAD ee3b6c8014bcb21e6d4c9ef3a3560dc40df61309. 원 native physics 35d9747a0bbedcafdb568467ce7c1e7a25f965b6.

## 새 실행결과를 먼저 확인했다

Drive·Dropbox 최신 B1/B2를 각각 전체 readback하여 네 SHA/크기/CRC를 검증했다. B1 payload161/161 및 case output131/131 PASS. 이미 끝난 q0 age64 block-max(NCP exit0, 19,756 RHS, 782.731 s)와 spectral128은 반복하지 않았다.

- age64 photon 2.002711130429069e-10, energy 1.929660553608937e-13: 기존 1e-8 gate PASS. 정확 Fraction 재합산도 PASS. age 수렴성과 RMS dilution 인과 판정은 HOLD.
- spectral64→128 He I 누적 photoevent 0.2660778682%: 기존 유한 이웃 결과만 재사용.
- age64 source jumps는 MISSING_DATA. 기존 18 관측 기록은 9 고유 상태다.

## 이번에 완성한 코드와 실제 검증

1. `--native-input-dir`: frozen153 inputs를 먼저 검증하여 동일156 prepared outputs 생성. none/count/기존pair 준비 identity를 정확히 보존.
2. `subnormal-pair` 및 `subnormal-pair-search`: 원래 실패 분기에서 정확 count base와 고정 node/positive support를 유지하며 원래 Kahan count·energy gate 모두 검사. exact dyadic interval, checked i128, 자원 예산과 비존재 범위 분리.
3. N2/N3 실제 셀에서 k1/k3 보정 성공. 변경된 N4 time8은 22.1506 s 후 새 16-node 셀에서 exit1. n10η, 양의 가중치10개 각각1η, 저장 energy246η≠목표245η, tol0. 현재 support·표현 아래 유일한 벡터이므로 이 셀은 그 범위에서 교정 불가. **native time8/16/32 HOLD.**
4. 명시적 age32 reference plan, passive binding-block telemetry, 실제 birth 전후 snapshot, 엄격한 source/runtime 비교, compact B1 자동 준비·binary 재사용 구현.
5. 실제 native birth2 OFF/ON 대조: 양쪽 exit0, 2.377/2.525 s, 각각1302 RHS. 저장 상태3개·endpoint·기존관측·ledger byte 동일. source jump2/2, tiny photon1.19296e-11, energy1.27900e-14 PASS.

신규 test methods는 native8 + S5 =13개이며 S 검토에서 기존 norm9개도 재사용 실행했다. 구현자와 reviewer의 같은 테스트를 unique 수에 중복 합산하지 않는다. N1/N3·N4·S 독립 검토 모두 범위 내 PASS. 전체 historical suite와24 prescribed-opacity 캠페인은 다시 돌리지 않았다. 실제 native RHS byte stream·모든 내부 adaptive step 좌표는 NOT_RECORDED로 남긴다.

## NCP READY: 한 사례

**q0 age32 block-max, binary64, source8/n_mu8/transport16/time1, 진단 ON, 1800 s cap.** 기존 age64 binary·계산 base·Python/NumPy/SciPy·48 transport threads를 맞춘 후 `age32-block-max-diagnostics`만 실행하고 기존 age64와 비교한다. 소스/실행 identity가 다르거나 실패하면 HOLD를 남긴다. 자동 age64 반복은 없다.

이번 NCP 도구는 실제 호출에서 월 사용량 중지 응답을 반환했다. NCP 실행은 NOT_RUN이며 compiler 부재·백업 연결 blocker는 상속하지 않았다. 복사 가능한 인계는 `HANDOFF_CODEX_CURRENT_KO.md`에 있다.

owner checkout, PR150/R9, LRS repo, 별도 BASS HHeD lane을 보존한다. PR은 draft, no merge, no force-push. **PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.
