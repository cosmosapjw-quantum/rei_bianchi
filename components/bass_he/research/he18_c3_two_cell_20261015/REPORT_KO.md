# HE18 C3: warm P01 두 번째 저장 셀의 전 구간 오차구성 및 첫 두 셀의 공변 광학깊이

**2026-10-15 KST** · `physmath-research-loop` C3 실제 수치설계 + stage-local 구성적 이론 계산. 부모: `BASS_HE` draft PR57 `49a3f747aead23ac412922a45c9c1f4ef2a54157`. 과거 HE17 R5의 사용자 소유 interval/Taylor 코드를 두 번째 물리 셀로 구성적으로 이식했다. 이전 결과를 미지의 native 코드를 재실행한 것처럼 표현하지 않는다.

## 1. 소스, 좌표, 초기 오차

실제 선택된 물리는 FT03/HM12 Case A, prescribed normal-comoving non-tilted LRS Bianchi I, 시그너처 `(-,+,+,+)`, `x^0=ct`, proper seconds. 원 receiver `rei_bianchi@a5c958c414dea41216b445c05f58df837f05cacb`; 원 NPZ SHA256 `3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be`; 원 HM12 emissivity SHA256 `88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b`. Photon은 2,904개 reference-volume `cm^-3` stock이고 gas는 `(x_HII,y_HeII,z_HeIII,w[eV/H])`. Electron proper `n_e=n_H[x+(3/38)(y+2z)]` with `n_H` in `cm^-3`; 열 계산의 `c=29979245800 cm/s`이므로 column `m^-2`에는 `10^4`를 한 번 사용한다.

이번 셀은 **원 source의 두 번째 저장 셀** `[6,250,000,000,12,500,000,000]` proper seconds이고 길이 `h=6,250,000,000 s`다. `u=(t-h)/h∈[0,1]`를 둔다. `t=h(1+u)`를 모든 background `volume`, `n_H`, `Hgeom`, `b(t)`에 적용한다. 초기 shear `b(t)`는 절대 global origin에서 `h*s_initial ∫_0^(1+u) du'/volume(u')`로 평가한다. 국소적 `b(0)=0`으로 다시 시작하지 않는다. `shear_anchor`의 전 구간 remainder는 Taylor 8차 미분구간을 `0≤(t/h)≤2`에 적용했다. Photon `S_j(t)` HM12 외부 강제항과 Verner 원 threshold를 그대로 사용하며, 실제 2,904개 spectral/activation 분기를 전 셀에서 거부조건과 함께 검사한다.

저장 상태에서 새 `FIXED_REFERENCE.npz`를 구성하면서 C1 원 RHS의 양끝 기울기만 새로 2회 계산해 binary64 dyadic으로 고정했다. 그 SHA256은 `3572256db4cc17f45f76cf9bcb14434c158066ddcf54d93db26279d688f4b26e`. 첫 셀 R7이 남긴 `gas4+photon2904` **비영 초기 오차** `ENDPOINT_MEMORY_R7.json` SHA256 `aaca8a993a951894bda57cdf29ac7f0fffb8d78e092c87f8356176fe451a9a39`를 사용했다. `C1` 원 `left`의 모든 2,908개 dyadic endpoint가 원 NPZ의 node1/2와 일치하는지 이번 검증에서 실제 확인했다.

## 2. 구성적 이론: 두 번째 셀의 오차 전달

원 미분계:

\[
\dot g=F_g(t,g,N),\qquad \dot N_j=S_j(t)-\kappa_j(t,g)N_j,
\quad \kappa_j\ge0.
\]

고정 Hermite reference `ĝ,N̂`에서 무차원 잔차는

\[
R_g=\partial_u\hat g-hF_g(t,\hat g,\hat N),\quad
R_{N,j}=\partial_u\hat N_j-h[S_j(t)-\kappa_j(\hat g,t)\hat N_j].
\]

기체 scale `S_g=diag(1,1,1,32 eV/H)`를 사용한다. 실제 source의 전체 기체 영역과 **positive true photon envelope** `N_j(h)≤N̂_j(h)+ε_{N,j}^{in}` 및 `N_j(t)≤N̂_j(h)+ε_{N,j}^{in}+h sup_t S_j(t)` 위에서 비음수 상계행렬 `Ā=|S_g^-1 ∂_g F_g S_g|`, `B̄=|S_g^-1∂_N F_g|`를 구성한다. C는 reference photon envelope의 `|∂_g(κ(g)N̂_j) S_g|`로 따로 구성한다. Transparent 784 node에는 κ=0을 정확하게 유지하고 공통 양의 photon 감쇠하한은 도입하지 않는다. 같은 prescribed HM12 source는 오차 방정식에서 상쇄되지만 reference 잔차에서 빠지지 않는다.

\[
P=h\bar A+\tfrac{h^2}{2}\bar B\bar C,
\quad d_g=\int_0^1|S_g^{-1}R_g|du,
\quad d_N=h\bar B\int_0^1(1-u)|R_N|du.
\]

