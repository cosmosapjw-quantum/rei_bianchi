Module[{mu,x,b4,b8,p4,p8,elev,res,rat,t,d1,d2,c1,c2,checks},
 x=(mu+1)/2;
 b4=Table[Binomial[4,k]x^k(1-x)^(4-k),{k,0,4}];
 b8=Table[Binomial[8,k]x^k(1-x)^(8-k),{k,0,8}];
 p4={b4[[1]]+b4[[5]],b4[[2]]+b4[[4]],b4[[3]]};
 p8={b8[[1]]+b8[[9]],b8[[2]]+b8[[8]],b8[[3]]+b8[[7]],b8[[4]]+b8[[6]],b8[[5]]};
 elev=Table[Sum[If[0<=k-i<=4,Binomial[4,i]Binomial[4,k-i]/Binomial[8,k] b8[[k+1]],0],{k,0,8}],{i,0,4}];
 res=Join[Expand[elev-b4],FullSimplify[(p4/.mu->-mu)-p4],FullSimplify[(p8/.mu->-mu)-p8],
  Integrate[p4,{mu,-1,1}]-{4/5,4/5,2/5},Integrate[p8,{mu,-1,1}]-{4/9,4/9,4/9,4/9,2/9}];
 rat=(t c1+(1-t)c2)/(t d1+(1-t)d2);
 checks=<|"all_literal_zero"->And@@Thread[res==0],
 "n4_endpoint"->((p4/.mu->1)=={1,0,0}),
 "n8_endpoint"->((p8/.mu->-1)=={1,0,0,0,0}),
 "ratio_weight_identity"->(Together[rat-(t d1/(t d1+(1-t)d2)c1/d1+(1-t)d2/(t d1+(1-t)d2)c2/d2)]===0),
 "ratio_derivative_identity"->(Together[D[rat,t]-(c1 d2-c2 d1)/(t d1+(1-t)d2)^2]===0),
 "common_scale_identity"->(Together[(7 c1)/(7 d1)-c1/d1]===0),
 "n4_full_sum"->(Expand[p4.{1,1,1}-1]===0),
 "n8_full_sum"->(Expand[p8.{1,1,1,1,1}-1]===0)|>;
 <|"unit"->"EXFOR11","literal_residuals"->res,"checks"->checks,"all_checks_true"->And@@Values[checks],"remote_cpu_s"->Null|>
]
