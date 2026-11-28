(* PHYS85 exact supplied-event reference. No physical rate or stopping supplier. *)
BeginPackage["PHYS85`"];
PHYS85Configure::usage="Load frozen integer-pair masses without evaluating strings.";
PHYS85EventOwner::usage="Return exact normal-frame event count and six energy owners, or Failure.";
PHYS85EnsembleOwner::usage="Average same-channel, same-route events with normalized exact weights.";
PHYS85RationalPair::usage="Reconstruct one validated exact integer pair.";
Begin["`Private`"];
ClearAll[exactQ, fail, PHYS85RationalPair, PHYS85Configure, PHYS85EventOwner, PHYS85EnsembleOwner];
exactQ[x_]:=IntegerQ[x]||Head[x]===Rational;
fail[tag_]:=Failure[tag,<|"scope"->"PHYS85 exact reference"|>];
PHYS85RationalPair[a_]:=If[AssociationQ[a]&&Sort[Keys[a]]==={"denominator","numerator"}&&IntegerQ[a["numerator"]]&&IntegerQ[a["denominator"]]&&a["denominator"]>0,a["numerator"]/a["denominator"],fail["INVALID_RATIONAL_PAIR"]];
$mass=<||>;$nuclear=<||>;
$channels=<|"np_dgamma"->{"n","p","d"},"nd_tgamma"->{"n","d","t"},"pd_hgamma"->{"p","d","h"}|>;
$energyNames={"thermal","fast","nuclear_rest","atomic_binding","radiation_injected","radiation_escape"};
PHYS85Configure[input_]:=Module[{rows,values},
 If[!AssociationQ[input]||!KeyExistsQ[input,"masses"],Return[fail["INVALID_FROZEN_INPUT"]]];
 rows=input["masses"];
 If[!AssociationQ[rows]||Sort[Keys[rows]]=!={"d","h","n","p","t"},Return[fail["INVALID_MASS_SPECIES"]]];
 values=Association@Table[s->PHYS85RationalPair[rows[s]["mc_energy_MeV"]],{s,Keys[rows]}];
 If[!AllTrue[Values[values],exactQ[#]&&#>0&],Return[fail["INVALID_MASS_VALUE"]]];
 If[!AllTrue[Values[rows],IntegerQ[#["A"]]&&IntegerQ[#["Z"]]&&#["A"]>0&&0<=#["Z"]<=#["A"]&],Return[fail["INVALID_NUCLEAR_INCIDENCE"]]];
 $mass=values;$nuclear=Association@Table[s->KeyTake[rows[s],{"A","Z"}],{s,Keys[rows]}];
 <|"status"->"CONFIGURED","species"->Sort[Keys[$mass]],"physical_rate_evaluations"->0|>
];
PHYS85EventOwner[event_]:=Module[{allowed,required,ch,k,r,mu,owner,route,abc,ma,mb,mc,m,w,q,gamma,beta,egStar,kcStar,eg,kc,kin,h,energies,counts,incidence},
 If[!AssociationQ[event],Return[fail["EVENT_ASSOCIATION_REQUIRED"]]];
 required={"channel","K_com_MeV","boost_r","mu","daughter_owner","radiation_route"};allowed=required;
 If[!ContainsAll[Keys[event],required],Return[fail["MISSING_REQUIRED_EVENT_FIELD"]]];
 If[Complement[Keys[event],allowed]=!={},Return[fail["UNSUPPORTED_OR_CONFLICTING_EVENT_FIELD"]]];
 {ch,k,r,mu,owner,route}=Lookup[event,required];
 If[!KeyExistsQ[$channels,ch],Return[fail["UNKNOWN_CHANNEL"]]];
 If[Length[$mass]!=5,Return[fail["NOT_CONFIGURED"]]];
 If[!AllTrue[{k,r,mu},exactQ],Return[fail["EXACT_RATIONAL_INPUT_REQUIRED"]]];
 If[!(k>=0&&0<=r<1&&-1<=mu<=1),Return[fail["EVENT_DOMAIN_VIOLATION"]]];
 If[!MemberQ[{"thermal_birth_model","fast_birth"},owner],Return[fail["INVALID_OR_CONFLICTING_DAUGHTER_OWNER"]]];
 If[!MemberQ[{"immediate_escape","emissivity_handoff"},route],Return[fail["INVALID_RADIATION_ROUTE"]]];
 abc=$channels[ch];{ma,mb,mc}=Lookup[$mass,abc];m=ma+mb;w=m+k;q=m-mc;
 gamma=(1+r^2)/(1-r^2);beta=2*r/(1+r^2);
 egStar=(w-mc)*(w+mc)/(2*w);kcStar=(w-mc)^2/(2*w);
 eg=gamma*egStar*(1+beta*mu);kc=gamma*(mc+kcStar-beta*egStar*mu)-mc;kin=gamma*w-m;
 If[!(eg>0&&kc>=0&&kin>=0),Return[fail["NONPHYSICAL_CAPTURE_KINEMATICS"]]];
 h=If[owner==="thermal_birth_model",1,0];
 energies=AssociationThread[$energyNames,{h*kc-kin,(1-h)*kc,-q,0,If[route==="emissivity_handoff",eg,0],If[route==="immediate_escape",eg,0]}];
 counts=<|"thermal"->h-2,"fast"->1-h,"nuclear_total"->-1,"electron"->0|>;
 incidence=AssociationThread[{"A","Z"},Table[$nuclear[abc[[3]]][key]-$nuclear[abc[[1]]][key]-$nuclear[abc[[2]]][key],{key,{"A","Z"}}]];
 <|"schema"->"PHYS85_EXACT_EVENT_V1","input"->event,"channel"->ch,"daughter_owner"->owner,"radiation_route"->route,"h"->h,"gamma"->gamma,"beta"->beta,"K_in_normal_MeV"->kin,"K_c_normal_MeV"->kc,"E_gamma_normal_MeV"->eg,"emitted_diagnostic_MeV"->eg,"Q_MeV"->q,"count_columns"->counts,"energy_columns_MeV"->energies,"energy_residual_MeV"->Total[Values[energies]],"particle_residual"->counts["thermal"]+counts["fast"]+1,"incidence_residuals"->incidence,"physical_rate_evaluations"->0|>
];
PHYS85EnsembleOwner[events_,weights_]:=Module[{rows,n,ch,route,average,meanEnergy,meanCounts,mh,mkc,joint},
 If[!ListQ[events]||!ListQ[weights]||Length[events]==0||Length[events]!=Length[weights],Return[fail["INVALID_OR_EMPTY_ENSEMBLE"]]];
 If[!AllTrue[weights,exactQ[#]&&#>=0&]||Total[weights]=!=1,Return[fail["INVALID_OR_NONNORMALIZED_WEIGHTS"]]];
 rows=PHYS85EventOwner/@events;
 If[AnyTrue[rows,FailureQ],Return[fail["INVALID_ENSEMBLE_EVENT"]]];
 ch=Lookup[rows,"channel"];route=Lookup[rows,"radiation_route"];
 If[Length[DeleteDuplicates[ch]]!=1,Return[fail["MIXED_CHANNELS"]]];
 If[Length[DeleteDuplicates[route]]!=1,Return[fail["MIXED_RADIATION_ROUTES"]]];
 n=Length[rows];average[f_]:=Sum[weights[[i]]*f[rows[[i]]],{i,n}];
 meanEnergy=Association@Table[key->average[Function[row,row["energy_columns_MeV"][key]]],{key,$energyNames}];
 meanCounts=Association@Table[key->average[Function[row,row["count_columns"][key]]],{key,{"thermal","fast","nuclear_total","electron"}}];
 mh=average[#["h"]&];mkc=average[#["K_c_normal_MeV"]&];joint=average[#["h"]*#["K_c_normal_MeV"]&];
 <|"schema"->"PHYS85_EXACT_ENSEMBLE_V1","channel"->First[ch],"radiation_route"->First[route],"weights"->weights,"events"->events,"event_count"->n,"mean_count_columns"->meanCounts,"mean_energy_columns_MeV"->meanEnergy,"mean_h"->mh,"mean_Kc_MeV"->mkc,"mean_joint_hKc_MeV"->joint,"product_mean_h_mean_Kc_MeV"->mh*mkc,"owner_energy_covariance_MeV"->joint-mh*mkc,"energy_residual_MeV"->Total[Values[meanEnergy]],"particle_residual"->meanCounts["thermal"]+meanCounts["fast"]+1,"physical_rate_evaluations"->0|>
];
End[];
EndPackage[];
