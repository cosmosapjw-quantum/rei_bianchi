Clear[t,mu,g,ep,rr,z];
phase=FullSimplify[{Cos[2 Pi (t+1/2)]+Cos[2 Pi t],Sin[2 Pi (t+1/2)]+Sin[2 Pi t]}];
bool=Flatten[Map[Function[v,Module[{ap=v[[1]],am=v[[2]],bp=v[[3]],bm=v[[4]],qa,qb,cc,oo,ha,hb,cs},
qa=ap bm;qb=bp am;cc=qa+qb-qa qb;oo=qa qb;
ha=ap+am-ap am;hb=bp+bm-bp bm;
cs=am bp+bm ap-(am bp)(bm ap);
{ap+am-ha-ap am,bp+bm-hb-bp bm,qa+qb-cc-oo,cc-cs,cc (1-ha),cc (1-hb)}
]],Tuples[{0,1},4]]];
energy=Expand[{(g+ep Sqrt[rr] mu)/2+(g-ep Sqrt[rr] mu)/2-g,(g-ep Sqrt[rr] mu)/2-((g+ep Sqrt[rr] mu)/2/.mu->-mu)}];
kk=40/51;yy=(1-kk)/4;haa=(1+kk)/4;hbb=yy;gg=17/3;
analytic={yy-11/204,haa-91/204,hbb-11/204,yy/haa-11/91,yy/hbb-1,2 yy-11/102,gg yy-11/36,gg yy/2-11/72};
rotation=Integrate[Piecewise[{{1/2-2 z,0<=z<=1/4},{2 z-3/2,3/4<=z<=1}},0],{z,0,1}]-1/8;
all=Join[phase,bool,energy,analytic,{rotation}];
ExportString[<|"unit"->"AZIMUTH09","groups"-><|"transverse_phase"->phase,"Boolean_vertex_residuals"->bool,"label_energy"->energy,"analytic_oracles"->analytic,"uniform_rotation_average"->{rotation}|>,"residual_count"->Length[all],"literal_zero_count"->Count[all,0],"all_zero"->And@@Map[TrueQ[#==0]&,all],"bisection_worst_case_checks"->{2/2^50<=1/(360*2^40),2/2^49>1/(360*2^40)},"exact_oracles"->Map[ToString[#,InputForm]&,{yy,haa,hbb,yy/haa,yy/hbb,gg yy,gg yy/2}],"actual_remote_cpu_s"->Null|>,"RawJSON"]
