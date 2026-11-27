# H/He 재결합 에너지에서 종별 광자 응답으로의 보존적 연결

2026-10-12 · BASS_HE RUX03 supplier 연구

## 1. 연구 질문과 적용 범위

회수된 warm HM12 H/He 모형의 실제 화학·열 계산은 FT03 Case A이다. 재결합 사건의 결합에너지와 전자 운동에너지는 현재 `escaped_energy_rate`에 합쳐진다. 이 계산을 재사용하면서 명시적 재결합 광자 수송 또는 국소 재흡수로 확장할 때, 어떤 양을 옮겨야 하고 어떤 원자 자료가 추가로 필요한지를 유도한다.

이 노트의 새 결과는 기존 source에 대한 사건·에너지 대응식과 고정 배경에서의 응답 핵이다. 다종 coupled OTS 자체는 Friedrich et al. (2012), §3.1.2에 선행 문헌이 있다. 여기서는 그 물리를 현재 FT03의 사건 장부, Bianchi 광자 특성선, 저장된 warm 입력에 맞춰 표현한다. 새로운 원자 spectrum 또는 새 coupled history를 계산한 것으로 분류하지 않는다.

계량 부호는 $(-,+,+,+)$, 가스는 비기울어진 정상 관측자와 공운동한다. $t$는 가스 고유시간, $H=\Theta/3$이다. 밀도는 proper $\mathrm{cm^{-3}}$, 사건율은 $\mathrm{cm^{-3}s^{-1}}$, 단면적은 $\mathrm{cm^2}$이다. $E,\chi,\epsilon_{\rm kin}$은 eV 단위로 쓰고, 에너지 밀도·가열식에는 $\varepsilon_{\rm eV}=1.602176634\times10^{-12}\,\mathrm{erg/eV}$를 곱한다. $c$와 $k_B$를 유지한다. $h=2\pi\hbar$는 광원 단위 변환에서 유지한다.

기저상태 HI/HeI/HeII의 등방적 총 광이온화 단면적, 단일 primary 전자 사건, Maxwell 전자 율의 선택된 source를 사용한다. 들뜬 상태의 정렬·편광·미분 방출 source는 해당 state와 tensor 규약을 별도로 제공할 때 연결한다.

## 2. 세 이온화 edge로 쓰는 원자핵·전하·내부에너지

종 순서를 $\boldsymbol n=(n_{\rm HI},n_{\rm HII},n_{\rm HeI},n_{\rm HeII},n_{\rm HeIII},n_e)^T$로 고정한다. HI, HeI, HeII 이온화의 열벡터를 모으면

$$
S=\begin{pmatrix}
-1&0&0\\
1&0&0\\
0&-1&0\\
0&1&-1\\
0&0&1\\
1&1&1
\end{pmatrix}.
$$

광이온화 사건율 $\boldsymbol A$, 충돌 이온화 $\boldsymbol C$, RR 및 같은 edge의 DR를 합친 재결합 $\boldsymbol R_{\rm tot}$에 대해 국소 화학 source는

$$\boldsymbol{\mathcal S}_{\rm chem}=S(\boldsymbol A+\boldsymbol C-\boldsymbol R_{\rm tot}).$$

팽창하는 proper 밀도의 실제 방정식은 $\dot{\boldsymbol n}+3H\boldsymbol n=\boldsymbol{\mathcal S}_{\rm chem}$이다. 원자핵당 분율은 같은 팽창항이 나누어져 사라진다. 음이온·분자종을 활성화하면 이에 맞춰 종과 $S$를 확장한다.

원자핵·전하의 세 행벡터를

$$L=\begin{pmatrix}1&1&0&0&0&0\\0&0&1&1&1&0\\0&1&0&1&2&-1\end{pmatrix}$$

로 두면 $LS=0$이다. 내부 이온화 에너지 계수는

$$\boldsymbol b=(0,\chi_H,0,\chi_{\rm HeI},\chi_{\rm HeI}+\chi_{\rm HeII},0)^T,$$

이므로 $\boldsymbol b^TS=\boldsymbol\chi^T$이다. 따라서 같은 사건율에서 자유전자 source와 내부에너지 source는 각각

