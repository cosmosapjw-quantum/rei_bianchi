Module[{dir,arc,xf,tensorResult,scalarChecks,vars,pi,temp,u,uv,gradU,hessU,vel,du,projectorDerivative,temperatureDifference,temperatureP4,temperatureAdjoint,rr,rfull,aa1,aa,af,ll1,ll,lf,tau,c1,c2,z0,jbirth,q1,pdirect,sectors,photonDerivativeCheck,mtest,stest,ftest,ltest,vtest,dtest,neumannCheck},
 dir=CreateDirectory[];
 arc=FileNameJoin[{dir,"xAct_1.3.0.tgz"}];
 URLDownload["https://xact.es/download/xAct_1.3.0.tgz",arc];
 If[FileHash[arc,"SHA256","HexString"] =!= "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be",Return[<|"Status"->"ArchiveIdentityMismatch"|>]];
 ExtractArchive[arc,dir];
 xf=First[Select[FileNames["xTensor.m",dir,Infinity],StringEndsQ[#,"/xAct/xTensor/xTensor.m"]&]];
 PrependTo[$Path,DirectoryName[xf,3]];PrependTo[$Path,DirectoryName[xf,2]];Get[xf];
 tensorResult=ToExpression["
 $xpermQ=False;
 DefManifold[HHState17,4,{aa17,bb17,cc17,dd17,ee17,ff17}];
 DefTensor[Disp17[aa17],HHState17];
 DefTensor[YResponse17[aa17],HHState17];
 DefTensor[FResponse17[aa17],HHState17];
 DefTensor[DResponse17[aa17],HHState17];
 DefTensor[Jac17[aa17,-bb17],HHState17];
 DefTensor[JacShift17[aa17,-bb17],HHState17];
 DefTensor[Mixed17[aa17,-bb17],HHState17];
 DefTensor[Hess17[aa17,-bb17,-cc17],HHState17,Symmetric[{-bb17,-cc17}]];
 DefTensor[Adj17[-aa17],HHState17];
 DefTensor[Goal17[-aa17],HHState17];
 DefTensor[Force17[aa17],HHState17];
 DefTensor[Nu17[aa17],HHState17];
 DefTensor[Opacity17[-aa17],HHState17];
 tensorChecks17=<|
 \"P2ResponseCancellation\"->ToCanonical[Expand[(Jac17[aa17,-bb17]+JacShift17[aa17,-bb17])YResponse17[bb17]-Jac17[aa17,-cc17]FResponse17[cc17]+Mixed17[aa17,-dd17]Disp17[dd17]-JacShift17[aa17,-ee17]YResponse17[ee17]-Mixed17[aa17,-ff17]Disp17[ff17]-Jac17[aa17,-bb17](YResponse17[bb17]-FResponse17[bb17])]],
 \"HessianResponseSymmetry\"->ToCanonical[Hess17[aa17,-bb17,-cc17]Disp17[bb17]YResponse17[cc17]-Hess17[aa17,-bb17,-cc17]YResponse17[bb17]Disp17[cc17]],
 \"CommonResponseAdjoint\"->ToCanonical[Expand[Goal17[-aa17]DResponse17[aa17]-Adj17[-bb17]Jac17[bb17,-cc17]DResponse17[cc17]-(Goal17[-aa17]-Adj17[-dd17]Jac17[dd17,-aa17])DResponse17[aa17]]],
 \"EndpointJacobianShift\"->ToCanonical[Expand[(Jac17[aa17,-bb17]+JacShift17[aa17,-bb17])DResponse17[bb17]-Jac17[aa17,-cc17]DResponse17[cc17]-JacShift17[aa17,-dd17]DResponse17[dd17]]],
 \"HessianAdjointScalar\"->ToCanonical[Adj17[-aa17]Hess17[aa17,-bb17,-cc17]Disp17[bb17]YResponse17[cc17]-Adj17[-bb17]Hess17[bb17,-cc17,-aa17]YResponse17[cc17]Disp17[aa17]],
 \"RankOneMixedAction\"->ToCanonical[Nu17[aa17]Opacity17[-bb17]Disp17[bb17]-Nu17[aa17]Opacity17[-cc17]Disp17[cc17]]
 |>;
 <|\"Backend\"->\"xAct xTensor with xPerm Wolfram Language group algorithms\",\"ExternalCanonicalizerUsed\"->$xpermQ,\"TensorChecks\"->tensorChecks17,\"TensorAllZero\"->And@@(#===0& /@ Values[tensorChecks17]),\"Messages\"->$MessageList|>
 "];
 vars={xx,yy,zz,ww};pi=1+ff+xx+ff*yy+2*ff*zz;temp=ct*ww/pi;
 u={1,0,0,ww/pi};vel={vx,vy,vz,vw};
 uv=-xx*aH[temp]+ff*kHe[yy,zz,temp];
 gradU=D[uv,{vars}];hessU=D[uv,{vars,2}];
 du={0,0,0,vw/pi-ww*({1,ff,2*ff,0}.vel)/pi^2};
 projectorDerivative=(gradU.vel-vx*(gradU.u)-xx*(vel.hessU.u+gradU.du))/ff;
 temperatureDifference=ct*w17[tt]/p17[tt]-ct*(w17[tt]-dw17[tt])/(p17[tt]-de17[tt]);
 temperatureP4=(ct*dw17'[tt]-(ct*w17[tt]/p17[tt])*de17'[tt]-D[ct*w17[tt]/p17[tt],tt]*de17[tt]-temperatureDifference*(p17'[tt]-de17'[tt]))/(p17[tt]-de17[tt]);
 temperatureAdjoint=(ct*dw17'[tt]-(ct*(w17[tt]-dw17[tt])/(p17[tt]-de17[tt]))*de17'[tt]-D[ct*w17[tt]/p17[tt],tt]*de17[tt]-temperatureDifference*p17'[tt])/(p17[tt]-de17[tt]);
 rr={{r11,r12},{r21,r22}};rfull={{rf11,rf12},{rf21,rf22}};
 aa1=DiagonalMatrix[{1/(1+t11[tt]),1/(1+t12[tt])}];
 tau=DiagonalMatrix[{t21[tt],t22[tt]}];aa=Inverse[IdentityMatrix[2]+tau];af=Inverse[IdentityMatrix[2]+2*tau];
 ll1=IdentityMatrix[2]-aa1;ll=IdentityMatrix[2]-aa;lf=IdentityMatrix[2]-af;
 c1=tau.aa.aa.af;c2=tau.tau.aa.aa.af;
 z0={z01,z02};jbirth={j01,j02};q1=rr.z0+bb17[tt]*jbirth;
 pdirect=ll1.q1+ll.(rr.aa1.q1+bb17[tt]*jbirth)-lf.(rfull.z0+2*bb17[tt]*jbirth);
 sectors={-(IdentityMatrix[2]-ll.rr).(aa1-aa).q1,ll.(rr.aa-aa.rr).q1,ll.(IdentityMatrix[2]-rr).rr.z0,c2.rr.rr.z0,lf.(rr.rr-rfull).z0,bb17[tt]*ll.aa.(rr-IdentityMatrix[2]).jbirth,-bb17[tt]*c1.jbirth};
 photonDerivativeCheck=Together /@ (D[pdirect,tt]-Total[D[#,tt]& /@ sectors]);
 mtest={{m11,m12},{m21,m22}};stest=IdentityMatrix[2]+mtest+MatrixPower[mtest,2];ftest={f01,f02};ltest={{l11,l12},{l21,l22}};dtest={d01,d02};
 vtest=stest.ftest;
 neumannCheck=Expand /@ ((IdentityMatrix[2]-mtest).dtest-ftest-ltest.dtest);
 scalarChecks=<|
 "FixedTemperatureTangent"->Together[Grad[temp,vars].u],
 "HeliumCoefficientProjector"->FullSimplify[uv-xx*(gradU.u)-ff*kHe[yy,zz,temp]],
 "HeliumCoefficientDerivative"->FullSimplify[projectorDerivative-D[kHe[yy,zz,temp],{vars}].vel],
 "FiniteTemperatureP4"->Together[D[temperatureDifference,tt]-temperatureP4],
 "CommonTemperatureCovector"->Together[temperatureP4-temperatureAdjoint],
 "PhotonSevenSectorValue"->(Together /@ (pdirect-Total[sectors])),
 "PhotonSevenSectorDerivative"->photonDerivativeCheck,
 "FiniteNeumannMatrixIdentityM2"->(Expand /@ Flatten[stest.(IdentityMatrix[2]-mtest)-(IdentityMatrix[2]-MatrixPower[mtest,3])]),
 "FiniteNeumannResponseRemainder"->(Expand /@ (dtest-vtest-MatrixPower[mtest,3].dtest-stest.ltest.dtest-stest.neumannCheck))
 |>;
 <|"Status"->"Completed","WolframVersion"->$Version,"ArchiveSHA256"->FileHash[arc,"SHA256","HexString"],"xTensorSHA256"->FileHash[xf,"SHA256","HexString"],"TensorResult"->tensorResult,"ScalarChecks"->scalarChecks,"ScalarAllZero"->And@@(#===0& /@ Flatten[Values[scalarChecks]]),"Scope"->"Exact symbolic identities; two-slot arbitrary noncommuting remap model is algebraic, physical 35-slot enclosures are separate stored-data execution."|>
]
