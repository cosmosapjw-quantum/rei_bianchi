# 온도 의존 native Grackle 반응 transaction

단위는 proper second, proper cm⁻³, photon/H, 열·binding·escape 에너지는 eV/H이다.
native gas의 저장량 `w`는 erg/H이며 `ev_erg=1.602176634e-12`로 변환한다.
metric signature는 `(-,+,+,+)`, transverse/longitudinal scale은
`a exp(-b), a exp(2b)`이고 `s=dot b`다. `s/H`는 signed, 공개 magnitude
`Sigma=sqrt(3)*abs(s)/H`는 부호를 잃는다.

## 연속 반응과 native source 대응

`Y=nHe/nH`, fractions `(x,y,z)=(HII/H,HeII/He,HeIII/He)`라 두면
per-H stocks는 `(1-x,x,Y*(1-y-z),Y*y,Y*z)`이고 electron/H는
`e=x+Y*(y+2*z)`다. native absorber와 ion density는 각각
`A=(nH*(1-x),nHe*(1-y-z),nHe*y)`, `I=(nH*x,nHe*y,nHe*z)`다.
`T=2*nH*w/[3*kB*(nH+nHe+ne)]`, `ne=nH*e`를 매 trial에서 회수한다.

`P_i=A_i*Gamma_i`, `C_i=ne*A_i*ci_i(T)`,
`R_i=ne*I_i*rr_i(T)`, `D=ne*nHe*y*dr(T)`는 cm⁻³ s⁻¹이다.
계수와 cooling은 `igm_rates(T)`의 실제 Grackle Case-A 원본이다.
`F0=P0+C0-R0`, `F1=P1+C1-R1-D`, `F2=P2+C2-R2`로 쓰면
native species derivative는 `(-F0,F0,-F1,F1-F2,F2,F0+F1+F2)`다.
이 식의 H 합과 He 합은 항별로 0이며 마지막 성분은
`dHII+dHeII+2*dHeIII`와 항별로 같다. RR/CI-only는 이 원본 event 성분을
분리한 진단을 의미하며, 모든 native 반응이 켜진 진화와 구별한다.

물리 binding per H는
`B=chiH*x+Y*(chiHeI*y+(chiHeI+chiHeII)*z)`다.
`chi=(13.598434599702,24.587389011,54.41776) eV`이고,
Verner fit activation `(13.60,24.59,54.42) eV`와 다르다.
photo event당 photon 에너지 E는 `(E-chi)`의 열과 `chi`의 binding으로 나뉜다.
CI는 동일 binding을 열에서 가져온다. RR/DR binding 방출과 실제 native kinetic
cooling, CE, freefree는 bolometric escape로 간다. 따라서 원래 native 식은

```
thermal_micro + binding_micro + escape - photo_input - cmb_to_gas = 0.
```

CMB reservoir 변화는 `-cmb_to_gas`다. RR kinetic cooling을 `3*kB*T/2`로
대체하지 않는다. Bolometric escape에서 frequency·각도·광자 수는 결정되지 않으므로
UV photons에 재삽입하거나 angular pressure를 임의로 만들지 않는다.

## 단일 implicit transaction과 보존 잔차

source가 비음수 `S_k`를 공급하고, 고정 geometry의 준비된 photon node k에서
`Ntilde=Nold+S`, `kappa=sum_i A_i(new)*sigma_i(E)`라 하면

```
Nnew = Ntilde/(1+dt*c*kappa)
Gamma_i = c*nH*sum_k Nnew_k*sigma_i(Ek)
heat_i = c*nH*ev_erg*sum_k Nnew_k*sigma_i(Ek)*(Ek-chi_i).
```

따라서 `Ntilde-Nnew=dt*c*kappa*Nnew`이고, 같은 endpoint에서 계산한
`dt*P_i/nH`의 합과 photon sink가 같다. `IgmPhotoInput`은 이 rate를 gas에
전달할 뿐 photon stock을 다시 빼지 않는다. 실제 구현은 기존 public
`Driver::chemical_stage`의 4변수 backward-Euler/Newton을 그대로 호출한다.
gas unknown `(x,y,z,w/ev_erg)`의 잔차를 `(rx,ry,rz,rw)`라 하면 source와
고정 geometry에서 한 transaction의 전체 에너지 잔차는 반올림을 제외하고

```
rE = rw + chiH*rx + Y*chiHeI*ry + Y*(chiHeI+chiHeII)*rz.
```

이다. 이는 photo, CI, capture binding이 항별로 상쇄되고 native escape와 CMB
적분을 같은 endpoint에서 취하는 것으로 유도된다. Electron/H event 잔차도
`rx+Y*(ry+2*rz)`다. 수치 검사는 이 nonlinear solve 잔차와 독립 event/energy
ledger를 모두 본다. 작은 Newton norm만으로 전체 ledger를 대신하지 않는다.

`Ntilde>=0`, `dt>=0`, `kappa>=0`이면 photon BE survivor는 비음수다. Gas는
native admissibility와 line search로 `0<=x<=1`, `y,z>=0`, `y+z<=1`, `w>0`,
회수된 `T in [1,1e6] K`를 만족하는 trial만 허용한다. 이는 accepted-state
admissibility이며 모든 dt에서의 해 존재나 Newton 수렴의 무조건적 증명이 아니다.
실패 시 clone 전체를 버리고 dt를 줄이며, source cursor·birth metadata·열·광자·ledger를
성공한 transaction에서만 함께 commit한다. Trial/RHS 비용 counter는 물리 상태와 구별한다.

Backward Euler와 source-before-reaction 조합의 전역 시간 정확도는 smooth한 영역에서
일차다. Frozen exact pair에 온도 의존 계수를 대입하거나 half-step 대칭 이름만으로
이차를 주장하지 않는다. 독립 continuous RHS/Radau와 실제 dt refinement로 차수를 검사한다.

## source age·geometry의 범위

native MD14 emissivity와 native source spectrum/Jacobian을 직접 사용한다.
source interval의 emission epoch와 count/energy는 accepted-only ledger에 기록한다.
이 기록은 surviving photons의 완전한 cohort distribution이나 stellar SSP age spectrum을
제공하지 않는다. Early/delayed pulse는 서로 다른 실제 주입 시점을 갖는 시험이다.
고정 geometry에서는 work=0이며 frozen signed shape를 동적 shear work로 부르지 않는다.
동적 smoke에서는 native background와 원래 `geometry_map`이 실제 photon/thermal work를
소유한다. 이번 짧은 trajectory와 refinement가 최종 Bianchi z20→4 이력을 대체하지 않는다.
