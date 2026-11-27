Clear[a,d,t,x,y,z];
u={1,1};v={1,-1};q={1,1,1};dd={{x,z},{z,y}};
ll={u,v,-u-v};cc=4IdentityMatrix[2]+dd;kk=ll.cc.Transpose[ll];
tstar=2a/(4a-d);
rr={
Expand[(a+t d/2)(a-d+t d/2)-(a-t d/2)^2-(-a d+t(d/2)(4a-d))],
FullSimplify[(-a d+t(d/2)(4a-d))/.t->tstar],
Expand[u.dd.v-(x-y)],
Expand[u.cc.u+v.cc.v-(16+2x+2y)],
Expand[q.kk.q],
Sequence@@(Expand/@(kk.q)),
({1,1,1}.{{1,-1,-1},{-1,1,-1},{-1,-1,1}}.{1,1,1}+9/10)-(-21/10)
};
ExportString[<|"scalar_residuals"->rr,"all_zero"->And@@(TrueQ[#==0]&/@rr),"positive_off_branch"->FullSimplify[0<tstar<2a/d,Assumptions->a>d>0],"scope"->"PHYS90 new symbolic identities only; no old displayed-matrix/eigen/rate rerun"|>,"RawJSON"]