첫 셀에서 전파된 scaled gas `ε_g^{in}`와 **raw photon** `ε_N^{in}`를 포함한 불변량의 충분조건:

\[
\boxed{D_g\le(I-P)^{-1}\bigl[\epsilon_g^{in}+h\bar B\epsilon_N^{in}+d_g+d_N\bigr].}
\]

여기서 gain `||P||_∞<0.002305062256164466<1`이고, 위 원 gas box에서 reference Bernstein control points에 `D_g`를 더한 최대 비율은 `0.07781016786217548<1`이다. 실제 해에 대한 이전 전체 구간 first-exit box와 이 strictly interior 관계가 같이 존재한다. `A/B/C`는 C2 **중점 표본** 값을 확대하여 인증한 것이 아니라 원 source를 `mpmath.iv` 70dps interval jet로 평가한 새 whole-cell 함수 상계다.

잔차는 midpoint degree-2 Taylor polynomial + order-3 whole-cell remainder로 감싼 뒤 16 Bernstein subsegments를 사용했다. `|u-1/2|≤1/2`에서 sup remainder는 `M3/8`, unweighted integral은 `M3/32`, `(1-u)` weighted integral은 `M3/64`이다. 2,904 photon node별로 각각 독립 구성했다.

세 번째 셀에 전달할 **원 2,904성분**의 다음 보수적 packet은

\[
\epsilon_{N,j}^{out}\le\epsilon_{N,j}^{in}+h\sum_k\bar C_{jk}D_{g,k}+\int_0^1|R_{N,j}|du.
\]

이를 실제 exact Fraction으로 2,904개 모두 계산해 `SECOND_ENDPOINT_MEMORY.json`에 남겼다. 합계는 incoming 약 `1.88953569e-20`, 새 coupling 약 `1.60926979e-23`, 새 photon 잔차 약 `2.41233260e-20` (원 photon reference-stock 좌표). 첫 셀의 고정 B에 대한 4성분 압축을 세 번째 셀로 이월하지 않는다.

## 3. 새로운 계산된 결과

| 대상 | 첫 셀 R7/R8 원본 | **이번 두 번째 셀 C3** |
|---|---|---|
| 시간 [proper s] | `[0,6.25e9]` | `[6.25e9,1.25e10]` |
| Column radius `m^-2` | `<1585.727990634604` | **`<17133.53906269203`** |
| nonnegative comparison gain | 원 R7 유효 | `<0.002305062256164466` |
| opacity=0 photon nodes | 784 | 784 |
| tau interval | `[7.99991934859042930820,7.99991934859042951919]e-9` | **`[7.99991602637340638090,7.99991602637340866051]e-9`** |

**연속한 처음 두 셀**의 같은 광선·source optical depth를 정확한 유리수로 더하면:

\[
\boxed{\tau_{0\to 2h}\in
[1.5999835374963835689099719,\;1.5999835374963838179682741]\times10^{-8}.}
\]

선택된 path에서 첫 충돌/scattering-out 확률 `1-exp(-tau)`를 교대급수 `S4(τ_lower),S5(τ_upper)`로 감싼 결과:

\[
\boxed{P_{0\to2h}\in
[1.5999835246966470358773239,\;1.5999835246966472849356221]\times10^{-8}.}
\]

**인증 상태:** 원본과 동치인 ideal exact-real finite P01 source, 정확한 dyadic Hermite reference, 이전 global gas domain, 지정된 수치 interval primitives가 올바른 outward enclosure를 제공한다는 계산 신뢰경계 아래의 **source-scoped conditional mathematical/numerical certificate**다. 이 인증은 (i) native binary64/source arithmetic roundoff 전체, (ii) 독립적인 `mpmath.iv` primitive의 형식검증, (iii) HM12·atomic fit 물리적 보정오차, (iv) photon spectral/angle continuum 이산화오차, (v) 실제 우주론적 관측자 foreground, (vi) 저장 셀 3–16의 fine error를 포함하지 않는다. 해당 범위의 물리 scientific admission이 아니다. 두 번째 셀의 `numpy longdouble GL24` 중심값은 별도 탐색값이며 새로운 정확한 중심값으로 덮어쓰지 않는다.

## 4. 실제 코드 및 재현

사용자 소유 HE17 R5 `warm_interval.py`, `interval_jet.py`, `run_evaluations.py`, `assemble_certificate.py`를 **두 번째 저장 셀의 global clock/shear, 원 Hermite 계수, 비영 incoming error**로 최소 변화시켜 사용했다. 새로운 `stage_inputs.py`는 원 ZIP C1 SHA `fedc88bf...`, R5 SHA `2f29435e...`, R8 SHA `b58f6e26...`를 확인하고 별도 private runtime에 원본 입력을 놓고 원 RHS 두 끝점을 계산한다. 첫 2개의 interval-jet 실행, 조립, 검증, 다음 photon packet 생성 외에 ODE는 재실행하지 않는다.

