(* PHYS46 finite21 outgoing Coulomb Volterra energy, Green jump and Jost bound. *)
ClearAll["Global`*"];
kap46=7/10; B46=20; R46=7/10; c46=59/70; T46=31; ellmax46=20; M46=28;
q46[r_,ell_]:=kap46^2+2/r-ell(ell+1)/r^2;
qmin46=FullSimplify[q46[T46,ellmax46]];
variation46=FullSimplify[2/T46+ellmax46(ellmax46+1)/T46^2];
exponent46=FullSimplify[variation46/qmin46];
energy46=FullSimplify[2kap46^2 Exp[exponent46](1/qmin46+1/kap46^2)];
tailp46=FullSimplify[2(B46-R46)-2c46(T46-B46)];
tailq46=FullSimplify[2(T46-R46)];
Qbound46=FullSimplify[(M46^2/kap46)(1+1/(B46-R46))*
 (Exp[-tailp46]/(1+c46)+Exp[-tailq46])];
alpha46=FullSimplify[Qbound46/(1-Qbound46)];
bnd46=FullSimplify[2alpha46/(1-alpha46)];
Print["PHYS46_RATIONAL_LOCKS=",{qmin46,variation46,exponent46,tailp46,tailq46}];
Print["PHYS46_ENERGY_AND_CONTRACTION=",N[{energy46,Qbound46,alpha46,bnd46},38]];
Print["PHYS46_POSITIVE_GATE=", {TrueQ[energy46<M46^2],TrueQ[Qbound46<1/2]}];
If[!TrueQ[energy46<M46^2]||!TrueQ[Qbound46<1/2],Quit[2]];
rl46={0,5,15,20};
eta46=-1/kap46;
rho46[r_]:=kap46 r;
hplus46[l_,r_]:=CoulombH1[l,eta46,rho46[r]];
hminus46[l_,r_]:=CoulombH2[l,eta46,rho46[r]];
row46=Table[
 Module[{t=47/2,rr=20,aa,bb,Hr,Tr,kk,jump,wron,eq,kval},
  aa[r_]:=hplus46[l,r];bb[r_]:=hminus46[l,r];
  kval[x_]:=(aa[x]bb[t]-bb[x]aa[t])/(2 I kap46);
  jump=N[Derivative[1][kval][t],45];
  wron=N[Conjugate[aa[rr]]Derivative[1][aa][rr],45];
  eq=N[Derivative[2][kval][rr]+q46[rr,l] kval[rr],45];
  {l,Abs[N[kval[t],45]],N[jump,35],
     Abs[N[eq,35]],N[Im[wron]/kap46,35]}],{l,rl46}];
Print["PHYS46_NUMERIC_GREEN_TABLE=",row46];
good46=And@@(#[[2]]<10^-30&&Abs[#[[3]]-1]<10^-30&&
 #[[4]]<10^-30&&Abs[#[[5]]-1]<10^-30&/@row46);
Print["PHYS46_GREEN_AND_WRONSKIAN_PASS=",good46];
If[!good46,Quit[3]];
(* Exact 2x2 algebraic boundary matrix identity for Jost similarity, noncommuting E/Ep *)
Clear[d46,e46,ep46,id46];
e46={{a11,a12},{a21,a22}};
ep46={{b11,b12},{b21,b22}};
lhs46=(IdentityMatrix[2]+ep46) . Inverse[IdentityMatrix[2]+e46]-IdentityMatrix[2];
rhs46=(ep46-e46) . Inverse[IdentityMatrix[2]+e46];
ident46=FullSimplify[lhs46-rhs46];
Print["PHYS46_JOST_MATRIX_IDENTITY_ZERO=",ident46];
If[!TrueQ[ident46===ConstantArray[0,{2,2}]],Quit[4]];
Print["PHYS46_THEORY_CAS_PASS=True"];
Quit[];
