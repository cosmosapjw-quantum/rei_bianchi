# BASS21 저장 이력의 Li6 전하-불가시 두 방향과 국소 이차 jet

2026-10-30. **원본 REI F4 작업을 대체하지 않는 단일한 신규 source-native 연구 단위.** 원본 REI working 33/88, central 28/88, physical-fast 4/7, F4 PARTIAL, L4 false. 새 IVP 0.

## 실제 기준 데이터 및 물리적 범위

- BASS 원본 모델 commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`, BASS `AtomicNetwork` 파이썬 source 원본 SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`.
- VigilODE PR121 저장 원본 `trajectory.npz` 254301 bytes, SHA256 `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`.
- REI PR275 소스 포함 ZIP 3805828 bytes, SHA256 `de81a869f19f8ffd0db6b12f5bac5c93109f5804b691954c7ac0eae4f22df24b`. PR275는 193시점×35이벤트=6755행의 source-native 별도 결합을 이미 완료했음. 신규 IVP 수행 없음.
- 실제 저장 BASS source의 proper baryon density `nb(x)=nb(0)e^{-3x}`, `x=ln(a/a_start)`; `z=21e^{-x}-1`와 양수 `H(x)`. 원본 BASS UV 및 온도는 `Q=.5[1+tanh((7-z)/.8)]`, `T=100+11900Q` K. REI의 ON_refined 300 K bath/P19 photon source와 동등하다고 가정하지 않는다.

## 이론적 구성 및 새로운 판별량

BASS의 21개 핵종-전하 상태 `Y_i=n_i/n_b`에서 Li6 전하 분포 4차원과 Li7 전하 분포 4차원은 동일한 `(Z=3,q)` 전자 전이율을 갖는다. 전하벡터 `q=(0,1,2,3)^T`, `gamma=nu6/nu7>0`로 두고 `δ=Y_Li6-gamma Y_Li7`, 원본 BASS source의 생성자

`M(t) = G_photo,Li(t) + n_e(t) G_rec,Li(T(t)),   n_e=n_b q21^T Y`

를 쓰면 BASS **내부**에서 `δ̇=Mδ`. `1^T M=0`, 양의 전이율 => ||δ||_1 비팽창. 이는 PR266/274에서 확보된 원래 등식이며 이번의 새로운 주장은 아님.

전하·총핵종 재고에 영향을 주지 않는 2차원 숨은 부분공간을 다음 기저로 고정한다.

`v1=(1,-2,1,0)^T`, `v2=(0,1,-2,1)^T`, `V=[v1,v2]`; `1^T V=q^T V=0`.

원본 Li6에 `δε=V α`를 더하되 `Y6+δε>=0`으로 제한하면 **초기 retained 17종과 총 자유전자 수는 변화하지 않는다**. 그럼에도 전자 charge-sensitive jet의 첫째·둘째 고유 proper-time 미분은

`h'=q^T M V α`,  `h''=q^T(M² + Mdot)V α`.

여기서 둘째 식은 **on-lift source Y6=gamma Y7를 기준으로 선형화한** nonautonomous source의 관측가능성 항등식이다. 일반적으로 ||δ||가 유한하게 크면 비선형 electron-feedback 고차항이 생기므로 전체 비선형 exact second derivative라고 주장하지 않는다. Frozen-rate 비교는 `Mdot=0`으로 제한된 다른 진단이다.

`S=max_ij |M_ij|>0`라 두고 위의 두 열로 구성된 **무차원 정규화 2×2 관측가능성 행렬**:

`O(t)= [ q^T M V / S ; q^T(M²+Mdot)V/S² ]`, `D(t)=det O(t)`.

`D(t)!=0`이면 주어진 source linearization에서 두 숨은 전하 방향은 첫 두 charge-derivative로 국소적으로 구별된다. `D=0`이면 같은 **두 미분만**으로는 full rank를 확보하지 못한다. 이는 장비 감도나 실험 가능성 보장이 아니다.

BASS 원본 source로부터 정확한 입력미분은

`UV_x=(1+z)/(2·0.8) sech²[(7-z)/0.8]`,  `T_x=11900 UV_x`,

`ne_x=-3 ne + (nb/H) q21^T F21(Y)`,

`Mdot = H{UV_x Gphoto,Li + ne_x Gne,Li + ne T_x (∂Gne,Li/∂T)}`.

