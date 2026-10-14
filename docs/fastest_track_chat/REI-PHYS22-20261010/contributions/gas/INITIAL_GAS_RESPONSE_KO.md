# PHYS22: 실제 초기 기체의 scalar shear response

기여자 `/root/phys22_gas`. 이 문서는 PHYS22 후보 유도와 국소 수치 계산에 대한 기여이며 최종 독립 판정이 아니다. 물리 상태는 `HOLD`다. 새 gas IVP, native Rust history, PHYS21 검산 suite는 실행하지 않았다.

## 1. 입력과 계수의 의미

PHYS22 계약은 `PHYSICS_CONTRACT.json`, SHA256 `1706650c98b6b30f12e57b2af670113fe8ec30770ae2f48909823c30936de4a6`이다. 입력 commit은 `3dc42c64ab32075f0a59c96af3ddf7435d9b7f97`, scientific source tree는 `cb69b4736dd046e4675557577eb8e0ead037d1f3`이다. PHYS21에서 닫힌 angular scalar kernel과 local gas derivative는 상속하고, 이번에는 실제 초기조건에서 새로운 시간 계수와 physical-direction JVP를 계산한다.

Metric signature는 \((-+++ )\), 시간은 gas-comoving proper seconds다. \(H,n_H(t),N_0,S,E_b\) 및 초기 scalar state는 무차원 \(\epsilon\)에 독립적으로 고정한다. \(B(t)=t\Sigma\), \(\operatorname{tr}\Sigma=0\)이며

\[
\Sigma=\varsigma\operatorname{diag}(1,-1,0),\qquad
q=\operatorname{tr}\Sigma^2=2\varsigma^2.
\tag{G1}
\]

\(\varsigma=((1.01\times10^{-14})-(0.99\times10^{-14}))/2\)는 해당 binary64 literal 차이에서 정한다. 이 기여자의 모든 수치는 ordinary binary64 평가다. source literal을 입력으로 한 정확한 실수 연속모델의 식과 source의 전체 binary64 stage를 같은 것으로 주장하지 않는다.

기체 좌표와 두 종류의 전개는

\[
y=(x,a,b,w)=(x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},w_{\rm eV/H}),
\]

\[
y_\epsilon(t)=y_0(t)+\epsilon^2\eta(t)+o(\epsilon^2),\qquad
\eta(t)=\eta_3t^3+\eta_4t^4+\cdots .
\tag{G2}
\]

따라서 \(\eta\)는 epsilon²의 계수이며 \(\partial_\epsilon^2 y|_0/2\)다. \(\eta_n\)에는 시간 Taylor 계수의 factorial을 추가로 나누지 않는다. 이 문서에서 He coordinate \(b\)와 photon birth time \(\tau\)는 구분한다.

실제 입력은 \(H=10^{-14}\,\mathrm{s}^{-1}\), \(n_H(0)=10^{-4}\,\mathrm{cm}^{-3}\), \(f=0.083\), \((x,a,b,T)=(0.9,0.3,0.6,50000\,\mathrm K)\), \(N_0=0.05\) photon/H, \(S=5\times10^{-15}\) photon/H/s, \(E_b=13.7\) eV다. \(\chi=13.598434599702\) eV와 HI opacity cutoff 13.60 eV를 구분한다. 초기 source는 generic FT03 [20,35,70] eV fixture가 아니다.

## 2. 첫 forcing과 응답의 차수

\(D=E\partial_E\), \(\mathscr C=D^2+3D\)로 둔다. Birth \(\tau\)의 age가 \(u=t-\tau\)일 때 \(A_s=(s-\tau)\Sigma\)이므로 PHYS21 kernel의 각 항은

\[
\operatorname{tr}A_t^2=qu^2,\qquad
M=\tfrac12(D\lambda)_*\Sigma u^2+O(t^3),\qquad
V=\tfrac13(\mathscr C\lambda)_*qu^3+O(t^4).
\tag{G3}
\]

Endpoint-opacity covariance와 mean-opacity 항은 \(O(u^3)\), survival variance 항은 \(O(u^4)\)부터 시작한다. 따라서 endpoint weight \(L\)의 선두항은