실제 이미 수행한 first run: `mid`/`whole` 각각 2,904 node와 gas residual series, assembly exit0. 새 runtime을 별도 경로에 만들고 **정확한 동일 입력에서 완전히 재실행**했으며, 시간소모 메타데이터를 제외한 scientific `CERTIFICATE`가 semantic-equal, `TWO_CELL_VALIDATION`과 2,904성분 `SECOND_ENDPOINT_MEMORY`는 byte-identical임을 확인했다. 비교행렬 원리식·비영 incoming 2,904개 사용·모든 2,908개 reference 양끝·원 gas box의 strictly interior·인접한 두 구간 clock 연결 등을 독립 Fraction 검사 10개로 확인했다.

Wolfram Language 15.0.1: photon forcing, 두 셀 광학깊이 가산성, helium number ratio, SI 변환 등 8 scalar 항등식 `0/True`; 사용자 local Wolfram Engine/xAct xTensor1.3.0: 현재 공변 전자전류 5개 tensor `0`, exit0. Native subagents / 외부 독립 scientific reviewer NOT_RUN.

**작업 실행 명령:** 공개 repo에는 Python source/code/검증/문헌·결과요약만 올린다. C1, R5, R8 원본 ZIP 및 HM12 표/원 photon data는 private ZIP에 남기고 Git에는 commit하지 않는다.

```bash
python checks/stage_inputs.py --c1 /path/BASS_HE_HE18_C1_SECOND_CELL_AND_AXBI_20261015_v1.zip \
  --r5 /path/BASS_HE_HE17_R5_FIRST_CELL_CERTIFICATE_20261014_v1.zip \
  --r8 /path/BASS_HE_HE17_R8_ADOPTION_INTEGRATION_20261014_v1.zip \
  --output /tmp/HE18_C3_RUNTIME_FRESH
cd /tmp/HE18_C3_RUNTIME_FRESH
PYTHONPATH=src python src/run_evaluations.py mid
PYTHONPATH=src python src/run_evaluations.py whole
PYTHONPATH=src python src/assemble_certificate.py
python checks/verify_c3.py
python checks/propagate_endpoint.py
```

## 5. 다른 repo와 현 진행중인 Codex 개발

최신 `rei_bianchi` Codex source `6cbdb57010a79eb3bbbc6a54b7f1a75d466702fd` (2026-10-15 KST 기준)에서 cold `SOURCE07` optional covariant momentum photon pilot과 수정된 energy/number ledger가 개발되어 있음을 읽었다. 이 source는 `YHe=0.2454`, 초기 IGM gas~8 K, MD14/Grackle 계수, `w[erg/H]`, 단일 emission cohort·frozen opacity reference다. **현재 warm P01 FT03/HM12 50000K gas 및 `w[eV/H]`와 다른 과학 문제**이므로 숫자/대응 진단을 혼합하지 않았다. Owner `AX08` signed recovery active, `AX11/12` prepared pending, `AX13` partial report prepared, 실제 전체 abundance scientific admission 미발급. 기존 owner source/queue/process/STATE 변화 및 새 solver 실행은 0. 별도 cold source 기하·파동수 레지스트리의 향후 인터페이스 방식만 참조했다.

## 6. R/C 단계와 계속할 실제 작업

이번 작업은 C3 **source-scoped constructive numerical design plus executed interval computation**이며, 일반 이론에서 positive diagonal photon attenuation과 비음수 gas/photon coupled comparison을 이 소스에 처음 두 셀까지 구성적으로 적용한 stage-local 이론 결과다. 계산을 실제 실행했지만 이를 C4–C10 완료로 자동 확장하지 않는다.

**다음 C4:** 첫 두 셀의 검증된 증거를 정확한 archive/hash로 checkpoint, 셀 3–16의 source-matched fixed reference와 개별 4gas+2904 incoming carry, 64-part refinement 효율/오차폭, 실제 로컬 RAM/CPU runtime 예산을 반영하여 bounded scientific DAG를 구성한다. 다음 선택적 이론 검토에서는 source primitive의 numerical roundoff 가정을 독립 평가하고 exact physical contour/opacity claim을 분리한다. `rei_bianchi` signed abundance/temperature plot 목표에 HE warm optical을 선행조건으로 넣지 않는다.

### 원전 기준

- Neumaier, *Computer-assisted proofs and ODEs*, Computing 52 (1994), 315–336, DOI `10.1007/BF02276880`; residual enclosure plus stability/tube, not solver tolerance alone.
- Talvila–Wiersma, arXiv:1202.0249; bounded quadrature remainder methods.
- Akrivis, Makridakis & Nochetto, *Optimal order a posteriori error estimates for Runge–Kutta and Galerkin methods*, continuous reconstruction residual and stability machinery. Present equations arise from source-specific rederivation, not imported constants.
- User-owned actual R5 interval evaluator and R7 raw photon memory with immutable source identities described above.
