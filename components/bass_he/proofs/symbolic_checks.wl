(* Independent identities used by the implementation. Atomic-unit angular matrices. *)
Module[{q,ph,s,r,x,pz,lx,ly,lz,lp,theta,g,zero,comm,avg},
 lp={{0,0,0},{Sqrt[2],0,0},{0,Sqrt[2],0}};
 lz=DiagonalMatrix[{-1,0,1}];lx=(lp+Transpose[lp])/2;ly=(lp-Transpose[lp])/(2 I);
 pz=DiagonalMatrix[{-1,1,-1}];zero=ConstantArray[0,{3,3}];
 g=DiagonalMatrix[Exp[-I theta {-1,0,1}]];
 comm=FullSimplify[pz.(x lx-r ly).(x lx-r ly)-(x lx-r ly).(x lx-r ly).pz];
 avg=FullSimplify[Integrate[4 q(1-q)Sin[ph]^2,{ph,0,2 Pi}]/(2 Pi)];
 <|"parity_commutator_zero"->(comm==zero),
   "gauge_rotation_identity"->(FullSimplify[ConjugateTranspose[g].lx.g-Cos[theta]lx+Sin[theta]ly,Assumptions->Element[theta,Reals]]==zero),
   "coherent_probability_phase_average"->avg,
   "exponent_difference_maximum"->Maximize[{Exp[-s]-Exp[-2s],s>=0},s],
   "radial_measure"->FullSimplify[2 Pi Sqrt[s]/(2 Sqrt[s]),Assumptions->s>0]|>
]