\[
K_{L,2}(t,\tau)=\frac q{15}(\mathscr C L)_*(t-\tau)^2+O(t^3).
\tag{G4}
\]

Initial delta measure와 constant birth measure를 분리하면

\[
r_L^{\rm init}(t)=\frac{N_0q}{15}(\mathscr C L)_*t^2+O(t^3),\qquad
r_L^{\rm birth}(t)=\frac{Sq}{45}(\mathscr C L)_*t^3+O(t^4).
\tag{G5}
\]

둘째 식의 \(1/3\)은 \(\int_0^t(t-\tau)^2d\tau=t^3/3\)에서 온다. Birth에서의 물리 입체각을 쓰므로 별도의 birth Jacobian을 곱하지 않는다. Per-H photon 수에 \(-3HN\)도 추가하지 않는다.

현재 spectrum은 HeI와 HeII cutoff 아래에 있고 HI cutoff 위의 열린 근방에 있다. 따라서 직접 photo forcing은 HI와 heat 두 성분뿐이다. \(\lambda=cn_H(1-x)\sigma_{\rm HI}\)와 \(h=E-\chi\)를 써서

\[
v_* = \bigl((\mathscr C\lambda)_*,0,0,(\mathscr C(\lambda h))_*\bigr)^T
\tag{G6}
\]

로 두자. PHYS21의 gas linear Volterra 방정식에서 \(\eta(0)=0\), forcing이 \(O(t^2)\)이므로 \(\eta_0=\eta_1=\eta_2=0\)이고

\[
\boxed{\eta_3=\frac{N_0q}{45}v_* .}
\tag{G7}
\]

Baseline drift, density dilution, survival attenuation, gas feedback은 이 선두 계수를 바꾸지 않는다. 여기에는 초기의 evolving-gas 문제를 상수 neutral fraction 문제로 치환하는 근사가 없다. 필요한 실제 baseline 값이 오직 \(y_0(0)\)이기 때문이다.

차수 검사는 구체적으로 다음과 같다. Initial-photon endpoint abundance feedback은 \(A_{\rm loc,*}\eta_3t^3\)를 만들어 \(\eta_4\)부터 들어간다. 초기 photon의 survival memory는 \(\int_0^tK(t,s)\eta(s)ds=O(t^4)\)이므로 \(\eta_5\)부터 들어간다. Local matrix의 시간 변화 역시 \(\eta_5\)부터 들어간다. Source-born endpoint feedback은 photon measure가 \(O(t)\)라서 initial response에 대해 \(\eta_5\)부터 기여한다.

Full next coefficient를 쓰면 \(F_2t^2+F_3t^3\)를 전체 geometric gas forcing이라 할 때

\[
3\eta_3=F_2,\qquad
4\eta_4=F_3+A_{\rm loc,*}\eta_3,
\quad A_{\rm loc,*}=J_{\rm np,*}+N_0\mathsf B\mathbf L_{y,*}.
\tag{G8}
\]

이번 기여자의 birth \(t^4\) 값은 이 식의 전체 \(\eta_4\)와 다르다. Root의 별도 계산이 initial-cohort drift와 full local feedback까지 포함한 \(\eta_4\)를 담당한다.

## 3. 온도의 입자수 항과 실제 leading sign

\[
X_e=x+f(a+2b),\quad \Pi=1+f+X_e,\quad
T=\mathcal A w/\Pi,\quad \mathcal A=2e_{\rm V}/(3k_B).
\tag{G9}
\]

여기서 \(k_B=1.380649\times10^{-16}\,\mathrm{erg/K}\), \(e_{\rm V}=1.602176634\times10^{-12}\,\mathrm{erg/eV}\)다. \(\eta_{a,3}=\eta_{b,3}=0\)이므로

\[
\boxed{\eta_{T,3}=\frac{\mathcal A}{\Pi_*}\eta_{w,3}
-\frac{T_*}{\Pi_*}\eta_{x,3}.}
\tag{G10}
\]

실제 HI fit의 spectral quantities는 다음과 같다. 숫자는 `LOCAL_INITIAL_RESPONSE.json`의 결과를 반올림했다.

