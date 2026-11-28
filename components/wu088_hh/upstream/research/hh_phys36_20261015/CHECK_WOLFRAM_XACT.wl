(* PHYS36: source-cancelled two-centre C7 identities.
Model h=-Delta/2-1/r-lambda*S(|r-R ez|), length a0, energy Ea=2I0.
This checks only symbolic source normalization and Euclidean tensor Green identity. *)
ClearAll["Global`*"];
ff[x_]:=Exp[-x];
ph[x_]:=Exp[-x]/Sqrt[Pi];
snorm=FullSimplify[4 Pi Integrate[x^2 ph[x]^2,{x,0,Infinity}]-1];
src=FullSimplify[4 (1+kap^2)^2 Integrate[x^2 Exp[-2x],{x,0,Infinity}]-(1+kap^2)^2];
mon=FullSimplify[
 (D[un[x],{x,2}]+(kap^2+2/x) un[x])*(2(1+kap^2)x Exp[-x])
 -2(1+kap^2)*(x D[un[x],{x,2}]+(kap^2*x+2)un[x])*Exp[-x]];
Ephi=Exp[-2rho]*(3+6rho+4rho^2)/24;
squaresR=FullSimplify[(Ephi/.rho->7/10)-229 Exp[-7/5]/600];
checks={snorm,src,mon,squaresR};
Print["PHYS36_SCALAR_RESIDUALS=",checks,"; PASS=",And@@(TrueQ[#===0]&/@checks)];
If[!And@@(TrueQ[#===0]&/@checks),Quit[2]];
pkg=FindFile["xAct`xTensor`"];
If[pkg===$Failed,Print["XACT_UNAVAILABLE"];Quit[3]];
Get["xAct`xTensor`"];
result=ToExpression[
"$xpermQ=False;DefManifold[MX,3,{aX,bX,cX,dX}];DefMetric[1,gX[-aX,-bX],Dx];DefTensor[pX[],MX];DefTensor[qX[],MX];ToCanonical[ContractMetric[Expand[Dx[-aX][pX[] Dx[aX][qX[]]-qX[] Dx[aX][pX[]]]-pX[]Dx[-aX][Dx[aX][qX[]]]+qX[]Dx[-aX][Dx[aX][pX[]]]]]]"];
Print["PHYS36_XTENSOR_GREEN_RESIDUAL=",result,"; PASS=",TrueQ[result===0]];
If[!TrueQ[result===0],Quit[4]];
Quit[];
