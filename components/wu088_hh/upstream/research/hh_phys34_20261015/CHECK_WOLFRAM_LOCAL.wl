(* Local PHYS34 scalar and xTensor checks, same physical convention as C5 source.
   Only product identities and the bounded-cusp transform are checked, not
   the full continuum scattering theorem or coefficient majorant. *)
ClearAll["Global`*"];
e[s_] := Exp[-s];
f[s_] := Exp[la e[s]];
us[s_] := la (e[s]-e[s]^2)/s - la e[s]/2 - (la+la^2/2) e[s]^2;
uFromConjugation[s_] := -((D[f[x],{x,2}]+2 D[f[x],x]/x)/(2 f[x]) /. x->s) - la(1+1/s) Exp[-2s];
checks = {FullSimplify[uFromConjugation[s]-us[s], s>0],
          FullSimplify[Limit[us[s],s->0,Direction->"FromAbove"]+la(1+la)/2],
          FullSimplify[4 Integrate[r^2 Exp[-2r],{r,0,Infinity}]-1],
          FullSimplify[r^2(uxx+(k^2+2/r-l(l+1)/r^2)u)-(r^2 uxx+(k^2 r^2+2r-l(l+1))u)]};
Print["SCALAR_CHECKS=",checks,"; ALL_ZERO=",And@@(TrueQ[#===0]&/@checks)];
$FailedLocalXact=False;
pkg=FindFile["xAct`xTensor`"];
Print["XACT_PATH=",pkg];
If[pkg =!= $Failed,
  Get["xAct`xTensor`"];
  tr = ToExpression["$xpermQ=False;DefManifold[EM,3,{ab,bc,cd,de}];DefMetric[1,gm[-ab,-bc],Dg];DefTensor[p[],EM];DefTensor[q[],EM];ToCanonical[ContractMetric[Expand[Dg[-ab][p[] Dg[ab][q[]]-q[] Dg[ab][p[]]]-p[] Dg[-ab][Dg[ab][q[]]]+q[] Dg[-ab][Dg[ab][p[]]]]]]"];
  Print["XTENSOR_RESIDUAL=",tr,"; EXACT_ZERO=",TrueQ[tr===0]];
  If[!TrueQ[tr===0], Quit[2]],
  Print["XTENSOR_NOT_FOUND_LOCALLY"]; Quit[3]];
Quit[];
