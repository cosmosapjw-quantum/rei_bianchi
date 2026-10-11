# C11 정밀도·production 제어 연구 기록

이 문서는 진행 중 기록이다. 최종 과학적 승격이나 전구간 실행을 뜻하지 않는다. 출발점은 C10R4 `fbc28add1280166d939f096d322c61ca0e57cb49`이며 기존 입력·물리식·최종 허용 기준은 고정했다. 변경 코드는 모두 C11에 별도로 두었다.

## 새로 닫은 국소 문제

C10의 작은 source-entry 간격 실패는 같은 HM12 보간과 FLRW 배경 해를 `log1p/expm1` 및 cell-relative 적분으로 평가하여 교정했다. 초기 셀의 직접 offset 적분 D는 진단값이며, 저장되는 물리 상태와 native moment reconstruction은 여전히 binary64 N/U이다. 따라서 새로운 숨겨진 상태나 photon seed를 도입하지 않았다.

| 항목 | 새 수치 근거 | 의미 |
|---|---:|---|
| h5e9/2.5e9 source 시간 적분 | 최대 order-pair 차이1.3541e-15 | 기존1e-10 국소 기준 통과 |
| MP80 동일공식 born-cell reference | 최대 상대차1.4867e-15 | 해당 입력에서 독립 산술 검산 |
| Source/redshift pairing | 최대3.0104e-16 | 기존1e-12 보존 pairing 통과 |
| C10 실제 cold-process restart | 상태·counter·prefix 차이0 | 저장된 실제 한 경계에서 다음 한 경계; C11 증거 아님 |
| Native threshold trace | 새5테스트,8SIGMA | 좌우 value trace; endpoint Jacobian 미제공 |

Source API는 r=0에 한정한다. 비등방 모델에는 이 FLRW 산술을 묵시적으로 적용하지 않는다. 물리 provider와 임계값, 이온화/열화학의 chi 정의, CR/RCT/secondary OFF 상태를 바꾸지 않았다.

## 새 시간 제어와 실제 첫 실패

Fixed-scale positive step doubling은 full step과 two half steps의 차이를 측정하고, 통과하면 positive fine path만 채택한다. Richardson 외삽을 사용하지 않는다. 이온분율 단위1, 온도1e4K, 원래 nH reference, Gamma1e-12/s 등은 실행 전 고정한 **수치 solver 스케일**이다. 최종 과학적65/129 세트별 fine maximum normalization을 대체하지 않는다. 처음부터0인 trace HeIII에 현재 순간값 상대오차를 강요하지 않는다.

PILOT01은 처음 h5e9 trial의 measured error ratio4.1874(GammaHI)로 감소했다. 이후 midpoint t977363400.0610615s에서 borncell [50000,50000.00421957968]의 기존 generic `FLOAT_Q_COORDINATE_UNRESOLVED` indicator1.655359e-7가 기존1e-7을 넘었다. 5개의 새 map call,36gas RHS,2824SIGMA를 수행했으며 **accepted 경계는0개**이다. 부정적인 결과를 accepted history나 checkpoint로 승격하지 않았다.

실패점의 추가 진단은 source 소실과 mean rounding을 분리했다. MP80 source mean과 binary64 reconstructed mean의 차이는2.9021e-12eV이고, authoritative U/(RN) 대비 division rounding은1.3091e-12eV다. 작은 support offset 대비 상대오차와 native smooth-kernel의 물리 에너지 상대오차는 다르다. 이 차이는 새로운 provider-specific bound를 조사할 근거이며 기존 guard를 무조건 제거할 허가가 아니다.

## 다음 판별

실제 native cross section/heat의 같은 활성 구간에 한정한 조건수·curvature bound, 양의 공통 quadrature와 moment pairing, threshold-side와50keV cap provenance를 함께 검토한다. 성립하는 경우에만 새 native-only adapter를 구성한다. 기존 generic guard, C10 파일,1e-7 own-component opacity/heat 기준은 남긴다. 각 첫 실패, as-run source, 입력, 로그를 보존하며 수정된 경로에 대해서만 새 검증을 수행한다.

실제 accepted C11 상태에서 cold-process restart를 수행하고 독립 reviewer가 생산 실행의 국소 전제를 판정한 후에만 전구간15.9→4 C2/C3 및 같은 grid 시간 refinement를 시도한다. 국소 성공은 그 전구간 기준의 성공을 뜻하지 않는다.
