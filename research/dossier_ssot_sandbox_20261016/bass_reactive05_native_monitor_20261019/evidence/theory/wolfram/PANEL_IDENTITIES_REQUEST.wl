Clear[pk, pl, pd, pf, py, pa, pb, ptheta];
{
"frozen_panel_mass_defect" -> FullSimplify[
pd Exp[-pk (pl+pd/2)] Sinh[pk pd/2]/(pk pd/2) - Integrate[Exp[-pk py],{py,pl,pl+pd},Assumptions->pk>0 && pd>0 && pl>=0],
Assumptions->pk>0 && pd>0 && pl>=0],
"emitted_mass_defect" -> Simplify[pd/2+pd/2-pd],
"emitted_first_moment_defect" -> Expand[pd((pl+pd pf)+(pl+pd(1-pf)))/2 - Integrate[py,{py,pl,pl+pd}]],
"emitted_second_moment_defect" -> Factor[pd((pl+pd pf)^2+(pl+pd(1-pf))^2)/2 - Integrate[py^2,{py,pl,pl+pd}]],
"uniform_two_atom_W1" -> FullSimplify[
Integrate[py,{py,0,pf}]+Integrate[1/2-py,{py,pf,1/2}]+Integrate[py-1/2,{py,1/2,1-pf}]+Integrate[1-py,{py,1-pf,1}],Assumptions->0<pf<1/2],
"uniform_two_atom_W1_defect" -> FullSimplify[
Integrate[py,{py,0,pf}]+Integrate[1/2-py,{py,pf,1/2}]+Integrate[py-1/2,{py,1/2,1-pf}]+Integrate[1-py,{py,1-pf,1}] - (pf^2+(1/2-pf)^2),Assumptions->0<pf<1/2],
"constant_opacity_zero_limit" -> Limit[Exp[-pk pl] (1-Exp[-pk pd])/pk,pk->0,Direction->"FromAbove"],
"conditional_mean_zero_limit" -> Limit[(1-(1+ptheta) Exp[-ptheta])/(ptheta (1-Exp[-ptheta])),ptheta->0,Direction->"FromAbove"],
"affine_distance_scale" -> FullSimplify[Abs[(pl+pd pa)-(pl+pd pb)]-pd Abs[pa-pb],Assumptions->Element[{pl,pa,pb},Reals] && pd>0]
}

