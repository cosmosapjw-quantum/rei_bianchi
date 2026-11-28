ass=t>0&&a0>0&&x0>0&&ee>0&&p0>=0;
uu=ee/t; rr=a0(1+p0 Sqrt[uu])/(x0+uu) uu^kap Exp[-uu];
rrp=rr/t(uu+uu/(x0+uu)-kap-p0 Sqrt[uu]/(2(1+p0 Sqrt[uu])));
r=ar t^(99/250) Exp[-33/t]+br t^(-83/250);
rp=ar t^(99/250) Exp[-33/t)((99/250)/t+33/t^2)-(83/250)/t br t^(-83/250);
f=r Exp[-d/t]; fp=Exp[-d/t](rp+r d/t^2);
tv=ta-gamma(v-va); kk=Exp[-d/tv];
gg=kk(aD-v)(q-v)-v(aH-q+v);
ggp=-kk((aD-v)+(q-v))-((aH-q+v)+v)-kk(aD-v)(q-v)d gamma/tv^2;
p=aH+aD-q; zeta=(aD-v)/p;
ci={den ch xe p,den ch xe(aD-v)};
gfixed=keq(aD-v)(q-v)-v(aH-q+v);
cx={0,den cr gfixed}; cival={den ch q p,den ch q(aD-v)};
bracket=Factor[Table[D[cx[[i]],s],{i,2},{s,{q,v}}].cival-Table[D[cival[[i]],s],{i,2},{s,{q,v}}].cx];
ExportString[<|
"Voronov_rate_derivative_residual"->FullSimplify[D[rr,t]-rrp,Assumptions->ass],
"Savin_reverse_derivative_residual"->Simplify[D[r,t]-rp,Assumptions->t>0],
"DB_forward_derivative_residual"->Simplify[D[f,t]-fp,Assumptions->t>0],
"D_scalar_balance_derivative_residual"->Simplify[D[gg,v]-ggp],
"CI_only_neutral_ratio_derivative_residual"->Simplify[D[zeta,q]ci[[1]]+D[zeta,v]ci[[2]]],
"CI_CX_fixedT_Lie_bracket"->ToString[bracket,InputForm],
"weighted_neutral_ratio_invariance_residual"->Simplify[(-rate y1)y2-y1(-rate y2)],
"ODE_calls"->0|>,"RawJSON"]
