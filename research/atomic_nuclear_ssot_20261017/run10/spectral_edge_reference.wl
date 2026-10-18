(* RUN10 MP55 reference. Executed through Wolfram, not ChatGPT sandbox.
   Exact-decimal reconstruction of read source formulas; no claim of Rust parity.
   eta=Exp[-0.0004] is a manufactured FLRW kinematic control, not a BASS ray.
   Response columns: HI sigma [m^2], DI sigma [m^2], HI/DI sigma*(E-chi) [eV m^2]. *)
Module[{wp=55,lo,hi,kt,ch,cd,eta,shape,mom,raw,rule,cuts,base,mean,ref,resp,pack,rows,tests,x,z,ruleResiduals},
lo=N[68/5,wp];hi=N[(68/5)(2459/1360)^(1/16),wp];
kt=N[(1380649/10^22)/(1602176634/10^21)*50000,wp];
ch=N[13598434599702/10^12,wp];cd=N[13602134599702/10^12,wp];eta=N[Exp[-1/2500],wp];
shape[e_?NumericQ]:=e^2/(Exp[e/kt]-1);
mom[a_?NumericQ,b_?NumericQ,k_Integer]:=mom[a,b,k]=NIntegrate[x^k shape[x],{x,a,b},WorkingPrecision->wp,AccuracyGoal->42,PrecisionGoal->42];
base=mom[lo,hi,0];mean=mom[lo,hi,1]/base;
cuts=DeleteDuplicates[Sort[N[Join[{lo,hi},Select[{lo,cd,lo/eta,cd/eta},lo<#<hi&]],wp]]];
raw[a_,b_]:=raw[a,b]=With[{mid=(a+b)/2,half=(b-a)/2},Table[half NIntegrate[z^k shape[mid+half z],{z,-1,1},WorkingPrecision->wp,AccuracyGoal->42,PrecisionGoal->42],{k,0,3}]];
rule[a_,b_]:=rule[a,b]=Module[{m=raw[a,b],mu,v,t,d,zm,zp,wm,wp2,mid=(a+b)/2,half=(b-a)/2},
mu=m[[2]]/m[[1]];v=m[[3]]/m[[1]]-mu^2;t=m[[4]]/m[[1]]-3mu m[[3]]/m[[1]]+2mu^3;d=t/v;
zm=mu+(d-Sqrt[d^2+4v])/2;zp=mu+(d+Sqrt[d^2+4v])/2;
wm=(zp-mu)/(zp-zm);wp2=(mu-zm)/(zp-zm);
{{mid+half zm,m[[1]]wm/base},{mid+half zp,m[[1]]wp2/base}}];
pack[n_Integer]:=pack[n]=Flatten[Table[With[{a=cuts[[s]],b=cuts[[s+1]]},Table[rule[a+(b-a)j/n,a+(b-a)(j+1)/n],{j,0,n-1}]],{s,1,Length[cuts]-1}],2];
resp[e_?NumericQ,k_Integer]:=Module[{q=eta e,y,s},If[q<If[k==1||k==3,lo,cd],Return[0]];
y=q/(4298/10000);s=54750(y-1)^2 y^((2963/1000)/2-11/2)(1+Sqrt[y/(3288/100)])^(-2963/1000)*10^-22;
If[k<=2,s,s(q-If[k==3,ch,cd])]];
ref=Table[NIntegrate[shape[x]resp[x,k],{x,If[k==1||k==3,lo/eta,cd/eta],hi},WorkingPrecision->wp,AccuracyGoal->40,PrecisionGoal->35]/base,{k,1,4}];
rows=Table[With[{q=pack[n]},<|"subdivisions"->n,"nodes"->Length[q],"count_residual"->N[Total[q[[All,2]]]-1,8],"mean_residual_eV"->N[Total[Times@@#& /@ q]-mean,8],"relative_response_errors_H_D_Hheat_Dheat"->N[Table[Total[(#[[2]]resp[#[[1]],k])& /@ q]/ref[[k]]-1,{k,1,4}],14],"D_crossing_mass"->N[Total[Cases[q,{e_,w_}/;cd<e<cd/eta:>w]],17]|>],{n,{1,2,4}}];
ruleResiduals=Flatten[Table[With[{a=cuts[[s]],b=cuts[[s+1]]},Table[Abs[base Total[(#[[2]]((#[[1]]-(a+b)/2)/((b-a)/2))^k)& /@ rule[a,b]]-raw[a,b][[k+1]]]/raw[a,b][[1]],{k,0,3}]],{s,1,Length[cuts]-1}]];
tests=<|"ordered_nodes_within_parent"->And@@Flatten[Table[(lo<#[[1]]<hi)& /@ pack[n],{n,{1,2,4}}]],"strictly_positive_weights"->And@@Flatten[Table[(#[[2]]>0)& /@ pack[n],{n,{1,2,4}}]],"zeroth_to_third_local_moments"->(Max[ruleResiduals]<10^-40),"source_count_unchanged"->And@@Table[Abs[Total[pack[n][[All,2]]]-1]<10^-40,{n,{1,2,4}}],"source_energy_continuous_mean_unchanged"->And@@Table[Abs[Total[Times@@#& /@ pack[n]]-mean]<10^-38,{n,{1,2,4}}],"D_crossing_class_mass"->And@@Table[Abs[Total[Cases[pack[n],{e_,w_}/;cd<e<cd/eta:>w]]-mom[cd,cd/eta,0]/base]<10^-40,{n,{1,2,4}}]|>;
<|"reference_values"->N[ref,18],"rows"->rows,"checks"->tests,"max_local_moment_scaled_residual"->N[Max[ruleResiduals],8],"scope"->"MP55 source-formula reference; manufactured monotone FLRW ray; frozen terminal response only; native Rust and joint BASS NOT_RUN"|>
]
