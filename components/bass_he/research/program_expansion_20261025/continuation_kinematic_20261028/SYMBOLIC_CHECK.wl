Clear[a,m,e,u,v,r];
s=a^2+2 a e; h=s-4 m^2; g=a+e;
l=e+g r u; t=h (1-u^2);
ep=(g+e r u)/2; em=(g-e r u)/2;
pp=(1-v^2)(e^2+g^2 u^2 h/s)-v^2 h (1-u^2);
qq=2 e g u (1-v^2);
reduce[expr_]:=Cancel[PolynomialRemainder[Expand[expr],r^2-h/s,r]];
residuals={
 reduce[4 ep^2-l^2-t-4m^2],
 reduce[4 em^2-(e-g r u)^2-t-4m^2],
 reduce[ep+em-g],
 reduce[(l+e-g r u)/2-e],
 reduce[(1-v^2)l^2-v^2 t-pp-qq r],
 reduce[D[l,u] t-l D[t,u]/2-h(g r+e u)],
 reduce[(g^2-e^2)-s],
 reduce[s r^2-h],
 reduce[(e^2-g^2 r^2)-(4m^2 g^2-s^2)/s],
 reduce[(h(g r+e u)/.u->-g r/e)],
 Cancel[((h/s)/.{a->3,m->2,e->6/5})-1/81],
 Cancel[((h/s)/.{a->3,m->2,e->5/4})-1/33],
 Cancel[((e^2-g^2 h/s)/.{a->3,m->2,e->3/2})],
 Cancel[((s/.{a->3,m->2,e->8/3}))-25],
 Cancel[((h/s)/.{a->3,m->2,e->8/3})-9/25]
};
cases={{0,0,0},{3,-2,9/4},{-3,2,9/4},{2,-1,3},{1,-2,3},{-2,1,3},{-1,2,3},{0,-2,3},{1,2,3},{-1,-2,3},{2,-9,0}};
actual=Map[Sign[#[[1]]+#[[2]]Sqrt[#[[3]]]]&,cases];
expected={0,0,0,1,-1,-1,1,-1,1,-1,1};
<|"residual_count"->Length[residuals],"zero_residual_count"->Count[residuals,0],"residuals"->residuals,"surd_signs"->actual,"sign_cases_match"->(actual===expected),"threshold_case"->((s-4m^2)/.{a->3,m->2,e->7/6}),"actual_remote_CPU_s"->Null,"scope"->"New KINEMATIC08 polynomial conservation, original sign predicate and fold identities only"|>
