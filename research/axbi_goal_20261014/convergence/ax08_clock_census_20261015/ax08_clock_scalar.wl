(* AX08 completed ZERO/HALF_PLUS, exact charge and clock identities.
   This is mathematics, not a new source ODE/AX11 continuum claim. *)
Module[{fH,fHe2,fHe3,nH,nHe,Ye,xi0,xiS,xc0,refa,refT,clock,
        q,odd,even,scaleQ,checks,out},
 Ye=nH fH+nHe (fHe2+2 fHe3);
 odd=q+( -q);
 even=q^2-(-q)^2;
 checks=<|
   "H01_H_element_norm"->TrueQ[FullSimplify[(1-fH)+fH-1]==0],
   "H02_He_element_norm"->TrueQ[FullSimplify[(1-fHe2-fHe3)+fHe2+fHe3-1]==0],
   "H03_charge_ratio"->TrueQ[FullSimplify[Ye/nH-fH-(nHe/nH)(fHe2+2 fHe3)]==0],
   "H04_mass_weighted_baryon_fraction"->TrueQ[FullSimplify[nH/(nH+4nHe)+4nHe/(nH+4nHe)-1]==0],
   "C01_clock_split_exact"->TrueQ[FullSimplify[(xiS-refT)-(xiS-refa)-(refa-refT)]==0],
   "C02_reversed_shear_even"->TrueQ[FullSimplify[even]==0],
   "C03_reversed_shear_odd"->TrueQ[FullSimplify[odd]==0]
 |>;
 out=<|"schema"->"rei.axbi.clock_census_scalar.v1",
   "wolfram_kernel"->$Version,
   "checks"->checks,"expected_checks"->7,"groups"->Length[checks],
   "all_pass"->And@@Values[checks],
   "scope"->"Only algebraic fraction/current and matched-clock decomposition; not coupled-source or discretization accuracy."|>;
 Print[ExportString[out,"RawJSON"]];
 Exit[If[TrueQ[out["all_pass"]],0,2]]
]