| Quantity | Binary64 local value |
|---|---:|
| \(\sigma_{\rm HI}(13.7\,\mathrm{eV})\) | \(6.22255406204696\times10^{-18}\,\mathrm{cm}^2\) |
| \(\lambda_*\) | \(1.865474777298942\times10^{-12}\,\mathrm{s}^{-1}\) |
| \((\mathscr C\lambda)_*\) | \(-2.0314659320992813\times10^{-12}\,\mathrm{s}^{-1}\) |
| \((\mathscr C(\lambda h))_*\) | \(-3.5409893574394624\times10^{-11}\,\mathrm{eV/s}\) |
| \(\Pi_*\) | \(2.1075\) |
| \(w_*\) | \(13.620772387478219\,\mathrm{eV/H}\) |

Product derivative는

\[
\mathscr C(\lambda h)=h\mathscr C\lambda+2E D\lambda+4E\lambda
\tag{G11}
\]

다. \(h\mathscr C\lambda\)만 유지하면 heat response를 잘못 계산한다. 두 curvature의 비는 약 17.4307100 eV이나 이것은 **두 signed coefficient의 비**다. 실제 한 event가 부여하는 excess energy 0.101565400298 eV로 해석하지 않는다.

| 선두 계수 | 값 | 단위 |
|---|---:|---|
| \(\eta_{x,3}\) | \(-4.514368737998336\times10^{-47}\) | \(\mathrm{s}^{-3}\) |
| \(\eta_{w,3}\) | \(-7.868865238754244\times10^{-46}\) | \(\mathrm{eV\,H^{-1}\,s^{-3}}\) |
| \(\eta_{T,3}\) | \(-1.817528627099142\times10^{-42}\) | \(\mathrm{K\,s^{-3}}\) |
| 열에너지의 \(\eta_{T,3}\) 기여 | \(-2.888553238723895\times10^{-42}\) | \(\mathrm{K\,s^{-3}}\) |
| 입자수의 \(\eta_{T,3}\) 기여 | \(+1.0710246116247533\times10^{-42}\) | \(\mathrm{K\,s^{-3}}\) |

따라서 initial quadratic response는 HII fraction과 열에너지/H를 줄이고, 온도도 줄인다. 전자·총 입자수 감소는 온도를 올리는 방향으로 작용하지만 여기서는 열에너지 감소가 더 크다. 이것은 \(t\to0^+\)의 첫 비영차 계수에 대한 결론이며 유한시간 끝점의 차이나 remainder bound가 아니다.

## 4. He가 한 차수 늦게 반응하는 방식

직접 He photon forcing은 열린 초기 근방에서 0이다. 그러나 He fractions는 전자수와 온도를 공유한다. \(a,b\)를 고정한 local He RHS는

\[
\dot a=n_eG_a(T),\qquad\dot b=n_eG_b(T),
\tag{G12}
\]

\[
G_a=(1-a-b)\beta_1-a\alpha_1-a(d_1+d_2)-a\beta_2+b\alpha_2,
\quad
G_b=a\beta_2-b\alpha_2.
\tag{G13}
\]

\(\beta_j,\alpha_j,d_k\)는 pinned FT03의 CI, RR, two-DR coefficient다. Leading response에서 \(\eta_a=\eta_b=0\)인 차수만 사용하므로

