(* WU088_HH PHYS52, independent local Wolfram exact finite-band glue. *)
ClearAll[k,rateC,B,T,M,q,lower,inv,dim,n,ct,cu,cubic,U,P,A,Z,lam,comm,flux];
{k,rateC,B,T,M}={7/10,4/5,27,43,43};
q=2863005967246512/10^24; (* certified rational OUTWARD prior PHYS51 decimal *)
lower=2885508710/10^24;
inv=346559342044058498094084768851728747685/10^24;
dim=Sum[Max[0,29-Max[21,Abs[m]]],{m,-28,28}];
n[m_]:=29-Max[21,Abs[m]];
ct=Sum[n[m]^2,{m,-28,28}];
cu=Sum[n[m]^2,{m,0,28}];
cubic=Sum[n[m]^3,{m,0,28}];
Print["COUNTS: ",{dim,ct,cu,cubic}];
j=k(1-q)^2/(M^2 Exp[2 rateC(T-B)]);
Print["SCOPED CURRENT lower bound numerical = ",N[j,42],
" lower_outward_valid=",FullSimplify[lower<=j],
" inverse_outward_valid=",FullSimplify[inv>=1/lower]];
If[{dim,ct,cu,cubic}!={400,3032,1548,12048},Exit[4]];
If[!TrueQ[FullSimplify[lower<=j && inv>=1/lower]],Exit[5]];

(* Verify flux identity algebra without assuming U commutes with U^dagger. *)
U={{1+I,2-I},{I,1-2I}};
A={{2,1},{1,3}};
P=ConjugateTranspose[Inverse[U]].(A+I k IdentityMatrix[2]);
Z=P.Inverse[U];
comm=FullSimplify[ConjugateTranspose[U].P-ConjugateTranspose[P].U-
     2 I k IdentityMatrix[2]];
flux=FullSimplify[(Z-ConjugateTranspose[Z])/(2 I)-
     k ConjugateTranspose[Inverse[U]].Inverse[U]];
lam={{3,1/2},{1/2,4}};
Print["EXACT JOST CURRENT MATRIX IDENTITY ZERO=",comm==ConstantArray[0,{2,2}]];
Print["EXACT DtN FLUX IDENTITY ZERO=",flux==ConstantArray[0,{2,2}]];
Print["MATCH MAT det=",FullSimplify[Det[lam-Z]]];
If[comm=!=ConstantArray[0,{2,2}] || flux=!=ConstantArray[0,{2,2}],Exit[6]];
If[!TrueQ[FullSimplify[Re[Det[lam-Z]]^2+Im[Det[lam-Z]]^2>0]],Exit[7]];
Print["PHYS52 Wolfram checks PASS"];
Exit[0];
