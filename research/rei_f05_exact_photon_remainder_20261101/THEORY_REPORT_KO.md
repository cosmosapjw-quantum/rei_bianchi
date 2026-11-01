# REI-F05 | 원본 26-event photon-owner 유한 변화 remainder 연구

**기준 과학 소유자:** 원래 2026-08-29 첫 canonical FLRW interval 46,080-node accepted tick160, 엄격한 다음 [160,161] logT 국소 오차 상계 2.1245050576368385e-4 > 2e-4. 원본 모든 생산 코드, Hummer–Seaton 및 photon-energy 소유권/열적 root/금지된 IVP 그대로 보호. **중앙 DAG=28/88 보고, canonical 추가=0.**

## 정의와 유도 (정확한 대수식)
한 원본 source 평가시각에서 4개 photon group의 실제 외부 sink E_g, current J_g 및 original cross-section·YHe·species별 총량 분모를 포함한 c_sg를 고정한다. 세 중성종 s=HI,HeI,HeII와 원본 46k node i에 대해
`D_g(n)=E_g+Σ_s c_sg S_s(n)`, `S_s(n)=Σ_i n_is`, `F_isg(n)=J_g c_sg n_is / D_g(n)`.
기준점 n0에서 δn과 `v_g=Σ_s c_sg δS_s/D0_g`를 두면
`F_isg(n0+δn)=F_isg(n0)+ (J_g c_sg/D0_g)(δn_is-n0_is v_g)+R_isg`
이고 **정확히**
`R_isg=(J_g c_sg/D0_g)(n0_is v_g^2-δn_is v_g)/(1+v_g)`.
Wolfram symbolic residual 0. 이는 이미 알려진 첫 미분을 **원본 46k 전체 부모 구간에 대하여 남은 비선형 항까지** 명시한다.

실제 동결 parent의 각 값 `n_is∈[L_is,U_is]`에 대해 원본 source의 positive denominator를 이용하여
`Dmin=E_g+Σ_s c_sg Σ_i L_is>0`,
`vabs=max(|Dmin-D0|,|Dmax-D0|)/D0`,
`δmax_is=max(|L_is-n0_is|,|U_is-n0_is|)`.
따라서 **원본 지정 binary64 source coeff J,c,E를 고정한다는 조건에서**
`|R_isg|≤(J_gc_sg/D0)[n0_is vabs²+δmax_is vabs]/(Dmin/D0)`.
원본 photons/초 단위에 적용하고, photoheating erg/초에는 동일 소스 owner의 excess-energy moments와 eV-erg 변환을 사용한다. 원본 핵자수 관계를 사용하지 않은 직사각형 부모 초집합의 상계이므로 보수적이지만 모든 물리적으로 가능한 부모 후보를 포함한다.

## 구현과 실제 검증/과학적 범위
`finite_source_remainder.py`는 PR332 원본 source wrapper `gp.context()`를 그대로 부르고 원본 archive/state SHA와 네 photon group owner를 읽는다. 각각의 46,080 노드에 대해 3개 광이온화 채널의 기준률, 원본 parent 내부의 **한 핵자수 보존 물리 후보**에 대한 실제 source rate, 1차 변분, 정확한 유한 remainder와 원래 전체 사각형 부모 상계를 저장한다. 표에는 원본 source의 photoheat remainder도 포함된다. 실제 핵반응 source 연산자가 이 baseline 및 sample 흡수율을 구간 포함하는지 검사한다. 입력 float는 정확한 binary64 유리수로 해석하여 Decimal100의 global S, photon source coefficients, remainder와 majorant를 구성하고 마지막 출력만 보수적으로 float로 변환한다.

이것은 원본 `_explicit_photo_fields`의 photoionization/source-only 부분에 대한 exact finite-change/remainder이며 원래 26-event event_box 전체, 재결합·냉각·heat implicit root 및 **공유 source 평가점 4개의 전체 MPRK22/SDIRK2 차분 map D_h(X,θ)** remainder는 아니다. 원본 광자 forcing의 시간·파라미터 불확실성도 함께 둘러싼 인증이 아니다. 성립범위 밖으로 확장하면 거짓 PASS이다.

## 증거/적대적 심사
- PR332의 정확한 세 전역 중성종 source moment와 원본 46k 수치상태를 사용하므로 후속 단순 point atlas 반복이 아님.
- 위 유한변화 식, 양의 분모, 전체 부모구간 bound, zero cross section과 subnormal 숫자 손실을 음성 테스트로 검증.
- Python 파일/실험에 대한 성공 주장과 GitHub Actions artifact는 **실제 실행 후 readback으로만 확정**한다.
- Original archival state/L4/Production HOLD, 원본 첫 구간 160/131072, 모든 old PR/branch 보호. Native remote desktop OFFLINE, distinct-author R6/C9 NOT_RUN.
- 다음 최소 실행: 이 source remainder를 공유 source/동일 부모에서 4개 평가시각의 전체 discrete-map implicit-stage `J_D` 및 검증된 remainder와 합성하고 **실제 [160,161] 변경 없는 기준**에 적용. 물리적 첫구간 인증이 아직 없으면 중앙 28/88 그대로.

References: original source Git blob `57f71d6aef1918c771e673afee0c608f426cad35` (original `reduced_interval_rhs.py`); PR332 source wrapper exact Git blob `91352a54b8d938fe24877925ad8c5fd6ec6e1609`; Pawlik & Schaye (2011) DOI 10.1111/j.1365-2966.2010.18032.x (independent literature context, not direct code validation).
