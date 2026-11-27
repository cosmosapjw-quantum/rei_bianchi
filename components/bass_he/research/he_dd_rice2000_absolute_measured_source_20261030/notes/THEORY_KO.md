# BASS_HE / PR125: Rice 2000 절대 \(^{4}\mathrm{He}(\gamma,dd)\) 실험자료의 전자기 상세평형 및 birth-kinetic 연구

## 1. 권위와 identity

- 기준 부모: `cosmosapjw-quantum/BASS_HE` PR124, HEAD `9696297205c2560bd8bdfc8d72b8b80b86fae8d3`, 사용자 제공 문헌 PDF의 SHA-256은 `sources/USER_FILE_IDENTITY.json` 참조.
- 고정 원전: Rice et al., *Phys. Rev. C* **61**, 064612 (2000), Table I (paper p.4), Table II (paper p.5), DOI `10.1103/PhysRevC.61.064612`. Rice (1998) Duke PhD thesis, Table 5.1 (supplied PDF p.115), preliminary distinct source **not independent experiment**.
- 최초 사용자 제공 `X4R8587_x4.zip`은 EXFOR `M0826`, Arkatov 1972 `M0826002`/`M0826003`의 요청 응답이며 **Rice 실험자료가 아니다**.
- 논문 PDF 바이너리는 저작권을 존중하여 Git에 게시하지 않는다. 원문 SHA 및 표를 수치 전사한 최소 사실 데이터만 Git에 둔다. 별도 개인 복원 ZIP에는 사용자 업로드 원문을 보존할 수 있다.

## 2. 실험적으로 확립된 것

Rice 2000 Table I에서 150–190 MeV 6각도, 190–250 MeV 6각도의 **절대 differential cross section 12개**를 얻었다. 단위 nb/sr; 표에 함께 제시한 불확실성은 순수 통계이다. 추가 systematic은 각각 7.1%, 13%. 같은 6개 telescope, 같은 실험 캠페인, 동일한 산란 사건의 대칭 반사점은 추가 독립 측정이 아니다.

Rice 2000 원문의 식 (1) 및 Section IV는 동일한 최종 중수소 2개 때문에 `sigma_tot = 2*pi*A0`를 명시한다. 따라서 표의 미분단면적은 전방/후방을 라벨로 세는 angular density에서 물리 사건 총단면적을 얻을 때 정확히 1/2이 들어가는, Rice 자기규약으로 해석할 수 있다. 이를 모든 EXFOR 실험의 κ가 확정됐다는 뜻으로 일반화하지 않는다.

Rice 1998 Table 5.1에는 같은 mid-energy 6각도의 수치가 있으나 학위논문 표의 DA는 2000년 논문보다 대략 1.21배 작다. 시험 원본 PDF는 139쪽으로 끝나며 Table 5.2·이후 부록이 없다. 차이의 원인(재정규화 또는 분석 수정 등)은 확인되지 않았다. 출판본을 SSOT로 채택하고 둘을 평균하거나 독립 자료로 결합하지 않는다.

## 3. 상세평형의 정의와 정확한 유도

원래 동결된 PR104 rest-energy 컨벤션: `M = M_alpha*c^2 = 3727.3794118 MeV`, `m = m_d*c^2 = 1875.61294500 MeV`, `Q=2m-M=23.84647820 MeV`. Metric `(-,+,+,+)`. 광자 입사, 핵 정지계에서 `s=M²+2M Eγ`, 두 최종 중수소의 CM 운동량에 c를 곱한 `q²=(s-4m²)/4`, 광자의 CM 에너지 `k²=(s-M²)²/(4s)`이다.

비편극, 미시적 시간반전 대칭, ordered final d angular density로 정의한 `dσ_photo^ord/dΩ = S/(64π² s) (q/k) (1/2)`, 입사 중수소 두 개를 spin 평균한 포획 `dσ_cap/dΩ = S/(64π²s) (k/q)(1/9)`를 조합하면

`(dσ_cap/dΩ)/(dσ_photo^ord/dΩ) = (2/9)(k/q)²`.

광분해의 **full sphere event angular density**를 `dσ_photo^event=dσ_photo^ord/2`로 정의하면 `dσ_cap/dσ_photo^event=(4/9)(k/q)²`다. 이 factor 2는 광분해 최종 identical-particle 사건 계수이며, homogeneous gas dd의 초기 입자쌍 collision rate에 도입하는 별도 `1/2`과 같은 객체가 아니다.

