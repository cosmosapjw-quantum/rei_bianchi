(* PHYS37 C7B: cusp-shell x=s/(2R) polynomial map. Exact scalar and actual xAct. *)
ClearAll["Global`*"];
radphys=7/10;
muvar=1-2 zz^2;
legcheck=Table[FullSimplify[LegendreP[ll,muvar]-
  Sum[(-1)^kk Binomial[ll,kk]Binomial[ll+kk,kk]zz^(2kk),{kk,0,ll}]],
  {ll,0,20}];
cuspzero=Table[FullSimplify[
  (ll(LegendreP[ll-1,muvar]-muvar LegendreP[ll,muvar])/.zz->0)],
  {ll,1,20}];
cancel=FullSimplify[(radphys-radphys*muvar)/(2radphys zz)-zz,zz>0];
jac=FullSimplify[D[muvar,zz]+4zz];
measure=FullSimplify[2Integrate[zz,{zz,0,1}]-1];
q0=FullSimplify[Limit[(1-Exp[-2radphys zz])/(2radphys zz),zz->0,Direction->"FromAbove"]-1];
checks=Join[legcheck,cuspzero,{cancel,jac,measure,q0}];
Print["SCALAR_EXACT_ZERO_COUNT=",Count[checks,0],"/",Length[checks],
      "; ALL_ZERO=",And@@(TrueQ[#===0]&/@checks)];
If[!And@@(TrueQ[#===0]&/@checks),Quit[2]];
pkg=FindFile["xAct`xTensor`"];If[pkg===$Failed,Print["XACT_MISSING"];Quit[3]];
Get["xAct`xTensor`"];
result=ToExpression[
"$xpermQ=False;DefManifold[EM37,3,{aa37,bb37,cc37,dd37}];DefMetric[1,gm37[-aa37,-bb37],DD37];DefTensor[pp37[],EM37];DefTensor[qq37[],EM37];ToCanonical[ContractMetric[Expand[DD37[-aa37][pp37[] DD37[aa37][qq37[]]-qq37[] DD37[aa37][pp37[]]]-pp37[] DD37[-aa37][DD37[aa37][qq37[]]]+qq37[] DD37[-aa37][DD37[aa37][pp37[]]]]]]"];
Print["XTENSOR_GREEN_ZERO=",TrueQ[result===0],"; TENSOR_RESIDUAL=",result];
If[!TrueQ[result===0],Quit[4]];
Quit[];
