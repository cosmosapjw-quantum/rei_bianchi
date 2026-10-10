# ACCEL02 phase2 독립 의미론 검토

현재 판정은 **HOLD_NATIVE_HISTORY_QUANTITATIVE_GATE**다. 에너지 좌표·Jacobian·event 처리에 선언한 물리 모형을 바꾸는 오류는 발견하지 않았다. 그러나 EVENT001은 photon-number ledger 기준을 통과하지 않았고 시간·스펙트럼·각도 수렴은 아직 판정하지 않았다. 구현/시험설계에 관여하지 않은 별도 검토자가 코드와 저장된 증거를 읽었으며 새 solver 실행은 없다.

U_i=E_i(t)N_i에서 λ_i=H+s(3μ_i²−1)이므로 Udot_i=E_i S_i−(κ_i+λ_i)U_i이다. 코드의 photon diagonal, gas 1/E 변환, absorption counter κ/E, redshift-work EV λ 항은 이 식과 맞는다. energy ledger는 이 좌표에서 state와 counter의 선형 결합이고 photon-number ledger는 ΣU/E(t)를 포함한다. 따라서 E오차가 roundoff 수준이어도 N오차는 독립적으로 검사해야 한다. EVENT001의 common-epoch N최대오차4.06436×10⁻⁸는 기존1×10⁻⁹ 기준을 넘는다.

고정 q의 continuous source는 매 stage 현재 에너지에서 평가된다. physical E>50keV인 특성선은 initial/source가 모두0일 때만 정확히 dormant로 제외되고, source entry 이후0초기값으로 활성화한다. source birth를 interval 끝에 몰아 full-step 흡수시키던 chronology와 다르다. 저에너지로 redshift된 photon은 삭제하지 않는다. event knot13.60/24.59/54.42는 actual Verner cross-section cutoff이며 binding ledger의 더 정밀한 χ와 구분되어 있다.

event endpoint의 one-sided 값은 열린 구간의 스펙트럼 branch를 선택한다. 에너지 조정은64binary64eps 이내로 제한되고 EVENT001 관측 최대값은3.92×10⁻¹⁶이다. 유한 상태 clipping이나 guard 삭제가 아니며 현 scoped convention으로 수용 가능하다. 한편 four-point monotonicity sampling만을 임의 geometry의 전역 증명으로 주장하면 안 된다. 선택된 expanding Bianchi background에서만 이 event 구성의 의미가 성립한다.

마감 전에 두 acceptance 표현을 바로잡아야 한다. 첫째, driver의 ledger boolean은 segment endpoint만 본다. 이미 저장한 common epochs에서 maxE는5.32374×10⁻¹¹로 endpoint4.67311×10⁻¹¹보다 크고 maxN도조금 더 크다. 최종 ledger 판정은 적어도 endpoint와 common-epoch 두 집합의 최대를 함께 사용해야 한다. EVENT001의 FAIL자체는 이 수정으로 바뀌지 않는다. 둘째, 모든 accepted step의 photon positivity는 실제로 검사하지만 gas fraction/temperature domain은 Newton RHS stage guard로만 확인한다. 저장129epoch의 gasdomain은 정상이나 모든 accepted gasstate의 strict positivity 주장과 동일하지 않다. 해당 accepted-state 근거를 추가하거나 주장 범위를 정확히 제한해야 한다.

NATIVE001의 실제 저장된 실패는 required step size below floating-point spacing이다. 50keV entry에 근접했다는 진단은 root의 별도 원인 분석이며 rawfailure와 구분해야 한다. NATIVE002/EVENT001 whole15.9→4 완주는 실제 진전이지만 과학 승격이나 N2 DONE을 뜻하지 않는다. EVENT002와 prospective refinement evidence가 도착하면 변한 증거만 판정하면 된다.