$$\dot n_e|_{\rm chem}=\boldsymbol1^T(\boldsymbol A+\boldsymbol C-\boldsymbol R_{\rm tot}),\qquad
\dot u_{\rm ion}|_{\rm chem}=\varepsilon_{\rm eV}\boldsymbol\chi^T(\boldsymbol A+\boldsymbol C-\boldsymbol R_{\rm tot}).$$

RCT의 $\mathrm{HI+HeIII\to HII+HeII+\gamma}$ 화학량론은 $\boldsymbol v_{\rm RCT}=S_H-S_{\rm HeII}=(-1,1,0,1,-1,0)^T$이다. 직접 전자 source는 0이고, 내부에너지는 $-Q$만큼 감소한다. 여기서 $Q=\chi_{\rm HeII}-\chi_H$이다. 이 직접 전자 보존은 다른 반응과 결합한 후속 전자 이력의 변화까지 소거하는 관계로 사용하지 않는다.

## 3. 현재 Case A escape 장부와 명시적 방출 source

아래 §3–6의 $R_j$와 $\boldsymbol R$는 RR만 나타낸다. DR는 resonance별 별도 사건으로 같은 보존 구조를 적용한다. 상위 이온의 밀도를 $n_{j,+}$라 하면 RR 사건율은 $R_j=n_e n_{j,+}\alpha_j^A(T)$이다. 회수된 FT03는

$$\epsilon_{{\rm kin},j}=\frac{k_BT}{\varepsilon_{\rm eV}}\left(\frac32+\frac{d\ln\alpha_j}{d\ln T}\right)$$

를 사용한다. 따라서 RR의 현재 local thermal 및 escaped-energy source는

$$\mathcal Q_{{\rm th},j}=-\varepsilon_{\rm eV}R_j\epsilon_{{\rm kin},j},\qquad
\mathcal Q_{{\rm esc},j}=\varepsilon_{\rm eV}R_j(\chi_j+\epsilon_{{\rm kin},j}).$$

내부에너지 감소 $-\varepsilon_{\rm eV}\chi_jR_j$까지 합하면 0이다. DR는 같은 계산에서 resonance별 사건율과 전자 에너지를 사용한다. 이 RR 운동에너지 식은 온도 독립 microscopic cross section을 Maxwell 평균한 경우의 로그미분 관계를 사용한 source 모형이다. 이번 작업은 그 기존 모형과 domain을 유지한다.

명시적 방출을 위해서는 $\eta_j(E)\ge0$, 단위 photons/(event eV)를 제공한다. cascade 전체를 한 사건의 source로 묶으면 $\int\eta_j\,dE$는 1보다 클 수 있다. 최종 원자가 기저상태이고 추적하지 않는 내부에너지·반동이 없다는 근사에서는

$$\int E\eta_j(E)\,dE=\chi_j+\epsilon_{{\rm kin},j}.$$

방출 source는 $q_{\rm rec}(E)=\sum_jR_j\eta_j(E)$이다. 이 source에 넣은 에너지만큼 기존 escape 장부에서 빼면 원래 RR 종 변화와 kinetic cooling을 그대로 재사용할 수 있다. 추적 에너지창 밖의 광자는 별도 outside-band 광자·에너지 장부로 보낸다. 준안정 상태에 남는 에너지나 recoil을 모델링하면 위 식에 그 별도 에너지 항을 추가한다.

광이온화는

$$a_s(E)=c n_s\sigma_s(E)n_E(E),\quad A_s=\int a_s(E)dE,$$
$$\mathcal Q_{{\rm ph},s}=\varepsilon_{\rm eV}\int(E-\chi_s)a_s(E)dE$$

로 계산한다. 광자 에너지에서 $\varepsilon_{\rm eV}\int Ea_s\,dE$가 빠지고, 그중 $\varepsilon_{\rm eV}\chi_sA_s$는 내부에너지로 들어간다. RR와 흡수를 합친 local interaction source는

$$\dot u_{\rm ion}|_{\rm int}+\mathcal Q_{\rm th}+\dot u_\gamma|_{\rm int}+\mathcal Q_{\rm esc}=0$$

을 만족한다. 서로 다른 clock 또는 proper/comoving 정의로 저장된 항은 먼저 같은 단위로 바꿔 이 식에 넣는다. 재결합 escape **energy**만 저장된 기존 결과는 $q_{\rm rec}$의 photon count를 정하지 않으므로, 아래의 energy-measure 응답을 먼저 사용할 수 있다.

