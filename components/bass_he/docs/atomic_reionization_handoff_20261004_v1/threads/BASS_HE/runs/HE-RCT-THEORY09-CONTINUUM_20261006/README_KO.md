# THEORY09A: outgoing Coulomb continuum과 threshold

CONDITIONAL_OUTGOING_CONTINUUM_AND_BENCHMARK_PASS__PHYSICAL_INPUT_OPEN. 출사 정규화/flux/threshold 하위이론은 완료했고 상위 actual-He THEORY09는 partial이다. 실제 원자 sigma0/sigma1/mean은 null이다.

새 유도: a=hbar^2/(2mu),gamma=C/(2a),k=sqrt(e/a),eta=gamma/k. Regular f와 outgoing h=G+iF에서 W=f*hprime-fprime*h. Green kernel=f(Rmin)*h(Rmax)/(a*W), pure Coulomb W=-k다. w(e)=-Im<q|Green|q>/pi=|<u_e|q>|^2. 밖에 source와 short-range tail이 없으면 w=a*k*|Aout|^2/pi=hbar*jout/(2pi). Robin Im(Hplusprime/Hplus)=k/|Hplus|^2>0을 쓴다. 물리상수/flux/energy normalization을 유지하고 final DOS를 다시 곱하지 않는다.

무차원 H=-d_r^2+l(l+1)/r^2+2gamma/r,합성 q=N*r^(l+1)*exp(-s*r)의 exact overlap:
I=N*C_l(gamma/k)*Gamma(2l+3)*k^(l+1)*(s+gamma/(l+1))*exp(2gamma/k*atan(k/s))/(s^2+k^2)^(l+2).
w(e)=I(sqrt(e))^2/(pi*sqrt(e)), integral w de=1. 이 q는 실제 He dipole/입사파가 아니다. l0,s1,S4에서 gamma0/1의 M4/M3=3.55538118884771/2.81401977784588이다. 숫자는 eV가 아닌 무차원 기준계다.

실제 threshold는 rho->0와 eta->infinity의 동시극한이다. 닫힌식에서 w(e)~A_l*exp(-2pi gamma/sqrt(e)). 반면 fixed delta>0의 resolvent broadening은 remote spectral mass를 threshold로 섞어 상대오차가 발산한다. Bound state가 없는 pure Coulomb에서도 gamma=s=1,l0,delta1e-6,e.01이면 true w=3.41837e-24, x in[1,4] leakage만7.12198e-8이다. Pointwise 오류를 모든 적분모멘트의 같은 상대오류로 일반화하지 않는다.

Projected A_n=P_c*1_[0,S](H)*(S-H)^n은 bounded이고 norm<=S^n. q=qR+r에서 moment 차이<=S^n*(2||qR||||r||+||r||^2). 따라서 spectral observable은 L2 source로 정의되며 unprojected 고차 교환자 domain과 다르다. Source cutoff bound가 potential-tail error까지 포함하지는 않는다.

실제 검산 네 명령 모두 exit0: symbolic zero11식+rational inequality1예제, radial4경우x35/55자리, boundary6점, moment4모형x35/55자리x3차수, threshold12점,broadening3에너지,incoming-sign1반례. 최대 radial 상대차3.66397490076711e-36, moment precision차1.13657426698356e-34. Tests-after,같은 mpmath backend,independent review/interval NOT_RUN. 원자/native/old-suite/consumer/root mutation0.

C2d L angular coupling을 E1 dipole로 바꾸어 쓰지 않았다. Winter1977 원문5-6쪽의 대표6자리 eigenvalues도 full V_i/V_f/d/tail/error payload로 승격하지 않았다. 이번 selected intake 미결이지 자료가 어디에도 없다는 주장은 아니다.

전체22식 보고서,실행 verifier,개별결과/로그는 BASS_HE_RCT_THEORY09_CONTINUUM_20261006_v1.zip에 있다. Git은 이 요약과 입력/계약/반환/검사identity/다음지침이다. Source moments null,baselineOFF,physicalHOLD,HE-F2globalfalse,HE-F3/F09blocked 유지. 다음 THEORY09B_SAME_CHANNEL_DIPOLE_SOURCE는 actual2psigma/1ssigma E1 source를 결속하며 기존 addon 채택의 추가 gate가 아니다.
