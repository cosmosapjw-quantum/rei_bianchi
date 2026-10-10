# ACCEL02 N1 — 장구간 물리 provider의 실제 native 연결

판정 제안은 **N1 범위 구현 검증 완료, 독립 승격 판정 대기**이다. `z_a=15.9→4`에 필요한 source/background/초기 기체 계약을 고정하고, 기존 IGM 저온 Case-A 함수를 실제 native `axisym_coupled_derivative` 호출에 연결했다. 기존 `PhysicalHistory`, FT03 고온 범위와 source-bound 짧은 receiver의 guard는 변경하지 않았다. 이 보고서의 point 검사는 trajectory 적분이나 전체 장기 history의 수렴 판정이 아니다. `RUN002`는 재실행하지 않았다.

## 선택한 입력과 최신 결과의 역할

- IGM `39c39eab1cc2f1a215723680accc123e67ef13b6`의 `igm_rates.rs`, `igm_state.rs`, `igm_thermal.rs`를 **byte-identical**로 import했다. Grackle3.4.1 원 commit은 `af7939494ce65007887ada7b98d1813df6843346`이다. 원 저작권·literal-C reference와 manifest도 유지했다.
- 물리 stack `8d9526a75e85202764e845c7d5d79d7f903e7c55`의 기존 `background.py`·`hm12_data.py` 및 원저자 두 table은 수정하지 않았다. `provider.py`가 실행 전에 네 source hash를 검사한다.
- 새 cold endpoint `51da705e4f24bd201444ac3e81db495b50a7d8f7`의 실제 report/contract도 읽었다. 그 결과는 HII RR+Compton, neutral He, zero photons, 별도 cosmology의 finite FLRW interval이다. 이를 H/He spectral reionization provider나 새 cosmology의 IC로 잘못 승격하지 않았다.
- Hubble/cosmology는 HM12 역사적 `(h,Omega_m,Omega_Lambda,Omega_b,Y)=(.7,.3,.7,.045,.24)`이다. `r=s_i/H_i`, `|r|≤.1`은 controlled sensitivity 범위이며 관측상 허용된 Bianchi 우주를 뜻하지 않는다.
- 초기 기체는 `T=20 K`, `(x_HII,x_HeII,x_HeIII)=(2e-4,0,0)`를 명시적으로 택한 **conditional Cauchy data**다. HyRec output, photoionization equilibrium 또는 관측 추정값이 아니다. charge neutrality와 열 EOS로 에너지를 정한다. 이 IC의 과학적 민감도는 후속 history에서 별도로 보아야 한다.
- `UVB.out(z=15.9)`는 최초 isotropic photon field에만 쓰고, 이후에는 `emissivity.out`만 공급원으로 쓴다. 후속 `J_nu(z)`나 Gamma를 해에 덮어쓰지 않는다.

## 단위와 연산자

metric은 `(-,+,+,+)`. `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`이며 `s=dot b`, `sigma²=3s²`이다. 광자 grid는 initial-frame conserved covector `q`와 `mu_0`를 사용한다. `R=E/q`라 놓으면

\[
R=\frac{\sqrt{(1-\mu_0^2)e^{2b}+\mu_0^2e^{-4b}}}{a_{\rm rel}},\qquad
\frac{d\Omega}{d\Omega_0}=\frac{1}{a_{\rm rel}^3R^3}.
\]

HM12 emissivity의 원 단위는 `erg s^-1 Hz^-1 comoving-Mpc^-3`다. proper angle-integrated source per `d ln E`는 `epsilon_nu (1+z)^3/(Mpc^3 h)` [photons cm^-3 s^-1]이다. quadrature weight `w_j=dlnq dmu_0/2`를 적용한 초기 reference-volume count는 `N_j=a_rel³ n_j`이며

\[
\dot N_j = \frac{w_j}{R_j^3}\,\dot n_{\ln E}(E_j,z)
-c\sum_a n_a\sigma_a(E_j)N_j.
\]

현재 stage의 같은 `Gamma_a`와 `(E-chi_a)`를 photon sink, ionic events, binding 증가와 heating에 한 번씩 사용한다. H/He charge·baryon sources와 local energy terms를 기존 native AXI guard에 실제로 넘긴다. 재결합의 binding release+kinetic cooling, DR·CE·freefree radiation은 escape에 기록하고 ionizing field에 재주입하지 않는다. 따라서 이름은 **primary-only Case-A escape**이며 explicit diffuse 또는 full OTS가 아니다. cooling의 `CE_HeI`는 `ne² nHeII`이고 그 계수 단위는 erg cm6/s이다.

온도 `1≤T≤10^6 K`는 import한 Grackle subset의 **operational domain**이다. empirical fit의 정확도 보증이 아니다. source CI floors, CE caps, DR low branch 정책은 원 코드대로 보존했다. fraction/temperature/overflow 오류를 clipping하지 않는다.

