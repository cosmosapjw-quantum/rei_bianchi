# Physical fast F4 부분의 BASS 21상태 전자 피드백 rank-one 정리

2026-10-29, 유도 및 실제 CAS/코드 검산. 원 DAG working **33/88**, central **28/88**, physical-fast **4/7** 유지. 원 IVP 0, 원자료 변경 0. 이전 PR265의 물리적 source mismatch는 이 정리로 해결되지 않는다.

## 1. 원본 source 및 가정

입력: REI PR265 HEAD `9b0b97aadeebf368802f865c10eb8b633f2726e4`, 파일 `research/rei_bass_physical_charge_preflight_20261029/source/BASS_ATOMIC_NETWORK.py`, Git blob `e3a0603176304f64b953c0b2faf898d6b75eceb`. 그 파일의 `AtomicNetwork.rates`와 `evaluate`를 읽어 식과 인덱스를 대조했다. BASS PR234 원원본 ZIP byte SHA256 `6a9c84ce076a3545a992f0b364d0fd67fe1063b7a33a290dbe77d44ecee98838`; 이 실행에서 해당 ZIP을 다시 수령해 SHA로 검증한 것은 **아니다**. PR265가 이전에 수행한 원본 ZIP 검증을 재사용한다.

BASS 자체의 `Y_i=n_i/n_b`, `q_i` 이온전하, `n_e=n_b q^T Y`를 유지한다. `G0,D` 단위 s⁻¹, `Gne` 단위 m³/s, `n_b` m⁻³, `t` proper s, `H` s⁻¹, `x=ln(a/a_ref)`. 온도 및 UV는 고정 외부 값으로 보아 `∂Y`를 취한다. `(−,+,+,+)` 부호와 양의 누적 Thomson optical depth를 유지한다. 원본 21-state H1/D/T/He3/He4/Li6/Li7, neutron 좌표를 모두 유지한다. full62 geometry feedback, T/UV 자체 tangent, 열 closure는 제외한다.

원본 RHS는

\[
F(Y)=(G_0+D+n_b(q^T Y)G_{ne})Y.
\]

## 2. 정리: 정확한 rank-one 전자 피드백

\[
J_Y=G_0+D+n_e G_{ne}+u q^T,\qquad u=n_bG_{ne}Y.
\]

증명: `D_Y[(q^T Y)Gne Y] = (Gne Y)q^T + (q^T Y)Gne`를 곱규칙으로 전개한다. `A=G0+D+n_eGne`를 *고정 상태의 행렬*로 정의할 뿐, `n_e`를 모든 Y에 대해 상수로 취급하지 않는다. 따라서 `rank(J_Y-A)≤1`은 정확하다. 보존 벡터 `a_i`(핵자수)가 원본 반응의 각 생성자와 직교하면 `a^T J_Y=0`도 성립한다.

시간 step `h=Δt≥0`에서 `M=I−hA`, `Mw=hu`, `Mz=b`, `s=1−q^Tw`로 정의한다. `M` 가역, `s≠0`이면 Sherman–Morrison 식은

\[
x=z+w\frac{q^Tz}{s}.
\]

비정확 기반해의 잔차 `r_z=b−Mz`, `r_w=hu−Mw`에 대해 실제 full-matrix residual도 정확히

\[
r=b−(M−huq^T)x=r_z+\frac{q^Tz}{s}r_w
\]

이다. 이는 두 선형해가 근사적이어도 성립하는 유용한 error-monitor identity다. `s≈0`이면 correction을 함부로 적용하지 않는다. 행렬 `M`의 가역성, `s` 비소멸, residual의 작은 값은 서로 별도 조건이다. 이 식 자체는 forward-error bound나 물리적 positivity 증명, 성능 향상 보장이 아니다.

Log-scale-factor와 원본 positive species scaling `Y=D_s y`로 변환하면

\[
J_{x,\mathrm{chem}}=\frac1H D_s^{-1}AD_s+
\underbrace{\frac{n_b}{H}D_s^{-1}G_{ne}Y}_{u_x}
\underbrace{(q^TD_s)}_{q_x^T}.
\]

이는 BASS full62 Jacobian의 **21×21 chemical diagonal subblock**에 대한 식이다. 실제 full62에서는 geometry/opacity 및 τ 교차 블록이 있으므로, 화학 블록만 선형 풀이한다고 전체 62×62 Newton step을 풀었다고 주장하면 안 된다.

## 3. source 연결과 물리적 범위

REI PR265에서 확인한 `He4/H1` 재고 약 0.494–0.519% 최소 불일치와 `T_BASS=0`, `T_REI>0` 충돌은 남는다. BASS `G0`는 별도 UV prescription이며 REI의 Puchwein six-moment rate와 같은 것이 아니다. REI full-chemistry Jacobian, 동일 source-baseline, geometry, `nHref/nb`, `K/H`, nonzero T/fast reservoir, Li6 charge, 실제 300 K bath/ON_refined history의 parameter tangent는 결합되지 않았다. 이 정리는 source-locked BASS 측 matrix factorization sub-obligation을 해소하지만 F4 closure나 physical τ/CMB admission은 해소하지 않는다.

## 4. 실제 검증

Python standalone 10 unittest PASS. CPU process user1.16+sys0.10=1.26s (wall0.87s, peak97928KiB). Seven Jacobian FD synthetic cases, 17 direct-vs-SM solves, 8 baryon/structural cases, exact inexact-base residual test, log-clock scaling and near-zero Schur guard. Wolfram 2×2 symbolic arbitrary nonzero real entries gave exact residual identity `{0,0}`; genuine independent *author/model* R6/C9은 도구 미노출로 NOT_RUN. Synthetic coefficients follow the source's declared 21-species topology but are **not** the actual published BASS table or REI saved bath. No IVP or physical observable computed.

Literature context: Puchwein et al. (2019), MNRAS, DOI `10.1093/mnras/stz222` models UVB/thermal histories, not a rate identification with BASS; Anninos et al. (1997), New Astronomy, DOI `10.1016/S1384-1076(97)00009-2` addresses stiff non-equilibrium chemical evolution. The rank-one/source-specific results here are directly derived, not attributed to those papers.
