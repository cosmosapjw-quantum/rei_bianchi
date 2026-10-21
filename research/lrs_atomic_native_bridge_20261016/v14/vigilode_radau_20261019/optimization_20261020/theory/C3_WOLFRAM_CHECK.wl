ClearAll["Global`*"];
p = c nh v { (1-x) sh, yy (1-y-z) s1, yy y s2 };
gd = {p[[1]], (p[[2]]-p[[3]])/yy, p[[3]]/yy};
bd = {chi0, yy chi1, yy (chi1+chi2)}.gd;
ed = {1,yy,2yy}.gd;
wd = (en-{chi0,chi1,chi2}).p;
nd = -Total[p];
analytic = c nh v {sh,yy (s1-s2), yy s1,0};
photonJac = D[nd, {{x,y,z,ww}}];
weights = {a0 Exp[theta q0],a1 Exp[theta q1],a2 Exp[theta q2]};
prob = weights/Total[weights];
qs = {q0,q1,q2}; fs = {f0,f1,f2};
mu = prob.qs; obs = prob.fs;
cov = prob.(qs fs) - mu obs;
variance = prob.(qs qs)-mu^2;
<|"energy_identity" -> FullSimplify[wd+bd+en nd],
"electron_identity" -> FullSimplify[ed-Total[p]],
"photon_gas_derivative_identity" -> FullSimplify[photonJac-analytic],
"entropy_mean_derivative_identity" -> FullSimplify[D[mu,theta]-variance],
"entropy_observable_derivative_identity" -> FullSimplify[D[obs,theta]-cov],
"prepared_cell_count_reference" -> (1+2(4+2*40))*40,
"prepared_cell_count_local_cache" -> 40+2(2*40)|>