현재 native 값은 $\chi=(13.598434599702,24.587389011,54.41776)$ eV다. Verner 단면적의 support cutoff는 $(13.60,24.59,54.42)$ eV이며 서로 다른 필드다. 이번 재사용에서는 각각 그대로 고정한다.

## 4. Bianchi 광자 특성선에서의 정확한 한 광자 응답

가스 정상 frame에서 광자 에너지는

$$\frac{dE}{dt}=-H_\parallel(t)E,\qquad H_\parallel=H+\sigma_{ab}e^ae^b$$

를 따른다. 축대칭 LRS에서는 $H_\parallel=H+s(3\mu^2-1)$이다. 방향 $\boldsymbol e(t)$도 이미 채택된 특성선을 따른다. 기하와 가스 이력을 prescribed로 고정하고 단일 primary 흡수까지 추적하면

$$\lambda_s(t)=c n_s(t)\sigma_s(E(t)),\quad
\Lambda(t)=\sum_s\lambda_s(t)+\lambda_{\rm out}(t),\quad
\mathcal S(t,b)=\exp\left[-\int_b^t\Lambda(v)dv\right].$$

$\lambda_{\rm out}$은 별도로 정의된 시스템 밖 이탈만 나타낸다. 이미 $\lambda_s$에 포함한 같은 HI 흡수를 이 채널에 다시 넣지 않는다. 현재 homogeneous 기준은 $\lambda_{\rm out}=0$이다.

$b$에 방출된 광자의 최종시각 $t_f$까지 종별 흡수확률, 이탈확률 및 잔존확률은

$$P_s(b)=\int_b^{t_f}\lambda_s(t)\mathcal S(t,b)dt,\quad
P_{\rm out}(b)=\int_b^{t_f}\lambda_{\rm out}(t)\mathcal S(t,b)dt,\quad
P_{\rm surv}(b)=\mathcal S(t_f,b).$$

$\partial_t\mathcal S=-\Lambda\mathcal S$를 적분하면

$$\sum_sP_s+P_{\rm out}+P_{\rm surv}=1.$$

각 항은 비음성이다. 가열의 에너지 응답은

$$K_{{\rm heat},s}(b)=\int_b^{t_f}[E(t)-\chi_s]\lambda_s(t)\mathcal S(t,b)dt.$$

단면적 support에서 $E\ge\chi_s$가 확보되면 이 값도 비음성이다. 흡수된 에너지 $K_{E,s}=\int E\lambda_s\mathcal S\,dt$와 geometry work

$$W_{\rm geom}(b)=\int_b^{t_f}H_\parallel(t)E(t)\mathcal S(t,b)dt$$

에 대해 $d(E\mathcal S)/dt=-(H_\parallel+\Lambda)E\mathcal S$이므로

$$E_b=E_fP_{\rm surv}+\sum_sK_{E,s}+K_{E,\rm out}+W_{\rm geom}.$$

즉 $K_{E,s}=\chi_sP_s+K_{{\rm heat},s}$가 수·내부에너지·열을 잇는다. $H_\parallel<0$인 방향에서는 $W_{\rm geom}$이 음수가 될 수 있으며 이는 청색이동이다. 이 기하학적 일은 열원과 별도다. 여기서 확률은 한 광자 또는 원자핵당 packet의 양이므로 추가 $a^{-3}$ 희석 인자를 곱하지 않는다. proper 에너지 밀도로 집계할 때의 체적 변화는 별도 density conversion이 담당한다.

이 식은 처방 이력 위의 선형 응답이다. 재흡수가 가스를 바꾸는 coupled 계산에서는 바뀐 이력의 $n_s,T,E$로 같은 구조를 다시 사용한다.

## 5. 방출 시각을 유지한 동결계수 응답

한 점의 밀도·에너지와 $\lambda_s$를 $\Delta t$ 동안 고정하고 이탈·적색이동을 생략한다. $\tau=\Lambda\Delta t$, $p_s=\lambda_s/\Lambda$라 두자. 처음에 들어온 한 광자는

$$P_s^{\rm initial}=p_s(1-e^{-\tau})$$

의 확률로 흡수된다. 같은 구간에서 일정한 source로 방출된 광자에 대해 방출 시각을 균일 평균하면

