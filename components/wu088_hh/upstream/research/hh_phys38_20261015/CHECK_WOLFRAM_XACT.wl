(* PHYS38 R5/C7: finite-width radial strip, angular-log modulus,
   Sobolev trace and actual xTensor Euclidean Green identity.
   Frozen model: Ea=2I0, r/R in a0, signature -+++, electron space Euclidean. *)
ClearAll["Global`*"];
angcut=del/(2 rad);
direxp=FullSimplify[2(
  Integrate[4 xx,{xx,0,angcut},
    Assumptions->0<del<rad&&rad>0]+
  Integrate[del^2/(rad^2 xx),{xx,angcut,1},
    Assumptions->0<del<rad&&rad>0])
  -del^2/rad^2(1+2Log[2rad/del]),
  Assumptions->0<del<rad&&rad>0];
radexp=FullSimplify[
  Integrate[tt^2(1+2 Log[2rad/tt]),{tt,0,del},
    Assumptions->0<del<rad&&rad>0]
   -del^3(5/9+2Log[2rad/del]/3),
  Assumptions->0<del<rad&&rad>0];
ee=Exp[-ss];q=(1-ee)/ss;uu=ee*q-ee/2-3ee^2/2;
uder=FullSimplify[D[uu,ss]-(-ee*q+ee*D[q,ss]+ee/2+3ee^2),ss>0];
dsrc=FullSimplify[D[Exp[-ee],ss]-ee Exp[-ee],ss>0];
trace=FullSimplify[
  2/(1/10)*Integrate[(1+rr)^2,{rr,7/10-1/10,7/10}]+
  2*(1/10)*Integrate[1,{rr,7/10-1/10,7/10}]-
  (1+7/10)^2];
checks={direxp,radexp,uder,dsrc};
Print["PHYS38_SCALAR_RESIDUALS=",checks,
      "; ALL_ZERO=",And@@(TrueQ[#===0]&/@checks),
      "; POSITIVE_MANUFACTURED_TRACE_MARGIN=",trace];
If[!(And@@(TrueQ[#===0]&/@checks)&&TrueQ[trace>0]),Quit[2]];
pkg=FindFile["xAct`xTensor`"];
If[pkg===$Failed,Print["XACT_MISSING"];Quit[3]];
Get["xAct`xTensor`"];
res=ToExpression[
"$xpermQ=False;DefManifold[ES38,3,{aa38,bb38,cc38,dd38}];DefMetric[1,gg38[-aa38,-bb38],DS38];DefTensor[p38[],ES38];DefTensor[q38[],ES38];ToCanonical[ContractMetric[Expand[DS38[-aa38][p38[] DS38[aa38][q38[]]-q38[] DS38[aa38][p38[]]]-p38[] DS38[-aa38][DS38[aa38][q38[]]]+q38[] DS38[-aa38][DS38[aa38][p38[]]]]]]"];
Print["PHYS38_XTENSOR_RESIDUAL=",res,"; EXACT_ZERO=",TrueQ[res===0]];
If[!TrueQ[res===0],Quit[4]];
Quit[];
