(* Exact homogeneous LRS Bianchi I photon (power4) and number (power3)
   angular Liouville PSTF m=0 coefficients in the BASS source conventions.
   Evaluates exact Legendre projections, not an inferred E/B collision model. *)
Clear[z,l,j,f4,f3,e,n,coeff,rho,pp,mu,kap,h,s];
f4[j_]:=3 z (1-z^2) D[LegendreP[j,z],z]-4(3z^2-1)LegendreP[j,z];
f3[j_]:=3 z (1-z^2) D[LegendreP[j,z],z]-3(3z^2-1)LegendreP[j,z];
coeff[f_,i_,j_]:=FullSimplify[Integrate[LegendreP[i,z](2 j+1)f[j],{z,-1,1}]/2];
e=Table[coeff[f4,i,j],{i,0,4},{j,0,4}];
n=Table[coeff[f3,i,j],{i,0,4},{j,0,4}];
If[e[[1]]=!={0,0,-2,0,0} || n[[1]]!={0,0,0,0,0} ||
   e[[3,1]]!=-8/5 || n[[3,1]]!=-6/5,
 Print["FAIL_BASS_SHEAR_MONOPOLE_LEDGER"];Exit[2]];
p2=(3z^2-1)/2;
W=1+kap p2;
mass=FullSimplify[Integrate[W,{z,-1,1}]/2];
quad=FullSimplify[Integrate[W p2,{z,-1,1}]/2];
If[!TrueQ[mass==1] || !TrueQ[quad==kap/5] ||
   !TrueQ[FullSimplify[MinValue[{W,-1<=z<=1&&-.5<=kap<=.5},{z,kap}]>=0]],
 Print["FAIL_POSITIVE_INITIAL_BASS_QUAD"];Exit[3]];
(* physical initial Pi/energy=J2/3=kappa/15 *)
If[!TrueQ[FullSimplify[quad/(3 mass)==kap/15]],
 Print["FAIL_INITIAL_PI_NORM"];Exit[4]];
Print["BASS_REI_HIERARCHY_EXACT_PSTF_PASS"];
Print["ENERGY_GL_MATRIX_L4=",InputForm[e]];
Print["NUMBER_GL_MATRIX_L4=",InputForm[n]];
Print["INITIAL_ENERGY_QUAD=",InputForm[quad]];
Print["BASS_P2_STRESS_FRACTION=",InputForm[quad/3]];
Exit[0];
