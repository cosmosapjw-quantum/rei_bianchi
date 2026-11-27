(* Independent polynomial differentiation oracle: does not call source moment
   helper to construct any expected moment. All energies dimensionless epsilon0. *)
ClearAll[PHYS86Assert,PHYS86Zero,PHYS86Run,PHYS86Snapshot,PHYS86Guard];
PHYS86Checks={};PHYS86Rows={};PHYS86Guards={};PHYS86Failures={};PHYS86SymbolicResiduals={};PHYS86Started=False;
PHYS86Assert[value_,label_]:=Module[{ok=TrueQ[value]},AppendTo[PHYS86Checks,<|"label"->label,"pass"->ok|>];If[!ok,AppendTo[PHYS86Failures,label]]];
PHYS86Zero[value_,label_]:=PHYS86Assert[Together[value]===0,label];
SetAttributes[PHYS86Guard,HoldFirst];
PHYS86Guard[expr_,label_,tag_]:=Module[{v=expr},AppendTo[PHYS86Guards,{label,If[FailureQ[v],ToString[First[v]],"NOT_FAILURE"]}];PHYS86Assert[FailureQ[v]&&ToString[First[v]]===tag,"guard:"<>label]];
PHYS86Snapshot[status_]:=<|"schema"->"PHYS86_FINITE_MOMENT_CERT_V1","status"->status,"counts"->{Length[PHYS86Rows],Length[PHYS86Guards],Length[PHYS86Checks],Count[Lookup[PHYS86Checks,"pass"],True]},
 "bits"->StringJoin[If[TrueQ[#],"1","0"]&/@Lookup[PHYS86Checks,"pass"]],"labels"->Lookup[PHYS86Checks,"label"],
 "rows"->PHYS86Rows,"guards"->PHYS86Guards,"symbolic_residuals"->PHYS86SymbolicResiduals,"failures"->PHYS86Failures,
 "runtime"->{$Version,$SystemID},"scope"->"constructed finite positive exponential family; symbolic Juttner/NR identities","kernel_count"->1,"hardware"->"UNOBSERVED","HH_R10"->"OFF"|>;
PHYS86Run[]:=Module[{q,points,ea,eb,wa,wb,g,h,kc,zA,zB,n,hPoly,jPoly,kappa,avgA,avgB,varA,varB,meanS,varS,meanH,joint,cov,selection,curvature,
 src,srcT,rs,vals,uc,rate,cv,raw,composed,srcTD,slopeTD,correction,wrong,zeroRate,z,r,ratioD,recRules,energyFromZ,cvRaw,cvTarget,asymK,rNR,uNR,cvNR,kB,temp,nTh,logSlope,nrSource,formalS,symbolicLabels},
 If[PHYS86Started,Return[PHYS86Snapshot["REFUSED_REPEATED_CAMPAIGN"]]];PHYS86Started=True;
 points={1/2,2/3,3/4};ea={2,3};eb={4,6};wa={1,2};wb={2,1};g={{1,3},{2,4}};h={{0,1},{1,0}};kc={{1,2},{3,5}};
 zA=q^2+2*q^3;zB=2*q^4+q^6;n=2*q^6+8*q^7+3*q^8+8*q^9;
 hPoly=8*q^7+3*q^8;jPoly=24*q^7+6*q^8;kappa=n/(zA*zB);
 avgA=q*D[zA,q]/zA;avgB=q*D[zB,q]/zB;
 varA=q*D[avgA,q];varB=q*D[avgB,q];meanS=q*D[n,q]/n;varS=q*D[meanS,q];
 meanH=hPoly/n;joint=jPoly/n;cov=q*D[joint,q];selection=q*D[kappa,q]/kappa;curvature=q*D[selection,q];
 Do[
 src=PHYS86Moments[point,ea,eb,wa,wb,g,h,kc];
 PHYS86Assert[AssociationQ[src]&&src["status"]==="POSITIVE_RATE","q"<>ToString[index]<>".positive"];
 If[AssociationQ[src]&&KeyExistsQ[src,"selection"],
 vals={src["N"]-n,src["Za"]-zA,src["Zb"]-zB,src["rate_coefficient"]-kappa,src["meanA"]-avgA,src["meanB"]-avgB,src["varA"]-varA,src["varB"]-varB,src["meanS"]-meanS,src["varS"]-varS,src["meanH"]-meanH,src["jointHKc"]-joint,src["covHKcS"]-cov,src["selection"]-selection,src["curvature"]-curvature}/.q->point;
 Do[PHYS86Zero[vals[[j]],"q"<>ToString[index]<>".r"<>ToString[j]],{j,Length[vals]}];
 raw=rate*(-meanS+avgA+avgB+joint-meanH*uc)/cv/.q->point;
 composed=PHYS86TemperatureSource[src,uc,rate,cv];
 PHYS86Zero[Expand[cv*(composed-raw)/rate],"q"<>ToString[index]<>".source_coeff"];
 (* T-dependent kernel has explicit factor q. Source moments are recomputed;
    independent correction differentiates only q, not incoming q^S weights. *)
 srcTD=PHYS86Moments[point,ea,eb,wa,wb,point*g,h,kc];
 slopeTD=(q*D[q*kappa,q]/(q*kappa))/.q->point;
 correction=(q*D[q,q]*n/(q*n))/.q->point;
 PHYS86Zero[srcTD["selection"]-(slopeTD-correction),"q"<>ToString[index]<>".kernel_corrected"];
 PHYS86Zero[srcTD["meanS"]-src["meanS"],"q"<>ToString[index]<>".measure_unchanged"];
 wrong=Together[srcTD["selection"]-slopeTD];PHYS86Assert[wrong=!=0,"q"<>ToString[index]<>".wrong_nonzero"];
 AppendTo[PHYS86Rows,<|"q"->point,"moments"->Lookup[src,{"rate_coefficient","meanA","meanB","meanS","varS","selection","curvature","meanH","jointHKc","covHKcS"}],"residuals"->(Together/@vals),"source_coefficient_residual"->Together[cv*(composed-raw)/rate],"kernel"->{Together[slopeTD],Together[correction],Together[wrong]}|>]
 ],{index,3},{point,{points[[index]]}}];
 PHYS86Assert[Length[PHYS86Rows]===3,"campaign.three_rows"];
 zeroRate=PHYS86Moments[1/2,ea,eb,wa,wb,0*g,h,kc];
 PHYS86Assert[zeroRate["status"]==="ZERO_RATE"&&zeroRate["source"]===0&&zeroRate["normalized_moments"]==="UNDEFINED","zero.rate"];
 PHYS86Zero[PHYS86TemperatureSource[zeroRate,uc,rate,cv],"zero.source"];
 PHYS86Zero[PHYS86TemperatureSource["UNDEFINED",uc,0,cv],"zero.before_means"];
 PHYS86Guard[PHYS86Moments[0,ea,eb,wa,wb,g,h,kc],"q_zero","INVALID_Q"];
 PHYS86Guard[PHYS86Moments[1,ea,eb,wa,wb,g,h,kc],"q_one","INVALID_Q"];
 PHYS86Guard[PHYS86Moments[-1/2,ea,eb,wa,wb,g,h,kc],"q_negative","INVALID_Q"];
 PHYS86Guard[PHYS86Moments[1/2,ea,eb,{-1,2},wb,g,h,kc],"negative_weight","INVALID_POSITIVE_WEIGHTS"];
 PHYS86Guard[PHYS86Moments[1/2,ea,eb,{0,2},wb,g,h,kc],"zero_base_weight","INVALID_POSITIVE_WEIGHTS"];
 PHYS86Guard[PHYS86Moments[1/2,ea,eb,wa,wb,{{-1,3},{2,4}},h,kc],"negative_kernel","INVALID_KERNEL"];
 PHYS86Guard[PHYS86Moments[1/2,ea,eb,wa,wb,g,{{1/2,1},{1,0}},kc],"fractional_membership","INVALID_MEMBERSHIP"];
 PHYS86Guard[PHYS86TemperatureSource[zeroRate,uc,rate,0],"zero_cv","NONPOSITIVE_CV"];
 PHYS86Guard[PHYS86TemperatureSource[zeroRate,uc,rate,-1],"negative_cv","NONPOSITIVE_CV"];
 PHYS86Guard[PHYS86TemperatureSource[zeroRate,uc,-1,cv],"negative_rate","NEGATIVE_RATE"];
 (* Symbolic Juttner differential identities via Bessel derivative and recurrence. *)
 recRules={BesselK[0,z]->BesselK[2,z]-2*BesselK[1,z]/z,BesselK[3,z]->BesselK[1,z]+4*BesselK[2,z]/z};
 ratioD=Together[D[BesselK[1,z]/BesselK[2,z],z]/.recRules];
 energyFromZ=Together[-D[BesselK[2,z]/z,z]/(BesselK[2,z]/z)/.recRules];
 cvRaw=3-z^2*ratioD;cvTarget=3+z^2-z^2*(BesselK[1,z]/BesselK[2,z])^2-3*z*BesselK[1,z]/BesselK[2,z];
 (* Standard large-z K_nu series coefficients, common exp/sqrt prefactor
    cancels. Exact coefficient construction supplies symbolic NR algebra. *)
 asymK[nu_]:=Sum[Product[4*nu^2-(2*j-1)^2,{j,1,i}]/(i!*(8*z)^i),{i,0,3}];
 rNR=Normal[Series[asymK[1]/asymK[2],{z,Infinity,3}]];
 uNR=Limit[z*(rNR-1)+3,z->Infinity];cvNR=Limit[3-z^2*D[rNR,z],z->Infinity];
 nrSource=-rate*kB*temp^2*(logSlope/temp)/(3*nTh*kB/2);
 formalS=-2*rate*temp*logSlope/(3*nTh);
 PHYS86SymbolicResiduals=Together/@{ratioD-((BesselK[1,z]/BesselK[2,z])^2+3*BesselK[1,z]/(z*BesselK[2,z])-1),energyFromZ-(BesselK[1,z]/BesselK[2,z]+3/z),cvRaw-cvTarget,uNR-3/2,cvNR-3/2,nrSource-formalS,(nrSource/.logSlope->1/2)+rate*temp/(3*nTh),nrSource/.logSlope->0};
 symbolicLabels={"bessel_ratio_derivative","partition_mean","heat_capacity","nr_u","nr_cv","nr_source","constant_sigma","inverse_speed"};
 Do[PHYS86Zero[PHYS86SymbolicResiduals[[j]],"symbolic."<>symbolicLabels[[j]]],{j,Length[symbolicLabels]}];
 PHYS86Snapshot[If[PHYS86Failures==={},"PASS","FAIL_PRESERVED"]]
];
