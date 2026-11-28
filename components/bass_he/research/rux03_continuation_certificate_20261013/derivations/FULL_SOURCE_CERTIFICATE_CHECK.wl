(* THEORY06: exact full-source certificate arithmetic; no RHS or ODE evaluation. *)
ClearAll["Global`*"];
caps = ImportString["{\"coefficient_caps_cm3_s\":{\"RR\":[\"1/5000000000000\",\"1/5000000000000\",\"1/1000000000000\"],\"CI\":[\"1/1000000000\",\"1/25000000000\",\"1/50000000000000\"],\"DR\":[\"1/25000000000000\",\"1/500000000000000\"]},\"temperature_derivative_caps_cm3_s_K\":{\"RR\":[\"7/1000000000000000000\",\"3/1000000000000000000\",\"1/25000000000000000\"],\"CI\":[\"1/10000000000000\",\"7/1000000000000000\",\"7/1000000000000000000\"],\"DR\":[\"1/125000000000000000\",\"1/2000000000000000000\"]},\"kinetic_caps_erg_cm3_s\":{\"RR\":[\"1/500000000000000000000000\",\"1/500000000000000000000000\",\"1/100000000000000000000000\"],\"DR\":[\"3/1000000000000000000000000\",\"1/5000000000000000000000000\"]},\"kinetic_temperature_derivative_caps_erg_cm3_s_K\":{\"RR\":[\"1/50000000000000000000000000000\",\"1/100000000000000000000000000000\",\"1/10000000000000000000000000000\"],\"DR\":[\"3/5000000000000000000000000000\",\"1/25000000000000000000000000000\"]},\"sigma_caps_cm2\":[[\"3/1000000000000000000\",\"1/1000000000000000000\",\"1/5000000000000000000\"],[\"0\",\"1/125000000000000000\",\"1/500000000000000000\"],[\"0\",\"0\",\"1/500000000000000000\"]],\"sigma_derivative_caps_cm2_per_ev\":[[\"1/1000000000000000000\",\"3/10000000000000000000\",\"3/100000000000000000000\"],[\"0\",\"1/1000000000000000000\",\"3/10000000000000000000\"],[\"0\",\"0\",\"3/10000000000000000000\"]]}", "RawJSON"];
rateInputSHA = "ef9fcb4d6d18d388bc45ae71844b1f8d3c284e529185898d195cdf28add69546";

