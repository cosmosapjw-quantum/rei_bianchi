# Source009 실제 BASS 구간 이력과 abundance 그림

외부 업데이트를 반영한 source007/008을 이어, source009의 동일한 native adaptive solver로 signed Bianchi와 cold FLRW의 z20→19.8 이력을 실제 완료했다. 두 결과와 그림은 독립 검토에서 탐색 실행·표시·게시 범위의 PASS를 받았다. 전체 재이온화 목표 완료는 아니다.

| Case | accepted | tentative starts | RHS | wall [s] | 최종 Tgas [K] |
|---|---:|---:|---:|---:|---:|
| SIGNED_MINUS | 21429 | 64350 | 450474 | 236.346626 | 22.6959576757 |
| COLD_FLRW | 21430 | 64353 | 450501 | 235.489573 | 22.6966349278 |

두 case 모두 실제z19.8, 종료exit0, 재시작·재시도·cap 종료 없음이다. 42,861개 저장 상태를 그림에 모두 사용했다. Y_i=ni/(nH+4nHe), 전자는 별도 panel이며 baryon분모에 포함하지 않는다. 초기HeII/III 정확한0만 log표시에서 mask하고 floor를 만들지 않았다. proper time은z20 이후 경과시간이며 Tgas축은 시간순서를 유지한다. 초기8.098143045064857K의 조건부 scenario로 full005 REC 초기조건과 구별된다.

## 그림

- [SIGNED: proper time](presentation_001/results/SIGNED_MINUS_Y_vs_elapsed_time.png)
- [SIGNED: Tgas](presentation_001/results/SIGNED_MINUS_Y_vs_Tgas_chronological.png)
- [COLD: proper time](presentation_001/results/COLD_FLRW_Y_vs_elapsed_time.png)
- [COLD: Tgas](presentation_001/results/COLD_FLRW_Y_vs_Tgas_chronological.png)

## 검증과 비용

nativePASS잔차는 각 행에 저장된 기존 허용오차 안에 있고 ledgerFAIL은0이다. checkpoint의source/config/table/case/epoch·6개배열·counter와 종점이 일치한다. 전체 검산을 반복하지 않고 기존source006/007/008 및 source009의3개PASS control을 재사용했다. 첫source00910초 테스트fixture 실패59.368794901초를 보존한 뒤, 두fixture구간만 줄인 표적 재검사와 원래build를 통과했다. solver/물리/허용오차/실제z19.8구간은 바꾸지 않았다.

구현검증67.908259451초, 실제native471.836199354초, 표시3.838635557초: 합계543.583094362초. 실행별실제argv/exit/source/config/output/자원은 해당RETURN_CONTRACT에 있다. 전체native원시자료는 로컬에 보존하고 publicGit에는 compact검토·행수·hash·그림을 게시한다.

## 유지된 결손과 다음 단계

SOURCE007 시간 수렴과 SOURCE008 threshold표현 동등성 HOLD를 유지한다. 이 두 배경은 table공급 prescribed geometry이며 dynamically coupled Einstein/fullEoR/각도·에너지 수렴/D-isotope/absolute-IVP를 입증하지 않는다. unknown/tail/absolute-IVP null 경계를 유지한다. 다음SOURCE010은 같은source/binary/mode의local_target5e-6 두case를 NCP에서 실행하여 이baseline과 비교하는 별도 한정 민감도 실험이다. 64core활용완료를 주장하지 않는다.
