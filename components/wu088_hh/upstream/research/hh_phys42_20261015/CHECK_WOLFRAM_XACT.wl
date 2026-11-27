(* WU088_HH PHYS42: signed original radial-angular strong residual and xAct. *)
ClearAll["Global`*"];
rC=7/10;
srcC=2 (1+49/100) Exp[-r42];
eC=Exp[-s42];
qC=(1-eC)/s42;
uC=eC qC-eC/2-3eC^2/2;
origC=a42-2eC h42/s42-2uC b42-srcC Exp[-eC];
newC=(a42-srcC)-2eC h42/s42-2uC b42+srcC (1-Exp[-eC]);
checkSource=FullSimplify[origC-newC,Assumptions->r42>0&&s42>0];
checkU=FullSimplify[uC-(eC (1-eC)/s42-eC/2-3eC^2/2)];
checkGeometric=FullSimplify[
 (r42^2+rC^2-2 r42 rC mu42)-(r42-rC mu42)^2-rC^2 (1-mu42^2)];
checkLegendre=Table[FullSimplify[
 ell (LegendreP[ell-1,mu42]-mu42 LegendreP[ell,mu42])-
 (1-mu42^2) D[LegendreP[ell,mu42],mu42]],{ell,1,20}];
checkJacobian=FullSimplify[D[(r42^2+rC^2-s42^2)/(2 r42 rC),s42]+s42/(r42 rC)];
checkVolume=FullSimplify[
 Integrate[x42^2,{x42,lo42,hi42}]*
 Integrate[1/2,{mu42,mlo42,mhi42}]-
 ((hi42^3-lo42^3)*(mhi42-mlo42)/6)];
all42=Join[{checkSource,checkU,checkGeometric,checkJacobian,checkVolume},
 checkLegendre];
Print["PHYS42_SCALAR_ZERO_COUNT=",Count[all42,0],"/",Length[all42],
 "; PASS=",And@@(TrueQ[#===0]&/@all42)];
If[!And@@(TrueQ[#===0]&/@all42),Quit[2]];
If[FindFile["xAct`xTensor`"]===$Failed,
 Print["PHYS42_XACT_MISSING"];Quit[3]];
Get["xAct`xTensor`"];
z42=ToExpression[
 "$xpermQ=False;DefManifold[ES42,3,{aa42,bb42,cc42,dd42}];DefMetric[1,gg42[-aa42,-bb42],DC42];DefTensor[f42[],ES42];DefTensor[v42[aa42],ES42];ToCanonical[ContractMetric[Expand[DC42[-aa42][v42[aa42] f42[]]-f42[] DC42[-aa42][v42[aa42]]-v42[aa42] DC42[-aa42][f42[]]]]]"
 ];
Print["PHYS42_XACT_TENSOR_LEIBNIZ_ZERO=",z42,
 "; PASS=",TrueQ[z42===0]];
If[!TrueQ[z42===0],Quit[4]];
Quit[];
