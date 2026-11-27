(* Independent four-vector and incidence oracle; never imports PHYS81 code. *)
BeginPackage["PHYS85Verify`",{"PHYS85`"}];
PHYS85RunVerification::usage="Run one exact reference campaign: 36 event rows, 6 ensembles, controls and symbolic witnesses.";
PHYS85VerificationSnapshot::usage="Preserve partial raw outcomes after failure or timeout.";
Begin["`Private`"];
$checks={};$cases={};$ensembles={};$guards={};$symbolics={};$failures={};$started=False;
assert[value_,label_]:=Module[{ok=TrueQ[value]},AppendTo[$checks,<|"label"->label,"pass"->ok|>];If[!ok,AppendTo[$failures,label];Throw[label,"PHYS85_FIRST_FAILURE"]]];
zero[x_,label_]:=assert[Together[x]===0,label];
(* Independent literal-pair reader: does not call production rational helper. *)
pair[a_]:=a["numerator"]/a["denominator"];
PHYS85VerificationSnapshot[status_]:=<|"schema"->"PHYS85_EXACT_REFERENCE_REPORT_V1","status"->status,"event_rows"->$cases,"event_row_count"->Length[$cases],"expected_event_rows"->36,"ensemble_rows"->$ensembles,"ensemble_row_count"->Length[$ensembles],"expected_ensemble_rows"->6,"execution_accounting"-><|"constructed_event_application_rows_returned"->Count[Lookup[$cases,"source"],_Association],"constructed_ensemble_application_rows_returned"->Count[Lookup[$ensembles,"source"],_Association],"verifier_assertions_evaluated"->Length[$checks],"guard_controls_evaluated"->Length[$guards],"scope"->"One bounded call combines conditional constructed event/ensemble applications and independent verification; row counts exclude extra API calls within ensembles and rejection controls."|>,"assertions"->$checks,"assertion_count"->Length[$checks],"passed_assertion_count"->Count[Lookup[$checks,"pass"],True],"guard_controls"->$guards,"guard_count"->Length[$guards],"symbolic_checks"->$symbolics,"failures"->$failures,"new_physical_nuclear_rates"->0,"parent_kernel_calls"->0,"old_cold_case_replays"->0,"local_numerical_children"->0,"single_kernel"->True,"parallel_kernel_launches"->0,"remote_hardware_identity"->"UNOBSERVED","production_admission"->"NOT_ISSUED","HH_R10"->"OFF"|>;
makeEvent[ch_,fixture_,owner_,route_]:=<|"channel"->ch,"K_com_MeV"->pair[fixture["K_com_MeV"]],"boost_r"->pair[fixture["boost_r"]],"mu"->pair[fixture["mu"]],"daughter_owner"->owner,"radiation_route"->route|>;
(* Oracle builds both time/z four-vectors by matrix multiplication. The transverse
   momentum is represented by its squared norm, avoiding artificial square roots. *)
