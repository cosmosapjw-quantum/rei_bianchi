Module[{p,q,r1,r2,rr0,d1,d2,d3,pp,rr,diag,proj,hh,hh2,a,b,c,gr,ge,r0,e0,t,phia,phib,jj,qq,rs,es,col,sink,two,odes,init,resonance,zerorate,cubic,all},
 pp={p,q,1-p-q};rr={r1,r2,-r1-r2};diag=DiagonalMatrix[{d1,d2,d3}];
 proj=IdentityMatrix[3]-Outer[Times,pp,{1,1,1}];hh=Outer[Times,pp,{d1,d2,d3}]-diag;
 col=FullSimplify[Total[hh]];sink=FullSimplify[hh.rr+proj.diag.rr];
 hh2=Outer[Times,{p,1-p},{d1,d2}]-DiagonalMatrix[{d1,d2}];
 two=FullSimplify[hh2.{rr0,-rr0}+(p d2+(1-p)d1){rr0,-rr0}];
 phia=(Exp[a t]-1)/a;phib=(Exp[b t]-1)/b;jj=(Exp[a t]-Exp[b t])/(a-b);qq=(jj-phib)/a;
 rs=Exp[a t] r0+phia gr;es=Exp[b t] e0+c jj r0+c qq gr+phib ge;
 odes=FullSimplify[{D[rs,t]-a rs-gr,D[es,t]-b es-c rs-ge},Assumptions->a!=0&&b!=0&&a!=b];
 init=FullSimplify[{(rs/.t->0)-r0,(es/.t->0)-e0},Assumptions->a!=0&&b!=0&&a!=b];
 resonance=FullSimplify[Limit[jj,b->a]-t Exp[a t]];
 zerorate=FullSimplify[Limit[qq,a->0]-(Exp[b t]-1-b t)/b^2,Assumptions->b!=0];
 cubic=FullSimplify[Coefficient[Normal[Series[Exp[-3t/2](Cosh[Sqrt[5]t/2]+3/Sqrt[5] Sinh[Sqrt[5]t/2])-Exp[-t](1+t),{t,0,3}]],t,3]-1/6];
 all=Flatten[{col,sink,two,odes,init,resonance,zerorate,cubic}];
 <|"column_sum_residuals"->col,"projected_sink_residuals"->sink,"two_state_decay_residuals"->two,"triangular_ODE_residuals"->odes,"initial_residuals"->init,"resonance_limit_residual"->resonance,"zero_rate_limit_residual"->zerorate,"bad_K_block_transfer_cubic_residual"->cubic,"zero_residual_count"->Count[all,0],"total_residual_count"->Length[all],"all_zero"->And@@(TrueQ[#==0]&/@all)|>
]
