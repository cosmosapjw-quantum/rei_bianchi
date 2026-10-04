# 독립 검토 경계

이번 검토는 새 이론 유도와 실제 `hhe_rhs`·provider를 호출하는 additive adapter, 명시적인 광자 bin 경계, 유한 cells 평균 및 그 실행 증거를 대상으로 한다. 기존 FLRW01·원자율·Peebles의 변경 없는 과학 suite는 되풀이하지 않는다. 최종 판정은 실제 산출물을 읽은 뒤 `REVIEW.json`에 별도로 기록한다.

국소 분율식은 핵수 continuity를 제거한 뒤 얻는 식이어야 하며, 순수 H에서 전자밀도는 `nH*x`다. 코드에 이미 존재하는 fixed-electron oracle와 혼동하지 않는다. actual event source와 photon loss의 primary absorption owner가 같아야 한다. Case-B 계수를 기존 `hhe_rhs`에 공급했다는 이유만으로 기존 Case-A toy의 thermal/escaping-energy output까지 OTS 열회계로 인정하지 않는다.

평균은 `X_V=<x>`, `X_M=<nH*x>/<nH>`, `Q_V=<I_ionized>`를 구별한다. 고정 comoving volume weights, 공통 H, 공통 핵수 dilution을 전제로 한 유한 ensemble 계산은 검증할 수 있다. 움직이는 phase geometry나 다른 expansion field가 있으면 별도의 경계·Reynolds/covariance 항이 필요하다. `X_M=Q_V*dI`의 미분에는 `Q_V*dot(dI)`가 남는다. supplied `Q_V,dot(Q_V)`로 inventory defect를 계산하는 도구는 독립적인 ionization-front solver가 아니다.

물리 frequency 또는 energy에 대한 proper spectral photon density는 conservative form에서 `3H*nE + dE(-H*E*nE)`, expanded form에서 `2H*nE-H*E*dE(nE)`를 갖는다. bin 적분 뒤에는 proper `3H` dilution이 있고 comoving 적분 뒤에는 없다. 고정 물리 threshold에서 lower-edge flux는 loss, upper edge는 inflow다. 내부 경계의 telescoping과 실제 within-bin spectrum의 edge reconstruction은 서로 다른 검증이다.

재결합 광자 ownership은 세 가지를 분리한다: Case-A primary-only, Case-A explicit diffuse, Case-B local OTS. 같은 ground recombination photon을 effective Case-B sink와 explicit emissivity 양쪽에 넣지 않는다. escaping energy에서 photon number를 추론하지 않는다.

최종 검토는 scalar 식의 재기록에 그치지 않고 실제 호출 경로, 독립 expected event/average/flux, 잘못된 모델을 넣었을 때의 검출, finite 실행 결과와 scope를 확인한다. 가벼운 trajectory가 추가되면 각도·열·source·초기값·단위·적분방식·step refinement를 명시한 연구 예제로만 인정한다. 이 검토로 F04, 물리 provider admission, 엄밀 uniform error, EoR history 또는 general Bianchi RT를 승격하지 않는다.
