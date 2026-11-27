timing=Timing[AbsoluteTiming[TimeConstrained[
a0=q2+l^2; b0=a0+2 qp-2 I l p; cc=Exp[I h (Log[a0]-Log[b0])]; ii=4 Pi cc/a0;
kk=2 ii ((1-I h) l/a0+I h (l-I p)/b0);
nn=(1-I h) l b0+I h (l-I p) a0;
aa=(l-I z)/2; bb=(l+I z)/2; dd=u^2/4; ss=aa+dd/bb;
checks=<|
"fixed_eta_derivative"->(Cancel[(-D[ii,l]-kk)/ii]===0),
"common_numerator"->(Cancel[kk/ii-2 nn/(a0 b0)]===0),
"orthogonality_factor"->(Cancel[((kk/ii)/.{q2->p^2,qp->-p^2})-2 (l-h p)/(p^2+l^2)]===0),
"matched_zero"->(Cancel[((kk/ii)/.{q2->p^2,qp->-p^2})/.h->l/p]===0),
"plane_wave_overlap"->(Cancel[(kk/.h->0)-8 Pi l/(q2+l^2)^2]===0),
"matched_numerator"->(Cancel[(nn/.{q2->d2+p^2-2 dp,qp->dp-p^2,h->l/p})-2 l (d2-(1+I l/p)dp)]===0),
"matched_complex_denominator"->(Expand[(b0/.{q2->d2+p^2-2 dp,qp->dp-p^2})-(d2+(l-I p)^2)]===0),
"parabolic_prefactor"->(Cancel[bb ss-(l^2+z^2+u^2)/4]===0),
"parabolic_branch_argument"->(Cancel[1-I p/ss-(l^2+z^2+u^2+2 z p-2 I l p)/(l^2+z^2+u^2)]===0),
"zeta_first_moment"->(FullSimplify[-D[Exp[-d x/b]/b,b]-Exp[-d x/b](b^-2-d x b^-3)]===0),
"independent_quad_plane_limit"->(Cancel[Pi/(2 bb)((1-dd/bb^2)/ss^2+1/(bb ss))-8 Pi l/(l^2+z^2+u^2)^2]===0),
"Sommerfeld_gamma"->TrueQ[FullSimplify[FunctionExpand[Exp[Pi h] Gamma[1+I h] Gamma[1-I h]]==2 Pi h/(1-Exp[-2 Pi h]),Assumptions->h>0]],
"box_flux_coefficient"->(2 Pi*16 Pi^2/(2 Pi)^6==4/(2 Pi)^3),
"delta_flux_coefficient"->((2 Pi)^4*(4 Pi/(2 Pi)^3)^2==4),
"small_transfer_generic_slope"->((D[t^2-(1+I h)t v,t]/.t->0)==-(1+I h)v),
"small_transfer_transverse_order"->((D[t^2,t,t]/.t->0)==2),
"eta_chain_rule_extra_term"->(FullSimplify[(D[ii/.h->l/p,l]-(D[ii,l]/.h->l/p))/(ii/.h->l/p)-I(Log[a0]-Log[b0])/p]===0),
"normalizer_eta_zero"->(Exp[Pi*0/2]Gamma[1-I*0]==1)
|>;checks,12,$Aborted]]];
<|"checks"->timing[[2,2]],"body_CPU_s"->timing[[1]],"body_wall_s"->timing[[2,1]],"remote_total_CPU"->"UNKNOWN_NOT_ZERO","scope"->"symbolic algebra only; physical validity and finite-domain numerics separate"|>
