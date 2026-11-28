(* WU088_HH PHYS39: actual Wolfram Engine15 and xAct/xTensor1.3.
   Screened two-centre source J_n and generic positive radius s-coordinate.
   Lengths in a0, Ea=2I0, (-+++) spacetime; electron space Euclidean. *)
ClearAll["Global`*"];
rad=7/10;
f1=FullSimplify[D[(xr^2+rad^2-ss^2)/(2 xr rad),ss]+ss/(xr rad)];
sourceSeries=FullSimplify[
  Sum[(-1)^nn(2^nn-2) zz^nn/nn!,{nn,2,Infinity}]
   -(1-Exp[-zz])^2,Assumptions->0<=zz<=1];
sourceFinite=FullSimplify[
 (1-Exp[-Exp[-ss]])^2-
 (1-2Exp[-Exp[-ss]]+Exp[-2Exp[-ss]]),ss>=0];
jn2=229 Exp[-7/5]/600;
rho=7/10;
testJ2=FullSimplify[
 (3+6rho+4rho^2)Exp[-2rho]/24-jn2];
moment=FullSimplify[
 Integrate[ss Exp[-nn ss],{ss,aa,bb},
  Assumptions->0<=aa<bb && nn>0]-
 ((1+nn aa)Exp[-nn aa]-(1+nn bb)Exp[-nn bb])/nn^2,
 Assumptions->0<=aa<bb && nn>0];
orth=Table[FullSimplify[
  Integrate[LegendreP[l,xx]LegendreP[m,xx]/2,{xx,-1,1}]
  -If[l==m,1/(2l+1),0]],{l,0,5},{m,0,5}];
checks=Join[{f1,sourceSeries,sourceFinite,testJ2,moment},Flatten[orth]];
Print["PHYS39_SCALAR_ZERO_COUNT=",Count[checks,0],"/",Length[checks],
      "; ALL_ZERO=",And@@(TrueQ[#===0]&/@checks)];
If[!And@@(TrueQ[#===0]&/@checks),Quit[2]];
pkg=FindFile["xAct`xTensor`"];
If[pkg===$Failed,Print["XACT_NOT_AVAILABLE"];Quit[3]];
Get["xAct`xTensor`"];
ten=ToExpression[
"$xpermQ=False;DefManifold[M39,3,{a39,b39,c39,d39}];DefMetric[1,g39[-a39,-b39],D39];DefTensor[p39[],M39];DefTensor[q39[],M39];ToCanonical[ContractMetric[Expand[D39[-a39][p39[] D39[a39][q39[]]-q39[] D39[a39][p39[]]]-p39[] D39[-a39][D39[a39][q39[]]]+q39[] D39[-a39][D39[a39][p39[]]]]]]"];
Print["PHYS39_XACT_EUCLIDEAN_GREEN_RESIDUAL=",ten,
      "; ZERO=",TrueQ[ten===0]];
If[!TrueQ[ten===0],Quit[4]];
Quit[];
