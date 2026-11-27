# HE18 coding C2: 실제 warm P01 두 번째 저장 셀의 gas/photon 미분 결합

**선택 단계:** C2 (식·데이터·코드 대응), 2026-10-15 KST. 사용자 지시에 따라 `BASS_HE` 원격에 실제 코드 변경과 별도 Ubuntu 로컬 실행을 포함했다. 출발점은 draft PR56, commit `429c288e6951c75b4bc9f28f49ddcc2c96b57a11`. 별도 Codex가 진행 중인 `rei_bianchi` 원본은 읽기 전용이며, 기존 실행·queue·AX08 recovery는 건드리지 않았다.

## 1. 실제 원본과 해석 영역

대상은 `rei_bianchi` commit `a5c958c414dea41216b445c05f58df837f05cacb`의 warm P01 FT03/HM12 Case A, CR/RCT/HH OFF, normal-comoving non-tilted LRS Bianchi I, metric `(-,+,+,+)`이다. 두 번째 셀 `t∈[6.25e9,1.25e10]` proper seconds. 4개 기체 좌표 `(x_HII,y_HeII,z_HeIII,w[eV/H])`와 2904개 광자 reference-volume cm^-3 stock. 원 입력 `P01_STATE.npz`, emissivity, R7 4gas+2904photon incoming 오류 및 C1 frozen source/reconstruction SHA256은 `src/jacobian_map.py`에 정확히 pin 되어 있다. 원 `src/warm_source_reference.py`를 새 모형으로 대체하지 않고 실제 import·호출하였다.

기체 proper `n_H,n_He`는 cm^-3, `f=n_He/n_H=3/38`, 전자밀도 `n_e=n_H[x+f(y+2z)]`. 

\[
\Pi=1+f+x+f(y+2z),\quad T={2\epsilon_{\rm eV}w\over3k_B\Pi},\quad
\nabla_g T={1\over\Pi}(-T,-fT,-2fT,2\epsilon_{\rm eV}/(3k_B)).
\]

Photon reference stock `P_j`는 proper gas 밀도와 다르다. 원 `Source.env(t)`의 reference-volume 배수 `vol`은 gas photo-rates에 `P_j/vol`로만 들어간다. 원 `C=29979245800`은 **cm/s**, SI electron column 사용 시 `1e4 cm^-2→m^-2`를 곱한다. `c_cm×1e4=c_SI×1e6`.

## 2. 전체 원 RHS로부터 분석적으로 계산한 결합

\[
L=(n_H(1-x),\;n_{He}(1-y-z),\;n_{He}y),\qquad
\kappa_j=c_{cm}\sum_{i=0}^2L_i\sigma_{ij},
\quad \dot P_j=S_j(t)-\kappa_j(g,t)P_j.
\]

\[
\partial_g\kappa_j=c_{cm}(-n_H\sigma_{0j},\ n_{He}(\sigma_{2j}-\sigma_{1j}),\ -n_{He}\sigma_{1j},\ 0),
\quad C_{jk}=\partial_{g_k}\dot P_j=-P_j\partial_{g_k}\kappa_j.
\]

기체 photoionization에서 광자에 관한 미분은

\[
B_{0j}={c_{cm}\over vol}(1-x)\sigma_{0j},\quad
B_{1j}={c_{cm}\over vol}[(1-y-z)\sigma_{1j}-y\sigma_{2j}],\quad
B_{2j}={c_{cm}\over vol}y\sigma_{2j},
\]

\[
B_{3j}={c_{cm}\over vol}\{(1-x)\sigma_{0j}(E_j-\chi_0)
+f[(1-y-z)\sigma_{1j}(E_j-\chi_1)+y\sigma_{2j}(E_j-\chi_2)]\}.
\]

즉 `A=∂F_g/∂g (4×4)`, `B=∂F_g/∂P (4×2904)`, `C=∂F_P/∂g (2904×4)`, photon 자체 block `-diag(κ)`. 여기서 **기체 Jacobian `A`에는 원 Source의 충돌이온화(CI), radiative recombination(RR), dielectronic recombination(DR), radiative captured kinetic energy(RK), photon heat 및 `-2Hw`가 모두 포함**된다. 특히 Hui–Gnedin fit의 `g=d ln α/d ln T`를 미분하여 `d g/d ln T`를 RK 미분에 남겼다. `S_j(t)`는 시간/기하·emissivity만의 외부 주입으로, 고정 시각의 gas 미분에서는 0이나 photon equation 자체에서 삭제하지 않는다.

## 3. 실제 local 원본 실행 관찰 (중점만, 충분상계 아님)

