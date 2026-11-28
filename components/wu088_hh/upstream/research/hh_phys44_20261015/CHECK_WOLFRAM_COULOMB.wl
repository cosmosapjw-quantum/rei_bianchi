(* PHYS44: Coulomb outgoing reference and conditional REI FT03 temperature Jacobian. *)
ClearAll["Global`*"];
kk44=7/10; eta44=-10/7; rho44=14; rr44=20; RR44=7/10;
h44[l_]:=CoulombH1[l,eta44,rho44];
hh44[l_]:=CoulombG[l,eta44,rho44]+I CoulombF[l,eta44,rho44];
deriv44[l_]:=((l+1)/rho44+eta44/(l+1))h44[l]-
 Sqrt[1+(eta44/(l+1))^2]h44[l+1];
rows44=Table[
 Module[{z,w,delta},z=N[kk44 deriv44[l]/h44[l],46];
 w=N[Im[Conjugate[h44[l]] deriv44[l]],46];
 delta=N[h44[l]-hh44[l],46];
 {l,Re[z],Im[z],w,Abs[delta]}],{l,{0,1,4,20}}];
goodWave44=And@@(#[[3]]>0&&Abs[#[[4]]-1]<10^-37&&#[[5]]<10^-37&/@rows44);
Print["PHYS44_WOLFRAM_COULOMB_OUTGOING_ROWS=",rows44];
Print["PHYS44_WOLFRAM_FLUX_AND_H1_EQUALITY=",goodWave44];
If[!goodWave44,Quit[2]];
regularChecks44=Flatten[Table[
 Module[{coef},coef[0]=1;coef[-1]=0;
 Do[coef[n]=FullSimplify[-(2 coef[n-1]+kk44^2 coef[n-2])/(n(n+2 l+1))],{n,1,18}];
 Table[FullSimplify[n(n+2l+1)coef[n]+2coef[n-1]+kk44^2coef[n-2]],{n,1,18}]],
 {l,{0,1,4,20}}]];
Print["PHYS44_FROBENIUS_EXACT_ZERO_COUNT=",Count[regularChecks44,0],"/",Length[regularChecks44]];
If[!And@@(TrueQ[#===0]&/@regularChecks44),Quit[3]];
tail44=FullSimplify[
 Integrate[2 (1+1/(rr44-RR44)) Exp[-2 (r44-RR44)],{r44,rr44,Infinity}]-
 (1+1/(rr44-RR44)) Exp[-2(rr44-RR44)]];
Print["PHYS44_SCREENED_TAIL_MAJORANT_EXACT_ZERO=",tail44];
If[tail44=!=0,Quit[4]];
Pi44=1+f44+x44+f44(y44+2 z44);
Ct44=2/(3 kb44);
t44=Ct44 w44/Pi44;
lhs44=FullSimplify[(Ct44(-chi44 q44)-t44 q44)/Pi44+
 (Ct44 chi44+t44)q44/Pi44];
Print["PHYS44_FT03_TEMP_JACOBIAN_ZERO=",lhs44];
If[lhs44=!=0,Quit[5]];
Print["PHYS44_THEORY_CAS_PASS=True"];
Quit[];
