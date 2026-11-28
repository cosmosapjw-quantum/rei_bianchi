ClearAll[x,u,p1,p2,d1,d2,d3,q,g0,g1,g2,r0];
ass=Element[x,Reals]&&x!=0;
a[x_]:=((x-1)Exp[x]+1)/x^2;
b[x_]:=(Exp[x]-1-x)/x^2;
phi[x_]:=(Exp[x]-1)/x;
p={p1,p2,1-p1-p2}; ds={d1,d2,d3}; hh=Outer[Times,p,ds]-DiagonalMatrix[ds];
parass=p1>=0&&p2>=0&&p1+p2<=1&&d1>=0&&d2>=0&&d3>=0&&Element[{p1,p2,d1,d2,d3},Reals];
moments={FullSimplify[Integrate[(1-u)Exp[x(1-u)],{u,0,1},Assumptions->ass]-a[x],ass],FullSimplify[Integrate[u Exp[x(1-u)],{u,0,1},Assumptions->ass]-b[x],ass],FullSimplify[a[x]-Exp[x]b[-x],ass],FullSimplify[b[x]-Exp[x]a[-x],ass],FullSimplify[a[x]+b[x]-phi[x],ass]};
limits={Limit[a[x],x->0]-1/2,Limit[b[x],x->0]-1/2,Limit[phi[x],x->0]-1};
cols=FullSimplify[Total[hh]];
norms=Table[FullSimplify[Total[Abs[hh[[All,j]]]]-2ds[[j]](1-p[[j]]),parass],{j,3}];
forcing=Expand[(q r0+g0+g1)+((q-1)g0+g2)-(q r0+q g0+g1+g2)];
all=Join[moments,limits,cols,norms,{forcing}];
<|"unit"->"WU_FULL_GENERATOR_BLOCK_R11","residuals"->all,"residual_count"->Length[all],"all_zero"->And@@Map[TrueQ[#==0]&,all],"scope"->"Bernstein signed-d identities, zero limits, H column/norm identities, aligned forcing left-limit algebra; uniform theorem independently proved"|>
