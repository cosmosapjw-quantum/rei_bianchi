(* WU088_HH PHYS45 exact original two-centre Yukawa potential. *)
ClearAll["Global`*"];
s45=s45x; r45=20; R45=7/10;
pot45=(1+1/s45) Exp[-2s45];
g45=Exp[-lam45 s45]/s45;
ident45=FullSimplify[
 ((g45-D[g45,lam45])/.lam45->2) - pot45,
 Assumptions->s45>0];
deriv45=FullSimplify[
 D[pot45,s45]+Exp[-2s45](2+2/s45+1/s45^2)];
convex45=FullSimplify[
 D[pot45,{s45,2}]-
 Exp[-2s45](4+4/s45+4/s45^2+2/s45^3)];
mu45=(r45^2+R45^2-s45^2)/(2r45 R45);
jac45=FullSimplify[D[mu45,s45]+s45/(r45 R45)];
recast45=FullSimplify[
 s45((1+1/s45)Exp[-2s45])-
 (s45+1)Exp[-2s45],
 Assumptions->s45>0];
weight45=FullSimplify[
 Integrate[s45/(r45 R45),{s45,r45-R45,r45+R45}]-2];
checks45={ident45,deriv45,convex45,jac45,recast45,weight45};
Print["PHYS45_SCALAR_IDENTITIES=",checks45];
Print["PHYS45_EXACT_ZERO_COUNT=",Count[checks45,0],"/",Length[checks45]];
If[!And@@(TrueQ[#===0]&/@checks45),Quit[2]];
pr45[l_,m_,mu_]:=LegendreP[l,mu]LegendreP[m,mu]
 v45[mu_]:=(1+1/Sqrt[r45^2+R45^2-2r45 R45 mu])*
      Exp[-2 Sqrt[r45^2+R45^2-2r45 R45 mu]];
pairs45={{0,0},{0,1},{1,1},{5,5},{20,20}};
rows45=Table[
 Module[{ell=pair[[1]],j=pair[[2]],val},
 val=NIntegrate[
  Sqrt[(2ell+1)(2j+1)]/2*pr45[ell,j,mu]*v45[mu],
  {mu,-1,1},WorkingPrecision->54,PrecisionGoal->36,
  AccuracyGoal->55,MaxRecursion->24];
 {ell,j,N[val,42]}],{pair,pairs45}];
Print["PHYS45_INDEPENDENT_WOLFRAM_GAUSS_ROWS=",rows45];
If[!And@@(NumericQ[#[[3]]]&&#[[3]]>0&/@rows45),Quit[3]];
Print["PHYS45_WOLFRAM_PASS=True"];
Quit[];
