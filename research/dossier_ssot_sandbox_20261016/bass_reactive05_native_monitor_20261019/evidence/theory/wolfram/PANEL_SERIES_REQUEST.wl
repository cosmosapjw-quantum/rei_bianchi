Clear[pk, pl, pd, pf, pu];
{
"panel_mass_taylor" -> Normal[Series[Exp[-pu pl] pd Sum[(-pu pd)^n/(n+1)!,{n,0,5}],{pu,0,3}]],
"panel_mass_zero_coefficient" -> Coefficient[Normal[Series[Exp[-pu pl] pd Sum[(-pu pd)^n/(n+1)!,{n,0,5}],{pu,0,3}]],pu,0],
"conditional_mean_series" -> Normal[Series[(Sum[(-pu)^n/(n!(n+2)),{n,0,6}])/(Sum[(-pu)^n/(n!(n+1)),{n,0,6}]),{pu,0,4}]],
"GL2_emitted_second_defect" -> FullSimplify[(pf^2-pf+1/6)/.pf->(1-1/Sqrt[3])/2],
"uniform_W1_bounds" -> Reduce[0<pf<1/2 && !(1/8<=pf^2+(1/2-pf)^2<=1/4),pf,Reals]
}

