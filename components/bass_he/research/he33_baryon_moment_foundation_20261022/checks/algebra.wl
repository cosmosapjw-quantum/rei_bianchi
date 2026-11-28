ClearAll[h,s,nu,p,q,Q,j,a,b,t,dt,pt,pl];
d=DiagonalMatrix[{-1,-1,2}]; pp=p IdentityMatrix[3]+q d; sig=s d;
rhs=-5 h pp-sig.pp-pp.sig-nu q d+(2 Q/3)IdentityMatrix[3]+j d;
pdot=Simplify[Tr[rhs]/3];
qdot=Simplify[Tr[d.rhs]/6];
energy=Simplify[3 pdot/2+5 h (3 p/2)+6 s q-Q];
trans=Simplify[{pdot-qdot,pdot+2 qdot}/.{p->(2pt+pl)/3,q->(pl-pt)/3}];
aMat={{-5h+2s-nu/3,nu/3},{2nu/3,-5h-4s-2nu/3}};
matres=Simplify[trans-aMat.{pt,pl}-{2Q/3-j,2Q/3+2j}];
traceColl=Simplify[{2,1}.({{-nu/3,nu/3},{2nu/3,-2nu/3}}.{pt,pl})];
coll=MatrixExp[{{-nu/3,nu/3},{2nu/3,-2nu/3}}dt];
collExpected={{2/3+Exp[-nu dt]/3,(1-Exp[-nu dt])/3},{2(1-Exp[-nu dt])/3,1/3+2Exp[-nu dt]/3}};
ExportString[<|"pdot"->ToString[pdot,InputForm],"qdot"->ToString[qdot,InputForm],"energy_residual"->energy,"lrs_matrix_residual"->matres,"collision_trace_residual"->traceColl,"collision_exponential_residual"->Simplify[coll-collExpected],"testA"->N[MatrixExp[(aMat/.{h->1/5,s->1/7,nu->2/3})7/10].{3/2,4/5},40]|>,"RawJSON"]