$$P_s^{\rm uniform}=p_s F(\tau),\qquad
F(\tau)=1-\frac{1-e^{-\tau}}{\tau}.$$

이는 $q$가 상수인 $\dot N=q-\Lambda N$, $N(0)=0$의 정확해 $N_f=q(1-e^{-\tau})/\Lambda$와 $A=q\Delta t-N_f$에서도 바로 나온다. 작은 $\tau$에서는

$$F(\tau)=\frac\tau2-\frac{\tau^2}{6}+\frac{\tau^3}{24}-\frac{\tau^4}{120}+O(\tau^5).$$

따라서 초기 광자와 지속 방출 광자는 optically thin 구간에서 약 두 배 다른 흡수분율을 가진다. $\tau\to\infty$에서 전체 흡수분율 $1-e^{-\tau}$와 $F(\tau)$는 1에 접근하고, 각 종의 확률은 $p_s$에 접근한다. $\Lambda=0$은 연속극한 $P_s=0$, $N_f=q\Delta t$로 처리한다.

이는 P03A의 ‘각 segment 방출 에너지를 왼쪽 끝에 배치한 상계’와 다른, 방출 시간분포를 지정한 응답이다. P03A의 원래 상계를 이 값으로 덮어쓰지 않는다. 일정 source 가정의 타당성은 실제 source 이력에서 별도로 평가한다. 이번 단일점 수치는 near-threshold 적색이동과 gas evolution을 포함한 P03A 원 수송 계산을 대체하지 않는다.

## 6. 다종 OTS를 현재 사건식으로 투영

흡수 시간이 가스·source·기하 변화보다 짧고 ionizing photon의 장거리 escape와 storage가 무시되는 국소 한계에서, 사건 $j$가 만든 photon source의 종별 수율은

$$B_{sj}=\int p_s(E)\eta_j(E)dE.$$

아래 문턱 photon의 $p_s$는 0이고, 별도 loss가 있으면 $\sum_s p_s\le1$이다. 따라서 모든 cascade를 포함한 $\sum_sB_{sj}$는 조건에 따라 1보다 클 수 있다. 화학식은

$$\dot{\boldsymbol n}|_{{\rm rec+reabs}}=S(B-I)\boldsymbol R.$$

현재 HI/HeI/HeII의 각 scalar Case B는 특별한 대각 근사로 복원된다. 즉 ground-state recombination photon만 같은 종에 되돌리고 그 수율을 $(\alpha_j^A-\alpha_j^B)/\alpha_j^A$로 놓으면

$$B_{sj}=\delta_{sj}\left(1-\frac{\alpha_j^B}{\alpha_j^A}\right),\qquad
S(B-I)\boldsymbol R=-S\,\mathrm{diag}(n_en_{j,+})\boldsymbol\alpha^B.$$

He의 ionizing continuum·cascade가 HI 또는 HeI를 이온화하면 $B$의 비대각 원소를 보존해야 한다. 예를 들어 hydrogenic HeII Ly-alpha의 약 $40.8$ eV 광자는 HI/HeI 이온화를 지원한다. 그것의 branching은 중성 HI/HeI 밀도와 단면적으로 정한다. 이 예는 실제 cascade multiplicity나 세기 값을 가정하지 않는다.

재결합 kinetic cooling과 재흡수 가열의 합은

$$\mathcal Q_{{\rm rec+reabs}}=\varepsilon_{\rm eV}\sum_jR_j\left[-\epsilon_{{\rm kin},j}+\sum_s\int(E-\chi_s)p_s(E)\eta_j(E)dE\right].$$

만일 한 사건의 모든 방출 에너지가 primary 이온화 채널에 완전히 재흡수되면, 에너지 정규화와 $\sum_sp_s=1$로

$$\frac{\mathcal Q_j}{\varepsilon_{\rm eV}R_j}=\chi_j-\sum_s\chi_s B_{sj}$$

를 얻는다. 같은 사건의 내부에너지 변화가 정확히 반대이므로 보존된다. Escape 또는 비이온화 cascade 에너지는 우변에서 그 에너지 몫만큼 차감하고 별도 복사 장부에 더한다.

## 7. spectrum이 아직 없을 때 재사용할 수 있는 energy-measure 결과

