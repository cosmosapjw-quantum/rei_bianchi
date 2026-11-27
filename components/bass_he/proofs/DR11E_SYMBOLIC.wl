(* Exact algebra checks. This does not certify a finite-basis eigenvalue numerically. *)
ClearAll[x,tau,u,a,m,v,d0,d1,d2,d3,a0,a1,a2,c1,c2,c3];
qq=x(x+4tau); gg=qq^(m/2) Exp[-x/2];
lhs=FullSimplify[(-D[qq D[gg v[x],x],x]+(u qq/(4tau^2)-a(1+x/(2tau))+4tau^2 m^2/qq)gg v[x])/gg,
 Assumptions->{x>0,tau>0,Element[m,Integers],m>=0}];
rhs=-qq v''[x]+(qq-(m+1)D[qq,x])v'[x]+(2tau(m+1)-m(m+1)-a+(m+1-a/(2tau))x+(u-tau^2)qq/(4tau^2))v[x];
radialCheck=FullSimplify[lhs-rhs,Assumptions->{x>0,tau>0,Element[m,Integers],m>=0}];
tt={{d0,a0,0,0},{c1,d1,a1,0},{0,c2,d2,a2},{0,0,c3,d3}};
ff=d1-c1 a0/d0-a1 c2/(d2-a2 c3/d3);
schurCheck=Factor[Det[tt]-ff d0(d2 d3-a2 c3)];
legendreCheck=FullSimplify[LegendreP[12,3,1/4]-(-1)^3(1-1/16)^(3/2) Factorial[15]/(2^3 Factorial[3]Factorial[9]) Hypergeometric2F1[-9,16,4,3/8]];
Print[<|"RadialGauge"->radialCheck,"SchurChart"->schurCheck,"LegendreHypergeometric"->legendreCheck|>];
If[!And@@(TrueQ[#==0]& /@ {radialCheck,schurCheck,legendreCheck}),Exit[1]];
