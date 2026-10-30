# F4 물리 노드: Li II 59.020723673 eV M1 광자의 원본 BASS21 동결 가스 흡수

## 문제와 지위

원본 BASS21 saved 193 epochs의 가스 상태와 독립 PR280에서 실측 문헌으로 묶인 Li II(1s2s 3S1→1s² 1S0) M1 전이 에너지를 사용한다. 원본 BASS photoionization 가스 단면적, 핵종별 가스 농도, proper Hubble를 직접 평가한다. **광자 방출 branching 확률, 실제 스펙트럼별 수송, gas deposited heat, 전체 REI17↔BASS21 공통 시스템은 계산하지 않는다.** 시간 적분/새 IVP 0.

## 물리적 정의와 유도

원본 BASS21 상태는 `Y_i=n_i/n_b` (nuclei/baryon)이고, 원본 gas-rest proper gas 밀도 `n_b` [m^-3]와 각 ionic ground-state photoionization σ_i(E) [m²]를 가진다. 이 모델에서 원자별 하나의 광이온화 사건에 대한 photo-only extinction은

\[\kappa_i(E,z)=n_b(z)Y_i(z)\sigma_i(E),\qquad\kappa=\sum_i\kappa_i\quad[\mathrm{m^{-1}}].\]

고정된 동질 가스에서 광자 길이좌표 ℓ마다 \(dI/d\ell=-\kappa I\), \(I(\ell)=I(0)e^{-\kappa\ell}\)이므로 **photoabsorption 조건부** 첫 흡수 채널의 정규화 분율은 \(p_i=\kappa_i/\kappa\), \(\sum_i p_i=1\)이다. 이 식은 photon scattering, continuum emission, line escape, full angular RT와 다른 microscopic local extinction 진단이다. 포획 확률을 포함하지 않는 normalized branching이다.

원본 BASS 단면적의 활성 단일 전자 전이에서는 native threshold \(I_i\) [eV]와 광자 에너지 \(E_\gamma=59.020723673157676\) eV의 차이가 첫 광전자 운동에너지이고, 조건부 평균은

\[\langle E_{\rm prim}\rangle=\sum_{i:\sigma_i>0}p_i(E_\gamma-I_i),\quad\langle E_{\rm bind}\rangle=\sum_{i:\sigma_i>0}p_i I_i,\quad \langle E_{\rm prim}\rangle+\langle E_{\rm bind}\rangle=E_\gamma.\]

후속 secondary electron cascade, collisional thermalization, fluorescence, reemission은 계산되지 않아 `E_primary`가 `gas heat`이라는 결론은 금지한다. Hubble 대비 비교 \(\tau_H^{\rm frozen}=c\kappa/H\)는 단일 epoch에서 **한 proper Hubble length = c/H**를 인위적으로 동결한 무차원 크기비다. 실제 \(\tau=\int c\kappa\,dt\), 방향별 Bianchi 경로·동일 photon history·CMB optical depth는 아니다. `mean free path = 1/κ`도 실제 우주론적으로 적분한 비행거리와 구분한다.

## Source identity, validity

- `BASS@cc602e209e7deeb511ab2a1f3b2268d55206c43c` source model; original network Python SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`, original trajectory SHA256 `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`.
- PR278 full source archive SHA256 `df871a18f297da15d05a5dadbad55e2aa29571217ad9136d9c4826921d1a11db`, PR280 full source archive SHA256 `fd9b8343ed2ea48b6caa9eff8aa5592d34a75fb77cfe223c81af3afbd8a21a91`. Both input archives are included in the new one.
- BASS original 129 coefficient **numeric projection**, source Git blob `2eba600a9d7a7359ca55f566f1b841a363a3e5c7`, not source whole-table raw byte parity. Its H/He/Li six photo rows were read from original Git blob; original 193 source and loader were not modified.
- BASS external field T(z) / UV(z) and stored Y(z),n_b(z),H(z) are prescribed pilot, not a self-consistent CMB/inference history or REI17 300 K bath. BASS no photon transport within this chemical atomic source.
- Isotope matching at same Z,q: H1/D/T neutral (indices 1,3,5), He3/He4 neutral (7,10), He3/He4 singly charged (8,11), Li6/Li7 neutral (13,17). Other species have σ(Eγ)=0 under the original thresholds. Nonzero Li I is included and tiny.
- Verner, Ferland, Korista, Yakovlev, ApJ 465 487 (1996), DOI 10.1086/177435, original fitting law and validity. Measured Li II triplet lifetime Saghiri et al. Phys Rev A 60 R3350 (1999), DOI 10.1103/PhysRevA.60.R3350; NIST level as source-pinned by sibling PR280. Lifetime is not used to predict any gas deposition or a line yield.

## Constructive physical result

Native M1 energy 59.020723673157676 eV, BASS photo σ_HI=9.65427192455e-24 m², σ_HeI=1.41726250062e-22 m², σ_HeII=1.27524685483e-22 m², σ_LiI=6.31501277318e-24 m². At z=20, κ=3.74711085585e-20 m^-1, λ=864.874 proper pc, cκ/H=94917.2703, H I and He I absorb fractions .45635108 and .54364892, mean initial photoelectron 39.4460220 eV. At z=2, κ=2.00503547827e-26 m^-1, λ=1.616320172e9 proper pc, cκ/H=.907697394, He II photo fraction .994507659, mean initial photoelectron 4.82487335 eV. All are local *source-model* numbers, not actual photon emission/heat or remote escape predictions.

Among 193 **saved** points He II photo fraction passes .5 between z=9.22607755 and 9.12296021; frozen cκ/H passes 1 between z=2.09261538 and 2.06143018. These are bracketing labels, not numerically solved continuous physical transition events.

The isotopic 193×21=4053 rows and 193 summary rows are the actual physical-data product. No original central-DAG/L4 promotion: working 33/88, central 28/88, physical-fast 4/7, Δ0. New scientific source-scoped auxiliary 1/1 after verification; full physical F4 and L4 remain HOLD.