{kernelSeconds, answer} = AbsoluteTiming[
 dHyd=1/1000; cLight=29979245800;
 epsEV=1602176634/10^21;
 chi={13598434599702/10^12,24587389011/10^9,5441776/10^5};
 gStar=841/840; btStar={0,0,41/841};
 gBar=501/500; btBar=49/1000;
 lTemp=1400; lGamma=1/5000000; lBeta=3/1000000; lDelta=1/250000;
 eBar=141/250; le=1/250;
 yBar={501/1000,21/500,21/1000}; ly={1/1000,1/500,1/1000};
 vBar={501/1000,21/1000,21/1000}; lv=ConstantArray[1/1000,3];
 gammaRelBar=101/100; lGammaRel=1/2500000;
 photonE={23,23,35,35,70,70};
 directions={{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
 starE=MapThread[gStar*(1-btStar.#1)*#2&,{directions,photonE}];
 energyColumn={1,1,2,2,3,3}; pOld=1/100;
 sig=Map[ToExpression,caps["sigma_caps_cm2"],{2}];
 sigPrime=Map[ToExpression,caps["sigma_derivative_caps_cm2_per_ev"],{2}];
 rr=ToExpression /@ caps["coefficient_caps_cm3_s"]["RR"];
 ci=ToExpression /@ caps["coefficient_caps_cm3_s"]["CI"];
 dr=ToExpression /@ caps["coefficient_caps_cm3_s"]["DR"];
 rrp=ToExpression /@ caps["temperature_derivative_caps_cm3_s_K"]["RR"];
 cip=ToExpression /@ caps["temperature_derivative_caps_cm3_s_K"]["CI"];
 drp=ToExpression /@ caps["temperature_derivative_caps_cm3_s_K"]["DR"];
 rrk=(ToExpression /@ caps["kinetic_caps_erg_cm3_s"]["RR"])/epsEV;
 drk=(ToExpression /@ caps["kinetic_caps_erg_cm3_s"]["DR"])/epsEV;
 rrkp=(ToExpression /@ caps["kinetic_temperature_derivative_caps_erg_cm3_s_K"]["RR"])/epsEV;
 drkp=(ToExpression /@ caps["kinetic_temperature_derivative_caps_erg_cm3_s_K"]["DR"])/epsEV;
 ratePair[k_,kp_,yy_,lY_]:={dHyd*eBar*yy*k,
   dHyd*((le*yy+eBar*lY+2*eBar*yy*lGamma)*k+eBar*yy*kp*lTemp)};
 rrPairs=MapThread[ratePair,{rr,rrp,vBar,lv}];
 ciPairs=MapThread[ratePair,{ci,cip,yBar,ly}];
 drPairs=MapThread[ratePair,{dr,drp,ConstantArray[vBar[[2]],2],ConstantArray[lv[[2]],2]}];
 rrKinPairs=MapThread[ratePair,{rrk,rrkp,vBar,lv}];
 drKinPairs=MapThread[ratePair,{drk,drkp,ConstantArray[vBar[[2]],2],ConstantArray[lv[[2]],2]}];
 bRR=rrPairs[[All,1]]; lRR=rrPairs[[All,2]];
 bCI=ciPairs[[All,1]]; lCI=ciPairs[[All,2]];
 bDR=drPairs[[All,1]]; lDR=drPairs[[All,2]];
 bBind=chi.bRR+chi[[2]]*Total[bDR];
 lBind=chi.lRR+chi[[2]]*Total[lDR];
 bKin=Total[rrKinPairs[[All,1]]]+Total[drKinPairs[[All,1]]];
 lKin=Total[rrKinPairs[[All,2]]]+Total[drKinPairs[[All,2]]];
 lambdaBar=Table[cLight*dHyd*yBar[[i]]*(1+btBar)*sig[[i,energyColumn[[q]]]],{i,3},{q,6}];
 lambdaL=Table[cLight*dHyd*(ly[[i]]*(1+btBar)*sig[[i,energyColumn[[q]]]]+
   yBar[[i]]*lBeta*sig[[i,energyColumn[[q]]]]+
   yBar[[i]]*(1+btBar)*sigPrime[[i,energyColumn[[q]]]]*photonE[[q]]*lDelta),{i,3},{q,6}];
 totalLambdaBar=Total[lambdaBar]; totalLambdaL=Total[lambdaL];
 bPho=pOld*lambdaBar; lPho0=pOld*lambdaL;
 lPho1=Table[pOld*lambdaBar[[i,q]]*totalLambdaL[[q]],{i,3},{q,6}];
 edgeB=Total /@ bPho; edgeL0=Total /@ lPho0; edgeL1=Total /@ lPho1;
 chemicalRows[atom_,photo_,dielectronic_]:={atom[[1]]+photo[[1]],
   Total[atom[[2;;3]]]+Total[photo[[2;;3]]]+Total[dielectronic],atom[[3]]+photo[[3]]};
 bChem=chemicalRows[bCI+bRR,edgeB,bDR];
 lChem0=chemicalRows[lCI+lRR,edgeL0,lDR];
 lChem1=chemicalRows[ConstantArray[0,3],edgeL1,{0,0}];
 thermalPhoto[mat_]:=Sum[Abs[starE[[q]]-chi[[i]]]*mat[[i,q]],{i,3},{q,6}];
 momentumPhoto[mat_]:=Sum[photonE[[q]]*mat[[i,q]],{i,3},{q,6}];
 bThermal=thermalPhoto[bPho]+chi.bCI+gammaRelBar*bKin+(gammaRelBar-1)*bBind;
 lThermal0=thermalPhoto[lPho0]+chi.lCI+gammaRelBar*lKin+(gammaRelBar-1)*lBind+lGammaRel*(bKin+bBind);
 lThermal1=thermalPhoto[lPho1];
 bMomentum=momentumPhoto[bPho]+gBar*btBar*(bKin+bBind);
 lMomentum0=momentumPhoto[lPho0]+(btBar*lGamma+gBar*lBeta)*(bKin+bBind)+gBar*btBar*(lKin+lBind);
 lMomentum1=momentumPhoto[lPho1];
 (* s_m >= 1000 eV/H uniformly over the specified mu family. *)
 bRows=Join[1000*bChem,{4*bThermal},ConstantArray[bMomentum/1000,3]];
 lRows0=Join[1000*lChem0,{4*lThermal0},ConstantArray[lMomentum0/1000,3]];
 lRows1=Join[1000*lChem1,{4*lThermal1},ConstantArray[lMomentum1/1000,3]];
 bMax=Max[bRows]; l0Max=Max[lRows0]; l1Max=Max[lRows1];
 hCandidate=500000000;
 (* Explicit rational selector: H L0 <=1/8 and H^2 L1 <=1/8. *)
 hCert=Min[hCandidate,9/(10*bMax),1/(8*l0Max),If[l1Max==0,hCandidate,1/(8*hCandidate*l1Max)]];
 lRows=lRows0+hCert*lRows1; lMax=Max[lRows];
 displacement=hCert*bRows; selfMap=hCert*bMax; contraction=hCert*lMax;
 inverseBound=1/(1-contraction); branchDerivative=bMax*inverseBound;
 iterations=8; picardError=contraction^iterations/(1-contraction)*selfMap;
 photonFloor=Table[pOld/(1+hCert*totalLambdaBar[[q]]),{q,6}];
 tempBranchRadius=lTemp*selfMap; betaBranchRadius=lBeta*selfMap; gammaBranchRadius=lGamma*selfMap;
 (* New exact identities, distinct from parent-suite revalidation. *)
 pPlus=(pZero+hh*sZero)/(1+hh*ll);
 residualElimination=Together[pPlus-pZero-hh*sZero+hh*ll*pPlus];
 dEvent=D[lam[xx]*(pZero+hh*sZero)/(1+hh*tot[xx]),xx];
 dEventExpected=(pZero+hh*sZero)*(lam'[xx]/(1+hh*tot[xx])-hh*lam[xx]*tot'[xx]/(1+hh*tot[xx])^2);
 residualEvent=Together[dEvent-dEventExpected];
 hEventDerivative=D[hh*la*(pZero+hh*sZero)/(1+hh*ll),hh];
 residualParameter=Together[hEventDerivative-la*(pZero+2*hh*sZero+hh^2*ll*sZero)/(1+hh*ll)^2];
 (* Algebraic derivation of the full affine thermal row with all channels. *)
 incidence={{1,0,0},{0,1,0},{0,-1,1}};
 bindingVector={chi[[1]],chi[[2]],chi[[2]]+chi[[3]]};
 photoSymbols=Array[rPhoton,{3,6}]; ciSymbols=Array[rCollision,3]; rrSymbols=Array[rRadiative,3];
 betaSymbols=Array[velocity,3]; drTotal=rDRfirst+rDRsecond;
 chemicalSymbol=Sum[incidence[[i]]*(Total[photoSymbols[[i]]]+ciSymbols[[i]]-rrSymbols[[i]]),{i,3}]-incidence[[2]]*drTotal;
 bindSymbol=chi.rrSymbols+chi[[2]]*drTotal;
 labEnergySymbol=Sum[photonE[[q]]*photoSymbols[[i,q]],{i,3},{q,6}]-gasGamma*(kineticSymbol+bindSymbol);
 momentumSymbol=Sum[photonE[[q]]*directions[[q]]*Total[photoSymbols[[All,q]]],{q,6}]-gasGamma*betaSymbols*(kineticSymbol+bindSymbol);
 relSymbol=gStar*gasGamma*(1-btStar.betaSymbols);
 expectedThermal=Sum[(starE[[q]]-chi[[i]])*photoSymbols[[i,q]],{i,3},{q,6}]-chi.ciSymbols-relSymbol*kineticSymbol-(relSymbol-1)*bindSymbol;
 residualThermal=Expand[gStar*(labEnergySymbol-btStar.momentumSymbol)-bindingVector.chemicalSymbol-expectedThermal];
 checks=<|
  "CS01_eliminated_photon_finite_balance"->TrueQ[residualElimination==0],
  "CS02_candidate_event_chain_derivative"->TrueQ[residualEvent==0],
  "CS03_stage_parameter_derivative"->TrueQ[residualParameter==0],
  "CS04_full_affine_thermal_source_identity"->TrueQ[residualThermal==0],
  "CS05_relative_gamma_value_and_derivative_caps"->TrueQ[gStar*gBar*(1+(41/841)*btBar)<=gammaRelBar && gStar*((1+(41/841)*btBar)*lGamma+gBar*(41/841)*lBeta)<=lGammaRel],
  "CS06_nonnegative_seven_row_majorants"->TrueQ[Min[Join[bRows,lRows0,lRows1]]>=0 && bMax>0 && lMax>0],
  "CS07_explicit_positive_rational_stage_interval"->TrueQ[hCert>0 && hCert<=hCandidate && Denominator[hCert]>=1],
  "CS08_uniform_strict_self_map"->TrueQ[selfMap<=9/10 && selfMap<1],
  "CS09_uniform_strict_contraction_and_inverse"->TrueQ[contraction<=1/4 && contraction<1 && inverseBound<21/20],
  "CS10_certified_branch_temperature_and_velocity_guards"->TrueQ[tempBranchRadius<1400 && betaBranchRadius<lBeta && gammaBranchRadius<lGamma],
  "CS11_eight_Picard_updates_uniform_error_bound"->TrueQ[picardError<1/10^12],
  "CS12_positive_eliminated_photon_inventories"->TrueQ[Min[photonFloor]>0 && Max[photonFloor]<=pOld]
 |>;
 exactString[x_]:=ToString[x,InputForm];
 exactList[x_List]:=Map[exactString,x,{-1}];
 <|"schema"->"bass-he-theory06-full-source-certificate-v1",
 "unit"->"HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06",
 "kernel"->$Version,"system_id"->$SystemID,
 "rate_envelope_input_sha256"->rateInputSHA,
 "all_pass"->And@@Values[checks],"passed"->Count[Values[checks],True],"named_groups"->Length[checks],"checks"->checks,
 "identity_residuals"->(exactString /@ {residualElimination,residualEvent,residualParameter,residualThermal}),
 "H_seconds"->exactString[hCert],"H_julian_years_display"->N[hCert/31557600,18],
 "scaled_source_b_per_second"->exactList[bRows],
 "scaled_source_ell0_per_second"->exactList[lRows0],
 "scaled_source_ell1_per_second_squared"->exactList[lRows1],
 "scaled_source_ell_at_H_per_second"->exactList[lRows],
 "scaled_source_b_display"->N[bRows,18],"scaled_source_ell_at_H_display"->N[lRows,18],
 "B_per_second"->exactString[bMax],"L_H_per_second"->exactString[lMax],
 "HB"->exactString[selfMap],"HL_H"->exactString[contraction],
 "self_map_margin"->exactString[1-selfMap],"contraction_margin"->exactString[1-contraction],
 "inverse_Jacobian_infinity_bound"->exactString[inverseBound],
 "branch_parameter_derivative_per_second_bound"->exactString[branchDerivative],
 "scaled_branch_component_displacement"->exactList[displacement],
 "scaled_branch_component_displacement_display"->N[displacement,18],
 "H_lambda_upper_by_node"->exactList[hCert*totalLambdaBar],
 "photon_inventory_per_H_lower"->exactList[photonFloor],
 "temperature_branch_radius_K"->exactString[tempBranchRadius],
 "velocity_branch_Euclidean_radius"->exactString[betaBranchRadius],
 "gamma_branch_radius"->exactString[gammaBranchRadius],
 "Picard_update_count_for_bound"->iterations,"Picard_uniform_error_bound"->exactString[picardError],
 "Picard_error_display"->N[picardError,18],
 "summary_display"-><|"HB"->N[selfMap,18],"HL"->N[contraction,18],"inverse_bound"->N[inverseBound,18],"branch_derivative"->N[branchDerivative,18],"temperature_radius_K"->N[tempBranchRadius,18]|>,
 "kinetic_and_binding_bounds_eV_per_H_per_second"->exactList[{bKin,lKin,bBind,lBind}],
 "photon_lambda_bounds_per_second"->exactList[lambdaBar],
 "photon_lambda_derivative_bounds_per_second"->exactList[lambdaL],
 "scope"->"Exact rational evaluation of analytically proved full-domain majorants. No native RHS, inverse root sampling, nonlinear solve or ODE execution. Picard count is a proven a-priori error estimate, not an executed iteration trajectory."|>
];
answer=Join[answer,<|"kernel_seconds"->kernelSeconds|>];
ExportString[answer,"RawJSON"]
