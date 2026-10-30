# Same-author blind-style hostile review, Ferrett direct ratios / BASS193

실제 외부 blind reviewer 또는 native subagent 검증이 아니다. 이번 연구 구현자가 '다른 작성자라면 어디를 공격하겠는가'를 기준으로 한 **한 번의 한정된 적대적 검산**이다.

1. **BLOCK_CLAIM, 선행 PR289 데이터 레이블:** Table IV triplet partial σ는 완전한 순수 직접 계측량이 아니다. Table II p.35 footnote a,c에서 R_p와 R31 평균 연장 가정을 확인했다. **최소 수정:** 모델 의존 RC/TableIV을 쓰지 않고 직접 R31(80..92.5), R32(80..99)의 공통 구간으로 f3S를 재구성. source image 검증 성공.
2. **BLOCK_CLAIM, singlet 비식별성:** n2_rest=1S+1P+3P로 분리되지 않았다. **명시적 반례:** `f1S=0,f3P=f_rest,f1P=0`과 `f1S=f_rest,f3P=0,f1P=0`은 동일한 R31/R32를 준다. 따라서 `[0,frest]`만 허용. 모델 근사로 순수 singlet 양의 하한을 만들지 않는다.
3. **SOURCE_OWNER, 이중 단면적 owner:** BASS의 1s native σ와 1987 n2/n3 부분 σ는 동일 한 해의 kernel이 아니다. 통계적으로 꼼꼼한 비율이더라도 source-common chemistry / full rate는 미완료. **수정:** conditionally reweight on frozen BASS only; actual event rates/thermal source 주장은 HOLD.
4. **NUMERICAL/UNCERTAINTY, 1σ 직사각형의 과대해석:** R31/R32 사이 covariance와 세 중간 bin의 보간오차가 원전에 없다. **수정:** marginal ±숫자 범위의 수학적 box image로만 결과 표기; 확률적 신뢰구간 또는 정밀도가 확립된 측정 불확도라는 해석 금지. 전 구간 93–99 BASS bin 입력 배제.
5. **ENERGY, 실험 1987 χ와 현대 NIST χ의 차이:** 1987 Table I `1S 66.15 eV`, NIST 계열에서 66.314 eV. **수정:** 에너지 장부는 단일 원전 historical χ만 사용하고 출처 차이를 분명히 표시. χ_n2_rest/χ_n3 불확실성과 ratio box 네 극점을 모두 점검.
6. **DOMAIN, 외부 channel 종속:** n2+n3 합은 실제 모든 K-event 단면적과 동일하지 않음. p.16 논문 자체가 2s valence와 n≥4를 무시한다고 설명. **수정:** conditional n2+n3 partition으로만 호출. `χ_n2_rest`는 1S+1P+3P만, n3는 Table I 특정 네 채널만.
7. **VALIDATION, source/coding:** user raw PDF byte lock, PR289 full source ZIP SHA, PR289 parent event-parity, 193 epochs×3 energies×2 isotope, exact channel sum, positive K, Wolfram derivative & closure, negative SHA tests. **사실 상태:** 21/21 Python targeted PASS, native external distinct-author R6/C9 NOT_RUN.

**판정:** 직접 비율을 이용한 실측 지지 photon-bin source history와 초기 photoelectron kinematic bound만 scoped-admit. 실제 gas heat, M1/2E1 emitted/absorbed photons, production, CMB τ, real Bianchi angle-resolved transport와 canonical DAG completion 미허용.