oracle[event_,input_]:=Module[{species,rows,masses,ma,mb,mc,w,r,g,b,u,p,ec,boost,photon,daughter,transverse2,h,kin,energies,counts,az},
 species=Switch[event["channel"],"np_dgamma",{"n","p","d"},"nd_tgamma",{"n","d","t"},"pd_hgamma",{"p","d","h"}];
 rows=input["masses"];masses=Table[pair[rows[s]["mc_energy_MeV"]],{s,species}];{ma,mb,mc}=masses;
 w=ma+mb+event["K_com_MeV"];r=event["boost_r"];u=event["mu"];g=(1+r*r)/(1-r*r);b=2*r/(1+r*r);
 p=(w*w-mc*mc)/(2*w);ec=(w*w+mc*mc)/(2*w);boost={{g,g*b},{g*b,g}};
 photon=boost.{p,p*u};daughter=boost.{ec,-p*u};transverse2=p*p*(1-u*u);
 h=Switch[event["daughter_owner"],"fast_birth",0,"thermal_birth_model",1];kin=g*w-ma-mb;
 energies={h*(daughter[[1]]-mc)-kin,(1-h)*(daughter[[1]]-mc),mc-ma-mb,0,If[event["radiation_route"]==="emissivity_handoff",photon[[1]],0],If[event["radiation_route"]==="immediate_escape",photon[[1]],0]};
 counts={h-2,1-h,-1,0};
 az=Table[rows[species[[3]]][key]-rows[species[[1]]][key]-rows[species[[2]]][key],{key,{"A","Z"}}];
 <|"photon_four_tz"->photon,"daughter_four_tz"->daughter,"transverse_momentum_squared"->transverse2,"photon_null_residual"->photon[[1]]^2-photon[[2]]^2-transverse2,"daughter_mass_shell_residual"->daughter[[1]]^2-daughter[[2]]^2-transverse2-mc^2,"total_energy_residual"->photon[[1]]+daughter[[1]]-g*w,"total_boost_momentum_residual"->photon[[2]]+daughter[[2]]-g*b*w,"energy_columns"->energies,"count_columns"->counts,"A_Z_incidence"->az,"gamma_identity_residual"->g^2*(1-b^2)-1,"Kc"->daughter[[1]]-mc,"Kin"->kin,"Egamma"->photon[[1]]|>
];
checkEvent[row_,o_,label_]:=Module[{energies=Values[row["energy_columns_MeV"]],counts=Values[row["count_columns"]]},
 Do[zero[o[key],label<>":"<>key],{key,{"gamma_identity_residual","photon_null_residual","daughter_mass_shell_residual","total_energy_residual","total_boost_momentum_residual"}}];
 Do[zero[energies[[i]]-o["energy_columns"][[i]],label<>":energy_column_"<>ToString[i]],{i,6}];
 assert[counts===o["count_columns"],label<>":exact_particle_counts"];
 zero[Total[energies],label<>":six_column_closure"];zero[row["energy_residual_MeV"],label<>":actual_energy_residual"];
 zero[counts[[1]]+counts[[2]]+1,label<>":nuclear_number_incidence"];
 assert[counts[[4]]===0,label<>":electron_unchanged"];assert[o["A_Z_incidence"]==={0,0},label<>":A_Z_oracle"];
 assert[Values[row["incidence_residuals"]]==={0,0},label<>":A_Z_source"];
 zero[row["K_c_normal_MeV"]-o["Kc"],label<>":daughter_kinetic"];zero[row["K_in_normal_MeV"]-o["Kin"],label<>":incoming_kinetic"];
 zero[row["E_gamma_normal_MeV"]-o["Egamma"],label<>":photon_energy"];
 assert[row["E_gamma_normal_MeV"]>0&&row["K_c_normal_MeV"]>0&&row["K_in_normal_MeV"]>0,label<>":nondegenerate_fixture_positive"];
 zero[energies[[5]]+energies[[6]]-row["emitted_diagnostic_MeV"],label<>":single_owned_radiation"];
];
reject[expr_,label_]:=Module[{result=expr},AppendTo[$guards,<|"label"->label,"result"->result,"rejected"->FailureQ[result]|>];assert[FailureQ[result],"guard:"<>label]];
(* Hold the expression until inside reject; a guard is evaluated exactly once. *)
SetAttributes[reject,HoldFirst];
symbolic[]:=Module[{r,w,mc,u,g,b,p,ec,eg,ed,pzg,pzd,pt2,x,s,theta,i1,i2,kappa,rateSlope,powerI1,powerI2,powerMean,tRate,tGas,nTh,slope,tdot,cov,h1,h2,h3,k1,k2,k3,kB,kMean,uDot,nDot,rawTdot,ws,hs,ks,hbar,kbar,centeredCov},
 g=(1+r^2)/(1-r^2);b=2*r/(1+r^2);p=(w^2-mc^2)/(2*w);ec=(w^2+mc^2)/(2*w);
 eg=g*(p+b*p*u);ed=g*(ec-b*p*u);pzg=g*(p*u+b*p);pzd=g*(-p*u+b*ec);pt2=p^2*(1-u^2);
 zero[g^2*(1-b^2)-1,"symbolic:boost_identity"];
 zero[ed^2-pzd^2-pt2-mc^2,"symbolic:daughter_mass_shell"];
 zero[eg^2-pzg^2-pt2,"symbolic:photon_null"];
 zero[eg+ed-g*w,"symbolic:energy_conservation"];
 zero[pzg+pzd-g*b*w,"symbolic:momentum_conservation"];
 (* dI1/dtheta=I2/theta^2 is the separately stated differentiated-integral premise. *)
 kappa=theta^(-3/2)*i1[theta];
 rateSlope=(theta*D[kappa,theta]/kappa)/.Derivative[1][i1][theta]->i2/theta^2;
 zero[rateSlope-(-3/2+i2/(theta*i1[theta])),"symbolic:maxwellian_rate_log_slope"];
 zero[D[Exp[-x/theta],theta]-x*Exp[-x/theta]/theta^2,"symbolic:differentiated_integrand"];
 (* Scale K=theta*x; Gamma recurrence provides the exact power-law ratio. *)
 powerI1=Integrate[x^(s+1)*Exp[-x],{x,0,Infinity},Assumptions->Element[s,Reals]&&s>-2];
 powerI2=Integrate[x^(s+2)*Exp[-x],{x,0,Infinity},Assumptions->Element[s,Reals]&&s>-2];
 powerMean=FullSimplify[theta*powerI2/powerI1,Assumptions->Element[s,Reals]&&s>-2&&theta>0];
 assert[TrueQ[FullSimplify[powerMean==(s+2)*theta,Assumptions->Element[s,Reals]&&s>-2&&theta>0]],"symbolic:power_law_selected_energy"];
 tdot=-(2/3)*(tRate*tGas/nTh)*(s+1/2);
 zero[(tdot/.s->0)+tRate*tGas/(3*nTh),"symbolic:constant_sigma_temperature"];
 zero[tdot/.s->(-1/2),"symbolic:inverse_speed_temperature"];
 uDot=-tRate*(3*kB*tGas/2+kMean);nDot=-2*tRate;
 rawTdot=2*uDot/(3*kB*nTh)-tGas*nDot/nTh;
 zero[(rawTdot/.kMean->kB*tGas*(3/2+slope))-(-(2/3)*tRate*tGas*slope/nTh),"symbolic:all_fast_raw_EOS_rate_slope"];
 cov=(h1*k1/2+h2*k2/3+h3*k3/6)-(h1/2+h2/3+h3/6)*(k1/2+k2/3+k3/6);
 ws={1/2,1/3,1/6};hs={h1,h2,h3};ks={k1,k2,k3};
 hbar=Sum[ws[[j]]*hs[[j]],{j,3}];kbar=Sum[ws[[j]]*ks[[j]],{j,3}];
 centeredCov=Sum[ws[[j]]*(hs[[j]]-hbar)*(ks[[j]]-kbar),{j,3}];
 zero[centeredCov-cov,"symbolic:centered_joint_owner_energy_covariance"];
 AppendTo[$symbolics,<|"power_integral_I1"->powerI1,"power_integral_I2"->powerI2,"selected_mean"->powerMean,"rate_slope"->rateSlope,"all_fast_temperature"->tdot,"scope"->"Conditional NR common-T Maxwellian theorem; no physical cross section supplied."|>];
];
PHYS85RunVerification[input_]:=Module[{config,channels,fixtures,owners,routes,e,row,o,label,events,weights,agg,oracles,energyExpected,countExpected,joint,mh,mkc,base,mixed,result},
 If[$started,Return[<|"status"->"REFUSED_REPEATED_CAMPAIGN_IN_SAME_KERNEL"|>]];$started=True;
 result=Catch[
 config=PHYS85Configure[input];assert[!FailureQ[config],"configure:frozen_exact_inputs"];
 channels={"np_dgamma","nd_tgamma","pd_hgamma"};fixtures=input["event_inputs"];owners={"fast_birth","thermal_birth_model"};routes={"immediate_escape","emissivity_handoff"};
 assert[Length[fixtures]===3,"fixtures:three_new_noncold_inputs"];
 Do[
  e=makeEvent[ch,fixture,owner,route];row=PHYS85EventOwner[e];label=ch<>":"<>fixture["id"]<>":"<>owner<>":"<>route;
  AppendTo[$cases,<|"id"->label,"source"->row|>];assert[!FailureQ[row],label<>":source_returned"];
  o=oracle[e,input];$cases[[-1]]=Append[$cases[[-1]],"independent_oracle"->o];checkEvent[row,o,label],
 {ch,channels},{fixture,fixtures},{owner,owners},{route,routes}];
 assert[Length[$cases]===36,"campaign:36_event_rows"];
 weights={1/2,1/3,1/6};
 Do[
 events=Table[makeEvent[ch,fixtures[[i]],If[i==1,"fast_birth","thermal_birth_model"],route],{i,3}];
 agg=PHYS85EnsembleOwner[events,weights];label=ch<>":ensemble:"<>route;AppendTo[$ensembles,<|"id"->label,"source"->agg|>];assert[!FailureQ[agg],label<>":source_returned"];
 oracles=oracle[#,input]&/@events;
 energyExpected=Table[Sum[weights[[i]]*oracles[[i]]["energy_columns"][[j]],{i,3}],{j,6}];
 countExpected=Table[Sum[weights[[i]]*oracles[[i]]["count_columns"][[j]],{i,3}],{j,4}];
 Do[zero[Values[agg["mean_energy_columns_MeV"]][[j]]-energyExpected[[j]],label<>":energy_"<>ToString[j]],{j,6}];
 assert[Values[agg["mean_count_columns"]]===countExpected,label<>":counts"];
 joint=weights[[2]]*oracles[[2]]["Kc"]+weights[[3]]*oracles[[3]]["Kc"];mh=weights[[2]]+weights[[3]];mkc=Sum[weights[[i]]*oracles[[i]]["Kc"],{i,3}];
 zero[agg["mean_joint_hKc_MeV"]-joint,label<>":joint_owner_energy"];
 zero[agg["owner_energy_covariance_MeV"]-(joint-mh*mkc),label<>":covariance"];
 assert[joint-mh*mkc=!=0,label<>":nonzero_owner_energy_covariance"];
 zero[agg["energy_residual_MeV"],label<>":actual_energy_residual"];zero[agg["particle_residual"],label<>":particle_residual"];
 $ensembles[[-1]]=Append[$ensembles[[-1]],"independent_oracle"-><|"energy_columns"->energyExpected,"count_columns"->countExpected,"joint_hKc"->joint,"covariance"->joint-mh*mkc|>],
 {ch,channels},{route,routes}];
 assert[Length[$ensembles]===6,"campaign:6_ensemble_rows"];
 (* Compare corresponding route rows, moving each radiative energy exactly once. *)
 Do[With[{a=$cases[[i]]["source"],brow=$cases[[i+1]]["source"]},assert[a["count_columns"]===brow["count_columns"],"route:counts_"<>ToString[i]];zero[a["energy_columns_MeV"]["radiation_escape"]-brow["energy_columns_MeV"]["radiation_injected"],"route:moved_once_"<>ToString[i]]],{i,1,35,2}];
 base=makeEvent[First[channels],First[fixtures],"fast_birth",First[routes]];
 reject[PHYS85EventOwner[Join[base,<|"channel"->"unknown"|>]],"unknown_channel"];
 Do[reject[PHYS85EventOwner[Join[base,<|key->0.1|>]],"nonrational_"<>key],{key,{"K_com_MeV","boost_r","mu"}}];
 reject[PHYS85EventOwner[Join[base,<|"K_com_MeV"->-1|>]],"negative_K"];
 reject[PHYS85EventOwner[Join[base,<|"boost_r"->-1/10|>]],"negative_r"];
 reject[PHYS85EventOwner[Join[base,<|"boost_r"->1|>]],"r_one"];
 reject[PHYS85EventOwner[Join[base,<|"boost_r"->2|>]],"r_above_one"];
 reject[PHYS85EventOwner[Join[base,<|"mu"->2|>]],"mu_above_one"];
 reject[PHYS85EventOwner[Join[base,<|"mu"->-2|>]],"mu_below_minus_one"];
 reject[PHYS85EventOwner[KeyDrop[base,"daughter_owner"]],"missing_owner"];
 reject[PHYS85EventOwner[Join[base,<|"daughter_owner"->{"fast_birth","thermal_birth_model"}|>]],"conflicting_owners"];
 reject[PHYS85EventOwner[Join[base,<|"daughter_owner"->"zeta_only"|>]],"zeta_only_owner"];
 reject[PHYS85EventOwner[Join[KeyDrop[base,"daughter_owner"],<|"zeta"->1/2|>]],"energy_fraction_without_membership"];
 reject[PHYS85EventOwner[Join[base,<|"radiation_route"->"both"|>]],"invalid_route"];
 reject[PHYS85EventOwner[KeyDrop[base,"radiation_route"]],"missing_route"];
 reject[PHYS85EnsembleOwner[{},{}],"empty_ensemble"];
 reject[PHYS85EnsembleOwner[{base},{-1}],"negative_weight"];
 reject[PHYS85EnsembleOwner[{base},{1/2}],"nonnormalized_weight"];
 reject[PHYS85EnsembleOwner[{base},{1.0}],"inexact_weight"];
 reject[PHYS85EnsembleOwner[{base},{}],"weight_length"];
 mixed=Join[base,<|"channel"->"nd_tgamma"|>];reject[PHYS85EnsembleOwner[{base,mixed},{1/2,1/2}],"mixed_channels"];
 reject[PHYS85EnsembleOwner[{base,Join[base,<|"radiation_route"->"emissivity_handoff"|>]},{1/2,1/2}],"mixed_routes"];
 symbolic[];"PASS", "PHYS85_FIRST_FAILURE",( "FAIL_FIRST_ATTEMPT_PRESERVED"&)];
 PHYS85VerificationSnapshot[result]
];
End[];
EndPackage[];
