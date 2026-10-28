# R3 주장·전제 정렬

각 case/source 대안을 별도로 고정한다. source identity에는 operator, bath, projection, source-z가 포함된다. time basis는 comoving proper seconds, frame은 bath-frame rest target이다. 두 finest case와 세 source-z2.316/2.479/2.649의 곱은6대안이며 이들을 합한 이력이 아니다.

각 scalar reward N[cm^-3] 또는 E[eV cm^-3]의 동일한 누적량을 F_i라 한다. T=(0,1000,10000,100000,300000,1000000,10000000)s, i=0…6. raw supplied finite binary64 endpoints의 exact represented 값을 L_i,U_i로 해석한다. P_U는 supplied all-time upper bound다.

P={F | L_i≤F_i≤U_i, 0≤F_i≤P_U, F_i≤F_(i+1), F_0=0}.

입력 전제는 유한 endpoint, L≤U, 엄격히 증가하는 시간, exact-zero 첫 horizon, 같은 case/source/operator/bath identity다. 모순을 clipping으로 지우지 않는다. P의 sharpness는 저장된 interval·단조성 정보에 대한 것이다. 실제 fixed-K semigroup trajectory 집합의 sharpness나 continuum error bound를 주장하지 않는다.

P_N×P_E는 미공급 N/E 의존성을 포함하지 않는 outer information set이다. Reservoir들은 이 공통 pair를 공유한다. 두 scalar interval의 모든 corner를 같은 물리 pulse가 달성한다고 해석하지 않는다. 개별 source alternative와 cumulative view도 추가 사건으로 합산하지 않는다.

Provider의 physical injection/history, recipientnb, pointwiseRHS, spectrum, exposure, stopping은 null이다. b=1.4e6m^-3, b_i=b(1+i/20), manufactured eta 및 방향 벡터는 인터페이스 검증 fixture이며 actual source 조건과 구별한다. 원래 native25를 유지하며 diagnostic photon port2개를 추가한 직렬화는 새27state ODE가 아니다.