CMB는 `T_gamma=2.7255(1+z)`인 prescribed isotropic blackbody bath다.

\[
Q_{\mathrm{CMB}\to g}=\frac{4\sigma_Ta_Rk_B}{m_ec}n_eT_\gamma^4(T_\gamma-T).
\]

이는 signed external power다. escape나 active-photon birth로 넣지 않는다. 이 CMB 가정은 Bianchi에서 진화하는 실제 anisotropic CMB를 푼 결과가 아니다. gas/radiation stress의 Einstein backreaction도 없다. reference-volume 적분 ledger는

\[
E_{\gamma+\mathrm{thermal+binding}}+E_{\rm esc}+W-E_{\rm emissivity}-E_{\mathrm{CMB}\to g}=E_0
\]

형태이며 `Wdot=a_rel³[H u_gamma+2s Delta p_gamma+2H u_th]`다. 가스 열변수는 `w=u_th/n_H` [eV/H]이므로 expansion은 `-2H w`이고, proper thermal density의 `-5H u_th`와 혼동하지 않는다.

## 물리 source band와 중요한 남은 한계

출력 source는 **physical E=10–50000 eV**로 고정한다. source support 밖은 선택한 truncated model의 정확한 zero다. 초기 `q>50000 eV` count도 zero다. 그러나 후대의 50keV source까지 담으려면 `q_max=50000 max(a_perp_rel,a_parallel_rel)`가 필요하다. FLRW에서는 최종 `q_max≈169000 eV`이다. 이 grid 준비가 없으면 fixed-q라도 후반 고에너지 source를 빠뜨린다.

native driver는 E>50keV node의 `N=S=0`일 때만 inactive characteristic으로 처리한다. 그곳의 nonzero count/source는 기존 atomic energy guard로 거절한다. 저에너지로 redshift된 photon은 버리지 않고 count를 유지하며 threshold 아래의 cross section은 zero다.

실제 table에서 50keV 위의 source tail을 별도로 적분했다. H-ionizing photon count에 대한 누락 비율은 z15.9에서 `5.86e-7`, z4에서 `2.16e-5`다. **에너지 누락 비율은 각각 0.300%와 7.668%**다. 작은 count fraction을 근거로 전체 energy/heating 정확도를 주장해서는 안 된다. 이 결과는 source power 비율이지 gas에 deposition되는 열 비율도 아니다. 높은 에너지에서 Compton/secondary/CR가 빠져 있으므로 full HM12 spectrum 또는 full deposition 모델은 HOLD이다.

## 실제 검증 및 실패 분류

- Python provider 검사 3개와 Rust native adapter 검사 4개가 실제 PASS했다. 새 API의 IC/source 역할, late source coverage, Jacobian, 같은 stage의 IGM 호출 일치, signed CMB 분리, reference-volume 단위, invalid input 및 high-q 정책을 확인했다.
- 기존 literal-C reference의 96개 전체 grid를 반복하지 않고 endpoint/join을 포함한 8개 행만 새 binary binding에 대조했다. 상대오차 기준 `1e-11`, zero는 exact zero를 유지했다.
- 새 source/background를 사용한 51개 point probe에서 최대 scaled photon/energy residual은 `1.1716555455768401e-16`이었다. 이때 gas path는 고정 fractions/adiabatic temperature를 넣은 **domain probe**다. 실제 coupled solution을 표시하는 history로 쓰면 안 된다.
- 최초 build는 cargo 부재로 exit127: `RUNTIME_ENVIRONMENT`. root가 설치한 Rust1.90.0에서 실제 release build와 tests를 실행했다.
- 최초 Python test는 oracle이 10eV 아래 source-band zero를 누락한 `IMPLEMENTATION(test)` 실패였다. production source를 바꾸지 않고 expected support를 수정했다.
- 최초 CMB test는 작은 bath 변화량을 큰 photoheating 차이에서 빼 cancellation 오차가 기준을 넘은 `NUMERICAL(test design)` 실패였다. 동일 기준을 유지하며 photon/expansion 없는 CMB 분리 probe로 고쳤다. 원 실패 로그를 보존했다.

현재 실행 binary SHA256은 `BINDING_CHECKS.json`에 있다. native source digest와 source imports는 `SOURCE_IDENTITY.json`, `IMPORTED_SOURCE.json`에 있다. 독립 scientific decision과 전체 history acceptance는 root 통합 단계의 별도 증거를 따른다.

## 다음 실제 실행

`provider.py`의 `HistoryProvider`와 `Native`가 N2/root 통합 API다. `ABI.json`은 입력/반환 순서와 단위를 고정한다. N2 characteristic time integration을 물려 전체 선택 구간에서 gas temperature·H/He fractions·radiation·ledger를 함께 진화시켜야 한다. 그때 실제 timestep/spectral convergence, 초기조건/Case-A sensitivity와 누락 고에너지 source 영향은 아직 남는다. N1 완료를 N3 장기 history 완료로 표현하지 않는다.
