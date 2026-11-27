ClearAll["Global`*"];
ly[f_] := -I hbar (z D[f,x]-x D[f,z]);
kin[f_] := -hbar^2/(2 mass) (D[f,{x,2}]+D[f,{y,2}]+D[f,{z,2}]);
v=-kappa/Sqrt[x^2+y^2+(z-a)^2];
ass=Element[{x,y,z,a,hbar,kappa,mass,rho},Reals] && mass>0 && rho>0 && x^2+y^2+(z-a)^2>0;
torqueResidual=FullSimplify[v ly[psi[x,y,z]]-ly[v psi[x,y,z]]-I hbar kappa a x psi[x,y,z]/(x^2+y^2+(z-a)^2)^(3/2),ass];
kineticResidual=Simplify[Expand[kin[ly[psi[x,y,z]]]-ly[kin[psi[x,y,z]]]]];
lyCyl[f_]:=-I hbar (z (Cos[phi] D[f,rho]-Sin[phi]/rho D[f,phi])-rho Cos[phi] D[f,z]);
brightIntegrand=Integrate[lyCyl[Amp[rho,z] Cos[phi]/Sqrt[Pi]]/Sqrt[2 Pi],{phi,0,2 Pi}];
darkIntegrand=Integrate[lyCyl[Amp[rho,z] Sin[phi]/Sqrt[Pi]]/Sqrt[2 Pi],{phi,0,2 Pi}];
brightExpected=-I hbar/Sqrt[2] (z (D[Amp[rho,z],rho]+Amp[rho,z]/rho)-rho D[Amp[rho,z],z]);
torqueAngular=Integrate[(I hbar rho Cos[phi] W[rho,z]) Amp[rho,z] Cos[phi]/Sqrt[Pi]/Sqrt[2 Pi],{phi,0,2 Pi}];
activeConnection=FullSimplify[-I hbar Exp[I theta ell/hbar] D[Exp[-I theta ell/hbar],theta],Element[{hbar,ell,theta},Reals] && hbar!=0];
results=<|
 "potential_commutator_residual"->torqueResidual,
 "kinetic_commutator_residual"->kineticResidual,
 "bright_angular_integral_residual"->Simplify[brightIntegrand-brightExpected],
 "dark_angular_integral"->Simplify[darkIntegrand],
 "torque_angular_integral_residual"->Simplify[torqueAngular-I hbar rho W[rho,z] Amp[rho,z]/Sqrt[2]],
 "sigma_phi_norm"->Integrate[1/(2 Pi),{phi,0,2 Pi}],
 "bright_phi_norm"->Integrate[Cos[phi]^2/Pi,{phi,0,2 Pi}],
 "dark_phi_norm"->Integrate[Sin[phi]^2/Pi,{phi,0,2 Pi}],
 "bright_dark_phi_inner_product"->Integrate[Cos[phi] Sin[phi]/Pi,{phi,0,2 Pi}],
 "active_rotation_connection"->activeConnection,
 "angular_vector_field_divergence"->D[z,x]+D[0,y]+D[-x,z],
 "coalesced_nucleus_torque"->Simplify[(I hbar kappa a x/(x^2+y^2+(z-a)^2)^(3/2))/.a->0],
 "phase_covariance_factor"->FullSimplify[Conjugate[Exp[I chiG]] Exp[I chiR],Element[{chiG,chiR},Reals]],
 "origin_shift_residual"->Simplify[Cross[{xx-aa,yy-bb,zz-cc},{px,py,pz}]-Cross[{xx,yy,zz},{px,py,pz}]+Cross[{aa,bb,cc},{px,py,pz}]],
 "bright_meridional_operator"->brightExpected
|>;
<|"kernel_version"->$Version,"results"->results,"scope"->"Operator/algebra and azimuthal integrals only; no molecular eigenfunction solve or finite-R value."|>
