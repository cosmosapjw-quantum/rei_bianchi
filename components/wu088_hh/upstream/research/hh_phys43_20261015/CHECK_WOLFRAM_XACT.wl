(* PHYS43 original screened D residual, exact global angular/radial tiling. *)
ClearAll["Global`*"];
rr43=7/10; k243=49/100;
ee43=Exp[-ss43];
q43=(1-ee43)/ss43;
uu43=ee43*q43-ee43/2-3ee43^2/2;
src43=2(1+k243)Exp[-r43];
old43=aa43-2ee43 hh43/ss43-2uu43 bb43-src43 Exp[-ee43];
new43=(aa43-src43)-2ee43 hh43/ss43-2uu43 bb43+
 src43(1-Exp[-ee43]);
fSource43=FullSimplify[old43-new43,Assumptions->r43>0&&ss43>0];
fU43=FullSimplify[
 uu43-(ee43*(1-ee43)/ss43-ee43/2-3ee43^2/2)];
s243=(r43-rr43)^2+2r43 rr43 (1-mu43);
fS43=FullSimplify[s243-(r43^2+rr43^2-2r43 rr43 mu43)];
fMeasure43=FullSimplify[Integrate[r43^2,{r43,a43,b43}]*
 Integrate[1/2,{mu43,m043,m143}]-
 (b43^3-a43^3)(m143-m043)/6];
fCuspCover43=FullSimplify[
  (switch43-(rr43-delta43))+
  ((rr43+delta43)-switch43)-2delta43];
fD43=FullSimplify[
 (rb43^3-ra43^3)+(rc43^3-rb43^3)-
 (rc43^3-ra43^3)];
fAngle43=FullSimplify[Integrate[1/2,{mu43,-1,1}]-1];
fMin43=FullSimplify[
 Min[P43,Q43]<=P43&&Min[P43,Q43]<=Q43,
 Assumptions->P43>=0&&Q43>=0];
fJac43=FullSimplify[
 D[(r43^2+rr43^2-ss43^2)/(2r43 rr43),ss43]+ss43/(r43 rr43)];
scalars43={fSource43,fU43,fS43,fMeasure43,fCuspCover43,
 fD43,fAngle43,fJac43};
Print["PHYS43_SCALAR_EXACT_ZERO_COUNT=",Count[scalars43,0],"/",
 Length[scalars43],"; MIN_VALID=",TrueQ[fMin43]];
If[!And@@(TrueQ[#===0]&/@scalars43)||!TrueQ[fMin43],Quit[2]];
If[FindFile["xAct`xTensor`"]===$Failed,
 Print["PHYS43_XACT_NOT_AVAILABLE"];Quit[3]];
Get["xAct`xTensor`"];
z43=ToExpression[
 "$xpermQ=False;DefManifold[ES43,3,{a43x,b43x,c43x,d43x}];DefMetric[1,g43[-a43x,-b43x],D43];DefTensor[f43[],ES43];DefTensor[h43[],ES43];ToCanonical[ContractMetric[Expand[D43[-a43x][f43[] D43[a43x][h43[]]-h43[] D43[a43x][f43[]]]-f43[] D43[-a43x][D43[a43x][h43[]]]+h43[] D43[-a43x][D43[a43x][f43[]]]]]]"
 ];
Print["PHYS43_XACT_GREEN_IDENTITY=",z43,"; PASS=",TrueQ[z43===0]];
If[!TrueQ[z43===0],Quit[4]];
Quit[];