실험 두 에너지구간의 각 점은 **구간 적분된 단면적**이다. 위 `R(E)`는 정확한 *단색광 같은 s* 관계일 뿐이며 E=170 또는 220 MeV에 측정한 것처럼 곱하는 것은 잘못이다. 수학적으로 같은 비음수 E가중을 두 방향에서 공유한다고 **추가 가정**하면 `min R(E) * σbar_photo ≤ σbar_cap ≤ max R(E)*σbar_photo`. `R(E)=(2/9)(s-M²)²/[s(s-4m²)]`의 도함수는 양의 E에서 한 번 영이 되며, 동결 질량의 변곡 E*=48.46766015 MeV보다 큰 150–250 MeV에서는 단조 증가한다. 따라서 구간 endpoints가 엄밀한 전환계수 extrema가 된다. 실제 실험 detector response 및 역반응 beam의 E가중 일치는 **미검증**이다.

`Eγ∈[150,190]`: ordered capture/photo ratio `[0.01969430946060728,0.02352067279700519]`; `Eγ∈[190,250]`: `[0.02352067279700519,0.02906493972499857]`. 이러한 변환 bounds를 부여한 수치는 원전의 직접 포획 측정값이 아니다.

각 photon event에서 생성되는 중수소 두 개의 총 birth kinetic energy는 정확히 `K1+K2 = Eγ-Q`다. 따라서 두 구간에서 각각 `[126.1535218,166.1535218] MeV`, `[166.1535218,226.1535218] MeV`의 source-supported kinematic *support*만 판정할 수 있다. 중수소의 물질 내 감속·침적·열로의 변환과는 별개다.

## 4. 원전 데이터로 검증한 systematic 오류 예산

Rice 1998 Sec. 3.6.1의 체계적 비율: photon-energy reconstruction/cut 3.3%, PID 4.6% (mid)/11.7% (high), target effective length 2.0%, target density 2.5%, tagging efficiency 2.8%. 논문의 사양과 동일하게 quadrature 합산하면 7.08096%/12.87905%로 Rice 2000의 7.1%/13%와 정합이다. 이는 논문 저자의 방법을 재현한 것이지, 12 관측치의 실제 joint covariance를 확보한 것은 아니다. `C_sys=null` 보존.

## 5. 자동 blind referee에서 발견한 source-internal 문제

Rice 2000 Table II의 `150–190 MeV, unconstrained, P2 only` 행은 `A0=1.31±0.07 nb/sr` 및 `σ_tot=8.32±0.40(stat)±0.65(sys) nb`를 기록한다. 같은 논문 식 `σ_tot=2πA0`를 적용하면 8.230972752... nb로, 저자가 인쇄한 8.32 nb와 차이 0.0890 nb이다. A0 두 자리 표기만의 반올림 오차로 설명하기 어렵다. `7.1% × 8.32=0.59072 nb`도 인쇄 `0.65 nb`와 다르다. 원문의 내부 불일치가 확인됐으며 **원문 수치를 수정하지 않고** `FLAG_SOURCE_TABLE_DISCREPANCY`로 유지한다. 나머지 7개 적합 행은 2π A0가 주어진 반올림 자리수와 정합이다.

이 문제는 Table I의 실측 12행과 그 오차를 무효화하지 않으며, 하나의 fit model 옵션에 특유한 검산 의무다. 출판사의 정정(erratum)이나 저자의 원본 피팅 파일이 확보되기 전까지 원인을 확정하지 않는다.

## 6. 물리적 적용 게이트

`R_event=null`, `heat_rate=null`, `kappa=null`, `L4=false`, `production=HOLD` 유지. Rice의 원본 12행 확보로 `RICE_ABSOLUTE_SOURCE_BLOCKED`만 닫혔다. 실제 He 고유계 photon phase-space `nγ(E,Ω,t,x)`, He4 target `nα`, 상관·편극/acceptance 별 source, nonthermal D stopping/deposition 및 `C_V`는 여전히 미충족. Global Central DAG=28/88, HE physical DAG=14/18; 새 source-qualified micro-DAG 3/3만 완료.