온도 미분은 원본 Verner–Ferland RR + Badnell DR 식을 analytic differentiation하여 구현하고 5개의 실제 저장 온도에서 중심차분의 source-input derivative와 독립적으로 대조했다. `H` 단위 s⁻¹, `ne` m⁻³, `Gne` m³s⁻¹, `M` s⁻¹, `Mdot` s⁻².

## 실제 193 원본 저장 상태의 결과

`results/NATIVE_193_LI_CHARGE_JET_ROWS.csv`에 각 저장 시각 `x,z,H,nb,ne,T,UV`와 `M`, 정규화 determinant, 첫·둘째 derivative 그리고 양의 isotope-preserving 전하 편차에 대한 electron-source 변화를 저장하였다. 다음 다섯 쌍은 `D`의 *수치 부호가 바뀌는 두 저장 샘플*이다. 범위는 (z 감소 순):

1. `14.4943273099 < z < 14.6521599843`
2. `11.7803642712 < z < 11.9105512120`
3. `9.7576359569 < z < 9.8672184137`
4. `8.9198344678 < z < 9.0208826754`
5. `8.2404593128 < z < 8.3345870781`.

임의의 매끄러운 기하/화학 원본 연속 궤적이 저장된 끝점 값과 부호를 그대로 연결하면 중간값 정리에 따라 각 구간에 적어도 하나의 `D=0`이 존재한다. 그러나 **원본 실제 미저장 BDF 궤적의 interval-certified 0 증명이나 영점 정밀 위치는 얻지 않았다**. 193개 고정 시점에서 `D`가 0으로 반올림되는 샘플은 없었다. Frozen-rate `det[q M V; q M²V]`는 3개 구간만 부호 전환하여 nonautonomous source의 차이를 실증했다.

대표 저장 샘플 `z=3.591836871`에서 nonautonomous `D=0.0107621082654045`, frozen `0.0107621080563906`. Li6 `q=2` 이온 80% 이하의 재배분 `δε=epsilon*(0,1,-2,1)`, `epsilon=8.80026230446e-17` per baryon은 총 Li6과 전하를 정확한 산술상 보존하면서 순간적 전자 source 변화의 1차 미분 `q M δε=2.22917970534e-30` electrons/baryon/s를 일으킨다. 이 조건에서 retained 17상태의 **초기 첫 미분 차이는 0**, 둘째 미분의 L1 차이는 `4.33102324167e-47` per baryon/s². 0이 아닌 계산적 구분이지 관측가능한 크기라는 주장은 아니다.

## 검증과 이전 연구에 대한 과학적 판정

원본 `trajectory.npz` raw SHA, donor ZIP 2개, original native `AtomicNetwork`, model SHA 확인. Python target 13/13, PR275의 저장 F/J 일부를 native 재계산으로 비교, charge-current의 별도 사건식 확인, nonautonomous `Mdot`의 source Taylor 입력 검산, 80자리 mpmath 193/193 determinant sign 일치(최대 절대 double vs MP80 차이 3.83e-15). Wolfram mass/charge-null basis, generator column-sum zero, `Mdot` 항의 determinant 차이 symbolic 확인. 수치 정밀도는 frozen binary64 source에 대한 산술 정밀도이며 과학적 원자료 오차구간이 아니다.

**이 연구는 BASS21 source에 대한 conditional local identifiability 진단이다.** 실제 REI17과 BASS의 isotope inventory, Li6/T/fast reservoir, radiation bath, redshift/clock, H, nb/nHref, full J 원천이 다르므로 true cross-owner 21↔17 projection/Jacobian 동등성이나 physical tau, CMB 관측/후험확률/production을 승인하지 않는다. R6/C9 다른 작성자 검증은 NOT_RUN, F4 PARTIAL, L4 false, original DAG 변화 0.

문헌 배경: Li & Rabitz, *Chemical Engineering Science* **44** (1989) 1413–1430, DOI 10.1016/0009-2509(89)85014-6 (exact kinetic lumping); Ovchinnikov et al. *Bioinformatics* **37** (2021), DOI 10.1093/bioinformatics/btab010 (constrained exact lumping). 해당 새 BASS 원자료 계산 결과를 이 논문의 직접 주장으로 인용하지 않는다.