User Ubuntu x86_64 isolated `/tmp/BASS_HE_HE18_C2_20261015` clone에서 GitHub 게시 소스 자체를 실행하였다. Private 원본은 별도 `/tmp/HE18_C2_INPUTS_20261015`에만 압축 해제하여 공개 repository index에 올리지 않았다.

- 중점 `t=9.375e9 s`; T≈49999.97910049289 K; Hgeom≈2.2148399858297704e-17 s^-1; proper nH≈5.9356182757161775e-5 cm^-3.
- Positive ray opacity `κ_j` 중 0인 경우 **784 photon nodes**. 대응하는 B,C 행렬 성분은 실제 계산에서 0.
- Gas scaling `Sg=diag(1,1,1,32 eV/H)` 후 pointwise `|| |Sg^-1 A Sg| ||∞=3.688083463534499e-13 s^-1`, `|| |Sg^-1 B| |C Sg| ||∞=4.908972582720406e-29 s^-2`.
- R7 nonzero photon 오차를 실제 2904개 전부 사용하여 pointwise `|Sg^-1 B| η_P ≈(6.539e-34,2.32548e-32,2.24762e-32,4.433e-34) s^-1`를 산출. 이 값에 `h`를 곱한 값도 **pointwise diagnostic일 뿐 true-error bound가 아님**.
- Photon rate identity `F_P=S-κP`와 실제 original `Source.rhs`의 normalized L1 mismatch 약 2.990e-22.
- 기체 4×4, B의 세 photon column, C의 3개 gas column, 3종 CI/RR/RK/DR rate 함수의 미분, 온도 전미분을 서로 독립적인 중심차분으로 비교해 현장 unittest **8/8 통과 (exit 0)**. Source 3개 값과 SHA pin을 바꾸지 않았다.
- Local Wolfram Engine 15의 실제 `xAct/xTensor 1.3.0` package load/원 전자 current tensor projection 4개를 실행하여 **4개 residual 모두 zero, exit 0**. Cloud Wolfram의 analytic scalar `κ/B/T/전자밀도/SI` 5개 zero 그룹도 확인. 초기 cloud 전체식은 `$Failed`였고 scalar 검사의 배열 판정 오류를 수정했음을 실패기록에 남김.

## 4. C2가 끝난 부분과 아직 열린 C3 의무

**COMPLETE_SCOPED_FORMULA_SOURCE_MAPPING, not certificate.** `A/B/C`는 **한 시각에서 분석적으로 정확한 구조의 수치 평가**이다. 더 엄격한 독립 부동소수점 포괄 검증이나 source/prod native Rust ABI parity를 완료하지 않았다. 향후 C3에서 구간 전체 gas-temperature simplex/tube에 대한 `A,B,C` majorant, photon envelope, exact `κ_min=0` 투명 node, whole-cell gas/photon residual·external HM12 forcing, geometry `b(t)` Gauss-12 오차·HM12 interpolation와 계수평가 roundoff, 첫 셀에서 넘어온 4gas+2904photon 오차를 함께 구성한 뒤 처음으로 참해 구간을 산출할 수 있다. 지금 두 번째 셀 `tau_true_interval=null`, `full_history_tau=null`, `observer_tail=null`이다.

## 5. 실제 Codex 지원 경계

같은 시간 별도 실제 `rei_bianchi`의 이력과 현재 실행 계약을 읽고 signed-shear의 원래 비교기 통합(HE floor, HH source pair, CR knot norm), AX07 full ZERO, AX08 signed recovery, AX11/12 준비를 구분하였다. 진행 중인 Codex owner의 다른 source/run/DAG 파일은 건드리지 않았고, 이번 C2는 warm HE source의 Jacobian map만 공개 BASS_HE branch에 반영하였다. Cold AXBI의 `YHe=.2454`, MD14/IGM, gas~8 K, `w[erg/H]`과 warm source의 CI/RR 계수는 혼합하지 않았다. 실행 중인 signed solver, shared scheduler나 누적 이력의 새로운 restart를 요구하지 않는다.

## 실행 명령 및 포인터

```
HE18_C1_DATA_ROOT=/tmp/HE18_C2_INPUTS_20261015/HE18_C1_20261014 \
 python3 -m unittest discover -s research/he18_c2_source_jacobian_20261015 -p test_jacobian_map.py -v
python3 research/he18_c2_source_jacobian_20261015/jacobian_map.py \
 --private-c1-root /tmp/HE18_C2_INPUTS_20261015/HE18_C1_20261014 \
 --out /tmp/HE18_C2_INPUTS_20261015/LOCAL_C2_JACOBIAN_MAP.json
```

Primary methodology: SciSpace source discovery of original numerical ODE posterior residual methods and Exa studies of componentwise source-positive estimates and goal functional error. Their published numerical constants were **not** imported into the present warm source; current A/B/C values are locally computed from actual original code only.
