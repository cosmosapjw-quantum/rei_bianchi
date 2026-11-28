(* PHYS40 actual Wolfram Engine and xAct/xTensor check.
Frozen-direct H(1s)+H(1s), R=kappa=7/10, r in Bohr radii, Ea=2I0. *)
ClearAll["Global`*"];
r40=1; rSpec40=7/10;
mu40=(r40^2+rSpec40^2-s40^2)/(2r40*rSpec40);
e40=Exp[-s40];
u40=e40(1-e40)/s40-e40/2-3e40^2/2;
h40=(r40-rSpec40 mu40)c40-(rSpec40/r40)t40;
gOriginal40=a40-2e40 h40/s40-2u40 b40-src40 Exp[-e40];
nAlgebra40=s40 a40-2e40 h40-2e40(1-e40)b40+
 s40 e40 b40+3s40 e40^2 b40-s40 src40 Exp[-e40];
identity40=FullSimplify[nAlgebra40-s40 gOriginal40,
 Assumptions->s40>0];
jac40=FullSimplify[D[mu40,s40]+s40/(r40 rSpec40)];
norm40=FullSimplify[Integrate[s40/(2r40 rSpec40),
 {s40,r40-rSpec40,r40+rSpec40}]-1];
weighted40=FullSimplify[Integrate[s40^2/s40,
 {s40,r40-rSpec40,r40+rSpec40}]/(2r40 rSpec40)-1];
q40=FullSimplify[Limit[(1-Exp[-s40])/s40,s40->0,
 Direction->"FromAbove"]-1];
nCusp40=FullSimplify[
 (rSpec40-rSpec40(1-s40^2/(2rSpec40^2)))/s40-s40/(2rSpec40),
 Assumptions->s40>0];
checks40={identity40,jac40,norm40,weighted40,q40,nCusp40};
Print["PHYS40_SCALAR_EXACT_ZEROS=",checks40,
  "; COUNT=",Count[checks40,0],"/",Length[checks40],
  "; PASS=",And@@(TrueQ[#===0]&/@checks40)];
If[!And@@(TrueQ[#===0]&/@checks40),Quit[2]];
pkg40=FindFile["xAct`xTensor`"];
If[pkg40===$Failed,Print["PHYS40_XACT_MISSING"];Quit[3]];
Get["xAct`xTensor`"];
zero40=ToExpression[
"$xpermQ=False;DefManifold[M40,3,{a40x,b40x,c40x,d40x}];DefMetric[1,g40[-a40x,-b40x],D40];DefTensor[p40[],M40];DefTensor[q40[],M40];ToCanonical[ContractMetric[Expand[D40[-a40x][p40[] D40[a40x][q40[]]-q40[]D40[a40x][p40[]]]-p40[]D40[-a40x][D40[a40x][q40[]]]+q40[]D40[-a40x][D40[a40x][p40[]]]]]]"];
Print["PHYS40_XTENSOR_EUCLIDEAN_GREEN_RESIDUAL=",zero40,
      "; EXACT_ZERO=",TrueQ[zero40===0]];
If[!TrueQ[zero40===0],Quit[4]];
Quit[];
