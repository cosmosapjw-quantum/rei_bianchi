# BASS_HE | M0826 원본 실측 DA–SIG 사건 계수 정합성 (2026-10-30)

## 원본과 범위

불변 원자료: IAEA-NDS/exfor_master@`939a14d7bba1ddce51975cb5e8711ce96b3b0871`. `M0826002`는 1972 Arkatov et al.의 [30,40], [40,50], [50,60], [60,75] MeV 총 광분해 단면적 `SIG` 네 구간(TABLE), `M0826003`는 [30,50] MeV 각도별 `DA` 아홉 구간(원문 FIG.1에서 CURVE 추출). `M0011002`는 별도의 1978 Arkatov et al. 총단면적 14점이며 원본 비교군으로 보존한다. 새 원본 실험 수는 0이다.

## 정의와 계산

정지 He-4 표적계 입사 광자, CM 각도 θ, 원자료의 각도구간 [θ_{i,-},θ_{i,+}]에서 보고한 평균값 D_i (μb sr^{-1})를 사용한다. 구간 내 보고 평균을 해당 유한 bin의 angular density로 간주하면

  Ω_i = 2π[cos(θ_{i,-}) - cos(θ_{i,+})],   I_DA = Σ_i Ω_i D_i.

M0826003의 원본 9행에서 I_DA = 5.430601681837213 μb. 포괄적(outgoing deuteron inclusive) daughter-counting DA라고 *조건부 가정*하면 서로 구별할 수 없는 최종 D 두 개를 단일 사건으로 환산하는 1/2가 붙는다:

  σ_evt,DA^(conditional) = I_DA/2 = 2.7153008409186064 μb.

M0826002의 첫 두 SIG 표본을 단순 에너지 구간폭 10 MeV로 평균한 비교기준은

  ⟨σ_SIG⟩_width = [10(2.94)+10(2.47)]/20 = 2.705 μb.

따라서 I_DA/⟨σ_SIG⟩_width=2.007616148553498; σ_evt,DA/⟨σ_SIG⟩_width -1=0.003808074276749. 차이는 0.0103008409186064 μb이며 통계적 모델의 정규화 계수 판별과 별개로 원전 값의 직접적인 cross-check를 제공한다.

## 통계와 해석의 정확한 경계

- DA 원전 ERR-S만 사용하고 9 bin 독립이라고 **추가 가정**했을 때 σ_evt,DA 통계 표준편차는 sqrt[Σ(Ω_i ERR-S_i/2)^2]=0.351295329671934 μb. 실제 실험 공분산은 알 수 없다. 표준편차의 PSD-compatible 상계로 Σ Ω_i ERR-S_i/2=0.968326005582964 μb를 별도 보존하며 이것을 측정 CI로 해석하지 않는다.
- SIG 두 bin의 독립 ERR-S 가정 평균 표준편차는 0.456097577279248 μb, 완전 상관 상계는 0.645 μb. `M0826001`의 광자 강도 계통오차는 5% 이하로 보고되며 공통 calibration/DA와의 상관성은 미지다.
- DA는 [30,50] MeV의 원전 유효 에너지 support에 대해, SIG는 두 서로 다른 [30,40]/[40,50] MeV bin에 대해 측정되었다. bin-width 평균이 **실제 실험 광자 flux response를 재구성했다는 뜻은 아니다**. 평균은 공개된 구간폭만 이용한 비교 규약이다.
- 원본 DA `STATUS CURVE`, SIG `STATUS TABLE`의 추출 차이가 있으며 검출기 acceptance와 각도별 응답의 원전 보정 의미론은 아직 검사해야 한다.
- 2배 가까운 일치는 포괄적 daughter counting의 1/2! 해석을 **지지**하지만 실험 정의의 증명은 아니다. 원전 총단면적이 event/counting 정의인지, detector efficiency가 어떤 의미의 angular density를 산출했는지 직접 확인해야 한다.
- M0011의 14 total SIG 원본 점은 저장했지만 M0826과의 차이를 실험 동일성·규약 불변으로 가정해 합산하거나 fit하지 않는다.

## 상세평형의 분리

반응 γ+α → d+d와 d+d → α+γ에 대해 s=(p_γ+p_α)^2, k=(s-m_α²c⁴)/(2√s), q=√(s/4-m_d²c⁴), 여기서 k,q는 CM 운동량에 c를 곱한 MeV 좌표다. 시간반전 미시진폭과 spin weights를 이용한 kinematic reciprocal weight는 기존 PR107에서 conditional로 정리했다. 하지만 M0826의 event-vs-daughter angular convention 및 polarization/detector normalization을 확인하지 않은 상태에서는 이번 I_DA/2 일치만으로 inverse capture absolute σ나 rate로 승격하지 않는다.

## 결론과 DAG

`M0826_MEASURED_EVENT_CONSISTENCY`: 2/2 source-scoped. Central 28/88, HE physical 14/18, canonical physical delta 0. `kappa`, `R_event`, `heat_rate`는 null; `L4=false`, `production=HOLD`. 다음 고우선 실제 연구: 1972 원논문 Table 1/Fig 1과 광자 flux 및 detector geometry의 event-counting 문구 확보, 1995/1998 Rice 학위논문 150–250 MeV absolute six-angle tables 정본 및 coincidence efficiency, 실제 He 고유계 gamma field와 D_fast stopping/deposition 연결.
