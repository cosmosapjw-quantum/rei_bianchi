Clear[a0,b0,cc,ii,kk,nn,aa,bb,dd,ss,q2,l,p,h,qp,z,u,d2,dp,t,v,d,x,b];
a0=q2+l^2; b0=a0+2 qp-2 I l p; cc=Exp[I h (Log[a0]-Log[b0])]; ii=4 Pi cc/a0;
kk=2 ii ((1-I h)l/a0+I h(l-I p)/b0); nn=(1-I h)l b0+I h(l-I p)a0;
aa=(l-I z)/2;bb=(l+I z)/2;dd=u^2/4;ss=aa+dd/bb;
raw=<|
"common_numerator"->(kk/ii-2 nn/(a0 b0)),
"orthogonality_factor"->(((kk/ii)/.{q2->p^2,qp->-p^2})-2(l-h p)/(p^2+l^2)),
"matched_numerator"->((nn/.{q2->d2+p^2-2dp,qp->dp-p^2,h->l/p})-2l(d2-(1+I l/p)dp)),
"parabolic_prefactor"->(bb ss-(l^2+z^2+u^2)/4),
"parabolic_branch_argument"->(1-I p/ss-(l^2+z^2+u^2+2z p-2I l p)/(l^2+z^2+u^2)),
"small_transfer_generic_slope"->((D[t^2-(1+I h)t v,t]/.t->0)+(1+I h)v)
|>;
timing=Timing[AbsoluteTiming[TimeConstrained[
diagnosis=AssociationMap[
Function[key,<|"raw"->ToString[raw[key],InputForm],"Cancel"->ToString[Cancel[raw[key]],InputForm],"Together"->ToString[Together[raw[key]],InputForm],"FullSimplify"->FullSimplify[raw[key],Assumptions->l>0&&p>0&&h>=0&&Element[{q2,qp,z,u,d2,dp,v},Reals]],"exact_rational_control"->FullSimplify[raw[key]/.{l->7/5,p->1/2,h->3/10,q2->9/10,qp->1/10,z->1/5,u->3/10,d2->4/5,dp->1/10,v->2/3}]|>],Keys[raw]],8,$Aborted]]];
<|"diagnosis"->diagnosis,"body_CPU_s"->timing[[1]],"body_wall_s"->timing[[2,1]],"remote_total_CPU"->"UNKNOWN_NOT_ZERO"|>
