# BASS_HE | 원본 M0826 각도 자료로 유도한 fast-D 운동에너지 분산

**2026-10-30; 부모 PR122 HEAD:** `6d105cd89bc8f47f00560ec07d6e41574bed1c38`. 고정 실측 원본은 IAEA-NDS/exfor_master@`939a14d7bba1ddce51975cb5e8711ce96b3b0871`의 M0826과 비교용 M0011이다. 두 원본의 byte identity는 실행시 SHA-256 및 Git blob으로 검증한다. PR114에서 M0011 E2 7점, E2/total 비율 및 sigma(E)(E-Q)를 이미 계산했으므로 이번 성과에 중복 산입하지 않는다. PR109에서 고에너지 M0475 대상으로 유사한 각도 모멘트 처리가 있었으나, 이번 물리적 입력은 저에너지 M0826의 실제 [30,50] MeV 분해능 제한 angular source이다.

## 원전과 자료 grain

M0826003의 원본은 1972 Arkatov et al. YF 16,12 Fig.1에서 CURVE로 편찬된 [30,50] MeV 범위의 **9개 각도 interval 관측** `(ANG-CM-MIN,ANG-CM-MAX,DATA-CM,ERR-S)`이며 단위는 (degree,degree,μb/sr,μb/sr)이다. 이는 9개 독립 실험이나 30·40·50 MeV의 단색 측정이 아니다. M0826001의 원전에는 계통적 γ-ray intensity error ≤5%가 따로 보고되어 있지만 검출기 acceptance나 공동 공분산은 주어지지 않는다. M0826002의 [30,40]과 [40,50] SIG는 서로 다른 energy grain이다. Rice et al. PRC61 064612 (2000)는 150–190, 190–250 MeV, 각 6각도 절대 측정이라고 원전 초록에 보고되어 있지만, 1998 PhD (TUNL 198쪽 스캔) 원본 수치표와 coincidence efficiency는 이 실행에서 읽지 못했다. 미확보된 12개 수치를 생성하지 않는다.

## 구성적 유도

Signature (-,+,+,+). `M=M_α c²=3727.37941180 MeV`, `m=m_d c²=1875.61294500 MeV`, `Q=2m−M=23.84647820 MeV`. 입사 광자 에너지 `E_γ`는 α 정지계에서 측정, `s=M²+2 M E_γ` [MeV²], `q=sqrt(s/4−m²)` [MeV]는 CM 중수소 3-운동량 크기에 c를 곱한 값이다. 고정 질량 기준의 문턱은 `E_thr=(4m²−M²)/(2M)`이다.

CM→α rest boost: `β=Eγ/(M+Eγ)`, `γ=(M+Eγ)/sqrt(s)`, 따라서 동일 질량 두 최종 중수소의 운동에너지

`K_±(Eγ,μ) = (Eγ−Q)/2 ± A(Eγ) μ`, `μ=cosθ_CM`, `A(Eγ)=Eγ q/sqrt(s)` [MeV].

정확한 짝 보존식 `K_++K_−=Eγ−Q`, 단일 event의 ± 부호 교환, `p_+^2=p_-^2=m_d²c²`(관례의 4-벡터 norm), 에너지 release 비음수 조건을 검사했다. 이는 정해진 Eγ와 θ의 **운동학**이며 실험 detector acceptance에 의존하지 않는다.

각 원본 구간 `i`를 `[θ_i^-,θ_i^+]`라 놓고 `u_i=cosθ_i^+`, `v_i=cosθ_i^-`로 정의하면 `ΔΩ_i=2π(v_i−u_i)>0`. **조건부 가정:** 원전의 CURVE 관측값 `D_i`가 해당 interval의 solid-angle average라고 취급될 수 있을 때 `w_i=D_i ΔΩ_i`, `P_i=w_i/Σw_j`이다. 이는 원전 기기 보정으로 완전히 입증된 사실이 아니다.

원래 interval 안의 미해결 angular distribution은 가정하지 않는다. `m_{i,min}=0` if `u_i≤0≤v_i`, otherwise `min(u_i²,v_i²)`; `m_{i,max}=max(u_i²,v_i²)`이면

`Σ_i P_i m_{i,min} ≤ <μ²> ≤ Σ_i P_i m_{i,max}`.

이 범위는 각 interval 지지집합만으로 얻는 sharp measure-theoretic bounds이다. 추가 *참고모형*으로 각 bin 안에서 일정한 differential density를 두면 `<μ²>_flat=Σ_i P_i (u_i²+u_i v_i+v_i²)/3`이다. 동일 D의 pair exchange로 두 daughter를 함께 세는 ensemble의 평균 운동에너지는 정확하게 `(Eγ−Q)/2`; source-normalized 두 daughter의 이에 대한 분산은 `A²<μ²>`.

아울러 source-reported `ERR-S`를 `D_i∈[max(0,D_i−ERR-S_i),D_i+ERR-S_i]`로 놓는 Cartesian *what-if box*의 sharp ratio extrema를 2^9=512개 weight vertices로 계산하였다. 이 구간은 어떤 실험적 joint CI도 아니다. 30,40,50 MeV는 source [30,50] support의 endpoint 및 reference-E **함수 평가 좌표일 뿐 별도 광자 에너지 측정이 아니다**. 실제 energy-angle separability와 광자 spectrum이 인증되지 않으므로 이 세 줄을 우주론적 photon flux 가중의 분산으로 단정하지 않는다.

## 직접 계산 결과

`Σ D_i ΔΩ_i = 5.430601681837213 μb`, PR122 기록과 일치. 조건부 nomimal source-bin weight의 `<μ²>∈[0.2034896337945987,0.4416976748602676]`, piecewise-constant reference `0.3108387148900143`. Source ERR-S Cartesian what-if box `[0.1225788975428183,0.5330307159952834]`.

| Eγ (MeV; 계산 좌표) | mean K_d (MeV) | A (MeV) | conditional Var(K_d) (MeV²) |
|---|---:|---:|---:|
| 30 | 3.0767609 | 0.8497478640 | [0.1469340513, 0.3189372728] |
| 40 | 8.0767609 | 1.8379668611 | [0.6874128458, 1.4921087133] |
| 50 | 13.0767609 | 2.9183344988 | [1.7330553306, 3.7617960958] |

9 measured angular intervals × 3 explicitly *non-measured monoenergetic* evaluation coordinates = 27 correlated, conditional D-pair-bin kinematic records. This does **not** add 27 independent observations or physical source event rate.

## Claim boundary and DAG

`established`: original EXFOR reaction/energy/angle/units and original source identity. `derived`: exact two-body boost and sharp within-bin angular-moment bounds under stated source-average interpretation. `numerically_checked`: Python 16/16, Wolfram independent summation. `unresolved`: precise experiment's angular bin interpretation, joint covariance, gamma-energy response, Rice 1998/2000 numeric table, stopping and proper He photon occupation. New source-scoped 2/2, central 28/88, HE physical 14/18, canonical physical delta 0, `R_event=null`, `heat_rate=null`, `kappa=null`, `L4=false`, `production=HOLD`.