\[
\boxed{
\eta_{a,4}=\frac14\left[n_HG_a\eta_{x,3}+n_eG_a'\eta_{T,3}\right],\qquad
\eta_{b,4}=\frac14\left[n_HG_b\eta_{x,3}+n_eG_b'\eta_{T,3}\right].
}
\tag{G14}
\]

이는 \((J_{\rm np,*}\eta_3)_{a,b}/4\)와 같다. HI의 instantaneous photo-abundance matrix는 He rows에 0이므로 He 선두 계수에는 추가 photo term이 없다. Gas memory도 아직 도달하지 않는다.

| He \(t^4\) 계수 | 전자밀도 변화 | 온도 변화 | 합계 |
|---|---:|---:|---:|
| \(\eta_{a,4}\) [\(\mathrm{s}^{-4}\)] | \(-2.47131123819\times10^{-63}\) | \(-1.03366199597\times10^{-62}\) | \(-1.28079311979\times10^{-62}\) |
| \(\eta_{b,4}\) [\(\mathrm{s}^{-4}\)] | \(+4.94287696595\times10^{-64}\) | \(-3.12867497133\times10^{-64}\) | \(+1.81420199462\times10^{-64}\) |

이 초기 상태에서는 HeIII가 순재결합 중이므로 \(G_b<0\)다. 전자밀도 감소가 재결합 속도를 줄이는 항은 양수다. 냉각이 만드는 음의 항보다 그 크기가 크므로 HeIII response가 양수로 시작한다. 이는 직접 He photoionization을 켰다는 뜻이 아니다. HeII response는 음수이며, HeI fraction은 nuclei 보존에 따라

\[
\eta_{{\rm HeI},4}=-\eta_{a,4}-\eta_{b,4}
=1.2626510998426593\times10^{-62}\,\mathrm{s}^{-4}
\tag{G15}
\]

로 시작한다. 온도 감소만 보고 모든 ionization fraction이 같은 부호로 변한다고 결론내릴 수 없다.

## 5. 연속 birth source의 명확한 분리

Full FLRW baseline과 그 linear causal operator를 고정하고, 순수 geometric forcing을 \(r^{\rm init}+r^{\rm birth}\)로 나눈 particular responses를 정의한다. 이 정의에서

\[
\boxed{\eta^{\rm birth}_4=\frac{Sq}{180}v_*
=\frac{S}{4N_0}\eta^{\rm init}_3,}
\tag{G16}
\]

\[
\boxed{\eta_{a,b,5}^{\rm birth}=\frac15(J_{\rm np,*}\eta_4^{\rm birth})_{a,b}
=\frac{S}{5N_0}\eta_{a,b,4}^{\rm init}.}
\tag{G17}
\]

| Birth particular의 첫 계수 | 값 |
|---|---:|
| HII \(t^4\) [\(\mathrm{s}^{-4}\)] | \(-1.1285921844995839\times10^{-60}\) |
| \(w\), \(t^4\) [\(\mathrm{eV\,H^{-1}\,s^{-4}}\)] | \(-1.9672163096885608\times10^{-59}\) |
| \(T\), \(t^4\) [\(\mathrm{K\,s^{-4}}\)] | \(-4.543821567747854\times10^{-56}\) |
| HeII \(t^5\) [\(\mathrm{s}^{-5}\)] | \(-2.561586239577681\times10^{-76}\) |
| HeIII \(t^5\) [\(\mathrm{s}^{-5}\)] | \(+3.6284039892362116\times10^{-78}\) |

이는 전체 해를 source amplitude \(S\)로 미분한 결과가 아니다. \(S\)를 바꾸면 baseline과 propagation operator도 바뀐다. 특히 전체 He \(t^5\)에 존재하는 모든 \(S\)-dependent term을 식 (G17)로 대체해서는 안 된다. 현재 \(N_0\ne0\) 문제의 H/w full \(t^4\) 계수 역시 birth particular만으로 주어지지 않는다.

## 6. 국소 보존·regularity·검산 상태

Photon count는 \(\dot N_2=-A_{{\rm HI},2}\)를 만족한다. 직접 event가 만드는 선두 gas change가 \(\dot\eta_x=A_{{\rm HI},2}+O(t^3)\)이므로

\[
[t^3]N_2=-\eta_{x,3}=4.514368737998336\times10^{-47}\;\mathrm{photon\,H^{-1}\,s^{-3}}.
\tag{G18}
\]

Primary matter energy의 event 부분은 \(Q+\chi A\)이므로 선두 forcing의 합은

\[
\mathscr C(\lambda(E-\chi))+\chi\mathscr C\lambda
=\mathscr C(\lambda E).
\tag{G19}
\]

Transport가 만드는 photon energy의 \(t^2\) 변화는 gas의 \(t^3\) leading response와 차수가 다르다. 전체 energy ledger에는 prescribed-geometry redshift work가 필요하다. 식 (G19)는 local primary transfer의 일관성이고 전체 ledger를 수치적으로 적분했다는 기록은 아니다.

첫 계수에는 \(\mathscr C L\)가 존재하는 C2 spectral regularity와 국소 연속 baseline이 충분하다. Integer-order higher expansion을 쓸 때에는 해당 추가 time/energy derivative가 필요하다. 실제 initial state는 fraction simplex, HI/He cutoff, FT03 temperature domain의 내부에 있으므로 analytic fit의 국소 근방이 존재한다. 그 근방의 정량적인 최대 시간이나 유한시간 remainder를 이 문서에서 증명하지는 않았다.

`local_initial_response.py --output NEW_PATH.json`을 실제 실행했다. 고정 PHYS21 local-gas 코드의 함수만 import했고 old entrypoint를 호출하지 않았다. 새 shear forcing 방향을 \((1,0,0,(\mathscr C Q)/(\mathscr C\lambda))\)로 scale한 뒤 다음을 비교했다.

- Nonphoto JVP 4성분과 complex-step smooth RHS.
- 입자수까지 포함한 temperature derivative 1성분과 complex step.
- Initial-photon endpoint abundance를 포함한 instantaneous coupled JVP 4성분과 complex step.
- 독립 식 (G14)의 electron/temperature 분해 2성분과 inherited analytic JVP.

실제 결과는 **11/11 PASS, exit 0**, 최대 상대차 \(5.750864319392478\times10^{-16}\), complex step \(10^{-24}\), 허용오차 \(2\times10^{-12}\)다. 새 physical-direction 한 개의 여러 성분을 확인한 것이며 독립된 11개 물리 법칙을 증명한 것으로 세지 않는다. `EXECUTION.json`에 실제 command, elapsed wall time, script/result SHA를 남겼다. 최초 실행부터 통과했고 실패·허용오차 변경은 없었다.

Ordinary binary64로 source의 initial-w expression을 계산하면 역변환 온도가 \(49999.99999999999\) K가 된다. 이 수치는 기록했고 임의로 50000 K로 덮어쓰지 않았다. Root의 exact-real-input 고정밀 수치와 비교할 때 이 마지막 bit 수준의 차이와 binary64 연산 차이를 허용해야 한다. Native implementation equivalence나 rigorously enclosed derivative의 증거로 사용하지 않는다.

`[160,161] FAIL`, `tick160`, auxiliary escape `FAIL`, HH/RCT/CR `OFF`, precision atomic `PARKED`를 보존한다. Finite-time coupled response, physical promotion, native stage differentiability, source/default/runtime mutation은 이 기여 범위 밖이다.

## 7. 직접 읽은 source와 상속한 근거

다음 source의 relevant definitions를 읽었다. Local bytes와 SHA는 `DEPENDENCIES.json`에 기록한다. Root가 이번 loop에 current commit/tree identity를 확인한 결과에 결속하며 이 기여자는 별도 중복 remote retrieval을 수행하지 않았다.

- [paired_runtime.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/paired_runtime.rs): actual IC, initial-w, 13.7 eV cohort, source amplitude, per-H normalization.
- [coupled_primary.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/coupled_primary.rs): zero-photon FT03 raw call, event/thermal units, primary ownership.
- [ft03_controlled.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/ft03_controlled.rs): CI/RR/two-DR stoichiometry and thermal channels.
- [ft03_rates.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/ft03_rates.rs): local rates and logarithmic thermal derivatives.
- [hhe_events.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/hhe_events.rs): \(c,k_B,e_{\rm V}\), thresholds and population conventions.
- [atomic_provider.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3dc42c64ab32075f0a59c96af3ddf7435d9b7f97/rust/rei_microphysics/src/atomic_provider.rs): HI Verner smooth fit and distinct opacity cutoffs.

PHYS21 report/source-gas derivation은 닫힌 입력으로 소비했다. 이 note의 새 결과는 초기 time-order 판정, actual leading coefficients, He sign decomposition과 새 physical-direction 국소 검산이다.
