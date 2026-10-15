(* Exact LRS Bianchi-I covariant stress and energy theorem.
   Signature (-,+,+,+); spatial orthonormal shear diag(-s,-s,2s).
   rho,p,Pi in SI energy J/m3; K=8 Pi G/c^2; proper time seconds.
   Sigma_user=sqrt(sigma_ab sigma^ab/2)/H, not s/H. *)
Clear[hh,ss,ds,dH,pr,pm,rr,rm,lam,kk,b,mu,rad,poly,et];
sh=DiagonalMatrix[{-ss,-ss,2ss}];
pit=DiagonalMatrix[{-pr-pm,-pr-pm,2(pr+pm)}];
variance={Tr[sh],Tr[sh.sh]/2,Tr[sh.pit],
  pit[[3,3]]-pit[[1,1]]};
If[!TrueQ[FullSimplify[variance=={0,3ss^2,6ss(pr+pm),3(pr+pm)}]],
 Print["FAIL_TENSOR_CONTRACTION"];Print[variance];Exit[2]];
(* Einstein directional mixed diagonal component, Hperp=H-s, Hparallel=H+2s *)
hp=hh-ss;hz=hh+2ss;
Gpp=-((dH-ds)+(dH+2ds)+hp^2+hz^2+hp hz);
Gzz=-(2(dH-ds)+3hp^2);
If[!TrueQ[FullSimplify[Gzz-Gpp==3(ds+3hh ss)]],
 Print["FAIL_DIRECTIONAL_EINSTEIN_SHEAR"];Exit[3]];
(* Total energy continuity and constraint time differentiation *)
dotm=-3hh rm-6ss pm;
dotr=-4hh rr-6ss pr;
dots=-3hh ss+kk(pr+pm);
dotHfromconstraint=FullSimplify[(kk/3(dotm+dotr)+2ss dots)/(2hh)];
expected=-kk/2(rm+4rr/3)-3ss^2;
If[!TrueQ[FullSimplify[dotHfromconstraint==expected]],
 Print["FAIL_HAMILTONIAN_CONTINUITY_RAYCHAUDHURI"];Exit[4]];
(* For viscous Pi_m=-2 eta s, the matter source equals +12 eta s^2 *)
If[!TrueQ[FullSimplify[(-6ss pm/.pm->(-2et ss))==12et ss^2]],
 Print["FAIL_NONNEGATIVE_MATTER_VISCOUS_HEATING"];Exit[5]];
(* All Taylor coefficients to order 7 for exact M0'(b)+2M2(b)=0 *)
den=(1-mu^2)Exp[-2b]+mu^2 Exp[4b];
ser=Normal[Series[den^-2,{b,0,8}]];
m0=Table[FullSimplify[Integrate[Coefficient[ser,b,j],{mu,-1,1}]/2],{j,0,8}];
m2=Table[FullSimplify[Integrate[(3mu^2-1)/2 Coefficient[ser,b,j],{mu,-1,1}]/2],{j,0,8}];
energycoeff=Table[FullSimplify[(j+1)m0[[j+2]]+2m2[[j+1]]],{j,0,7}];
If[energycoeff=!=ConstantArray[0,8],Print["FAIL_RADIATION_M0_M2_ENERGY"];Exit[6]];
Print["WOLFRAM15_SIGMA_PI_COUPLED_GR_ENERGY_PASS"];
Print["TENSOR_DIAG_AND_WORK=",InputForm[variance]];
Print["EINSTEIN_SPATIAL_DELTA=",InputForm[FullSimplify[Gzz-Gpp]]];
Print["RAYCHAUDHURI_FROM_CONSTRAINT=",InputForm[dotHfromconstraint]];
Print["RADIATION_CONSERVATION_SERIES_COEFFICIENTS=",InputForm[energycoeff]];
Print["P2_LINEAR_QUADRATIC=",InputForm[{m2[[2]],m2[[3]]}]];
Exit[0];
