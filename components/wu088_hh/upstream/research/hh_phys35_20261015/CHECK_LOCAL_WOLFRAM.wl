(* PHYS35 R5+C6+C8: Wolfram Engine/xTensor local source-bound checks.
   Original Hamiltonian h_lambda=-Delta/2-1/r-lambda*S(|r-Rzhat|).
   All lengths in a0 and energies in Ea=2I0. *)
ClearAll["Global`*"];
ff[x_] := Exp[ll Exp[-x]];
UU[x_] := ll*(Exp[-x]-Exp[-2*x])/x-ll*Exp[-x]/2-(ll+ll^2/2)*Exp[-2*x];
originalU[x_] := -((D[ff[t],{t,2}]+2*D[ff[t],t]/t)/(2*ff[t])/.t->x)-ll*(1+1/x)*Exp[-2*x];
derivation=FullSimplify[originalU[s]-UU[s],s>0];
ineq=Resolve[ForAll[{vv,aa,lam},
  Implies[0<vv<=1&&vv<=aa<=1&&0<=lam<=1,
   -1<=aa-1/2-(1+lam/2)vv<=1]],Reals];
p0[x_] := 1+2 x+3 x^2;
mom[n_Integer,j_Integer,a_,b_] := If[j-n==-1,Log[b/a],(b^(j-n+1)-a^(j-n+1))/(j-n+1)];
intResiduals=Table[FullSimplify[
  Integrate[p0[rr]^2/rr^n,{rr,1/10,3/2}]
 -Sum[Coefficient[Expand[p0[rr]^2],rr,j]mom[n,j,1/10,3/2],{j,0,4}]],{n,{2,4}}];
scalarPass=And[TrueQ[ineq],TrueQ[derivation===0],And@@(TrueQ[#===0]&/@intResiduals)];
Print["SCALAR_ZERO_RESIDUALS=",Prepend[intResiduals,derivation],
      "; CUSP_SCREENING_BOUND_PROVED=",ineq,"; PASS=",scalarPass];
pkg=FindFile["xAct`xTensor`"];
If[pkg===$Failed,Print["XACT_UNAVAILABLE"];Quit[3]];
Get["xAct`xTensor`"];
tensor=ToExpression["$xpermQ=False;DefManifold[MG,3,{aG,bG,cG,dG}];DefMetric[1,gG[-aG,-bG],DG];DefTensor[pG[],MG];DefTensor[qG[],MG];ToCanonical[ContractMetric[Expand[DG[-aG][pG[]DG[aG][qG[]]-qG[]DG[aG][pG[]]]-pG[]DG[-aG][DG[aG][qG[]]]+qG[]DG[-aG][DG[aG][pG[]]]]]]"];
Print["XTENSOR_RESIDUAL=",tensor,"; PASS=",TrueQ[tensor===0]];
If[!And[scalarPass,TrueQ[tensor===0]],Quit[2]];
Quit[];
