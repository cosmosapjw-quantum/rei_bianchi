ClearAll["Global`*"];
ker=System`$Version;
ev=1602176634/10^28; kb=1380649/10^29; mh=167262192369/10^38; mu=mh/2;
th=kb*50000/ev; fac=50*Sqrt[8*ev/(Pi*mu)]/th^(3/2)/10^18;
j1[x_]=-th*(x+th)*Exp[-x/th];
j2[x_]=-th*(x^2+2*th*x+2*th^2)*Exp[-x/th];
segInt[{a_,b_,m_,q_}]:=m*(j2[b]-j2[a])+q*(j1[b]-j1[a]);
cl={{14,31/2,-1,16},{31/2,18,1,-15}};
cu={{14,33/2,1,-12},{33/2,18,-1,21}};
fl={{14,59/4,-1,16},{59/4,16,1,-27/2},{16,67/4,-1,37/2},{67/4,18,1,-15}};
fu={{14,61/4,1,-12},{61/4,16,-1,37/2},{16,69/4,1,-27/2},{69/4,18,-1,21}};
allsegs=Join[cl,cu,fl,fu];
residuals=FullSimplify[D[#[[3]]*j2[x]+#[[4]]*j1[x],x]-(#[[3]]*x+#[[4]])*x*Exp[-x/th]]&/@allsegs;
vals=fac*(Total[segInt/@#]&/@{cl,cu,fl,fu});
ivs=Map[N[Interval[{#,#}],60]&,vals];
rnd[x_]:=ToString[x,InputForm];
endpoints=({rnd[Floor[SetPrecision[Min[#],Infinity]*10^45]/10^45],rnd[Ceiling[SetPrecision[Max[#],Infinity]*10^45]/10^45]}&/@ivs);
proofs=<|"coarse_lower_switch"->(16-31/2==31/2-15),"coarse_upper_switch"->(33/2-12==21-33/2),"positive_width"->TrueQ[Min[ivs[[2]]-ivs[[1]]]>0],"nested_lower"->TrueQ[Min[ivs[[3]]-ivs[[1]]]>0],"nested_upper"->TrueQ[Min[ivs[[2]]-ivs[[4]]]>0],"fine_ordered"->TrueQ[Min[ivs[[4]]-ivs[[3]]]>0]|>;
<|"status"->If[And@@(TrueQ[#===0]&/@residuals)&&And@@Values[proofs],"PASS","FAIL"],"kernel"->ker,"segment_primitive_residuals"->residuals,"residual_count"->Length[residuals],"inequality_checks"->proofs,"rate_intervals_rational"->endpoints,"mid_values"->N[vals,25],"refinement_width_reduction"->N[(vals[[2]]-vals[[1]])/(vals[[4]]-vals[[3]]),25],"classification"->"manufactured endpoint witness; not physical cross-section data"|>
