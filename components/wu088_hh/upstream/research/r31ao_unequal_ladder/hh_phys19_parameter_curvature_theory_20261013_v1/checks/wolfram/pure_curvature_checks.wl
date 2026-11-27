Module[{dir,arc,xf,timing,tensorResult,scalarChecks,matrixChecks,kernelChecks,
 xvars,g0,pv,kv,gpath,dx,localH,chainActual,chainExpected,hessian,gtheta,
 bg,qg,lg,blambda,sub0,subpath,Qpath,residual,jrow,carriedExpected,
 poly,ww,pp,de,dw,piF,T2,TF,FF,T2pp,Fpp,FppDirect,
 xpath,survival,survivalExpected,xone,xtwo,zeta,Aone,Atwo,
 rr,rfull,aa1,aa,af,ll1,ll,lf,tau,c1,c2,z0,jbirth,q1,q2,pdirect,sectors,
 aFns,mass,kernelPolynomial,kernelPolyError,guard1,guard2,bpoly,bilin,
 th,la,be,xx,ss,h,ct,kappa,vph,dl,db,allZero,scalarCount,matrixCount},
 dir=CreateDirectory[];
 arc=FileNameJoin[{dir,"xAct_1.3.0.tgz"}];
 URLDownload["https://xact.es/download/xAct_1.3.0.tgz",arc];
 If[FileHash[arc,"SHA256","HexString"] =!= "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be",
  Return[<|"Status"->"ArchiveIdentityMismatch"|>]];
 ExtractArchive[arc,dir];
 xf=First[Select[FileNames["xTensor.m",dir,Infinity],StringEndsQ[#,"/xAct/xTensor/xTensor.m"]&]];
 PrependTo[$Path,DirectoryName[xf,3]];PrependTo[$Path,DirectoryName[xf,2]];Get[xf];
 timing=AbsoluteTiming[
 tensorResult=ToExpression["
 $xpermQ=False;
 DefManifold[HHState19,4,{ia19,ib19,ic19,id19,ie19,if19}];
 DefTensor[P19[ia19],HHState19];DefTensor[PF19[ia19],HHState19];
 DefTensor[P119[ia19],HHState19];DefTensor[K19[ia19],HHState19];
 DefTensor[KD19[ia19],HHState19];DefTensor[F19[ia19],HHState19];
 DefTensor[J19[ia19,-ib19],HHState19];DefTensor[L19[ia19,-ib19],HHState19];
 DefTensor[H19[ia19,-ib19,-ic19],HHState19,System`Symmetric[{-ib19,-ic19}]];
 DefTensor[DH19[ia19,-ib19,-ic19],HHState19,System`Symmetric[{-ib19,-ic19}]];
 DefTensor[H119[ia19,-ib19,-ic19],HHState19,System`Symmetric[{-ib19,-ic19}]];
 DefTensor[G19[ia19,-ib19],HHState19];DefTensor[DG19[ia19,-ib19],HHState19];
 DefTensor[G119[ia19,-ib19],HHState19];
 DefTensor[N19[-ia19],HHState19];DefTensor[Z19[-ia19],HHState19];
 rPure19=(J19[ia19,-ib19]+L19[ia19,-ib19])K19[ib19]+(H19[ia19,-ib19,-ic19]+DH19[ia19,-ib19,-ic19])P19[ib19]P19[ic19]+2(G19[ia19,-ib19]+DG19[ia19,-ib19])P19[ib19];
 direct19=J19[ia19,-ib19]K19[ib19]+H19[ia19,-ib19,-ic19]PF19[ib19]PF19[ic19]+2G19[ia19,-ib19]PF19[ib19];
 correlated19=rPure19-L19[ia19,-ib19]K19[ib19]-DH19[ia19,-ib19,-ic19]P19[ib19]P19[ic19]-2H19[ia19,-ib19,-ic19](P19[ib19]-PF19[ib19])(P19[ic19]-(P19[ic19]-PF19[ic19])/2)-2DG19[ia19,-ib19]P19[ib19]-2G19[ia19,-ib19](P19[ib19]-PF19[ib19]);
 tensorChecks19=<|
 \"C10CorrelatedPureDefect\"->ToCanonical[Expand[direct19-correlated19]],
 \"C10SymmetricPureContractionDifference\"->ToCanonical[Expand[H19[ia19,-ib19,-ic19](P19[ib19]P19[ic19]-PF19[ib19]PF19[ic19]-(P19[ib19]-PF19[ib19])(P19[ic19]+PF19[ic19]))]],
 \"C12StagePureHessianDifference\"->ToCanonical[Expand[H119[ia19,-ib19,-ic19]P119[ib19]P119[ic19]-H19[ia19,-ib19,-ic19]P19[ib19]P19[ic19]-(H119[ia19,-ib19,-ic19]-H19[ia19,-ib19,-ic19])P119[ib19]P119[ic19]+H19[ia19,-ib19,-ic19](P19[ib19]-P119[ib19])(P19[ic19]+P119[ic19])]],
 \"C12StageParameterGradientDifference\"->ToCanonical[Expand[G119[ia19,-ib19]P119[ib19]-G19[ia19,-ib19]P19[ib19]-(G119[ia19,-ib19]-G19[ia19,-ib19])P119[ib19]+G19[ia19,-ib19](P19[ib19]-P119[ib19])]],
 \"CommonAdjointWithResidual\"->ToCanonical[Expand[N19[-ia19]KD19[ia19]-Z19[-ia19]F19[ia19]-(N19[-ia19]-Z19[-id19]J19[id19,-ia19])KD19[ia19]-Z19[-ia19](J19[ia19,-ib19]KD19[ib19]-F19[ia19])]],
 \"AdjointPureHessianIndexSymmetry\"->ToCanonical[Z19[-ia19]H19[ia19,-ib19,-ic19]P19[ib19]PF19[ic19]-Z19[-ib19]H19[ib19,-ic19,-ia19]PF19[ic19]P19[ia19]]
 |>;
 <|\"Backend\"->\"xAct xTensor with xPerm Wolfram Language group algorithms\",\"ExternalCanonicalizerUsedForChecks\"->$xpermQ,\"TensorChecks\"->tensorChecks19,\"TensorAllZero\"->And@@(#===0& /@ Values[tensorChecks19]),\"Messages\"->$MessageList|>
 "];
 xvars={gx19,gy19};g0={g019,g029};pv={p119,p219};kv={k119,k219};
 gpath=g0+th*pv+th^2*kv/2;dx=xvars-g0;
 hessian={{h1119,h1219},{h1219,h2219}};gtheta={gt119,gt219};
 localH=hf019+{j119,j219}.dx+ht19*th+dx.hessian.dx/2+th*gtheta.dx+htt19*th^2/2;
 chainActual=D[localH/.Thread[xvars->gpath],{th,2}]/.th->0;
 chainExpected={j119,j219}.kv+pv.hessian.pv+2gtheta.pv+htt19;
 bg=b019+b119*gx19+b219*gy19+(b1119*gx19^2+2b1219*gx19*gy19+b2219*gy19^2)/2;
 qg=qh019+qh119*gx19+qh219*gy19+(qh1119*gx19^2+2qh1219*gx19*gy19+qh2219*gy19^2)/2;
 lg=l019+l119*gx19+l219*gy19+(l1119*gx19^2+2l1219*gx19*gy19+l2219*gy19^2)/2;
 blambda=bg+(lambda019+dl*th)*qg;
 sub0=Thread[xvars->g0];subpath=Thread[xvars->gpath];
 Qpath=Q019+Qp19*th+Qk19*th^2/2;
 residual=gpath[[1]]-(first019+firstP19*th+firstK19*th^2/2)-h*(blambda/.subpath)-vph*(lg/.subpath)*Qpath;
 jrow={1,0}-h*(D[blambda,{xvars}]/.sub0/.th->0)-vph*Q019*(D[lg,{xvars}]/.sub0);
 carriedExpected=jrow.kv-firstK19-h*pv.(D[blambda,{xvars,2}]/.sub0/.th->0).pv-2h*dl*(D[qg,{xvars}]/.sub0).pv-vph*((pv.(D[lg,{xvars,2}]/.sub0).pv)*Q019+2*(D[lg,{xvars}]/.sub0).pv*Qp19+(lg/.sub0)*Qk19);
 poly[c0_,c1_,c2_]:=c0+c1*th+c2*th^2/2;
 ww=poly[w019,wp19,wk19];pp=poly[pi019,pip19,pik19];de=poly[de019,dep19,dek19];dw=poly[dw019,dwp19,dwk19];
 piF=pp-de;T2=ct*ww/pp;TF=ct*(ww-dw)/piF;FF=T2-TF;
 T2pp=(ct*D[ww,{th,2}]-T2*D[pp,{th,2}]-2D[T2,th]*D[pp,th])/pp;
 FppDirect=(ct*D[dw,{th,2}]-T2*D[de,{th,2}]-D[T2,{th,2}]*de-2D[T2,th]*D[de,th]-2D[FF,th]*D[piF,th]-FF*D[piF,{th,2}])/piF;
 Fpp=(ct*D[dw,{th,2}]-TF*D[de,{th,2}]-D[T2,{th,2}]*de-2D[T2,th]*D[de,th]-2D[FF,th]*D[piF,th]-FF*D[pp,{th,2}])/piF;
 xpath=poly[x019,xp19,xk19];survival=1/(1+kappa*(1-xpath));
 survivalExpected=kappa*survival^2*D[xpath,{th,2}]+2kappa^2*survival^3*D[xpath,th]^2;
 xone=poly[x1019,x1p19,x1k19];xtwo=poly[x2019,x2p19,x2k19];
 zeta=h*(a219*(1-xtwo)-a119*(1-xone));Aone=1/(1+h*a119*(1-xone));Atwo=1/(1+h*a219*(1-xtwo));
 bpoly=f0019+f1019*la+f0119*be+f2019*la^2/2+f1119*la*be+f0219*be^2/2;
 mass=Integrate[-ss*(1-xx),{ss,0,xx}]+Integrate[-xx*(1-ss),{ss,xx,1}];
 kernelPolynomial=Sum[kc19[i]*ss^i,{i,0,6}];
 kernelPolyError=(kernelPolynomial/.ss->xx)-(1-xx)*(kernelPolynomial/.ss->0)-xx*(kernelPolynomial/.ss->1)-Integrate[-ss*(1-xx)*D[kernelPolynomial,{ss,2}],{ss,0,xx}]-Integrate[-xx*(1-ss)*D[kernelPolynomial,{ss,2}],{ss,xx,1}];
 bilin=(1-la)*(1-be)*fc0019+la*(1-be)*fc1019+(1-la)*be*fc0119+la*be*fc1119;
 scalarChecks=<|
 "C3PureImplicitLocalC2JetChain"->Expand[chainActual-chainExpected],
 "C8CarriedPureGasLocalC2JetChain"->Expand[(D[residual,{th,2}]/.th->0)-carriedExpected],
 "C6PureSurvival"->Together[D[survival,{th,2}]-survivalExpected],
 "C12FactoredZetaPure"->Expand[D[zeta,{th,2}]+h*((a219-a119)*D[xtwo,{th,2}]+a119*D[xtwo-xone,{th,2}])],
 "C12SurvivalDifferencePureProduct"->Together[D[Aone-Atwo,{th,2}]-D[zeta,{th,2}]*Aone*Atwo-2D[zeta,th]*(D[Aone,th]*Atwo+Aone*D[Atwo,th])-zeta*(D[Aone,{th,2}]*Atwo+2D[Aone,th]*D[Atwo,th]+Aone*D[Atwo,{th,2}])],
 "C15EndpointTemperaturePureQuotient"->Together[D[T2,{th,2}]-T2pp],
 "C16FiniteTemperatureDirectPure"->Together[D[FF,{th,2}]-FppDirect],
 "C16CommonFullTemperatureCovector"->Together[FppDirect-Fpp],
 "C13BirthTimesPureLambda"->Expand[D[be*bpoly,{la,2}]-be*D[bpoly,{la,2}]],
 "C13BirthTimesPureBirthFactor2"->Expand[D[be*bpoly,{be,2}]-be*D[bpoly,{be,2}]-2D[bpoly,be]],
 "C18PeanoKernelMass"->Expand[mass+xx*(1-xx)/2],
 "C18PeanoIdentityDegreeSixPolynomial"->Expand[kernelPolyError],
 "C17C20BilinearCornerCoefficients"->Expand[bilin-(fc0019+(fc1019-fc0019)*la+(fc0119-fc0019)*be+(fc1119-fc1019-fc0119+fc0019)*la*be)]
 |>;
 kernelChecks=<|
 "LeftKernelNonpositive"->FullSimplify[-ss*(1-xx)<=0,Assumptions->0<=ss<=xx<=1],
 "RightKernelNonpositive"->FullSimplify[-xx*(1-ss)<=0,Assumptions->0<=xx<=ss<=1],
 "PositiveConvexInterpolationWeights"->FullSimplify[xx>=0&&1-xx>=0&&(1-xx)+xx==1,Assumptions->0<=xx<=1],
 "MaximumKernelAbsoluteMassAtMostOneEighth"->FullSimplify[0<=xx*(1-xx)/2<=1/8,Assumptions->0<=xx<=1]
 |>;
 rr={{r1119,r1219},{r2119,r2219}};rfull={{rf1119,rf1219},{rf2119,rf2219}};
 aFns=Table[Unique["a19"],{4}];
 aa1=DiagonalMatrix[(#[la,be]& /@ Take[aFns,2])];
 aa=DiagonalMatrix[(#[la,be]& /@ Take[aFns,-2])];
 tau=Inverse[aa]-IdentityMatrix[2];af=Inverse[IdentityMatrix[2]+2tau];
 ll1=IdentityMatrix[2]-aa1;ll=IdentityMatrix[2]-aa;lf=IdentityMatrix[2]-af;
 c1=tau.aa.aa.af;c2=tau.tau.aa.aa.af;z0={z0119,z0219};jbirth={j0119,j0219};q1=rr.z0+be*jbirth;q2=rr.aa1.q1+be*jbirth;
 pdirect=ll1.q1+ll.q2-lf.(rfull.z0+2be*jbirth);
 sectors={-(IdentityMatrix[2]-ll.rr).(aa1-aa).q1,ll.(rr.aa-aa.rr).q1,ll.(IdentityMatrix[2]-rr).rr.z0,c2.rr.rr.z0,lf.(rr.rr-rfull).z0,be*ll.aa.(rr-IdentityMatrix[2]).jbirth,-be*c1.jbirth};
 guard1=aa1.q1+ll1.q1-q1;guard2=aa.q2+ll.q2-q2;
 matrixChecks=<|
 "C7SecondIncomingPureLambda"->(Together /@ (D[q2,{la,2}]-rr.(D[aa1,{la,2}].q1))),
 "C7SecondIncomingPureBirthFactor2"->(Together /@ (D[q2,{be,2}]-rr.(D[aa1,{be,2}].q1+2D[aa1,be].jbirth))),
 "C13SevenSectorValueNoncommutingRemap"->(Together /@ (pdirect-Total[sectors])),
 "C13SevenSectorPureLambdaNoncommutingRemap"->(Together /@ (D[pdirect,{la,2}]-Total[D[#,{la,2}]& /@ sectors])),
 "C13SevenSectorPureBirthNoncommutingRemap"->(Together /@ (D[pdirect,{be,2}]-Total[D[#,{be,2}]& /@ sectors])),
 "FirstHalfAbsorptionOutgoingPureBirthPartition"->(Together /@ D[guard1,{be,2}]),
 "SecondHalfAbsorptionOutgoingPureBirthPartition"->(Together /@ D[guard2,{be,2}])
 |>;
 scalarCount=Count[Values[scalarChecks],0];matrixCount=Count[Flatten[Values[matrixChecks]],0];
 allZero=tensorResult["TensorAllZero"]&&And@@(#===0& /@ Values[scalarChecks])&&And@@(#===0& /@ Flatten[Values[matrixChecks]])&&And@@Values[kernelChecks];
 ];
 <|"Status"->If[allZero,"Completed","NonzeroOrUnresolvedCheck"],"WolframVersion"->$Version,
 "ArchiveURL"->"https://xact.es/download/xAct_1.3.0.tgz",
 "ArchiveSHA256"->FileHash[arc,"SHA256","HexString"],"xTensorSHA256"->FileHash[xf,"SHA256","HexString"],
 "AlgebraWallSeconds"->First[timing],"TensorResult"->tensorResult,"ScalarChecks"->scalarChecks,
 "MatrixChecks"->matrixChecks,"KernelChecks"->kernelChecks,
 "TensorExactZeroCount"->Count[Values[tensorResult["TensorChecks"]],0],"ScalarExactZeroCount"->scalarCount,"MatrixComponentExactZeroCount"->matrixCount,"KernelTrueCount"->Count[Values[kernelChecks],True],
 "AllChecksSatisfied"->allZero,
 "Scope"->"Formal second-derivative identities for arbitrary local C2 jets and symmetric tensors; generic symbolic two-slot noncommuting photon graph; Peano kernel algebra and signs. Original 35-slot physical interval enclosures, scientific source executions, nonlinear roots and numerical graph data are outside this symbolic check."|>
]
