# REI physical fast F4 · 원본 BASS193 Li6 전하-불가시 jet 연구 보고서

## 무엇이 새로 진행되었는가?

직전 REI [PR274](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/274)는 BASS21 Li6/Li7 isotope lift, off-manifold forcing, 5개 실제 저장 endpoint 검산을 완료했다. 최신 [PR275](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/275)는 193 저장시점 × 35 반응 사건 = 6,755 source-native event 행을 생성했다. 이번 단위는 이전 결과를 다시 계산하는 대신 **원본 BASS 저장 궤적의 193개 시점에서 전하·동위원소 총량으로 가려지는 두 Li6 숨은 방향이 전자 source의 첫째·둘째 미분으로 구별되는지** 계산했다.

### 수학적 구성

`Y_i=n_i/n_b`, `q_Li=(0,1,2,3)^T`, `gamma=nu6/nu7`, `Y6=gamma Y7+delta`. 원본 BASS의 동일한 Li 동위원소별 전리·재결합 생성자 `M=UV Gphoto+ne Gne(T)`로 `delta_dot=M delta`.

`1^T V=q^T V=0`, `V=[(1,-2,1,0),(0,1,-2,1)]`는 2차원 양자수/전자수 불변 전하 redistribution basis. `h=q^T delta`로 놓으면 on-lift baseline에서 hidden perturbation에 대한 선형화 jet는

`h_dot=q^T M V alpha`, `h_ddot=q^T (M^2+Mdot) V alpha`.

`Mdot=H[UV_x Gphoto+ne_x Gne+ne T_x partial_T Gne]`, `ne_x=-3 ne+(nb/H) q21^T F21`. BASS 원본 source의 `nb_x=-3nb`, `T_x=11900 UV_x`, original UV tanh source. 실험과 달리 **관측량 자체**가 아닌 source 내의 *linearized local observability* 판별이다. `Mdot=0` frozen-rate 근사는 별도 가정이다.

`S=max|M_ij|`로 나눈 무차원 행렬 `O=[(q M V)/S; q(M^2+Mdot)V/S^2]`의 `det(O)` 부호를 비교했다.

### 실측된 original-owner 저장 데이터의 계산 결과

193개 source-native 상태 모두에서 국소 행렬을 계산했다. 80자리 mpmath가 *표현된 binary64 native source M/Mdot*를 다시 읽어 193개 행렬식 부호를 193/193 일치시켰고, double 대비 최대 절대 행렬식 차이는 **3.83e-15**였다. 193개 저장 시점의 determinant 값은 모두 0이 아니었다. 하지만 연속된 두 원본 저장 시점의 **서로 반대인 부호**는 정확히 5개 쌍에서 나타났다.

| 시점 i→i+1 | 부호 교차 redshift 구간 | 시간변화 source를 포함한 determinant 값 |
|---|---|---|
| 29→30 | 14.4943–14.6522 | -0.00977569 → +0.01182631 |
| 48→49 | 11.7804–11.9106 | +0.01179244 → -0.00432832 |
| 65→66 | 9.7576–9.8672 | -0.00490657 → +0.00089358 |
| 73→74 | 8.9198–9.0209 | +0.00647070 → -0.01708779 |
| 80→81 | 8.2405–8.3346 | -0.00336779 → +0.00040131 |

Frozen-rate determinant에서는 부호 전환이 3개 쌍만 나타났다. 이 차이는 물리적 전자/UV/온도 source 변화율을 생략하면 local 2-jet rank 진단이 달라질 수 있음을 나타낸다.

**보수적인 주장 한계:** 원본 BDF의 **저장된 점**을 재평가한 결과다. 원본 실제 continuous solution이 smooth이고 해당 end-point 부호를 따른다면, 중간값 정리로 위 각 구간에 적어도 하나의 zero-crossing이 있으나 본 연구는 미저장 경로의 엄밀 interval root finder를 수행하지 않았다. 특정 영점 위치나 실측 가능한 Li6 검출을 주장하지 않는다.

양수·핵종보존·전자중립 Li6 재배분의 실제 source 예제: `z=3.591836871`의 저장 원본에서 `epsilon=8.80026230446e-17` per baryon, `delta=epsilon*(0,1,-2,1)`로 양수 재고를 유지했다. 첫 순간 전자수 및 retained 17 상태 source 편차가 정확한 소스 수식에서는 0이다. 그러나 `q^T M delta=2.22917970534e-30` electrons/(baryon·s), 둘째 proper-time retained source L1 편차는 `4.33102324167e-47` baryon⁻¹ s⁻²다. 매우 작은 source-native counterfactual이므로 실험/우주 관측 예측값이 아니다.

### 검증, 반례, 수치 경고

- 원본 full PR275 ZIP SHA256 `de81a869f19f8ffd0db6b12f5bac5c93109f5804b691954c7ac0eae4f22df24b`, 원본 VigilODE PR121 ZIP SHA256 `19513fec19e53d5f2da8da50ba22aa066c634dee79ff94cff31d07b4cfb8f907`, original saved 193 NPZ SHA256 `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`, BASS atomic source SHA 확인.
- 직접 native `AtomicNetwork.evaluate`와 archived PR275 F/J 6개 시점 대조. RR/DR의 analytic `dGne/dT`를 5개 저장 온도에서 중심차분과 비교. 별도 사건 charge-current 식으로 `q^T M` 재검산, local `Mdot`의 source-input finite difference 4개 지점 검사.
- Python targeted **13/13 PASS**, mpmath80 **193/193 sign** 동일, Wolfram `1^T V=q^T V=0`, source generator `1^T M=0`, symbolic nonautonomous determinant correction 확인.
- 첫 테스트 전용 디버깅 오류는 `T≈100 K` 원본 하한 바깥으로 중심차분을 적용한 점과 지나치게 엄격한 절대 반올림 검사였고, source domain과 상대 반올림 bound로 교정했다. 증거와 실제 수정 기록을 보존한다. 물리 계수·원본 상태·검증 요구 허용오차는 완화하지 않았다.
- 본 단위의 새 IVP 0. 외부 193 stored original/source arrays는 불변. Native distinct-author R6/C9 `NOT_RUN`이고 GitHub repo-wide CI는 별도 상태 확인 전 PASS 미판정.

### 물리적 유효성·DAG

**BASS21 source 내부의 source-qualified 연구만 유효.** REI ON_refined 300 K chemistry는 BASS 21-state의 inventory, UV source, Li6/T/fast/nuclear/CR, electron pool과 clock source가 다르다. 이 분석은 실제 REI↔BASS full 21↔17 model source equality, physical Thomson tau, anisotropic CMB, posterior, production solver를 수립하지 않는다.

Original REI working **33/88**, central **28/88**, physical fast **4/7**; 새로운 원본 DAG 완료 **0**. F4 PARTIAL, L4 false, NO_MORE_IVPs true, NO_MERGE/NO_FORCE_PUSH. Scoped 18/20, 진정한 독립 R6/C9는 미실행.

### 다음 실제 물리 문제

다음 source-owner 노드는 `COMMON_OWNER_REI_BASS_FULL_ISOTOPE_ELECTRON_RATE_AND_CLOCK_BIND`. 동일 물리 계의 H1/D/T/He3/He4/Li6/Li7 재고, 전자 pool, REI 17과 BASS 21 full event rates, 실제 광자 및 thermal source, 기하학적 H, nHref/nb, K, proper-time/source clock, 일치 초기 조건을 연결해야 진정한 cross-repository F/J projection defect를 계산할 수 있다. 새로운 IVP는 별도 승인 및 물리 gate 전에는 실행하지 않는다.