기존 escape-energy 장부는 양의 방출 에너지 측도 $dW(E)$의 총량 $W=\int dW$를 제공한다. 여기서는 방출 시각과 방향을 고정한다. 전체 source의 시간·방향을 합칠 때에는 $dW(b,E,\Omega)$와 공동 지원집합 $\mathcal D$를 사용하고 그 전체 영역에서 infimum/supremum을 취하거나, 확인된 source의 조건부 평균 응답핵을 사용한다. 고정한 한 광자 응답에서 종별 흡수수와 가열은

$$A_s=\int\frac{P_s(E)}{E}dW(E),\qquad
H_s=\int\frac{K_{{\rm heat},s}(E)}{E}dW(E).$$

여기서 $W,H_s$는 같은 eV 기반 energy 단위를 사용한다. 에너지 정규화가 있는 양의 source에 대해 $dW/W$가 확률측도이므로, 임의의 선택된 선형 관측량 $O=\int K_O(E)dW(E)$는

$$W\inf_{E\in\mathcal D}K_O(E)\le O\le W\sup_{E\in\mathcal D}K_O(E)$$

를 만족한다. 여러 관측량의 벡터는 응답 곡선의 convex hull에 속한다. 실제 수율 모멘트가 더 제공되면 같은 집합에 추가 선형 제약을 넣어 범위를 줄인다.

이 관계는 total rate 또는 total energy로 spectrum 값을 임의 지정하지 않고도, 이미 계산된 energy 장부를 관측량 선별에 활용하는 방법이다. 유한 표에서 얻은 최소·최대는 그 유한 표와 동결 이력에 대한 범위로 보고한다. 연속 energy domain의 bound에는 그 domain의 supremum 검증이 추가로 필요하다. spectrum이 지원하는 에너지창과 omitted-energy budget을 명시하면 그 부분별 bound를 합칠 수 있다.

## 8. 검산·상태와 구현 전달

Wolfram Language로 $LS=0$, $b^TS=\chi^T$, RCT 벡터/전자 source, RR+흡수 에너지 source 합 0, uniform-birth ledger와 급수, 대각 Case B 극한을 symbolic 확인했다. 최초 호출의 괄호 syntax 오류와 수정 뒤 출력은 모두 `evidence/WOLFRAM_CHECKS.json`에 남겼다. 단순 bracket 수정이었고 물리식은 변경하지 않았다.

확률·에너지 응답식과 energy-measure 부등식은 위 적분 항등식과 양의 측도로 직접 유도했다. 수치 screening은 별도 `screening/`에 있으며 원자 spectrum 또는 새 coupled trajectory 실행을 포함하지 않는다. 원자 모델의 정확도, 기존 native 실행의 provenance, 이후 owner의 실제 callback 주입은 각 source 기록과 독립 판정의 범위를 따른다.

구현에 전달할 최소 양은 (i) species/단위/domain이 고정된 $R_j$, (ii) 현재 escape energy와 kinetic cooling, (iii) 새로 공급할 $\eta_j$ 또는 직접 검증된 응답 모멘트, (iv) 동일 사건의 photon-count·energy·species 연결이다. 선택된 warm 기준에서는 현재 Case A escape를 유지하면서 이 인터페이스를 별도 확장으로 붙일 수 있다.

### 주요 문헌 및 내부 source

- Friedrich, Mellema, Iliev & Shapiro (2012), MNRAS **421**, 2232–2250, §3.1.1–3.1.2: https://arxiv.org/abs/1201.0602 . Coupled H/He OTS 선행 근거.
- Hui & Gnedin (1997), MNRAS **292**, 27–42, Appendix A: https://arxiv.org/abs/astro-ph/9612232 . 채택된 rate family의 문헌 계보.
- Verner et al. (1996), ApJ **465**, 487: https://arxiv.org/abs/astro-ph/9601009 . 기저상태 photoionization fit.
- Haardt & Madau (2012), ApJ **746**, 125: https://arxiv.org/abs/1105.2039 ; author tables https://www.ucolick.org/~pmadau/CUBA/DOWNLOADS.html . 초기 광자장과 별도 comoving emissivity의 출처.
- 실제 source/callback/hash: `ATOM_OWNER_MATRIX.json`, `RATE_DOMAIN_MAP.json`, `evidence/EXACT_SCIENCE_SOURCE_MAP.json`, `PHYSICAL_INPUT_ADMISSION.json`.
