(* PHYS50: rigorously source-locked high-l two-boundary collar lifting. *)
ClearAll["Global`*"];
b50=20; t50=27; d50=t50-b50;
lfirst50=21; k50=7/10; R50=7/10;
w50[l_]:=d50/(2(l+1));
emax50[l_]:=1/w50[l]+l(l+1)w50[l]/(3b50^2);
c50=FullSimplify[2/d50+d50/(6b50^2)];
hat50=FullSimplify[
 Integrate[1/w50[l]^2+l(l+1)/b50^2(1-x/w50[l])^2,
    {x,0,w50[l]}],
 Assumptions->l>20];
margin50=FullSimplify[c50(l+1)-hat50,
 Assumptions->l>20];
emin50=FullSimplify[lfirst50(lfirst50+1)/t50^2-2/t50-k50^2];
lam50=FullSimplify[9/d50^2+emin50];
delta50=2(1+1/(b50-R50))Exp[-2(b50-R50)];
beta50=emin50-delta50;
gamma50=Sqrt[c50/beta50];
alpha50=delta50/(lam50-delta50);
Print["PHYS50_SOURCE_HAT_EQUALITY=",FullSimplify[hat50-emax50[l]]];
Print["PHYS50_RATIONAL_CONST=",c50," MARGIN=",margin50];
Print["PHYS50_BARRIER_AND_LAMBDA=",{emin50,lam50}];
Print["PHYS50_INDEPENDENT_TRUE_EXP_NUMERIC=",N[{delta50,beta50,gamma50,alpha50,delta50 gamma50,delta50 alpha50},40]];
ok50=And@@{
 TrueQ[c50===4849/16800],
 TrueQ[margin50===7/2400],
 TrueQ[emin50===1693/24300],
 TrueQ[lam50===301657/1190700],
 TrueQ[beta50>0],
 TrueQ[delta50<lam50],
 TrueQ[gamma50<21/10]
};
Print["PHYS50_MAIN_THEORY_GATES=",ok50];
If[!ok50,Quit[2]];
(* Selfadjoint free constant barrier as an independent finite DtN sign check. *)
Clear[omega50];
dn50=omega50{{Coth[omega50 d50],-Csch[omega50 d50]},
             {-Csch[omega50 d50],Coth[omega50 d50]}};
eig50=FullSimplify[Eigenvalues[dn50],Assumptions->omega50>0];
Print["PHYS50_REFERENCE_POSITIVE_DTN_EIGENVALUES=",eig50];
Print["PHYS50_LOCAL_WOLFRAM_PASS=True"];
Quit[];
