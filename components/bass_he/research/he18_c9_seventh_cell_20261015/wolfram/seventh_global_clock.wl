(* Seventh saved time slab with original-epoch clock, exact scalar checks. *)
Module[{u,mu,bb,vv,step,sig,aa,be,ff,moving,der,expect,q,checks,out},
 aa=Exp[2 bb[u]](1-mu^2);
 be=Exp[-4 bb[u]]mu^2;
 ff=Sqrt[aa+be]/vv[6+u]^(1/3);
 moving=be/(aa+be);
 der=D[Log[ff],u]/.Derivative[1][bb][u]->step sig/vv[6+u];
 expect=-Derivative[1][vv][6+u]/(3 vv[6+u])+step sig/vv[6+u]*(1-3 moving);
 checks=<|
 "S01_global_epoch_clock"->TrueQ[FullSimplify[der-expect]==0],
 "S02_even_source_direction"->TrueQ[FullSimplify[(ff/.mu->-mu)-ff]==0],
 "S03_longitudinal_redshift"->TrueQ[FullSimplify[(der-expect)/.mu->1]==0],
 "S04_transverse_redshift"->TrueQ[FullSimplify[(der-expect)/.mu->0]==0],
 "S05_bernstein_partition"->TrueQ[Expand[(1-q)^2+2q(1-q)+q^2-1]==0],
 "S06_positive_bernstein_basis"->TrueQ[FullSimplify[(1-q)^2>=0&&2q(1-q)>=0&&q^2>=0,0<=q<=1]],
 "S07_collision_probability_monotonic"->TrueQ[FullSimplify[D[1-Exp[-q],q]>0,q>=0]],
 "S08_shear_direction_parity"->TrueQ[FullSimplify[(moving/.mu->-mu)-moving]==0]
 |>;
 out=<|"unit"->"HE18_C9_SEVENTH_SCALAR_KINEMATICS",
 "wolfram_kernel"->$Version,"actual_checks"->Length[checks],
 "checks"->checks,"all_pass"->(Length[checks]==8&&And@@Values[checks]),
 "scope"->"Exact clock, ray symmetry and Bernstein algebra only; not a proof of interval arithmetic or source ODE."|>;
 Print[ExportString[out,"RawJSON"]];
 Exit[If[TrueQ[out["all_pass"]],0,2]]
]